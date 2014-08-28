from tests.integration_tests.common_tests.implementation.white_space_calculator_test_collection import WhiteSpaceCalculatorTestCollection
from tests.integration_tests.common_tests.implementation.lox_test_collection import LoxTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from core.service.svc_main.main_api import app as main_app


__author__ = 'erezrubinstein'


class TestCommonStuff(ServiceTestCase):
    """
    Test case for Workflow Service.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {
            "MAIN": main_app,
            "MDS": mds_app,
            "WFS": wfs_app
        }
        cls.svc_key = "WFS"
        cls.test_colls = {
            "WHITE_SPACE_CALCULATOR": WhiteSpaceCalculatorTestCollection,
            "CREAM_CHEESE_AND_LOX": LoxTestCollection
        }
        cls.svc_main_exempt = {}

    def test_calculator_complete_run(self):
        self.tests["WHITE_SPACE_CALCULATOR"].test_calculator_complete_run()

    def test_calculator_complete_run__with_competition(self):
        self.tests["WHITE_SPACE_CALCULATOR"].test_calculator_complete_run__with_competition()

    def test_lox(self):
        self.tests["CREAM_CHEESE_AND_LOX"].test_locks()

    def test_lox_keep_alive(self):
        self.tests["CREAM_CHEESE_AND_LOX"].test_locks_keep_alive()
