from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from retailer.web.retailer_app_runner import app as retailer_web_app
import unittest
from tests.integration_tests.retailer_tests.implementation.retailer_client_admin_test_collection import RetailerClientAdminTestCollection
from core.service.svc_master_data_storage.mds_api import app as mds_app


class RetailControllersTests(ServiceTestCase):
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {
            "RETAILER_WEB": retailer_web_app,
            "MDS": mds_app
            }
        cls.svc_key = "RETAILER_WEB"
        cls.test_colls = {
            "RETAILER_CLIENT": RetailerClientAdminTestCollection
        }
        cls.svc_main_exempt = {}

    #-----------------------# RETAIL_CLIENT_CONTROLLER #-----------------------#

    def test_add_new_retailer_client(self):
        self.tests["RETAILER_CLIENT"].add_new_retailer_client()

    def test_get_retailer_client_by_id(self):
        self.tests["RETAILER_CLIENT"].get_retailer_client_by_id()

    def test_get_retailer_client_by_name(self):
        self.tests["RETAILER_CLIENT"].get_retailer_client_by_name()

    def test_update_retailer_client_by_id(self):
        self.tests["RETAILER_CLIENT"].update_retailer_client_by_id()

    def test_update_retailer_client_by_name(self):
        self.tests["RETAILER_CLIENT"].update_retailer_client_by_name()


if __name__ == '__main__':
    unittest.main()
