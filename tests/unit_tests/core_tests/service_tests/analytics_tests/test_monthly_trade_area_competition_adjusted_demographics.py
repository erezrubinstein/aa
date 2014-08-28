# coding=utf-8
from __future__ import division
import mox
from datetime import datetime
from common.utilities.date_utilities import FastDateParser
from common.utilities.time_series import get_monthly_time_series
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from core.service.svc_analytics.implementation.calc.engines.demographics.monthly_trade_area_competition_adjusted_demographics \
    import MonthlyTradeAreaCompetitionAdjustedDemographics


class MonthlyTradeAreaCompetitionAdjustedDemographicsTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(MonthlyTradeAreaCompetitionAdjustedDemographicsTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # instantiate calc engine without init
        self.engine = MonthlyTradeAreaCompetitionAdjustedDemographics.__new__(
            MonthlyTradeAreaCompetitionAdjustedDemographics)

    def test_calculate(self):
        # Setup test data
        end_date = datetime(2011, 5, 1)
        test_dates = get_monthly_time_series(end=end_date)
        test_demographic_values = [50000, 50000, 50000, 50000, 50000]
        test_weighted_away_store_counts = [1.6, 0, 0.7, 1, 1]

        entity_data = self._get_data_for_entity("some_id", test_dates, [2011], [test_demographic_values],
                                                test_weighted_away_store_counts)

        # Setup and run calculations
        self.engine.fetched_data = [
            entity_data
        ]

        self.engine.date_parser = FastDateParser()
        self.engine._calculate()

        result = self.engine.results["some_id"][0]

        # Validate target year
        self.assertEqual(2011, result["target_year"])

        self.assertListEqual(test_dates, [item["date"] for item in result["series"]])

        # Validate values
        # Manually calculate this because we don't want to naively trust python's division
        expected_values = [19230.77, 50000, 29411.76, 25000]

        actual_values = [item["value"] for item in result["series"]]

        for actual_value, expected_value in zip(actual_values, expected_values):
            if expected_value is None:
                self.assertIsNone(actual_value)
            else:
                # Check within 2 decimal places
                self.assertAlmostEqual(expected_value, actual_value, 2)

    def test_calculate_multiple_target_years(self):
        # Create test dates
        end_date = datetime(2011, 4, 1)
        test_dates = get_monthly_time_series(end=end_date)
        target_years = [2011, 2012, 2013]

        # Create test monthly demographics per target year
        test_demographic_values = [
            [2000, 6000, 12000], #2011
            [4000, 12000, 24000], #2012
            [6000, 18000, 36000]  #2013
        ]

        test_weighted_away_store_counts = [1, 2, 3]

        entity_data = self._get_data_for_entity("some_id", test_dates, target_years, test_demographic_values,
                                                test_weighted_away_store_counts)

        # Setup and run calculations
        self.engine.fetched_data = [
            entity_data
        ]

        self.engine.date_parser = FastDateParser()
        self.engine._calculate()

        # Validate for each target year
        result = self.engine.results["some_id"]

        self.assertEqual(2011, result[0]["target_year"])
        self.assertEqual(2012, result[1]["target_year"])
        self.assertEqual(2013, result[2]["target_year"])

        self.assertListEqual([1000, 2000, 3000], [item["value"] for item in result[0]["series"]])
        self.assertListEqual([2000, 4000, 6000], [item["value"] for item in result[1]["series"]])
        self.assertListEqual([3000, 6000, 9000], [item["value"] for item in result[2]["series"]])


    def test_calculate_multiple_entities(self):
        """
        Test with multiple entities with totally different time series dates and values
        """

        # Setup entity 1
        end_date_1 = datetime(2011, 3, 1)
        test_dates_1 = get_monthly_time_series(end=end_date_1)
        test_demographic_values_1 = [2000, 6000, 3]
        test_weighted_away_store_counts_1 = [1, 2, 2]
        entity_data_1 = self._get_data_for_entity("some_id_1", test_dates_1, [2011], [test_demographic_values_1],
                                                  test_weighted_away_store_counts_1)

        # Setup entity 2
        end_date_2 = datetime(2011, 4, 1)
        test_dates_2 = get_monthly_time_series(end=end_date_2)
        test_demographic_values_2 = [12000, 25000, 24000, 3]
        test_weighted_away_store_counts_2 = [3, 4, 5, 2]
        entity_data_2 = self._get_data_for_entity("some_id_2", test_dates_2, [2012], [test_demographic_values_2],
                                                  test_weighted_away_store_counts_2)

        # Setup and run calculations
        self.engine.fetched_data = [
            entity_data_1,
            entity_data_2
        ]

        self.engine.date_parser = FastDateParser()
        self.engine._calculate()

        # Validate entity 1
        result = self.engine.results["some_id_1"]

        self.assertEqual(2011, result[0]["target_year"])
        self.assertListEqual(test_dates_1, [item["date"] for item in result[0]["series"]])
        self.assertListEqual([1000, 2000, 1], [item["value"] for item in result[0]["series"]])

        # Validate entity 2
        result = self.engine.results["some_id_2"]

        self.assertEqual(2012, result[0]["target_year"])
        self.assertListEqual(test_dates_2, [item["date"] for item in result[0]["series"]])
        self.assertListEqual([3000, 5000, 4000, 1], [item["value"] for item in result[0]["series"]])

    def test_calculate_time_series_alignment(self):
        """
        Tests whether the calculation will work for time series where the dates don't match up
        """
        monthly_demographics = [
            {
                "target_year": 2011,
                "series":
                    [
                        {'date': datetime(2011, 06, 30), 'value': 1000},
                        {'date': datetime(2012, 05, 15), 'value': 5000},
                        {'date': datetime(2010, 04, 04), 'value': 8000},
                    ]
            }
        ]

        away_store_counts = [
            {'date': datetime(2011, 04, 04), 'value': 1.6},
            {'date': datetime(2011, 06, 30), 'value': 0},
            {'date': datetime(2012, 05, 15), 'value': 1}
        ]

        self.engine.fetched_data = [
            [
                "test_entity",
                monthly_demographics,
                away_store_counts
            ]
        ]

        self.engine.date_parser = FastDateParser()
        self.engine._calculate()

        result = self.engine.results["test_entity"][0]["series"]

        expected = [
            {'date': datetime(2012, 5, 15), 'value': 2500},
            {'date': datetime(2011, 6, 30), 'value': 1000},
        ]

        self.assertListEqual(expected, result)


    def _get_data_for_entity(self, entity_id, dates, target_years, yearly_demographic_values,
                             weighted_away_store_counts):
        monthly_demographics = []

        for target_year, demographic_values in zip(target_years, yearly_demographic_values):
            monthly_demographics.append(
                {
                    "target_year": target_year,
                    "series": [{'date': d, 'value': v} for d, v in zip(dates, demographic_values)]
                }
            )

        monthly_weighted_away_store_counts = [{'date': d, 'value': v} for d, v in
                                              zip(dates, weighted_away_store_counts)]

        return [
            entity_id,
            monthly_demographics,
            monthly_weighted_away_store_counts
        ]





