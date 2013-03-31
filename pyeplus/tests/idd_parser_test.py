import unittest
import tests.harness as test
import eplus


class DataDictionaryParsingTestCase(unittest.TestCase):

    def setUp(self):
        self.idd_parser = eplus.DataDictionaryParser()
        self.idf_parser = eplus.IdfParser()

    def test_accepts_alpha_fields(self):
        idd = """
        Class1,
          A1; \\field Field1
              \\type alpha
        """
        class_def = self.idd_parser.parse(idd)['Class1']
        self.assertField(class_def.fields[0], 'A1', 'Field1', 'alpha')

    def test_accepts_integer_fields(self):
        idd = """
        Class1,
          N1; \\field Field1
              \\type integer
        """
        class_def = self.idd_parser.parse(idd)['Class1']
        self.assertField(class_def.fields[0], 'N1', 'Field1', 'integer')

    def test_recognises_single_class_definition(self):
        class_defs = self.idd_parser.parse_file(test.path_to_datafile('simple_class.idd'))

        (objects, errors) = self.idf_parser.parse_file(test.path_to_datafile('simple_object.idf'), class_defs)

        expected = ['Class value1 value2 value3'.split(' ')]
        self.assertEqual(errors, [])
        self.assertEqual(objects, expected)

    def test_recognises_multiple_class_definitions(self):
        definitions = self.idd_parser.parse_file(test.path_to_datafile('multiple_classes.idd'))

        (objects, errors) = self.idf_parser.parse_file(test.path_to_datafile('multiple_objects.idf'), definitions)

        expected = ['Class1 alpha1 alpha2 alpha3'.split(' '), 'Class2 1 2 alpha3'.split(' ')]
        self.assertEqual(errors, [])
        self.assertEqual(objects, expected)

    def assertField(self, field, expected_id, expected_name, expected_type):
        self.assertEquals(field.id, expected_id)
        self.assertEquals(field.attributes['field'], expected_name)
        self.assertEquals(field.attributes['type'], expected_type)
