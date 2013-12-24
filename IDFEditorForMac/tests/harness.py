import unittest
from PySide.QtGui import QApplication


class PyEplusTestCase(unittest.TestCase):

    def assertIdfFilesContentEquals(self, file1, file2):
        with open(file1, 'r') as f1:
            content1 = f1.read()
        with open(file2, 'r') as f2:
            content2 = f2.read()
        self.assertEquals(content1, content2)

    def assertIdfFileContentEquals(self, file, expected):
        with open(file, 'r') as f:
            content = f.read()
        self.assertEquals(content, expected)


class AppTestCase(PyEplusTestCase):

    def setUp(self):
        qApp = QApplication.instance()
        if qApp is None:
            self.app = QApplication([])
        else:
            self.app = qApp

    def tearDown(self):
        self.app = None
