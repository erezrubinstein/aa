import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.competition.company_away_stores_vs_trade_area_competitive_stores_data_check import CompanyAwayStoresVsTradeAreaCompetitiveStoresDataCheck
from common.utilities.date_utilities import START_OF_WORLD, END_OF_WORLD, LAST_ANALYTICS_DATE, FastDateParser


__author__ = 'vgold'


class TestCompanyAwayStoresVsTradeAreaCompetitiveStoresDataCheck(unittest.TestCase):

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

        self.co1 = ObjectId()
        self.co2 = ObjectId()
        self.co3 = ObjectId()
        self.co4 = ObjectId()
        self.co5 = ObjectId()
        self.co6 = ObjectId()
        self.co7 = ObjectId()

        self.store20 = ObjectId()
        self.store21 = ObjectId()
        self.store22 = ObjectId()
        self.store30 = ObjectId()
        self.store31 = ObjectId()
        self.store32 = ObjectId()
        self.store38 = ObjectId()
        self.store39 = ObjectId()
        self.store50 = ObjectId()
        self.store60 = ObjectId()

        self.cci1 = ObjectId()
        self.cci2 = ObjectId()
        self.cci3 = ObjectId()
        self.cci4 = ObjectId()

        companies = [
            {
                "_id": self.co1,
                "data": {
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
                    "workflow": {
                        "current": {
                            "status": "published"
                        }
                    }
                }
            },
            {
                "_id": self.co3,
                "data": {
                    "workflow": {
                        "current": {
                            "status": "published"
                        }
                    }
                }
            },
            {
                "_id": self.co4,
                "data": {
                    "workflow": {
                        "current": {
                            "status": "published"
                        }
                    }
                }
            },
            {
                "_id": self.co5,
                "data": {
                    "workflow": {
                        "current": {
                            "status": "published"
                        }
                    }
                }
            },
            {
                "_id": self.co7,
                "data": {
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
            for co in companies
        }

        self.mds.company.insert(companies)
        self.mds.company.insert(
            {
                "_id": self.co6,
                "data": {
                    "workflow": {
                        "current": {
                            "status": "new"
                        }
                    }
                }
            }
        )

        self.mds.trade_area.insert([
            {
                "_id": ObjectId(),
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "competitive_stores": [
                        {
                            "away_company_id": self.co2,
                            "away_store_id": self.store20,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        },
                        {
                            "away_company_id": self.co3,
                            "away_store_id": self.store30,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        },
                        {
                            "away_company_id": self.co3,
                            "away_store_id": self.store31,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        },
                        {
                            "away_company_id": self.co3,
                            "away_store_id": self.store38,
                            "start_date": START_OF_WORLD,
                            "end_date": START_OF_WORLD
                        },
                        {
                            "away_company_id": self.co3,
                            "away_store_id": self.store39,
                            "start_date": END_OF_WORLD,
                            "end_date": END_OF_WORLD
                        }
                    ]
                }
            },
            {
                "_id": ObjectId(),
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "competitive_stores": [
                        {
                            "away_company_id": self.co2,
                            "away_store_id": self.store21,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        },
                        {
                            "away_company_id": self.co2,
                            "away_store_id": self.store22,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        },
                        {
                            "away_company_id": self.co3,
                            "away_store_id": self.store31,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        },
                        {
                            "away_company_id": self.co3,
                            "away_store_id": self.store32,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        }
                    ]
                }
            },
            {
                "_id": ObjectId(),
                "interval": [END_OF_WORLD, END_OF_WORLD],
                "data": {
                    "competitive_stores": [
                        {
                            "away_company_id": self.co3,
                            "away_store_id": self.store32,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        }
                    ]
                }
            }
        ])

        self.mds.company_competition_instance.insert([
            {
                "_id": self.cci1,
                "data": {
                    "pair": {
                        "entity_id_from": self.co1,
                        "entity_id_to": self.co2
                    },
                    "from": {
                        "name": "1"
                    },
                    "to": {
                        "name": "2"
                    },
                    "analytics": {
                        "competition": {
                            "monthly": {
                                "DistanceMiles10": {
                                    "distinct_away_store_counts": [{"value": 3, "date": LAST_ANALYTICS_DATE}]
                                }
                            }
                        }
                    }
                }
            },
            {
                "_id": self.cci2,
                "data": {
                    "pair": {
                        "entity_id_from": self.co1,
                        "entity_id_to": self.co3
                    },
                    "from": {
                        "name": "1"
                    },
                    "to": {
                        "name": "3"
                    },
                    "analytics": {
                        "competition": {
                            "monthly": {
                                "DistanceMiles10": {
                                    "distinct_away_store_counts": [{"value": 3, "date": LAST_ANALYTICS_DATE}]
                                }
                            }
                        }
                    }
                }
            },
            {
                "_id": self.cci3,
                "data": {
                    "pair": {
                        "entity_id_from": self.co1,
                        "entity_id_to": self.co4
                    },
                    "from": {
                        "name": "1"
                    },
                    "to": {
                        "name": "4"
                    },
                    "analytics": {
                        "competition": {
                            "monthly": {
                                "DistanceMiles10": {
                                    "distinct_away_store_counts": [{"value": 0, "date": LAST_ANALYTICS_DATE}]
                                }
                            }
                        }
                    }
                }
            },
            {
                "_id": self.cci4,
                "data": {
                    "pair": {
                        "entity_id_from": self.co1,
                        "entity_id_to": self.co5
                    },
                    "from": {
                        "name": "1"
                    },
                    "to": {
                        "name": "5"
                    },
                    "analytics": {
                        "competition": {
                            "monthly": {
                                "DistanceMiles10": {
                                    "distinct_away_store_counts": [{"value": 0, "date": LAST_ANALYTICS_DATE}]
                                }
                            }
                        }
                    }
                }
            }
        ])

    def tearDown(self):

        self.mds.trade_area.drop()
        self.mds.company_competition_instance.drop()
        self.mds.company.drop()

    def test_company_away_store_vs_trade_area_competitive_stores__good(self):
        
        checker = CompanyAwayStoresVsTradeAreaCompetitiveStoresDataCheck(self.mds, {"_id": self.co1}, self.company_dict, date_parser=self.date_parser)
        result = checker.check()

        self.assertTrue(result)

    def test_company_away_store_vs_trade_area_competitive_stores__unpublished_companies(self):

        self.mds.trade_area.insert([
            {
                "_id": ObjectId(),
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "competitive_stores": [
                        {
                            "away_company_id": self.co6,
                            "away_store_id": self.store60,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        }
                    ]
                }
            }
        ])

        checker = CompanyAwayStoresVsTradeAreaCompetitiveStoresDataCheck(self.mds, {"_id": self.co1}, self.company_dict, date_parser=self.date_parser)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted([str(self.co6)])
        )

    def test_company_away_store_vs_trade_area_competitive_stores__bad_cci(self):

        self.mds.trade_area.insert([
            {
                "_id": ObjectId(),
                "interval": [None, None],
                "data": {
                    "company_id": str(self.co1),
                    "competitive_stores": [
                        {
                            "away_company_id": self.co5,
                            "away_store_id": self.store50,
                            "start_date": START_OF_WORLD,
                            "end_date": END_OF_WORLD
                        }
                    ]
                }
            }
        ])

        cci5 = ObjectId()
        self.co7 = ObjectId()

        self.mds.company_competition_instance.insert([
            {
                "_id": cci5,
                "data": {
                    "pair": {
                        "entity_id_from": self.co1,
                        "entity_id_to": self.co7
                    },
                    "from": {
                        "name": "1"
                    },
                    "to": {
                        "name": "6"
                    },
                    "analytics": {
                        "competition": {
                            "monthly": {
                                "DistanceMiles10": {
                                    "distinct_away_store_counts": [{"value": 5, "date": LAST_ANALYTICS_DATE}]
                                }
                            }
                        }
                    }
                }
            }
        ])

        checker = CompanyAwayStoresVsTradeAreaCompetitiveStoresDataCheck(self.mds, {"_id": self.co1}, self.company_dict, date_parser=self.date_parser)
        result = checker.check()

        self.assertFalse(result)

        self.assertEqual(
            sorted(checker.failures),
            sorted([
                (self.cci4, '1', 0, '5', 1),
                (cci5, '1', 5, '6', 0)
            ])
        )


if __name__ == '__main__':
    unittest.main()
