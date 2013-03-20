import os, sys, zipfile, time
from modulegraph.find_modules import PY_SUFFIXES
from modulegraph.modulegraph import os_listdir
import macholib.util

def os_path_islink(path):
    """
    os.path.islink with zipfile support.

    Luckily zipfiles cannot contain symlink, therefore the implementation is
    trivial.
    """
    return os.path.islink(path)

def os_readlink(path):
    """
    os.readlink with zipfile support.

    Luckily zipfiles cannot contain symlink, therefore the implementation is
    trivial.
    """
    return os.readlink(path)

def os_path_isdir(path):
    """
    os.path.isdir that understands zipfiles.

    Assumes that you're checking a path the is the result of os_listdir and 
    might give false positives otherwise.
    """
    while path.endswith('/') and path != '/':
        path = path[:-1]

    zf, zp = path_to_zip(path)
    if zf is None:
        return os.path.isdir(zp)

    else:
        zip = zipfile.ZipFile(zf)
        try:
            info = zip.getinfo(zp)

        except KeyError:
            return True

        else:
            # Not quite true, you can store information about directories in
            # zipfiles, but those have a lash at the end of the filename
            return False

def copy_resource(source, destination, dry_run=0):
    """
    Copy a resource file into the application bundle
    """
    if os.path.isdir(source):
        # XXX: This is wrong, need to call ourselves recursively
        if not dry_run:
            if not os.path.exists(destination):
                os.mkdir(destination)
        for fn in os_listdir(source):
            copy_resource(os.path.join(source, fn), 
                    os.path.join(destination, fn), dry_run=dry_run)

    else:
        copy_file_data(source, destination, dry_run=dry_run)



def copy_file_data(source, destination, dry_run=0):
    zf, zp = path_to_zip(source)
    if zf is None:
        data = open(zp,'rb').read()
    else:
        data = get_zip_data(zf, zp)

    if not dry_run:
        fp = open(destination, 'wb')
        fp.write(data)
        fp.close()

def get_zip_data(path_to_zip, path_in_zip):
    zf = zipfile.ZipFile(path_to_zip)
    return zf.read(path_in_zip)

def path_to_zip(path):
    """
    Returns (pathtozip, pathinzip). If path isn't in a zipfile pathtozip
    will be None
    """
    orig_path = path
    from distutils.errors import DistutilsFileError
    if os.path.exists(path):
        return (None, path)

    else:
        rest = ''
        while not os.path.exists(path):
            path, r = os.path.split(path)
            if not path:
                raise DistutilsFileError("File doesn't exist: %s"%(orig_path,))
            rest = os.path.join(r, rest)

        if not os.path.isfile(path):
            # Directory really doesn't exist
            raise DistutilsFileError("File doesn't exist: %s"%(orig_path,))

        try:
           zf = zipfile.ZipFile(path)
        except zipfile.BadZipfile:
            raise DistutilsFileError("File doesn't exist: %s"%(orig_path,))

        if rest.endswith('/'):
            rest = rest[:-1]

        return path, rest


def get_mtime(path, mustExist=True):
    """
    Get mtime of a path, even if it is inside a zipfile
    """

    try:
        return os.stat(path).st_mtime

    except os.error:
        from distutils.errors import DistutilsFileError
        try:
            path, rest = path_to_zip(path)
        except DistutilsFileError:
            if not mustExist:
                return -1
            raise

        zf = zipfile.ZipFile(path)
        info = zf.getinfo(rest)
        return time.mktime(info.date_time + (0, 0, 0))

def newer(source, target):
    """
    distutils.dep_utils.newer with zipfile support
    """

    msource = get_mtime(source)
    mtarget = get_mtime(target, mustExist=False)

    return msource > mtarget

def is_python_package(path):
    """Returns whether `path` is a python package (has a __init__.py(c|o) file).
    """
    if os_path_isdir(path):
        for p in os_listdir(path):
            if p.startswith('__init__.') and p[8:] in {'.py', '.pyc', '.pyo'}:
                return True
    return False

def make_exec(path):
    mask = os.umask(0)
    os.umask(mask)
    os.chmod(path, os.stat(path).st_mode | (0o111 & ~mask))

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def mergecopy(src, dest):
    return macholib.util.mergecopy(src, dest)

def mergetree(src, dst, condition=None, copyfn=mergecopy):
    """Recursively merge a directory tree using mergecopy()."""
    return macholib.util.mergetree(src, dst, condition=condition, copyfn=copyfn)

def move(src, dst):
    return macholib.util.move(src, dst)

LOADER = """
def __load():
    import imp, os, sys, os.path
    ext = %r
    library_path = os.environ['LIBRARYPATH']
    dynload_path = os.path.join(library_path, 'lib-dynload')
    ext = os.path.join(dynload_path, ext)
    if os.path.exists(ext):
        mod = imp.load_dynamic(__name__, ext)
    else:
        raise ImportError(repr(ext) + " not found")
__load()
del __load
"""

def make_loader(fn):
    return LOADER % fn

