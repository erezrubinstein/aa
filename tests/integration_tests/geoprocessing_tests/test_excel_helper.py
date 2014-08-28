import os
import unittest
import datetime
from common.utilities.inversion_of_control import dependencies, Dependency
from common.utilities.signal_math import SignalDecimal
from geoprocessing.business_logic.business_objects.company import Company
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies
from geoprocessing.helpers.excel_helper import CompanyExcelReader, MasterCompetitionExcelReader
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import delete_test_companies_and_competitive_companies, delete_test_company
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository

__author__ = 'spacecowboy'

class TestExcelHelper(unittest.TestCase):

    def setUp(self):
        register_concrete_dependencies(False)
        self.sql_provider = Dependency("DataRepository").value

        # get current path for files
        self.current_folder = os.path.dirname(__file__)

    def tearDown(self):
        dependencies.clear()

    def test_add_workbook(self):
        file = os.path.join(self.current_folder, 'test_data/woot_2012_10_5.xls')
        parser = CompanyExcelReader()
        parser._get_company_info(file)
        parser._read_workbook(file)
        self.assertIsNotNone(parser._book)

    def test_get_rows_from_workbook(self):
        file = os.path.join(self.current_folder, 'test_data/woot_2012_10_5.xls')
        parser = CompanyExcelReader()
        parser._get_company_info(file)
        parser._read_workbook(file)
        self.assertEqual(len(parser._rows), 6)

    def test_parse_excel_file_for_loader(self):
        try:
            file = os.path.join(self.current_folder, 'test_data/woot_2012_10_5.xls')
            parser = CompanyExcelReader()
            parser.read_manila_excel_file(file)

            self.assertEqual(parser._company_info.company_name, 'Woot Random Stuff Inc')
            self.assertEqual(parser._company_info.ticker, 'Woot')
            self.assertEqual(parser._company_info.sectors[0].sector_name, 'Random Stuff')
            self.assertEqual(parser._company_info.sectors[0].is_primary, True)

            self.assertEqual(parser._company_info.parsed_records[0].street_number, str(409))
            self.assertEqual(parser._company_info.parsed_records[0].street, 'East Putnam Avenue')
            self.assertEqual(parser._company_info.parsed_records[0].city, 'Cos Cob')
            self.assertEqual(parser._company_info.parsed_records[0].state, 'CT')
            self.assertEqual(parser._company_info.parsed_records[0].zip_code, '06807')
            self.assertEqual(parser._company_info.parsed_records[0].phone_number, '2038696087')
            self.assertEqual(parser._company_info.parsed_records[0].longitude, SignalDecimal(1))
            self.assertEqual(parser._company_info.parsed_records[0].latitude, SignalDecimal(1))
            self.assertEqual(parser._company_info.records[0], '{"RecordType": "D", "Action": "C", "LoaderRecordID": "555aaa", "Address": "409 East Putnam Avenue", "City": "Cos Cob", "State": "CT", "Zip": "6807", "Phone": "2038696087", "Country": "None", "MallName": "Roosevelt", "OpenedOn": "2012-05-05 00:00:00", "Suite": "A", "CompanyGeneratedStoreNum": "1.0", "StoreFormat": "format1", "Note": "LOL", "Longitude": "1.0", "Latitude": "1.0"}')

            self.assertEqual(parser._company_info.parsed_records[0].source_date, datetime.datetime(2012, 10, 5))
            self.assertEqual(parser._company_info.parsed_records[0].opened_on, datetime.datetime(2012, 5, 5))
            self.assertEqual(parser._company_info.parsed_records[0].loader_opened_on, datetime.datetime(2012, 5, 5))
            self.assertEqual(parser._company_info.parsed_records[0].note, 'LOL')
            self.assertEqual(parser._company_info.parsed_records[0].core_store_id, "555aaa")
            self.assertEqual(parser._company_info.parsed_records[0].store_format, 'format1')
            self.assertEqual(parser._company_info.parsed_records[0].suite_numbers, 'A')
            self.assertEqual(parser._company_info.parsed_records[0].company_generated_store_number, '1.0')
            self.assertEqual(parser._company_info.parsed_records[0].loader_record_id, '555aaa')

            # suite is in the address name
            self.assertEqual(parser._company_info.parsed_records[1].street_number.strip(), str(2156))
            self.assertEqual(parser._company_info.parsed_records[1].street, 'Rob Ave')
            self.assertEqual(parser._company_info.parsed_records[1].state, 'NJ')
            self.assertEqual(parser._company_info.parsed_records[1].core_store_id, '777')
            self.assertEqual(parser._company_info.parsed_records[1].city, 'Eatontown')
            self.assertEqual(parser._company_info.parsed_records[1].zip_code, '07724')
            self.assertEqual(parser._company_info.parsed_records[1].phone_number, '7325421800')
            self.assertEqual(parser._company_info.parsed_records[1].longitude, SignalDecimal(2))
            self.assertEqual(parser._company_info.parsed_records[1].latitude, SignalDecimal(2))

            self.assertEqual(parser._company_info.parsed_records[1].source_date, datetime.datetime(2012, 10, 5))
            self.assertEqual(parser._company_info.parsed_records[1].opened_on, datetime.datetime(2013, 5, 5))
            self.assertEqual(parser._company_info.parsed_records[1].loader_opened_on, datetime.datetime(2013, 5, 5))
            self.assertEqual(parser._company_info.parsed_records[1].note, 'OMG')
            self.assertEqual(parser._company_info.parsed_records[1].store_format, 'format2')
            self.assertEqual(parser._company_info.parsed_records[1].suite_numbers, 'B')
            self.assertEqual(parser._company_info.parsed_records[1].company_generated_store_number, '2.0')
            self.assertEqual(parser._company_info.parsed_records[1].loader_record_id, '777')

            # no suite no open date
            self.assertEqual(parser._company_info.parsed_records[2].street_number, str(7))
            self.assertEqual(parser._company_info.parsed_records[2].street, 'Marie Dr')
            self.assertEqual(parser._company_info.parsed_records[2].opened_on, datetime.datetime(1900, 1, 1))
            self.assertEqual(parser._company_info.parsed_records[2].loader_opened_on, None)
            self.assertEqual(parser._company_info.parsed_records[2].city, 'Highland Park')
            self.assertEqual(parser._company_info.parsed_records[2].state, 'IL')
            self.assertEqual(parser._company_info.parsed_records[2].zip_code, '60035')
            self.assertEqual(parser._company_info.parsed_records[2].phone_number, '8479268357')
            self.assertEqual(parser._company_info.parsed_records[2].longitude, SignalDecimal(3))
            self.assertEqual(parser._company_info.parsed_records[2].latitude, SignalDecimal(3))

            self.assertEqual(parser._company_info.parsed_records[2].source_date, datetime.datetime(2012, 10, 5))
            self.assertEqual(parser._company_info.parsed_records[2].note, 'WTF')
            self.assertEqual(parser._company_info.parsed_records[2].store_format, 'format3')
            self.assertEqual(parser._company_info.parsed_records[2].suite_numbers, None)
            self.assertEqual(parser._company_info.parsed_records[2].core_store_id, '888')
            self.assertEqual(parser._company_info.parsed_records[2].company_generated_store_number, '3.0')
            self.assertEqual(parser._company_info.parsed_records[2].loader_record_id, '888')
        finally:
            # delete all companies since they can save themselves
            for company in parser._company_info.parsed_records:
                delete_test_company(company.company_id)

    def test_read_manila_excel_file_no_phone_number(self):
        """
        We took the phone number out of one of the records to account for this case
        """
        try:
            file = os.path.join(self.current_folder, 'test_data/woot_2012_10_5_no_phone_number.xlsx')
            parser = CompanyExcelReader()
            parser.read_manila_excel_file(file)

            self.assertEqual(parser._company_info.company_name, 'Woot Random Stuff Inc')
            self.assertEqual(parser._company_info.ticker, 'Woot')
            self.assertEqual(parser._company_info.sectors[0].sector_name, 'Random Stuff')
            self.assertEqual(parser._company_info.sectors[0].is_primary, True)

            self.assertEqual(parser._company_info.parsed_records[0].street_number, str(409))
            self.assertEqual(parser._company_info.parsed_records[0].street, 'East Putnam Avenue')
            self.assertEqual(parser._company_info.parsed_records[0].city, 'Cos Cob')
            self.assertEqual(parser._company_info.parsed_records[0].state, 'CT')
            self.assertEqual(parser._company_info.parsed_records[0].zip_code, '06807')
            self.assertEqual(parser._company_info.parsed_records[0].phone_number, None)
            self.assertEqual(parser._company_info.parsed_records[0].longitude, 1)
            self.assertEqual(parser._company_info.parsed_records[0].latitude, 1)
        finally:
            # delete all companies since they can save themselves
            for company in parser._company_info.parsed_records:
                delete_test_company(company.company_id)

    def test_read_manila_excel_file(self):
        try:
            file = os.path.join(self.current_folder, 'test_data/woot_2012_10_5.xls')
            parser = CompanyExcelReader()
            parser.read_manila_excel_file(file)

            self.assertEqual(parser._company_info.company_name, 'Woot Random Stuff Inc')
            self.assertEqual(parser._company_info.ticker, 'Woot')
            self.assertEqual(parser._company_info.sectors[0].sector_name, 'Random Stuff')
            self.assertEqual(parser._company_info.sectors[0].is_primary, True)

            self.assertEqual(parser._company_info.parsed_records[0].street, 'East Putnam Avenue')
            self.assertEqual(parser._company_info.parsed_records[0].city, 'Cos Cob')
            self.assertEqual(parser._company_info.parsed_records[0].state, 'CT')
            self.assertEqual(parser._company_info.parsed_records[0].zip_code, '06807')
            self.assertEqual(parser._company_info.parsed_records[0].phone_number, '2038696087')
            self.assertEqual(parser._company_info.parsed_records[0].longitude, 1)
            self.assertEqual(parser._company_info.parsed_records[0].latitude, 1)

            self.assertEqual(parser._company_info.parsed_records[1].street_number, str(2156))
            self.assertEqual(parser._company_info.parsed_records[1].street, 'Rob Ave')
            self.assertEqual(parser._company_info.parsed_records[1].state, 'NJ')
            self.assertEqual(parser._company_info.parsed_records[1].city, 'Eatontown')
            self.assertEqual(parser._company_info.parsed_records[1].zip_code, '07724')
            self.assertEqual(parser._company_info.parsed_records[1].phone_number, '7325421800')
            self.assertEqual(parser._company_info.parsed_records[1].longitude, 2)
            self.assertEqual(parser._company_info.parsed_records[1].latitude, 2)

            self.assertEqual(parser._company_info.parsed_records[2].street_number, str(7))
            self.assertEqual(parser._company_info.parsed_records[2].street, 'Marie Dr')
            self.assertEqual(parser._company_info.parsed_records[2].city, 'Highland Park')
            self.assertEqual(parser._company_info.parsed_records[2].state, 'IL')
            self.assertEqual(parser._company_info.parsed_records[2].zip_code, '60035')
            self.assertEqual(parser._company_info.parsed_records[2].phone_number, '8479268357')
            self.assertEqual(parser._company_info.parsed_records[2].longitude, 3)
            self.assertEqual(parser._company_info.parsed_records[2].latitude, 3)
        finally:
            # delete all companies since they can save themselves
            for company in parser._company_info.parsed_records:
                delete_test_company(company.company_id)

    def test_read_master_competition_file(self):
        try:
            start_date = datetime.datetime(1900, 1, 1, 0, 0)

            file = os.path.join(self.current_folder, 'test_data/master_competition_file.xlsx')
            parser = MasterCompetitionExcelReader()
            parser.read_master_competition_file(file)

            competitions = parser._competitions
            dupe_competitions = parser._dupe_competitions

            self.assertEqual(27, len(competitions))
            self.assertEqual(2, len(dupe_competitions))

            # count self competitions
            self_competitions = 0

            # count number of checks
            num_loop_checks = 0

            for comp in competitions:
                # check that the first instance of Athleta/Nike is used
                if comp.home_company == 'unittest_Athleta' and comp.away_company == 'unittest_Nike':
                    self.assertEqual(1, comp.competition_strength)
                    num_loop_checks += 1
                elif comp.away_company == 'unittest_Athleta' and comp.home_company == 'unittest_Nike':
                    self.assertEqual(2, comp.competition_strength)
                    num_loop_checks += 1
                elif comp.home_company == comp.away_company:
                    self_competitions += 1



            self.assertEqual(7, self_competitions)
            self.assertEqual(2, num_loop_checks)

            # do some not-so-random spot checks
            # at index 10, it should have skipped the dupe
            i = 10
            self.assertEqual(competitions[i].home_company, 'unittest_Nike')
            self.assertEqual(competitions[i].away_company, 'unittest_Calvin Klein PERFORMANCE')
            self.assertEqual(competitions[i].competition_strength, 1)
            self.assertEqual(competitions[i].start_date, start_date)

            # at index 20, we should have the first self-competition
            # since python sets don't guarantee order, we can't anticipate the actual company names here,
            # just that they are the same
            i = 20
            self.assertEqual(competitions[i].home_company, competitions[i].away_company)
            self.assertEqual(competitions[i].competition_strength, 1)
            self.assertEqual(competitions[i].start_date, start_date)

            # at index 26, we should have the last self-competition
            i = 26
            self.assertEqual(competitions[i].home_company, competitions[i].away_company)
            self.assertEqual(competitions[i].competition_strength, 1)
            self.assertEqual(competitions[i].start_date, start_date)
        finally:
            delete_test_companies_and_competitive_companies()

    def test_read_master_competition_file_asterix(self):
        # mock up data repository just for this one test.  This should not be the case, but the logic of "adding" companies is baked into the excel provider.
        mock_data_provider = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", mock_data_provider)

        # mock up three companies
        mock_data_provider.all_companies = [Company.standard_init(1, "", "Company1", None, None),
                                            Company.standard_init(2, "", "Company2", None, None),
                                            Company.standard_init(3, "", "Company3", None, None)]

        # parse the asterix file
        file = os.path.join(self.current_folder, 'test_data/master_competition_file_asterix.xlsx')
        parser = MasterCompetitionExcelReader()
        parser.read_master_competition_file(file)

        # verify that every company competes with every company
        self.assertEqual(len(parser._competitions), 9)
        self.assertEqual(parser._competitions[0].home_company_id, 1)
        self.assertEqual(parser._competitions[0].away_company_id, 1)
        self.assertEqual(parser._competitions[1].home_company_id, 1)
        self.assertEqual(parser._competitions[1].away_company_id, 2)
        self.assertEqual(parser._competitions[2].home_company_id, 1)
        self.assertEqual(parser._competitions[2].away_company_id, 3)
        self.assertEqual(parser._competitions[3].home_company_id, 2)
        self.assertEqual(parser._competitions[3].away_company_id, 1)
        self.assertEqual(parser._competitions[4].home_company_id, 2)
        self.assertEqual(parser._competitions[4].away_company_id, 2)
        self.assertEqual(parser._competitions[5].home_company_id, 2)
        self.assertEqual(parser._competitions[5].away_company_id, 3)
        self.assertEqual(parser._competitions[6].home_company_id, 3)
        self.assertEqual(parser._competitions[6].away_company_id, 1)
        self.assertEqual(parser._competitions[7].home_company_id, 3)
        self.assertEqual(parser._competitions[7].away_company_id, 2)
        self.assertEqual(parser._competitions[8].home_company_id, 3)
        self.assertEqual(parser._competitions[8].away_company_id, 3)

