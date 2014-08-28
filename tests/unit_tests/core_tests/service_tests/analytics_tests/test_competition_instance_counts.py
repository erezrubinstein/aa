from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competition.competition_instance_counts \
    import CompetitionInstanceCounts
import unittest
import datetime
import mox


__author__ = 'vgold'


class CompetitionInstanceCountsTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(CompetitionInstanceCountsTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.maxDiff = None

    def doCleanups(self):

        super(CompetitionInstanceCountsTests, self).doCleanups()
        dependencies.clear()

    def test_calculate__sum(self):

        company_id = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()
        competitor_id3 = generate_id()
        competitor_id4 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = CompetitionInstanceCounts.__new__(CompetitionInstanceCounts)
        calc_engine.date_parser = FastDateParser()
        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [
            [
                100,
                company_id,
                competitor_id4,
                0.5,
                [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1
                    }
                ],
                "Competitor 4"
            ],
            [
                110,
                company_id,
                company_id,
                1.0,
                [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1
                    }
                ],
                "Company"
            ],
            [
                120,
                company_id,
                competitor_id2,
                0.8,
                [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        "value": 2
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1
                    }
                ],
                "Competitor 2"
            ],
            [
                130,
                company_id,
                competitor_id3,
                0.5,
                [
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        "value": 1
                    }
                ],
                "Competitor 3"
            ],
            [
                140,
                company_id,
                competitor_id1,
                0.8,
                [
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        "value": 2
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        "value": 1
                    }
                ],
                "Competitor 1"
            ]
        ]

        calc_engine.competitor_dict = {
            company_id: "company",
            competitor_id1: "competitor1",
            competitor_id2: "competitor2",
            competitor_id3: "competitor3",
            competitor_id4: "competitor4"
        }

        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "aggregate": "sum"
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            str(company_id): {
                'raw': {
                    'total': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 4
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 4
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 2
                        }
                    ],
                    'primary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 3
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 1
                        }
                    ],
                    'secondary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 1
                        }
                    ],
                    'cluster': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1
                        }
                    ]
                },
                'weighted': {
                    'total': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 0.5 + (2*0.8) + 1
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': (3*0.8) + 0.5
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 0.8 + 0.5
                        }
                    ],
                    'primary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2*0.8
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': (3*0.8)
                        },
                        {
                            'date': datetime.datetime(2013, 4, 1) - one_day,
                            'value': 0.8
                        }
                    ],
                    'secondary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 0.5
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
                    'cluster': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1.0
                        }
                    ]
                }
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate__min(self):

        company_id = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()
        competitor_id3 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = CompetitionInstanceCounts.__new__(CompetitionInstanceCounts)
        calc_engine.date_parser = FastDateParser()
        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [
            [
                100,
                company_id,
                competitor_id1,
                0.5,
                [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1
                    }
                ],
                "Competitor 1"
            ],
            [
                110,
                company_id,
                company_id,
                1.0,
                [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1
                    }
                ],
                "Company"
            ],
            [
                120,
                company_id,
                competitor_id2,
                0.8,
                [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        "value": 2
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1
                    }
                ],
                "Competitor 2"
            ],
            [
                130,
                company_id,
                competitor_id3,
                0.5,
                [
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1
                    }
                ],
                "Competitor 3"
            ]
        ]

        calc_engine.competitor_dict = {
            company_id: "company",
            competitor_id1: "competitor1",
            competitor_id2: "competitor2",
            competitor_id3: "competitor3"
        }

        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "aggregate": "min"
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            str(company_id): {
                'raw': {
                    'total': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'company_name': 'Competitor 1',
                            'company_id': str(competitor_id1),
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'company_name': 'Competitor 2',
                            'company_id': str(competitor_id2),
                            'value': 1
                        }
                    ],
                    'primary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'company_name': 'Competitor 2',
                            'company_id': str(competitor_id2),
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'company_name': 'Competitor 2',
                            'company_id': str(competitor_id2),
                            'value': 1
                        }
                    ],
                    'secondary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'company_name': 'Competitor 1',
                            'company_id': str(competitor_id1),
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'company_name': 'Competitor 3',
                            'company_id': str(competitor_id3),
                            'value': 1
                        }
                    ],
                    'cluster': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'company_name': 'Company',
                            'company_id': str(company_id),
                            'value': 1
                        }
                    ]
                },
                'weighted': {
                    'total': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'company_name': 'Competitor 1',
                            'company_id': str(competitor_id1),
                            'value': 0.5
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'company_name': 'Competitor 3',
                            'company_id': str(competitor_id3),
                            'value': 0.5
                        }
                    ],
                    'primary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'company_name': 'Competitor 2',
                            'company_id': str(competitor_id2),
                            'value': 1.6
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'company_name': 'Competitor 2',
                            'company_id': str(competitor_id2),
                            'value': 0.8
                        }
                    ],
                    'secondary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'company_name': 'Competitor 1',
                            'company_id': str(competitor_id1),
                            'value': 0.5
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'company_name': 'Competitor 3',
                            'company_id': str(competitor_id3),
                            'value': 0.5
                        }
                    ],
                    'cluster': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'company_name': 'Company',
                            'company_id': str(company_id),
                            'value': 1.0
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

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = CompetitionInstanceCounts.__new__(CompetitionInstanceCounts)
        calc_engine.date_parser = FastDateParser()
        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [parent_id]
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [
            [
                100,
                company_id1,
                competitor_id1,
                0.5,
                [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        "value": 1
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        "value": 1
                    }
                ],
                "Competitor 1"
            ],
            [
                200,
                company_id2,
                competitor_id2,
                0.8,
                [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        "value": 2
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        "value": 2
                    }
                ],
                "Competitor 2"
            ]
        ]

        calc_engine.child_to_parent_dict = {
            str(company_id1): str(parent_id),
            str(company_id2): str(parent_id)
        }

        calc_engine.output = {
            "aggregate": "sum"
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            str(parent_id): {
                'raw': {
                    'total': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 3
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 3
                        }
                    ],
                    'primary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 2
                        }
                    ],
                    'secondary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 1
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 1
                        }
                    ],
                    'cluster': []
                },
                'weighted': {
                    'total': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 0.5 + (2*0.8)
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 0.5 + (2*0.8)
                        }
                    ],
                    'primary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 2*0.8
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 2*0.8
                        }
                    ],
                    'secondary': [
                        {
                            'date': datetime.datetime(2013, 6, 1) - one_day,
                            'value': 0.5
                        },
                        {
                            'date': datetime.datetime(2013, 5, 1) - one_day,
                            'value': 0.5
                        }
                    ],
                    'cluster': []
                }
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()
