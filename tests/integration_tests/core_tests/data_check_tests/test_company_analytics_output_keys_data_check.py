import unittest
import copy
import os

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.validity.company_analytics_output_keys_data_check import CompanyAnalyticsCompetitionKeysDataCheck, CompanyAnalyticsDemographicsKeysDataCheck, CompanyAnalyticsStoresKeysDataCheck, CompanyAnalyticsEconomicsKeysDataCheck
from core.service.svc_analytics.implementation.helpers.ref_data_helper import read_analytics_reference_data
from core.service.utilities.helpers import get_code_root


__author__ = 'vgold'


class TestCompanyAnalyticsOutputKeysDataCheck(unittest.TestCase):

    conn = None
    mds = None

    @classmethod
    def setUpClass(cls):

        cls.conn = mongo_client.MongoClient("localhost", 27017)
        cls.mds = cls.conn["itest_mds"]

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        """
        This is cruel, but since we're calling the service endpoint directly the good_company_analytics dict below
        will have to contain ALL analytics keys for a company that has been defined in default_calcs

        If this test breaks, you probably added/modified default_calcs.json and need to update good_company_analytics

        To find out what keys need to be present in the document below, run this query on your analytics database:
        db.calcs.find({"output.target_entity_type": "company", "output.key" : /^data.analytics/  }, { "output.key": 1 }).sort( {"output.key" :1 })

        And make sure the keys listed are in the dictionary below

        I wish this could be done in a different way, but there's no simple way to mock the analytics service endpoint
        or even change the default_calcs in the analytics database (for now). Let me know if there's a better idea.
        """
        complete_company_analytics = {
            "competition": {
                "monthly": {
                    "DistanceMiles10": {
                        "aggregate_competitor_average_trade_area_competition_ratio": {
                            "max": 1,
                            "mean": 1,
                            "median": 1,
                            "min": 1
                        },
                        "aggregate_competitor_company_competition_ratio": {
                            "max": 1,
                            "mean": 1,
                            "median": 1,
                            "min": 1
                        },
                        "aggregate_competitor_trade_area_income": {
                            "max": 1,
                            "median": 1
                        },
                        "aggregate_competitor_trade_area_population": {
                            "max": 1,
                            "median": 1
                        },
                        "aggregate_distinct_stores_affected": 1,
                        "aggregate_trade_area_competition_ratio": {
                            "mean": 1,
                            "median": 1
                        },
                        "average_competition_weight": 1,
                        "company_competition_ratio": 1,
                        "competition_instance_counts": {
                            "max": 1,
                            "sum": 1
                        },
                        "competitive_company_counts": 1,
                        "aggregate_competition_instances": {
                            "mean": 1
                        }
                    }
                }
            },
            "competition_adjusted_demographics": {
                "monthly": {
                    "DistanceMiles10": {
                        "aggregate_trade_area_income": {
                            "min": 1,
                            "max": 1,
                            "mean": 1,
                            "median": 1,
                            "variance": 1
                        },
                        "aggregate_trade_area_income_for_store_closings": {
                            "median": 1
                        },
                        "aggregate_trade_area_income_for_store_openings": {
                            "median": 1
                        },
                        "aggregate_trade_area_population": {
                            "min": 1,
                            "max": 1,
                            "mean": 1,
                            "median": 1,
                            "variance": 1
                        },
                        "aggregate_trade_area_population_for_store_closings": {
                            "median": 1
                        },
                        "aggregate_trade_area_population_for_store_openings": {
                            "median": 1
                        },
                        "aggregate_trade_area_households": {
                            "mean": 1,
                            "min": 1,
                            "max": 1
                        }
                    }
                }
            },
            "demographics": {
                "monthly": {
                    "DistanceMiles10": {
                        "aggregate_trade_area_population": {
                            "min": 1,
                            "max": 1,
                            "median": 1,
                            "mean": 1
                        },
                        "aggregate_trade_area_income": {
                            "min": 1,
                            "max": 1,
                            "median": 1,
                            "mean": 1
                        },
                        "aggregate_trade_area_households": {
                            "mean": 1,
                            "min": 1,
                            "max": 1
                        },
                        "aggregate_trade_area_per_capita_income": {
                            "mean": 1,
                            "min": 1,
                            "max": 1
                        }
                    }
                }
            },
            "monopolies": {
                "monthly": {
                    "DistanceMiles10": {
                        "aggregate_competitor_single_player_monopolies": {
                            "max": 1,
                            "median": 1,
                            "mean": 1
                        },
                        "store_monopoly_percent": 1
                    }
                }
            },
            "stores": {
                "monthly": {
                    "store_counts": 1,
                    "store_openings": 1,
                    "store_closings": 1,
                    "store_growth": 1,
                }
            },
            "economics": {
                "monthly": {
                    "DistanceMiles10": {
                        "aggregate_trade_area_unemployment_rate": {
                            "mean": 1
                        },
                        "aggregate_competitor_trade_area_unemployment_rate": {
                            "mean": 1,
                            "median": 1
                        }
                    }
                }
            },
            "white_space_demographic_distributions": {
                "data": 1
            }
        }

        self.co1 = ObjectId()
        self.co2 = ObjectId()
        self.co3 = ObjectId()
        self.co4 = ObjectId()
        self.co5 = ObjectId()
        
        good_data1 = copy.deepcopy(complete_company_analytics)

        bad_data1 = copy.deepcopy(complete_company_analytics)
        del bad_data1["competition"]

        bad_data2 = copy.deepcopy(complete_company_analytics)
        del bad_data2["stores"]["monthly"]["store_growth"]

        bad_data3 = copy.deepcopy(complete_company_analytics)
        del bad_data3["economics"]

        bad_data4 = copy.deepcopy(complete_company_analytics)
        del bad_data4["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]

        self.companies = [
            {
                "_id": self.co1,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {"status": "published"},
                        "analytics": {"plan_b_has_run": True}
                    },
                    "analytics": good_data1
                }
            },
            {
                "_id": self.co2,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {"status": "published"},
                        "analytics": {"plan_b_has_run": True}
                    },
                    "analytics": bad_data1
                }
            },
            {
                "_id": self.co3,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {"status": "published"},
                        "analytics": {"plan_b_has_run": True}
                    },
                    "analytics": bad_data2
                }
            },
            {
                "_id": self.co4,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {"status": "published"},
                        "analytics": {"plan_b_has_run": True}
                    },
                    "analytics": bad_data3
                }
            },
            {
                "_id": self.co5,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {"status": "published"},
                        "analytics": {"plan_b_has_run": True}
                    },
                    "analytics": bad_data4
                }
            }
        ]
        self.mds.company.insert(self.companies)
        self.company_dict = {
            str(co["_id"])
            for co in self.companies
        }

        code_root = get_code_root()
        engines_path = os.path.join(code_root, "core/service/svc_analytics/implementation/calc/engines")
        calcs = read_analytics_reference_data(engines_path)
        self.mds.calcs.insert(calcs)

    def tearDown(self):
        self.mds.company.drop()
        self.mds.company.drop()

    def test_company_analytics_output_keys_data_check(self):
        query = {
            "output.target_entity_type": "company"
        }
        projection = {
            "output.key": 1,
            "input.target_entity_role": 1,
            "engine": 1
        }
        calcs = list(self.mds.calcs.find(query, projection))
        extra_data = {
            "analytics_calc_records": calcs
        }

        # check for good ones
        checker = CompanyAnalyticsCompetitionKeysDataCheck(self.mds, self.companies[0], self.company_dict, extra_data)
        result = checker.check()
        self.assertTrue(result)

        checker = CompanyAnalyticsDemographicsKeysDataCheck(self.mds, self.companies[0], self.company_dict, extra_data)
        result = checker.check()
        self.assertTrue(result)

        checker = CompanyAnalyticsStoresKeysDataCheck(self.mds, self.companies[0], self.company_dict, extra_data)
        result = checker.check()
        self.assertTrue(result)

        checker = CompanyAnalyticsEconomicsKeysDataCheck(self.mds, self.companies[0], self.company_dict, extra_data)
        result = checker.check()
        self.assertTrue(result)

        # check bad ones
        checker = CompanyAnalyticsCompetitionKeysDataCheck(self.mds, self.companies[1], self.company_dict, extra_data)
        result = checker.check()
        self.assertFalse(result)

        checker = CompanyAnalyticsStoresKeysDataCheck(self.mds, self.companies[2], self.company_dict, extra_data)
        result = checker.check()
        self.assertFalse(result)

        checker = CompanyAnalyticsEconomicsKeysDataCheck(self.mds, self.companies[3], self.company_dict, extra_data)
        result = checker.check()
        self.assertFalse(result)

        checker = CompanyAnalyticsDemographicsKeysDataCheck(self.mds, self.companies[4], self.company_dict, extra_data)
        result = checker.check()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
