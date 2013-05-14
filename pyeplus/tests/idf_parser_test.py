import unittest
import os
import eplus
import tests.harness as test


class IdfParserTest(unittest.TestCase):

    def setUp(self):
        self.defs = eplus.ClassDefinitions()
        self.defs.add_class('Class')
        self.p = eplus.IdfParser(self.defs)

    def test_parses_single_inline_object_without_spaces(self):
        idf = "Class,value1,value2,value3;"
        expected = ['Class value1 value2 value3'.split(' ')]
        self._assert_parsing(idf, expected)

    def test_parses_single_inline_object_with_spaces_and_cr(self):
        idf = "  \n   Class, value1, \n value2, value3;"
        expected = ['Class value1 value2 value3'.split(' ')]
        self._assert_parsing(idf, expected)

    def test_parses_single_object_on_multiple_lines(self):
        idf = """Class,\n
          value1,
          value2,
          value3;"""
        expected = ['Class value1 value2 value3'.split(' ')]
        self._assert_parsing(idf, expected)

    def test_accepts_field_comments(self):
        idf = """Class,
        field1, !- comment1, with ; delimeters for objects
        field2, !- comment2
        field3; !- comment3
        """
        self._assert_parsing(idf, [['Class', 'field1', 'field2', 'field3']])

    def test_accepts_multiwords_string_fields(self):
        idf = """Class,field with more than 1 word;"""
        self._assert_parsing(idf, [['Class', 'field with more than 1 word']])

    def test_accepts_integer_fields(self):
        idf = """Class,34;"""
        self._assert_parsing(idf, [['Class', '34']])

    def test_accepts_float_fields(self):
        idf = """Class,42.6;"""
        self._assert_parsing(idf, [['Class', '42.6']])

    #
    # Handling of invalid content
    #

    def test_parsing_skips_objects_of_unknown_classes(self):
        objs = self.p.parse("Class,field1;\nclass2,field2;")
        self.assertEquals(objs, [['Class', 'field1']])
        self.assertEquals(self.p.errors, ['Found unsupported object'])

    #
    # File IO
    #

    def test_parses_from_file(self):
        expected = ['Class value1 value2 value3'.split(' ')]
        objects = self.p.parse_file(test.path_to_datafile('simple_object.idf'))
        self.assertEqual(objects, expected)

    def test_writes_objects_to_file(self):
        filename = test.path_to_datafile('expexted_file.idf')
        if os.path.exists(filename):
            os.remove(filename)
        objects = ['Class value1 value2 value3'.split(' ')]
        self.p.write_file(objects, filename)

        os.remove(filename)

    def _assert_parsing(self, idf, expected_objects):
        self.assertEqual(self.p.parse(idf), expected_objects)
