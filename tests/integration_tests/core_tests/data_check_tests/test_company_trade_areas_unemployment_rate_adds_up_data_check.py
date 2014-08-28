import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.economics.company_trade_areas_unemployment_rate_adds_up_data_check import CompanyTradeAreasUnemploymentRateAddsUpDataCheck
from tests.integration_tests.core_tests.data_check_tests.data_check_test_helpers import create_trade_area


__author__ = 'vgold'


class TestCompanyTradeAreasUnemploymentRateAddsUpDataCheck(unittest.TestCase):
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
        self.mds.trade_area.drop()
        self.mds.company.drop()

        self.co1 = ObjectId()
        self.co2 = ObjectId()

        self.ta1 = ObjectId()
        self.ta2 = ObjectId()
        self.ta3 = ObjectId()

        self.companies = [
            {
                "_id": self.co1,
                "data": {
                    "type": "retail_banner",
                    "workflow": {
                        "current": {
                            "status": "published"
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
            create_trade_area(self.ta1, self.co1, 2, 2, 4, 50),
            create_trade_area(self.ta2, self.co1, 3, 0, 5, 100),
            create_trade_area(self.ta3, self.co1, 4, 2, -1, 23)
        ])

    def tearDown(self):
        pass

    def test_company_trade_areas_workforce_adds_up(self):
        self.maxDiff = None

        checker = CompanyTradeAreasUnemploymentRateAddsUpDataCheck(self.mds, self.companies[0], self.company_dict)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted([
                (str(self.ta2), 3, 5, 100),
                (str(self.ta3), 4, -1, 23)
            ])
        )

        expected = 3
        actual = 1
        percent_diff = round((expected - actual) / float(expected) * 100.0, 2)
        self.assertEqual(checker.failure_difference["percent_diff"], "%s%%" % percent_diff)

    def test_under_10_percent_tolerance(self):
        self.mds.trade_area.insert([
            create_trade_area(ObjectId(), self.co2, 2, 2, 4, 50)
            for _ in range(10)
        ] + [
            create_trade_area(ObjectId(), self.co2, 2, 2, 4, 80),
        ])

        checker = CompanyTradeAreasUnemploymentRateAddsUpDataCheck(self.mds, self.companies[1], self.company_dict)
        result = checker.check()

        self.assertTrue(result)
        self.assertEqual(len(checker.failures), 0)


if __name__ == '__main__':
    unittest.main()
