from time import sleep
import unittest
import datetime
import json
from geoprocessing.business_logic.business_objects.address import Address
from common.business_logic.company_info import CompanyInfo
from geoprocessing.business_logic.business_objects.source_file import SourceFile
from geoprocessing.business_logic.business_objects.source_file_record import SourceFileRecord
from geoprocessing.business_logic.config import Config
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from common.utilities.signal_math import SignalDecimal
from geoprocessing.data_access.data_repository import DataRepository
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import insert_test_company, insert_test_source_file, delete_test_company, delete_test_source_file, select_source_file_by_id, select_source_file_notes_by_id, insert_test_source_file_record, delete_test_source_file_record

__author__ = 'spacecowboy et al.'


class SourceFileHandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)

        cls._company_id = insert_test_company()
        cls._source_file_id = insert_test_source_file('/Volumes/Rob/test_2012_25_12.xlsx', datetime.datetime(1990, 05, 18), 42)

    @classmethod
    def tearDownClass(cls):
        if cls._source_file_id is not None:
            delete_test_source_file(cls._source_file_id)
        if cls._company_id is not None:
            delete_test_company(cls._company_id)



    def test_insert_source_file__new_file(self):
        try:
            # insert a new file into the db
            source_file_id = self._SQL_data_repository.insert_source_file("UNITTEST_FILE_PATH", "2012-01-01", 1000)

            # select file from the db and verify its contents
            source_file = select_source_file_by_id(source_file_id)
            self.assertGreater(source_file_id, 0)
            self.assertEqual(source_file.full_path, "UNITTEST_FILE_PATH")
            self.assertEqual(source_file.file_created_date, datetime.datetime(2012, 1, 1))
            self.assertEqual(source_file.file_modified_date, datetime.datetime(2012, 1, 1))
            self.assertEqual(source_file.file_size_in_bytes, 1000)
            # created should equal updated (since it's new)
            self.assertEqual(source_file.created_at, source_file.updated_at)
        except:
            raise
        finally:
            delete_test_source_file(source_file_id)

    def test_insert_source_file__update_file(self):
        try:
            # insert a new file into the db
            source_file_id = self._SQL_data_repository.insert_source_file("UNITTEST_FILE_PATH", "2012-01-01", 1000)

            # sleep for a little to make sure updated date is updated
            sleep(.3)

            # insert the file again, which should update it
            source_file_id_updated = self._SQL_data_repository.insert_source_file("UNITTEST_FILE_PATH", "2012-02-02", 2000)

            # verify that the updated id matches the inserted id
            self.assertEqual(source_file_id, source_file_id_updated)

            # select file from the db and verify its contents were updated correctly
            source_file = select_source_file_by_id(source_file_id)
            self.assertGreater(source_file_id, 0)
            self.assertEqual(source_file.full_path, "UNITTEST_FILE_PATH")
            self.assertEqual(source_file.file_created_date, datetime.datetime(2012, 1, 1))
            self.assertEqual(source_file.file_modified_date, datetime.datetime(2012, 2, 2))
            self.assertEqual(source_file.file_size_in_bytes, 2000)
            # updated > created (since it's updated)
            self.assertGreater(source_file.updated_at, source_file.created_at)
        except:
            raise
        finally:
            delete_test_source_file(source_file_id)

    def test_save_loader_records_and_parsed_addresses(self):
        notes_back = None
        company_info = None
        try:
            company_info = CompanyInfo(source_name = 'test_2012_12_25.xlsx')
            company_info._source_file_id = self._source_file_id

            record_1 = {'pirate': 1}
            record_2 = {'santa': 1}

            records = [json.dumps(record_1), json.dumps(record_2)]

            address_1 = Address.complex_init_for_loader(address_id = None,
                                                        street_number = str(123),
                                                        street = ' '.join(['Davie Jones', 'Dr']).strip(),
                                                        city = 'Pirate Ship',
                                                        state = 'The Ocean',
                                                        zip_code = '00000',
                                                        country_id = None,
                                                        phone_number = 'Aaarrrr',
                                                        longitude = -42.00,
                                                        latitude = 42.00,
                                                        suite_numbers = None,
                                                        complex = None,
                                                        loader_opened_on = datetime.datetime(1800, 12, 25),
                                                        source_date = datetime.datetime(1800, 12, 24),
                                                        note = 'Walk the plank aarrr',
                                                        store_format = None,
                                                        company_generated_store_number = str(42),
                                                        loader_record_id = 42)

            parsed_record_2 = Address.complex_init_for_loader(address_id = None,
                                                        street_number = str(123),
                                                        street = ' '.join(['Candycane', 'Lane']).strip(),
                                                        city = 'North Pole',
                                                        state = 'NP',
                                                        zip_code = '00000',
                                                        country_id = None,
                                                        phone_number = 'Hohoho',
                                                        longitude = -180.00,
                                                        latitude = 180.00,
                                                        suite_numbers = 'Workshop B',
                                                        complex = 'Toy Facility #12578',
                                                        loader_opened_on = datetime.datetime(2012, 12, 25),
                                                        source_date = datetime.datetime(2012, 12, 24),
                                                        note = "We're understaffed!",
                                                        store_format = None,
                                                        company_generated_store_number = str(42),
                                                        loader_record_id = 42)

            parsed_records = [address_1, parsed_record_2]
            company_info.records = records
            company_info.parsed_records = parsed_records

            self._SQL_data_repository.save_loader_records_and_parsed_addresses(company_info)
            notes_back = select_source_file_notes_by_id(self._source_file_id)
            self.assertEqual(len(notes_back), 2)
            self.assertEqual(notes_back[0][0], 'Walk the plank aarrr')
            self.assertEqual(notes_back[1][0], "We're understaffed!")

        except:
            raise
        finally:
            if notes_back:
                self._SQL_data_repository.delete_loader_records_for_current_file(company_info)


    def test_select_source_file_by_source_file_id(self):
        try:
            # insert a new file into the db
            source_file_id = self._SQL_data_repository.insert_source_file("UNITTEST_FILE_PATH", "2012-01-01", 1000)

            # select file from the db and verify its contents
            source_file = SourceFile.select_by_id(source_file_id)
            self.assertEqual(source_file.source_file_id, source_file_id)
            self.assertEqual(source_file.full_path, "UNITTEST_FILE_PATH")
            self.assertEqual(source_file.file_created_date, datetime.datetime(2012, 1, 1))
            self.assertEqual(source_file.file_modified_date, datetime.datetime(2012, 1, 1))
            self.assertEqual(source_file.file_size_in_bytes, 1000)

        except:
            raise
        finally:
            delete_test_source_file(source_file_id)

    def test_select_source_file_record_by_source_file_record_id(self):
        try:
            # insert a new file into the db
            source_file_id = self._SQL_data_repository.insert_source_file("UNITTEST_FILE_PATH", "2012-01-01", 1000)
            # insert a source file record for this source file
            source_file_record_id = insert_test_source_file_record(source_file_id,
                row_number=1,
                record='(spam:(1,2), eggs:(3,4))',
                loader_record_id=12,
                street_number='317',
                street='Madison Ave',
                city='New York',
                state='NY',
                zip='10017',
                country_id=840,
                phone='646-560-5402',
                longitude=SignalDecimal('-73.978828'),
                latitude=SignalDecimal('40.752716'),
                suite='811',
                shopping_center_name='Verifone Media Place',
                opened_date='11/1/2012',
                source_date='12/28/2012',
                note='Chipotle',
                store_format='burritos',
                company_generated_store_number='1024')

            # select file from the db and verify its contents
            source_file_record = SourceFileRecord.select_by_id(source_file_record_id)
            self.assertEqual(source_file_record.source_file_id, source_file_id)
            self.assertEqual(source_file_record.row_number, 1)
            self.assertEqual(source_file_record.record, '(spam:(1,2), eggs:(3,4))')
            self.assertEqual(source_file_record.loader_record_id, '12')
            self.assertEqual(source_file_record.street_number, '317')
            self.assertEqual(source_file_record.street, 'Madison Ave')
            self.assertEqual(source_file_record.city, 'New York')
            self.assertEqual(source_file_record.state, 'NY')
            self.assertEqual(source_file_record.zip, '10017')
            self.assertEqual(source_file_record.country_id, 840)
            self.assertEqual(source_file_record.phone, '646-560-5402')
            self.assertEqual(source_file_record.longitude, SignalDecimal('-73.978828'))
            self.assertEqual(source_file_record.latitude, SignalDecimal('40.752716'))
            self.assertEqual(source_file_record.suite, '811')
            self.assertEqual(source_file_record.shopping_center_name, 'Verifone Media Place')
            self.assertEqual(source_file_record.opened_date, datetime.datetime.strptime('2012-11-01', '%Y-%m-%d'))
            self.assertEqual(source_file_record.source_date, datetime.datetime.strptime('2012-12-28', '%Y-%m-%d'))
            self.assertEqual(source_file_record.note, 'Chipotle')
            self.assertEqual(source_file_record.store_format, 'burritos')
            self.assertEqual(source_file_record.company_generated_store_number, '1024')

        except:
            raise
        finally:
            delete_test_source_file_record(source_file_record_id)
            delete_test_source_file(source_file_id)

if __name__ == '__main__':
    unittest.main()