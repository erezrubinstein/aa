import mox
from retailer.common.business_logic.abstract_csv_validator import AbstractCsvValidator
from retailer.common.business_logic.csv_column_helper import CsvColumnHelper
import unittest

class TestCsvColumnHelper(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(TestCsvColumnHelper, self).setUp()


    def doCleanups(self):
        # call parent clean up
        super(TestCsvColumnHelper, self).doCleanups()


    def test_convert_all_columns_to_upper_in_constructor(self):
        columns_in_file = ["a", "b", "c"]

        cch = CsvColumnHelper(columns_in_file, None)

        # make sure error registered
        self.assertEqual(cch.columns_in_file, ["A", "B", "C"])


    def test_initialize_column_definitions__order_columns(self):
        """
        Make sure column definitions get returned in the same column order as columns_in_file.
        """
        columns_in_file = ["c", "b", "a"]
        predefined_column_defs = {
            "A": {
                "db_field": "a",
                "req": True,
                "type": "str"
            },
            "B": {
                "db_field": "b",
                "req": True,
                "type": "str"
            },
            "C": {
                "db_field": "c",
                "req": True,
                "type": "str"
            }
        }

        cch = CsvColumnHelper(columns_in_file, predefined_column_defs)

        expected_ordered_column_definitions = [
            {
                "db_field": "c",
                "req": True,
                "type": "str",
                "index": 0,
                "name": "C"
            },
            {
                "db_field": "b",
                "req": True,
                "type": "str",
                "index": 1,
                "name": "B"
            },
            {
                "db_field": "a",
                "req": True,
                "type": "str",
                "index": 2,
                "name": "A"
            }
        ]

        # go
        ordered_column_definitions, custom_column_names = cch.initialize_column_definitions()

        # verify
        self.assertEqual(ordered_column_definitions, expected_ordered_column_definitions)
        self.assertEqual(custom_column_names, [])


    def test_initialize_column_definitions__custom_columns(self):
        """
        Make sure column definitions get returned in the same column order as columns_in_file.
        """
        columns_in_file = ["c", "b", "a", "custom"]
        predefined_column_defs = {
            "A": {
                "db_field": "a",
                "req": True,
                "type": "str"
            },
            "B": {
                "db_field": "b",
                "req": True,
                "type": "str"
            },
            "C": {
                "db_field": "c",
                "req": True,
                "type": "str"
            }
        }

        cch = CsvColumnHelper(columns_in_file, predefined_column_defs)

        expected_ordered_column_definitions = [
            {
                "db_field": "c",
                "req": True,
                "type": "str",
                "index": 0,
                "name": "C"
            },
            {
                "db_field": "b",
                "req": True,
                "type": "str",
                "index": 1,
                "name": "B"
            },
            {
                "db_field": "a",
                "req": True,
                "type": "str",
                "index": 2,
                "name": "A"
            },
            {
                "db_field": "custom",
                "req": False,
                "type": "str",
                "index": 3,
                "name": "CUSTOM"
            }
        ]

        # go
        ordered_column_definitions, custom_column_names = cch.initialize_column_definitions()

        # verify
        self.assertEqual(ordered_column_definitions, expected_ordered_column_definitions)
        self.assertEqual(custom_column_names, ["CUSTOM"])

if __name__ == '__main__':
    unittest.main()
