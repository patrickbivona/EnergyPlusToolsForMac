import unittest
import os
import os.path
import subprocess
import time


class PyEplusTestCase(unittest.TestCase):

    def assertIdfFilesContentEquals(self, file1, file2):

        with open(file1, 'r') as f1:
            content1 = f1.read()
        with open(file2, 'r') as f2:
            content2 = f2.read()
        self.assertEquals(content1, content2)


class AppTestCase(PyEplusTestCase):

    def setUp(self):
        self.app_proxy = IdfEditorAppProxy()
        self.app_proxy.launch_app()

    def tearDown(self):
        self.app_proxy.stop_app()


class IdfEditorAppProxy:

    def launch_app(self):
        self._run_ascript("scripts/launch_app.applescript")

    def stop_app(self):
        self._run_ascript("scripts/stop_app.applescript")

    def open_test_idf(self, relative_filepath):
        fullpath = os.path.join(os.getcwd(), relative_filepath)
        filedir, filename = os.path.split(fullpath)
        self._run_ascript("scripts/open_idf.applescript", [filedir, filename])

    def save_test_idf_as(self, relative_filepath):
        fullpath = os.path.join(os.getcwd(), relative_filepath)
        destdir = os.path.dirname(fullpath)
        basename = os.path.splitext(os.path.basename(fullpath))[0]
        self._run_ascript("scripts/save_idf_as.applescript", [destdir, basename])
        # give some time to the OS to write the file to disk
        time.sleep(1)


    def select_menuitem(self, menupath):
        self._run_ascript("scripts/select_menuitem.applescript", menupath)

    def select_class(self, classname):
        self._run_ascript("scripts/select_class.applescript", [classname])

    def input_object(self, fields):
        self._run_ascript("scripts/input_object.applescript", fields)

    def _run_ascript(self, script_filepath, script_args=[]):
        # TODO only compile if .scpt is older than .applescript
        self._compile_applescript(script_filepath)
        subprocess.call(['osascript', script_filepath] + script_args)

    def _compile_applescript(self, script_filepath):
        (base, ext) = os.path.splitext(script_filepath)
        out = base + '.scpt'
        subprocess.call(['osacompile', '-o', out, script_filepath])
