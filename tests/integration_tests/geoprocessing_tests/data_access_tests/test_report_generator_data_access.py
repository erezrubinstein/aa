import unittest
from geoprocessing.business_logic.business_objects.data_check import DataCheck
from geoprocessing.business_logic.config import Config
from geoprocessing.business_logic.enums import DataCheckTypeRef
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_check_handler import get_non_sql_data_check_rowcounts
from geoprocessing.data_access.data_repository import DataRepository
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import insert_test_data_check_type, delete_test_data_check, delete_data_check_type

class ReportGeneratorDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)

    @classmethod
    def tearDownClass(cls):
        dependencies.clear()

    def test_get_non_sql_data_check_rowcounts(self):
        sql = 'UNITTEST_SQL'
        severity_level = 0
        fail_threshold = -1
        data_check_type_id = -1
        data_check_type_name = 'UNITTEST_DATA_CHECK_TYPE'
        entity_type_id = 1

        data_check_with_sql_id = None

        data_checks = {}

        try:
            row_count_before = self.__get_row_count_from_rows(get_non_sql_data_check_rowcounts())

            # create negative test stuffs
            insert_test_data_check_type(data_check_type_id, data_check_type_name, entity_type_id, sql, severity_level, fail_threshold)
            data_check_with_sql = DataCheck.pre_init(data_check_type_id)
            data_check_with_sql_id = self._SQL_data_repository.save_data_check(data_check_with_sql)

            # create data checks with one of each type of DataCheckTypeRef
            for value in DataCheckTypeRef.get_values():
                data_checks[value] = self._SQL_data_repository.save_data_check(DataCheck.pre_init(value))

            row_count_after = self.__get_row_count_from_rows(get_non_sql_data_check_rowcounts())

            self.assertEqual(row_count_before + len(data_checks), row_count_after)
        except:
            raise
        finally:
            if data_check_with_sql_id is not None:
                delete_test_data_check(data_check_with_sql_id)
            for data_check_id in data_checks.itervalues():
                delete_test_data_check(data_check_id)
            delete_data_check_type(data_check_type_id)



    def __get_row_count_from_rows(self, rows):
        row_count_after = 0
        for row in get_non_sql_data_check_rowcounts():
            row_count_after += row.count
        return row_count_after

if __name__ == '__main__':
    unittest.main()
