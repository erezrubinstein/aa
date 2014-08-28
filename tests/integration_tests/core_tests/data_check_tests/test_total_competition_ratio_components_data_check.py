import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client
from common.utilities.date_utilities import LAST_ANALYTICS_DATE

from core.data_checks.implementation.company_checks.competition.total_competition_ratio_components_data_check import TotalCompetitionRatioComponentsDataCheck


__author__ = 'vgold'


class TestTotalCompetitionRatioComponentsDataCheck(unittest.TestCase):

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

        test_date = LAST_ANALYTICS_DATE.isoformat()
        test_bad_date = "2014-01-01T00:00:00"

        self.co1 = ObjectId()
        self.co2 = ObjectId()
        self.co3 = ObjectId()
        self.co4 = ObjectId()
        self.co5 = ObjectId()
        self.co6 = ObjectId()
        self.co7 = ObjectId()

        self.mds.company.insert([
            {
                "_id": self.co1,
                "name": "1",
                "data": self.__form_company_analytics_dict({
                    "raw": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    },
                    "weighted": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    }
                })
            },
            {
                "_id": self.co2,
                "name": "2",
                "data": self.__form_company_analytics_dict({
                    "raw": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10.000000000000001}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    },
                    "weighted": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    }
                })
            },
            {
                "_id": self.co3,
                "name": "3",
                "data": self.__form_company_analytics_dict({
                    "raw": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 1}],
                        "secondary": [{"date": test_date, "value": 1}],
                        "cluster": [{"date": test_date, "value": 1}]
                    },
                    "weighted": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    }
                })
            },
            {
                "_id": self.co4,
                "name": "4",
                "data": self.__form_company_analytics_dict({
                    "raw": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    },
                    "weighted": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 1}],
                        "secondary": [{"date": test_date, "value": 1}],
                        "cluster": [{"date": test_date, "value": 1}]
                    }
                })
            },
            {
                "_id": self.co5,
                "name": "5",
                "data": self.__form_company_analytics_dict({
                    "raw": {
                        "total": [{"date": test_bad_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    },
                    "weighted": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    }
                })
            },
            {
                "_id": self.co6,
                "name": "6",
                "data": self.__form_company_analytics_dict({
                    "raw": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    },
                    "weighted": {
                        "total": [{"date": test_bad_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    }
                })
            },
            {
                "_id": self.co7,
                "name": "7",
                "data": self.__form_company_analytics_dict({
                    "raw": {
                        "total": [{"date": test_date, "value": 20.001}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    },
                    "weighted": {
                        "total": [{"date": test_date, "value": 20}],
                        "primary": [{"date": test_date, "value": 10}],
                        "secondary": [{"date": test_date, "value": 7}],
                        "cluster": [{"date": test_date, "value": 3}]
                    }
                })
            }
        ])

    def tearDown(self):

        self.mds.company.drop()

    def test_total_competition_ratio_components(self):

        expected_failures = {
            self.co3: ("3", self.co3),
            self.co4: ("4", self.co4),
            self.co5: ("5", self.co5),
            self.co6: ("6", self.co6),
        }

        for company in self.mds.company.find():

            checker = TotalCompetitionRatioComponentsDataCheck(self.mds, company)
            result = checker.check()

            self.assertEqual(result, not company["_id"] in expected_failures)
            if company["_id"] in expected_failures:
                self.assertEqual(checker.failures[0], expected_failures[company["_id"]])

    def __form_company_analytics_dict(self, cr_dict):

        return {
            "analytics": {
                "competition": {
                    "monthly": {
                        "DistanceMiles10": {
                            "company_competition_ratio": cr_dict
                        }
                    }
                }
            }
        }


if __name__ == '__main__':
    unittest.main()
