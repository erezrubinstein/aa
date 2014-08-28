from core.service.svc_analytics.implementation.calc.engines.competition.aggregate_competition_instances import AggregateCompetitionInstances
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from common.utilities.date_utilities import FastDateParser
from core.common.utilities.helpers import generate_id
import unittest
import datetime
import pprint
import mox


__author__ = 'vgold'


class AggregateCompetitionInstancesTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AggregateCompetitionInstancesTests, self).setUp()

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

        super(AggregateCompetitionInstancesTests, self).doCleanups()
        dependencies.clear()

    def test_calculate(self):

        calc_engine = AggregateCompetitionInstances.__new__(AggregateCompetitionInstances)
        calc_engine.date_parser = FastDateParser()

        company_id = generate_id()
        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        calc_engine.output = {
            "aggregate": "mean"
        }

        calc_engine.run_params = {
            "target_entity_ids": [company_id],
        }

        calc_engine.child_to_parent_dict = None

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                generate_id(),
                company_id,
                competitor_id1,
                1.0,
                {
                    "counts": {
                        "raw": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.0
                            }
                        ]
                    },
                    "percents": {
                        "raw": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 25.0
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 20.0
                            }
                        ]
                    }
                }
            ],
            [
                generate_id(),
                company_id,
                competitor_id2,
                0.5,
                {
                    "counts": {
                        "raw": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 3
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.5
                            }
                        ]
                    },
                    "percents": {
                        "raw": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 18.0
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 10.0
                            }
                        ]
                    }
                }
            ]
        ]

        calc_engine._calculate()

        expected_result = {
            str(company_id): {
                "counts": {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 2.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 3.0
                            }
                        ],
                        "cluster": []
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.25
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.5
                            }
                        ],
                        "cluster": []
                    }
                },
                "percents": {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 21.5
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 25.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 18.0
                            }
                        ],
                        "cluster": []
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 15.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 20.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 10.0
                            }
                        ],
                        "cluster": []
                    }
                }
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate__parent(self):

        calc_engine = AggregateCompetitionInstances.__new__(AggregateCompetitionInstances)
        calc_engine.date_parser = FastDateParser()

        parent_id = generate_id()
        banner_id = generate_id()
        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        calc_engine.output = {
            "aggregate": "mean"
        }

        calc_engine.run_params = {
            "target_entity_ids": [parent_id],
        }

        calc_engine.child_to_parent_dict = {
            str(banner_id): str(parent_id)
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                generate_id(),
                banner_id,
                competitor_id1,
                1.0,
                {
                    "counts": {
                        "raw": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.0
                            }
                        ]
                    },
                    "percents": {
                        "raw": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 25.0
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 20.0
                            }
                        ]
                    }
                }
            ],
            [
                generate_id(),
                banner_id,
                competitor_id2,
                0.5,
                {
                    "counts": {
                        "raw": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 3
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.5
                            }
                        ]
                    },
                    "percents": {
                        "raw": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 18.0
                            }
                        ],
                        "weighted": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 10.0
                            }
                        ]
                    }
                }
            ]
        ]

        calc_engine._calculate()

        expected_result = {
            str(parent_id): {
                "counts": {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 2.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 3.0
                            }
                        ],
                        "cluster": []
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.25
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1.5
                            }
                        ],
                        "cluster": []
                    }
                },
                "percents": {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 21.5
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 25.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 18.0
                            }
                        ],
                        "cluster": []
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 15.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 20.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 10.0
                            }
                        ],
                        "cluster": []
                    }
                }
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()