import tests.harness
import os
import errno
import pyplugin


class BridgeTestCase(tests.harness.PyEplusTestCase):

    def setUp(self):
        self.doc = pyplugin.PyIdfDocument()

    def test_read_returns_empty_list_when_file_does_not_exist(self):
        self.doc.readFromFile_('file/does/not/exist.idf')
        self.assertEquals(len(self.doc.objs), 0)

    def test_read_returns_objects_for_valid_file(self):
        self.doc.readFromFile_('test_file.idf')
        self.assertEquals(len(self.doc.objs), 3)
        self.assertEquals(self.doc.objs[0], "Version,7.2".split(','))
        self.assertEquals(self.doc.objs[1], "ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless".split(','))
        self.assertEquals(self.doc.objs[2], "ScheduleTypeLimits,Comfort Temperature,19,26,Continuous,Temperature".split(','))

    def test_writes_objects_read_from_file(self):
        try:
            os.remove('other_file.idf')
        except OSError as e:
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise  # re-raise exception if a different error occured
        self.doc.readFromFile_('test_file.idf')
        self.doc.writeToFile_('other_file.idf')
        self.assertIdfFilesContentEquals('test_file.idf', 'other_file.idf')

    def test_returns_object_classes_with_count(self):
        self.doc.readFromFile_('test_file.idf')
        class_count = self.doc.classesWithObjectCount()
        self.assertEquals(len(class_count), 2)
        self.assertEquals(class_count['Version'], 1)
        self.assertEquals(class_count['ScheduleTypeLimits'], 2)

    def test_objects_for_class_leaves_other_objects_out(self):
        self.doc.readFromFile_('test_file.idf')
        only_version = self.doc.objectsOfClass_('Version')
        self.assertEquals(only_version[0][0], 'Version')
        only_schedule_type_limits = self.doc.objectsOfClass_('ScheduleTypeLimits')
        self.assertEquals(only_schedule_type_limits[0][0], 'ScheduleTypeLimits')
        self.assertEquals(only_schedule_type_limits[1][0], 'ScheduleTypeLimits')
