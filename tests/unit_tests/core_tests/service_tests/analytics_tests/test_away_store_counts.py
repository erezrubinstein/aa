from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competition.away_store_counts \
    import AwayStoreCounts
import unittest
import mox
import datetime
from core.service.svc_analytics.implementation.calc.engines.competition.trade_area_competitive_stores import CompStore
from tests.unit_tests.core_tests.data_stub_helpers import create_mock_taci


__author__ = 'vgold'


class AwayStoreCountsTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AwayStoreCountsTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.maxDiff = None

    def doCleanups(self):

        super(AwayStoreCountsTests, self).doCleanups()
        dependencies.clear()

    def test_calculate(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        company_id = generate_id()
        store_id = generate_id()

        # Make an instance without pesky __init__
        calc_engine = AwayStoreCounts.__new__(AwayStoreCounts)
        calc_engine.date_parser = FastDateParser()

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [[trade_area_id1]]
        mock_tacis = [
            create_mock_taci(
                "woot",
                trade_area_id1,
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(company_id, store_id, 0.5),
                    CompStore(company_id, store_id, 0.5)
                ]
            ),
            create_mock_taci(
                "woot",
                trade_area_id1,
                str(datetime.datetime(2013, 5, 1) - one_day),
                [
                    CompStore(company_id, store_id, 0.5),
                    CompStore(company_id, store_id, 0.5)
                ]
            ),
            create_mock_taci(
                "woot",
                trade_area_id1,
                str(datetime.datetime(2013, 4, 1) - one_day),
                [
                    CompStore(company_id, store_id, 0.5)
                ]
            ),
            create_mock_taci(
                "woot",
                trade_area_id1,
                str(datetime.datetime(2013, 3, 1) - one_day),
                [
                    CompStore(company_id, store_id, 0.5)
                ]
            ),
        ]

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id],
            "tacis": mock_tacis
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            trade_area_id1: {
                "raw": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 2,
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 2,
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 1,
                    },
                    {
                        'date': datetime.datetime(2013, 3, 1) - one_day,
                        'value': 1,
                    },
                ],
                "weighted": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1.0,
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 1.0,
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 0.5,
                    },
                    {
                        'date': datetime.datetime(2013, 3, 1) - one_day,
                        'value': 0.5,
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()