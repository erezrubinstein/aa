from bson.objectid import ObjectId
import mox
from datetime import datetime
from retailer.common.business_logic.abstract_csv_loader import AbstractCsvLoader
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from retailer.common.business_logic.has_value_detector import HasValueDetector
import unittest

class SomeDerivedCsvLoader(AbstractCsvLoader):
    def __init__(self, columns_in_file, retailer_client_id):

        self.predefined_column_definitions = {
            "CUSTOMER_ID": {
                "db_field": "customer_id",
                "req": True,
                "type": "str",
            },
            "AS_OF_DATE": {
                "db_field": "as_of_date",
                "req": False,
                "type": "datetime",
            },
            "SOME_INT": {
                "db_field": "some_int",
                "req": False,
                "type": "int",
            },
            "SOME_FLOAT": {
                "db_field": "some_float",
                "req": False,
                "type": "float",
            }
        }

        self.entity_type = 'customer'
        self.parsers = []

        self.retailer_client_id = retailer_client_id
        self.has_value_detector = HasValueDetector()
        self.mds_file_id = "mds_file_id"

        super(SomeDerivedCsvLoader, self).__init__({}, columns_in_file, retailer_client_id,
                                                       self.has_value_detector, self.mds_file_id)

class TestAbstractCsvLoader(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(TestAbstractCsvLoader, self).setUp()
        register_common_mox_dependencies(self.mox)


    def doCleanups(self):
        # call parent clean up
        super(TestAbstractCsvLoader, self).doCleanups()


    def test_build_raw_entity(self):
        test_columns_in_file = [
            "CUSTOMER_ID",
            "AS_OF_DATE",
            "SOME_FLOAT",
            "SOME_INT"
        ]

        test_line = [
            "MYTESTID",
            "10/28/2013",
            "1.01",
            "231"
        ]

        loader = SomeDerivedCsvLoader(test_columns_in_file, "client_id")
        actual = loader.build_raw_entity(test_line)

        expected = {
            "name": "_",
            "data": {
                "retailer_client_id": "client_id",
                "mds_file_id": "mds_file_id",
                "customer_id": "MYTESTID",
                "as_of_date": datetime(2013, 10, 28),
                "some_float": 1.01,
                "some_int": 231
            }
        }

        self.assertIn("_id", actual)
        self.assertTrue(isinstance(actual["_id"], ObjectId))
        del actual["_id"]

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
