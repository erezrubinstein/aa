from __future__ import division
from core.service.svc_analytics.implementation.calc.engines.demographics.aggregate_churn_time_series_demographics \
    import AggregateChurnTimeSeriesDemographics
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from bson.objectid import ObjectId
import datetime
import unittest
import mox


__author__ = 'imashhor'


class AggregateChurnTimeSeriesDemographicsTests(mox.MoxTestBase):

    def setUp(self):

        super(AggregateChurnTimeSeriesDemographicsTests, self).setUp()
        register_common_mox_dependencies(self.mox)

    def test_calculate(self):

        calc_engine = AggregateChurnTimeSeriesDemographics.__new__(AggregateChurnTimeSeriesDemographics)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "target_entity_type": "company",
            "aggregates": ["mean"]
        }

        company_id = ObjectId()

        calc_engine.run_params = {
            "target_entity_ids": [str(company_id)]
        }

        calc_engine.input = {
            "fields": []
        }

        calc_engine.fetched_data = [
            [
                ObjectId(),
                str(company_id),
                datetime.datetime(2013, 5, 1),
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 5, 1),
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 4, 1),
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 3, 1),
                                "value": 10000
                            }
                        ]
                    }
                ]
            ],
            [
                ObjectId(),
                str(company_id),
                datetime.datetime(2013, 4, 1),
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 5, 1),
                                "value": 20000
                            },
                            {
                                "date": datetime.datetime(2013, 4, 1),
                                "value": 20000
                            },
                            {
                                "date": datetime.datetime(2013, 3, 1),
                                "value": 20000
                            }
                        ]
                    }
                ]
            ]
        ]

        calc_engine._calculate()

        expected_results = {
            str(company_id): {
                "mean": [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 5, 1),
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 4, 1),
                                "value": 20000
                            }
                        ]
                    }
                ]
            }
        }

        self.assertDictEqual(expected_results, calc_engine.results)

    def test_calculate_parent(self):

        calc_engine = AggregateChurnTimeSeriesDemographics.__new__(AggregateChurnTimeSeriesDemographics)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "target_entity_type": "company",
            "aggregates": ["mean"]
        }

        parent_id = ObjectId()
        banner_id1 = ObjectId()
        banner_id2 = ObjectId()

        calc_engine.child_to_parent_dict = {
            str(banner_id1): str(parent_id),
            str(banner_id2): str(parent_id)
        }

        calc_engine.run_params = {
            "target_entity_ids": [str(parent_id)]
        }

        calc_engine.input = {
            "fields": []
        }

        calc_engine.fetched_data = [
            [
                ObjectId(),
                str(banner_id1),
                datetime.datetime(2013, 5, 1),
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 5, 1),
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 4, 1),
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 3, 1),
                                "value": 10000
                            }
                        ]
                    }
                ]
            ],
            [
                ObjectId(),
                str(banner_id2),
                datetime.datetime(2013, 4, 1),
                [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 5, 1),
                                "value": 20000
                            },
                            {
                                "date": datetime.datetime(2013, 4, 1),
                                "value": 20000
                            },
                            {
                                "date": datetime.datetime(2013, 3, 1),
                                "value": 20000
                            }
                        ]
                    }
                ]
            ]
        ]

        calc_engine._calculate()

        expected_results = {
            str(parent_id): {
                "mean": [
                    {
                        "target_year": 2011,
                        "series": [
                            {
                                "date": datetime.datetime(2013, 5, 1),
                                "value": 10000
                            },
                            {
                                "date": datetime.datetime(2013, 4, 1),
                                "value": 20000
                            }
                        ]
                    }
                ]
            }
        }

        self.assertDictEqual(expected_results, calc_engine.results)




if __name__ == '__main__':
    unittest.main()
