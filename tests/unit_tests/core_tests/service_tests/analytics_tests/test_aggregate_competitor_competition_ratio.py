from common.utilities.date_utilities import FastDateParser
from core.service.svc_analytics.implementation.calc.engines.competitor_summary.aggregate_competitor_competition_ratio \
    import AggregateCompetitorCompetitionRatio
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
import datetime
import unittest
import mox


__author__ = 'vgold'


class AggregateCompetitorCompetitionRatioTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AggregateCompetitorCompetitionRatioTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

    def doCleanups(self):

        super(AggregateCompetitorCompetitionRatioTests, self).doCleanups()
        dependencies.clear()

    def test_calculate__mean(self):

        # Make an instance without pesky __init__
        calc_engine = AggregateCompetitorCompetitionRatio.__new__(AggregateCompetitorCompetitionRatio)
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
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 2.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 2.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 3.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 3.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.0
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 5.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 5.0
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 2.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 2.1
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 3.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 3.1
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.1
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 5.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 5.1
                            }
                        ]
                    }
                }
            ],
            [
                competitor_id2,
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 6.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 6.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 8.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 8.0
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 10.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 10.0
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.1
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 6.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 6.1
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 8.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 8.1
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 10.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 10.1
                            }
                        ]
                    }
                }
            ]
        ]

        # Do maths
        calc_engine._calculate()

        # Results of operation
        expected_results = {
            str(company_id): {
                "raw": {
                    "total": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 3.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 3.0
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 2.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 2.0
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 4.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 4.0
                        }
                    ],
                    "cluster": []
                },
                "weighted": {
                    "total": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 3.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 3.1
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 2.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 2.1
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 4.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 4.1
                        }
                    ],
                    "cluster": []
                }
            }
        }

        # Steam Punk
        self.assertEqual(calc_engine.results, expected_results)

    def test_calculate__min(self):

        # Make some object ids to be real
        company_id = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = AggregateCompetitorCompetitionRatio.__new__(AggregateCompetitorCompetitionRatio)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }
        calc_engine.output = {
            "aggregate": "min"
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
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 2.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 2.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 3.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 3.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.0
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 5.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 5.0
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 2.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 2.1
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 3.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 3.1
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.1
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 5.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 5.1
                            }
                        ]
                    }
                }
            ],
            [
                competitor_id2,
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 6.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 6.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 8.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 8.0
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 10.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 10.0
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.1
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 6.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 6.1
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 8.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 8.1
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 10.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 10.1
                            }
                        ]
                    }
                }
            ]
        ]

        # Do maths
        calc_engine._calculate()

        # Results of operation
        expected_results = {
            str(company_id): {
                "raw": {
                    "total": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "company_id": str(competitor_id1),
                            "company_name": "Competitor 1",
                            "value": 2.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "company_id": str(competitor_id1),
                            "company_name": "Competitor 1",
                            "value": 2.0
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "company_id": str(competitor_id1),
                            "company_name": "Competitor 1",
                            "value": 2.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "company_id": str(competitor_id1),
                            "company_name": "Competitor 1",
                            "value": 2.0
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "company_id": str(competitor_id2),
                            "company_name": "Competitor 2",
                            "value": 4.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "company_id": str(competitor_id2),
                            "company_name": "Competitor 2",
                            "value": 4.0
                        }
                    ],
                    "cluster": []
                },
                "weighted": {
                    "total": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "company_id": str(competitor_id1),
                            "company_name": "Competitor 1",
                            "value": 2.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "company_id": str(competitor_id1),
                            "company_name": "Competitor 1",
                            "value": 2.1
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "company_id": str(competitor_id1),
                            "company_name": "Competitor 1",
                            "value": 2.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "company_id": str(competitor_id1),
                            "company_name": "Competitor 1",
                            "value": 2.1
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "company_id": str(competitor_id2),
                            "company_name": "Competitor 2",
                            "value": 4.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "company_id": str(competitor_id2),
                            "company_name": "Competitor 2",
                            "value": 4.1
                        }
                    ],
                    "cluster": []
                }
            }
        }

        # Steam Punk
        self.assertEqual(calc_engine.results, expected_results)

    def test_calculate_parent__mean(self):

        # Make an instance without pesky __init__
        calc_engine = AggregateCompetitorCompetitionRatio.__new__(AggregateCompetitorCompetitionRatio)
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
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 2.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 2.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 3.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 3.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.0
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 5.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 5.0
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 2.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 2.1
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 3.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 3.1
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.1
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 5.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 5.1
                            }
                        ]
                    }
                }
            ],
            [
                str(competitor_id2),
                {
                    "raw": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.0
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 6.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 6.0
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 8.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 8.0
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 10.0
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 10.0
                            }
                        ]
                    },
                    "weighted": {
                        "total": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 4.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 4.1
                            }
                        ],
                        "primary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 6.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 6.1
                            }
                        ],
                        "secondary": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 8.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 8.1
                            }
                        ],
                        "cluster": [
                            {
                                "date": datetime.datetime(2012, 6, 1) - one_day,
                                "value": 10.1
                            },
                            {
                                "date": datetime.datetime(2012, 5, 1) - one_day,
                                "value": 10.1
                            }
                        ]
                    }
                }
            ]
        ]

        # Do maths
        calc_engine._calculate()

        # Results of operation
        expected_results = {
            str(parent_id): {
                "raw": {
                    "total": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 3.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 3.0
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 2.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 2.0
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 4.0
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 4.0
                        }
                    ],
                    "cluster": []
                },
                "weighted": {
                    "total": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 3.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 3.1
                        }
                    ],
                    "primary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 2.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 2.1
                        }
                    ],
                    "secondary": [
                        {
                            "date": datetime.datetime(2012, 6, 1) - one_day,
                            "value": 4.1
                        },
                        {
                            "date": datetime.datetime(2012, 5, 1) - one_day,
                            "value": 4.1
                        }
                    ],
                    "cluster": []
                }
            }
        }

        # Steam Punk
        self.assertEqual(calc_engine.results, expected_results)



if __name__ == '__main__':
    unittest.main()