def byte_compile(py_files, optimize=0, force=0,
                 target_dir=None, verbose=1, dry_run=0,
                 direct=None):

    if direct is None:
        direct = (__debug__ and optimize == 0)

    # "Indirect" byte-compilation: write a temporary script and then
    # run it with the appropriate flags.
    if not direct:
        from tempfile import mktemp
        from distutils.util import execute, spawn
        script_name = mktemp(".py")
        if verbose:
            print("writing byte-compilation script '%s'" % script_name)
        if not dry_run:
            script = open(script_name, "w")
            script.write("""
from pluginbuilder.util import byte_compile
from modulegraph.modulegraph import *
files = [
""")

            for f in py_files:
                script.write(repr(f) + ",\n")
            script.write("]\n")
            script.write("""
byte_compile(files, optimize=%r, force=%r,
             target_dir=%r,
             verbose=%r, dry_run=0,
             direct=1)
""" % (optimize, force, target_dir, verbose))

            script.close()

        cmd = [sys.executable, script_name]
        if optimize == 1:
            cmd.insert(1, "-O")
        elif optimize == 2:
            cmd.insert(1, "-OO")
        spawn(cmd, verbose=verbose, dry_run=dry_run)
        execute(os.remove, (script_name,), "removing %s" % script_name,
                verbose=verbose, dry_run=dry_run)


    else:
        from py_compile import compile
        from distutils.dir_util import mkpath

        for mod in py_files:
            # Terminology from the py_compile module:
            #   cfile - byte-compiled file
            #   dfile - purported source filename (same as 'file' by default)
            if mod.filename == mod.identifier:
                cfile = os.path.basename(mod.filename)
                dfile = cfile + (__debug__ and 'c' or 'o')
            else:
                cfile = mod.identifier.replace('.', os.sep)

                if mod.packagepath:
                    dfile = cfile + os.sep + '__init__.py' + (__debug__ and 'c' or 'o')
                else:
                    dfile = cfile + '.py' + (__debug__ and 'c' or 'o')
            if target_dir:
                cfile = os.path.join(target_dir, dfile)

            if force or newer(mod.filename, cfile):
                if verbose:
                    print("byte-compiling %s to %s" % (mod.filename, dfile))
                if not dry_run:
                    mkpath(os.path.dirname(cfile))
                    suffix = os.path.splitext(mod.filename)[1]

                    if suffix in ('.py', '.pyw'):
                        zfile, pth = path_to_zip(mod.filename)
                        if zfile is None:
                            compile(mod.filename, cfile, dfile)
                        else:
                            fn = dfile + '.py'
                            open(fn, 'wb').write(get_zip_data(zfile, pth))
                            compile(mod.filename, cfile, dfile)
                            os.unlink(fn)

                    elif suffix in PY_SUFFIXES:
                        # Minor problem: This will happily copy a file
                        # <mod>.pyo to <mod>.pyc or <mod>.pyc to
                        # <mod>.pyo, but it does seem to work.
                        copy_file_data(mod.filename, cfile)
                    else:
                        raise RuntimeError \
                              ("Don't know how to handle %r" % mod.filename)
            else:
                if verbose:
                    print("skipping byte-compilation of %s to %s" % \
                          (mod.filename, dfile))

SCMDIRS = {'CVS', '.svn', '.hg', '.git'}
def skipscm(ofn):
    fn = os.path.basename(ofn)
    if fn in SCMDIRS:
        return False
    return True

def iter_platform_files(path, is_platform_file=macholib.util.is_platform_file):
    """
    Iterate over all of the platform files in a directory
    """
    for root, dirs, files in os.walk(path):
        for fn in files:
            fn = os.path.join(root, fn)
            if is_platform_file(fn):
                yield fn

def copy_tree(src, dst,
        preserve_mode=1,
        preserve_times=1,
        preserve_symlinks=0,
        update=0,
        verbose=0,
        dry_run=0,
        condition=None):

    """
    Copy an entire directory tree 'src' to a new location 'dst'.  Both
    'src' and 'dst' must be directory names.  If 'src' is not a
    directory, raise DistutilsFileError.  If 'dst' does not exist, it is
    created with 'mkpath()'.  The end result of the copy is that every
    file in 'src' is copied to 'dst', and directories under 'src' are
    recursively copied to 'dst'.  Return the list of files that were
    copied or might have been copied, using their output name.  The
    return value is unaffected by 'update' or 'dry_run': it is simply
    the list of all files under 'src', with the names changed to be
    under 'dst'.

    'preserve_mode' and 'preserve_times' are the same as for
    'copy_file'; note that they only apply to regular files, not to
    directories.  If 'preserve_symlinks' is true, symlinks will be
    copied as symlinks (on platforms that support them!); otherwise
    (the default), the destination of the symlink will be copied.
    'update' and 'verbose' are the same as for 'copy_file'.
    """
    assert isinstance(src, str), repr(src)
    assert isinstance(dst, str), repr(dst)


    from distutils.dir_util import mkpath
    from distutils.file_util import copy_file
    from distutils.dep_util import newer
    from distutils.errors import DistutilsFileError
    from distutils import log

    if condition is None:
        condition = skipscm

    if not dry_run and not os_path_isdir(src):
        raise DistutilsFileError("cannot copy tree '%s': not a directory" % src)
    try:
        names = os_listdir(src)
    except os.error as xxx_todo_changeme:
        (errno, errstr) = xxx_todo_changeme.args
        if dry_run:
            names = []
        else:
            raise DistutilsFileError("error listing files in '%s': %s" % (src, errstr))

    if not dry_run:
        mkpath(dst)

    outputs = []

    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)
        if (condition is not None) and (not condition(src_name)):
            continue

        if preserve_symlinks and os_path_islink(src_name):
            link_dest = os_readlink(src_name)
            log.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                if update and not newer(src, dst_name):
                    pass
                else:
                    if os_path_islink(dst_name):
                        os.remove(dst_name)
                    os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        elif os_path_isdir(src_name):
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          dry_run=dry_run, condition=condition))
        else:
            copy_file(src_name, dst_name, preserve_mode,
                      preserve_times, update, dry_run=dry_run)
            outputs.append(dst_name)

    return outputs
