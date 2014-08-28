from __future__ import division
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_trade_area
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import parse_date, get_start_date_of_previous_month, ANALYTICS_TARGET_YEAR
from core.common.utilities.helpers import generate_id
from common.utilities.time_series import get_monthly_time_series
from datetime import datetime


__author__ = 'imashhor'


class AnalyticsDemographicsTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "analytics_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.analytics_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def analytics_test_monthly_trade_area_demographics(self):
        # Create the test trade areas
        insert_kwargs = {
            "analytics": {
                "demographics": {
                    "monthly": {}
                }
            }
        }

        company_id1 = generate_id()
        company_id2 = generate_id()

        opened_date = datetime(2011, 9, 3)
        closed_date = datetime(2012, 3, 3)

        insert_test_trade_area(company_id=company_id1, dem_total_population=111, **insert_kwargs)

        test_trade_area_id = insert_test_trade_area(
            company_id=company_id2,
            opened_date=opened_date, closed_date=closed_date,
            dem_total_population=3465, **insert_kwargs)

        # Run the calculation (get company_id = 1)
        calc_params = self._build_run_calc_params("trade_area", [str(company_id2)])
        self.analytics_access.call_post_run_calc_by_name("Monthly Trade Area Total Population Demographics", calc_params, self.context)

        # Fetch the results
        result = self._fetch_monthly_trade_area_demographics_result(test_trade_area_id)

        # Verify target year
        self.test_case.assertEqual(ANALYTICS_TARGET_YEAR, result["target_year"])

        # Validate every value in the time series
        result_series = result["series"]

        expected_series = self._get_expected_start_of_month_series(opened_date, closed_date)

        self.test_case.assertEqual(len(expected_series), len(result_series))

        for idx, series_item in enumerate(result_series):
            item_date = parse_date(series_item["date"])
            self.test_case.assertEqual(expected_series[idx], item_date)

            self.test_case.assertTrue(item_date >= datetime(2011, 9, 1))
            self.test_case.assertTrue(item_date <= datetime(2012, 3, 1))

            self.test_case.assertEqual(3465, series_item["value"])

    def _get_expected_start_of_month_series(self, start_date, end_date):

        return get_monthly_time_series(start_date, get_start_date_of_previous_month(end_date))

    def _fetch_monthly_trade_area_demographics_result(self, entity_id):

        query = {"_id": entity_id}
        entity_fields = ["_id", "data.analytics.demographics.monthly.TOTPOP_CY"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query,
                                                   entity_fields=entity_fields, as_list=True)["params"]

        # Returning result[first trade area found][index to the analytics data][first target year entry]
        return self.main_access.mds.call_find_entities_raw("trade_area", params, self.context)[0][1][0]

    def _build_run_calc_params(self, entity_type, entity_ids):
        return {
            "target_entity_ids": entity_ids,
            "target_entity_type": entity_type,
            "options": {
                "fetch": True,
                "save": True,
                "return": True,
                "overwrite": True,
                "sample": False,
                "summary": False
            }
        }
