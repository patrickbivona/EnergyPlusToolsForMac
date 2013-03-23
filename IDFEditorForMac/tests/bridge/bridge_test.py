import unittest
import pyplugin


class BridgeTestCase(unittest.TestCase):

    def setUp(self):
        self.bridge = pyplugin.PyIdfFileIO()

    def test_open_returns_empty_list_when_file_does_not_exist(self):
        objs = self.bridge.readEplusObjectsFromFile_('file/does/not/exist.idf')
        self.assertEquals(len(objs), 0)
