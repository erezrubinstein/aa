import unittest
import datetime
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.config import Config
from common.utilities.signal_math import SignalDecimal
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository
from geoprocessing.business_logic.business_objects.source_file_record import SourceFileRecord

__author__ = 'jsternberg'

class SourceFileRecordTests(unittest.TestCase):
    def setUp(self):
        # set up mock dependencies
        dependencies.register_dependency("Config", Config().instance)
        self._data_repository = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", self._data_repository)

    def tearDown(self):
        dependencies.clear()

    def test_standard_init(self):
        source_file_record = SourceFileRecord().standard_init(source_file_record_id=888,
            source_file_id=999,
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
            opened_date=datetime.datetime.strptime('2012-11-01', '%Y-%m-%d'),
            source_date=datetime.datetime.strptime('2012-12-28', '%Y-%m-%d'),
            note='Chipotle',
            store_format='burritos',
            company_generated_store_number='1024')

        self.assertEqual(source_file_record.source_file_record_id, 888)
        self.assertEqual(source_file_record.source_file_id, 999)
        self.assertEqual(source_file_record.row_number, 1)
        self.assertEqual(source_file_record.record, '(spam:(1,2), eggs:(3,4))')
        self.assertEqual(source_file_record.loader_record_id, 12)
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


    def test_select_by_id(self):
            db_source_file_record = SourceFileRecord().standard_init(source_file_record_id=888,
                source_file_id=999,
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
                opened_date=datetime.datetime.strptime('2012-11-01', '%Y-%m-%d'),
                source_date=datetime.datetime.strptime('2012-12-28', '%Y-%m-%d'),
                note='Chipotle',
                store_format='burritos',
                company_generated_store_number='1024')
            self._data_repository.source_file_records[1024] = db_source_file_record
            test_source_file_record = SourceFileRecord.select_by_id(1024)
            self.assertEqual(test_source_file_record, db_source_file_record)