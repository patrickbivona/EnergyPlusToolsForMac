import tests.harness
import os
import errno
import pyplugin


class BridgeTestCase(tests.harness.PyEplusTestCase):

    def setUp(self):
        self.bridge = pyplugin.PyIdfFileIO()

    def test_open_returns_empty_list_when_file_does_not_exist(self):
        objs = self.bridge.readEplusObjectsFromFile_('file/does/not/exist.idf')
        self.assertEquals(len(objs), 0)

    def test_open_returns_objects_for_valid_file(self):
        objs = self.bridge.readEplusObjectsFromFile_('test_file.idf')
        self.assertEquals(len(objs), 2)
        self.assertEquals(objs[0], "Version,7.2".split(','))
        self.assertEquals(objs[1], "ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless".split(','))

    def test_writes_objects_read_from_file(self):
        try:
            os.remove('other_file.idf')
        except OSError as e:
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise  # re-raise exception if a different error occured
        objs = self.bridge.readEplusObjectsFromFile_('test_file.idf')
        self.bridge.writeEplusObjects_toFile_(objs, 'other_file.idf')
        self.assertIdfFilesContentEquals('test_file.idf', 'other_file.idf')
