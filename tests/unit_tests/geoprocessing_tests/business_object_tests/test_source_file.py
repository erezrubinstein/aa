import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.config import Config
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository
from geoprocessing.business_logic.business_objects.source_file import SourceFile

__author__ = 'jsternberg'

class SourceFileTests(unittest.TestCase):
    def setUp(self):
        # set up mock dependencies
        dependencies.register_dependency("Config", Config().instance)
        self._data_repository = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", self._data_repository)

    def tearDown(self):
        dependencies.clear()

    def test_standard_init(self):
        source_file = SourceFile().standard_init(1024, '/path/to/file.txt', '2012-12-21', '2012-12-22', 1025)
        self.assertEqual(source_file.source_file_id, 1024)
        self.assertEqual(source_file.full_path, '/path/to/file.txt')
        self.assertEqual(source_file.file_created_date, '2012-12-21')
        self.assertEqual(source_file.file_modified_date, '2012-12-22')
        self.assertEqual(source_file.file_size_in_bytes, 1025)

    def test_select_by_id(self):
        db_source_file = SourceFile().standard_init(1024, '/path/to/file.txt', '2012-12-21', '2012-12-22', 1025)
        self._data_repository.source_files[1024] = db_source_file
        test_source_file = SourceFile.select_by_id(1024)
        self.assertEqual(test_source_file, db_source_file)