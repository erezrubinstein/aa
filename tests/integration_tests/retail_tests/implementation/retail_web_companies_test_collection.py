from __future__ import division
import pprint
from dateutil.relativedelta import relativedelta
from tests.integration_tests.utilities.entity_hierarchy_test_helper import create_companies_and_relationships, create_companies_and_relationships_just_parent, create_companies_and_relationships_just_banner
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.date_utilities import LAST_ANALYTICS_DATE, LAST_ECONOMICS_DATE
from requests.cookies import RequestsCookieJar


__author__ = 'vgold'


class RetailWebCompaniesTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "retail_web_companies_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_test_user_get_cookies()
        self.global_stores_end_date = "2013-08-15T00:00:00"
        self.global_stores_start_date = "2012-07-25T00:00:00"
        self.last_store_date = LAST_ANALYTICS_DATE.strftime("%Y-%m-%dT%H:%M:%S")
        self.last_store_count = 19
        self.last_economics_date = LAST_ECONOMICS_DATE.strftime("%Y-%m-%dT%H:%M:%S")
        self.store_collection_dates = ["2013-08-15", "2012-07-25"]
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##
        
    def __login_test_user_get_cookies(self):
        params = {"email": "test@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    def __compare_results_with_expected(self, expected_results, company_results):

        expected_company_hierarchy = expected_results["company_hierarchy"]
        actual_company_hierarchy = company_results["company_hierarchy"]

        del expected_results["company_hierarchy"]
        del company_results["company_hierarchy"]

        # sort the company tree ids to make them match
        expected_results["company_tree_ids"] = sorted(expected_results["company_tree_ids"])
        company_results["company_tree_ids"] = sorted(company_results["company_tree_ids"])
        expected_results["family_list"] = sorted(expected_results["family_list"])
        company_results["family_list"] = sorted(company_results["family_list"])

        self.test_case.maxDiff = None
        self.test_case.assertDictEqual(expected_results, company_results)

        self.test_case.assertListEqual(sorted(expected_company_hierarchy["secondary_parents"]),
                                       sorted(actual_company_hierarchy["secondary_parents"]))

        self.test_case.assertListEqual(sorted(expected_company_hierarchy["parents"]),
                                       sorted(actual_company_hierarchy["parents"]))

        self.test_case.assertListEqual(sorted(expected_company_hierarchy["banners"]),
                                       sorted(actual_company_hierarchy["banners"]))

        self.test_case.assertListEqual(sorted(expected_company_hierarchy["secondary_banners"]),
                                       sorted(actual_company_hierarchy["secondary_banners"]))

        self.test_case.assertListEqual(sorted(expected_company_hierarchy["owners"]),
                                       sorted(actual_company_hierarchy["owners"]))

        self.test_case.assertListEqual(sorted(expected_company_hierarchy["cooperatives"]),
                                       sorted(actual_company_hierarchy["cooperatives"]))

    ##------------------------------------ Retail Web Company Tests ---------------------------------------##

    def web_test_get_company_hierarchy_banner(self):

        create_companies_and_relationships(self)

        expected_results = {
            u"_id": self.company_id23,
            u"company_tree_ids": [self.company_id23],
            u'all_competing_industries_published': False,
            u'white_space_competition_set': [],
            u'any_competing_industries_published': False,
            u'all_primary_industries_of_banners_published': False,
            "valid": {
                "analytics": False,
                "v1_2": {
                    "analytics": {
                        'competition': False,
                        'competitor_summary': False,
                        'monopolies': False,
                        'demographics': False,
                        'economics': False,
                        'stores': False,
                        'white_space': False
                    }
                }
            },
            u"name": u"BC",
            u"status": u"BC",
            u"description": u"BC",
            u"ticker": u"BC",
            u"exchange": u"BC",
            u"type": u"retail_banner",
            u"main_site_url": None,
            u"primary_industry": None,
            u"published": True,
            u'last_analytics_stores_date': self.last_store_date,
            u'last_analytics_competition_date': self.last_store_date,
            u'last_analytics_economics_date': self.last_economics_date,
            u'last_store_date': self.last_store_date,
            u'last_store_count': self.last_store_count,
            u'global_stores_start_date': self.global_stores_start_date,
            u'global_stores_end_date': self.global_stores_end_date,
            u'analytics_dates': {u"monthly": {u"stores": {u"end": self.last_store_date},
                                             u"competition": {u"end": self.last_store_date},
                                             u"economics": {u"end": self.last_economics_date}}},
            u'store_collection_dates': self.store_collection_dates,
            u"family_list": [self.company_id2,
                             self.company_id3,
                             self.company_id6,
                             self.company_id12,
                             self.company_id23,
                             self.company_id100],
            u"company_hierarchy": {
                "secondary_banners": [],
                "secondary_parents": [
                    {
                        "id": self.company_id100,
                        "name": "AAA",
                        "ticker": "AAA",
                        "exchange": "AAA",
                        "primary_industry": None,
                        "published": True
                    }
                ],
                u"parents": [
                    {
                        "id": self.company_id2,
                        "name": "B",
                        "ticker": "B",
                        "exchange": "B",
                        "primary_industry": {
                            "id": self.industry_id2,
                            "name": "b",
                            "label": "b b",
                            'publish_competition_for_banners': False
                        },
                        "published": True
                    }
                ],
                u"owners": [
                    {
                        "id": self.company_id6,
                        "name": "F",
                        "ticker": "F",
                        "exchange": "F",
                        "primary_industry": None,
                        "published": True
                    }
                ],
                u"banners": [
                    {
                        "id": self.company_id12,
                        "name": "AB",
                        "ticker": "AB",
                        "exchange": "AB",
                        "primary_industry": None,
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    },
                    {
                        "id": self.company_id23,
                        "name": "BC",
                        "ticker": "BC",
                        "exchange": "BC",
                        "primary_industry": None,
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    }
                ],
                u"cooperatives": [
                    {
                        "id": self.company_id3,
                        "name": "C",
                        "ticker": "C",
                        "exchange": "C",
                        "primary_industry": {
                            "id": self.industry_id3,
                            "name": "c",
                            "label": "c c",
                            'publish_competition_for_banners': False
                        },
                        "published": True
                    }
                ]
            }
        }

        results = self.web_access.get("/api/companies/%s" % self.company_id23, "", cookies=self.cooks, time_out=9999).json()
        company_results = results["company"]
        self.__compare_results_with_expected(expected_results, company_results)

    def web_test_get_company_hierarchy_parent(self):

        create_companies_and_relationships(self)

        expected_results = {
            u"_id": self.company_id2,
            u"company_tree_ids": [self.company_id2, self.company_id12, self.company_id23],
            u"name": u"B",
            u"status": u"B",
            u'all_competing_industries_published': False,
            u'white_space_competition_set': [],
            u'any_competing_industries_published': False,
            u'all_primary_industries_of_banners_published': False,
            "valid": {
                "analytics": False,
                "v1_2": {
                    "analytics": {
                        'competition': False,
                        'competitor_summary': False,
                        'monopolies': False,
                        'demographics': False,
                        'economics': False,
                        'stores': False,
                        'white_space': False
                    }
                }
            },
            u"description": u"B",
            u"ticker": u"B",
            u"exchange": u"B",
            u"type": u"retail_parent",
            u"main_site_url": None,
            u"primary_industry": {
                u'id': self.industry_id2,
                u'label': u'b b',
                u'name': u'b',
                u'publish_competition_for_banners': False
            },
            u"published": True,
            u'last_analytics_stores_date': self.last_store_date,
            u'last_analytics_competition_date': self.last_store_date,
            u'last_analytics_economics_date': self.last_economics_date,
            u'last_store_date': self.last_store_date,
            u'last_store_count': self.last_store_count,
            u'global_stores_start_date': self.global_stores_start_date,
            u'global_stores_end_date': self.global_stores_end_date,
            u'analytics_dates': {u"monthly": {u"stores": {u"end": self.last_store_date},
                                             u"competition": {u"end": self.last_store_date},
                                             u"economics": {u"end": self.last_economics_date}}},
            u'store_collection_dates': self.store_collection_dates,
            u"family_list": [self.company_id2,
                             self.company_id3,
                             self.company_id6,
                             self.company_id12,
                             self.company_id23],
            u"company_hierarchy": {
                "secondary_banners": [],
                "secondary_parents": [],
                u"parents": [
                    {
                        "id": self.company_id2,
                        "name": "B",
                        "ticker": "B",
                        "exchange": "B",
                        "primary_industry": {
                            "id": self.industry_id2,
                            "name": "b",
                            "label": "b b",
                            'publish_competition_for_banners': False
                        },
                        "published": True
                    }
                ],
                u"owners": [
                    {
                        "id": self.company_id6,
                        "name": "F",
                        "ticker": "F",
                        "exchange": "F",
                        "primary_industry": None,
                        "published": True
                    }
                ],
                u"banners": [
                    {
                        "id": self.company_id12,
                        "name": "AB",
                        "ticker": "AB",
                        "exchange": "AB",
                        "primary_industry": None,
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    },
                    {
                        "id": self.company_id23,
                        "name": "BC",
                        "ticker": "BC",
                        "exchange": "BC",
                        "primary_industry": None,
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    }
                ],
                u"cooperatives": [
                    {
                        "id": self.company_id3,
                        "name": "C",
                        "ticker": "C",
                        "exchange": "C",
                        "primary_industry": {
                            "id": self.industry_id3,
                            "name": "c",
                            "label": "c c",
                            'publish_competition_for_banners': False
                        },
                        "published": True
                    }
                ]
            }
        }

        results = self.web_access.get("/api/companies/%s" % self.company_id2, "", cookies=self.cooks, time_out=9999).json()
        company_results = results["company"]
        self.__compare_results_with_expected(expected_results, company_results)

    def web_test_get_company_hierarchy_cooperative(self):

        create_companies_and_relationships(self)

        expected_results = {
            u"_id": self.company_id3,
            u"company_tree_ids": [self.company_id3, self.company_id23, self.company_id34],
            u"name": u"C",
            u"status": u"C",
            u"description": u"C",
            u'all_competing_industries_published': False,
            u'white_space_competition_set': [],
            u'any_competing_industries_published': False,
            u'all_primary_industries_of_banners_published': False,
            "valid": {
                "analytics": False,
                "v1_2": {
                    "analytics": {
                        'competition': False,
                        'competitor_summary': False,
                        'monopolies': False,
                        'demographics': False,
                        'economics': False,
                        'stores': False,
                        'white_space': False
                    }
                }
            },
            u"ticker": u"C",
            u"exchange": u"C",
            u"type": u"retailer_cooperative",
            u"main_site_url": None,
            u"primary_industry": {
                u'id': self.industry_id3,
                u'label': u'c c',
                u'name': u'c',
                u'publish_competition_for_banners': False
            },
            u"published": True,
            u'last_analytics_stores_date': self.last_store_date,
            u'last_analytics_competition_date': self.last_store_date,
            u'last_analytics_economics_date': self.last_economics_date,
            u'last_store_date': self.last_store_date,
            u'last_store_count': self.last_store_count,
            u'global_stores_start_date': self.global_stores_start_date,
            u'global_stores_end_date': self.global_stores_end_date,
            u'analytics_dates': {u"monthly": {u"stores": {u"end": self.last_store_date},
                                             u"competition": {u"end": self.last_store_date},
                                             u"economics": {u"end": self.last_economics_date}}},
            u'store_collection_dates': self.store_collection_dates,
            u"family_list": [self.company_id2,
                             self.company_id3,
                             self.company_id6,
                             self.company_id23,
                             self.company_id34,
                             self.company_id100],
            u"company_hierarchy": {
                "secondary_banners": [],
                "secondary_parents": [
                    {
                        "id": self.company_id100,
                        "name": "AAA",
                        "ticker": "AAA",
                        "exchange": "AAA",
                        "primary_industry": None,
                        "published": True
                    }
                ],
                u"parents": [
                    {
                        "id": self.company_id2,
                        "name": "B",
                        "ticker": "B",
                        "exchange": "B",
                        "primary_industry": {
                            "id": self.industry_id2,
                            "name": "b",
                            "label": "b b",
                            'publish_competition_for_banners': False
                        },
                        "published": True
                    }
                ],
                u"owners": [
                    {
                        "id": self.company_id6,
                        "name": "F",
                        "ticker": "F",
                        "exchange": "F",
                        "primary_industry": None,
                        "published": True
                    }
                ],
                u"banners": [
                    {
                        "id": self.company_id34,
                        "name": "CD",
                        "ticker": "CD",
                        "exchange": "CD",
                        "primary_industry": None,
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    },
                    {
                        "id": self.company_id23,
                        "name": "BC",
                        "ticker": "BC",
                        "exchange": "BC",
                        "primary_industry": None,
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    }
                ],
                u"cooperatives": [
                    {
                        "id": self.company_id3,
                        "name": "C",
                        "ticker": "C",
                        "exchange": "C",
                        "primary_industry": {
                            "id": self.industry_id3,
                            "name": "c",
                            "label": "c c",
                            'publish_competition_for_banners': False
                        },
                        "published": True
                    }
                ]
            }
        }

        results = self.web_access.get("/api/companies/%s" % self.company_id3, "", cookies=self.cooks, time_out=9999).json()
        company_results = results["company"]
        self.__compare_results_with_expected(expected_results, company_results)

    def web_test_get_company_hierarchy_owner(self):

        create_companies_and_relationships(self)

        expected_results = {
            u"_id": self.company_id6,
            u"company_tree_ids": [self.company_id2, self.company_id6, self.company_id12, self.company_id23],
            u"name": u"F",
            u"status": u"F",
            u'all_competing_industries_published': False,
            u'white_space_competition_set': [],
            u'any_competing_industries_published': False,
            u'all_primary_industries_of_banners_published': False,
            "valid": {
                "analytics": False,
                "v1_2": {
                    "analytics": {
                        'competition': False,
                        'competitor_summary': False,
                        'monopolies': False,
                        'demographics': False,
                        'economics': False,
                        'stores': False,
                        'white_space': False
                    }
                }
            },
            u"description": u"F",
            u"ticker": u"F",
            u"exchange": u"F",
            u"type": u"retail_owner",
            u"main_site_url": None,
            u"primary_industry": None,
            u"published": True,
            u'last_analytics_stores_date': self.last_store_date,
            u'last_analytics_competition_date': self.last_store_date,
            u'last_analytics_economics_date': self.last_economics_date,
            u'last_store_date': self.last_store_date,
            u'last_store_count': self.last_store_count,
            u'global_stores_start_date': self.global_stores_start_date,
            u'global_stores_end_date': self.global_stores_end_date,
            u'analytics_dates': {u"monthly": {u"stores": {u"end": self.last_store_date},
                                             u"competition": {u"end": self.last_store_date},
                                             u"economics": {u"end": self.last_economics_date}}},
            u'store_collection_dates': self.store_collection_dates,
            u"family_list": [self.company_id2,
                             self.company_id3,
                             self.company_id6,
                             self.company_id12,
                             self.company_id23],
            u"company_hierarchy": {
                "secondary_banners": [],
                "secondary_parents": [],
                u"parents": [
                    {
                        "id": self.company_id2,
                        "name": "B",
                        "ticker": "B",
                        "exchange": "B",
                        "primary_industry": {
                            "id": self.industry_id2,
                            "name": "b",
                            "label": "b b",
                            'publish_competition_for_banners': False
                        },
                        "published": True
                    }
                ],
                u"owners": [
                    {
                        "id": self.company_id6,
                        "name": "F",
                        "ticker": "F",
                        "exchange": "F",
                        "primary_industry": None,
                        "published": True
                    }
                ],
                u"banners": [
                    {
                        "id": self.company_id12,
                        "name": "AB",
                        "ticker": "AB",
                        "exchange": "AB",
                        "primary_industry": None,
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    },
                    {
                        "id": self.company_id23,
                        "name": "BC",
                        "ticker": "BC",
                        "exchange": "BC",
                        "primary_industry": None,
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    }
                ],
                u"cooperatives": [
                    {
                        "id": self.company_id3,
                        "name": "C",
                        "ticker": "C",
                        "exchange": "C",
                        "primary_industry": {
                            "id": self.industry_id3,
                            "name": "c",
                            "label": "c c",
                            'publish_competition_for_banners': False
                        },
                        "published": True
                    }
                ]
            }
        }

        results = self.web_access.get("/api/companies/%s" % self.company_id6, "", cookies=self.cooks,
                                      time_out=9999).json()
        company_results = results["company"]
        self.__compare_results_with_expected(expected_results, company_results)

    def web_test_get_company_hierarchy_just_parent(self):

        create_companies_and_relationships_just_parent(self)

        expected_results = {
            u"_id": self.company_id1,
            u"company_tree_ids": [self.company_id1],
            u"name": u"A",
            u"status": u"A",
            u'all_competing_industries_published': False,
            u'white_space_competition_set': [],
            u'any_competing_industries_published': False,
            u'all_primary_industries_of_banners_published': False,
            "valid": {
                "analytics": False,
                "v1_2": {
                    "analytics": {
                        'competition': False,
                        'competitor_summary': False,
                        'monopolies': False,
                        'demographics': False,
                        'economics': False,
                        'stores': False,
                        'white_space': False
                    }
                }
            },
            u"description": u"A",
            u"ticker": u"A",
            u"exchange": u"A",
            u"type": u"retail_parent",
            u"main_site_url": None,
            u"primary_industry": None,
            u"published": True,
            u'last_analytics_stores_date': self.last_store_date,
            u'last_analytics_competition_date': self.last_store_date,
            u'last_analytics_economics_date': self.last_economics_date,
            u'last_store_date': self.last_store_date,
            u'last_store_count': self.last_store_count,
            u'global_stores_start_date': (LAST_ANALYTICS_DATE - relativedelta(years = 1)).strftime("%Y-%m-%dT%H:%M:%S"),
            u'global_stores_end_date': LAST_ANALYTICS_DATE.strftime("%Y-%m-%dT%H:%M:%S"),
            u'analytics_dates': {u"monthly": {u"stores": {u"end": self.last_store_date},
                                             u"competition": {u"end": self.last_store_date},
                                             u"economics": {u"end": self.last_economics_date}}},
            u'store_collection_dates': None,
            u"family_list": [self.company_id1],
            u"company_hierarchy": {
                "secondary_banners": [],
                "secondary_parents": [],
                u"parents": [
                    {
                        "id": self.company_id1,
                        "name": "A",
                        "ticker": "A",
                        "exchange": "A",
                        "primary_industry": None,
                        "published": True
                    }
                ],
                u"owners": [],
                u"banners": [],
                u"cooperatives": []
            }
        }

        results = self.web_access.get("/api/companies/%s" % self.company_id1, "", cookies=self.cooks, time_out=9999).json()
        company_results = results["company"]

        self.__compare_results_with_expected(expected_results, company_results)


    def web_test_get_company_hierarchy_just_banner(self):

        create_companies_and_relationships_just_banner(self)

        expected_results = {
            u"_id": self.company_id01,
            u"company_tree_ids": [self.company_id01],
            u"name": u"AA",
            u"status": u"AA",
            u'all_competing_industries_published': True,
            u'white_space_competition_set': [],
            u'any_competing_industries_published': True,
            u'all_primary_industries_of_banners_published': True,
            "valid": {
                "analytics": False,
                "v1_2": {
                    "analytics": {
                        'competition': False,
                        'competitor_summary': False,
                        'monopolies': False,
                        'demographics': False,
                        'economics': False,
                        'stores': False,
                        'white_space': False
                    }
                }
            },
            u"description": u"AA",
            u"ticker": u"AA",
            u"exchange": u"AA",
            u"type": u"retail_banner",
            u"main_site_url": None,
            u"primary_industry": {
                "id": self.industry_id1,
                "name": "a",
                "label": "a a",
                'publish_competition_for_banners': True
            },
            u"published": True,
            u'last_analytics_stores_date': self.last_store_date,
            u'last_analytics_competition_date': self.last_store_date,
            u'last_analytics_economics_date': self.last_economics_date,
            u'last_store_date': self.last_store_date,
            u'last_store_count': self.last_store_count,
            u'global_stores_start_date': self.global_stores_start_date,
            u'global_stores_end_date': self.global_stores_end_date,
            u'analytics_dates': {u"monthly": {u"stores": {u"end": self.last_store_date},
                                             u"competition": {u"end": self.last_store_date},
                                             u"economics": {u"end": self.last_economics_date}}},
            u'store_collection_dates': self.store_collection_dates,
            u"family_list": [self.company_id01],
            u"company_hierarchy": {
                "secondary_banners": [],
                "secondary_parents": [],
                u"parents": [],
                u"owners": [],
                u"banners": [
                    {
                        "id": self.company_id01,
                        "name": "AA",
                        "ticker": "AA",
                        "exchange": "AA",
                        "primary_industry": {
                            "id": self.industry_id1,
                            "name": "a",
                            "label": "a a",
                            'publish_competition_for_banners': True
                        },
                        "published": True,
                        u'store_collection_dates': self.store_collection_dates,
                    }
                ],
                u"cooperatives": []
            }
        }

        results = self.web_access.get("/api/companies/%s" % self.company_id01, "", cookies=self.cooks, time_out=9999).json()
        company_results = results["company"]

        self.__compare_results_with_expected(expected_results, company_results)
