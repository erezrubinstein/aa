import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.economics.company_unemployment_distribution_matches_store_count_data_check import CompanyUnemploymentDistributionMatchesStoreCountDataCheck
from common.utilities.date_utilities import LAST_ECONOMICS_DATE


__author__ = 'vgold'


class TestCompanyUnemploymentDistributionMatchesStoreCountDataCheck(unittest.TestCase):

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

        self.co1 = ObjectId()
        self.co2 = ObjectId()
        self.co3 = ObjectId()

        self.ta1 = ObjectId()
        self.ta2 = ObjectId()
        self.ta3 = ObjectId()
        self.ta4 = ObjectId()
        self.ta5 = ObjectId()
        self.ta6 = ObjectId()
        self.ta7 = ObjectId()
        self.ta8 = ObjectId()
        self.ta9 = ObjectId()
        self.ta10 = ObjectId()
        self.ta11 = ObjectId()
        self.ta12 = ObjectId()
        self.ta13 = ObjectId()
        self.ta14 = ObjectId()
        self.ta15 = ObjectId()
        self.ta16 = ObjectId()
        self.ta17 = ObjectId()


        self.companies = [
            {
                "_id": self.co1,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {
                            "status": "published"
                        }
                    },
                    "analytics": {
                        "stores": {
                            "monthly": {
                                "store_counts": [
                                    {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 3}
                                ]
                            }
                        }
                    }
                }
            },
            {
                "_id": self.co2,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {
                            "status": "published"
                        }
                    },
                    "analytics": {
                        "stores": {
                            "monthly": {
                                "store_counts": [
                                    {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 12}
                                ]
                            }
                        }
                    }
                }
            },
            {
                "_id": self.co3,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {
                            "status": "published"
                        }
                    },
                    "analytics": {
                        "stores": {
                            "monthly": {
                                "store_counts": [
                                    {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 3}
                                ]
                            }
                        }
                    }
                }
            }
        ]

        self.company_dict = {
            str(co["_id"])
            for co in self.companies
        }

        self.mds.company.insert(self.companies)

        self.mds.trade_area.insert([
            # COMPANY 1 -------------------------------------
            {
                "_id": self.ta1,
                "interval": [None, None],
                "data": { "company_id": str(self.co1) }
            },
            {
                "_id": self.ta2,
                "interval": [None, None],
                "data": { "company_id": str(self.co1) }
            },
            {
                "_id": self.ta3,
                "interval": [None, None],
                "data": { "company_id": str(self.co1) }
            },
            # COMPANY 2 -------------------------------------
            {
                "_id": self.ta4,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta5,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta6,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta7,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta8,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta9,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta10,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta11,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta12,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta13,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta14,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            {
                "_id": self.ta15,
                "interval": [None, None],
                "data": { "company_id": str(self.co2) }
            },
            # COMPANY 3 -------------------------------------
            {
                "_id": self.ta16,
                "interval": [None, None],
                "data": { "company_id": str(self.co3) }
            },
            {
                "_id": self.ta17,
                "interval": [None, None],
                "data": { "company_id": str(self.co3) }
            }
        ])

        company_analytics = [
            {
                "data": {
                    "company_id": str(self.co1),
                    "engine": "economics",
                    "date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0],
                    "analytics": {
                        "aggregate_trade_area_unemployment_rate": [1, 2, 3]
                    }
                }
            },
            {
                "data": {
                    "company_id": str(self.co2),
                    "engine": "economics",
                    "date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0],
                    "analytics": {
                        "aggregate_trade_area_unemployment_rate": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    }
                }
            },
            {
                "data": {
                    "company_id": str(self.co3),
                    "engine": "economics",
                    "date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0],
                    "analytics": {
                        "aggregate_trade_area_unemployment_rate": [1, 2, 3]
                    }
                }
            }
        ]

        self.mds.company_analytics.insert(company_analytics)

    def tearDown(self):

        self.mds.trade_area.drop()
        self.mds.company.drop()
        self.mds.company_analytics.drop()

    def test_company_unemployment_distribution_matches_store_count(self):

        checker = CompanyUnemploymentDistributionMatchesStoreCountDataCheck(self.mds, self.companies[0], self.company_dict)
        result = checker.check()

        self.assertTrue(result)
        self.assertEqual(checker.results, (3, 3, 3))

        checker = CompanyUnemploymentDistributionMatchesStoreCountDataCheck(self.mds, self.companies[1], self.company_dict)
        result = checker.check()

        self.assertFalse(result)
        self.assertEqual(checker.results, (12, 12, 10))

        checker = CompanyUnemploymentDistributionMatchesStoreCountDataCheck(self.mds, self.companies[2], self.company_dict)
        result = checker.check()

        # companies off-by-one with very small counts should NOT be ok
        self.assertFalse(result)
        self.assertEqual(checker.results, (3, 2, 3))

        # off by more than one should fail, so remove one of company 3's trade areas
        self.mds.trade_area.remove({"_id": self.ta17})
        checker = CompanyUnemploymentDistributionMatchesStoreCountDataCheck(self.mds, self.companies[2], self.company_dict)
        result = checker.check()

        self.assertFalse(result)
        self.assertEqual(checker.results, (3, 1, 3))


if __name__ == '__main__':
    unittest.main()
