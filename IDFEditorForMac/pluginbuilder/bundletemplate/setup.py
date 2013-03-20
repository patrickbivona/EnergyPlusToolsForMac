import os
import re
import distutils.sysconfig
import distutils.util
import distutils.ccompiler

def main_executable_path():
    basepath = os.path.dirname(__file__)
    return os.path.join(basepath, 'prebuilt', 'main')

def main():
    basepath = os.path.dirname(__file__)
    dest = main_executable_path()
    src = os.path.join(basepath, 'src', 'main.m')
    if os.path.exists(dest) and (os.stat(dest).st_mtime < os.stat(src).st_mtime):
        return dest

    builddir = os.path.join(basepath, 'prebuilt')
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    cfg = distutils.sysconfig.get_config_vars()
    os.environ['MACOSX_DEPLOYMENT_TARGET'] = cfg['MACOSX_DEPLOYMENT_TARGET']
    CFLAGS = cfg['CFLAGS']
    architectures = re.findall(r'-arch\s+(\S+)', CFLAGS)
    isysroot = re.findall(r'-isysroot\s+(\S+)', CFLAGS)[0]
    compiler = distutils.ccompiler.new_compiler(verbose=True)
    compiler.add_include_dir(distutils.sysconfig.get_python_inc())
    extra_args = []
    for arch in architectures:
        extra_args += ['-arch', arch]
    extra_args += ['-isysroot', isysroot]
    compiler.compile([src], extra_postargs=extra_args)
    obj = compiler.object_filenames([src])[0]
    # add link args to extra args
    extra_args += ['-bundle', '-framework', 'Foundation', '-framework', 'AppKit', '-undefined', 'dynamic_lookup']
    compiler.link_executable([obj], dest, extra_postargs=extra_args)
    os.remove(obj)
    return dest

if __name__ == '__main__':
    if os.path.exists(main_executable_path()):
        os.remove(main_executable_path())
    main()
