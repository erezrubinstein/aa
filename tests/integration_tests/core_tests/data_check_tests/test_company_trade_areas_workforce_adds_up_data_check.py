import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.economics.company_trade_areas_workforce_adds_up_data_check import CompanyTradeAreasWorkforceAddsUpDataCheck
from tests.integration_tests.core_tests.data_check_tests.data_check_test_helpers import create_trade_area
from common.utilities.date_utilities import LAST_ECONOMICS_DATE, get_datetime_months_ago, get_start_date_of_next_month


__author__ = 'vgold'


class TestCompanyTradeAreasWorkforceAddsUpDataCheck(unittest.TestCase):
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

        self.ta21 = ObjectId()
        self.ta22 = ObjectId()
        self.ta23 = ObjectId()
        self.ta24 = ObjectId()

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
                    },
                    "analytics": {
                        "stores": {
                            "monthly": {
                                "store_counts": [
                                    {"date": get_datetime_months_ago(3, start=LAST_ECONOMICS_DATE).isoformat().split(".", 1)[0], "value": 3}
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
            create_trade_area(self.ta1, self.co1, 2, 2, 4),
            create_trade_area(self.ta2, self.co1, 2, 2, 6),
            create_trade_area(self.ta3, self.co1, 2, 2, 1),
            create_trade_area(self.ta4, self.co1, 2, 2, 5, store_closed_date=LAST_ECONOMICS_DATE),
            create_trade_area(self.ta5, self.co1, 2, 2, 5, store_opened_date=get_start_date_of_next_month(LAST_ECONOMICS_DATE)),

            create_trade_area(self.ta21, self.co2, 4, 4, 8, store_closed_date=get_datetime_months_ago(2, start=LAST_ECONOMICS_DATE)),
            create_trade_area(self.ta22, self.co2, 4, 4, 8, store_opened_date=get_datetime_months_ago(3, start=LAST_ECONOMICS_DATE)),
            create_trade_area(self.ta23, self.co2, 4, 4, 8, store_closed_date=get_datetime_months_ago(3, start=LAST_ECONOMICS_DATE)),
            create_trade_area(self.ta24, self.co2, 4, 4, 8, store_opened_date=get_datetime_months_ago(2, start=LAST_ECONOMICS_DATE))
        ])

    def tearDown(self):
        pass

    def test_company_trade_areas_workforce_adds_up(self):
        self.maxDiff = None

        checker = CompanyTradeAreasWorkforceAddsUpDataCheck(self.mds, self.companies[0], self.company_dict)
        result = checker.check()

        self.assertFalse(result)

        expected_results = [
            (str(self.ta2), 2, 2, 6),
            (str(self.ta3), 2, 2, 1)
        ]

        self.assertEqual(
            sorted(checker.failures),
            sorted(expected_results)
        )

        expected = 5
        actual = 1
        percent_diff = round(2.0 / 5.0 * 100.0, 2)
        self.assertEqual(checker.failure_difference["percent_diff"], "%s%%" % percent_diff)

    def test_company_trade_areas_workforce_adds_up__old_last_store_date(self):
        self.maxDiff = None

        checker = CompanyTradeAreasWorkforceAddsUpDataCheck(self.mds, self.companies[1], self.company_dict)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted([
                #(str(self.ta23), "--", "--", "--"),
                (str(self.ta24), None, None, None)
            ])
        )

        expected = 4
        actual = 2
        percent_diff = round(1.0 / 4.0 * 100.0, 2)
        self.assertEqual(checker.failure_difference["percent_diff"], "%s%%" % percent_diff)


if __name__ == '__main__':
    unittest.main()
