import os
import os.path
import subprocess
import shutil
import objp.o2p
import pyplugin

objp.o2p.generate_objc_code(pyplugin.PyIdfFileIO, os.path.join('.', 'autogen'))

pydest = 'build/py'
if not os.path.exists(pydest):
    os.mkdir(pydest)
shutil.copy(os.path.join('.', 'pyplugin.py'), pydest)
# For some strange reason, a "site.py" file is required at pydest.
with open(os.path.join('build/py', 'site.py'), 'w'):
    pass

from pluginbuilder import copy_embeddable_python_dylib, collect_dependencies
copy_embeddable_python_dylib('build')
collect_dependencies(os.path.join('.', 'pyplugin.py'), 'build/py')

from pluginbuilder import get_python_header_folder
if not os.path.exists('build/PythonHeaders'):
    os.symlink(get_python_header_folder(), 'build/PythonHeaders')

# build app
subprocess.call('xcodebuild')

# launch test
# a test is a python script that calls OSA instructions
# why not make it a unittest script?
#subprocess.call('nosetests', 'tests')

# show result
