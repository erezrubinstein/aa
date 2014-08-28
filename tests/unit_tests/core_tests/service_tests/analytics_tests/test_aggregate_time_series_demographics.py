from __future__ import division
from core.service.svc_analytics.implementation.calc.engines.demographics.aggregate_time_series_demographics \
    import AggregateTimeSeriesDemographics
from core.service.svc_analytics.implementation.calc.company_analytics_calc_helper import CompanyAnalyticsCalcHelper
from core.service.svc_analytics.implementation.calc.retail_parent_calc_engine import RetailParentCalcEngine
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import FastDateParser
from bson.objectid import ObjectId
import numpy as np
import datetime
import unittest
import mox
from mox import Comparator, IsA


class IsNumpyArrayEqual(Comparator):

    def __init__(self, nparray):
        self._nparray = nparray

    def equals(self, rhs):
        return np.array_equal(rhs, self._nparray)


class AggregateTimeSeriesDemographicsTests(mox.MoxTestBase):

    def setUp(self):

        super(AggregateTimeSeriesDemographicsTests, self).setUp()
        register_common_mox_dependencies(self.mox)

        self.main_param = Dependency("CoreAPIParamsBuilder").value
        self.main_access = Dependency("CoreAPIProvider").value

    def test_calculate_company(self):

        calc_engine = AggregateTimeSeriesDemographics.__new__(AggregateTimeSeriesDemographics)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "target_entity_type": "company",
            "aggregate": "mean"
        }

        company_id = ObjectId()

        calc_engine.run_params = {
            "target_entity_ids": [str(company_id)]
        }

        calc_engine.fetched_data = [
            [
                ObjectId(),
                str(company_id),
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
            str(company_id): [
                {
                    "target_year": 2011,
                    "series": [
                        {
                            "date": datetime.datetime(2013, 5, 1),
                            "value": 15000
                        },
                        {
                            "date": datetime.datetime(2013, 4, 1),
                            "value": 15000
                        },
                        {
                            "date": datetime.datetime(2013, 3, 1),
                            "value": 15000
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(expected_results, calc_engine.results)

    def test_calculate_company_parent(self):

        calc_engine = AggregateTimeSeriesDemographics.__new__(AggregateTimeSeriesDemographics)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "target_entity_type": "company",
            "aggregate": "mean"
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

        calc_engine.fetched_data = [
            [
                ObjectId(),
                str(banner_id1),
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
            str(parent_id): [
                {
                    "target_year": 2011,
                    "series": [
                        {
                            "date": datetime.datetime(2013, 5, 1),
                            "value": 15000
                        },
                        {
                            "date": datetime.datetime(2013, 4, 1),
                            "value": 15000
                        },
                        {
                            "date": datetime.datetime(2013, 3, 1),
                            "value": 15000
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(expected_results, calc_engine.results)

    def test_calculate_company_analytics(self):

        calc_engine = AggregateTimeSeriesDemographics.__new__(AggregateTimeSeriesDemographics)

        calc_engine.engine = "competition_adjusted_demographics"
        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "target_entity_type": "company_analytics",
            "key": "data.analytics.aggregate_trade_area_population"
        }

        company_id = ObjectId()

        calc_engine.run_params = {
            "target_entity_ids": [str(company_id)]
        }

        calc_engine.fetched_data = [
            [
                ObjectId(),
                str(company_id),
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
                                "value": 100
                            },
                            {
                                "date": datetime.datetime(2013, 3, 1),
                                "value": 10
                            }
                        ]
                    }
                ]
            ],
            [
                ObjectId(),
                str(company_id),
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
                                "value": 200
                            },
                            {
                                "date": datetime.datetime(2013, 3, 1),
                                "value": 20
                            }
                        ]
                    }
                ]
            ]
        ]

        self.mox.StubOutWithMock(CompanyAnalyticsCalcHelper, "_process_can")

        # we expect 3 CAN saves here
        # using a custom Comparator to make sure the numpy arrays work
        CompanyAnalyticsCalcHelper(calc_engine, calc_engine.engine, use_target_year=True, memoize=False)._process_can(str(company_id), 2011, datetime.datetime(2013, 5, 1), IsNumpyArrayEqual(np.array([10000, 20000], float)), "aggregate_trade_area_population")
        CompanyAnalyticsCalcHelper(calc_engine, calc_engine.engine, use_target_year=True, memoize=False)._process_can(str(company_id), 2011, datetime.datetime(2013, 4, 1), IsNumpyArrayEqual(np.array([100, 200], float)), "aggregate_trade_area_population")
        CompanyAnalyticsCalcHelper(calc_engine, calc_engine.engine, use_target_year=True, memoize=False)._process_can(str(company_id), 2011, datetime.datetime(2013, 3, 1), IsNumpyArrayEqual(np.array([10, 20], float)), "aggregate_trade_area_population")

        self.mox.ReplayAll()

        calc_engine._calculate()


    def test_save_company_analytics__does_nothing(self):
        """
        If output is company_analytics, the calc engine should basically do nothing, since save is handled during _calculate()
        """

        calc_engine = AggregateTimeSeriesDemographics.__new__(AggregateTimeSeriesDemographics)

        calc_engine.output = {
            "target_entity_type": "company_analytics"
        }

        self.mox.ReplayAll()

        calc_engine._save()


    def test_save_company__calls_super(self):
        """
        If output is company, the calc engine should call the super class _save()
        """

        calc_engine = AggregateTimeSeriesDemographics.__new__(AggregateTimeSeriesDemographics)

        calc_engine.output = {
            "target_entity_type": "company",
        }

        self.mox.StubOutWithMock(RetailParentCalcEngine, "_save")
        #init args are: config, logger, calc_id, engine, engine_module, _input, output, run_params, context, date_parser
        RetailParentCalcEngine(IsA(dict), IsA(object), IsA(object), IsA(basestring), IsA(object), IsA(dict), calc_engine.output, IsA(dict), IsA(dict), IsA(object))._save()
        self.mox.ReplayAll()
        calc_engine._save()



if __name__ == '__main__':
    unittest.main()