from __future__ import division
from tests.integration_tests.retail_tests.implementation.retail_web_white_space_distribution_test_collection import RetailWebWhiteSpaceDistributionTestCollection
from tests.integration_tests.retail_tests.implementation.summary_measures_test_collection import SummaryMeasuresTestCollection
from tests.integration_tests.retail_tests.implementation.economics_test_collection import EconomicsTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_analytics.analytics_api import app as analytics_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from core.service.svc_main.main_api import app as main_app
from retail.v010.retail_app_runner import app as web_app
import unittest


__author__ = "vgold"


class TestRetailMainEndpoints(ServiceTestCase):
    """
    Test case for Main Service.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {
            "RETAIL_WEB": web_app,
            "MDS": mds_app,
            "MAIN": main_app,
            "ANALYTICS": analytics_app,
            "WFS": wfs_app
        }
        cls.svc_key = "RETAIL_WEB"
        cls.test_colls = {
            "SUMMARY_MEASURES": SummaryMeasuresTestCollection,
            "ECONOMICS": EconomicsTestCollection,
            "RETAIL_WEB_WHITE_SPACE_DIST": RetailWebWhiteSpaceDistributionTestCollection
        }

##############################################################################################################
##
## Test methods must adhere to a strict naming convention:
##   1)  Name of test method must have "test_" prepended to the actual name of the test method
##       from the test collection.
##
##   2)  The actual test that should run must be called from within the test method (obviously).
##
##   3)  The actual test's name must start with its lowercase service key and an underscore ("mds_",
##       "main_", "rds_", "wfs_", etc.).
##
##   **  NOTE: The values of these test methods are dynamically overwritten to execute the setUp and
##       tearDown methods from the test's collection before and after the actual test specified. This
##       was a design decision, because the test collection should know how to set up and tear down
##       each test it houses.
##
##############################################################################################################

    def test_analytics_test_unemployment_distribution(self):
        self.tests["ECONOMICS"].analytics_test_unemployment_distribution()

    # RET-1914
    # def test_analytics_test_competition_measures(self):
    #     self.tests["SUMMARY_MEASURES"].analytics_test_competition_measures()

    def test_analytics_test_economic_measures(self):
        self.tests["SUMMARY_MEASURES"].analytics_test_economic_measures()

    def test_retail_test_get_white_space_competition_demographic_distribution(self):
        self.tests["RETAIL_WEB_WHITE_SPACE_DIST"].retail_test_get_white_space_competition_demographic_distribution()


if __name__ == '__main__':
    unittest.main()
