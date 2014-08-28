import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.competition.company_competition_ratio_data_check import CompanyCompetitionRatioDataCheck
from common.utilities.date_utilities import get_datetime_months_ago, LAST_ANALYTICS_DATE


__author__ = 'imashhor'


class TestCompanyCompetitionRatioDataCheck(unittest.TestCase):

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
        pass

    def tearDown(self):

        self.mds.company.drop()
        self.mds.company_competition_instance.drop()

    def test_good_banner_data_check__no_stores(self):

        banner_id = ObjectId()

        date_string = get_datetime_months_ago(1, start=LAST_ANALYTICS_DATE).isoformat().split('.')[0]

        bad_banner = {
            "_id": banner_id,
            "data": {
                "type": "retail_banner",
                "analytics": {
                    "stores": {
                        "monthly": {
                            "store_counts": [{"date": date_string, "value": 3}]
                        }
                    }
                }
            }
        }

        checker = CompanyCompetitionRatioDataCheck(self.mds, bad_banner)
        result = checker.check()

        self.assertTrue(result)

    def test_good_banner_data_check(self):

        good_banner_id = ObjectId()

        date_string = LAST_ANALYTICS_DATE.isoformat().split('.')[0]

        good_banner = {
            "_id": good_banner_id,
            "data": {
                "type": "retail_banner",
                "analytics": {
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "company_competition_ratio": {
                                    "raw": {
                                        "total": [{"date": date_string, "value": 14}],
                                        "primary": [{"date": date_string, "value": 5}],
                                        "secondary": [{"date": date_string, "value": 7}],
                                        "cluster": [{"date": date_string, "value": 2}]
                                    },
                                    "weighted": {
                                        "total": [{"date": date_string, "value": 7.533333}],
                                        "primary": [{"date": date_string, "value": 1.633333}],
                                        "secondary": [{"date": date_string, "value": 3.9}],
                                        "cluster": [{"date": date_string, "value": 2}]
                                    }
                                }
                            }
                        }
                    },
                    "stores": {
                        "monthly": {
                            "store_counts": [{"date": date_string, "value": 3}]
                        }
                    }
                }
            }
        }

        self.__insert_test_cci_with_company_counts(good_banner_id, good_banner_id, 1, LAST_ANALYTICS_DATE, 6, 6)
        self.__insert_test_cci_with_company_counts(good_banner_id, ObjectId(), 0.9, LAST_ANALYTICS_DATE, 10, 0.9)
        self.__insert_test_cci_with_company_counts(good_banner_id, ObjectId(), 0.8, LAST_ANALYTICS_DATE, 5, 4.0)
        self.__insert_test_cci_with_company_counts(good_banner_id, ObjectId(), 0.6, LAST_ANALYTICS_DATE, 12, 7.2)
        self.__insert_test_cci_with_company_counts(good_banner_id, ObjectId(), 0.5, LAST_ANALYTICS_DATE, 9, 4.5)

        checker = CompanyCompetitionRatioDataCheck(self.mds, good_banner)
        result = checker.check()

        self.assertTrue(result)

    def test_bad_banner_data_check__values_dont_add_up(self):

        bad_banner_id = ObjectId()

        date_string = LAST_ANALYTICS_DATE.isoformat().split('.')[0]

        bad_banner = {
            "_id": bad_banner_id,
            "data": {
                "type": "retail_banner",
                "analytics": {
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "company_competition_ratio": {
                                    "raw": {
                                        "total": [{"date": date_string, "value": 13}],
                                        "primary": [{"date": date_string, "value": 5}],
                                        "secondary": [{"date": date_string, "value": 7}],
                                        "cluster": [{"date": date_string, "value": 2}]
                                    },
                                    "weighted": {
                                        "total": [{"date": date_string, "value": 7.533333}],
                                        "primary": [{"date": date_string, "value": 1.633333}],
                                        "secondary": [{"date": date_string, "value": 3.9}],
                                        "cluster": [{"date": date_string, "value": 2}]
                                    }
                                }
                            }
                        }
                    },
                    "stores": {
                        "monthly": {
                            "store_counts": [{"date": date_string, "value": 3}]
                        }
                    }
                }
            }
        }

        self.__insert_test_cci_with_company_counts(bad_banner_id, bad_banner_id, 1, LAST_ANALYTICS_DATE, 6, 6)
        self.__insert_test_cci_with_company_counts(bad_banner_id, ObjectId(), 0.9, LAST_ANALYTICS_DATE, 10, 0.9)
        self.__insert_test_cci_with_company_counts(bad_banner_id, ObjectId(), 0.8, LAST_ANALYTICS_DATE, 5, 4.0)
        self.__insert_test_cci_with_company_counts(bad_banner_id, ObjectId(), 0.6, LAST_ANALYTICS_DATE, 12, 7.2)
        self.__insert_test_cci_with_company_counts(bad_banner_id, ObjectId(), 0.5, LAST_ANALYTICS_DATE, 9, 4.5)

        checker = CompanyCompetitionRatioDataCheck(self.mds, bad_banner)
        result = checker.check()

        self.assertFalse(result)

    def test_bad_banner_data_check__bad_dates(self):

        bad_banner_id = ObjectId()

        date_string = LAST_ANALYTICS_DATE.isoformat().split('.')[0]
        old_date_string = get_datetime_months_ago(1, start=LAST_ANALYTICS_DATE).isoformat().split('.')[0]

        bad_banner = {
            "_id": bad_banner_id,
            "data": {
                "type": "retail_banner",
                "analytics": {
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "company_competition_ratio": {
                                    "raw": {
                                        "total": [{"date": old_date_string, "value": 14}],
                                        "primary": [{"date": old_date_string, "value": 5}],
                                        "secondary": [{"date": old_date_string, "value": 7}],
                                        "cluster": [{"date": old_date_string, "value": 2}]
                                    },
                                    "weighted": {
                                        "total": [{"date": old_date_string, "value": 7.533333}],
                                        "primary": [{"date": old_date_string, "value": 1.633333}],
                                        "secondary": [{"date": old_date_string, "value": 3.9}],
                                        "cluster": [{"date": old_date_string, "value": 2}]
                                    }
                                }
                            }
                        }
                    },
                    "stores": {
                        "monthly": {
                            "store_counts": [{"date": date_string, "value": 3}]
                        }
                    }
                }
            }
        }

        self.__insert_test_cci_with_company_counts(bad_banner_id, bad_banner_id, 1, LAST_ANALYTICS_DATE, 6, 6)
        self.__insert_test_cci_with_company_counts(bad_banner_id, ObjectId(), 0.9, LAST_ANALYTICS_DATE, 10, 0.9)
        self.__insert_test_cci_with_company_counts(bad_banner_id, ObjectId(), 0.8, LAST_ANALYTICS_DATE, 5, 4.0)
        self.__insert_test_cci_with_company_counts(bad_banner_id, ObjectId(), 0.6, LAST_ANALYTICS_DATE, 12, 7.2)
        self.__insert_test_cci_with_company_counts(bad_banner_id, ObjectId(), 0.5, LAST_ANALYTICS_DATE, 9, 4.5)

        checker = CompanyCompetitionRatioDataCheck(self.mds, bad_banner)
        result = checker.check()

        self.assertFalse(result)

    def __insert_test_cci_with_company_counts(self, from_id, to_id, competition_strength, date, raw_value,
                                              weighted_value):
        self.mds.company_competition_instance.insert({
            "_id": ObjectId(),
            "data": {
                "pair": {
                    "entity_id_from": from_id,
                    "entity_id_to": to_id,
                    "data": {
                        "competition_strength": competition_strength
                    }
                },
                "analytics": self.__form_company_analytics_dict(date, raw_value, weighted_value)
            }
        })

    def __form_company_analytics_dict(self, date, raw_value, weighted_value):
        return {
            "competition": {
                "monthly": {
                    "DistanceMiles10": {
                        "competition_instances": {
                            "counts": {
                                "raw": [
                                    {
                                        "date": date.isoformat().split(".", 1)[0],
                                        "value": raw_value
                                    }
                                ],
                                "weighted": [
                                    {
                                        "date": date.isoformat().split(".", 1)[0],
                                        "value": weighted_value
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }


if __name__ == '__main__':
    unittest.main()
