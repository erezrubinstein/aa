import logging
import unittest
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.business_logic.config import Config
from common.utilities.Logging.log_manager import LogManager
from geoprocessing.census_ingest import CensusDatasetIngestor
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_census_ingest_provider import MockCensusIngestProvider
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository

__author__ = 'jsternberg'


class CensusIngestorTests(unittest.TestCase):
    def setUp(self):
        self.__config = Config().instance
        dependencies.register_dependency('Config', self.__config)
        self.__logger = LogManager(logging.ERROR)
        dependencies.register_dependency('LogManager', self.__logger)

        self.__dummy_census_ingest_files = [{'test_table1':
                                        {'file_path':'test_file1.txt',
                                          'db_file_path':'db/test_file1.txt',
                                          'db_format_file_path':'db/test_file1.xml',
                                          'field_delimiter':',',
                                          'skip_first_row':True,
                                          'trim_double_quotes_from_columns':None,
                                          'column_list':['col1','col2']}},
                                      {'test_table2':
                                        {'file_path':'test_file2.dat',
                                          'db_file_path':'db/test_file2.txt',
                                          'db_format_file_path':'db/test_file2.xml',
                                          'field_delimiter':' ',
                                          'skip_first_row':True,
                                          'trim_double_quotes_from_columns':None,
                                          'column_list':['col3','col4']}}]

        self.__dummy_data = [['Ham', 'and', 'jam', 'and', 'spam-alot.'],
                             ['Have', 'to', 'push', 'the', 'pram-alot.']]

        self.__row_counts = [{'table_name': 'test_table1', 'row_count': 2},
                             {'table_name': 'test_table2', 'row_count': 2}]

        self.__db_row_counts = [{'table_name': 'test_table1', 'row_count': 2},
                              {'table_name': 'test_table2', 'row_count': 2}]

        self.data_repository = MockSQLDataRepository()
        dependencies.register_dependency('DataRepository', self.data_repository)



    def tearDown(self):
        dependencies.clear()

    #####################################################################################################################
    #############################################  initialization Tests ################################################
    #####################################################################################################################
    def test_ingestor_initialization_from_normal_config(self):
        #get an ingestor using the mock provider (still reads the normal configs)
        ingestor = CensusDatasetIngestor(MockCensusIngestProvider)

        #make sure the values are initialized correctly
        self.assertEqual(ingestor.census_year, self.__config.census_ingest_year)
        self.assertEqual(ingestor.census_ingest_files, self.__config.census_ingest_files_list)

    def test_ingestor_initialization_from_test_config(self):
        # save off a copy of the normal config list
        save_list = list(self.__config.census_ingest_files_list)
        try:
            # swap in the test config file list
            self.__config.census_ingest_files_list = self.__dummy_census_ingest_files

            #get an ingestor using the mock provider
            ingestor = CensusDatasetIngestor(MockCensusIngestProvider)

            #make sure the values are initialized correctly
            self.assertEqual(ingestor.census_year, self.__config.census_ingest_year)
            self.assertEqual(ingestor.census_ingest_files, self.__config.census_ingest_files_list)

            #get the providers from Dependency using hashes
            cips = [Dependency(cip_hash).value for cip_hash in ingestor.cip_hashes]

            #assert that every test ingest file attribute exists in the providers object collection
            for f in self.__dummy_census_ingest_files:
                table_name = f.keys()[0]
                self.assertIn(table_name, [cip.table_name for cip in cips])
                file_path = f[table_name]['file_path']
                self.assertIn(file_path, [cip.file_path for cip in cips])
                field_delimiter = f[table_name]['field_delimiter']
                self.assertIn(field_delimiter, [cip.field_delimiter for cip in cips])
                column_list = f[table_name]['column_list']
                self.assertIn(column_list, [cip.column_list for cip in cips])
                skip_first_row = f[table_name]['skip_first_row']
                self.assertIn(skip_first_row, [cip.skip_first_row for cip in cips])
        finally:
            #put back the config list
            self.__config.census_ingest_files_list = save_list


    #####################################################################################################################
    #############################################  Read Tests ################################################
    #####################################################################################################################

    def test_read_dataset(self):
        # save off a copy of the normal config list
        save_list = list(self.__config.census_ingest_files_list)
        try:
            # swap in the test config file list
            self.__config.census_ingest_files_list = self.__dummy_census_ingest_files

            #get an ingestor using the mock provider, and make it read the dataset
            ingestor = CensusDatasetIngestor(MockCensusIngestProvider)
            ingestor.read_dataset(10)

            #get the providers from Dependency using hashes
            cips = [Dependency(cip_hash).value for cip_hash in ingestor.cip_hashes]

            #assert dummy data in each provider
            for cip in cips:
                self.assertEqual(cip.census_ingest_data, self.__dummy_data)
        finally:
            #put back the config list
            self.__config.census_ingest_files_list = save_list

    def test_get_census_ingest_data_rowcounts(self):
        # save off a copy of the normal config list
        save_list = list(self.__config.census_ingest_files_list)
        try:
            # swap in the test config file list
            self.__config.census_ingest_files_list = self.__dummy_census_ingest_files

            #get an ingestor using the mock provider, make it read the dataset, get data
            ingestor = CensusDatasetIngestor(MockCensusIngestProvider)
            ingestor.read_dataset(10)
            test_row_counts = ingestor.get_census_ingest_data_row_counts()
            expected_row_counts = '; '.join(['%s: %d rows.' % (rc['table_name'], rc['row_count']) for rc in self.__row_counts])

            #assert first 10 rows
            self.assertEqual(test_row_counts, expected_row_counts)
        finally:
            #put back the config list
            self.__config.census_ingest_files_list = save_list


    def test_get_census_ingest_data(self):
        # save off a copy of the normal config list
        save_list = list(self.__config.census_ingest_files_list)
        try:
            # swap in the test config file list
            self.__config.census_ingest_files_list = self.__dummy_census_ingest_files

            #get an ingestor using the mock provider, make it read the dataset, get data
            ingestor = CensusDatasetIngestor(MockCensusIngestProvider)
            ingestor.read_dataset(10)
            rows_text = ingestor.get_census_ingest_data(0,10)
            expected_rows_text = "\nTable: test_table1\n['Ham', 'and', 'jam', 'and', 'spam-alot.']\n['Have', 'to', 'push', 'the', 'pram-alot.']\n\nTable: test_table2\n['Ham', 'and', 'jam', 'and', 'spam-alot.']\n['Have', 'to', 'push', 'the', 'pram-alot.']"

            #assert first 10 rows
            self.assertEqual(rows_text, expected_rows_text)
        finally:
            #put back the config list
            self.__config.census_ingest_files_list = save_list


    #####################################################################################################################
    #############################################  Save Tests ################################################
    #####################################################################################################################

    def test_save_dataset(self):
        # save off a copy of the normal config list
        save_list = list(self.__config.census_ingest_files_list)
        try:
            # swap in the test config file list
            self.__config.census_ingest_files_list = self.__dummy_census_ingest_files

            #get an ingestor using the mock provider, make it read the dataset, save
            ingestor = CensusDatasetIngestor(MockCensusIngestProvider)
            ingestor.read_dataset(10)
            ingestor.save_dataset()

            #get the providers from Dependency using hashes
            cips = [Dependency(cip_hash).value for cip_hash in ingestor.cip_hashes]
            for cip in cips:
                self.assertEqual(cip.census_ingest_data, self.data_repository.inserted_census_data[hash(cip)])

        finally:
            #put back the config list
            self.__config.census_ingest_files_list = save_list

    def test_get_db_row_counts(self):
        # save off a copy of the normal config list
        save_list = list(self.__config.census_ingest_files_list)
        try:
            # swap in the test config file list
            self.__config.census_ingest_files_list = self.__dummy_census_ingest_files

            #get an ingestor using the mock provider, make it read the dataset, save, validate row counts
            ingestor = CensusDatasetIngestor(MockCensusIngestProvider)
            ingestor.read_dataset(10)
            ingestor.save_dataset()
            ingestor.get_db_row_counts()

            #validations should match
            self.assertEqual(ingestor.db_row_counts, self.__db_row_counts)

        finally:
            #put back the config list
            self.__config.census_ingest_files_list = save_list


    def test_bulk_save_dataset(self):
        # save off a copy of the normal config list
        save_list = list(self.__config.census_ingest_files_list)
        try:
            # swap in the test config file list
            self.__config.census_ingest_files_list = self.__dummy_census_ingest_files

            #get an ingestor using the mock provider, make it read the dataset, bulk save
            ingestor = CensusDatasetIngestor(MockCensusIngestProvider)
            ingestor.read_dataset(10)
            ingestor.bulk_save_dataset()

            #get the providers from Dependency using hashes
            cips = [Dependency(cip_hash).value for cip_hash in ingestor.cip_hashes]
            for cip in cips:
                self.assertEqual(cip.census_ingest_data, self.data_repository.inserted_census_data[hash(cip)])

        finally:
            #put back the config list
            self.__config.census_ingest_files_list = save_list

#####################################################################################################################
###############################################  Main ######### #####################################################
#####################################################################################################################
if __name__ == "__main__":
    unittest.main()
