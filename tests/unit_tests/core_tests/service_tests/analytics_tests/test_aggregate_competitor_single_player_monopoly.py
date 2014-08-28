from common.utilities.date_utilities import FastDateParser
from core.service.svc_analytics.implementation.calc.engines.competitor_summary.aggregate_competitor_single_player_monopolies \
    import AggregateCompetitorSinglePlayerMonopolies
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
import datetime
import unittest
import mox


__author__ = 'clairseager'


class AggregateCompetitorSinglePlayerMonopoliesTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(AggregateCompetitorSinglePlayerMonopoliesTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

    def doCleanups(self):

        super(AggregateCompetitorSinglePlayerMonopoliesTests, self).doCleanups()
        dependencies.clear()

    def test_calculate__mean(self):

        calc_engine = AggregateCompetitorSinglePlayerMonopolies.__new__(AggregateCompetitorSinglePlayerMonopolies)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        # Make some object ids to be real
        company_id = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }
        calc_engine.output = {
            "aggregate": "mean"
        }

        calc_engine.company_pair_dict = {
            str(company_id): {
                str(competitor_id1): {
                    "_id": str(competitor_id1),
                    "name": "Competitor 1",
                    "weight": 1.0
                },
                str(competitor_id2): {
                    "_id": str(competitor_id2),
                    "name": "Competitor 2",
                    "weight": 0.5
                }
            }
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                competitor_id1,
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.95
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.8
                    }
                ],
            ],
            [
                competitor_id2,
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.35
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.2
                    }
                ],
            ]
        ]

        # run the calc
        calc_engine._calculate()

        # obviously not the real thing, skipping repetitive intermediate data points
        expected_results = {
            str(company_id): {
                "total": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": (0.95 + 0.35) / 2
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": (0.8 + 0.2) / 2
                    }
                ],
                "primary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.95
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.8
                    }
                ],
                "secondary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.35
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.2
                    }
                ],
                "cluster": []
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_results)

    def test_calculate__max(self):

        calc_engine = AggregateCompetitorSinglePlayerMonopolies.__new__(AggregateCompetitorSinglePlayerMonopolies)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        # Make some object ids to be real
        company_id = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }
        calc_engine.output = {
            "aggregate": "max"
        }

        calc_engine.company_pair_dict = {
            str(company_id): {
                str(competitor_id1): {
                    "_id": str(competitor_id1),
                    "name": "Competitor 1",
                    "weight": 1.0
                },
                str(competitor_id2): {
                    "_id": str(competitor_id2),
                    "name": "Competitor 2",
                    "weight": 0.5
                }
            }
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                competitor_id1,
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.95
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.8
                    }
                ],
            ],
            [
                competitor_id2,
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.35
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.2
                    }
                ],
            ]
        ]

        # run the calc
        calc_engine._calculate()

        # obviously not the real thing, skipping repetitive intermediate data points
        expected_results = {
            str(company_id): {
                "total": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "company_id": str(competitor_id1),
                        "company_name": "Competitor 1",
                        "value": 0.95
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "company_id": str(competitor_id1),
                        "company_name": "Competitor 1",
                        "value": 0.8
                    }
                ],
                "primary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "company_id": str(competitor_id1),
                        "company_name": "Competitor 1",
                        "value": 0.95
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "company_id": str(competitor_id1),
                        "company_name": "Competitor 1",
                        "value": 0.8
                    }
                ],
                "secondary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "company_id": str(competitor_id2),
                        "company_name": "Competitor 2",
                        "value": 0.35
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "company_id": str(competitor_id2),
                        "company_name": "Competitor 2",
                        "value": 0.2
                    }
                ],
                "cluster": []
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_results)

    def test_calculate_parent__mean(self):

        calc_engine = AggregateCompetitorSinglePlayerMonopolies.__new__(AggregateCompetitorSinglePlayerMonopolies)
        calc_engine.date_parser = FastDateParser()

        # Make some object ids to be real
        parent_id = generate_id()
        banner_id1 = generate_id()
        banner_id2 = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [str(parent_id)]
        }
        calc_engine.output = {
            "aggregate": "mean"
        }

        calc_engine.company_pair_dict = {
            str(banner_id1): {
                str(competitor_id1): {
                    "_id": str(competitor_id1),
                    "name": "Competitor 1",
                    "weight": 1.0
                }
            },
            str(banner_id2): {
                str(competitor_id2): {
                    "_id": str(competitor_id2),
                    "name": "Competitor 2",
                    "weight": 0.5
                }
            }
        }

        calc_engine.child_to_parent_dict = {
            str(banner_id1): str(parent_id),
            str(banner_id2): str(parent_id)
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                str(competitor_id1),
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.95
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.8
                    }
                ],
            ],
            [
                str(competitor_id2),
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.35
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.2
                    }
                ],
            ]
        ]

        # run the calc
        calc_engine._calculate()

        # obviously not the real thing, skipping repetitive intermediate data points
        expected_results = {
            str(parent_id): {
                "total": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": (0.95 + 0.35) / 2
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": (0.8 + 0.2) / 2
                    }
                ],
                "primary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.95
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.8
                    }
                ],
                "secondary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 0.35
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 0.2
                    }
                ],
                "cluster": []
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_results)


if __name__ == '__main__':
    unittest.main()
