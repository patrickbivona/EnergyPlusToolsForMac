import imp
import sys
import os
import os.path as op
import plistlib
import shutil
from io import StringIO
import sysconfig

from distutils.util import convert_path
from distutils.dir_util import mkpath
from distutils.file_util import copy_file
from distutils import log
from pkg_resources import resource_filename

from modulegraph.find_modules import find_modules, parse_mf_results
from modulegraph.modulegraph import SourceModule, Package, os_listdir
from modulegraph.util import imp_find_module

import macholib.dyld
import macholib.MachOStandalone
from macholib.util import has_filename_filter, strip_files
from macholib.framework import framework_info

from . import bundletemplate, recipes
from .util import (byte_compile, make_loader, copy_tree, makedirs, iter_platform_files, skipscm,
    copy_file_data, copy_resource, SCMDIRS, mergecopy, mergetree, make_exec, is_python_package)

from distutils.sysconfig import get_config_var
PYTHONFRAMEWORK=get_config_var('PYTHONFRAMEWORK')

class PythonStandalone(macholib.MachOStandalone.MachOStandalone):
    def copy_dylib(self, src):
        dest = os.path.join(self.dest, os.path.basename(src))
        return copy_dylib(src, dest)

    def copy_framework(self, info):
        destfn = copy_framework(info, self.dest)
        dest = os.path.join(self.dest, info['shortname'] + '.framework')
        self.pending.append((destfn, iter_platform_files(dest)))
        return destfn

class Target:
    def __init__(self, script):
        self.script = script
        self.plist = {}
        self.prescripts = []
    
    def get_dest_base(self):
        return os.path.basename(os.path.splitext(self.script)[0])
    

def normalize_data_file(fn):
    if isinstance(fn, str):
        fn = convert_path(fn)
        return ('', [fn])
    return fn

def force_symlink(src, dst):
    try:
        os.remove(dst)
    except OSError:
        pass
    os.symlink(src, dst)

def copy_python_framework(info, dst):
    # XXX - In this particular case we know exactly what we can
    #       get away with.. should this be extended to the general
    #       case?  Per-framework recipes?
    indir = os.path.dirname(os.path.join(info['location'], info['name']))
    outdir = os.path.dirname(os.path.join(dst, info['name']))
    mkpath(os.path.join(outdir, 'Resources'))
    # Since python 3.2, the naming scheme for config files location has considerably
    # complexified. The old, simple way doesn't work anymore. Fortunately, a new module was
    # added to get such paths easily.
    
    # It's possible that virtualenv is messing with us here, so we only use the rightmost part of
    # each of the two paths below. For pyconfig_path, it's the last 3 elements of the path
    # (include/python3.2m/pyconfig.h) and for makefile_path it's the last 4
    # (lib/python3.2/config-3.2m/Makefile). Yes, this kind of location can change depending on the
    # platform, but we're only supporting Mac OS X eh? We'll take these last path parts and append
    # them to indir and we'll have our non-virtualenv paths.
    pyconfig_path = sysconfig.get_config_h_filename()
    makefile_path = sysconfig.get_makefile_filename()
    pyconfig_path = op.join(*pyconfig_path.split(os.sep)[-3:])
    makefile_path = op.join(*makefile_path.split(os.sep)[-4:])
    assert pyconfig_path.startswith('include')
    assert makefile_path.startswith('lib')

    # distutils looks for some files relative to sys.executable, which
    # means they have to be in the framework...
    mkpath(op.join(outdir, op.dirname(pyconfig_path)))
    mkpath(op.join(outdir, op.dirname(makefile_path)))
    fmwkfiles = [
        os.path.basename(info['name']),
        'Resources/Info.plist',
        pyconfig_path,
        makefile_path,
    ]
    for fn in fmwkfiles:
        copy_file(os.path.join(indir, fn), os.path.join(outdir, fn))

