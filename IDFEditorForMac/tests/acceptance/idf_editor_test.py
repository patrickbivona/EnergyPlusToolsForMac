import tests.harness as th
import os
import errno
from idf_editor import IdfEditorWindow
from PySide.QtCore import Qt, QPoint
from PySide.QtTest import QTest


class IdfEditorTestCase(th.AppTestCase):

    def setUp(self):
        super(IdfEditorTestCase, self).setUp()
        self.window = IdfEditorWindow()

    def test_open_file_and_save_as_other(self):
        try:
            os.remove('other_file.idf')
        except OSError as e:
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise  # re-raise exception if a different error occured
        self.window.openFile('test_file.idf')
        self.window.saveFileAs('other_file.idf')
        self.assertIdfFilesContentEquals('test_file.idf', 'other_file.idf')

    def test_toggle_show_classes_with_objects_only_shows_all_classes_for_empty_doc(self):
        self.window.showClassesWithObjectsOnly(True)
        self.assertEquals(self.window.ui.listView.model().rowCount(), 3)

    def test_tables_contains_object_for_selected_class(self):
        self.window.openFile('test_file.idf')
        model = self.window.ui.tableView.model()

        self.window.selectClass("Version")
        self.assertEquals(model.data(model.createIndex(0, 0)), "7.2")

        self.window.selectClass("ScheduleTypeLimits")
        self.assertEquals(model.data(model.createIndex(0, 0)), "Fraction")

    def test_can_toggle_show_classes_with_objects_only(self):

        self.window.openFile('test_file.idf')

        self.window.showClassesWithObjectsOnly(False)
        self.assertEquals(set(self.window.classes()), set(['Version', 'ScheduleTypeLimits', 'Timestep']))

        self.window.showClassesWithObjectsOnly(True)
        self.assertEquals(set(self.window.classes()), set(['Version', 'ScheduleTypeLimits']))

    def test_adds_new_object(self):
        if os.path.exists("current_running_test.idf"):
            os.remove("current_running_test.idf")

        # only necessary to test shortcuts, which... doesn't work
        # self.window.show()
        # QTest.qWaitForWindowShown(self.window)

        self.window.selectClass("ScheduleTypeLimits")
        # This doesn't work currently, for some reason
        # QTest.keyClick(self.window, Qt.Key_N, Qt.ShiftModifier)
        self.window.addNewObject()

        self.assertEquals(self.window.doc.objectsOfClass("ScheduleTypeLimits")[0], "ScheduleTypeLimits,,,,,".split(","))

    def test_does_not_delete_object_when_none_selected(self):
        self.window.openFile('test_file.idf')
        self.assertEquals(len(self.window.doc.objects()), 2)

        self.window.deleteObject()

        self.assertEquals(len(self.window.doc.objects()), 2)

    def test_deletes_selected_object(self):

        self.window.openFile('test_file.idf')
        self.assertEquals(self.window.doc.objectsOfClass("ScheduleTypeLimits"), ["ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless".split(",")])

        self.window.selectClass('ScheduleTypeLimits')
        self.select_object_field_at(0, 0)
        self.window.deleteObject()

        self.assertEquals(self.window.doc.objectsOfClass("ScheduleTypeLimits"), [])

    # def test_input_object(self):

    #     self.window.selectClass("ScheduleTypeLimits")
    #     self.window.addNewObject()

    #     # this code is supposed to edit a QTableView but doesn't work...
    #     # see http://stackoverflow.com/questions/12604739/how-can-you-edit-a-qtableview-cell-from-a-qtest-unit-test
    #     xPos = self.window.ui.tableView.columnViewportPosition(1) + 5
    #     yPos = self.window.ui.tableView.rowViewportPosition(0) + 10
    #     viewport = self.window.ui.tableView.viewport()

    #     QTest.mouseClick(viewport, Qt.LeftButton, Qt.NoModifier, QPoint(xPos, yPos))
    #     QTest.mouseDClick(viewport, Qt.LeftButton, Qt.NoModifier, QPoint(xPos, yPos))
    #     QTest.keyClicks(viewport.focusWidget(), "Fraction")
    #     QTest.keyClick(viewport.focusWidget(), Qt.Key_Enter)
    #     # QTest.keyClicks(viewport.focusWidget(), "0")
    #     # QTest.keyClicks(viewport.focusWidget(), "1")
    #     # QTest.keyClicks(viewport.focusWidget(), "Continuous")
    #     # QTest.keyClicks(viewport.focusWidget(), "Dimensionless")

    #     self.assertEquals(self.window.doc.objectsOfClass("ScheduleTypeLimits")[0], "ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless".split(","))

    def select_object_field_at(self, row, column):
        xPos = self.window.ui.tableView.columnViewportPosition(row) + 5
        yPos = self.window.ui.tableView.rowViewportPosition(column) + 10
        viewport = self.window.ui.tableView.viewport()
        QTest.mouseClick(viewport, Qt.LeftButton, pos=QPoint(xPos, yPos))
