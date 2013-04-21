import unittest
import os.path
import subprocess


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
        self._run_ascript("scripts/launch_app.scpt")

    def stop_app(self):
        self._run_ascript("scripts/stop_app.scpt")

    def open_test_idf(self, relative_filepath):
        fullpath = os.path.join(os.getcwd(), relative_filepath)
        filedir, filename = os.path.split(fullpath)
        print(filedir)
        self._run_ascript("scripts/open_idf.scpt", [filedir, filename])

    def save_test_idf_as(self, relative_filepath):
        fullpath = os.path.join(os.getcwd(), relative_filepath)
        destdir = os.path.dirname(fullpath)
        basename = os.path.splitext(os.path.basename(fullpath))[0]
        self._run_ascript("scripts/save_idf_as.scpt", [destdir, basename])

    def click_menuitem(self, menupath):
        self._run_ascript("scripts/click_menuitem.scpt", menupath)

    def _run_ascript(self, script_filepath, script_args=[]):
        subprocess.call(['osascript', script_filepath] + script_args)
