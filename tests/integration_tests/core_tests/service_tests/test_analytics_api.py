from __future__ import division
from tests.integration_tests.core_tests.service_tests.implementation.analytics_default_calcs_test_collection import AnalyticsDefaultCalcsTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.analytics_demographics_test_collection import AnalyticsDemographicsTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.analytics_competition_test_collection import AnalyticsCompetitionTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.analytics_retailer_test_collection import AnalyticsRetailerTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.analytics_service_test_collection import AnalyticsServiceTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.analytics_stores_test_collection import AnalyticsStoresTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_analytics.analytics_api import app as analytics_app
from core.service.svc_main.main_api import app as main_app
import unittest


__author__ = "irsalmashhor"


class Test_Analytics_API(ServiceTestCase):
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
        cls.apps = {"MDS": mds_app, "MAIN": main_app, "ANALYTICS": analytics_app}
        cls.svc_key = "ANALYTICS"
        cls.test_colls = {
            "SERVICE": AnalyticsServiceTestCollection,
            "CALCS": AnalyticsDefaultCalcsTestCollection,
            "DEMOGRAPHICS": AnalyticsDemographicsTestCollection,
            "COMPETITION": AnalyticsCompetitionTestCollection,
            "STORES": AnalyticsStoresTestCollection,
            "RETAILER": AnalyticsRetailerTestCollection
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
##############################################################################################################o

    def test_circular_calc_dependencies(self):
        self.tests["CALCS"].analytics_test_circular_calc_dependencies()

    def test_monthly_trade_area_demographics(self):
        self.tests["DEMOGRAPHICS"].analytics_test_monthly_trade_area_demographics()

    def test_analytics_competition_monthly_average_trade_area_competition_ratio(self):
        self.tests["COMPETITION"].analytics_competition_monthly_average_trade_area_competition_ratio()

    def test_analytics_competition_monthly_company_competition_ratio(self):
        self.tests["COMPETITION"].analytics_competition_monthly_company_competition_ratio()

    def test_monthly_store_growth(self):
        self.tests["STORES"].analytics_test_monthly_store_growth()

    def test_company_data_check__read_docstring_if_fail(self):
        self.tests["SERVICE"].analytics_test_company_data_check__read_docstring_if_fail()

    def test_retailer_aggregate_transactions_per_customer(self):
        self.tests["RETAILER"].test_aggregate_transactions_per_customer()

    def test_retailer_aggregate_transactions_per_customer__ltm(self):
        self.tests["RETAILER"].test_aggregate_transactions_per_customer__ltm()

    def test_retailer_aggregate_transactions_per_store(self):
        self.tests["RETAILER"].test_aggregate_transactions_per_store()

if __name__ == '__main__':
    unittest.main()
