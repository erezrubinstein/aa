from core.common.business_logic.service_entity_logic.address_helper import get_addresses_by_id, get_addresses_by_company_ids
from core.common.utilities.helpers import ensure_id
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_address
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.testing_utilities import convert_entity_list_to_dictionary


__author__ = 'erezrubinstein'


class AddressHelperTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "main_export_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):
        # delete when starting
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    # -------------------------------------- Begin Testing!! -------------------

    def test_get_addresses_per_store(self):
        # create three addresses
        address_1 = ensure_id(insert_test_address(1, 1))
        address_2 = ensure_id(insert_test_address(2, 2))
        address_3 = ensure_id(insert_test_address(3, 3))

        # query two of them
        addresses = get_addresses_by_id([address_1, address_2], self.context)
        addresses = convert_entity_list_to_dictionary(addresses)

        # make sure both addresses were selected
        self.test_case.assertEqual(len(addresses), 2)
        self.test_case.assertIn(address_1, addresses)
        self.test_case.assertIn(address_2, addresses)

        # make sure the fields I want are included in the results
        self.test_case.assertIn("_id", addresses[address_1])
        self.test_case.assertIn("data", addresses[address_1])
        self.test_case.assertIn("street_number", addresses[address_1]["data"])
        self.test_case.assertIn("street", addresses[address_1]["data"])
        self.test_case.assertIn("city", addresses[address_1]["data"])
        self.test_case.assertIn("state", addresses[address_1]["data"])
        self.test_case.assertIn("zip", addresses[address_1]["data"])
        self.test_case.assertIn("latitude", addresses[address_1]["data"])
        self.test_case.assertIn("longitude", addresses[address_1]["data"])
        self.test_case.assertIn("suite", addresses[address_1]["data"])
        self.test_case.assertIn("shopping_center", addresses[address_1]["data"])

    def test_get_addresses_per_company_ids(self):

        # create addresses for three companies
        address_1 = ensure_id(insert_test_address(1, 1, company_id="1"))
        address_2 = ensure_id(insert_test_address(2, 2, company_id="1"))
        address_3 = ensure_id(insert_test_address(3, 3, company_id="2"))
        address_4 = ensure_id(insert_test_address(4, 4, company_id="3"))
        
        # select addresses for two of the companies
        addresses = get_addresses_by_company_ids(["1", "3"], self.context)

        # make sure it's correct
        self.test_case.assertEqual(sorted(addresses), sorted([
            self._create_test_address(address_1, 1, 1),
            self._create_test_address(address_2, 2, 2),
            self._create_test_address(address_4, 4, 4)
        ]))

    # ------------------------ Private Methods ------------------------ #

    def _create_test_address(self, address_id, latitude, longitude):

        return {
            "_id": address_id,
            "data": {
                "street_number": 0,
                "street": "UNITTEST",
                "city": "UNITTEST",
                "state": "NY",
                "zip": 11111,
                "suite": "woot",
                "shopping_center": "chicken",
                "longitude": longitude,
                "latitude": latitude
            }
        }
