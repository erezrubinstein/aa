import unittest
from common.data_access.multidb_mongo_access import MultiDBMongoAccess
from pymongo.mongo_client import MongoClient

__author__ = 'jsternberg'

class MultiDBMongoAccessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # connection variables
        ref_data = {
            "entity_types": {
                "company": { },
                "store_weather": {
                    "db_connection": "analytics",
                }
            }
        }

        # db connection settings
        connections_dict = {
            "default": {
                "db": 'itest_mongo_access',
                "host": 'localhost',
                "port": 27017,
                "replica_set": None,
                "read_preference": None,
                "tag_sets": None,
                'autoreconnect_max_retries': 10,  # max number of autoreconnect attempts before failing
                'autoreconnect_retry_interval': 2,  # seconds between attempts
                'autoreconnect_attempt_log_frequency': 1  # log every x attempts to reconnect
            },

            # this is the secondary mongodb that we will begin using for analytics work.
            "analytics": {
                "db": 'itest_mongo_access_2',
                "host": 'localhost',
                "port": 27017,
                "replica_set": None,
                "read_preference": None,
                "tag_sets": None,
                'autoreconnect_max_retries': 10,  # max number of autoreconnect attempts before failing
                'autoreconnect_retry_interval': 2,  # seconds between attempts
                'autoreconnect_attempt_log_frequency': 1  # log every x attempts to reconnect
            }
        }

        # db connection
        cls.mongo_access = MultiDBMongoAccess(connections_dict, ref_data, None)

        # clear collections
        cls.mongo_access.remove("company", {})
        cls.mongo_access.remove("store_weather", {})

    @classmethod
    def tearDownClass(cls):

        # not cleaning up db, because drop them about 2 seconds per run
        pass


    def test_basic_init(self):

        self.assertIsInstance(self.mongo_access.conns["default"], MongoClient)
        self.assertIsInstance(self.mongo_access.conns["analytics"], MongoClient)

    def test_insert_select_two_databases(self):

        # insert a company and a store_weather
        self.mongo_access.insert("company", {})
        self.mongo_access.insert("store_weather", {})

        # create a mongo client for each database
        company_db = MongoClient("localhost", 27017)["itest_mongo_access"]
        store_weather_db = MongoClient("localhost", 27017)["itest_mongo_access_2"]

        # verify that each db only has its own data
        self.assertEqual(company_db.company.count(), 1)
        self.assertEqual(store_weather_db.company.count(), 0)
        self.assertEqual(company_db.store_weather.count(), 0)
        self.assertEqual(store_weather_db.store_weather.count(), 1)



if __name__ == '__main__':
    unittest.main()

