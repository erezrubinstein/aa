from __future__ import division
from common.utilities.date_utilities import FastDateParser
from core.service.svc_analytics.implementation.calc.engines.competition.average_competition_weight \
    import AverageCompetitionWeight
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from core.common.utilities.helpers import generate_id
import datetime
import mox
from core.service.svc_analytics.implementation.calc.engines.competition.trade_area_competitive_stores import CompStore
from tests.unit_tests.core_tests.data_stub_helpers import create_mock_taci


class AverageCompetitionWeightTests(mox.MoxTestBase):

    def setUp(self):

        super(AverageCompetitionWeightTests, self).setUp()
        register_common_mox_dependencies(self.mox)

    def test_calculate(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        store_id01 = generate_id()
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
        calc_engine = AverageCompetitionWeight.__new__(AverageCompetitionWeight)
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

        calc_engine.child_to_parent_dict = None

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id],
            "tacis": mock_tacis
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            company_id: {
                "total": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': (0.8 + 0.8 + 1.0 + 0.35) / 4
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': (0.5 + 0.5 + 1.0 + 0.8) / 4
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': (1.0 + 0.5) / 2
                    }
                ],
                "primary": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 0.8
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': (1.0 + 0.8) / 2
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 1.0
                    }
                ],
                "secondary": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 0.35
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 0.5
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 0.5
                    }
                ],
                "cluster": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1.0
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': None
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': None
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate__parent(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        store_id01 = generate_id()
        trade_area_id2 = generate_id()

        parent_id = generate_id()
        company_id1 = generate_id()
        company_id2 = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        store_id1 = generate_id()
        store_id2 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = AverageCompetitionWeight.__new__(AverageCompetitionWeight)
        calc_engine.date_parser = FastDateParser()

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [[trade_area_id1], [trade_area_id2]]
        mock_tacis = [
            create_mock_taci(
                company_id1,
                trade_area_id1,
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.8),
                    CompStore(company_id1, store_id01, 1.0)
                ]
            ),
            create_mock_taci(
                company_id2,
                trade_area_id2,
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(company_id1, store_id01, 0.8),
                    CompStore(competitor_id2, store_id2, 0.35)
                ]
            )
        ]

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [parent_id],
            "tacis": mock_tacis,
            "child_to_parent_dict": {
                company_id1: parent_id,
                company_id2: parent_id
            }
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            parent_id: {
                "total": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': (0.8 + 0.8 + 1.0 + 0.35) / 4
                    }
                ],
                "primary": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 0.8
                    }
                ],
                "secondary": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 0.35
                    }
                ],
                "cluster": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1.0
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)




