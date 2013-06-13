import unittest
import os
import eplus


class IdfFormattingTestCase(unittest.TestCase):

    def setUp(self):
        self.p = eplus.IdfParser(eplus.NoddingClassDefinitions())
        self.objs = [
            "Version,8.0".split(','),
            "ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless".split(',')
        ]
        if os.path.exists('test_file.idf'):
            os.remove('test_file.idf')

    def tearDown(self):
        if os.path.exists('test_file.idf'):
            os.remove('test_file.idf')

    def test_inline_formatting(self):

        self.p.write_file(self.objs, 'test_file.idf', eplus.InlineIdfFormatter())

        expected = """Version,8.0;
ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless;
"""
        self._assertIdfFileContentEquals('test_file.idf', expected)

    def test_pretty_formatting_without_comments(self):
        if os.path.exists('test_file.idf'):
            os.remove('test_file.idf')

        expected = """Version,
    8.0;

ScheduleTypeLimits,
    Fraction,
    0,
    1,
    Continuous,
    Dimensionless;

"""
        self.p.write_file(self.objs, 'test_file.idf', eplus.PrettyIdfFormatter(False))
        self._assertIdfFileContentEquals('test_file.idf', expected)

    def _assertIdfFileContentEquals(self, file, expected):
        with open(file, 'r') as f:
            content = f.read()
        self.assertEquals(content, expected)
