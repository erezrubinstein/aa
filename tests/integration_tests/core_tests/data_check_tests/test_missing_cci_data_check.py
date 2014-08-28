import unittest

from bson.objectid import ObjectId
from pymongo import mongo_client

from core.data_checks.implementation.company_checks.competition.missing_cci_data_check import MissingCCIDataCheck


__author__ = 'vgold'


class TestMissingCCIDataCheck(unittest.TestCase):

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

        self.ind1 = ObjectId()
        self.ind2 = ObjectId()
        self.ind3 = ObjectId()

        self.co10 = ObjectId()
        self.co11 = ObjectId()
        self.co20 = ObjectId()
        self.co21 = ObjectId()
        self.co30 = ObjectId()

        self.mds.industry.insert([
            {
                "_id": self.ind1,
                "links": {
                    "industry": {
                        "industry_competition": [
                            {
                                "entity_role_from": "competitor",
                                "entity_role_to": "competitor",
                                "entity_id_to": self.ind1
                            },
                            {
                                "entity_role_from": "competitor",
                                "entity_role_to": "competitor",
                                "entity_id_to": self.ind2
                            }
                        ]
                    }
                }
            },
            {
                "_id": self.ind2,
                "links": {
                    "industry": {
                        "industry_competition": [
                            {
                                "entity_role_from": "competitor",
                                "entity_role_to": "competitor",
                                "entity_id_to": self.ind1
                            },
                            {
                                "entity_role_from": "competitor",
                                "entity_role_to": "competitor",
                                "entity_id_to": self.ind2
                            }
                        ]
                    }
                }
            },
            {
                "_id": self.ind3,
                "links": {
                    "industry": {
                        "industry_competition": [
                            {
                                "entity_role_from": "competitor",
                                "entity_role_to": "competitor",
                                "entity_id_to": self.ind3
                            }
                        ]
                    }
                }
            }
        ])

        self.mds.company.insert([
            {
                "_id": self.co10,
                "data": {"type": "retail_banner", "workflow": {"current": {"status": "published"}}},
                "links": {
                    "industry": {
                        "industry_classification": [
                            {
                                "entity_role_from": "primary_industry_classification",
                                "entity_role_to": "primary_industry",
                                "entity_id_to": self.ind1
                            }
                        ]
                    }
                }
            },
            {
                "_id": self.co11,
                "data": {"type": "retail_banner", "workflow": {"current": {"status": "published"}}},
                "links": {
                    "industry": {
                        "industry_classification": [
                            {
                                "entity_role_from": "primary_industry_classification",
                                "entity_role_to": "primary_industry",
                                "entity_id_to": self.ind1
                            }
                        ]
                    }
                }
            },
            {
                "_id": self.co20,
                "data": {"type": "retail_banner", "workflow": {"current": {"status": "published"}}},
                "links": {
                    "industry": {
                        "industry_classification": [
                            {
                                "entity_role_from": "primary_industry_classification",
                                "entity_role_to": "primary_industry",
                                "entity_id_to": self.ind2
                            }
                        ]
                    }
                }
            },
            {
                "_id": self.co21,
                "data": {"type": "retail_banner", "workflow": {"current": {"status": "published"}}},
                "links": {
                    "industry": {
                        "industry_classification": [
                            {
                                "entity_role_from": "primary_industry_classification",
                                "entity_role_to": "primary_industry",
                                "entity_id_to": self.ind2
                            }
                        ]
                    }
                }
            },
            {
                "_id": self.co30,
                "data": {"type": "retail_banner", "workflow": {"current": {"status": "published"}}},
                "links": {
                    "industry": {
                        "industry_classification": [
                            {
                                "entity_role_from": "primary_industry_classification",
                                "entity_role_to": "primary_industry",
                                "entity_id_to": self.ind3
                            }
                        ]
                    }
                }
            }
        ])

        self.mds.company_competition_instance.insert([
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co10,
                        "entity_id_to": self.co10
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co10,
                        "entity_id_to": self.co11
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co10,
                        "entity_id_to": self.co20
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co10,
                        "entity_id_to": self.co21
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co11,
                        "entity_id_to": self.co10
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co11,
                        "entity_id_to": self.co11
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co11,
                        "entity_id_to": self.co20
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co11,
                        "entity_id_to": self.co21
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co20,
                        "entity_id_to": self.co10
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co20,
                        "entity_id_to": self.co11
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co20,
                        "entity_id_to": self.co20
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co20,
                        "entity_id_to": self.co21
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co21,
                        "entity_id_to": self.co10
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co21,
                        "entity_id_to": self.co11
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co21,
                        "entity_id_to": self.co20
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co21,
                        "entity_id_to": self.co21
                    }
                }
            },
            {
                "_id": ObjectId(),
                "data": {
                    "pair": {
                        "entity_id_from": self.co30,
                        "entity_id_to": self.co30
                    }
                }
            }
        ])

    def tearDown(self):

        self.mds.industry.drop()
        self.mds.company.drop()
        self.mds.company_competition_instance.drop()

    def test_missing_cci_data_check__good(self):

        published_company_set = {
            str(co["_id"])
            for co in self.mds.company.find({"data.workflow.current.status": "published"}, {"_id": 1})
        }
        
        checker = MissingCCIDataCheck(self.mds, self.mds.company.find_one({"_id": self.co10}), published_company_set)
        result = checker.check()

        self.assertTrue(result)
        self.assertEqual(len(checker.failures), 0)

    def test_missing_cci_data_check__bad(self):

        ind4 = ObjectId()

        self.mds.industry.insert({
            "_id": ind4,
            "links": {
                "industry": {
                    "industry_competition": [
                        {
                            "entity_role_from": "competitor",
                            "entity_role_to": "competitor",
                            "entity_id_to": ind4
                        }
                    ]
                }
            }
        })

        co22 = ObjectId()
        co40 = ObjectId()

        self.mds.company.insert([
            {
                "_id": co22,
                "data": {"type": "retail_banner", "workflow": {"current": {"status": "published"}}},
                "links": {
                    "industry": {
                        "industry_classification": [
                            {
                                "entity_role_from": "primary_industry_classification",
                                "entity_role_to": "primary_industry",
                                "entity_id_to": self.ind2
                            }
                        ]
                    }
                }
            },
            {
                "_id": co40,
                "data": {"type": "retail_banner", "workflow": {"current": {"status": "published"}}},
                "links": {
                    "industry": {
                        "industry_classification": [
                            {
                                "entity_role_from": "primary_industry_classification",
                                "entity_role_to": "primary_industry",
                                "entity_id_to": ind4
                            }
                        ]
                    }
                }
            }
        ])

        published_company_set = {
            str(co["_id"])
            for co in self.mds.company.find({"data.workflow.current.status": "published"}, {"_id": 1})
        }

        checker = MissingCCIDataCheck(self.mds, self.mds.company.find_one({"_id": self.co10}), published_company_set)
        result = checker.check()

        self.assertFalse(result)
        self.assertEqual(
            checker.failures,
            {self.ind2: ({co22}, 3, 2)}
        )

        checker = MissingCCIDataCheck(self.mds, self.mds.company.find_one({"_id": co22}), published_company_set)
        result = checker.check()

        self.assertFalse(result)
        self.assertEqual(
            sorted(checker.failures),
            [self.ind1, self.ind2]
        )

        checker = MissingCCIDataCheck(self.mds, self.mds.company.find_one({"_id": co40}), published_company_set)
        result = checker.check()

        self.assertFalse(result)
        self.assertEqual(
            checker.failures,
            {ind4: ({co40}, 1, 0)}
        )


if __name__ == '__main__':
    unittest.main()
