from __future__ import division
from common.service_access.utilities.json_helpers import APIEncoder_New, APIDecoder
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_trade_area, insert_test_store, insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from core.service.svc_analytics.implementation.calc.calc import Calc
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import parse_date
from core.common.utilities.helpers import ensure_id
import datetime


__author__ = "vgold"


class AnalyticsCompetitionTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "analytics_competition_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # some pycharm/unittest param that blocks you from seeing a diff failure in an assert statement if it's too long
        self.maxDiff = None
        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.analytics_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def analytics_competition_monthly_average_trade_area_competition_ratio(self):

        # Create trade area
        company_id = insert_test_company()

        interval = [None, None]
        store_id = insert_test_store(company_id, interval)

        one_day = datetime.timedelta(days=1)

        monthly_away_competitor_count = [
            {
                "date": datetime.datetime(2012, 2, 1) - one_day,
                "value": 1
            },
            {
                "date": datetime.datetime(2012, 3, 1) - one_day,
                "value": 3
            },
            {
                "date": datetime.datetime(2012, 4, 1) - one_day,
                "value": 7
            },
            {
                "date": datetime.datetime(2012, 5, 1) - one_day,
                "value": 2
            }
        ]

        data = {
            "analytics": {
                "competition": {
                    "monthly": {
                        "away_store_count": monthly_away_competitor_count
                    }
                }
            }
        }

        insert_test_trade_area(store_id, company_id, **data)

        name = description = "Monthly Average Trade Area Competition Ratio - Integration Test"
        engine_module = "aggregate_trade_area_competition_ratio"

        input_rec = {
            "entity_type": "trade_area",
            "entity_query": "{}",
            "target_entity_field": "data.company_id",
            "fields": [
                "_id",
                "data.company_id",
                "data.analytics.competition.monthly.away_store_count"
            ]
        }

        output = {
            "target_entity_type": "company",
            "key": "data.analytics.competition.monthly.aggregate_trade_area_competition_ratio.mean",
            "aggregate": "mean"
        }

        calc = Calc.make_calc_record(name, description, "competition", engine_module, input_rec, output)

        calc_id = self.analytics_access.call_post_new_calc(calc, self.context)

        run_params = {
            "target_entity_ids": [company_id],
            "options": {
                "fetch": True,
                "save": True,
                "return": False
            }
        }

        results = self.analytics_access.call_post_run_calc(calc_id, run_params, self.context)

        calc_run = self.analytics_access.call_get_calc_run(results["_id"], self.context)
        self.test_case.assertTrue(calc_run is not None)

        query = {
            "_id": ensure_id(company_id)
        }

        entity_fields = ["_id", output["key"]]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query,
                                                   entity_fields=entity_fields, as_list=True)["params"]
        company = self.mds_access.call_find_entities_raw("company", params, self.context)[0]

        reverse_monthly_away_competitor_count = sorted(monthly_away_competitor_count,
                                                       key=lambda x: x["date"], reverse=True)

        for i, result in enumerate(company[1]):
            self.test_case.assertEqual(parse_date(result["date"]), reverse_monthly_away_competitor_count[i]["date"])
            self.test_case.assertEqual(result["value"], reverse_monthly_away_competitor_count[i]["value"])

    def analytics_competition_monthly_company_competition_ratio(self):
        # Create a company with fake analytics data
        analytics_data = {
            "competition": {
                "monthly": {
                    "DistanceMiles10": {
                        "competition_instance_counts": {
                            "sum": {
                                "raw": {
                                    "total": [
                                        {
                                            "date": "2013-07-01",
                                            "value": 1000
                                        },
                                        {
                                            "date": "2013-06-01",
                                            "value": 1234
                                        }
                                    ]
                                },
                                "weighted": {
                                    "total": [
                                        {
                                            "date": "2013-07-01",
                                            "value": 1000
                                        },
                                        {
                                            "date": "2013-06-01",
                                            "value": 1234
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            "stores": {
                "monthly": {
                    "store_count": [
                        {
                            "date": "2013-07-01",
                            "value": 900
                        },
                        {
                            "date": "2013-06-01",
                            "value": 56
                        }
                    ]
                }
            }
        }

        company_id = insert_test_company(analytics=analytics_data)

        name = description = "Monthly Company Competition Ratio - Integration Test"
        engine_module = "company_competition_ratio"

        _input = {
            "target_entity_role": "retail_segment",
            "entity_type": "company",
            "entity_query": "{}",
            "target_entity_field": "_id",
            "fields": [
                "_id",
                "data.analytics.competition.monthly.DistanceMiles10.competition_instance_counts.sum",
                "data.analytics.stores.monthly.store_count"
            ]
        }

        output = {
            "key": "data.analytics.competition.monthly.DistanceMiles10.company_competition_ratio.mean",
            "target_entity_type": "company",
            "aggregate": "mean"
        }

        calc = Calc.make_calc_record(name, description, "competition", engine_module, _input, output)

        calc_id = self.analytics_access.call_post_new_calc(calc, self.context)

        run_params = {
            "target_entity_ids": [company_id],
            "options": {
                "fetch": True,
                "save": True,
                "return": False
            }
        }

        results = self.analytics_access.call_post_run_calc(calc_id, run_params, self.context)

        expected_results_part1 = {
            u'calc_id': calc_id,
            u'run_params': {
                u'options': {
                    u'fetch': True,
                    u'overwrite': True,
                    u'return': False,
                    u'save': True,
                    u'save_calc_run': True,
                    u'update_workflow': False
                },
                u'target_entity_ids': [company_id]
            }
        }
        self.test_case.assertDictContainsSubset(expected_results_part1, results)

        expected_results_part2 = {
            u'message': u'Calculation completed successfully.',
            u'status': u'success'
        }
        self.test_case.assertDictContainsSubset(expected_results_part2, results["meta"])

        company = self.mds_access.call_get_entity("company", company_id, json_encoder=APIEncoder_New, json_decoder=APIDecoder)

        expected_company_data_analytics = {
            u'competition': {
                u'monthly': {
                    u'DistanceMiles10': {
                        u'company_competition_ratio': {
                            u'mean': {
                                u'raw': {
                                    u'total': [
                                        {
                                            u'date': datetime.datetime(2013,7,1),
                                            u'value': 1.1111111111111112
                                        },
                                        {
                                            u'date': datetime.datetime(2013,6,1),
                                            u'value': 22.035714285714285
                                        }
                                    ],
                                    'primary': [],
                                    'secondary': [],
                                    'cluster': []
                                },
                                u'weighted': {
                                    u'total': [
                                        {
                                            u'date': datetime.datetime(2013,7,1),
                                            u'value': 1.1111111111111112
                                        },
                                        {
                                            u'date': datetime.datetime(2013,6,1),
                                            u'value': 22.035714285714285
                                        }
                                    ],
                                    'primary': [],
                                    'secondary': [],
                                    'cluster': []
                                }
                            }
                        },
                        u'competition_instance_counts': {
                            u'sum': {
                                u'raw': {
                                    u'total': [
                                        {
                                            u'date': u'2013-07-01',
                                            u'value': 1000
                                        },
                                        {
                                            u'date': u'2013-06-01',
                                            u'value': 1234
                                        }
                                    ]
                                },
                                u'weighted': {
                                    u'total': [
                                        {
                                            u'date': u'2013-07-01',
                                            u'value': 1000
                                        },
                                        {
                                            u'date': u'2013-06-01',
                                            u'value': 1234
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            u'stores': {
                u'monthly': {
                    u'store_count': [
                        {
                            u'date': u'2013-07-01',
                            u'value': 900
                        },
                        {
                            u'date': u'2013-06-01',
                            u'value': 56
                        }
                    ]
                }
            }
        }

        self.test_case.assertEqual(company["data"]["analytics"], expected_company_data_analytics)


###################################################################################################
