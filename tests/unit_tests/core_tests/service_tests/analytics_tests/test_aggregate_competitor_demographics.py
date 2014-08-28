from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competitor_summary.aggregate_competitor_demographics \
    import AggregateCompetitorDemographics
import unittest
import datetime
import mox


__author__ = 'vgold'


class AggregateCompetitorDemographicsTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AggregateCompetitorDemographicsTests, self).setUp()

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

        super(AggregateCompetitorDemographicsTests, self).doCleanups()
        dependencies.clear()

    def test_calculate__sum(self):

        calc_engine = AggregateCompetitorDemographics.__new__(AggregateCompetitorDemographics)
        calc_engine.date_parser = FastDateParser()

        company_id = generate_id()
        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }

        calc_engine.output = {
            "aggregate": "sum"
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                competitor_id1,
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 600
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 6000
                            }
                        ]
                    }
                ]
            ],
            [
                competitor_id2,
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 3000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 1800
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 30000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 18000
                            }
                        ]
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
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 4000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 2400
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 40000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 24000
                            }
                        ]
                    }
                ],
                "primary": [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 600
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 6000
                            }
                        ]
                    }
                ],
                "secondary": [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 3000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 1800
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 30000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 18000
                            }
                        ]
                    }
                ],
                "cluster": [
                    {
                        "target_year": 2011,
                        "series": []
                    },
                    {
                        "target_year": 2016,
                        "series": []
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate__min(self):

        calc_engine = AggregateCompetitorDemographics.__new__(AggregateCompetitorDemographics)
        calc_engine.date_parser = FastDateParser()

        company_id = generate_id()
        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }

        calc_engine.output = {
            "aggregate": "min"
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        calc_engine.fetched_data = [
            [
                competitor_id1,
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": competitor_id1,
                                "company_name": "Competitor 1",
                                "value": 1000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": competitor_id1,
                                "company_name": "Competitor 1",
                                "value": 600
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": competitor_id1,
                                "company_name": "Competitor 1",
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": competitor_id1,
                                "company_name": "Competitor 1",
                                "value": 6000
                            }
                        ]
                    }
                ]
            ],
            [
                competitor_id2,
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": competitor_id2,
                                "company_name": "Competitor 2",
                                "value": 3000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": competitor_id2,
                                "company_name": "Competitor 2",
                                "value": 1800
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": competitor_id2,
                                "company_name": "Competitor 2",
                                "value": 30000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": competitor_id2,
                                "company_name": "Competitor 2",
                                "value": 18000
                            }
                        ]
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
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": str(competitor_id1),
                                "company_name": "Competitor 1",
                                "value": 1000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": str(competitor_id1),
                                "company_name": "Competitor 1",
                                "value": 600
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": str(competitor_id1),
                                "company_name": "Competitor 1",
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": str(competitor_id1),
                                "company_name": "Competitor 1",
                                "value": 6000
                            }
                        ]
                    }
                ],
                "primary": [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": str(competitor_id1),
                                "company_name": "Competitor 1",
                                "value": 1000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": str(competitor_id1),
                                "company_name": "Competitor 1",
                                "value": 600
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": str(competitor_id1),
                                "company_name": "Competitor 1",
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": str(competitor_id1),
                                "company_name": "Competitor 1",
                                "value": 6000
                            }
                        ]
                    }
                ],
                "secondary": [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": str(competitor_id2),
                                "company_name": "Competitor 2",
                                "value": 3000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": str(competitor_id2),
                                "company_name": "Competitor 2",
                                "value": 1800
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "company_id": str(competitor_id2),
                                "company_name": "Competitor 2",
                                "value": 30000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "company_id": str(competitor_id2),
                                "company_name": "Competitor 2",
                                "value": 18000
                            }
                        ]
                    }
                ],
                "cluster": [
                    {
                        "target_year": 2011,
                        "series": []
                    },
                    {
                        "target_year": 2016,
                        "series": []
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate_parent__sum(self):

        calc_engine = AggregateCompetitorDemographics.__new__(AggregateCompetitorDemographics)
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
            "aggregate": "sum"
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
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 600
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 6000
                            }
                        ]
                    }
                ]
            ],
            [
                str(competitor_id2),
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 3000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 1800
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 30000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 18000
                            }
                        ]
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
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 4000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 2400
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 40000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 24000
                            }
                        ]
                    }
                ],
                "primary": [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 1000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 600
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 6000
                            }
                        ]
                    }
                ],
                "secondary": [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 3000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 1800
                            }
                        ]
                    },
                    {
                        "target_year": 2016,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 6, 1) - one_day,
                                "value": 30000
                            },
                            {
                                "date": datetime.datetime(2013, 5, 1) - one_day,
                                "value": 18000
                            }
                        ]
                    }
                ],
                "cluster": [
                    {
                        "target_year": 2011,
                        "series": []
                    },
                    {
                        "target_year": 2016,
                        "series": []
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()