def copy_versioned_framework(info, dst):
    # XXX - Boy is this ugly, but it makes sense because the developer
    #       could have both Python 2.3 and 2.4, or Tk 8.4 and 8.5, etc.
    #       Saves a good deal of space, and I'm pretty sure this ugly
    #       hack is correct in the general case.
    def framework_copy_condition(src):
        # Skip Headers, .svn, and CVS dirs
        return skipscm(src) and os.path.basename(src) != 'Headers'
    
    short = info['shortname'] + '.framework'
    infile = os.path.join(info['location'], short)
    outfile = os.path.join(dst, short)
    version = info['version']
    if version is None:
        condition = framework_copy_condition
    else:
        vsplit = os.path.join(infile, 'Versions').split(os.sep)
        def condition(src, vsplit=vsplit, version=version):
            srcsplit = src.split(os.sep)
            if (
                    len(srcsplit) > len(vsplit) and
                    srcsplit[:len(vsplit)] == vsplit and
                    srcsplit[len(vsplit)] != version and
                    not os.path.islink(src)
                ):
                return False
            # Skip Headers, .svn, and CVS dirs
            return framework_copy_condition(src)
    
    return copy_tree(infile, outfile, preserve_symlinks=True, condition=condition)

def copy_framework(info, dst):
    if info['shortname'] == PYTHONFRAMEWORK:
        copy_python_framework(info, dst)
    else:
        copy_versioned_framework(info, dst)
    return os.path.join(dst, info['name'])

def copy_dylib(src, dst):
    # will be copied from the framework?
    if src != sys.executable:
        copy_file(src, dst)
    return dst

def copy_package_data(package, target_dir):
    """
    Copy any package data in a python package into the target_dir.

    This is a bit of a hack, it would be better to identify python eggs
    and copy those in whole.
    """
    exts = [ i[0] for i in imp.get_suffixes() ]
    exts.append('.py')
    exts.append('.pyc')
    exts.append('.pyo')
    def datafilter(item):
        for e in exts:
            if item.endswith(e):
                return False
        return True

    target_dir = os.path.join(target_dir, *(package.identifier.split('.')))
    for dname in package.packagepath:
        filenames = list(filter(datafilter, os_listdir(dname)))
        for fname in filenames:
            if fname in SCMDIRS:
                # Scrub revision manager junk
                continue
            if fname in ('__pycache__',):
                # Ignore PEP 3147 bytecode cache
                continue
            pth = os.path.join(dname, fname)

            # Check if we have found a package, exclude those
            if is_python_package(pth):
                continue
            copydest = op.join(target_dir, fname)
            if op.isdir(pth):
                copy_tree(pth, copydest)
            else:
                copy_file(pth, copydest)

def strip_dsym(platfiles, appdir):
    """ Remove .dSYM directories in the bundled application """

    #
    # .dSYM directories are contain detached debugging information and
    # should be completely removed when the "strip" option is specified.
    #
    for dirpath, dnames, fnames in os.walk(appdir):
        for nm in list(dnames):
            if nm.endswith('.dSYM'):
                print("removing debug info: %s/%s"%(dirpath, nm))
                shutil.rmtree(os.path.join(dirpath, nm))
                dnames.remove(nm)
    return [file for file in platfiles if '.dSYM' not in file]

def strip_files_and_report(files, verbose):
    unstripped = 0
    stripfiles = []
    for fn in files:
        unstripped += os.stat(fn).st_size
        stripfiles.append(fn)
        log.info('stripping %s', os.path.basename(fn))
    strip_files(stripfiles)
    stripped = 0
    for fn in stripfiles:
        stripped += os.stat(fn).st_size
    log.info('stripping saved %d bytes (%d / %d)',
        unstripped - stripped, stripped, unstripped)

def get_bootstrap(bootstrap):
    if isinstance(bootstrap, str):
        if not os.path.exists(bootstrap):
            bootstrap = imp_find_module(bootstrap)[1]
    return bootstrap

