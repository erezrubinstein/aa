import json
from bson.objectid import ObjectId
from common.utilities.date_utilities import parse_date, END_OF_WORLD, LAST_ANALYTICS_DATE
from common.utilities.time_series import get_monthly_time_series
from core.service.svc_analytics.implementation.calc.engines.monopolies.single_player_monopolies import SinglePlayerMonopolies
from common.helpers.common_dependency_helper import register_common_mox_dependencies
import datetime
import unittest
import mox


__author__ = 'clairseager'


class SinglePlayerMonopoliesTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(SinglePlayerMonopoliesTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

    def test_calculate(self):

        calc_engine = SinglePlayerMonopolies.__new__(SinglePlayerMonopolies)
        calc_engine.child_to_parent_dict = None

        calc_engine.run_params = {
            "target_entity_ids": ["company1", "company2"]
        }

        calc_engine.fetched_data = [
            # trade area 1 - a monopoly the whole time
            [
                "asdf",
                "company1",
                [
                    {
                        "start_date": "1900-01-01T00:00:00",
                        "end_date": "2013-04-01T00:00:00",
                        "monopoly_type": "SinglePlayerMonopoly"
                    }
                ],
                [None, "2013-05-01T00:00:00"]
            ],
            # trade area 2 - monopoly gap from 2012-01 to 2013-01
            [
                "qwer",
                "company1",
                [
                    {
                        "start_date": "1900-01-01T00:00:00",
                        "end_date": "2012-01-01T00:00:00",
                        "monopoly_type": "SinglePlayerMonopoly"
                    },
                    {
                        "start_date": "2013-01-01T00:00:00",
                        "end_date": END_OF_WORLD.isoformat(),
                        "monopoly_type": "SinglePlayerMonopoly"
                    }
                ],
                [None, None]
            ],
            # trade area 1 - never a monopoly
            ["zxcv", "company2", None, None]
        ]

        calc_engine.date_parser = self.mox.CreateMockAnything()
        calc_engine.date_parser.parse_date = parse_date

        # run the calc
        calc_engine._calculate()

        expected_results = {
            'company1': [],
            'company2': []
        }

        dates = get_monthly_time_series(sort_descending=True, end=LAST_ANALYTICS_DATE)

        for date in dates:

            if date < datetime.datetime(2012, 1, 1):
                value = 100.0
            elif datetime.datetime(2012, 1, 1) <= date < datetime.datetime(2013, 1, 1):
                value = 50.0
            elif datetime.datetime(2013, 1, 1) <= date < datetime.datetime(2013, 4, 1):
                value = 100.0
            elif datetime.datetime(2013, 4, 1) <= date < datetime.datetime(2013, 5, 1):
                value = 50.0
            else:
                value = 100.0

            expected_results['company1'].append({
                "date": date,
                "value": value
            })

            expected_results['company2'].append({
                "date": date,
                "value": 0.0
            })
        self.maxDiff = None
        self.assertDictEqual(expected_results, calc_engine.results)

    def test_calculate_parent(self):

        calc_engine = SinglePlayerMonopolies.__new__(SinglePlayerMonopolies)

        parent_id = ObjectId()
        banner_id1 = ObjectId()
        banner_id2 = ObjectId()

        calc_engine.run_params = {
            "target_entity_ids": [str(parent_id)]
        }

        calc_engine.child_to_parent_dict = {
            str(banner_id1): str(parent_id),
            str(banner_id2): str(parent_id)
        }

        calc_engine.fetched_data = [
            # trade area 1 - a monopoly the whole time
            [
                "asdf",
                str(banner_id1),
                [
                    {
                        "start_date": "1900-01-01T00:00:00",
                        "end_date": "2013-04-01T00:00:00",
                        "monopoly_type": "SinglePlayerMonopoly"
                    }
                ],
                [None, "2013-04-01T00:00:00"]
            ],
            # trade area 2 - monopoly gap from 2012-01 to 2013-01
            [
                "qwer",
                str(banner_id2),
                [
                    {
                        "start_date": "1900-01-01T00:00:00",
                        "end_date": "2012-01-01T00:00:00",
                        "monopoly_type": "SinglePlayerMonopoly"
                    },
                    {
                        "start_date": "2013-01-01T00:00:00",
                        "end_date": "2013-04-01T00:00:00",
                        "monopoly_type": "SinglePlayerMonopoly"
                    }
                ],
                [None, "2013-04-01T00:00:00"]
            ],
            # trade area 1 - never a monopoly
            ["zxcv", str(banner_id2), None, None]
        ]

        calc_engine.date_parser = self.mox.CreateMockAnything()
        calc_engine.date_parser.parse_date = parse_date

        # run the calc
        calc_engine._calculate()

        expected_results = {
            str(parent_id): []
        }

        dates = get_monthly_time_series(sort_descending=True, end=LAST_ANALYTICS_DATE)

        for date in dates:

            if date < datetime.datetime(2012, 01, 01) \
                    or (datetime.datetime(2013, 04, 01) > date >= datetime.datetime(2013, 01, 01)):
                value = 2 / 3.0 * 100
            elif date < datetime.datetime(2013, 04, 01):
                value = 1 / 3.0 * 100
            else:
                value = 0.0

            expected_results[str(parent_id)].append({
                "date": date,
                "value": value
            })

        self.maxDiff = None
        self.assertDictEqual(expected_results, calc_engine.results)


if __name__ == '__main__':
    unittest.main()
