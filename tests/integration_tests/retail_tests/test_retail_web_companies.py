from __future__ import division
from tests.integration_tests.retail_tests.implementation.retail_web_companies_test_collection import RetailWebCompaniesTestCollection
from tests.integration_tests.retail_tests.implementation.retail_white_space_test_collection import RetailWhiteSpaceTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_main.main_api import app as main_app
from retail.v010.retail_app_runner import app as web_app
import unittest


__author__ = 'vgold'


class RetailWebCompaniesTests(ServiceTestCase):
    """
    Test case for Retail Web Company Page endpoints.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {"RETAIL_WEB": web_app, "MAIN": main_app, "MDS": mds_app}
        cls.svc_key = "RETAIL_WEB"
        cls.test_colls = {
            "RETAIL_WEB_COMPANIES": RetailWebCompaniesTestCollection,
            "RETAIL_WHITE_SPACE": RetailWhiteSpaceTestCollection
        }
        cls.svc_main_exempt = {}

    ##------------------------------------ Tests ------------------------------------------------##

    def test_web_test_get_company_hierarchy_banner(self):
        self.tests["RETAIL_WEB_COMPANIES"].web_test_get_company_hierarchy_banner()

    def test_web_test_get_company_hierarchy_parent(self):
        self.tests["RETAIL_WEB_COMPANIES"].web_test_get_company_hierarchy_parent()

    def test_web_test_get_company_hierarchy_cooperative(self):
        self.tests["RETAIL_WEB_COMPANIES"].web_test_get_company_hierarchy_cooperative()

    def test_web_test_get_company_hierarchy_owner(self):
        self.tests["RETAIL_WEB_COMPANIES"].web_test_get_company_hierarchy_owner()

    def test_web_test_get_company_hierarchy_just_parent(self):
        self.tests["RETAIL_WEB_COMPANIES"].web_test_get_company_hierarchy_just_parent()

    def test_web_test_get_company_hierarchy_just_banner(self):
        self.tests["RETAIL_WEB_COMPANIES"].web_test_get_company_hierarchy_just_banner()

    def test_retail_whitespace_stores(self):
        self.tests["RETAIL_WHITE_SPACE"].test_retail_get_whitespace_stores()

    def test_retail_whitespace_grid(self):
        self.tests["RETAIL_WHITE_SPACE"].test_retail_get_whitespace_grid()


if __name__ == '__main__':
    unittest.main()
