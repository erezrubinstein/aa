from __future__ import division
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from bson.objectid import ObjectId
import copy


class AnalyticsServiceTestCollection(ServiceTestCollection):

    def initialize(self):
        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.analytics_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def analytics_test_company_data_check__read_docstring_if_fail(self):
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
        good_company_analytics = {
            "analytics": {
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
                "white_space_demographic_distributions": {}
            }
        }

        # Lets make a few bad analytics companies by removing some keys
        bad_company_analytics_1 = copy.deepcopy(good_company_analytics)
        bad_company_analytics_1["analytics"]["stores"]["monthly"].pop("store_counts", None)

        bad_company_analytics_2 = copy.deepcopy(good_company_analytics)
        bad_company_analytics_2["analytics"]["demographics"]["monthly"]["DistanceMiles10"].pop(
            "aggregate_trade_area_income", None)

        bad_company_analytics_3 = copy.deepcopy(good_company_analytics)
        bad_company_analytics_3["analytics"]["competition"]["monthly"]["DistanceMiles10"].pop(
            "competitive_company_counts", None)

        # Insert some good and bad companies
        company_id_good_1 = insert_test_company(workflow_status="published", **good_company_analytics)
        company_id_good_2 = insert_test_company(workflow_status="published", **good_company_analytics)
        company_id_bad_1 = insert_test_company(workflow_status="published", **bad_company_analytics_1)
        company_id_bad_2 = insert_test_company(workflow_status="published", **bad_company_analytics_2)
        company_id_bad_3 = insert_test_company(workflow_status="published", **bad_company_analytics_3)
        company_id_bad_4 = insert_test_company(workflow_status="published")

        # RUN IT
        self.analytics_access.call_company_data_check()

        # Get the results from database
        company_ids = [company_id_good_1, company_id_good_2, company_id_bad_1, company_id_bad_2, company_id_bad_3,
                       company_id_bad_4]

        query = {
            "_id": {"$in": [ObjectId(company_id) for company_id in company_ids]}
        }

        entity_fields = ["_id", "data.valid.analytics"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query,
                                                   entity_fields=entity_fields, as_list=True)["params"]

        results = self.main_access.mds.call_find_entities_raw("company", params, self.context)

        results = [result_sublist[1] for result_sublist in results]

        self.test_case.assertListEqual([True, True, False, False, False, False], results)
