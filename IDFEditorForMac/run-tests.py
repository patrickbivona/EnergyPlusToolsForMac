
import subprocess


# build app
subprocess.call('xcodebuild')

# launch test
# a test is a python script that calls OSA instructions
# why not make it a unittest script?
subprocess.call('nosetests', 'tests')

# show result
