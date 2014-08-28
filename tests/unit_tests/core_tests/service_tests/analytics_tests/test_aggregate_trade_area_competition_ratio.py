from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competition.aggregate_trade_area_competition_ratio \
    import AggregateTradeAreaCompetitionRatio
import datetime
import unittest
import mox


__author__ = 'vgold'


class MonthlyAverageTradeAreaCompetitionRatioTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(MonthlyAverageTradeAreaCompetitionRatioTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

    def doCleanups(self):

        super(MonthlyAverageTradeAreaCompetitionRatioTests, self).doCleanups()
        dependencies.clear()

    def test_calculate(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        trade_area_id2 = generate_id()
        company_id = generate_id()

        # Make an instance without pesky __init__
        calc_engine = AggregateTradeAreaCompetitionRatio.__new__(AggregateTradeAreaCompetitionRatio)
        calc_engine.date_parser = FastDateParser()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }
        calc_engine.output = {
            "aggregate": "mean"
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Instead of figuring out which day is the last of the month, just subtract one day from the first
        # of the next month
        monthly_competitor_count1 = [
            {
                "date": str(datetime.datetime(2012, 2, 1) - one_day),
                "value": 1
            },
            {
                "date": str(datetime.datetime(2012, 3, 1) - one_day),
                "value": 3
            },
            {
                "date": str(datetime.datetime(2012, 4, 1) - one_day),
                "value": 7
            },
            {
                "date": str(datetime.datetime(2012, 5, 1) - one_day),
                "value": 2
            }
        ]

        monthly_competitor_count2 = [
            {
                "date": str(datetime.datetime(2012, 3, 1) - one_day),
                "value": 7
            },
            {
                "date": str(datetime.datetime(2012, 4, 1) - one_day),
                "value": 7
            },
            {
                "date": str(datetime.datetime(2012, 5, 1) - one_day),
                "value": 20
            },
            {
                "date": str(datetime.datetime(2012, 6, 1) - one_day),
                "value": 6
            }
        ]

        # Set fetched data
        calc_engine.fetched_data = [
            [
                trade_area_id1,
                company_id,
                monthly_competitor_count1
            ],
            [
                trade_area_id2,
                company_id,
                monthly_competitor_count2
            ]
        ]

        # Results of operation
        expected_results = {
            company_id: [
                {
                    "date": datetime.datetime(2012, 6, 1) - one_day,
                    "value": 6
                },
                {
                    "date": datetime.datetime(2012, 5, 1) - one_day,
                    "value": 11
                },
                {
                    "date": datetime.datetime(2012, 4, 1) - one_day,
                    "value": 7
                },
                {
                    "date": datetime.datetime(2012, 3, 1) - one_day,
                    "value": 5
                },
                {
                    "date": datetime.datetime(2012, 2, 1) - one_day,
                    "value": 1
                }
            ]
        }

        # Do maths
        calc_engine._calculate()

        # Steam Punk
        self.assertEqual(calc_engine.results, expected_results)


if __name__ == '__main__':
    unittest.main()