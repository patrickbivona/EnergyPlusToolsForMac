import pytest
import os
import errno
import tests.harness as th
from idf_editor import IdfEditorWindow
from PySide.QtGui import QApplication
from PySide.QtCore import Qt, QPoint
from PySide.QtTest import QTest


@pytest.fixture
def qApp():
    qApp = QApplication.instance()
    if qApp is None:
        qApp = QApplication([])
    return qApp


@pytest.fixture
def editor(qApp):
    return IdfEditorWindow()


def test_open_file_and_save_as_other(editor):
    try:
        os.remove('other_file.idf')
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occured
    editor.openFile('test_file.idf')
    editor.saveFileAs('other_file.idf')

    th.assert_idf_files('test_file.idf', 'other_file.idf')


def test_toggle_show_classes_with_objects_only_shows_all_classes_for_empty_doc(editor):
    editor.showClassesWithObjectsOnly(True)
    assert editor.ui.listView.model().rowCount() == 3


def test_tables_contains_object_for_selected_class(editor):
    editor.openFile('test_file.idf')
    model = editor.ui.tableView.model()

    editor.selectClass("Version")
    assert model.data(model.createIndex(0, 0)) == "7.2"

    editor.selectClass("ScheduleTypeLimits")
    assert model.data(model.createIndex(0, 0)) == "Fraction"


def test_can_toggle_show_classes_with_objects_only(editor):

    editor.openFile('test_file.idf')

    editor.showClassesWithObjectsOnly(False)
    assert set(editor.classes()) == set(['Version', 'ScheduleTypeLimits', 'Timestep'])

    editor.showClassesWithObjectsOnly(True)
    assert set(editor.classes()) == set(['Version', 'ScheduleTypeLimits'])


def test_adds_new_object(editor):
    if os.path.exists("current_running_test.idf"):
        os.remove("current_running_test.idf")

    # only necessary to test shortcuts, which... doesn't work
    # editor.show()
    # QTest.qWaitForWindowShown(editor)

    editor.selectClass("ScheduleTypeLimits")
    # This doesn't work currently, for some reason
    # QTest.keyClick(editor, Qt.Key_N, Qt.ShiftModifier)
    editor.addNewObject()

    assert editor.doc.objectsOfClass("ScheduleTypeLimits")[0] == "ScheduleTypeLimits,,,,,".split(",")


def test_does_not_delete_object_when_none_selected(editor):
    editor.openFile('test_file.idf')
    assert len(editor.doc.objects()) == 3

    editor.deleteObject()

    assert len(editor.doc.objects()) == 3


def test_deletes_selected_object(editor):

    editor.openFile('test_file.idf')
    assert len(editor.doc.objectsOfClass("ScheduleTypeLimits")) == 2

    editor.selectClass('ScheduleTypeLimits')
    select_object_field_at(editor.ui.tableView, 0, 0)
    editor.deleteObject()

    objs = editor.doc.objectsOfClass("ScheduleTypeLimits")
    assert len(objs) == 1
    assert objs[0][1] == "Comfort Temperature"

# def test_input_object(editor):

#     editor.selectClass("ScheduleTypeLimits")
#     editor.addNewObject()

#     # this code is supposed to edit a QTableView but doesn't work...
#     # see http://stackoverflow.com/questions/12604739/how-can-you-edit-a-qtableview-cell-from-a-qtest-unit-test
#     xPos = editor.ui.tableView.columnViewportPosition(1) + 5
#     yPos = editor.ui.tableView.rowViewportPosition(0) + 10
#     viewport = editor.ui.tableView.viewport()

#     QTest.mouseClick(viewport, Qt.LeftButton, Qt.NoModifier, QPoint(xPos, yPos))
#     QTest.mouseDClick(viewport, Qt.LeftButton, Qt.NoModifier, QPoint(xPos, yPos))
#     QTest.keyClicks(viewport.focusWidget(), "Fraction")
#     QTest.keyClick(viewport.focusWidget(), Qt.Key_Enter)
#     # QTest.keyClicks(viewport.focusWidget(), "0")
#     # QTest.keyClicks(viewport.focusWidget(), "1")
#     # QTest.keyClicks(viewport.focusWidget(), "Continuous")
#     # QTest.keyClicks(viewport.focusWidget(), "Dimensionless")

#     assert editor.doc.objectsOfClass("ScheduleTypeLimits")[0], "ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless".split(","))


def select_object_field_at(tableView, row, column):
    xPos = tableView.columnViewportPosition(row) + 5
    yPos = tableView.rowViewportPosition(column) + 10
    viewport = tableView.viewport()
    QTest.mouseClick(viewport, Qt.LeftButton, pos=QPoint(xPos, yPos))
