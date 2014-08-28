import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.economics.company_trade_areas_mean_unemployment_rate_data_check import CompanyTradeAreasMeanUnemploymentRateDataCheck
from tests.integration_tests.core_tests.data_check_tests.data_check_test_helpers import create_trade_area
from common.utilities.date_utilities import LAST_ECONOMICS_DATE


__author__ = 'vgold'


class TestCompanyTradeAreasMeanUnemploymentRateDataCheck(unittest.TestCase):
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

        self.ta21 = ObjectId()
        self.ta22 = ObjectId()
        self.ta23 = ObjectId()

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
                        },
                        "economics": {
                            "monthly": {
                                "DistanceMiles10": {
                                    "aggregate_trade_area_unemployment_rate": {
                                        "mean": [
                                            {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 70.0}
                                        ]
                                    }
                                }
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
            create_trade_area(self.ta21, self.co1, 8, 2, 10, 80),
            create_trade_area(self.ta22, self.co1, 8, 2, 10, 80),
            create_trade_area(self.ta23, self.co1, 8, 2, 10, 80)
        ])

    def tearDown(self):
        pass

    def test_company_mean_unemployment_rate(self):
        checker = CompanyTradeAreasMeanUnemploymentRateDataCheck(self.mds, self.companies[0], self.company_dict)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            checker.failures,
            (80.0, 70.0)
        )

        expected = 80.0
        actual = 70.0
        percent_diff = round((expected - actual) / float(expected) * 100.0, 2)
        self.assertEqual(checker.failure_difference["percent_diff"], "%s%%" % percent_diff)


if __name__ == '__main__':
    unittest.main()
