import pytest
import os
import errno
import tests.harness as th
from idf_doc import IdfDocument


@pytest.fixture
def doc():
    return IdfDocument()


def test_doc_is_empty(doc):
    assert doc.isEmpty()

    doc.addEmptyObject("Version")
    assert not doc.isEmpty()


def test_read_returns_empty_list_when_file_does_not_exist(doc):
    doc.readFromFile('file/does/not/exist.idf')
    assert len(doc.objs) == 0


def test_read_returns_objects_for_valid_file(doc):
    doc.readFromFile('test_file.idf')
    assert len(doc.objs) == 3
    assert doc.objs[0] == "Version,7.2".split(',')
    assert doc.objs[1] == "ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless".split(',')
    assert doc.objs[2] == "ScheduleTypeLimits,Comfort Temperature,19,26,Continuous,Temperature".split(',')


def test_writes_objects_read_from_file(doc):
    try:
        os.remove('other_file.idf')
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occured
    doc.readFromFile('test_file.idf')
    doc.writeToFile('other_file.idf')
    th.assert_idf_files('test_file.idf', 'other_file.idf')


def test_returns_only_classes_with_objects_with_count(doc):
    doc.readFromFile('test_file.idf')
    class_count = doc.onlyClassesWithObjectsWithObjectCount()
    assert len(class_count) == 2
    assert class_count['Version'] == 1
    assert class_count['ScheduleTypeLimits'] == 2


def test_returns_all_classes_with_count(doc):
    doc.readFromFile('test_file.idf')

    classes = doc.allClassesWithObjectCount()

    assert len(classes) == 3
    assert classes['Version'] == 1
    assert classes['ScheduleTypeLimits'] == 2
    assert classes['Timestep'] == 0


def test_objects_for_class_returns_empty_list_when_no_object_for_class(doc):
    assert doc.objectsOfClass('classNotFound') == []


def test_objects_for_class_leaves_other_objects_out(doc):
    doc.readFromFile('test_file.idf')
    only_version = doc.objectsOfClass('Version')
    assert only_version[0][0] == 'Version'
    only_schedule_type_limits = doc.objectsOfClass('ScheduleTypeLimits')
    assert only_schedule_type_limits[0][0] == 'ScheduleTypeLimits'
    assert only_schedule_type_limits[1][0] == 'ScheduleTypeLimits'


def test_fields_of_class_returns_empty_list_when_class_not_found(doc):
    assert doc.fieldsOfClass("classNotFound") == []


def test_fields_of_class(doc):
    doc.readFromFile('test_file.idf')
    assert doc.fieldsOfClass('Version') == ['Version Identifier']
    assert doc.fieldsOfClass('ScheduleTypeLimits') == ['Name', 'Lower Limit Value', 'Upper Limit Value', 'Numeric Type', 'Unit Type']
    assert doc.fieldsOfClass('Timestep') == ['Number of Timesteps per Hour']


def test_new_object_returns_empty_object_with_class_name(doc):
    doc.addEmptyObject('ScheduleTypeLimits')
    assert doc.objectsOfClass('ScheduleTypeLimits') == ['ScheduleTypeLimits,,,,,'.split(',')]


def test_returns_object_of_class_at_index(doc):
    doc.readFromFile('test_file.idf')
    assert doc.objectOfClassAtIndex('Version', 0) == ['Version', '7.2']
    assert doc.objectOfClassAtIndex('Version', 1) == []


def test_replaces_object_at_index(doc):
    doc.readFromFile('test_file.idf')
    doc.replaceObjectAtIndexWithObject(0, ['Version', '8.0'])
    assert doc.objectsOfClass('Version') == [['Version', '8.0']]


def test_deletes_object_at_valid_index(doc):
    doc.readFromFile('test_file.idf')
    doc.deleteObjectOfClassAtIndex('Version', 0)
    assert doc.objectsOfClass('Version') == []


def test_does_nothing_when_deleting_object_at_invalid_index(doc):
    doc.readFromFile('test_file.idf')
    doc.deleteObjectOfClassAtIndex('Version', 1)
    assert doc.objectsOfClass('Version') == [['Version', '7.2']]
