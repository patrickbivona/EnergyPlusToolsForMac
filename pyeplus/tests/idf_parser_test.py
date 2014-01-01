import pytest
import os
import eplus
import tests.harness as test


@pytest.fixture
def defs():
    defs = eplus.ClassDefinitions()
    defs.add_class_def(eplus.ClassDefinition('Class'))
    return defs


@pytest.fixture
def parser(defs):
    return eplus.IdfParser(defs)


def test_parses_single_inline_object_without_spaces(parser):
    idf = "Class,value1,value2,value3;"
    expected = ['Class value1 value2 value3'.split(' ')]
    assert_parsing(parser, idf, expected)


def test_parses_single_inline_object_with_spaces_and_return(parser):
    idf = "  \n   Class, value1, \n value2, value3;"
    expected = ['Class value1 value2 value3'.split(' ')]
    assert_parsing(parser, idf, expected)


def test_parses_single_object_on_multiple_lines(parser):
    idf = """Class,\n
      value1,
      value2,
      value3;"""
    expected = ['Class value1 value2 value3'.split(' ')]
    assert_parsing(parser, idf, expected)


def test_accepts_empty_fields_as_empty_strings(parser):
    idf = 'Class,,field,;'
    assert_parsing(parser, idf, [['Class', '', 'field', '']])


def test_accepts_field_comments(parser):
    idf = """Class,
    field1, !- comment1, with ; delimeters for objects
    field2, !- comment2
    field3; !- comment3
    """
    assert_parsing(parser, idf, [['Class', 'field1', 'field2', 'field3']])


def test_accepts_multiwords_string_fields(parser):
    idf = "Class,field with more than 1 word;"
    assert_parsing(parser, idf, [['Class', 'field with more than 1 word']])


def test_accepts_integer_fields(parser):
    idf = "Class,34;"
    assert_parsing(parser, idf, [['Class', '34']])


def test_accepts_float_fields(parser):
    idf = "Class,42.6;"
    assert_parsing(parser, idf, [['Class', '42.6']])


def test_accepts_class_names_with_colons(parser, defs):
    add_class_def(defs, 'Class:With:Colon')
    idf = "Class:With:Colon,42;"
    assert_parsing(parser, idf, [['Class:With:Colon', '42']])


#
# Handling of invalid content
#

def test_parsing_skips_objects_of_unknown_classes(parser):
    objs = parser.parse("Class,field1;\nOtherClass,field2;")
    assert parser.errors == ['Found unsupported object: OtherClass,field2;']
    assert objs == [['Class', 'field1']]


#
# File IO
#

def test_parses_from_file(parser):
    expected = ['Class value1 value2 value3'.split(' ')]
    objects = parser.parse_file(test.path_to_datafile('simple_object.idf'))
    assert objects == expected


def test_writes_objects_to_file(parser):
    filename = test.path_to_datafile('expexted_file.idf')
    if os.path.exists(filename):
        os.remove(filename)
    objects = ['Class value1 value2 value3'.split(' ')]
    parser.write_file(objects, filename, eplus.InlineIdfFormatter())

    os.remove(filename)


def assert_parsing(parser, idf, expected_objects):
    objs = parser.parse(idf)
    assert parser.errors == []
    assert objs == expected_objects


def add_class_def(defs, class_name):
    defs.add_class_def(eplus.ClassDefinition(class_name))
