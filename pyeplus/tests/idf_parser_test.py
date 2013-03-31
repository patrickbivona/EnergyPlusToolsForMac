import unittest
import os
import eplus
import tests.harness as test


class IdfParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = eplus.IdfParser()
        self.single_allowed_class = {'Class': eplus.ClassDefinition('Class', [self._make_alpha_field("A" + str(n)) for n in range(3)])}
        self.two_allowed_classes = {'Class1': eplus.ClassDefinition('Class1', [self._make_alpha_field("A" + str(n)) for n in range(3)]),
                                    'Class2': eplus.ClassDefinition('Class2', [self._make_alpha_field("A" + str(n)) for n in range(3)])}

    def test_parses_single_inline_object_without_spaces(self):
        idf = "Class,value1,value2,value3;"
        expected = ['Class value1 value2 value3'.split(' ')]
        self._assert_parsing(idf, self.single_allowed_class, expected)

    def test_parses_single_inline_object_with_spaces_and_cr(self):
        idf = "  \n   Class, value1, value2, value3;"
        expected = ['Class value1 value2 value3'.split(' ')]
        self._assert_parsing(idf, self.single_allowed_class, expected)

    def test_parses_single_object_on_multiple_lines(self):
        idf = """Class,\n
          value1,
          value2,
          value3;"""
        expected = ['Class value1 value2 value3'.split(' ')]
        self._assert_parsing(idf, self.single_allowed_class, expected)

    def test_parses_multiple_objects_of_same_class(self):
        idf = "Class,value1,value2,value3;\n\
               Class,value4,value5,value6;"
        expected = ['Class value1 value2 value3'.split(' '), 'Class value4 value5 value6'.split(' ')]
        self._assert_parsing(idf, self.single_allowed_class, expected)

    def test_parses_multiple_objects_of_different_class(self):
        idf = "Class1,value1,value2,value3;\n\
               Class2,value4,value5,value6;"
        expected = ['Class1 value1 value2 value3'.split(' '), 'Class2 value4 value5 value6'.split(' ')]
        self._assert_parsing(idf, self.two_allowed_classes, expected)

    def test_parses_from_file(self):
        expected = ['Class value1 value2 value3'.split(' ')]
        (objects, errors) = self.parser.parse_file(test.path_to_datafile('simple_object.idf'), self.single_allowed_class)
        self.assertEqual(objects, expected)
        self.assertEqual(errors, [])

    def test_writes_objects_to_file(self):
        filename = test.path_to_datafile('expexted_file.idf')
        if os.path.exists(filename):
            os.remove(filename)
        objects = ['Class value1 value2 value3'.split(' ')]
        self.parser.write_file(objects, filename)

        os.remove(filename)

    def _make_alpha_field(self, id):
        return eplus.FieldDefinition(id, {'type': 'alpha'})

    def _assert_parsing(self, idf, defs, expected_objects):
        (objects, errors) = self.parser.parse(idf, defs)
        self.assertEqual(objects, expected_objects)
        self.assertEqual(errors, [])
