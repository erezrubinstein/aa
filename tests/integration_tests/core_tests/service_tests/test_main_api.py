from __future__ import division
from tests.integration_tests.core_tests.service_tests.implementation.main_analytics_export_test_collection import MainAnalyticsExportTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.company_store_count_test_collection import CompanyStoreCountTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.main_export_test_collection import MainExportTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.main_plan_b_test_collection import MainPlanBTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.main_test_collection import MainTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.main_weather_test_collection import MainWeatherTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_raw_data_storage.rds_api import app as rds_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from core.service.svc_main.main_api import app as main_app
import unittest


__author__ = "vahram"


###################################################################################################


class TestMainAPI(ServiceTestCase):
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
            "MAIN": main_app,
            "MDS": mds_app,
            "RDS": rds_app,
            "WFS": wfs_app
        }
        cls.svc_key = "MAIN"
        cls.test_colls = {
            "MAIN": MainTestCollection,
            "MAIN_EXPORT": MainExportTestCollection,
            "COMPANY_STORE_COUNT": CompanyStoreCountTestCollection,
            "ANALYTICS_EXPORT": MainAnalyticsExportTestCollection,
            "MAIN_PLAN_B": MainPlanBTestCollection,
            "MAIN_WEATHER": MainWeatherTestCollection
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

    ##-----------------------## Main Tests ##-------------------------##

    def test_main_test_get_entity_type_summary(self):
        self.tests["MAIN"].main_test_get_entity_type_summary()

    def test_main_test_get_entity_summary(self):
        self.tests["MAIN"].main_test_get_entity_summary()

    def test_main_test_get_data_entities(self):
        self.tests["MAIN"].main_test_get_data_entities()

    def test_main_test_get_data_entity_relationships(self):
        self.tests["MAIN"].main_test_get_data_entity_relationships()

    def test_main_test_file_upload_single(self):
        self.tests["MAIN"].main_test_file_upload_single()

    def test_main_test_file_upload_multiple(self):
        self.tests["MAIN"].main_test_file_upload_multiple()

    def test_main_test_find_multiple_files(self):
        self.tests["MAIN"].main_test_find_multiple_files()

    def test_main_test_find_files_linked_to_entity(self):
        self.tests["MAIN"].main_test_find_files_linked_to_entity()

    def test_main_test_post_files_linked_to_entity(self):
        self.tests["MAIN"].main_test_post_files_linked_to_entity()

    def test_main_test_add_rir(self):
        self.tests['MAIN'].main_test_add_rir()

    def test_main_export_test_companies(self):
        self.tests["MAIN_EXPORT"].main_export_test_companies()

    def test_main_export_test_companies_invalid_analytics(self):
        self.tests["MAIN_EXPORT"].main_export_test_companies_invalid_analytics()

    def test_main_export_test_retail_input_records(self):
        self.tests["MAIN_EXPORT"].main_export_test_retail_input_records()

    def test_main_export_stores(self):
        self.tests["MAIN_EXPORT"].main_export_stores()

    def test_main_export_get_stores_by_companies_and_dates__two_companies(self):
        self.tests["MAIN_EXPORT"].main_export_get_stores_by_companies_and_dates__two_companies()

    def test_main_export_get_stores_by_companies_and_dates__date_queries(self):
        self.tests["MAIN_EXPORT"].main_export_get_stores_by_companies_and_dates__date_queries()

    def test_main_export_get_geoprocessing_trade_area_demographics(self):
        self.tests["MAIN_EXPORT"].get_geoprocessing_trade_area_demographics()

    def test_main_export_get_dupe_stores(self):
        self.tests["MAIN_EXPORT"].get_dupe_stores()

    def test_main_export_get_company_analytics_status(self):
        self.tests["MAIN_EXPORT"].get_company_analytics_status()

    def test_store_count_test_get_company_store_count(self):
        self.tests["COMPANY_STORE_COUNT"].store_count_test_get_company_store_count()

    def test_main_preset_test_upload_get_update_store_count_files(self):
        self.tests["COMPANY_STORE_COUNT"].main_preset_test_upload_get_update_store_count_files()

    def test_main_analytics_export_test_trade_area_to_trade_area(self):
        self.tests["ANALYTICS_EXPORT"].main_analytics_export_test_trade_area_to_trade_area()

    def test_main_analytics_export_test_trade_area_monthly_demographics(self):
        self.tests["ANALYTICS_EXPORT"].main_analytics_export_test_trade_area_monthly_demographics()

    def test_main_export_get_geoprocessing_trade_area_competition(self):
        self.tests["ANALYTICS_EXPORT"].main_analytics_export_test_trade_area_competition()

    def test_main_analytics_export_test_trade_area_monopolies(self):
        self.tests["ANALYTICS_EXPORT"].main_analytics_export_test_trade_area_monopolies()

    def test_main_export_get_geoprocessing_store_trade_area_checks(self):
        self.tests["MAIN_EXPORT"].get_geoprocessing_store_trade_area_checks()

    def test_main_export_industry_competition(self):
        self.tests["MAIN_EXPORT"].main_export_industry_competition()

    def test_main_preset_get_trade_areas(self):
        self.tests["MAIN"].main_test_get_trade_areas()

    def test_main_preset_get_trade_area_by_id(self):
        self.tests["MAIN"].main_test_get_trade_area_by_id()

    def test_mark_as_needing_plan_b__companies(self):
        self.tests["MAIN_PLAN_B"].main_test_mark_as_needing_plan_b__companies()

    def test_main_test_mark_as_needing_plan_b__industries(self):
        self.tests["MAIN_PLAN_B"].main_test_mark_as_needing_plan_b__industries()

    def test_weather_test_run_api_weather_stores(self):
        self.tests["MAIN_WEATHER"].test_run_api_weather_stores()

    def test_weather_test_run_api_weather_stores__multiple_stores_per_station(self):
        self.tests["MAIN_WEATHER"].test_run_api_weather_stores__multiple_stores_per_station()

    def test_weather_get_period_weather_data__null_aggregates(self):
        self.tests["MAIN_WEATHER"].test_get_period_weather_data__null_aggregates()

if __name__ == '__main__':
    unittest.main()
