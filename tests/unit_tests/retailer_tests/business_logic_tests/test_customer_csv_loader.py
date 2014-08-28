import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from retailer.common.business_logic.customer_csv_loader import CustomerCsvLoader
from retailer.common.business_logic.has_value_detector import HasValueDetector
import unittest

class TestCustomerCsvLoader(mox.MoxTestBase):
    def setUp(self):
        super(TestCustomerCsvLoader, self).setUp()

        register_common_mox_dependencies(self.mox)
        self.mock = self.mox.CreateMock(CustomerCsvLoader)
        self.has_value_detector = HasValueDetector()

    def doCleanups(self):
        # call parent clean up
        super(TestCustomerCsvLoader, self).doCleanups()


    def test_parse_geocode(self):
        loader = CustomerCsvLoader({}, [], None, self.has_value_detector, "mds_file_id")

        customer = {
            "data": {
                "latitude": "042844830N",
                "longitude":  "071651223W"
            }
        }

        loader.parse_geocode(customer)

        expected = {
            "data": {
                'geo': [-71.651223, 42.84483],
                'latitude': 42.84483,
                'longitude': -71.651223,
                'raw_latitude': "042844830N",
                'raw_longitude': "071651223W"
            }
        }

        self.assertEqual(expected, customer)

if __name__ == '__main__':
    unittest.main()
