import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.economics.company_trade_areas_economics_time_series_length_data_check import CompanyTradeAreasEconomicsTimeSeriesLengthDataCheck
from tests.integration_tests.core_tests.data_check_tests.data_check_test_helpers import create_trade_area, create_time_series
from common.utilities.date_utilities import *


__author__ = 'vgold'


class TestCompanyTradeAreasEconomicsTimeSeriesLengthDataCheck(unittest.TestCase):
    conn = None
    mds = None

    @classmethod
    def setUpClass(cls):
        cls.conn = mongo_client.MongoClient("localhost", 27017)
        cls.mds = cls.conn["itest_mds"]
        cls.date_parser = FastDateParser()

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
                                    {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 3}
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
                                    {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 11}
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

        self.ts = create_time_series(LAST_ECONOMICS_DATE, ECONOMICS_START_DATE, 0)
        self.mds.econ.insert({"ZCTA5": 11111, "measure_text":"employment", "timeseries": self.ts})

    def tearDown(self):
        pass

    def test_company_trade_areas_workforce_adds_up(self):
        self.maxDiff = None

        checker = CompanyTradeAreasEconomicsTimeSeriesLengthDataCheck(self.mds, self.companies[0], self.company_dict, date_parser=self.date_parser)
        result = checker.check()

        self.assertFalse(result)

        proper_time_series_length = len(self.ts)

        self.assertEqual(
            sorted(checker.failures),
            sorted([
                (str(self.ta4), proper_time_series_length, proper_time_series_length-1),
                (str(self.ta9), proper_time_series_length, 50)
            ])
        )

        expected = 9
        actual = 7
        percent_diff = round((expected - actual) / float(expected) * 100.0, 2)
        self.assertEqual(checker.failure_difference["percent_diff"], "%s%%" % percent_diff)

    def test_under_10_percent_tolerance(self):
        self.mds.trade_area.insert([
            create_trade_area(ObjectId(), self.co3, 2, 2, 4, 50)
            for _ in range(10)
        ] + [
            create_trade_area(ObjectId(), self.co3, 8, 2, 10, 80, override_length=50)
        ])

        checker = CompanyTradeAreasEconomicsTimeSeriesLengthDataCheck(self.mds, self.companies[2], self.company_dict, date_parser=self.date_parser)
        result = checker.check()

        self.assertTrue(result)
        self.assertEqual(len(checker.failures), 0)


if __name__ == '__main__':
    unittest.main()
