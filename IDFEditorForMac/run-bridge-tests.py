import sys
import os
import os.path
import nose

sys.path.append(os.path.join(os.getcwd(), '../pyeplus'))
os.chdir('tests/bridge')
nose.main()
