import unittest


class OpenTypeSaveTestCase(unittest.TestCase):

    def test_open_type_in_new_object_and_save(self):

        defs = {}
        app = launch_app_with_definitions(defs)
        obj = ('Class', 'value1', '2.0')
        app.type_object(obj)
        app.save_to_file('test_file.idf')

        expected = "Class,\
          value1,\
          2.0"
        self.assertIdfFileContentEquals(expected)

    def assertIdfFileContentEquals(self, expected_content):
        self.assertTrue(False)


def launch_app_with_definitions(defs):
    pass
