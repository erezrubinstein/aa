from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competition.aggregate_distinct_stores_affected \
    import AggregateDistinctStoresAffected
import unittest
import mox
import datetime
from core.service.svc_analytics.implementation.calc.engines.competition.trade_area_competitive_stores import CompStore
from tests.unit_tests.core_tests.data_stub_helpers import create_mock_taci


__author__ = 'vgold'


class AggregateDistinctStoresAffectedTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(AggregateDistinctStoresAffectedTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.maxDiff = None

    def doCleanups(self):

        super(AggregateDistinctStoresAffectedTests, self).doCleanups()
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

        store_id1 = generate_id()
        store_id2 = generate_id()
        store_id3 = generate_id()
        store_id4 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = AggregateDistinctStoresAffected.__new__(AggregateDistinctStoresAffected)
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
                str(datetime.datetime(2013, 5, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5),
                    CompStore(competitor_id3, store_id3, 1.0)
                ]
            ),
            create_mock_taci(
                company_id,
                trade_area_id2,
                str(datetime.datetime(2013, 4, 1) - one_day),
                [
                    CompStore(competitor_id3, store_id3, 1.0)
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
                str(datetime.datetime(2013, 3, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 1.0)
                ]
            )
        ]

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id],
            "tacis": mock_tacis
        }

        calc_engine.company_date_store_count_dict = {
            company_id: {
                datetime.datetime(2013, 6, 1) - one_day: 58,
                datetime.datetime(2013, 5, 1) - one_day: 46,
                datetime.datetime(2013, 4, 1) - one_day: 77,
                datetime.datetime(2013, 3, 1) - one_day: 35,
                datetime.datetime(2013, 2, 1) - one_day: 10
            }
        }

        calc_engine.child_to_parent_dict = None

        # Do maths
        calc_engine._calculate()

        expected_result = {
            company_id: {
                "counts": {
                    "total": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 3, 1) - one_day,
                            'value': 1
                        }
                    ],
                    "primary": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 3, 1) - one_day,
                            'value': 1
                        }
                    ],
                    "secondary": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 3, 1) - one_day,
                            'value': 0
                        }
                    ],
                    "cluster": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 0
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 0
                        },
                        {
                            'date': datetime.datetime(2013, 3, 1) - one_day,
                            'value': 0
                        }
                    ]
                },
                "percents": {
                    "total": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2 / 58.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 2 / 46.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 2 / 77.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 3, 1) - one_day,
                            'value': 1 / 35.0 * 100.0
                        }
                    ],
                    "primary": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2 / 58.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 2 / 46.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 1 / 77.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 3, 1) - one_day,
                            'value': 1 / 35.0 * 100.0
                        }
                    ],
                    "secondary": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1 / 58.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 2 / 46.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 1 / 77.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 3, 1) - one_day,
                            'value': 0 / 35.0 * 100.0
                        }
                    ],
                    "cluster": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1 / 58.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 0 / 46.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 0 / 77.0 * 100.0
                        },
                        {
                            'date': datetime.datetime(2013, 3, 1) - one_day,
                            'value': 0 / 35.0 * 100.0
                        }
                    ]
                }
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate__parent(self):

        parent_id = generate_id()
        company_id1 = generate_id()
        company_id2 = generate_id()

        trade_area_id1 = generate_id()
        trade_area_id2 = generate_id()
        trade_area_id3 = generate_id()

        store_id01 = generate_id()
        store_id1 = generate_id()
        store_id2 = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = AggregateDistinctStoresAffected.__new__(AggregateDistinctStoresAffected)
        calc_engine.date_parser = FastDateParser()

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [[trade_area_id1], [trade_area_id2], [trade_area_id3]]
        mock_tacis = [
            create_mock_taci(
                company_id1,
                trade_area_id1,
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 0.8),
                    CompStore(company_id1, store_id01, 1.0)
                ]
            ),
            create_mock_taci(
                company_id2,
                trade_area_id2,
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 0.8),
                    CompStore(competitor_id1, store_id1, 0.35)
                ]
            ),
            create_mock_taci(
                company_id2,
                trade_area_id3,
                str(datetime.datetime(2013, 6, 1) - one_day),
                None
            )
        ]

        calc_engine.company_date_store_count_dict = {
            parent_id: {
                datetime.datetime(2013, 6, 1) - one_day: 3
            }
        }

        calc_engine.child_to_parent_dict = {
            company_id1: parent_id,
            company_id2: parent_id
        }

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [parent_id],
            "tacis": mock_tacis
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            parent_id: {
                "counts": {
                    "total": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2
                        }
                    ],
                    "primary": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2
                        }
                    ],
                    "secondary": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1
                        }
                    ],
                    "cluster": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1
                        }
                    ]
                },
                "percents": {
                    "total": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2 / 3.0 * 100.0
                        }
                    ],
                    "primary": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2 / 3.0 * 100.0
                        }
                    ],
                    "secondary": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1 / 3.0 * 100.0
                        }
                    ],
                    "cluster": [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1 / 3.0 * 100.0
                        }
                    ]
                }
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()