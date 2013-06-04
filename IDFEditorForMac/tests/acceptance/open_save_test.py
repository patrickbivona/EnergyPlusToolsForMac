import tests.harness as th
import os
import errno


class OpenSaveTestCase(th.AppTestCase):

    def test_open_file_and_save_as_other(self):
        try:
            os.remove('other_file.idf')
        except OSError as e:
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise  # re-raise exception if a different error occured
        self.app_proxy.open_test_idf('test_file.idf')
        self.app_proxy.save_test_idf_as('other_file.idf')
        self.assertIdfFilesContentEquals('test_file.idf', 'other_file.idf')


def app_path():
    return os.path.join(os.getcwd(), '../build/Release/IDFEditorForMac.app')
