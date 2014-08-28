import mox
from retailer.common.business_logic.abstract_csv_validator import AbstractCsvValidator
from retailer.common.business_logic.has_value_detector import HasValueDetector
import unittest

class TestAbstractCsvValidator(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(TestAbstractCsvValidator, self).setUp()

        # main class to be tested
        #self.mock = self.mox.CreateMock(AbstractCsvValidator)
        #self.mock.errors = []
        self.parsed_columns = ["CUSTOMER_ID", "AS_OF_DATE", "SOME_FLOAT", "SOME_INT"]
        self.expected_column_definitions = {
            "CUSTOMER_ID": {
                "req": True,
                "type": "str"
            },
            "AS_OF_DATE": {
                "req": False,
                "type": "datetime"
            },
            "SOME_FLOAT": {
                "req": False,
                "type": "float"
            },
            "SOME_INT": {
                "req": False,
                "type": "int"
            }
        }
        self.has_value_detector = HasValueDetector()


    def doCleanups(self):
        # call parent clean up
        super(TestAbstractCsvValidator, self).doCleanups()


    def test_validate_column_count__failure(self):
        line = [1, 2, 3]
        acv = AbstractCsvValidator(self.expected_column_definitions, self.parsed_columns, self.has_value_detector)
        acv._validate_column_count(line)

        # make sure error registered
        self.assertEqual(acv.errors, ['Expecting at least 4 columns but only 3 found.'])


    def test_validate_schema__success(self):
        line = ["asdf", "10/28/2013", "1.2", "94938"]
        acv = AbstractCsvValidator(self.expected_column_definitions, self.parsed_columns, self.has_value_detector)
        acv._validate_column_schema(line)

        # make sure no errors
        self.assertEqual(acv.errors, [])


    def test_validate_schema__missing_required(self):
        line = ["", "10/28/2013", "1.2", "94938"]
        acv = AbstractCsvValidator(self.expected_column_definitions, self.parsed_columns, self.has_value_detector)
        acv._validate_column_schema(line)

        # make sure no errors
        self.assertEqual(acv.errors, ["Required value 'CUSTOMER_ID' not found."])


    def test_validate_schema__invalid_datetime(self):
        line = ["asdf", "asdf10/28/2013", "1.2", "94938"]
        acv = AbstractCsvValidator(self.expected_column_definitions, self.parsed_columns, self.has_value_detector)
        acv._validate_column_schema(line)

        # make sure no errors
        self.assertEqual(acv.errors, ["Expecting type 'datetime' for column 'AS_OF_DATE'"])


    def test_validate_schema__invalid_float(self):
        line = ["asdf", "10/28/2013", "kklsdasdf1.2", "94938"]
        acv = AbstractCsvValidator(self.expected_column_definitions, self.parsed_columns, self.has_value_detector)
        acv._validate_column_schema(line)

        # make sure no errors
        self.assertEqual(acv.errors, ["Expecting type 'float' for column 'SOME_FLOAT'"])


    def test_validate_schema__invalid_int(self):
        line = ["asdf", "10/28/2013", "1.2", "df 94938"]
        acv = AbstractCsvValidator(self.expected_column_definitions, self.parsed_columns, self.has_value_detector)
        acv._validate_column_schema(line)

        # make sure no errors
        self.assertEqual(acv.errors, ["Expecting type 'int' for column 'SOME_INT'"])

if __name__ == '__main__':
    unittest.main()
