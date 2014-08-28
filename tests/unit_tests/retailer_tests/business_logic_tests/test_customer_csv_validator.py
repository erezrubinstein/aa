import mox
from retailer.common.business_logic.customer_csv_validator import CustomerCsvValidator
from retailer.common.business_logic.has_value_detector import HasValueDetector
import unittest
import datetime


class TestCustomerCsvValidator(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(TestCustomerCsvValidator, self).setUp()

        # main class to be tested
        self.mock = self.mox.CreateMock(CustomerCsvValidator)
        self.parsed_columns = ["CUSTOMER_ID", "AS_OF_DATE", "NAME_PREFIX", "NAME_FIRST", "NAME_MIDDLE", "NAME_LAST",
                               "NAME_SUFFIX", "EMAIL", "GENDER", "BUSINESS_NAME", "ADDRESS_1", "ADDRESS_2", "CITY",
                               "STATE", "ZIP", "COUNTY", "LONGITUDE", "LATITUDE", "GEOCODE_TYPE", "DECEASED_CODE",
                               "EMPLOYEE_FLAG", "MARITAL_STATUS", "AGE", "TOTAL_LTM_SPEND"]
        self.has_value_detector = HasValueDetector()


    def doCleanups(self):
        # call parent clean up
        super(TestCustomerCsvValidator, self).doCleanups()


    def test_req_gender__success(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        good_values = ["M","F", "U", "B"]
        for good_value in good_values:
            line = ["", "", "", "", "", "", "", "", good_value]
            result = ccv.req_gender(line)

            # make sure no error
            self.assertIsNone(result)


    def test_req_gender__failure(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        bad_values = ["X","@","&","q","~","%"]
        for bad_value in bad_values:
            line = ["", "", "", "", "", "", "", "", bad_value]
            result = ccv.req_gender(line)

            # make sure error registered
            self.assertIsNotNone(result)


    def test_req_geocode__success(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "12.4232", "23.677856"]
        result = ccv.req_geocode(line)

        # make sure no error
        self.assertIsNone(result)


    def test_req_geocode__failure_one_missing(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "12.4232"]
        result = ccv.req_geocode(line)

        # make sure error registered
        self.assertEqual(result, "Missing either longitude or latitude value")

        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "12.4232", ""]
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        result = ccv.req_geocode(line)

        # make sure error registered
        self.assertEqual(result, "Missing either longitude or latitude value")


    #def test_req_geocode__failure_value_type(self):
    #    ccv = CustomerCsvValidator(self.parsed_columns)
    #    line = ["", "", "", "", "", "", "", "", "", "", "",
    #            "", "", "", "", "", "12.4232", "23.677856as"]
    #    result = ccv.req_geocode(line)
    #
    #    # make sure error registered
    #    self.assertEqual(result, "Longitude and latitude values must be floats.")


    def test_req_geocode_type__success(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "12.4232", "23.677856", "R"]
        result = ccv.req_geocode_type(line)

        # make sure error registered
        self.assertIsNone(result)


    def test_req_geocode_type__failure_missing(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "12.4232", "23.677856", ""]
        result = ccv.req_geocode_type(line)

        # make sure error registered
        self.assertEqual(result, "Longitude/latitude was given without GEOCODE_TYPE")


    def test_req_geocode_type__failure_wrong_value(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "12.4232", "23.677856", "MN"]
        result = ccv.req_geocode_type(line)

        # make sure error registered
        self.assertIsNotNone(result)


    def test_req_deceased_code__success(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "I"]
        result = ccv.req_deceased_code(line)

        # make sure error registered
        self.assertIsNone(result)


    def test_req_deceased_code__failure(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "asdfsad"]
        result = ccv.req_deceased_code(line)

        # make sure error registered
        self.assertIsNotNone(result)


    def test_req_employee_flag__success(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "Y"]
        result = ccv.req_employee_flag(line)

        # make sure error registered
        self.assertIsNone(result)


    def test_req_employee_flag__failure(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "D"]
        result = ccv.req_employee_flag(line)

        # make sure error registered
        self.assertIsNotNone(result)


    def test_req_marital_status__success(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "", "1S"]
        result = ccv.req_marital_status(line)

        # make sure error registered
        self.assertIsNone(result)


    def test_req_marital_status__failure_incorrect_number_chars(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "", "1"]
        result = ccv.req_marital_status(line)

        # make sure error registered
        self.assertIsNotNone(result)


    def test_req_marital_status__failure_incorrect_first_char(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "", "9S"]
        result = ccv.req_marital_status(line)

        # make sure error registered
        self.assertIn("The first character", result)


    def test_req_marital_status__failure_incorrect_second_char(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "", "1B"]
        result = ccv.req_marital_status(line)

        # make sure error registered
        self.assertIn("The second character", result)


    def test_req_age__success(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "", "", "25"]
        result = ccv.req_age(line)

        # make sure error registered
        self.assertIsNone(result)

        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "", "", "U"]
        result = ccv.req_age(line)

        # make sure error registered
        self.assertIsNone(result)


    def test_req_age__failure_invalid_age_value(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "", "", "100"]
        result = ccv.req_age(line)

        # make sure error registered
        self.assertEqual(result, "Age must be a value between 19 and 99 - Value given - 100")


    def test_req_age__failure_invalid_type(self):
        ccv = CustomerCsvValidator(self.parsed_columns, self.has_value_detector)
        line = ["", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "", "", "S"]
        result = ccv.req_age(line)

        # make sure error registered
        self.assertEqual(result, "If age is not unknown, it must be an integer - Value given - S")

if __name__ == '__main__':
    unittest.main()
