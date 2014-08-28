import pprint
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competition.company_competition_ratio \
    import CompanyCompetitionRatio
import unittest
import datetime
import mox


__author__ = 'vgold'


class CompanyCompetitionRatioTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(CompanyCompetitionRatioTests, self).setUp()

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

        super(CompanyCompetitionRatioTests, self).doCleanups()
        dependencies.clear()

    def test_calculate(self):

        calc_engine = CompanyCompetitionRatio.__new__(CompanyCompetitionRatio)
        calc_engine.date_parser = FastDateParser()

        company_id = generate_id()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                company_id,
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 600
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 700
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 400
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 200
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 150
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 100
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 50
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 550.4
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 384.6
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 428.2
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 200.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 87.5
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 46.5
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 5.0
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 3.7
                            }
                        ]
                    }
                },
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1200
                    },
                    {
                        "date": datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1000
                    }
                ]
            ]
        ]

        calc_engine.child_to_parent_dict = None

        # run the calc
        calc_engine._calculate()

        expected_result = {
            str(company_id): {
                "raw": {
                    "total": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 1000 / 1200.0
                        },
                        {
                            "date": datetime.datetime(2013, 5, 1) - one_day,
                            "value": 600 / 1000.0
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 700 / 1200.0
                        },
                        {
                            "date": datetime.datetime(2013, 5, 1) - one_day,
                            "value": 400 / 1000.0
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 200 / 1200.0
                        },
                        {
                            "date": datetime.datetime(2013, 5, 1) - one_day,
                            "value": 150 / 1000.0
                        }
                    ],
                    "cluster": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 100 / 1200.0
                        },
                        {
                            "date": datetime.datetime(2013, 5, 1) - one_day,
                            "value": 50 / 1000.0
                        }
                    ]
                },
                "weighted": {
                    "total": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 550.4 / 1200.0
                        },
                        {
                            "date": datetime.datetime(2013, 5, 1) - one_day,
                            "value": 384.6 / 1000.0
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 428.2 / 1200.0
                        },
                        {
                            "date": datetime.datetime(2013, 5, 1) - one_day,
                            "value": 200.0 / 1000.0
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 87.5 / 1200.0
                        },
                        {
                            "date": datetime.datetime(2013, 5, 1) - one_day,
                            "value": 46.5 / 1000.0
                        }
                    ],
                    "cluster": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 5.0 / 1200.0
                        },
                        {
                            "date": datetime.datetime(2013, 5, 1) - one_day,
                            "value": 3.7 / 1000.0
                        }
                    ]
                }
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate__parent(self):

        calc_engine = CompanyCompetitionRatio.__new__(CompanyCompetitionRatio)
        calc_engine.date_parser = FastDateParser()

        parent_id = generate_id()

        company_id1 = generate_id()
        company_id2 = generate_id()

        competitor_id1 = generate_id()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [parent_id]
        }

        calc_engine.child_to_parent_dict = {
            str(company_id1): str(parent_id),
            str(company_id2): str(parent_id)
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                company_id1,
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1000
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 700
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 200
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 100
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 550.4
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 428.2
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 87.5
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 5.0
                            }
                        ]
                    }
                },
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1200
                    }
                ]
            ],
            [
                company_id2,
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1000
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 700
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 200
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 100
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 550.4
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 428.2
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 87.5
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 5.0
                            }
                        ]
                    }
                },
                [
                    {
                        "date": datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1200
                    }
                ]
            ]
        ]

        # run the calc
        calc_engine._calculate()

        expected_result = {
            str(parent_id): {
                "raw": {
                    "total": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 1000 / 2400.0 * 2
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 700 / 2400.0 * 2
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 200 / 2400.0 * 2
                        }
                    ],
                    "cluster": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 100 / 2400.0 * 2
                        }
                    ]
                },
                "weighted": {
                    "total": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 550.4 / 2400.0 * 2
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 428.2 / 2400.0 * 2
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 87.5 / 2400.0 * 2
                        }
                    ],
                    "cluster": [
                        {
                            "date": datetime.datetime(2013, 6, 1) - one_day,
                            "value": 5.0 / 2400.0 * 2
                        }
                    ]
                }
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()