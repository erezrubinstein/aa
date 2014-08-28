import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.economics.company_trade_areas_missing_labor_data_check import CompanyTradeAreasMissingLaborDataCheck
from common.utilities.date_utilities import LAST_ANALYTICS_DATE, LAST_ECONOMICS_DATE, get_start_date_of_next_month


__author__ = 'vgold'


class TestCompanyTradeAreasMissingLaborDataCheck(unittest.TestCase):

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

        self.ta1 = ObjectId()
        self.ta2 = ObjectId()
        self.ta3 = ObjectId()
        self.ta4 = ObjectId()
        self.ta5 = ObjectId()
        self.ta6 = ObjectId()
        self.ta7 = ObjectId()
        self.ta8 = ObjectId()

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
                                    {"date": LAST_ECONOMICS_DATE.isoformat().split(".", 1)[0], "value": 1}
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

        good_date = LAST_ECONOMICS_DATE
        bad_date = get_start_date_of_next_month(LAST_ECONOMICS_DATE)

        self.mds.trade_area.insert([
            {
                "_id": self.ta1,
                "interval": None,
                "data": {
                    "street_number": 123,
                    "street": "Main St",
                    "suite": "Suite 1A",
                    "city": "Anytown",
                    "state": "BA",
                    "zip": "45666",
                    "company_id": str(self.co1),
                    "analytics": self.__add_labor_analytics(good_date, skip_key="area_type")
                }
            },
            {
                "_id": self.ta2,
                "interval": [None, None],
                "data": {
                    "street_number": 456,
                    "street": "Two St",
                    "suite": None,
                    "city": "Anytown",
                    "state": "AR",
                    "company_id": str(self.co1),
                    "analytics": self.__add_labor_analytics(good_date, skip_key="area_text")
                }
            },
            {
                "_id": self.ta3,
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "analytics": self.__add_labor_analytics(good_date, skip_key="unemployment")
                }
            },
            {
                "_id": self.ta4,
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "analytics": self.__add_labor_analytics(good_date, skip_key="employment")
                }
            },
            {
                "_id": self.ta5,
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "analytics": self.__add_labor_analytics(good_date, skip_key="unemployment rate")
                }
            },
            {
                "_id": self.ta6,
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "analytics": self.__add_labor_analytics(good_date, skip_key="labor force")
                }
            },
            {
                "_id": self.ta7,
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "analytics": self.__add_labor_analytics(bad_date)
                }
            },
            {
                "_id": self.ta8,
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "analytics": self.__add_labor_analytics(good_date)
                }
            }
        ])

    def tearDown(self):

        self.mds.trade_area.drop()
        self.mds.company.drop()

    def test_company_trade_areas_missing_labor_data(self):

        checker = CompanyTradeAreasMissingLaborDataCheck(self.mds, self.companies[0], self.company_dict)
        result = checker.check()

        def tostring(ta):
            if ta == self.ta1:
                return "TA %s: \"123 Main St Suite 1A, Anytown, BA, 45666\"" % ta
            elif ta == self.ta2:
                return 'TA %s: "456 Two St , Anytown, AR, None"' % ta
            return "TA %s: \"None None , None, None, None\"" % ta

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted(map(tostring, [self.ta1, self.ta2, self.ta3, self.ta4, self.ta5, self.ta6, self.ta7]))
        )

    def __add_labor_analytics(self, date, skip_key=None):

        date_string = date.isoformat().split(".", 1)[0]

        data = {
            "economics": {
                "area_type": "C",
                "area_text": "Anytown, UT",
                "monthly": {
                    "unemployment": [{"date": date_string, "value": 1234}],
                    "unemployment rate": [{"date": date_string, "value": 1234}],
                    "employment": [{"date": date_string, "value": 1234}],
                    "labor force": [{"date": date_string, "value": 1234}],
                }
            }
        }

        if skip_key is not None:
            if skip_key in data["economics"].keys():
                del data["economics"][skip_key]

            elif skip_key in data["economics"]["monthly"].keys():
                del data["economics"]["monthly"][skip_key]

        return data


if __name__ == '__main__':
    unittest.main()
