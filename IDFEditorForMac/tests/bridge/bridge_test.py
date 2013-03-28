import unittest
import pyplugin
import eplus


class BridgeTestCase(unittest.TestCase):

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
