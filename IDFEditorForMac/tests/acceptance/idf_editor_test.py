import tests.harness as th
import os
import errno
from idf_editor import IdfEditorWindow


class IdfEditorTestCase(th.AppTestCase):

    def setUp(self):
        super(IdfEditorTestCase, self).setUp()
        self.window = IdfEditorWindow()

    def test_open_file_and_save_as_other(self):
        try:
            os.remove('other_file.idf')
        except OSError as e:
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise  # re-raise exception if a different error occured
        self.window.openFile('test_file.idf')
        self.window.saveFileAs('other_file.idf')
        self.assertIdfFilesContentEquals('test_file.idf', 'other_file.idf')


    def test_can_toggle_show_classes_with_objects_only(self):        
        
        self.window.openFile('test_file.idf')

        self.window.showClassesWithObjectsOnly(False)
        self.assertEquals(set(self.window.classes()), set(['Version', 'ScheduleTypeLimits', 'Timestep']))
        
        self.window.showClassesWithObjectsOnly(True)
        self.assertEquals(set(self.window.classes()), set(['Version', 'ScheduleTypeLimits']))
        