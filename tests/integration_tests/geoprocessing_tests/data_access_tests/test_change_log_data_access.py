from datetime import datetime
import unittest
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.enums import StoreChangeType, AddressChangeType
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import delete_test_source_file, insert_test_company, insert_test_address, insert_test_store, delete_test_store, delete_test_address, delete_test_company, delete_store_change_logs_by_source_file_id, select_stores_change_log_entries, select_addresses_change_log_entries, delete_addresses_change_logs_by_source_file_id, select_addresses_change_log_values, delete_addresses_change_log_values_by_source_file_id

__author__ = 'erezrubinstein'

class ChangeLogDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._data_repository = DataRepository()
        dependencies.register_dependency('DataRepository', cls._data_repository)

    @classmethod
    def tearDownClass(cls):
        dependencies.clear()




    def test_save_stores_to_change_log(self):
            try:
                # insert a new file into the db
                source_file_id = self._data_repository.insert_source_file("UNITTEST_FILE_PATH", "2012-01-01", 1000)

                # create 5 fake stores
                company_id = insert_test_company()
                address_id = insert_test_address(-40, 40)
                store_id1 = insert_test_store(company_id, address_id)
                store_id2 = insert_test_store(company_id, address_id)
                store_id3 = insert_test_store(company_id, address_id)
                store_id4 = insert_test_store(company_id, address_id)
                store_id5 = insert_test_store(company_id, address_id)

                # create list of 2 deleted stores
                deleted_store_ids = [store_id1, store_id2]

                # create list of 3 changed stores
                store3 = Store()
                store3.store_id = store_id3
                store3.change_type = StoreChangeType.StoreConfirmed
                store3.mismatched_parameters = []
                store4 = Store()
                store4.store_id = store_id4
                store4.change_type = StoreChangeType.StoreUpdated
                store4.mismatched_parameters = ['chicken', 'beef']
                store5 = Store()
                store5.store_id = store_id5
                store5.change_type = StoreChangeType.StoreOpened
                store5.mismatched_parameters = []
                changed_stores = [store3, store4, store5]

                # add the change_longs for the 5 stores (2 deleted, one opened, one confirmed, one updated)
                source_file_id = self._data_repository.save_stores_to_change_log(deleted_store_ids, changed_stores, "2012-01-01", source_file_id)

                # select the change log entries and verify their contents
                change_logs = select_stores_change_log_entries(source_file_id)
                # verify deleted stores
                # store 1
                self.assertEqual(len(change_logs), 5)
                self.assertEqual(change_logs[0].store_id, store_id1)
                self.assertEqual(change_logs[0].log_date, datetime(2012, 1, 1))
                self.assertEqual(change_logs[0].change_type_id, StoreChangeType.StoreClosed)
                self.assertIsNone(change_logs[0].comment)
                self.assertEqual(change_logs[0].source_file_id, source_file_id)
                # store 2
                self.assertEqual(change_logs[1].store_id, store_id2)
                self.assertEqual(change_logs[1].log_date, datetime(2012, 1, 1))
                self.assertEqual(change_logs[1].change_type_id, StoreChangeType.StoreClosed)
                self.assertIsNone(change_logs[1].comment)
                self.assertEqual(change_logs[1].source_file_id, source_file_id)
                # store 3
                self.assertEqual(change_logs[2].store_id, store_id3)
                self.assertEqual(change_logs[2].log_date, datetime(2012, 1, 1))
                self.assertEqual(change_logs[2].change_type_id, StoreChangeType.StoreConfirmed)
                self.assertEqual(change_logs[2].comment, '[]')
                self.assertEqual(change_logs[2].source_file_id, source_file_id)
                # store 4
                self.assertEqual(change_logs[3].store_id, store_id4)
                self.assertEqual(change_logs[3].log_date, datetime(2012, 1, 1))
                self.assertEqual(change_logs[3].change_type_id, StoreChangeType.StoreUpdated)
                self.assertEqual(change_logs[3].comment, "['chicken', 'beef']")
                self.assertEqual(change_logs[3].source_file_id, source_file_id)
                # store 5
                self.assertEqual(change_logs[4].store_id, store_id5)
                self.assertEqual(change_logs[4].log_date, datetime(2012, 1, 1))
                self.assertEqual(change_logs[4].change_type_id, StoreChangeType.StoreOpened)
                self.assertEqual(change_logs[4].comment, "[]")
                self.assertEqual(change_logs[4].source_file_id, source_file_id)
            except:
                raise
            finally:
                delete_store_change_logs_by_source_file_id(source_file_id)
                delete_test_source_file(source_file_id)
                delete_test_store(store_id1)
                delete_test_store(store_id2)
                delete_test_store(store_id3)
                delete_test_store(store_id4)
                delete_test_store(store_id5)
                delete_test_address(address_id)
                delete_test_company(company_id)


    def test_save_address_to_change_log(self):
        try:
            # insert a new file into the db
            source_file_id = self._data_repository.insert_source_file("UNITTEST_FILE_PATH", "2012-01-01", 1000)

            # create 3 fake addresses
            company_id = insert_test_company()
            address_id1 = insert_test_address(-40, 40)
            address_id2 = insert_test_address(-50, 50)
            address_id3 = insert_test_address(-60, 60)

            # create list of 3 changed addresses
            address1 = Address()
            address1.address_id = address_id1
            address1.change_type = AddressChangeType.AddressCreated
            address1.mismatched_parameters = []

            address2 = Address()
            address2.address_id = address_id2
            address2.change_type = AddressChangeType.AddressChanged
            address2.mismatched_parameters = [('city','somewhere','nowhere')]

            address3 = Address()
            address3.address_id = address_id3
            address3.change_type = AddressChangeType.MismatchAddressIgnored
            address3.mismatched_parameters = [('city','somewhere','nowhere')]

            for address in [address1,address2,address3]:
                source_file_id = self._data_repository.save_address_to_change_log(address, "2012-01-01", source_file_id)

            # select the change log entries and verify their contents
            change_logs = select_addresses_change_log_entries(source_file_id)
            change_logs_values = select_addresses_change_log_values(source_file_id)

            # verify
            self.assertEqual(len(change_logs), 3)
            self.assertEqual(len(change_logs_values), 2)

            #address 1
            self.assertEqual(change_logs[0].address_id, address_id1)
            self.assertEqual(change_logs[0].log_date, datetime(2012, 1, 1))
            self.assertEqual(change_logs[0].change_type_id, AddressChangeType.AddressCreated)
            self.assertEqual(change_logs[0].comment,str([]))
            self.assertEqual(change_logs[0].source_file_id, source_file_id)

            #address 2
            self.assertEqual(change_logs[1].address_id, address_id2)
            self.assertEqual(change_logs[1].log_date, datetime(2012, 1, 1))
            self.assertEqual(change_logs[1].change_type_id, AddressChangeType.AddressChanged)
            self.assertEqual(change_logs[1].comment, str([('city','somewhere','nowhere')]))
            self.assertEqual(change_logs[1].source_file_id, source_file_id)

            self.assertEqual(change_logs_values[0].value_type, 'city')
            self.assertEqual(change_logs_values[0].from_value, 'somewhere')
            self.assertEqual(change_logs_values[0].to_value, 'nowhere')

            #address 3
            self.assertEqual(change_logs[2].address_id, address_id3)
            self.assertEqual(change_logs[2].log_date, datetime(2012, 1, 1))
            self.assertEqual(change_logs[2].change_type_id, AddressChangeType.MismatchAddressIgnored)
            self.assertEqual(change_logs[2].comment, str([('city','somewhere','nowhere')]))
            self.assertEqual(change_logs[2].source_file_id, source_file_id)

            self.assertEqual(change_logs_values[1].value_type, 'city')
            self.assertEqual(change_logs_values[1].from_value, 'somewhere')
            self.assertEqual(change_logs_values[1].to_value, 'nowhere')

        except:
            raise
        finally:
            delete_addresses_change_log_values_by_source_file_id(source_file_id)
            delete_addresses_change_logs_by_source_file_id(source_file_id)
            delete_test_source_file(source_file_id)
            delete_test_address(address_id1)
            delete_test_address(address_id2)
            delete_test_address(address_id3)
            delete_test_company(company_id)

if __name__ == '__main__':
    unittest.main()