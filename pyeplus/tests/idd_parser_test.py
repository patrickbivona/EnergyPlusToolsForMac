import unittest
import test_harness as test
import eplus


class DataDictionaryParsingTestCase(unittest.TestCase):

    def setUp(self):
        self.idd_parser = eplus.DataDictionaryParser()
        self.idf_parser = eplus.IdfParser()

    def test_recognises_single_class_definition(self):
        definitions = self.idd_parser.parse(test.path_to_datafile('simple_class.idd'))
        print definitions['Class']

        (objects, errors) = self.idf_parser.parse_file(test.path_to_datafile('simple_object.idf'), definitions)

        expected = ['Class value1 value2 value3'.split(' ')]
        self.assertEqual(errors, [])
        self.assertEqual(objects, expected),

    def test_recognises_multiple_class_definitions(self):
        definitions = self.idd_parser.parse(test.path_to_datafile('multiple_classes.idd'))

        (objects, errors) = self.idf_parser.parse_file(test.path_to_datafile('multiple_object.idf'), definitions)

        expected = ['Class1 value1 value2 value3'.split(' '), 'Class2 1 value2 3'.split(' ')]
        self.assertEqual(errors, [])
        self.assertEqual(objects, expected)