def get_bootstrap_data(bootstrap):
    bootstrap = get_bootstrap(bootstrap)
    if not isinstance(bootstrap, str):
        return bootstrap.getvalue()
    else:
        return open(bootstrap, 'rU').read()

def create_pluginbundle(destdir, name, plist):
    module = bundletemplate
    kw = module.plist_template.infoPlistDict(
        plist.get('CFBundleExecutable', name), plist)
    plugin = os.path.join(destdir, kw['CFBundleName'] + '.plugin')
    contents = os.path.join(plugin, 'Contents')
    resources = os.path.join(contents, 'Resources')
    platdir = os.path.join(contents, 'MacOS')
    dirs = [contents, resources, platdir]
    plist = plistlib.Plist()
    plist.update(kw)
    plistPath = os.path.join(contents, 'Info.plist')
    if os.path.exists(plistPath):
        if plist != plistlib.Plist.fromFile(plistPath):
            for d in dirs:
                shutil.rmtree(d, ignore_errors=True)
    for d in dirs:
        makedirs(d)
    plist.write(plistPath)
    srcmain = module.setup.main_executable_path()
    destmain = os.path.join(platdir, kw['CFBundleExecutable'])
    open(os.path.join(contents, 'PkgInfo'), 'w').write(
        kw['CFBundlePackageType'] + kw['CFBundleSignature']
    )
    mergecopy(srcmain, destmain)
    make_exec(destmain)
    mergetree(
        resource_filename(module.__name__, 'lib'),
        resources,
        condition=skipscm,
        copyfn=mergecopy,
    )
    return plugin, plist

class Options:
    def __init__(self, main_script_path, includes=None, packages=None, excludes=None, dylib_excludes=None,
            resources=None, frameworks=None, plist=None, optimize=0, strip=True, alias=False,
            argv_inject=None, use_pythonpath=False, site_package=False, verbose=False, dry_run=False,
            bdist_base='build', dist_dir='dist', debug_modulegraph=False, debug_skip_macholib=False):
        self.target = Target(main_script_path)
        self.bdist_base = bdist_base
        self.optimize = optimize
        self.strip = strip
        self.alias = alias
        self.argv_inject = argv_inject
        self.site_packages = site_package
        self.use_pythonpath = use_pythonpath
        self.verbose = verbose
        self.dry_run = dry_run
        self.additional_paths = [os.path.abspath(os.path.dirname(self.target.script))]
        self.includes = set(includes if includes else [])
        self.includes.add('encodings.*')
        self.packages = set(packages if packages else [])
        self.excludes = set(excludes if excludes else [])
        self.excludes.add('readline')
        self.excludes.add('site')
        self.dylib_excludes = []
        if dylib_excludes:
            for fn in dylib_excludes:
                try:
                    res = macholib.dyld.framework_find(fn)
                except ValueError:
                    try:
                        res = macholib.dyld.dyld_find(fn)
                    except ValueError:
                        res = fn
                self.dylib_excludes.append(res)
        self.resources = resources if resources else []
        self.frameworks = []
        if frameworks:
            for fn in frameworks:
                try:
                    res = macholib.dyld.framework_find(fn)
                except ValueError:
                    res = macholib.dyld.dyld_find(fn)
                while res in self.dylib_excludes:
                    self.dylib_excludes.remove(res)
                self.frameworks.append(res)
        self.plist = plist if plist else {}
        if isinstance(self.plist, str):
            self.plist = plistlib.Plist.fromFile(self.plist)
        if isinstance(self.plist, plistlib.Dict):
            self.plist = dict(self.plist.__dict__)
        else:
            self.plist = dict(self.plist)
        
        self.dist_dir = dist_dir
        self.debug_skip_macholib = debug_skip_macholib
        self.debug_modulegraph = debug_modulegraph
    

