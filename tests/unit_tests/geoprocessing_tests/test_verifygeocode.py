import logging
import unittest
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.enums import  FailThreshold
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import PostgresDataRepository
from geoprocessing.geoprocessors.validation.verify_geocode import VerifyGeocode
from geoprocessing.business_logic.config import Config
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockRestProvider
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository

__author__ = 'spacecowboy'

class VerifyGeocodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # set up mock dependencies
        dependencies.register_dependency("Config", Config().instance)
        cls.__sql_provider = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", cls.__sql_provider)
        dependencies.register_dependency("RestProvider", MockRestProvider())
        dependencies.register_dependency("LogManager", LogManager(logging.CRITICAL))
        dependencies.register_dependency('PostgresDataRepository', PostgresDataRepository())

        # set up data
        cls.__store = Store()
        cls.__store.store_id = 777777
        cls.__store.company_id = 666666
        cls.__store.address_id = 10
        cls.__store.address = Address.standard_init(10, 600, "Cape May st", "Harrison", "NJ", "07029", None, -74.150363, 40.736869, None, None)
        cls.__sql_provider.stores[777777] = cls.__store
        cls.__sql_provider.addresses[10] = cls.__store.address

    @classmethod
    def tearDownClass(cls):
        dependencies.clear()


    #####################################################################################################################
    #############################################   initialization Tests ################################################
    #####################################################################################################################
    def test_initialization_ESRI(self):
        verify_geocode_processor = VerifyGeocode('ESRI')
        verify_geocode_processor._home_store = self.__store
        verify_geocode_processor._initialize()

        #make sure the values are initialized correctly
        self.assertEqual(verify_geocode_processor._address.address_id, self.__store.address_id)

    def test_initialization_Google(self):
        verify_geocode_processor = VerifyGeocode('Google')
        verify_geocode_processor._home_store = self.__store
        verify_geocode_processor._initialize()

        #make sure the values are initialized correctly
        self.assertEqual(verify_geocode_processor._address.address_id, self.__store.address_id)


    #####################################################################################################################
    ##############################################   get_GIS_data Tests #################################################
    #####################################################################################################################
    def test_get_GIS_reverse_geocodes_ESRI(self):
        """
        Test that VerifyGeocode gets the right URL
        """
        verify_geocode_processor = VerifyGeocode('ESRI')
        verify_geocode_processor._home_store = self.__store
        verify_geocode_processor._initialize()
        verify_geocode_processor._do_geoprocessing()

        self.assertTrue(str(verify_geocode_processor._home_store.address.longitude) in verify_geocode_processor._reverse_geocode_url_with_qualifiers)
        self.assertTrue(str(verify_geocode_processor._home_store.address.latitude) in verify_geocode_processor._reverse_geocode_url_with_qualifiers)

    def test_get_GIS_reverse_geocodes_Google(self):
        """
        Test that VerifyGeocode gets the right URL
        """
        verify_geocode_processor = VerifyGeocode('Google')
        verify_geocode_processor._home_store = self.__store
        verify_geocode_processor._initialize()
        verify_geocode_processor._do_geoprocessing()

        self.assertTrue(str(verify_geocode_processor._home_store.address.longitude) in verify_geocode_processor._reverse_geocode_url_with_qualifiers)
        self.assertTrue(str(verify_geocode_processor._home_store.address.latitude) in verify_geocode_processor._reverse_geocode_url_with_qualifiers)

    #####################################################################################################################
    #############################################   process_GIS_data Tests ##############################################
    #####################################################################################################################
    def test_process_GIS_data_ESRI(self):
        """
        Test that gp1 parses the response and appends it to its internal list
        """
        #set up fake data and process it
        verify_geocode_processor = VerifyGeocode('ESRI')
        verify_geocode_processor._home_store = self.__store
        verify_geocode_processor._initialize()
        verify_geocode_processor._do_geoprocessing()

        verify_geocode_processor._reverse_geocode_response = {'location':
                                                                  {'y': 40.736869, 'x': 74.150363, 'spatialReference': {'wkid': 4326, 'latestWkid': 4326}},
                                                              'address':
                                                                  {'Loc_name': 'Address_Points', 'City': 'Harrison', 'State': 'NJ', 'Zip': '07029', 'Address': '600 Cape May St'}}
        verify_geocode_processor._preprocess_data_for_save()
        self.assertEqual(verify_geocode_processor._expected_address.city, 'Harrison')
        self.assertEqual(verify_geocode_processor._expected_address.state, 'NJ')
        self.assertEqual(verify_geocode_processor._expected_address.zip_code, '07029')

        # pass all tests

        self.assertTrue(verify_geocode_processor._data_check.bad_data_rows < FailThreshold.ReverseGeoCodeESRI)

        # fail one test (city), pass overall
        verify_geocode_processor._reverse_geocode_response = {'location':
                                                                  {'y': 40.736869, 'x': 74.150363, 'spatialReference': {'wkid': 4326, 'latestWkid': 4326}},
                                                              'address':
                                                                  {'Loc_name': 'Address_Points', 'City': 'LOL', 'State': 'NJ', 'Zip': '07029', 'Address': '600 Cape May St'}}
        verify_geocode_processor._preprocess_data_for_save()
        self.assertTrue(verify_geocode_processor._data_check.bad_data_rows < FailThreshold.ReverseGeoCodeESRI)
        self.assertEqual(verify_geocode_processor._data_check.bad_data_rows, 1)

        # fail two tests (city, state), fail overall
        verify_geocode_processor._reverse_geocode_response = {'location':
                                                                  {'y': 40.736869, 'x': 74.150363, 'spatialReference': {'wkid': 4326, 'latestWkid': 4326}},
                                                              'address':
                                                                  {'Loc_name': 'Address_Points', 'City': 'LOL', 'State': 'WHAT?', 'Zip': '07029', 'Address': '600 Cape May St'}}
        verify_geocode_processor._preprocess_data_for_save()
        self.assertFalse(verify_geocode_processor._data_check.bad_data_rows < FailThreshold.ReverseGeoCodeESRI)
        self.assertEqual(verify_geocode_processor._data_check.bad_data_rows, 2)

        # fail three tests (city, state, zip), fail overall
        verify_geocode_processor._reverse_geocode_response = {'location':
                                                                  {'y': 40.736869, 'x': 74.150363, 'spatialReference': {'wkid': 4326, 'latestWkid': 4326}},
                                                              'address':
                                                                  {'Loc_name': 'Address_Points', 'City': 'LOL', 'State': 'WHAT?', 'Zip': '00000', 'Address': '600 Cape May St'}}
        verify_geocode_processor._preprocess_data_for_save()
        self.assertFalse(verify_geocode_processor._data_check.bad_data_rows < FailThreshold.ReverseGeoCodeESRI)
        self.assertEqual(verify_geocode_processor._data_check.bad_data_rows, 3)

    def test_process_GIS_data_Google(self):
        """
        Test that gp1 parses the response and appends it to its internal list
        """
        #set up fake data and process it
        verify_geocode_processor = VerifyGeocode('Google')
        verify_geocode_processor._home_store = self.__store
        verify_geocode_processor._initialize()

        verify_geocode_processor._reverse_geocode_response = {
            "results" : [
                {
                    "address_components" : [
                        {
                            "long_name" : "600",
                            "short_name" : "600",
                            "types" : [ "street_number" ]
                        },
                        {
                            "long_name" : "Cape May St",
                            "short_name" : "Cape May St",
                            "types" : [ "route" ]
                        },
                        {
                            "long_name" : "Harrison",
                            "short_name" : "Harrison",
                            "types" : [ "locality", "political" ]
                        },
                        {
                            "long_name" : "Hudson",
                            "short_name" : "Hudson",
                            "types" : [ "administrative_area_level_2", "political" ]
                        },
                        {
                            "long_name" : "New Jersey",
                            "short_name" : "NJ",
                            "types" : [ "administrative_area_level_1", "political" ]
                        },
                        {
                            "long_name" : "United States",
                            "short_name" : "US",
                            "types" : [ "country", "political" ]
                        },
                        {
                            "long_name" : "07029",
                            "short_name" : "07029",
                            "types" : [ "postal_code" ]
                        }
                    ]
                }
            ]
        }
        verify_geocode_processor._preprocess_data_for_save()
        self.assertEqual(verify_geocode_processor._expected_address.city, 'Harrison')
        self.assertEqual(verify_geocode_processor._expected_address.state, 'NJ')
        self.assertEqual(verify_geocode_processor._expected_address.zip_code, '07029')

        # pass all tests

        self.assertTrue(verify_geocode_processor._data_check.bad_data_rows < FailThreshold.ReverseGeoCodeESRI)

        # fail one test (city), pass overall
        verify_geocode_processor._reverse_geocode_response = {
            "results" : [
                {
                    "address_components" : [
                        {
                            "long_name" : "600",
                            "short_name" : "600",
                            "types" : [ "street_number" ]
                        },
                        {
                            "long_name" : "Cape May St",
                            "short_name" : "Cape May St",
                            "types" : [ "route" ]
                        },
                        {
                            "long_name" : "LOL",
                            "short_name" : "LOL",
                            "types" : [ "locality", "political" ]
                        },
                        {
                            "long_name" : "Hudson",
                            "short_name" : "Hudson",
                            "types" : [ "administrative_area_level_2", "political" ]
                        },
                        {
                            "long_name" : "New Jersey",
                            "short_name" : "NJ",
                            "types" : [ "administrative_area_level_1", "political" ]
                        },
                        {
                            "long_name" : "United States",
                            "short_name" : "US",
                            "types" : [ "country", "political" ]
                        },
                        {
                            "long_name" : "07029",
                            "short_name" : "07029",
                            "types" : [ "postal_code" ]
                        }
                    ]
                }
            ]
        }
        verify_geocode_processor._preprocess_data_for_save()
        self.assertTrue(verify_geocode_processor._data_check.bad_data_rows < FailThreshold.ReverseGeoCodeESRI)
        self.assertEqual(verify_geocode_processor._data_check.bad_data_rows, 1)

        # fail two tests (city, state), fail overall
        verify_geocode_processor._reverse_geocode_response = {
            "results" : [
                {
                    "address_components" : [
                        {
                            "long_name" : "600",
                            "short_name" : "600",
                            "types" : [ "street_number" ]
                        },
                        {
                            "long_name" : "Cape May St",
                            "short_name" : "Cape May St",
                            "types" : [ "route" ]
                        },
                        {
                            "long_name" : "LOL",
                            "short_name" : "LOL",
                            "types" : [ "locality", "political" ]
                        },
                        {
                            "long_name" : "Hudson",
                            "short_name" : "Hudson",
                            "types" : [ "administrative_area_level_2", "political" ]
                        },
                        {
                            "long_name" : "WHAT?",
                            "short_name" : "WHAT?",
                            "types" : [ "administrative_area_level_1", "political" ]
                        },
                        {
                            "long_name" : "United States",
                            "short_name" : "US",
                            "types" : [ "country", "political" ]
                        },
                        {
                            "long_name" : "07029",
                            "short_name" : "07029",
                            "types" : [ "postal_code" ]
                        }
                    ]
                }
            ]
        }
        verify_geocode_processor._preprocess_data_for_save()
        self.assertFalse(verify_geocode_processor._data_check.bad_data_rows < FailThreshold.ReverseGeoCodeESRI)
        self.assertEqual(verify_geocode_processor._data_check.bad_data_rows, 2)

        # fail three tests (city, state, zip), fail overall
        verify_geocode_processor._reverse_geocode_response = {
            "results" : [
                {
                    "address_components" : [
                        {
                            "long_name" : "600",
                            "short_name" : "600",
                            "types" : [ "street_number" ]
                        },
                        {
                            "long_name" : "Cape May St",
                            "short_name" : "Cape May St",
                            "types" : [ "route" ]
                        },
                        {
                            "long_name" : "LOL",
                            "short_name" : "LOL",
                            "types" : [ "locality", "political" ]
                        },
                        {
                            "long_name" : "Hudson",
                            "short_name" : "Hudson",
                            "types" : [ "administrative_area_level_2", "political" ]
                        },
                        {
                            "long_name" : "WHAT?",
                            "short_name" : "WHAT?",
                            "types" : [ "administrative_area_level_1", "political" ]
                        },
                        {
                            "long_name" : "United States",
                            "short_name" : "US",
                            "types" : [ "country", "political" ]
                        },
                        {
                            "long_name" : "00000",
                            "short_name" : "00000",
                            "types" : [ "postal_code" ]
                        }
                    ]
                }
            ]
        }
        verify_geocode_processor._preprocess_data_for_save()
        self.assertFalse(verify_geocode_processor._data_check.bad_data_rows < FailThreshold.ReverseGeoCodeESRI)
        self.assertEqual(verify_geocode_processor._data_check.bad_data_rows, 3)


    #####################################################################################################################
    ###########################################   save_processed_data Tests #############################################
    #####################################################################################################################
    def test_save_processed_data_ESRI(self):
        """
        Test that gp1 calls the correct data access (insert_demographics) method with it's built in _demographics
        """
        #set up fake data and process it
        verify_geocode_processor = VerifyGeocode('ESRI')
        verify_geocode_processor._home_store = self.__store
        verify_geocode_processor._initialize()
        verify_geocode_processor._do_geoprocessing()
        verify_geocode_processor._preprocess_data_for_save()
        verify_geocode_processor._save_processed_data()

        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].value_type, 'city')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].expected_value, 'Woot Land')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].actual_value, 'Harrison')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].value_type, 'state')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].expected_value, 'Rob\'s Desk')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].actual_value, 'NJ')
        self.assertEqual(verify_geocode_processor._data_repository.entity_id, verify_geocode_processor._address.address_id)
        self.assertTrue(verify_geocode_processor._data_check.bad_data_rows >= FailThreshold.ReverseGeoCodeESRI)

    def test_save_processed_data_Google(self):
        """
        Test that gp1 calls the correct data access (insert_demographics) method with it's built in _demographics
        """
        #set up fake data and process it
        verify_geocode_processor = VerifyGeocode('Google')
        verify_geocode_processor._home_store = self.__store
        verify_geocode_processor._initialize()
        verify_geocode_processor._do_geoprocessing()
        verify_geocode_processor._preprocess_data_for_save()
        verify_geocode_processor._save_processed_data()


        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].value_type, 'city')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].expected_value, 'Woot Land')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].actual_value, 'Harrison')

        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].value_type, 'state')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].expected_value, 'Rob\'s Desk')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].actual_value, 'NJ')

        self.assertEqual(verify_geocode_processor._data_repository.entity_id, verify_geocode_processor._address.address_id)
        self.assertTrue(verify_geocode_processor._data_check.bad_data_rows >= FailThreshold.ReverseGeoCodeESRI)

    #####################################################################################################################
    #############################################   complete process Tests ##############################################
    #####################################################################################################################
    def test_complete_process_ESRI(self):
        """
        Main end-to-end test of the process function.
        """
        verify_geocode_processor = VerifyGeocode('ESRI')
        verify_geocode_processor.process(self.__store.company_id, self.__store.store_id)


        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].value_type, 'city')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].expected_value, 'Woot Land')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].actual_value, 'Harrison')

        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].value_type, 'state')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].expected_value, 'Rob\'s Desk')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].actual_value, 'NJ')

        self.assertEqual(verify_geocode_processor._data_repository.entity_id, verify_geocode_processor._address.address_id)
        self.assertEqual(verify_geocode_processor._data_repository.bad_data_rows, 2)

    def test_complete_process_Google(self):
        """
        Main end-to-end test of the process function.
        """
        verify_geocode_processor = VerifyGeocode('Google')
        verify_geocode_processor.process(self.__store.company_id, self.__store.store_id)


        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].value_type, 'city')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].expected_value, 'Woot Land')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[0].actual_value, 'Harrison')

        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].value_type, 'state')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].expected_value, 'Rob\'s Desk')
        self.assertEqual(verify_geocode_processor._data_repository.mismatched_values[1].actual_value, 'NJ')

        self.assertEqual(verify_geocode_processor._data_repository.entity_id, verify_geocode_processor._address.address_id)
        self.assertEqual(verify_geocode_processor._data_repository.bad_data_rows, 2)


#####################################################################################################################
###############################################  Main ######### #####################################################
#####################################################################################################################
if __name__ == "__main__":
    unittest.main()
