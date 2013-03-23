import unittest
import os
import os.path
import errno
import subprocess
import time


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

    def _run_ascript(self, script_filepath, script_args=[]):
        subprocess.call(['osascript', script_filepath] + script_args)


class OpenTypeSaveTestCase(unittest.TestCase):

    def setUp(self):
        self.app_proxy = IdfEditorAppProxy()

    def tearDown(self):
        self.app_proxy.stop_app()
        pass

    # def test_open_file_in_new_object_and_save(self):

    #     launch_app()
    #     obj = ('Class', 'value1', '2.0')
    #     type_object(obj)
    #     save_to_file('test_file.idf')

    #     expected = "Class,\
    #       value1,\
    #       2.0"
    #     self.assertIdfFileContentEquals(expected)

    def test_open_file_and_save_as_other(self):
        try:
            os.remove('other_file.idf')
        except OSError as e:
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise  # re-raise exception if a different error occured
        self.app_proxy.launch_app()
        self.app_proxy.open_test_idf('test_file.idf')
        self.app_proxy.save_test_idf_as('other_file.idf')
        time.sleep(1)
        self.assertIdfFilesContentEquals('test_file.idf', 'other_file.idf')

    def assertIdfFileContentEquals(self, expected_content):
        self.assertTrue(False)

    def assertIdfFilesContentEquals(self, file1, file2):
        with open(file1, 'r') as f1:
            content1 = f1.read()
        with open(file2, 'r') as f2:
            content2 = f2.read()
        self.assertEquals(content1, content2)


def app_path():
    return os.path.join(os.getcwd(), '../build/Release/IDFEditorForMac.app')