class Folders:
    def __init__(self, opts):
        self.bdist_dir = os.path.join(opts.bdist_base, 'python%s-standalone' % (sys.version[:3],), 'app')
        
        self.collect_dir = os.path.abspath(os.path.join(self.bdist_dir, "collect"))
        mkpath(self.collect_dir)
        
        self.temp_dir = os.path.abspath(os.path.join(self.bdist_dir, "temp"))
        mkpath(self.temp_dir)
        
        self.dist_dir = os.path.abspath(opts.dist_dir)
        mkpath(self.dist_dir)
        
        self.ext_dir = os.path.join(self.bdist_dir, 'lib-dynload')
        mkpath(self.ext_dir)
        
        self.framework_dir = os.path.join(self.bdist_dir, 'Frameworks')
        mkpath(self.framework_dir)
        
        # also the directory where the pythonXX.dylib must reside
        app_dir = os.path.dirname(opts.target.get_dest_base())
        if os.path.isabs(app_dir):
            raise Exception("app directory must be relative: %s" % (app_dir,))
        app_dir = os.path.join(self.dist_dir, app_dir)
        mkpath(app_dir)
    

class PluginBuilder:
    def __init__(self, folders, opts):
        self.folders = folders
        self.opts = opts
    
    #--- Plist
    def get_default_plist(self):
        plist = {}
        target = self.opts.target

        version = '0.0.0'
        plist['CFBundleVersion'] = version

        name = 'UNKNOWN'
        if name == 'UNKNOWN':
            base = target.get_dest_base()
            name = os.path.basename(base)
        plist['CFBundleName'] = name

        return plist
    
    def get_plist_options(self):
        return dict(
            PyOptions=dict(
                use_pythonpath=bool(self.opts.use_pythonpath),
                site_packages=bool(self.opts.site_packages),
                alias=bool(self.opts.alias),
                optimize=self.opts.optimize,
            ),
        )
    
    def initialize_plist(self):
        plist = self.get_default_plist()
        plist.update(self.opts.target.plist)
        plist.update(self.opts.plist)
        plist.update(self.get_plist_options())
        self.opts.plist = plist
        return plist
    
    #--- Runtime
    @staticmethod
    def get_runtime(prefix=None, version=None):
        # XXX - this is a bit of a hack!
        #       ideally we'd use dylib functions to figure this out
        if prefix is None:
            prefix = sys.prefix
        if version is None:
            version = sys.version
        version = version[:3]
        info = None
        if os.path.exists(os.path.join(prefix, ".Python")):
            # We're in a virtualenv environment, locate the real prefix
            fn = os.path.join(prefix, "lib", "python%d.%d"%(sys.version_info[:2]), "orig-prefix.txt")
            if os.path.exists(fn):
                prefix = open(fn, 'rU').read().strip()

        try:
            fmwk = macholib.dyld.framework_find(prefix)
        except ValueError:
            info = None
        else:
            info = macholib.dyld.framework_info(fmwk)

        if info is not None:
            dylib = info['name']
            runtime = os.path.join(info['location'], info['name'])
        else:
            dylib = 'libpython%s.dylib' % (sys.version[:3],)
            runtime = os.path.join(prefix, 'lib', dylib)
        return dylib, runtime
    
    #--- Misc pre-build
    def initialize_prescripts(self):
        prescripts = []
        if self.opts.site_packages or self.opts.alias:
            prescripts.append('site_packages')

        if self.opts.argv_inject is not None:
            prescripts.append('argv_inject')
            prescripts.append(
                StringIO('_argv_inject(%r)\n' % (self.opts.argv_inject,)))

        if not self.opts.alias:
            prescripts.append('disable_linecache')
            prescripts.append('boot_plugin')
        else:
            if self.opts.additional_paths:
                prescripts.append('path_inject')
                prescripts.append(
                    StringIO('_path_inject(%r)\n' % (self.opts.additional_paths,)))
            prescripts.append('boot_aliasplugin')
        newprescripts = []
        for s in prescripts:
            if isinstance(s, str):
                newprescripts.append(get_bootstrap('pluginbuilder.bootstrap.' + s))
            else:
                newprescripts.append(s)

        prescripts = self.opts.target.prescripts
        self.opts.target.prescripts = newprescripts + prescripts
    
    def process_recipes(self, mf, filters, flatpackages, loader_files):
        rdict = {}
        for name in dir(recipes):
            if name.startswith('_'):
                continue
            check = getattr(getattr(recipes, name), 'check', None)
            if check is not None:
                rdict[name] = check
        # XXX This control flow below seems rather hacky. Isn't there a better way?
        while True:
            for name, check in rdict.items():
                rval = check(mf)
                if rval is None:
                    continue
                # we can pull this off so long as we stop the iter
                del rdict[name]
                print('*** using recipe: %s ***' % (name,))
                self.opts.packages.update(rval.get('packages', ()))
                for pkg in rval.get('flatpackages', ()):
                    if isinstance(pkg, str):
                        pkg = (os.path.basename(pkg), pkg)
                    flatpackages[pkg[0]] = pkg[1]
                filters.extend(rval.get('filters', ()))
                loader_files.extend(rval.get('loader_files', ()))
                newbootstraps = list(map(get_bootstrap, rval.get('prescripts', ())))

                for fn in newbootstraps:
                    if isinstance(fn, str):
                        mf.run_script(fn)
                self.opts.target.prescripts.extend(newbootstraps)
                break
            else:
                break
    #--- Data manipulation
    def iter_data_files(self):
        for (path, files) in map(normalize_data_file, self.opts.resources):
            for fn in files:
                yield fn, os.path.join(path, os.path.basename(fn))
    
    def iter_frameworks(self):
        for fn in self.opts.frameworks:
            fmwk = macholib.dyld.framework_info(fn)
            if fmwk is None:
                yield fn
            else:
                basename = fmwk['shortname'] + '.framework'
                yield os.path.join(fmwk['location'], basename)
    
    #--- Modulefinder and collect
    def collect_packagedirs(self):
        return list(filter(os.path.exists, [
            os.path.join(os.path.realpath(get_bootstrap(pkg)), '')
            for pkg in self.opts.packages
        ]))
    
    def collect_scripts(self):
        # these contains file names
        target = self.opts.target
        scripts = {target.script,}
        scripts.update(k for k in target.prescripts if isinstance(k, str))
        return scripts
    
    def finalize_modulefinder(self, mf):
        for item in mf.flatten():
            if isinstance(item, Package) and item.filename == '-':
                fn = os.path.join(self.folders.temp_dir, 'empty_package', '__init__.py')
                if not os.path.exists(fn):
                    dn = os.path.dirname(fn)
                    if not os.path.exists(dn):
                        os.makedirs(dn)
                    fp = open(fn, 'w')
                    fp.close()

                item.filename = fn

        py_files, extensions = parse_mf_results(mf)
        py_files = list(py_files)
        extensions = list(extensions)
        return py_files, extensions

    def filter_dependencies(self, mf, filters):
        print("*** filtering dependencies ***")
        nodes_seen, nodes_removed, nodes_orphaned = mf.filterStack(filters)
        print('%d total' % (nodes_seen,))
        print('%d filtered' % (nodes_removed,))
        print('%d orphaned' % (nodes_orphaned,))
        print('%d remaining' % (nodes_seen - nodes_removed,))
    
    def collect_all(self):
        debug = 4 if self.opts.debug_modulegraph else 0
        mf = find_modules(scripts=self.collect_scripts(), includes=self.opts.includes,
            packages=self.opts.packages, excludes=self.opts.excludes, debug=debug)
        filters = [has_filename_filter]
        flatpackages = {}
        loader_files = []
        self.process_recipes(mf, filters, flatpackages, loader_files)

        if self.opts.debug_modulegraph:
            import pdb
            pdb.Pdb().set_trace()

        self.filter_dependencies(mf, filters)

        py_files, extensions = self.finalize_modulefinder(mf)
        pkgdirs = self.collect_packagedirs()
        return py_files, pkgdirs, extensions, loader_files
    
    #--- Build
    def create_bundle(self, target, script):
        plist = self.opts.plist
        base = target.get_dest_base()
        appdir = os.path.join(self.folders.dist_dir, os.path.dirname(base))
        appname = plist['CFBundleName']
        print("*** creating plugin bundle: %s ***" % (appname,))
        dylib, runtime = self.get_runtime()
        if self.opts.alias:
            runtime_location = runtime
        else:
            runtime_location = os.path.join('@executable_path', '..', 'Frameworks', dylib)
        plist.setdefault('PyRuntimeLocation', runtime_location)
        appdir, plist = create_pluginbundle(appdir, appname, plist=plist)
        resdir = os.path.join(appdir, 'Contents', 'Resources')
        return appdir, resdir, plist
    
    def copyexts(self, copyexts, dst):
        for copyext in copyexts:
            fn = os.path.join(dst,
                (copyext.identifier.replace('.', os.sep) +
                os.path.splitext(copyext.filename)[1])
            )
            mkpath(os.path.dirname(fn))
            copy_file_data(copyext.filename, fn, dry_run=self.opts.dry_run)
    
    def build_executable(self, target, copyexts, script):
        # Build an executable for the target
        appdir, resdir, plist = self.create_bundle(target, script)
        self.appdir = appdir
        self.opts.plist = plist

        for src, dest in self.iter_data_files():
            dest = os.path.join(resdir, dest)
            mkpath(os.path.dirname(dest))
            copy_resource(src, dest, dry_run=self.opts.dry_run)

        bootfn = '__boot__'
        bootfile = open(os.path.join(resdir, bootfn + '.py'), 'w')
        for fn in target.prescripts:
            bootfile.write(get_bootstrap_data(fn))
            bootfile.write('\n\n')
        bootfile.write('_run(%r)\n' % (os.path.basename(script),))
        bootfile.close()

        copy_file(script, resdir)
        pydir = os.path.join(resdir, 'lib', 'python' + sys.version[:3])
        mkpath(pydir)
        force_symlink('../../site.py', os.path.join(pydir, 'site.py'))
        realcfg = os.path.dirname(sysconfig.get_makefile_filename())
        cfgdir = os.path.join(resdir, os.path.relpath(realcfg, sys.prefix))
        mkpath(cfgdir)
        for fn in 'Makefile', 'Setup', 'Setup.local', 'Setup.config':
            rfn = os.path.join(realcfg, fn)
            if os.path.exists(rfn):
                copy_file(rfn, os.path.join(cfgdir, fn))

        # see copy_python_framework() for explanation.
        pyconfig_path = sysconfig.get_config_h_filename()
        pyconfig_path_relative = os.path.relpath(os.path.dirname(pyconfig_path), sys.prefix)
        inc_dir = os.path.join(resdir, pyconfig_path_relative)
        mkpath(inc_dir)
        copy_file(pyconfig_path, os.path.join(inc_dir, 'pyconfig.h'))


        copy_tree(self.folders.collect_dir, pydir)
        
        ext_dir = os.path.join(pydir, os.path.basename(self.folders.ext_dir))
        copy_tree(self.folders.ext_dir, ext_dir, preserve_symlinks=True)
        copy_tree(self.folders.framework_dir, os.path.join(appdir, 'Contents', 'Frameworks'), 
            preserve_symlinks=True)
        for pkg in self.opts.packages:
            pkg = get_bootstrap(pkg)
            dst = os.path.join(pydir, os.path.basename(pkg))
            mkpath(dst)
            copy_tree(pkg, dst)
        self.copyexts(copyexts, ext_dir)

        target.appdir = appdir
        return appdir
    
    def build_alias_executable(self, target, script):
        # Build an alias executable for the target
        appdir, resdir, plist = self.create_bundle(target, script)

        # symlink python executable
        execdst = os.path.join(appdir, 'Contents', 'MacOS', 'python')
        prefixPathExecutable = os.path.join(sys.prefix, 'bin', 'python')
        if os.path.exists(prefixPathExecutable):
            pyExecutable = prefixPathExecutable
        else:
            pyExecutable = sys.executable
        force_symlink(pyExecutable, execdst)

        # make PYTHONHOME
        pyhome = os.path.join(resdir, 'lib', 'python' + sys.version[:3])
        realhome = os.path.join(sys.prefix, 'lib', 'python' + sys.version[:3])
        makedirs(pyhome)
        force_symlink('../../site.py', os.path.join(pyhome, 'site.py'))
        force_symlink(os.path.join(realhome, 'config'), os.path.join(pyhome, 'config'))
        
        # symlink data files
        for src, dest in self.iter_data_files():
            dest = os.path.join(resdir, dest)
            if src == dest:
                continue
            makedirs(os.path.dirname(dest))
            force_symlink(os.path.abspath(src), dest)

        # symlink frameworks
        for src in self.iter_frameworks():
            dest = os.path.join(appdir, 'Contents', 'Frameworks', os.path.basename(src))
            if src == dest:
                continue
            makedirs(os.path.dirname(dest))
            force_symlink(os.path.abspath(src), dest)

        bootfn = '__boot__'
        bootfile = open(os.path.join(resdir, bootfn + '.py'), 'w')
        for fn in target.prescripts:
            bootfile.write(get_bootstrap_data(fn))
            bootfile.write('\n\n')
        bootfile.write('try:\n')
        bootfile.write('    _run(%r)\n' % os.path.realpath(script))
        bootfile.write('except KeyboardInterrupt:\n')
        bootfile.write('    pass\n')
        bootfile.close()

        target.appdir = appdir
        return appdir
    
    def create_loader(self, item):
        # Hm, how to avoid needless recreation of this file?
        slashname = item.identifier.replace('.', os.sep)
        pathname = os.path.join(self.folders.temp_dir, "%s.py" % slashname)
        if os.path.exists(pathname):
            if self.opts.verbose:
                print(("skipping python loader for extension %r"
                    % (item.identifier,)))
        else:
            mkpath(os.path.dirname(pathname))
            # and what about dry_run?
            if self.opts.verbose:
                print(("creating python loader for extension %r"
                    % (item.identifier,)))

            fname = slashname + os.path.splitext(item.filename)[1]
            source = make_loader(fname)
            if not self.opts.dry_run:
                open(pathname, "w").write(source)
            else:
                return
        return SourceModule(item.identifier, pathname)
    
    def copy_and_compile_collected(self, dst, py_files, pkgdirs, extensions, loader_files,
            create_ext_loader=True):
        copyexts = []
        def packagefilter(mod, pkgdirs=pkgdirs):
            fn = os.path.realpath(getattr(mod, 'filename', None))
            if fn is None:
                return None
            for pkgdir in pkgdirs:
                if fn.startswith(pkgdir):
                    return None
            return fn
        if pkgdirs:
            py_files = list(filter(packagefilter, py_files))
        for ext in extensions:
            fn = packagefilter(ext)
            if fn is not None:
                if create_ext_loader and '.' in ext.identifier:
                    py_files.append(self.create_loader(ext))
                copyexts.append(ext)
        

        # byte compile the python modules into the target directory
        print("*** byte compile python files ***")
        byte_compile(py_files,
                     target_dir=dst,
                     optimize=self.opts.optimize,
                     force=True,
                     verbose=self.opts.verbose,
                     dry_run=self.opts.dry_run)

        for item in py_files:
            if not isinstance(item, Package): continue
            copy_package_data(item, dst)

        for path, files in loader_files:
            dest = os.path.join(dst, path)
            mkpath(dest)
            for fn in files:
                destfn = os.path.join(dest, os.path.basename(fn))
                if os.path.isdir(fn):
                    copy_tree(fn, destfn, preserve_symlinks=False)
                else:
                    copy_file(fn, destfn)
        return copyexts
    
    def create_binaries(self, py_files, pkgdirs, extensions, loader_files):
        print("*** create binaries ***")
        copyexts = self.copy_and_compile_collected(self.folders.collect_dir, py_files,
            pkgdirs, extensions, loader_files)
        # build the executables
        target = self.opts.target
        dst = self.build_executable(target, copyexts, target.script)
        exp = os.path.join(dst, 'Contents', 'MacOS')
        execdst = os.path.join(exp, 'python')
        if os.path.exists(os.path.join(sys.prefix, ".Python")):
            fn = os.path.join(sys.prefix, "lib", "python%d.%d"%(sys.version_info[:2]), "orig-prefix.txt")
            if os.path.exists(fn):
                prefix = open(fn, 'rU').read().strip()

            rest_path = os.path.normpath(sys.executable)[len(os.path.normpath(sys.prefix))+1:]
            if rest_path.startswith('.'):
                rest_path = rest_path[1:]

            copy_file(os.path.join(prefix, rest_path), execdst)

        else:
            copy_file(sys.executable, execdst)
        if not self.opts.debug_skip_macholib:
            mm = PythonStandalone(dst, executable_path=exp)
            dylib, runtime = self.get_runtime()
            mm.mm.run_file(runtime)
            for exclude in self.opts.dylib_excludes:
                info = macholib.dyld.framework_info(exclude)
                if info is not None:
                    exclude = os.path.join(
                        info['location'], info['shortname'] + '.framework')
                mm.excludes.append(exclude)
            for fmwk in self.opts.frameworks:
                mm.mm.run_file(fmwk)
            platfiles = mm.run()
            if self.opts.strip and not self.opts.dry_run:
                platfiles = strip_dsym(platfiles, self.appdir)
                strip_files_and_report(platfiles, self.opts.verbose)
    
    def run_alias(self):
        self.build_alias_executable(self.opts.target, self.opts.target.script)
    
    def run_normal(self):
        py_files, pkgdirs, extensions, loader_files = self.collect_all()
        self.create_binaries(py_files, pkgdirs, extensions, loader_files)
    
    def run_collect(self, dst):
        py_files, pkgdirs, extensions, loader_files = self.collect_all()
        copyexts = self.copy_and_compile_collected(dst, py_files, pkgdirs, extensions, loader_files,
            create_ext_loader=False)
        self.copyexts(copyexts, dst)

def build_plugin(main_script_path, **options):
    opts = Options(main_script_path, **options)
    folders = Folders(opts)
    builder = PluginBuilder(folders, opts)
    builder.initialize_plist()
    builder.initialize_prescripts()
    
    sys_old_path = sys.path[:]
    try:
        sys.path[:0] = opts.additional_paths
        if opts.alias:
            builder.run_alias()
        else:
            builder.run_normal()
    finally:
        sys.path = sys_old_path

def collect_dependencies(main_script_path, dst, **options):
    opts = Options(main_script_path, **options)
    folders = Folders(opts)
    builder = PluginBuilder(folders, opts)
    builder.run_collect(dst)

def copy_embeddable_python_dylib(dst):
    _, runtime = PluginBuilder.get_runtime()
    filedest = op.join(dst, 'Python')
    shutil.copy(runtime, filedest)
    os.chmod(filedest, 0o774) # We need write permission to use install_name_tool
    cmd = 'install_name_tool -id @rpath/Python %s' % filedest
    os.system(cmd)

def get_python_header_folder():
    return op.dirname(sysconfig.get_config_h_filename())
