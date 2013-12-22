import sys
import os
import os.path

sys.path.append(os.path.join(os.getcwd(), '../pyeplus'))


def build():
    pass


def run_acceptance_tests(tests):
    os.chdir('tests/acceptance')
    os.system('nosetests-3.3 ' + ' '.join(tests))
    os.chdir('../..')

if __name__ == '__main__':

    allowed_cmds = ['build', 'test']

    if len(sys.argv) < 2 or sys.argv[1] not in allowed_cmds:
        print("Usage: python setup.py " + '|'.join(allowed_cmds))
        sys.exit()
    cmd = sys.argv[1]
    if cmd == 'build':
        build()
    if cmd == 'test':
        run_acceptance_tests(sys.argv[2:])
