from datetime import datetime
import unittest
from geoprocessing.business_logic.business_objects.address import Address
from common.business_logic.company_info import CompanyInfo, Sector, Competitor
from geoprocessing.business_logic.business_objects.parsed_loader_record import ParsedLoaderRecord
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.enums import StoreChangeType
from common.utilities.inversion_of_control import dependencies, Dependency
from common.utilities.signal_math import SignalDecimal
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from geoprocessing.loader import Loader

__author__ = 'spacecowboy'

class LoaderTests(unittest.TestCase):

    def setUp(self):
        register_mock_dependencies()
        self.config = Dependency("Config").value
        self.file_provider = Dependency("FileProvider").value
        self.sql_provider = Dependency("DataRepository").value
        self.excel_provider = Dependency("ExcelProvider").value

    def tearDown(self):
        dependencies.clear()

    def test_initialize(self):
        # mock two stores
        parsed_record_1 = Address.standard_init(address_id = None, street_number = 42, street = 'Woot Ln',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 1, latitude = 1, suite_numbers = None, complex = None)
        parsed_record_2 = Address.standard_init(address_id = None, street_number = 43, street = 'Woot Ln',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 2, latitude = 2, suite_numbers = None, complex = None)

        # mock up company ids
        self.sql_provider.company_ids_per_name["David Gage"] = 41

        # mock up competitors / sectors
        self.sql_provider.open_competitive_companies_per_company[41] = [99, 100]
        self.sql_provider.sector_ids_per_company[41] = [4, 5]

        # mock up fake stores
        self.sql_provider.store_ids_and_opened_dates_for_company[41] = []
        for store_id in range(1, 5):
            store = Store()
            store.store_id = store_id
            store.assumed_open_date = datetime(2012, 12, store_id)
            self.sql_provider.store_ids_and_opened_dates_for_company[41].append(store)

        # mock up fake company
        company = CompanyInfo('David Gage', ['Music', 'Specialty'], None, [parsed_record_1, parsed_record_2], "Woot_2012_12_25.xlsx", ticker = 'DGAGE')

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()

        self.assertEqual(loader._company_info, company)
        self.assertEqual(company.company_id, 41)
        self.assertEqual(loader._db_stores_for_company, self.sql_provider.store_ids_and_opened_dates_for_company[41])
        self.assertEqual(loader._db_sector_ids_for_company, [4, 5])
        self.assertEqual(loader._db_away_company_ids_for_company, [99, 100])


    def test_store_assumed_opened_date__initial_load__known_opened_date(self):
        """
        Verify that we always set the assumed and real opened date to store's opened date if we know what it is (regardless of initial load or not)
        """
        # mock up store and company
        record = ParsedLoaderRecord(address_id = None,
                                    street_number = "1",
                                    street = "street",
                                    city = "city",
                                    state = "state",
                                    zip_code = "11111",
                                    country_id = 840,
                                    latitude = SignalDecimal(1.0),
                                    longitude = SignalDecimal(2.0),
                                    loader_opened_on = datetime(2010, 5, 5),
                                    source_date = datetime(2012, 1, 1),
                                    phone_number = None)

        company = CompanyInfo('Company', [Sector('Random Stores', 'Yes')], [], [record], "Woot_2012_12_25.xlsx", ticker = 'DGAGE', records = ['rob'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._load_company()

        # verify that the opened_date is 01/01/1900
        self.assertEqual(loader._company_info.parsed_records[0].street, 'street')
        self.assertEqual(loader._company_info.stores[0]._assumed_opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0]._opened_date, datetime(2010, 5, 5))

    def test_store_phone_number_international_parsing_no_leading_one_no_parenthesis_USA(self):
        """
        This tests that the international phone number parsing for great US and A, with a leading one (15555555555 -> +1 555-555-5555).
        """
        # mock up store and company

        record = ParsedLoaderRecord(None, "1", "street", "city", "state", "11111", 840, SignalDecimal(1.0), SignalDecimal(2.0), datetime(2010, 5, 5), datetime(2012, 1, 1), phone_number = '5555555555')
        company = CompanyInfo('Company', [Sector('Random Stores', 'Yes')], [], [record], "Woot_2012_12_25.xlsx", ticker = 'DGAGE', records = ['rob'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._load_company()

        # verify that the opened_date is 01/01/1900
        self.assertEqual(loader._company_info.parsed_records[0].street, 'street')
        self.assertEqual(loader._company_info.parsed_records[0].phone_number, '5555555555')
        self.assertEqual(loader._company_info.stores[0]._assumed_opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0]._opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0].phone_number, '+1 555-555-5555')

    def test_store_phone_number_international_parsing_no_leading_one_punctuation_USA(self):
        """
        This tests that the international phone number parsing for great US and A, with a leading one (15555555555 -> +1 555-555-5555).
        """
        # mock up store and company

        parsed_record_1 = ParsedLoaderRecord(address_id = None,
                                             street_number = "1",
                                             street = "street",
                                             city = "city",
                                             state = "state",
                                             zip_code = "11111",
                                             country_id = 840,
                                             latitude = SignalDecimal(1.0),
                                             longitude = SignalDecimal(2.0),
                                             loader_opened_on = datetime(2010, 5, 5),
                                             source_date = datetime(2012, 1, 1),
                                             phone_number = '(555) 555.5555')

        parsed_record_2 = ParsedLoaderRecord(address_id = None,
                                             street_number = "1",
                                             street = "street",
                                             city = "city",
                                             state = "state",
                                             zip_code = "11111",
                                             country_id = 840,
                                             latitude = SignalDecimal(1.0),
                                             longitude = SignalDecimal(2.0),
                                             loader_opened_on = datetime(2010, 5, 5),
                                             source_date = datetime(2012, 1, 1),
                                             phone_number = '(555) 555-5555 ext 5305')


        company = CompanyInfo('Company', [Sector('Random Stores', 'Yes')], [], [parsed_record_1, parsed_record_2], "Woot_2012_12_25.xlsx", ticker = 'DGAGE', records = ['rob'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._load_company()

        # verify that the opened_date is 01/01/1900
        self.assertEqual(loader._company_info.parsed_records[0].street, 'street')
        self.assertEqual(loader._company_info.parsed_records[0].phone_number, '(555) 555.5555')
        self.assertEqual(loader._company_info.stores[0]._assumed_opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0]._opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0].phone_number, '+1 555-555-5555')
        self.assertEqual(loader._company_info.stores[1].phone_number, '+1 555-555-5555 ext. 5305')

    def test_store_phone_number_international_parsing_no_leading_one_no_parenthesis_USA(self):
        """
        This tests that the international phone number parsing for great US and A, with a leading one (15555555555 -> +1 555-555-5555).
        """
        # mock up store and company

        record = ParsedLoaderRecord(address_id = None,
                                    street_number = "1",
                                    street = "street",
                                    city = "city",
                                    state = "state",
                                    zip_code = "11111",
                                    country_id = 840,
                                    latitude = SignalDecimal(1.0),
                                    longitude = SignalDecimal(2.0),
                                    loader_opened_on = datetime(2010, 5, 5),
                                    source_date = datetime(2012, 1, 1),
                                    phone_number = '15555555555')

        company = CompanyInfo('Company', [Sector('Random Stores', 'Yes')], [], [record], "Woot_2012_12_25.xlsx", ticker = 'DGAGE', records = ['rob'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._load_company()

        # verify that the opened_date is 01/01/1900
        self.assertEqual(loader._company_info.parsed_records[0].street, 'street')
        self.assertEqual(loader._company_info.parsed_records[0].phone_number, '15555555555')
        self.assertEqual(loader._company_info.stores[0]._assumed_opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0]._opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0].phone_number, '+1 555-555-5555')

    def test_store_phone_number_international_parsing_missing_phone_number(self):
        """
        This tests that the international phone number parsing for great US and A, with a leading one (15555555555 -> +1 555-555-5555).
        """
        # mock up store and company
        record = ParsedLoaderRecord(address_id = None,
                                    street_number = "1",
                                    street = "street",
                                    city = "city",
                                    state = "state",
                                    zip_code = "11111",
                                    country_id = 840,
                                    latitude = SignalDecimal(1.0),
                                    longitude = SignalDecimal(2.0),
                                    loader_opened_on = datetime(2010, 5, 5),
                                    source_date = datetime(2012, 1, 1),
                                    phone_number = None)

        company = CompanyInfo('Company', [Sector('Random Stores', 'Yes')], [], [record], "Woot_2012_12_25.xlsx", ticker = 'DGAGE', records = ['rob'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._load_company()

        # verify that the opened_date is 01/01/1900
        self.assertEqual(loader._company_info.parsed_records[0].street, 'street')
        self.assertEqual(loader._company_info.parsed_records[0].phone_number, None)
        self.assertEqual(loader._company_info.stores[0]._assumed_opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0]._opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0].phone_number, None)


    def test_store_assumed_opened_date__not_initial_load__known_opened_date(self):
        """
        Verify that we always set the assumed and real opened date to store's opened date if we know what it is (regardless of initial load or not)
        """
        # mock up count of stores (i.e. not the first run)
        self.sql_provider.store_count[1] = 100

        # mock up store and company
        record = ParsedLoaderRecord(address_id = None,
                                    street_number = "1",
                                    street = "street",
                                    city = "city",
                                    state = "state",
                                    zip_code = "11111",
                                    country_id = 840,
                                    latitude = SignalDecimal(1.0),
                                    longitude = SignalDecimal(2.0),
                                    loader_opened_on = datetime(2010, 5, 5),
                                    source_date = datetime(2012, 1, 1),
                                    phone_number = None)

        company = CompanyInfo('Company', [Sector('Random Stores', 'Yes')], [], [record], "Woot_2012_12_25.xlsx", ticker = 'DGAGE', records = ['rob'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._load_company()

        # verify that the opened_date is 01/01/1900
        self.assertEqual(loader._company_info.parsed_records[0].street, 'street')
        self.assertEqual(loader._company_info.stores[0]._assumed_opened_date, datetime(2010, 5, 5))
        self.assertEqual(loader._company_info.stores[0]._opened_date, datetime(2010, 5, 5))


    def test_store_assumed_opened_date__initial_load__unknown_opened_date(self):
        """
        Verify that we always set the assumed and real opened date to 1/1/1900 if the store's open date is unknown and this is the initial date
        """
        # mock up store and company
        record = ParsedLoaderRecord(address_id = None,
                                    street_number = "1",
                                    street = "street",
                                    city = "city",
                                    state = "state",
                                    zip_code = "11111",
                                    country_id = 840,
                                    latitude = SignalDecimal(1.0),
                                    longitude = SignalDecimal(2.0),
                                    loader_opened_on = None,
                                    source_date = datetime(2012, 12, 25),
                                    phone_number = None)

        company = CompanyInfo('Company', [Sector('Random Stores', 'Yes')], [], [record], "Woot_2012_12_25.xlsx", ticker = 'DGAGE', records = ['rob'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._save()

        # verify that the opened_date is 01/01/1900
        self.assertEqual(loader._company_info.parsed_records[0].street, 'street')
        self.assertEqual(loader._company_info.stores[0]._assumed_opened_date, datetime(1900, 1, 1))
        self.assertEqual(loader._company_info.stores[0]._opened_date, datetime(1900, 1, 1))


    def test_store_assumed_opened_date__not_initial_load__unknown_opened_date(self):
        """
        Verify that we set the assumed date to the source file's date and real opened date to 1/1/1900 if the store's open date is unknown and this is NOT the initial date
        """
        # mock up count of stores (i.e. not the first run)
        self.sql_provider.store_count[1] = 100

        # mock up company ids
        self.sql_provider.company_ids_per_name["Company"] = 1

        # mock up store and company
        record = ParsedLoaderRecord(address_id = None,
                                    street_number = "1",
                                    street = "street",
                                    city = "city",
                                    state = "state",
                                    zip_code = "11111",
                                    country_id = 840,
                                    latitude = SignalDecimal(1.0),
                                    longitude = SignalDecimal(2.0),
                                    loader_opened_on = None,
                                    source_date = datetime(2012, 12, 25),
                                    phone_number = None)

        company = CompanyInfo('Company', [Sector('Random Stores', 'Yes')], [], [record], "Woot_2012_12_25.xlsx", ticker = 'DGAGE', records = ['rob'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._save()

        # verify that the opened_date is 01/01/1900
        self.assertEqual(loader._company_info.parsed_records[0].street, 'street')
        self.assertEqual(loader._company_info.stores[0]._assumed_opened_date, datetime(2012, 12, 25))
        self.assertEqual(loader._company_info.stores[0]._opened_date, datetime(1900, 1, 1))

    def test_update_company_ticker_sectors_competitors(self):
        # mock addresses
        self.sql_provider.addresses_within_range.append(ParsedLoaderRecord(address_id = None,
                                                                           street_number = "1",
                                                                           street = "street",
                                                                           city = "city",
                                                                           state = "state",
                                                                           zip_code = "11111",
                                                                           country_id = None,
                                                                           latitude = SignalDecimal(1.9999),
                                                                           longitude = SignalDecimal(2.0001),
                                                                           loader_opened_on = None,
                                                                           source_date = datetime(2012, 12, 24),
                                                                           phone_number = None))

        # mock two stores
        parsed_record_1 = Address.standard_init(address_id = None, street_number = 42, street = 'Woot Ln',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 1, latitude = 1, suite_numbers = None, complex = None)
        parsed_record_2 = Address.standard_init(address_id = None, street_number = 43, street = 'Woot Ln',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 2, latitude = 2, suite_numbers = None, complex = None)

        # mock up sectors
        self.sql_provider.sector_id_per_name["Music"] = 1
        self.sql_provider.sector_id_per_name["Specialty"] = 1

        # mock up fake company
        company = CompanyInfo('David Gage', [Sector('Music', 'Yes'), Sector('Specialty', 'Yes')],
            [Competitor.init_with_dates_and_company_id_query('David Gage', 'Upton Basses', '1', datetime(2012, 12, 24),
                datetime(2050, 12, 24))], [parsed_record_1, parsed_record_2], 'Woot_2012_12_25.xlsx', ticker = 'DGAGE')

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._update_company_ticker()
        loader._insert_sectors()
        Loader.insert_competitors(company.competitors)

        self.assertEqual(loader._company_info.ticker, self.sql_provider.test_company_ticker)
        self.assertEqual(loader._company_info.sectors, self.sql_provider.test_company_sectors)
        self.assertEqual(loader._company_info.competitors, self.sql_provider.test_company_competitors)
        self.assertEqual(datetime(2012, 12, 24), self.sql_provider.assumed_start_date)

    def test_save_addresses__same_address_different_phone_number_does_not_match(self):
        """
        Make sure that a store that shares an address with another, but has a different phone number is not matched (i.e. it opens a new one)
        """
        # mock up fake address

        self.sql_provider.addresses_within_range.append(ParsedLoaderRecord(address_id = 43,
                                                                        street_number = '43',
                                                                        street = 'Woot Ln East',
                                                                        city = 'Wootville',
                                                                        state = 'WT',
                                                                        zip_code = '1337',
                                                                        country_id = None,
                                                                        latitude = SignalDecimal(2.0001),
                                                                        longitude = SignalDecimal(1.9999),
                                                                        loader_opened_on = datetime(1900, 1, 1),
                                                                        source_date = datetime(2012, 12, 24),
                                                                        phone_number = None))


        # mock a store in the db (gets updated)
        store_match_update = Store()
        store_match_update.store_id = 43
        store_match_update.company_id = 40
        store_match_update.address_id = 43
        store_match_update.phone_number = '+1 223-455-7890'
        store_match_update._opened_date = datetime(1900, 1, 1)
        store_match_update._assumed_opened_date = datetime(1900, 1, 1)

        self.sql_provider.mock_db_stores = [store_match_update]
        self.sql_provider.phone_number_store_id[43] = '+1 223-455-7890'

        # mock up addresses
        record = ParsedLoaderRecord(None, '43', 'Woot Ln East', 'Wootville', 'WT', '1337', None, SignalDecimal(1.9999), SignalDecimal(2.0001), loader_opened_on = datetime(2012, 1, 1), phone_number='223-456-7890')

        # mock up company ids
        self.sql_provider.company_ids_per_name["Woot"] = 40

        # mock up fake company and competitor
        test_competitors = [Competitor.init_with_company_id_query('Woot', 'Banana Republic', 1), Competitor.init_with_company_id_query('Woot', 'Paul Shark', 1)]
        company = CompanyInfo('Woot', [Sector('Random Stores', 'Yes')], test_competitors, [record], "woot_2012_12_25", records = ['woot_chicken'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._save()

        self.assertEqual(loader._company_info.addresses[0].street, 'Woot Ln East')
        self.assertEqual(loader._company_info.addresses[0].address_id, 43)
        self.assertEqual(loader._company_info.addresses[0].mismatched_parameters, [])
        self.assertEqual(loader._company_info.stores[0].change_type, StoreChangeType.StoreOpened)
        self.assertEqual(self.sql_provider.loader_records_parsed_addresses[0], ('woot_chicken', record))

    def test_save_addresses_and_stores_confirmed(self):

        # mock up fake address

        self.sql_provider.addresses_within_range_companies.append(ParsedLoaderRecord(address_id = 43,
                                                                          street_number = '43',
                                                                          street = 'Woot Ln East',
                                                                          city = 'Wootville',
                                                                          state = 'WT',
                                                                          zip_code = '1337',
                                                                          country_id = None,
                                                                          latitude = SignalDecimal(1.9999),
                                                                          longitude = SignalDecimal(2.0001),
                                                                          loader_opened_on = datetime(1900, 1, 1),
                                                                          source_date = datetime(2012, 12, 24),
                                                                          phone_number = None))

        # create fake store 1
        store_match_update = Store()
        store_match_update.store_id = 43
        store_match_update.company_id = 40
        store_match_update.address_id = 43
        store_match_update.phone_number = '+1 223-455-7890'
        store_match_update._opened_date = datetime(1900, 1, 1)
        store_match_update._assumed_opened_date = datetime(1900, 1, 1)
        # create fake store 2
        store_match_update2 = Store()
        store_match_update2.store_id = 42
        store_match_update2.company_id = 40
        store_match_update2.address_id = 42
        store_match_update2.phone_number = '+1 223-446-7890'
        store_match_update2._opened_date = datetime(1900, 1, 1)
        store_match_update2._assumed_opened_date = datetime(1900, 1, 1)

        # create test addresses
        parsed_record_1 = ParsedLoaderRecord(None, '42', 'Chicken Ln', 'Chickenville', 'CH', '1337', None, 1, 1, loader_opened_on = datetime(2012, 5, 18), phone_number='223-446-7890')
        parsed_record_2 = ParsedLoaderRecord(None, '43', 'Woot Ln E', 'Wootville', 'WT', '1337', None, 2, 2, loader_opened_on = datetime(2012, 1, 1), phone_number='223-455-7890')

        # mock up stores and phone numbers
        self.sql_provider.mock_db_stores = [store_match_update, store_match_update2]
        self.sql_provider.phone_number_store_id[43] = '+1 223-455-7890'
        self.sql_provider.phone_number_store_id[42] = '+1 223-446-7890'

        # mock up company ids
        self.sql_provider.company_ids_per_name["Woot"] = 40

        # mock up fake company and competitor

        test_competitors = [Competitor.init_with_company_id_query('Woot', 'Banana Republic', 1), Competitor.init_with_company_id_query('Woot', 'Paul Shark', 1)]
        company = CompanyInfo('Woot', [Sector('Random Stores', 'Yes')], test_competitors, [parsed_record_1, parsed_record_2], "woot_2012_12_25", records = ['rob', 'is'])


        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._save()

        expected_mismatched_params = [('latitude', SignalDecimal(1.9999), SignalDecimal(2)),
                                      ('longitude', SignalDecimal(2.0001), SignalDecimal(2)),
                                      ('street', 'Woot Ln East', 'Woot Ln E')]

        # verify the first store matched correctly
        self.assertEqual(loader._company_info.stores[0].change_type, StoreChangeType.StoreConfirmed)
        self.assertEqual(loader._company_info.stores[0].mismatched_parameters, [])
        self.assertEqual(loader._company_info.addresses[0].street, 'Chicken Ln')
        self.assertEqual(loader._company_info.addresses[0].address_id, 42)
        self.assertEqual(loader._company_info.addresses[0].mismatched_parameters, [])
        self.assertEqual(self.sql_provider.phone_number_store_id[42], ' '.join(['+1', parsed_record_1.phone_number]))

        # verify the second store matched correctly
        self.assertEqual(loader._company_info.stores[1].change_type, StoreChangeType.StoreConfirmed)
        self.assertEqual(loader._company_info.stores[1].mismatched_parameters, [])
        self.assertEqual(loader._company_info.addresses[1].street, 'Woot Ln E')
        self.assertEqual(loader._company_info.addresses[1].address_id, 43)
        self.assertEqual(loader._company_info.addresses[1].mismatched_parameters, expected_mismatched_params)
        self.assertEqual(self.sql_provider.phone_number_store_id[43], ' '.join(['+1', parsed_record_2.phone_number]))

        # verify that nothing was updated
        self.assertEqual(len(self.sql_provider.updated_stores), 0)


    def test_save_addresses_and_stores_updated(self):

        # mock up fake address
        self.sql_provider.addresses_within_range_companies.append(ParsedLoaderRecord(address_id = 1,
                                                                           street_number = '1',
                                                                           street = 'test road',
                                                                           city = 'test city',
                                                                           state = 'NY',
                                                                           zip_code = '10016',
                                                                           country_id = None,
                                                                           latitude = SignalDecimal(1),
                                                                           longitude = SignalDecimal(2),
                                                                           loader_opened_on = datetime(1900, 1, 1),
                                                                           source_date = datetime(2012, 1, 1),
                                                                           phone_number = None))

        # create a fake store
        store = Store()
        store.store_id = 1
        store.company_id = 1
        store.address_id = 1
        store.phone_number = '+1 223-223-2234'
        store.store_format = "store_format"
        store.note = "store_note"
        store._opened_date = datetime(1900, 1, 1)
        store._assumed_opened_date = datetime(1900, 1, 1)

        # create test addresses

        parsed_record = ParsedLoaderRecord(None, '1', 'test road', 'test city', 'NY', '10016', None, 1, 2, loader_opened_on = datetime(2012, 1, 1),
            phone_number = '223-223-2234', store_format = "store_format", note = "store_note_updated")

        # mock up stores and phone numbers
        self.sql_provider.mock_db_stores = [store]

        # mock up company ids
        self.sql_provider.company_ids_per_name["test_company"] = 1

        # mock up fake company and competitor
        company = CompanyInfo('test_company', [Sector('Random Stores', 'Yes')], [], [parsed_record], "test_2012_12_25", records = ['woot'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._save()

        # verify the first store matched correctly
        self.assertEqual(loader._company_info.stores[0].change_type, StoreChangeType.StoreUpdated)
        self.assertEqual(loader._company_info.addresses[0].address_id, 1)
        self.assertEqual(loader._company_info.addresses[0].mismatched_parameters, [])

        # verify the mismatched parameters
        self.assertEqual(len(self.sql_provider.updated_stores[0].mismatched_parameters), 1)
        self.assertEqual(self.sql_provider.updated_stores[0].mismatched_parameters[0][0], "note")
        self.assertEqual(self.sql_provider.updated_stores[0].mismatched_parameters[0][1], "store_note")
        self.assertEqual(self.sql_provider.updated_stores[0].mismatched_parameters[0][2], "store_note_updated")

        # verify that the store was indeed updated
        self.assertEqual(len(self.sql_provider.updated_stores), 1)
        self.assertEqual(self.sql_provider.updated_stores[0].store_id, 1)
        self.assertEqual(self.sql_provider.updated_stores[0].note, "store_note_updated")


    def test_close_old_companies_sectors(self):

        # mock up fake addresses
        self.sql_provider.addresses_within_range.append(ParsedLoaderRecord(43, '43', 'Woot Ln East', 'Wootville', 'WT', '1337', None, SignalDecimal(1.9999),
            SignalDecimal(2.0001), source_date = datetime(2012, 12, 24)))

        self.sql_provider.store_match_phone_number = Store()
        self.sql_provider.store_match_phone_number.address_id = 43
        self.sql_provider.store_match_phone_number.phone_number = '223-455-7890'

        # mock up store
        address_store_record = ParsedLoaderRecord(address_id = None, street_number = '42', street = 'Woot Ln',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 1, latitude = 1, suite_numbers = None, complex = None, source_date = datetime(2012, 12, 25))

        # mock up company ids
        self.sql_provider.company_ids_per_name["David Gage"] = 41

        # mock up sectors
        self.sql_provider.sector_id_per_name["Specialty"] = 1
        self.sql_provider.sector_id_per_name["Music"] = 2

        # mock existing sectors
        self.sql_provider.sector_ids_per_company[41] = [1, 2, 3, 4]

        # mock up fake company
        company = CompanyInfo('David Gage', [Sector('Music', 'Yes'), Sector('Specialty', 'Yes')],
            [Competitor.init_with_company_id_query('David Gage', 'Upton Basses', '1')], [address_store_record], "Woot_2012_12_25", ticker = 'DGAGE', records = ['woot'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._save()
        loader._close_old_companies_sectors()

        # old sectors are [1, 2, 3, 4]
        # new sectors are [1, 2]

        self.assertEqual(loader._company_info.deleted_sector_ids, [3, 4])

    def test_close_old_company_competitors(self):
        # mock up addresses / store data
        self.sql_provider.addresses_within_range.append(ParsedLoaderRecord(43, '43', 'Woot Ln East', 'Wootville', 'WT', '1337', None, SignalDecimal(1.9999),
            SignalDecimal(2.0001), source_date = datetime(2012, 12, 24)))
        self.sql_provider.store_match_phone_number = Store()
        self.sql_provider.store_match_phone_number.address_id = 43
        self.sql_provider.store_match_phone_number.phone_number = '223-455-7890'

        # mock up company ids
        self.sql_provider.company_ids_per_name["David Gage"] = 41

        # mock up existing competitors
        self.sql_provider.open_competitive_companies_per_company[41] = [53, 54]

        # mock two stores=
        address_store_record = ParsedLoaderRecord(address_id = None, street_number = '43', street = 'Woot Ln East',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 2, latitude = 2, suite_numbers = None, complex = None, source_date = datetime(2012, 12, 25))

        # mock up fake company
        company = CompanyInfo('David Gage', [Sector('Music', 'Yes')], [], [address_store_record], "Woot_2012_12_25", ticker = 'DGAGE', records = ['woot'])


        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._save()
        loader._close_old_company_competitors()

        self.assertEqual(loader._company_info.deleted_competitor_ids, [53, 54])

    def test_close_old_stores(self):
        # mock two stores
        parsed_record_1 = ParsedLoaderRecord(address_id = None, street_number = '42', street = 'Woot Ln',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 1, latitude = 1, suite_numbers = None, complex = None, source_date = datetime(2012, 12, 25))
        parsed_record_2 = ParsedLoaderRecord(address_id = None, street_number = '43', street = 'Woot Ln East',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 2, latitude = 2, suite_numbers = None, complex = None, source_date = datetime(2012, 12, 25))

        # set mocked data
        self.sql_provider.store_match_phone_number = Store()
        self.sql_provider.store_match_phone_number.address_id = 43
        self.sql_provider.store_match_phone_number.phone_number = '223-455-7890'

        # set up fake company id and store_ids
        self.sql_provider.company_ids_per_name["David Gage"] = 41
        self.sql_provider.store_ids_and_opened_dates_for_company[41] = []
        for store_id in range(1, 5):
            store = Store()
            store.store_id = store_id
            store.assumed_open_date = datetime(2012, 12, store_id)
            self.sql_provider.store_ids_and_opened_dates_for_company[41].append(store)

        # mock up fake company
        company = CompanyInfo('David Gage', [Sector('Music', 'Yes'), Sector('Specialty', 'Yes')],
            [Competitor.init_with_company_id_query('David Gage', 'Upton Basses', '1')], [parsed_record_1, parsed_record_2], "Woot_2012_12_25", ticker = 'DGAGE', records = ['rob', 'is'])

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._save()
        loader._close_stores_and_log()

        self.assertEqual(loader._company_info.deleted_store_ids, range(1, 5))
        self.assertEqual(self.sql_provider.other_stores, loader._company_info.stores)
        self.assertEqual(self.sql_provider.deleted_stores, loader._company_info.deleted_store_ids)
        self.assertEqual(set(self.sql_provider.closed_store_and_date.values()), set([loader._company_info.as_of_date]))


    def test_load_several_companies(self):
        # up 2 files
        file_1 = 'Woot_2012_1_1.xlsx'
        file_2 = 'Woot_2012_2_2.xlsx'
        file_3 = 'Woot_2012_2_3.xlsx'

        # mock up 2 addresses
        parsed_record_1 = ParsedLoaderRecord(None, "1", "street", "city", "state", "1111", 840, 1, -1, None, datetime(2012, 1, 1))
        parsed_record_2 = ParsedLoaderRecord(None, "2", "street2", "city2", "state2", "2222", 840, 2, -2, None, datetime(2012, 2, 2))
        parsed_record_3 = ParsedLoaderRecord(None, "3", "street3", "city3", "state3", "333", 840, 3, -3, None, datetime(2012, 2, 3))

        # mock up 2 companies
        company1 = CompanyInfo("company1", [Sector('Test', 'Yes')], [], [parsed_record_1], file_1, records = ['rob'])
        company2 = CompanyInfo("company2", [Sector('Test', 'Yes')], [], [parsed_record_2], file_2, records = ['is'])
        company3 = CompanyInfo("company3", [Sector('Test', 'Yes')], [], [parsed_record_3], file_3, records = ['good at bass'])
        self.excel_provider.files[file_1] = company1
        self.excel_provider.files[file_2] = company2
        self.excel_provider.files[file_3] = company3

        # load three companies
        files = [file_3, file_1, file_2]
        report = Loader.load_companies(files)

        # verify that both companies ran successfully and in the correct sequence
        self.assertEqual(report.successful_list[0], file_1)
        self.assertEqual(report.successful_list[1], file_2)
        self.assertEqual(report.successful_list[2], file_3)
        self.assertEqual(len(report.failed_list), 0)

    def test_empty_sectors_not_saved(self):
        # mock two stores
        address = Address.standard_init(address_id = None, street_number = 42, street = 'Woot Ln',
            city = 'Wootville', state = 'WT', zip_code = '1337', country_id = None, longitude = 1, latitude = 1, suite_numbers = None, complex = None)

        # mock up sector
        self.sql_provider.sector_id_per_name["OK"] = 1

        # mock up fake company
        company = CompanyInfo('David Gage', [Sector('', 'Yes'), Sector(None, 'Yes'), Sector("OK", "Yes")], [], [address], 'Woot_2012_12_25.xlsx', ticker = '')

        # process and verify directories has two files
        loader = Loader(company)
        loader._initialize()
        loader._insert_sectors()

        # make sure only the good sector was saved
        self.assertEqual(len(self.sql_provider.test_company_sectors), 1)
        self.assertEqual(self.sql_provider.test_company_sectors[0].sector_name, "OK")


    def test_load_master_competition_file(self):
        file = 'master_competition_file.xlsx'
        competition_1 = Competitor.simple_init(1, 2, 1, datetime(1900, 1, 1, 0, 0))
        competition_2 = Competitor.simple_init(5, 5, .7, datetime(1900, 3, 3, 0, 0))
        # this will be ignored
        competition_3 = Competitor.simple_init(3, 4, 0, datetime(1900, 2, 2, 0, 0))
        competition_4 = Competitor.simple_init(5, 5, 0, datetime(1900, 3, 3, 0, 0))

        master_competition_excel_provider = Dependency('MasterCompetitionExcelProvider').value
        master_competition_excel_provider.files[file] = [competition_1, competition_2, competition_3, competition_4]
        Loader.load_master_competition_file(file)

        competitors = self.sql_provider.test_company_competitors
        self.assertEqual(2, len(competitors))
        self.assertEqual(1, competitors[0].home_company_id)
        self.assertEqual(2, competitors[0].away_company_id)
        self.assertEqual(1, competitors[0].competition_strength)
        self.assertEqual(5, competitors[1].home_company_id)
        self.assertEqual(5, competitors[1].away_company_id)
        self.assertEqual(.7, competitors[1].competition_strength)

