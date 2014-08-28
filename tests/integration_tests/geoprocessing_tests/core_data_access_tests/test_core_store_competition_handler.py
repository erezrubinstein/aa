from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_workflow.workflow_api import app as wfs_app
import unittest
from tests.integration_tests.geoprocessing_tests.core_data_access_tests.implementation.core_store_compeitition_handler_test_collection import CoreStoreCompetitionHandlerTestCollection


__author__ = 'erezrubinstein'


class TestCoreStoreCompetitionHandler(ServiceTestCase):
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
        cls.apps = { "MDS": mds_app, "WFS": wfs_app }
        cls.svc_key = "MDS"
        cls.test_colls = {"CORE_STORE_COMPETITION_HANDLER": CoreStoreCompetitionHandlerTestCollection}
        cls.svc_main_exempt = {}


    def test_get_competitive_stores(self):
        self.tests["CORE_STORE_COMPETITION_HANDLER"].test_get_competitive_stores()

    def test_batch_upsert_competitive_stores(self):
        self.tests["CORE_STORE_COMPETITION_HANDLER"].test_batch_upsert_competitive_stores()




if __name__ == '__main__':
    unittest.main()
