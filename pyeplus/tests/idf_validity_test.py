import unittest
import eplus


class IdfValidityTest(unittest.TestCase):

    def setUp(self):
        self.parser = eplus.IdfParser()
        self.class_definitions = {'Class1': eplus.ClassDefinition('Class1', \
                                                                  [eplus.FieldDefinition('Field1', {'type': 'alpha'}), \
                                                                   eplus.FieldDefinition('Field2', {'type': 'integer'})])}

    def test_parses_object_for_valid_class(self):
        idf = "Class1, value1, 2;"
        self._assert_parsing(idf, self.class_definitions, ["Class1 value1 2".split(' ')], [])

    def test_parsing_skips_object_of_unsupported_class(self):
        idf = "Class1, value1, 2;"
        self._assert_parsing(idf, {}, [], ["Missing definition for object of class Class1"])

    def test_parsing_skips_object_with_incorrect_number_of_fields(self):
        idf = "Class1, value1;"
        self._assert_parsing(idf, self.class_definitions, [], ["Incorrect number of fields for class: 1, expected 2"])

    def test_parsing_skips_object_with_incorrect_argument_type(self):
        idf = "Class1, value1, value2"
        self._assert_parsing(idf, self.class_definitions, [], ["Invalid value value2 for field Field2"])

    def _assert_parsing(self, idf, defs, expected_objects, expected_errors):
        (objects, errors) = self.parser.parse(idf, defs)
        self.assertEqual(objects, expected_objects)
        self.assertEqual(errors, expected_errors)
