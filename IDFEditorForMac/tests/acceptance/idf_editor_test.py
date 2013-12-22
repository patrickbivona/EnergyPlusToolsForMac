import tests.harness as th
import os
import errno
from idf_editor import IdfEditorWindow
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

    def test_can_toggle_show_classes_with_objects_only(self):

        self.window.openFile('test_file.idf')

        self.window.showClassesWithObjectsOnly(False)
        self.assertEquals(set(self.window.classes()), set(['Version', 'ScheduleTypeLimits', 'Timestep']))

        self.window.showClassesWithObjectsOnly(True)
        self.assertEquals(set(self.window.classes()), set(['Version', 'ScheduleTypeLimits']))

    # def test_input_object_in_new_file(self):
    #     if os.path.exists("current_running_test.idf"):
    #         os.remove("current_running_test.idf")

    #     self.window.selectClass("ScheduleTypeLimits")
    #     self.window.addNewObject()
    #     QTest.keyClicks(self.window.ui.tableView, "Fraction")
    #     QTest.keyClicks(self.window.ui.tableView, "0")
    #     QTest.keyClicks(self.window.ui.tableView, "1")
    #     QTest.keyClicks(self.window.ui.tableView, "Continuous")
    #     QTest.keyClicks(self.window.ui.tableView, "Dimensionless")
    #     self.window.saveFileAs("current_running_test.idf")

    #     # compare with expected result
    #     self.assertIdfFilesContentEquals('current_running_test.idf', 'fraction_schedule_type.idf')

    # def test_delete_object(self):
    #     pass
#         if os.path.exists('current_running_test.idf'):
#             os.remove('current_running_test.idf')

#         self.app_proxy.open_test_idf('test_file.idf')
#         self.app_proxy.select_class('ScheduleTypeLimits')
#         self.app_proxy.move_to_column(0)
#         self.app_proxy.select_menuitem(['Edit', 'Delete Object'])
#         self.app_proxy.save_test_idf_as('current_running_test.idf')

#         expected = """Version,7.2;
# """
#         self.assertIdfFileContentEquals('current_running_test.idf', expected)

