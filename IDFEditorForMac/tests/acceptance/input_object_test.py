import os
import os.path
import tests.harness as th


class InputObjectTest(th.AppTestCase):

    def test_input_object_in_new_file(self):
        if os.path.exists('current_running_test.idf'):
            os.remove('current_running_test.idf')

        # type Command+N for new file
        self.app_proxy.select_menuitem(['File', 'New'])
        self.app_proxy.select_class('ScheduleTypeLimits')
        self.app_proxy.select_menuitem(['Edit', 'New Object'])
        self.app_proxy.input_object(['Fraction', '0', '1', 'Continuous', 'Dimensionless'])
        self.app_proxy.save_test_idf_as('current_running_test.idf')
        # compare with expected result
        self.assertIdfFilesContentEquals('current_running_test.idf', 'fraction_schedule_type.idf')
