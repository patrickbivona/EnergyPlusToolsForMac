import pytest
import eplus


@pytest.fixture
def parser():
    return eplus.DataDictionaryParser()


def test_skips_class_level_attributes_for_now(parser):
    idd = """
Class,
\\memo Some comment
A1 ; \\field Field"""
    defs = parser.parse(idd)
    assert len(defs) == 1


def test_accepts_alpha_fields(parser):
    idd = """
    Class,
      A1; \\field Field1
          \\type alpha
    """
    defs = parser.parse(idd)
    class_def = defs.class_def('Class')
    assertField(class_def.fields[0], 'A1', 'Field1', 'alpha')


def test_accepts_integer_fields(parser):
    idd = """
    Class,
      N1; \\field Field1
          \\type integer
    """
    defs = parser.parse(idd)
    class_def = defs.class_def('Class')
    assertField(class_def.fields[0], 'N1', 'Field1', 'integer')


def test_parses_definitions_on_multiple_lines(parser):
    idd = """
    Class,
      A1; \\field Field1
          \\type alpha
    OtherClass,
      N1; \\field Field1
          \\type integer
    """
    defs = parser.parse(idd)
    assert 'Class' in defs.class_names()
    assert 'OtherClass' in defs.class_names()


def test_allows_using_bracket_operator_to_find_class_def(parser):
    idd = "Class,A1; \\field Field"
    defs = parser.parse(idd)
    assert defs['Class'].name == 'Class'


def assertField(field, expected_id, expected_name, expected_type):
    assert field.id == expected_id
    assert field.attributes['field'] == expected_name
    assert field.attributes['type'] == expected_type
