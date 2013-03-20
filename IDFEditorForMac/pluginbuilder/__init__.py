__version__ = '1.1.0'

# If we import build_plugin as top level imports, then it's impossible to get __version__ without
# importing pluginbuilder's dependencies first. So, import build_plugin only when it's called.

def build_plugin(*args, **kwargs):
    from .build_plugin import build_plugin as real_build_plugin
    real_build_plugin(*args, **kwargs)

def collect_dependencies(*args, **kwargs):
    from .build_plugin import collect_dependencies as real_collect_dependencies
    real_collect_dependencies(*args, **kwargs)

def copy_embeddable_python_dylib(dst):
    from .build_plugin import copy_embeddable_python_dylib as real_copy_embeddable_python_dylib
    return real_copy_embeddable_python_dylib(dst)

def get_python_header_folder():
    from .build_plugin import get_python_header_folder as real_get_python_header_folder
    return real_get_python_header_folder()