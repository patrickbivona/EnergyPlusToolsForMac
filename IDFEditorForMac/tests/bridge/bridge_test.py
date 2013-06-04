import tests.harness as th
import os
import errno
import pyplugin


class BridgeTestCase(th.PyEplusTestCase):

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

    def test_returns_only_classes_with_objects_with_count(self):
        self.doc.readFromFile_('test_file.idf')
        class_count = self.doc.onlyClassesWithObjectsWithObjectCount()
        self.assertEquals(len(class_count), 2)
        self.assertEquals(class_count['Version'], 1)
        self.assertEquals(class_count['ScheduleTypeLimits'], 2)

    def test_returns_all_classes_with_count(self):
        self.doc.readFromFile_('test_file.idf')

        classes = self.doc.allClassesWithObjectCount()

        self.assertEquals(len(classes), 3)
        self.assertEquals(classes['Version'], 1)
        self.assertEquals(classes['ScheduleTypeLimits'], 2)
        self.assertEquals(classes['Timestep'], 0)

    def test_objects_for_class_leaves_other_objects_out(self):
        self.doc.readFromFile_('test_file.idf')
        only_version = self.doc.objectsOfClass_('Version')
        self.assertEquals(only_version[0][0], 'Version')
        only_schedule_type_limits = self.doc.objectsOfClass_('ScheduleTypeLimits')
        self.assertEquals(only_schedule_type_limits[0][0], 'ScheduleTypeLimits')
        self.assertEquals(only_schedule_type_limits[1][0], 'ScheduleTypeLimits')

    def test_fields_of_class(self):
        self.doc.readFromFile_('test_file.idf')
        self.assertEquals(self.doc.fieldsOfClass_('Version'), ['Version Identifier'])
        self.assertEquals(self.doc.fieldsOfClass_('ScheduleTypeLimits'), ['Name', 'Lower Limit Value', 'Upper Limit Value', 'Numeric Type', 'Unit Type'])
        self.assertEquals(self.doc.fieldsOfClass_('Timestep'), ['Number of Timesteps per Hour'])

    def test_new_object_returns_empty_object_with_class_name(self):
        self.doc.addEmptyObject_('ScheduleTypeLimits')
        self.assertEquals(self.doc.objectsOfClass_('ScheduleTypeLimits'), ['ScheduleTypeLimits,,,,,'.split(',')])

    def test_returns_object_of_class_at_index(self):
        self.doc.readFromFile_('test_file.idf')
        self.assertEquals(self.doc.objectOfClass_atIndex_('Version', 0), ['Version', '7.2'])
        self.assertEquals(self.doc.objectOfClass_atIndex_('Version', 1), [])

    def test_replaces_object_at_index(self):
        self.doc.readFromFile_('test_file.idf')
        self.doc.replaceObjectAtIndex_withObject_(0, ['Version', '8.0'])
        self.assertEquals(self.doc.objectsOfClass_('Version'), [['Version', '8.0']])


