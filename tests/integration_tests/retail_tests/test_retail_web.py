from __future__ import division
from tests.integration_tests.retail_tests.implementation.retail_web_white_space_competition_set_test_collection import RetailWebWhiteSpaceCompetitionSetTestCollection
from tests.integration_tests.retail_tests.implementation.retail_web_company_typeahead_test_collection import RetailWebCompanyTypeaheadTestCollection
from tests.integration_tests.retail_tests.implementation.retail_web_trade_area_grid_test_collection import RetailWebTradeAreaGridTestCollection
from tests.integration_tests.retail_tests.implementation.retail_web_download_file_test_collection import RetailWebDownloadFileTestCollection
from tests.integration_tests.retail_tests.implementation.retail_web_trial_user_test_collection import RetailWebTrialUserTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_raw_data_storage.rds_api import app as rds_app
from core.service.svc_main.main_api import app as main_app
from retail.v010.retail_app_runner import app as web_app
import unittest


__author__ = 'vgold'


class RetailWebTests(ServiceTestCase):
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
        cls.apps = {"RETAIL_WEB": web_app, "MAIN": main_app, "MDS": mds_app, "RDS": rds_app}
        cls.svc_key = "RETAIL_WEB"
        cls.test_colls = {
            "RETAIL_WEB_DOWNLOAD_FILE": RetailWebDownloadFileTestCollection,
            "RETAIL_WEB_COMPANY_TYPEAHEAD": RetailWebCompanyTypeaheadTestCollection,
            "RETAIL_WEB_TRADE_AREA_GRID": RetailWebTradeAreaGridTestCollection,
            "RETAIL_WEB_TRIAL_USER": RetailWebTrialUserTestCollection,
            "RETAIL_WEB_WHITE_SPACE_COMP_SET": RetailWebWhiteSpaceCompetitionSetTestCollection
        }
        cls.svc_main_exempt = {}

    ##------------------------------------ Tests ------------------------------------------------##

    def test_retail_test_download_file__exists(self):
        self.tests["RETAIL_WEB_DOWNLOAD_FILE"].retail_test_download_file__exists()

    def test_retail_test_download_file__unauthorized(self):
        self.tests["RETAIL_WEB_DOWNLOAD_FILE"].retail_test_download_file__unauthorized()

    def test_retail_test_download_stores_export_file(self):
        self.tests["RETAIL_WEB_DOWNLOAD_FILE"].retail_test_download_stores_export_file()

    def test_retail_test_download_competitors_export_file(self):
        self.tests["RETAIL_WEB_DOWNLOAD_FILE"].retail_test_download_competitors_export_file()

    def test_retail_test_download_full_report_by_trial_user(self):
        self.tests["RETAIL_WEB_TRIAL_USER"].retail_test_download_full_report_by_trial_user()

    def test_retail_test_company_typeahead(self):
        self.tests["RETAIL_WEB_COMPANY_TYPEAHEAD"].retail_test_company_typeahead()

    def test_retail_test_trade_area_grids(self):
        self.tests["RETAIL_WEB_TRADE_AREA_GRID"].retail_test_trade_area_grids()

    def test_retail_store_grid_helper__all_stores(self):
        self.tests["RETAIL_WEB_TRADE_AREA_GRID"].test_retail_store_grid_helper__all_stores(web_app)

    #-------------------------# RETAIL_WEB_WHITE_SPACE_COMP_SET #-------------------------#

    def test_retail_test_create_white_space_competition_set(self):
        self.tests["RETAIL_WEB_WHITE_SPACE_COMP_SET"].retail_test_create_white_space_competition_set()


if __name__ == '__main__':
    unittest.main()
