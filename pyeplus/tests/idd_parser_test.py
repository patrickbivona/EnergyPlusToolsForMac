import unittest
import eplus


class DataDictionaryParsingTestCase(unittest.TestCase):

    def setUp(self):
        self.p = eplus.DataDictionaryParser()

    def test_skips_class_level_attributes_for_now(self):
        idd = """
Class,
    \\memo Some comment
    A1 ; \\field Field"""
        defs = self.p.parse(idd)
        self.assertEquals(len(defs), 1)

    def test_accepts_alpha_fields(self):
        idd = """
        Class,
          A1; \\field Field1
              \\type alpha
        """
        defs = self.p.parse(idd)
        class_def = defs.class_def('Class')
        self.assertField(class_def.fields[0], 'A1', 'Field1', 'alpha')

    def test_accepts_integer_fields(self):
        idd = """
        Class,
          N1; \\field Field1
              \\type integer
        """
        defs = self.p.parse(idd)
        class_def = defs.class_def('Class')
        self.assertField(class_def.fields[0], 'N1', 'Field1', 'integer')

    def test_parses_definitions_on_multiple_lines(self):
        idd = """
        Class,
          A1; \\field Field1
              \\type alpha
        OtherClass,
          N1; \\field Field1
              \\type integer
        """
        defs = self.p.parse(idd)
        self.assertTrue('Class' in defs.class_names())
        self.assertTrue('OtherClass' in defs.class_names())

    def test_allows_using_bracket_operator_to_find_class_def(self):
        idd = "Class,A1; \\field Field"
        defs = self.p.parse(idd)
        self.assertEquals(defs['Class'].name, 'Class')

    def assertField(self, field, expected_id, expected_name, expected_type):
        self.assertEquals(field.id, expected_id)
        self.assertEquals(field.attributes['field'], expected_name)
        self.assertEquals(field.attributes['type'], expected_type)
