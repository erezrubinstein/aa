from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competition.distinct_stores_affected_per_competitor \
    import DistinctStoresAffectedPerCompetitor
import unittest
import mox
import datetime
from core.service.svc_analytics.implementation.calc.engines.competition.trade_area_competitive_stores import CompStore
from tests.unit_tests.core_tests.data_stub_helpers import create_mock_taci


__author__ = 'vgold'


class DistinctStoresAffectedPerCompetitorTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(DistinctStoresAffectedPerCompetitorTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.maxDiff = None

    def doCleanups(self):

        super(DistinctStoresAffectedPerCompetitorTests, self).doCleanups()
        dependencies.clear()

    def test_calculate(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        trade_area_id2 = generate_id()
        store_id02 = generate_id()

        company_id = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()
        competitor_id3 = generate_id()
        competitor_id4 = generate_id()

        cci_id0 = generate_id()
        cci_id1 = generate_id()
        cci_id2 = generate_id()
        cci_id3 = generate_id()
        cci_id4 = generate_id()

        store_id1 = generate_id()
        store_id2 = generate_id()
        store_id20 = generate_id()
        store_id3 = generate_id()
        store_id30 = generate_id()
        store_id4 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = DistinctStoresAffectedPerCompetitor.__new__(DistinctStoresAffectedPerCompetitor)
        calc_engine.date_parser = FastDateParser()

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [[trade_area_id1], [trade_area_id2]]

        mock_tacis = [
            create_mock_taci(
                company_id,
                trade_area_id1,
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 0.8),
                    CompStore(company_id, store_id02, 1.0)
                ]
            ),
            create_mock_taci(
                company_id,
                trade_area_id1,
                str(datetime.datetime(2013, 4, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5)
                ]
            ),
            create_mock_taci(
                company_id,
                trade_area_id2,
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 0.8),
                    CompStore(competitor_id4, store_id4, 0.35)
                ]
            ),
            create_mock_taci(
                company_id,
                trade_area_id2,
                str(datetime.datetime(2013, 5, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5),
                    CompStore(competitor_id3, store_id3, 1.0)
                ]
            ),
            create_mock_taci(
                company_id,
                trade_area_id1,
                str(datetime.datetime(2013, 5, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5),
                    CompStore(competitor_id2, store_id2, 0.8)
                ]
            ),
            create_mock_taci(
                company_id,
                trade_area_id2,
                str(datetime.datetime(2013, 4, 1) - one_day),
                [
                    CompStore(competitor_id3, store_id3, 1.0)
                ]
            )
        ]

        calc_engine.company_to_cci_dict = {
            company_id: {
                company_id: cci_id0,
                competitor_id1: cci_id1,
                competitor_id2: cci_id2,
                competitor_id3: cci_id3,
                competitor_id4: cci_id4
            }
        }

        calc_engine.company_date_store_dict = {
            company_id: {
                datetime.datetime(2013, 6, 1) - one_day: 4,
                datetime.datetime(2013, 5, 1) - one_day: 4,
                datetime.datetime(2013, 4, 1) - one_day: 2
            }
        }

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id],
            "tacis": mock_tacis
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            cci_id0: {
                "counts": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1
                    }
                ],
                "percents": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 25.0
                    }
                ]
            },
            cci_id1: {
                "counts": [
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 1
                    }
                ],
                "percents": [
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 50.0
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 50.0
                    }
                ]
            },
            cci_id2: {
                "counts": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 1
                    }
                ],
                "percents": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 50.0
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 25.0
                    }
                ]
            },
            cci_id3: {
                "counts": [
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 1
                    }
                ],
                "percents": [
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 25.0
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 50.0
                    }
                ]
            },
            cci_id4: {
                "counts": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1
                    }
                ],
                "percents": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 25.0
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()