import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.economics.company_trade_areas_out_of_bounds_unemployment_rate_data_check import CompanyTradeAreasOutOfBoundsUnemploymentRateDataCheck
from tests.integration_tests.core_tests.data_check_tests.data_check_test_helpers import create_trade_area
from common.utilities.date_utilities import LAST_ECONOMICS_DATE


__author__ = 'vgold'


class TestCompanyTradeAreasOutOfBoundsUnemploymentRateDataCheck(unittest.TestCase):
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
        self.ta4 = ObjectId()
        self.ta5 = ObjectId()
        self.ta6 = ObjectId()
        self.ta7 = ObjectId()
        self.ta8 = ObjectId()
        self.ta9 = ObjectId()

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
                                    {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 11}
                                ]
                            }
                        },
                        "economics": {
                            "monthly": {
                                "DistanceMiles10": {
                                    "aggregate_trade_area_unemployment_rate": {
                                        "mean": [
                                            {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 50.0}
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
            create_trade_area(self.ta1, self.co1, 2, 2, 4, 50),
            create_trade_area(self.ta2, self.co1, 3, 0, 5),
            create_trade_area(self.ta3, self.co1, 4, 2, -1),
            create_trade_area(self.ta4, self.co1, 4, 4, 8, timeseries_offset=1),
            create_trade_area(self.ta5, self.co1, 4, 4, 8, 70),
            create_trade_area(self.ta6, self.co1, 4, 4, 8, 120),
            create_trade_area(self.ta7, self.co1, 4, 4, 8, 50, state="AK"),
            create_trade_area(self.ta8, self.co1, 9, 1, 10, 90),
            create_trade_area(self.ta9, self.co1, 8, 2, 10, 80, override_length=50)
        ])

        self.extra_data = {
            "min_unemployment_rate": 1,
            "max_unemployment_rate": 85
        }

    def tearDown(self):
        pass

    def test_company_trade_areas_workforce_adds_up(self):
        self.maxDiff = None

        checker = CompanyTradeAreasOutOfBoundsUnemploymentRateDataCheck(self.mds, self.companies[0], self.company_dict,
                                                            self.extra_data)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted([
                (str(self.ta2), 0, 1, 85),
                (str(self.ta3), 0, 1, 85),
                (str(self.ta4), None, 1, 85),
                (str(self.ta6), 120, 1, 85),
                (str(self.ta8), 90, 1, 85)
            ])
        )

        expected = 9
        actual = 4
        percent_diff = round((expected - actual) / float(expected) * 100.0, 2)
        self.assertEqual(checker.failure_difference["percent_diff"], "%s%%" % percent_diff)

    def test_under_10_percent_tolerance(self):
        self.mds.trade_area.insert([
            create_trade_area(ObjectId(), self.co2, 2, 2, 4, 50)
            for _ in range(10)
        ] + [
            create_trade_area(ObjectId(), self.co2, 2, 2, 4, 81),
        ])

        checker = CompanyTradeAreasOutOfBoundsUnemploymentRateDataCheck(self.mds, self.companies[1], self.company_dict,
                                                            self.extra_data)
        result = checker.check()

        self.assertTrue(result)
        self.assertEqual(len(checker.failures), 0)


if __name__ == '__main__':
    unittest.main()
