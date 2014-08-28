from tests.integration_tests.geoprocessing_tests.core_data_access_tests.implementation.core_monopoly_handler_test_collection import CoreMonopolyHandlerTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_workflow.workflow_api import app as wfs_app
import unittest


__author__ = 'erezrubinstein'


class TestCoreMonopolyHandler(ServiceTestCase):
    """
    Test case for Main Service Export Data functions.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {"MDS": mds_app, "WFS": wfs_app}
        cls.svc_key = "MDS"
        cls.test_colls = {"CORE_MONOPOLY_HANDLER": CoreMonopolyHandlerTestCollection}
        cls.svc_main_exempt = {}

    def test_select_active_monopoly_record(self):
        self.tests["CORE_MONOPOLY_HANDLER"].test_select_active_monopoly_record()

    def test_insert_close_upsert__basic_stay_closed(self):
        self.tests["CORE_MONOPOLY_HANDLER"].test_insert_close_upsert__basic_stay_closed()

    def test_insert_close_upsert__basic_stay_open(self):
        self.tests["CORE_MONOPOLY_HANDLER"].test_insert_close_upsert__basic_stay_open()

    def test_insert_close_upsert__complex_series(self):
        self.tests["CORE_MONOPOLY_HANDLER"].test_insert_close_upsert__complex_series()


if __name__ == '__main__':
    unittest.main()
