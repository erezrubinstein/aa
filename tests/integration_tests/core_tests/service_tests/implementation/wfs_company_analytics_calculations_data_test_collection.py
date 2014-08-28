from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_store, insert_test_trade_area
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import START_OF_WORLD, END_OF_WORLD
from numpy.lib.function_base import median
from bson.objectid import ObjectId
import datetime
import numpy


__author__ = 'vgold'


class WFSCompanyAnalyticsCalculationsDataTestCollection(ServiceTestCollection):

    def initialize(self):

        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            'user_id': ObjectId(),
            'source': 'wfs_company_analytics_calculations_test_collection.py'
        }

    def setUp(self):

        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def wfs_test_company_analytics_task__trade_area_store_level_default_calcs(self):
        """
        The monster setup returns three home trade areas corresponding to stores HS1, HS2, HS3. Their competition timelines are given below

        KEY:
             )    = exclusive
             [    = inclusive
             xNSM = {
                        x: Home (H), Primary (P), or Secondary (S) competitor
                        N: Company # (1 or 2). Not displayed for the Home Company
                        S: Store
                        M: Store # (1, 2, or 3)
             }


        Home Trade Area 1 (dem_total_population = 1000, dem_total_income = 500)

                      2011                                                                    2012                                                                    2013
                      01    02    03    04    05    06    07    08    09    10    11    12    01    02    03    04    05    06    07    08    09    10    11    12    01    02    03    04    05    06    07    08    09    10    11    12
         HOME STORE
                HS1                               [-----------------------------------------------------------------------------------------------------------------------------------------------)
         COMPETITOR
                HS2   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                HS3   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               P1S1   -----------------------------------------------------------------------------------------------------)
               P1S2   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               P1S3         [--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               S1S1                                                                                                   [---)
               S1S2                                                                          [-)
               S1S3                                                                                                                                                                           [--------------------------------------------


        Home Trade Area 2 (dem_total_population = 1200, dem_total_income = 400)

                      2011                                                                    2012                                                                    2013
                      01    02    03    04    05    06    07    08    09    10    11    12    01    02    03    04    05    06    07    08    09    10    11    12    01    02    03    04    05    06    07    08    09    10    11    12
         HOME STORE
                HS2   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
         COMPETITOR
                HS1                               [-----------------------------------------------------------------------------------------------------------------------------------------------)
                HS3   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               P2S1   ----------------------------------------------------------------------------------------------------)
               P2S2   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               P2S3                                                                                [-------)
               S2S1   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               S2S2             [------------)
               S2S3   [--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


        Home Trade Area 3 (dem_total_population = 1500, dem_total_income = 300)

                      2011                                                                    2012                                                                    2013
                      01    02    03    04    05    06    07    08    09    10    11    12    01    02    03    04    05    06    07    08    09    10    11    12    01    02    03    04    05    06    07    08    09    10    11    12
         HOME STORE
                HS3   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
         COMPETITOR
                HS1                               [-----------------------------------------------------------------------------------------------------------------------------------------------)
               P2S3                                                                                [-------)
               S2S2             [------------)
               S1S3                                                                                                                                                                           [--------------------------------------------

        """
        home_company_id, home_trade_area_1_id, home_trade_area_2_id, home_trade_area_3_id = self._monster_setup()

        # run analytics
        task_rec = {
            'input': {
                'banner_ids': [home_company_id],
                'engines': ["demographics", "competition", "monopolies", "stores"],
                'spawn_async_tasks': False,
                'wait_for_tasks': True,
                'sleep_interval': 1,
                'run_report': False
            },
            'meta': {
                'async': False
            }
        }

        self.wfs_access.call_task_new('retail_analytics',
                                      'analytics',
                                      'company_analytics_calculations',
                                      task_rec,
                                      self.context,
                                      timeout = 999999)

        home_company = self.main_access.mds.call_find_entities_raw('company', {'query': {'_id': ObjectId(home_company_id)}, 'entity_fields': ['_id', 'data']})[0]
        home_trade_area_1 = self.main_access.mds.call_find_entities_raw('trade_area', {'query': {'_id': ObjectId(home_trade_area_1_id)}, 'entity_fields': ['_id', 'data']})[0]
        home_trade_area_2 = self.main_access.mds.call_find_entities_raw('trade_area', {'query': {'_id': ObjectId(home_trade_area_2_id)}, 'entity_fields': ['_id', 'data']})[0]
        home_trade_area_3 = self.main_access.mds.call_find_entities_raw('trade_area', {'query': {'_id': ObjectId(home_trade_area_3_id)}, 'entity_fields': ['_id', 'data']})[0]

        expected_company_months = [r["date"] for r in home_trade_area_3['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:]]
        expected_company_months__growth = [r["date"] for r in home_trade_area_3['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][:-1][-31:]]

        # ____ "Monthly Away Store Count"
        self.verify_monthly_away_store_count(home_trade_area_1, home_trade_area_2, home_trade_area_3)

        # ____ "Monthly Mean Trade Area Competition Ratio" // "Monthly Median Trade Area Competition Ratio"
        months_competition_weights__raw = self.verify_monthly_mean_median_ta_competition_ratio(home_company, home_trade_area_1, home_trade_area_2, home_trade_area_3)

        # ____ "Trade Area Aggregate Income"
        self.verify_trade_area_aggregate_income(home_trade_area_1, home_trade_area_2, home_trade_area_3)

        # ____ "Monthly Trade Area Total Population Demographics"
        self.verify_monthly_trade_area_total_population_demographics(home_trade_area_1, home_trade_area_2, home_trade_area_3)

        # ____ "Monthly Trade Area Total Population Competition Adjusted Demographics"
        months_c_adjusted_tot_pop, months_competition_weights_weighted = self.verify_monthly_trade_area_total_population_competition_adjusted_demographics(home_trade_area_1, home_trade_area_2, home_trade_area_3)

        # ____ "Monthly Trade Area Total Income Demographics"
        self.verify_monthly_trade_area_total_income_demographics(home_trade_area_1, home_trade_area_2, home_trade_area_3)

        # ____ "Monthly Trade Area Total Income Competition Adjusted Demographics"
        months_c_adjusted_tot_inc = self.verify_monthly_trade_area_total_income_competition_adjusted_demographics(home_trade_area_1, home_trade_area_2, home_trade_area_3)

        # ____ "Monthly Single Player Monopolies"
        self.verify_monthly_single_player_monopolies(home_company, expected_company_months)

        # ____ "Monthly Store Count"
        self.verify_monthly_store_count(home_company, expected_company_months)

        # ____ "Monthly Store Openings"
        self.verify_monthly_store_openings(home_company, expected_company_months)

        # ____ "Monthly Store Closings"
        self.verify_monthly_store_closings(home_company, expected_company_months)

        # ____ "Monthly Store Growth"
        self.verify_monthly_store_growth(home_company, expected_company_months__growth)

        # ____ "Monthly Company Store Median Total Population Demographics"
        self.verify_monthly_company_store_median_total_population(home_company, expected_company_months)

        # ____ "Monthly Company Store Median Competition Adjusted Total Population Demographics"
        self.verify_monthly_company_store_median_competition_adjusted_total_population(home_company, expected_company_months, months_c_adjusted_tot_pop)

        # ____ "Monthly Company Store Median Total Income Demographics"
        self.verify_monthly_company_store_median_total_income(home_company, expected_company_months)

        # ____ "Monthly Company Store Median Competition Adjusted Total Income Demographics"
        self.verify_monthly_company_store_median_competition_adjusted_total_income(home_company, expected_company_months, months_c_adjusted_tot_inc)

        # ____ "Monthly Company Store Max Total Population Demographics"
        self.verify_monthly_company_store_max_total_population(home_company, expected_company_months)

        # ____ "Monthly Company Store Max Competition Adjusted Total Population Demographics"
        self.verify_monthly_company_store_max_competition_adjusted_total_population(home_company, expected_company_months, months_c_adjusted_tot_pop)

        # ____ "Monthly Company Store Max Total Income Demographics"
        self.verify_monthly_company_store_max_total_income(home_company, expected_company_months)

        # ____ "Monthly Company Store Max Competition Adjusted Total Income Demographics"
        self.verify_monthly_company_store_max_competition_adjusted_total_income(home_company, expected_company_months, months_c_adjusted_tot_inc)

        # ____ "Monthly Company Store Mean Competition Adjusted Total Population Demographics"
        self.verify_monthly_company_store_mean_competition_adjusted_total_population(home_company, expected_company_months, months_c_adjusted_tot_pop)

        # ____ "Monthly Company Store Mean Competition Adjusted Total Income Demographics"
        self.verify_monthly_company_store_mean_competition_adjusted_total_income(home_company, expected_company_months, months_c_adjusted_tot_inc)

        # ____ "Monthly Company Store Variance Competition Adjusted Total Population Demographics"
        self.verify_monthly_company_store_variance_competition_adjusted_total_population(home_company, expected_company_months, months_c_adjusted_tot_pop)

        # ____ "Monthly Company Store Variance Competition Adjusted Total Income Demographics"
        self.verify_monthly_company_store_variance_competition_adjusted_total_income(home_company, expected_company_months, months_c_adjusted_tot_inc)

        # ____ "Monthly Company Store Median Competition Adjusted Total Population Demographics For Store Openings"
        self.verify_monthly_company_store_median_competition_adjusted_total_population__openings(home_company, home_trade_area_1)

        # ____ "Monthly Company Store Median Competition Adjusted Total Population Demographics For Store Closings"
        self.verify_monthly_company_store_median_competition_adjusted_total_population__closings(home_company, home_trade_area_1)

        # ____ "Monthly Company Store Median Competition Adjusted Total Income Demographics For Store Openings"
        self.verify_monthly_company_store_median_competition_adjusted_total_income__openings(home_company, home_trade_area_1)

        # ____ "Monthly Company Store Median Competition Adjusted Total Income Demographics For Store Closings"
        self.verify_monthly_company_store_median_competition_adjusted_total_income__closings(home_company, home_trade_area_1)

        # ____ "Monthly Company Store Average Competition Weight"
        self.verify_monthly_average_competition_weight__cluster(home_company, expected_company_months)
        self.verify_monthly_average_competition_weight__total(home_company, expected_company_months, months_competition_weights_weighted, months_competition_weights__raw)
        self.verify_monthly_average_competition_weight__primary(home_company, expected_company_months)
        self.verify_monthly_average_competition_weight__secondary(home_company, expected_company_months)

    def verify_monthly_average_competition_weight__total(self, home_company, expected_months, months_competition_weights, months_competition_weights__raw):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["total"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["total"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            _m = timeseries_to_test[i]
            vals_weighted = months_competition_weights[_m["date"]]
            vals_raw = months_competition_weights__raw[_m["date"]]

            # the sum filters out zero entries :)
            average = sum(vals_weighted) / float(sum(vals_raw))
            self.test_case.assertAlmostEqual(average, _m["value"], 4)


    def verify_monthly_average_competition_weight__secondary(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["secondary"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["secondary"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            self.test_case.assertEqual(0.5, timeseries_to_test[i]["value"])


    def verify_monthly_average_competition_weight__primary(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["primary"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["primary"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            self.test_case.assertEqual(1.0, timeseries_to_test[i]["value"])


    def verify_monthly_average_competition_weight__cluster(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["cluster"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["cluster"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            self.test_case.assertEqual(1.0, timeseries_to_test[i]["value"])


    def verify_monthly_company_store_median_competition_adjusted_total_income__closings(self, home_company, home_trade_area_1):

        competition_ratio = home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][0]["value"] + 1

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income_for_store_closings"]["median"][0]["series"]
        self.test_case.assertEqual(1, len(timeseries_to_test))
        self.test_case.assertEqual("2013-05-01T00:00:00", timeseries_to_test[0]["date"])
        self.test_case.assertAlmostEqual(500000 / competition_ratio, timeseries_to_test[0]["value"], 4)

    def verify_monthly_company_store_median_competition_adjusted_total_income__openings(self, home_company, home_trade_area_1):

        competition_ratio = home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-1]["value"] + 1

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income_for_store_openings"]["median"][0]["series"]
        self.test_case.assertEqual(1, len(timeseries_to_test))
        self.test_case.assertAlmostEqual(500000 / competition_ratio, timeseries_to_test[0]["value"], 4)
        self.test_case.assertEqual("2011-05-01T00:00:00", timeseries_to_test[0]["date"])


    def verify_monthly_company_store_median_competition_adjusted_total_population__closings(self, home_company, home_trade_area_1):

        competition_ratio = home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][0]["value"] + 1

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population_for_store_closings"]["median"][0]["series"]
        self.test_case.assertEqual(1, len(timeseries_to_test))
        self.test_case.assertEqual("2013-05-01T00:00:00", timeseries_to_test[0]["date"])
        self.test_case.assertAlmostEqual(1000 / competition_ratio, timeseries_to_test[0]["value"], 4)


    def verify_monthly_company_store_median_competition_adjusted_total_population__openings(self, home_company, home_trade_area_1):

        competition_ratio = home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-1]["value"] + 1

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population_for_store_openings"]["median"][0]["series"]
        self.test_case.assertEqual(1, len(timeseries_to_test))
        self.test_case.assertAlmostEqual(1000 / competition_ratio, timeseries_to_test[0]["value"], 4)
        self.test_case.assertEqual("2011-05-01T00:00:00", timeseries_to_test[0]["date"])


    def verify_monthly_company_store_variance_competition_adjusted_total_income(self, home_company, expected_months, months_c_adjusted_tot_inc):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["variance"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["variance"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]
            vals = months_c_adjusted_tot_inc[month["date"]]
            self.test_case.assertEqual("%.4f" % numpy.var(vals), "%.4f" % month["value"])

    def verify_monthly_company_store_variance_competition_adjusted_total_population(self, home_company, expected_months, months_c_adjusted_tot_pop):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["variance"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["variance"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]
            vals = months_c_adjusted_tot_pop[month["date"]]
            self.test_case.assertEqual("%.4f" % numpy.var(vals), "%.4f" % month["value"])

    def verify_monthly_company_store_mean_competition_adjusted_total_income(self, home_company, expected_months, months_c_adjusted_tot_inc):
        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["mean"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["mean"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]
            vals = months_c_adjusted_tot_inc[month["date"]]
            self.test_case.assertAlmostEqual(sum(vals) / float(len(vals)), month["value"], 4)

    def verify_monthly_company_store_mean_competition_adjusted_total_population(self, home_company, expected_months, months_c_adjusted_tot_pop):
        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["mean"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["mean"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]
            vals = months_c_adjusted_tot_pop[month["date"]]
            self.test_case.assertAlmostEqual(sum(vals) / float(len(vals)), month["value"], 4)

    def verify_monthly_company_store_max_competition_adjusted_total_income(self, home_company, expected_months, months_c_adjusted_tot_inc):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["max"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["max"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]

            self.test_case.assertEqual(max(months_c_adjusted_tot_inc[month["date"]]), month["value"])

    def verify_monthly_company_store_max_total_income(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["max"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["max"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            if i in [0, 1, 2, 3, 28, 29, 30]:
                self.test_case.assertEqual(480000.0, timeseries_to_test[i]["value"])

            else:
                self.test_case.assertEqual(500000, timeseries_to_test[i]["value"])

    def verify_monthly_company_store_max_competition_adjusted_total_population(self, home_company, expected_months, months_c_adjusted_tot_pop):
        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["max"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["max"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]

            self.test_case.assertEqual(max(months_c_adjusted_tot_pop[month["date"]]), month["value"])

    def verify_monthly_company_store_max_total_population(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["max"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["max"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            self.test_case.assertEqual(1500.0, timeseries_to_test[i]["value"])

    def verify_monthly_company_store_median_competition_adjusted_total_income(self, home_company, expected_months, months_c_adjusted_tot_inc):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["median"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["median"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]

            self.test_case.assertEqual(median(months_c_adjusted_tot_inc[month["date"]]), month["value"])

    def verify_monthly_company_store_median_total_income(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["median"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_income"]["median"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]

            if i in [0, 1, 2, 3, 28, 29, 30]:
                self.test_case.assertEqual(465000.0, month["value"])

            else:
                self.test_case.assertEqual(480000, month["value"])

    def verify_monthly_company_store_median_competition_adjusted_total_population(self, home_company, expected_months, months_c_adjusted_tot_pop):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["median"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["median"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]

            self.test_case.assertEqual(median(months_c_adjusted_tot_pop[month["date"]]), month["value"])

    def verify_monthly_company_store_median_total_population(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["median"][0]["series"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["median"][0]["series"][-31:][::-1]

        for i in range(len(timeseries_to_test)):

            month = timeseries_to_test[i]

            if i in [0, 1, 2, 3, 28, 29, 30]:
                self.test_case.assertEqual(1350.0, month["value"])

            else:
                self.test_case.assertEqual(1200, month["value"])

    def verify_monthly_store_growth(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["stores"]["monthly"]["store_growth"][-31:]]

        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["stores"]["monthly"]["store_growth"][-31:][::-1]

        for i in range(len(timeseries_to_test)):
            month = timeseries_to_test[i]

            if month["date"] == "2011-05-01T00:00:00":
                self.test_case.assertEqual(0.5, month["value"])

            elif month["date"] == "2013-05-01T00:00:00":
                self.test_case.assertAlmostEqual(-0.3333, month["value"], 4)

            else:
                self.test_case.assertEqual(0, month["value"])

    def verify_monthly_store_closings(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["stores"]["monthly"]["store_closings"][-31:]]

        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["stores"]["monthly"]["store_closings"][-31:][::-1]

        for i in range(31):
            month = timeseries_to_test[i]

            if i == 28:
                self.test_case.assertEqual(1, month["value"])
            else:
                self.test_case.assertEqual(0, month["value"])

    def verify_monthly_store_openings(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["stores"]["monthly"]["store_openings"][-31:]]

        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["stores"]["monthly"]["store_openings"][-31:][::-1]

        for i in range(31):
            month = timeseries_to_test[i]

            if i == 4:
                self.test_case.assertEqual(1, month["value"])
            else:
                self.test_case.assertEqual(0, month["value"])

    def verify_monthly_store_count(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["stores"]["monthly"]["store_counts"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["stores"]["monthly"]["store_counts"][-31:][::-1]

        for i in range(31):
            month = timeseries_to_test[i]

            if i in [0, 1, 2, 3, 28, 29, 30]:

                self.test_case.assertEqual(2, month["value"])

            else:
                self.test_case.assertEqual(3, month["value"])

    def verify_monthly_single_player_monopolies(self, home_company, expected_months):

        actual_months = [r["date"] for r in home_company["data"]["analytics"]["monopolies"]["monthly"]["DistanceMiles10"]["store_monopoly_percent"][-31:]]
        self.test_case.assertEqual(expected_months, actual_months)

        timeseries_to_test = home_company["data"]["analytics"]["monopolies"]["monthly"]["DistanceMiles10"]["store_monopoly_percent"][-31:][::-1]

        for i in range(31):
            month = timeseries_to_test[i]

            if i in [1, 2, 12, 13, 28, 29, 30]:
                self.test_case.assertEqual(0.0, month["value"])

            elif i in [0, 3]:
                self.test_case.assertEqual(50.0, month["value"])

            else:
                self.test_case.assertAlmostEqual(33.3333, month["value"], 4)


    def verify_monthly_trade_area_total_income_demographics(self, home_trade_area_1, home_trade_area_2, home_trade_area_3):

        # ____ first trade area
        # _____________________
        # ____ we have already verified the dates in the away store counts raw list
        expected_dates = [r["date"] for r in home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:]]
        actual_dates = [r["date"] for r in home_trade_area_1['data']['analytics']['demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]]
        self.test_case.assertEqual(expected_dates, actual_dates)

        for month in home_trade_area_1['data']['analytics']['demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]:
            self.test_case.assertEqual(500000, month["value"])

        # ____ second trade area
        # ______________________
        # ____ we have already verified the dates in the away store counts raw list
        expected_dates = [r["date"] for r in home_trade_area_2['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:]]
        actual_dates = [r["date"] for r in home_trade_area_2['data']['analytics']['demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]]
        self.test_case.assertEqual(expected_dates, actual_dates)

        for month in home_trade_area_2['data']['analytics']['demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]:
            self.test_case.assertEqual(480000, month["value"])

        # ____ third trade area
        # _____________________
        # ____ we have already verified the dates in the away store counts raw list
        expected_dates = [r["date"] for r in home_trade_area_3['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:]]
        actual_dates = [r["date"] for r in home_trade_area_3['data']['analytics']['demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]]
        self.test_case.assertEqual(expected_dates, actual_dates)

        for month in home_trade_area_3['data']['analytics']['demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]:
            self.test_case.assertEqual(450000, month["value"])


    def verify_monthly_trade_area_total_income_competition_adjusted_demographics(self, home_trade_area_1, home_trade_area_2, home_trade_area_3):

        months_weighted_ratios = {}

        # ____ first trade area
        # _____________________
        for month in home_trade_area_1['data']['analytics']['competition_adjusted_demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]:

            adjusted_factor_list = [r["value"] for r in home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-31:] if r["date"] == month["date"]]
            self.test_case.assertEqual(1, len(adjusted_factor_list))
            self.test_case.assertAlmostEqual(500000 / (adjusted_factor_list[0] + 1.0), month["value"], 4)

            if month["date"] not in months_weighted_ratios:
                months_weighted_ratios[month["date"]] = []

            months_weighted_ratios[month["date"]].append(month["value"])

        # ____ second trade area
        # ______________________
        for month in home_trade_area_2['data']['analytics']['competition_adjusted_demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]:

            adjusted_factor_list = [r["value"] for r in home_trade_area_2['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-31:] if r["date"] == month["date"]]
            self.test_case.assertEqual(1, len(adjusted_factor_list))
            self.test_case.assertAlmostEqual(480000 / (adjusted_factor_list[0] + 1.0), month["value"], 4)

            if month["date"] not in months_weighted_ratios:
                months_weighted_ratios[month["date"]] = []

            months_weighted_ratios[month["date"]].append(month["value"])

        # ____ third trade area
        # _____________________
        for month in home_trade_area_3['data']['analytics']['competition_adjusted_demographics']['monthly']['AGG_INCOME_CY'][0]["series"][-31:]:

            adjusted_factor_list = [r["value"] for r in home_trade_area_3['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-31:] if r["date"] == month["date"]]
            self.test_case.assertEqual(1, len(adjusted_factor_list))
            self.test_case.assertAlmostEqual(450000 / (adjusted_factor_list[0] + 1.0), month["value"], 4)

            if month["date"] not in months_weighted_ratios:
                months_weighted_ratios[month["date"]] = []

            months_weighted_ratios[month["date"]].append(month["value"])

        return months_weighted_ratios
    def verify_monthly_trade_area_total_population_competition_adjusted_demographics(self, home_trade_area_1, home_trade_area_2, home_trade_area_3):

        months_weighted_ratios = {}
        adjusted_factors_dict = {}
        # ____ first trade area
        # _____________________
        for month in home_trade_area_1['data']['analytics']['competition_adjusted_demographics']['monthly']['TOTPOP_CY'][0]["series"][-31:]:

            adjusted_factor_list = [r["value"] for r in home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-31:] if r["date"] == month["date"]]
            self.test_case.assertEqual(1, len(adjusted_factor_list))
            self.test_case.assertAlmostEqual(1000 / (adjusted_factor_list[0] + 1.0), month["value"], 4)

            if month["date"] not in adjusted_factors_dict:
                adjusted_factors_dict[month["date"]] = []

            adjusted_factors_dict[month["date"]].append(adjusted_factor_list[0])


            if month["date"] not in months_weighted_ratios:
                months_weighted_ratios[month["date"]] = []

            months_weighted_ratios[month["date"]].append(month["value"])

        # ____ second trade area
        # ______________________
        for month in home_trade_area_2['data']['analytics']['competition_adjusted_demographics']['monthly']['TOTPOP_CY'][0]["series"][-31:]:

            adjusted_factor_list = [r["value"] for r in home_trade_area_2['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-31:] if r["date"] == month["date"]]
            self.test_case.assertEqual(1, len(adjusted_factor_list))
            self.test_case.assertAlmostEqual(1200 / (adjusted_factor_list[0] + 1.0), month["value"], 4)

            if month["date"] not in adjusted_factors_dict:
                adjusted_factors_dict[month["date"]] = []
            adjusted_factors_dict[month["date"]].append(adjusted_factor_list[0])

            if month["date"] not in months_weighted_ratios:
                months_weighted_ratios[month["date"]] = []

            months_weighted_ratios[month["date"]].append(month["value"])
        # ____ third trade area
        # _____________________
        for month in home_trade_area_3['data']['analytics']['competition_adjusted_demographics']['monthly']['TOTPOP_CY'][0]["series"][-31:]:

            adjusted_factor_list = [r["value"] for r in home_trade_area_3['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-31:] if r["date"] == month["date"]]
            self.test_case.assertEqual(1, len(adjusted_factor_list))
            self.test_case.assertAlmostEqual(1500 / (adjusted_factor_list[0] + 1.0), month["value"], 4)

            if month["date"] not in adjusted_factors_dict:
                adjusted_factors_dict[month["date"]] = []
            adjusted_factors_dict[month["date"]].append(adjusted_factor_list[0])

            if month["date"] not in months_weighted_ratios:
                months_weighted_ratios[month["date"]] = []

            months_weighted_ratios[month["date"]].append(month["value"])

        return months_weighted_ratios, adjusted_factors_dict


    def verify_monthly_trade_area_total_population_demographics(self, home_trade_area_1, home_trade_area_2, home_trade_area_3):

        # ____ first trade area
        # _____________________
        # ____ we have already verified the dates in the away store counts raw list
        expected_dates = [r["date"] for r in home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:]]
        actual_dates = [r["date"] for r in home_trade_area_1['data']['analytics']['demographics']['monthly']['TOTPOP_CY'][0]["series"][-31:]]
        self.test_case.assertEqual(expected_dates, actual_dates)

        for month in home_trade_area_1['data']['analytics']['demographics']['monthly']['TOTPOP_CY'][0]["series"]:
            self.test_case.assertEqual(1000, month["value"])

        # ____ second trade area
        # ______________________
        # ____ we have already verified the dates in the away store counts raw list
        expected_dates = [r["date"] for r in home_trade_area_2['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:]]
        actual_dates = [r["date"] for r in home_trade_area_2['data']['analytics']['demographics']['monthly']['TOTPOP_CY'][0]["series"][-31:]]
        self.test_case.assertEqual(expected_dates, actual_dates)

        for month in home_trade_area_2['data']['analytics']['demographics']['monthly']['TOTPOP_CY'][0]["series"]:
            self.test_case.assertEqual(1200, month["value"])

        # ____ third trade area
        # _____________________
        # ____ we have already verified the dates in the away store counts raw list
        expected_dates = [r["date"] for r in home_trade_area_3['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:]]
        actual_dates = [r["date"] for r in home_trade_area_3['data']['analytics']['demographics']['monthly']['TOTPOP_CY'][0]["series"][-31:]]
        self.test_case.assertEqual(expected_dates, actual_dates)

        for month in home_trade_area_3['data']['analytics']['demographics']['monthly']['TOTPOP_CY'][0]["series"]:
            self.test_case.assertEqual(1500, month["value"])


    def verify_trade_area_aggregate_income(self, home_trade_area_1, home_trade_area_2, home_trade_area_3):

        self.test_case.assertEqual(500000, home_trade_area_1["data"]["analytics"]["demographics"]["AGG_INCOME_CY"]["value"])
        self.test_case.assertEqual(480000, home_trade_area_2["data"]["analytics"]["demographics"]["AGG_INCOME_CY"]["value"])
        self.test_case.assertEqual(450000, home_trade_area_3["data"]["analytics"]["demographics"]["AGG_INCOME_CY"]["value"])


    def verify_monthly_mean_median_ta_competition_ratio(self, home_company, home_trade_area_1, home_trade_area_2, home_trade_area_3):

        competition_ratios = {}
        for trade_area in [home_trade_area_1, home_trade_area_2, home_trade_area_3]:
            for weight in trade_area['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:]:

                if weight["date"] not in competition_ratios:
                    competition_ratios[weight["date"]] = []

                competition_ratios[weight["date"]].append(weight["value"])

        # ____ mean
        for tacr in home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_competition_ratio"]["mean"][-31:]:

            tas_mean = sum(competition_ratios[tacr["date"]]) / float(len(competition_ratios[tacr["date"]]))
            self.test_case.assertAlmostEqual(tas_mean, tacr["value"], 4)

        # ____ median
        for tacr in home_company["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_competition_ratio"]["median"][-31:]:

            tas_median = median(competition_ratios[tacr["date"]])
            self.test_case.assertEqual(tas_median, tacr["value"])

        return competition_ratios

    def verify_monthly_away_store_count(self, home_trade_area_1, home_trade_area_2, home_trade_area_3):

        # ____ first trade area
        self.test_case.assertEqual(home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['raw'], self.__get_ta_1_away_store_counts_raw())
        self.test_case.assertEqual(home_trade_area_1['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'], self.__get_ta_1_away_store_counts_weighted())

        # ____ second trade area
        self.test_case.assertEqual(home_trade_area_2['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:], self.__get_ta_2_away_store_counts_raw())
        self.test_case.assertEqual(home_trade_area_2['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-31:], self.__get_ta_2_away_store_counts_weighted())

        # ____ third trade area
        self.test_case.assertEqual(home_trade_area_3['data']['analytics']['competition']['monthly']['away_store_counts']['raw'][-31:], self.__get_ta_3_away_store_counts_raw())
        self.test_case.assertEqual(home_trade_area_3['data']['analytics']['competition']['monthly']['away_store_counts']['weighted'][-31:], self.__get_ta_3_away_store_counts_weighted())



    # ____ IMPLEMENTATION
    # ___________________


    def _monster_setup(self):

        # ____ insert test companies
        # __________________________
        home_company_id = insert_test_company(name = "home_company_id", type = "retail_banner", workflow_status = "published")

        primary_away_company_1 = insert_test_company(name = "primary_away_company_1", type = "retail_banner", workflow_status = "published")
        primary_away_company_2 = insert_test_company(name = "primary_away_company_2", type = "retail_banner", workflow_status = "published")

        secondary_away_company_1 = insert_test_company(name = "secondary_away_company_1", type = "retail_banner", workflow_status = "published")
        secondary_away_company_2 = insert_test_company(name = "secondary_away_company_2", type = "retail_banner", workflow_status = "published")


        # ____ insert test stores (12 competitors (3 x competitor), 3 home stores)
        # ________________________________________________________________________
        home_store_1_interval = [datetime.datetime(2011, 05, 18), datetime.datetime(2013, 05, 18)]
        home_store_1_id = insert_test_store(home_company_id, home_store_1_interval)

        home_store_2_interval = [START_OF_WORLD, END_OF_WORLD]
        home_store_2_id = insert_test_store(home_company_id, home_store_2_interval)

        home_store_3_interval = [START_OF_WORLD, END_OF_WORLD]
        home_store_3_id = insert_test_store(home_company_id, home_store_3_interval)


        # ____ primary away stores from primary away company 1
        primary_away_1_store_1_interval = [START_OF_WORLD, datetime.datetime(2012, 05, 31, 12, 0, 0)]
        primary_away_1_store_1_id = insert_test_store(primary_away_company_1, primary_away_1_store_1_interval)

        primary_away_1_store_2_interval = [START_OF_WORLD, END_OF_WORLD]
        primary_away_1_store_2_id = insert_test_store(primary_away_company_1, primary_away_1_store_2_interval)

        primary_away_1_store_3_interval = [datetime.datetime(2011, 02, 01), END_OF_WORLD]
        primary_away_1_store_3_id = insert_test_store(primary_away_company_1, primary_away_1_store_3_interval)


        # ____ primary away stores from primary away company 2
        primary_away_2_store_1_interval = [START_OF_WORLD, datetime.datetime(2012, 05, 15, 12, 0, 0)]
        primary_away_2_store_1_id = insert_test_store(primary_away_company_2, primary_away_2_store_1_interval)

        primary_away_2_store_2_interval = [START_OF_WORLD, END_OF_WORLD]
        primary_away_2_store_2_id= insert_test_store(primary_away_company_2, primary_away_2_store_2_interval)

        primary_away_2_store_3_interval = [datetime.datetime(2012, 01, 31, 23, 0, 0), datetime.datetime(2012, 03, 01)]
        primary_away_2_store_3_id = insert_test_store(primary_away_company_2, primary_away_2_store_3_interval)


        # ____ secondary away stores from secondary away company 1
        secondary_away_1_store_1_interval = [datetime.datetime(2012, 05, 01), datetime.datetime(2012, 05, 18)]
        secondary_away_1_store_1_id = insert_test_store(secondary_away_company_1, secondary_away_1_store_1_interval)

        secondary_away_1_store_2_interval = [datetime.datetime(2011, 12, 25), datetime.datetime(2012, 01, 01)]
        secondary_away_1_store_2_id = insert_test_store(secondary_away_company_1, secondary_away_1_store_2_interval)

        secondary_away_1_store_3_interval = [datetime.datetime(2013, 05, 01), END_OF_WORLD]
        secondary_away_1_store_3_id = insert_test_store(secondary_away_company_1, secondary_away_1_store_3_interval)


        # ____ secondary away stores from secondary away company 2
        secondary_away_2_store_1_interval = [START_OF_WORLD, END_OF_WORLD]
        secondary_away_2_store_1_id = insert_test_store(secondary_away_company_2, secondary_away_2_store_1_interval)

        secondary_away_2_store_2_interval = [datetime.datetime(2011, 02, 15), datetime.datetime(2011, 04, 30)]
        secondary_away_2_store_2_id = insert_test_store(secondary_away_company_2, secondary_away_2_store_2_interval)

        secondary_away_2_store_3_interval = [datetime.datetime(2011, 01, 01), END_OF_WORLD]
        secondary_away_2_store_3_id = insert_test_store(secondary_away_company_2, secondary_away_2_store_3_interval)

        # ____ insert test home trade area with competitors
        # _________________________________________________
        # ____ the first home store gets all of the primary away company 1 and secondary away company 1 stores
        home_store_1_competitive_stores = [

            # ____ competitors from the same company
            self._competitive_store_doc(home_company_id, home_store_2_id, home_store_1_interval, home_store_2_interval, 1.0),
            self._competitive_store_doc(home_company_id, home_store_3_id, home_store_1_interval, home_store_3_interval, 1.0),

            # ____ competitors from the first primary competitive company
            self._competitive_store_doc(primary_away_company_1, primary_away_1_store_1_id, home_store_1_interval, primary_away_1_store_1_interval, 1.0),
            self._competitive_store_doc(primary_away_company_1, primary_away_1_store_2_id, home_store_1_interval, primary_away_1_store_2_interval, 1.0),
            self._competitive_store_doc(primary_away_company_1, primary_away_1_store_3_id, home_store_1_interval, primary_away_1_store_3_interval, 1.0),

            # ____ competitors from the first secondary competitive company
            self._competitive_store_doc(secondary_away_company_1, secondary_away_1_store_1_id, home_store_1_interval, secondary_away_1_store_1_interval, 0.5),
            self._competitive_store_doc(secondary_away_company_1, secondary_away_1_store_2_id, home_store_1_interval, secondary_away_1_store_2_interval, 0.5),
            self._competitive_store_doc(secondary_away_company_1, secondary_away_1_store_3_id, home_store_1_interval, secondary_away_1_store_3_interval, 0.5)

        ]

        # ____ the second home store gets all of the primary away company 2 and secondary away company 2 stores
        home_store_2_competitive_stores = [

            # ____ competitors from the same company
            self._competitive_store_doc(home_company_id, home_store_1_id, home_store_2_interval, home_store_1_interval, 1.0),
            self._competitive_store_doc(home_company_id, home_store_3_id, home_store_2_interval, home_store_3_interval, 1.0),

            # ____ competitors from the first primary competitive company
            self._competitive_store_doc(primary_away_company_2, primary_away_2_store_1_id, home_store_2_interval, primary_away_2_store_1_interval, 1.0),
            self._competitive_store_doc(primary_away_company_2, primary_away_2_store_2_id, home_store_2_interval, primary_away_2_store_2_interval, 1.0),
            self._competitive_store_doc(primary_away_company_2, primary_away_2_store_3_id, home_store_2_interval, primary_away_2_store_3_interval, 1.0),

            # ____ competitors from the first secondary competitive company
            self._competitive_store_doc(secondary_away_company_2, secondary_away_2_store_1_id, home_store_2_interval, secondary_away_2_store_1_interval, 0.5),
            self._competitive_store_doc(secondary_away_company_2, secondary_away_2_store_2_id, home_store_2_interval, secondary_away_2_store_2_interval, 0.5),
            self._competitive_store_doc(secondary_away_company_2, secondary_away_2_store_3_id, home_store_2_interval, secondary_away_2_store_3_interval, 0.5)

        ]

        # ____ the third home store gets combinations that produce monopolies during certain months
        home_store_3_competitive_stores = [

            # ___
            self._competitive_store_doc(home_company_id, home_store_1_id, home_store_3_interval, home_store_1_interval, 1.0),

            # ____ starts datetime.datetime(2011, 02, 15), ends datetime.datetime(2011, 04, 31)]
            self._competitive_store_doc(secondary_away_company_2, secondary_away_2_store_2_id, home_store_3_interval, secondary_away_2_store_2_interval, 0.5),

            # ____ starts datetime.datetime(2012, 01, 31, 23, 0, 0), ends datetime.datetime(2012, 03, 01)
            self._competitive_store_doc(primary_away_company_2, primary_away_2_store_3_id, home_store_3_interval, primary_away_2_store_3_interval, 1.0),

            # ___ starts datetime.datetime(2013, 05, 01)
            self._competitive_store_doc(secondary_away_company_1, secondary_away_1_store_3_id, home_store_3_interval, secondary_away_1_store_3_interval, 0.5)

        ]

        home_store_3_monopolies = [
            {
                "start_date": START_OF_WORLD.isoformat(),
                "end_date": secondary_away_2_store_2_interval[0],
                "monopoly_type": "AbsoluteMonopoly"
            },
            {
                "start_date": secondary_away_2_store_2_interval[1].isoformat(),
                "end_date": home_store_1_interval[0].isoformat(),
                "monopoly_type": "AbsoluteMonopoly"
            },
            {
                "start_date": home_store_1_interval[0].isoformat(),
                "end_date": primary_away_2_store_3_interval[0].isoformat(),
                "monopoly_type": "SinglePlayerMonopoly"
            },
            {
                "start_date": primary_away_2_store_3_interval[1].isoformat(),
                "end_date": secondary_away_1_store_3_interval[0].isoformat(),
                "monopoly_type": "SinglePlayerMonopoly"
            }
        ]

        return (
            home_company_id,
            insert_test_trade_area(home_store_1_id, home_company_id, opened_date = home_store_1_interval[0], closed_date = home_store_1_interval[1], competitive_stores = home_store_1_competitive_stores, dem_total_population = 1000, per_capita_income = 500, monopolies = []),
            insert_test_trade_area(home_store_2_id, home_company_id, opened_date = home_store_2_interval[0], closed_date = home_store_2_interval[1], competitive_stores = home_store_2_competitive_stores, dem_total_population = 1200, per_capita_income = 400, monopolies = []),
            insert_test_trade_area(home_store_3_id, home_company_id, opened_date = home_store_3_interval[0], closed_date = home_store_3_interval[1], competitive_stores = home_store_3_competitive_stores, dem_total_population = 1500, per_capita_income = 300, monopolies = home_store_3_monopolies)
        )


    def _competitive_store_doc(self, away_company_id, away_store_id, home_store_interval, away_store_interval, weight):

        if home_store_interval[0] > away_store_interval[0]:
            start_date = home_store_interval[0]
        else:
            start_date = away_store_interval[0]

        if home_store_interval[1] < away_store_interval[1]:
            end_date = home_store_interval[1]
        else:
            end_date = away_store_interval[1]

        return {
            "away_company_id": away_company_id,
            "away_store_id": away_store_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "weight": weight,
            "away_company_name": "away_company_name",
            "away_street_number": "away_street_number",
            "away_street": "away_street",
            "away_city": "away_city",
            "away_state": "away_state",
            "away_zip": "away_zip",
            "away_geo": ["away_geo_lng", "away_geo_lat"],
            "away_lng": "away_geo_lng",
            "away_lat": "away_geo_lat"
        }

    # ____ data feed

    def __get_ta_1_away_store_counts_raw(self):

        return [
            {
                "date": "2013-04-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-03-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-02-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-01-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-12-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-11-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-10-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-09-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-08-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-07-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-06-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-05-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-04-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-03-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-02-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-01-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-12-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-11-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-10-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-09-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-08-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-07-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-06-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-05-01T00:00:00",
                "value": 5
            }
        ]

    def __get_ta_1_away_store_counts_weighted(self):

        return [
            {
                "date": "2013-04-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-03-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-02-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-01-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-12-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-11-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-10-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-09-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-08-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-07-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-06-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-05-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-04-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-03-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-02-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-01-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-12-01T00:00:00",
                "value": 5.5
            },
            {
                "date": "2011-11-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-10-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-09-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-08-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-07-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-06-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-05-01T00:00:00",
                "value": 5
            }
        ]

    def __get_ta_2_away_store_counts_raw(self):

        return [
            {
                "date": "2013-07-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-06-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-05-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-04-01T00:00:00",
                "value": 5
            },
            {
                "date": "2013-03-01T00:00:00",
                "value": 5
            },
            {
                "date": "2013-02-01T00:00:00",
                "value": 5
            },
            {
                "date": "2013-01-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-12-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-11-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-10-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-09-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-08-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-07-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-06-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-05-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-04-01T00:00:00",
                "value": 6
            },
            {
                "date": "2012-03-01T00:00:00",
                "value": 6
            },
            {
                "date": "2012-02-01T00:00:00",
                "value": 7
            },
            {
                "date": "2012-01-01T00:00:00",
                "value": 7
            },
            {
                "date": "2011-12-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-11-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-10-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-09-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-08-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-07-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-06-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-05-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-04-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-03-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-02-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-01-01T00:00:00",
                "value": 5
            }
        ]

    def __get_ta_2_away_store_counts_weighted(self):

        return [
            {
                "date": "2013-07-01T00:00:00",
                "value": 3
            },
            {
                "date": "2013-06-01T00:00:00",
                "value": 3
            },
            {
                "date": "2013-05-01T00:00:00",
                "value": 3
            },
            {
                "date": "2013-04-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-03-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-02-01T00:00:00",
                "value": 4
            },
            {
                "date": "2013-01-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-12-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-11-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-10-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-09-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-08-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-07-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-06-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-05-01T00:00:00",
                "value": 4
            },
            {
                "date": "2012-04-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-03-01T00:00:00",
                "value": 5
            },
            {
                "date": "2012-02-01T00:00:00",
                "value": 6
            },
            {
                "date": "2012-01-01T00:00:00",
                "value": 6
            },
            {
                "date": "2011-12-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-11-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-10-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-09-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-08-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-07-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-06-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-05-01T00:00:00",
                "value": 5
            },
            {
                "date": "2011-04-01T00:00:00",
                "value": 4.0
            },
            {
                "date": "2011-03-01T00:00:00",
                "value": 4.5
            },
            {
                "date": "2011-02-01T00:00:00",
                "value": 4.5
            },
            {
                "date": "2011-01-01T00:00:00",
                "value": 4
            }
        ]

    def __get_ta_3_away_store_counts_raw(self):
        return [
            {
                "date": "2013-07-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-06-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-05-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-04-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-03-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-02-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-01-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-12-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-11-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-10-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-09-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-08-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-07-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-06-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-05-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-04-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-03-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-02-01T00:00:00",
                "value": 2
            },
            {
                "date": "2012-01-01T00:00:00",
                "value": 2
            },
            {
                "date": "2011-12-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-11-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-10-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-09-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-08-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-07-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-06-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-05-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-04-01T00:00:00",
                "value": 0
            },
            {
                "date": "2011-03-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-02-01T00:00:00",
                "value": 1
            },
            {
                "date": "2011-01-01T00:00:00",
                "value": 0
            }
        ]

    def __get_ta_3_away_store_counts_weighted(self):
        return [
            {
                "date": "2013-07-01T00:00:00",
                "value": 0.5
            },
            {
                "date": "2013-06-01T00:00:00",
                "value": 0.5
            },
            {
                "date": "2013-05-01T00:00:00",
                "value": 0.5
            },
            {
                "date": "2013-04-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-03-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-02-01T00:00:00",
                "value": 1
            },
            {
                "date": "2013-01-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-12-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-11-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-10-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-09-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-08-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-07-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-06-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-05-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-04-01T00:00:00",
                "value": 1
            },
            {
                "date": "2012-03-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2012-02-01T00:00:00",
                "value": 2
            },
            {
                "date": "2012-01-01T00:00:00",
                "value": 2
            },
            {
                "date": "2011-12-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2011-11-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2011-10-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2011-09-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2011-08-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2011-07-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2011-06-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2011-05-01T00:00:00",
                "value": 1.0
            },
            {
                "date": "2011-04-01T00:00:00",
                "value": 0.0
            },
            {
                "date": "2011-03-01T00:00:00",
                "value": 0.5
            },
            {
                "date": "2011-02-01T00:00:00",
                "value": 0.5
            },
            {
                "date": "2011-01-01T00:00:00",
                "value": 0
            }
        ]
