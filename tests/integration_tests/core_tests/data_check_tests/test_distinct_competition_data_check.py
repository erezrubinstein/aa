import pprint
import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.competition.distinct_competition_data_check import DistinctCompetitionDataCheck
from common.utilities.date_utilities import LAST_ANALYTICS_DATE, get_datetime_months_ago


__author__ = 'vgold'


class TestDistinctCompetitionDataCheck(unittest.TestCase):

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

        self.co0 = ObjectId()
        self.co1 = ObjectId()
        self.co2 = ObjectId()
        self.co3 = ObjectId()

        self.company_dict = {
            str(self.co0): None,
            str(self.co1): None,
            str(self.co2): None,
            str(self.co3): None
        }

        self.parent = {
            "_id": self.co0,
            "data": {
                "type": "retail_parent",
                "status": "operating",
                "workflow": {
                    "current": {
                        "status": "published"
                    }
                },
                "analytics": {
                    "stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value": 1}]}},
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [{"date": LAST_ANALYTICS_DATE, "value": 3}],
                                    "primary": [{"date": LAST_ANALYTICS_DATE, "value": 3}],
                                    "secondary": [{"date": LAST_ANALYTICS_DATE, "value": 1}],
                                    "cluster": [{"date": LAST_ANALYTICS_DATE, "value": 2}]
                                }
                            }
                        }
                    }
                }
            },
            "links": {
                "company": {
                    "retailer_branding": [
                        {
                            "entity_id_to": self.co1,
                            "entity_role_to": "retail_segment"
                        },
                        {
                            "entity_id_to": self.co2,
                            "entity_role_to": "retail_segment"
                        }
                    ]
                }
            }
        }

        self.banner1 = {
            "_id": self.co1,
            "data": {
                "type": "retail_banner",
                "status": "operating",
                "workflow": {
                    "current": {
                        "status": "published"
                    }
                },
                "analytics": {
                    "stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value": 1}]}},
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [{"date": LAST_ANALYTICS_DATE, "value": 3}],
                                    "primary": [{"date": LAST_ANALYTICS_DATE, "value": 2}],
                                    "secondary": [{"date": LAST_ANALYTICS_DATE, "value": 0}],
                                    "cluster": [{"date": LAST_ANALYTICS_DATE, "value": 1}]
                                }
                            }
                        }
                    }
                }
            }
        }

        self.banner2 = {
            "_id": self.co2,
            "data": {
                "type": "retail_banner",
                "status": "operating",
                "workflow": {
                    "current": {
                        "status": "published"
                    }
                },
                "analytics": {
                    "stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value": 1}]}},
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [{"date": LAST_ANALYTICS_DATE, "value": 3}],
                                    "primary": [{"date": LAST_ANALYTICS_DATE, "value": 1}],
                                    "secondary": [{"date": LAST_ANALYTICS_DATE, "value": 1}],
                                    "cluster": [{"date": LAST_ANALYTICS_DATE, "value": 1}]
                                }
                            }
                        }
                    }
                }
            }
        }

        self.mds.company_competition_instance.insert([
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co1,
                        "entity_id_to": self.co1,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co1,
                        "entity_id_to": self.co2,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co1,
                        "entity_id_to": self.co3,
                        "data": {
                            "competition_strength": 0.75
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co2,
                        "entity_id_to": self.co1,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co2,
                        "entity_id_to": self.co2,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co2,
                        "entity_id_to": self.co3,
                        "data": {
                            "competition_strength": 0.2
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co3,
                        "entity_id_to": self.co1,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co3,
                        "entity_id_to": self.co2,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co3,
                        "entity_id_to": self.co3,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            }
        ])

    def tearDown(self):

        self.mds.company.drop()
        self.mds.company_competition_instance.drop()

    def test_distinct_competition__banner(self):
        
        checker = DistinctCompetitionDataCheck(self.mds, self.banner1, self.company_dict)
        result = checker.check()

        self.assertTrue(result)

    def test_distinct_competition__banner__bad_values(self):

        co4 = ObjectId()

        banner4 = {
            "_id": co4,
            "data": {
                "type": "retail_banner",
                "status": "operating",
                "workflow": {
                    "current": {
                        "status": "published"
                    }
                },
                "analytics": {
                    "stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value": 1}]}},
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [{"date": LAST_ANALYTICS_DATE, "value": 3}],
                                    "primary": [{"date": LAST_ANALYTICS_DATE, "value": 1}],
                                    "secondary": [{"date": LAST_ANALYTICS_DATE, "value": 0}],
                                    "cluster": [{"date": LAST_ANALYTICS_DATE, "value": 1}]
                                }
                            }
                        }
                    }
                }
            }
        }

        self.company_dict[str(co4)] = None

        self.mds.company_competition_instance.insert([
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co4,
                        "entity_id_to": self.co1,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co4,
                        "entity_id_to": self.co2,
                        "data": {
                            "competition_strength": 0.3
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co4,
                        "entity_id_to": co4,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            }
        ])

        checker = DistinctCompetitionDataCheck(self.mds, banner4, self.company_dict)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted([
                ("Secondary", 0, 1)
            ])
        )

    def test_distinct_competition__banner__bad_dates(self):

        co4 = ObjectId()
        month = get_datetime_months_ago(1, start=LAST_ANALYTICS_DATE)

        banner4 = {
            "_id": co4,
            "data": {
                "type": "retail_banner",
                "status": "operating",
                "workflow": {
                    "current": {
                        "status": "published"
                    }
                },
                "analytics": {
                    "stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value": 1}]}},
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [{"date": month, "value": 3}],
                                    "primary": [{"date": month, "value": 1}],
                                    "secondary": [{"date": month, "value": 0}],
                                    "cluster": [{"date": month, "value": 1}]
                                }
                            }
                        }
                    }
                }
            }
        }

        self.company_dict[str(co4)] = None

        self.mds.company_competition_instance.insert([
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co4,
                        "entity_id_to": self.co1,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co4,
                        "entity_id_to": self.co2,
                        "data": {
                            "competition_strength": 0.3
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co4,
                        "entity_id_to": co4,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            }
        ])

        checker = DistinctCompetitionDataCheck(self.mds, banner4, self.company_dict)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted([
                ("Total", 0, 3),
                ("Primary", 0, 1),
                ("Secondary", 0, 1),
                ("Cluster", 0, 1)
            ])
        )

    def test_distinct_competition__parent__good(self):

        checker = DistinctCompetitionDataCheck(self.mds, self.parent, self.company_dict)
        result = checker.check()

        self.assertTrue(result)

    def test_distinct_competition__parent__bad(self):

        pid2 = ObjectId()
        co3 = ObjectId()

        self.company_dict[str(co3)] = None

        parent = {
            "_id": pid2,
            "data": {
                "type": "retail_parent",
                "status": "operating",
                "workflow": {
                    "current": {
                        "status": "published"
                    }
                },
                "analytics": {
                    "stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value": 1}]}},
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [{"date": LAST_ANALYTICS_DATE, "value": 3}],
                                    "primary": [{"date": LAST_ANALYTICS_DATE, "value": 1}],
                                    "secondary": [{"date": LAST_ANALYTICS_DATE, "value": 0}],
                                    "cluster": [{"date": LAST_ANALYTICS_DATE, "value": 1}]
                                }
                            }
                        }
                    }
                }
            },
            "links": {
                "company": {
                    "retailer_branding": [
                        {
                            "entity_id_to": co3,
                            "entity_role_to": "retail_segment"
                        }
                    ]
                }
            }
        }

        self.mds.company_competition_instance.insert([
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co3,
                        "entity_id_to": self.co1,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co3,
                        "entity_id_to": self.co2,
                        "data": {
                            "competition_strength": 0.3
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": co3,
                        "entity_id_to": co3,
                        "data": {
                            "competition_strength": 1.0
                        }
                    },
                    "analytics": self.__form_company_analytics_dict(LAST_ANALYTICS_DATE, 1)
                }
            }
        ])

        checker = DistinctCompetitionDataCheck(self.mds, parent, self.company_dict)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted([
                ("Secondary", 0, 1)
            ])
        )

    def __form_company_analytics_dict(self, date, value):

        return {
            "competition": {
                "monthly": {
                    "DistanceMiles10": {
                        "distinct_away_store_counts": [
                            {
                                "date": date.isoformat().split(".", 1)[0],
                                "value": value
                            }
                        ]
                    }
                }
            }
        }


if __name__ == '__main__':
    unittest.main()
