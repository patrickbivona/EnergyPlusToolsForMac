
import tests.harness as th


class ClassesWithObjectTest(th.AppTestCase):

    def test_can_toggle_show_objects_with_classes_only(self):
        self.app_proxy.open_test_idf('test_file.idf')
        self.app_proxy.select_menuitem(['View', 'Show Classes with Objects Only'])
