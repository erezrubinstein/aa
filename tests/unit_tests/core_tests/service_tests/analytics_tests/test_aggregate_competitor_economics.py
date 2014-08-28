from core.service.svc_analytics.implementation.calc.engines.competitor_summary.aggregate_competitor_economics import AggregateCompetitorEconomics
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from common.utilities.date_utilities import FastDateParser
from core.common.utilities.helpers import generate_id
import unittest
import datetime
import mox


__author__ = 'vgold'


class AggregateCompetitorEconomicsTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AggregateCompetitorEconomicsTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.cfg = "bah"
        self.logger = Dependency("FlaskLogger").value
        self.input = {
            "target_entity_field": "asdf"
        }
        self.output = {
            "key": 42
        }
        self.context_data = {"stuff": True}

    def doCleanups(self):

        super(AggregateCompetitorEconomicsTests, self).doCleanups()
        dependencies.clear()

    def test_calculate__mean(self):

        calc_engine = AggregateCompetitorEconomics.__new__(AggregateCompetitorEconomics)
        calc_engine.date_parser = FastDateParser()

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

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                competitor_id1,
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 600
                    }
                ]
            ],
            [
                competitor_id2,
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 3000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1800
                    }
                ]
            ]
        ]

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

        calc_engine.child_to_parent_dict = None

        # run the calc
        calc_engine._calculate()

        expected_result = {
            str(company_id): {
                "total": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 2000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1200
                    }
                ],
                "primary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 600
                    }
                ],
                "secondary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 3000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1800
                    }
                ],
                "cluster": []
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate__parent_mean(self):

        calc_engine = AggregateCompetitorEconomics.__new__(AggregateCompetitorEconomics)
        calc_engine.date_parser = FastDateParser()

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
                        "value": 1000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 600
                    }
                ]
            ],
            [
                str(competitor_id2),
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 3000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1800
                    }
                ]
            ]
        ]

        # run the calc
        calc_engine._calculate()

        expected_result = {
            str(parent_id): {
                "total": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 2000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1200
                    }
                ],
                "primary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 600
                    }
                ],
                "secondary": [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 3000
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1800
                    }
                ],
                "cluster": []
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()