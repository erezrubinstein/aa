import unittest

from geoprocessing.business_logic.business_objects.data_check import DataCheck, DataCheckType, DataCheckValue
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import delete_test_data_check,  delete_data_check_type, select_test_data_check, select_test_data_check_values, delete_test_entity_type, insert_test_entity_type, insert_test_data_check_type


class DataCheckDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)

    @classmethod
    def tearDownClass(cls):
        dependencies.clear()

    def test_get_data_check_types(self):
        """
        This test verifies that data check types are retrieved correctly from the database
        """
        entity_type_id = -1
        entity_type_name = 'UNITTEST_ENTITY_TYPE'
        sql = 'UNITTEST_SQL'
        severity_level = 0
        fail_threshold = -1
        data_check_type_id = -1
        data_check_type_name = 'UNITTEST_DATA_CHECK_TYPE'
        data_check_type = DataCheckType.standard_init(data_check_type_id, data_check_type_name, entity_type_id, sql, severity_level, fail_threshold)
        try:
            # insert new entity type
            insert_test_entity_type(entity_type_id, entity_type_name)
            # insert new data check type
            insert_test_data_check_type(data_check_type_id, data_check_type_name, entity_type_id, sql, severity_level, fail_threshold)

            # get data check types
            data_check_types = self._SQL_data_repository.get_sql_data_check_types()

            self.assertTrue(data_check_type_id in data_check_types and
                            data_check_types[data_check_type_id] == data_check_type)
        except:
            raise
        finally:
            delete_data_check_type(data_check_type_id)
            delete_test_entity_type(entity_type_id)



    def test_save_data_check(self):
        """
        This test verifies that data checks are saved correctly to the database
        """
        entity_type_id = -1
        entity_type_name = 'UNITTEST_ENTITY_TYPE'
        sql = 'UNITTEST_SQL'
        severity_level = 0
        fail_threshold = -1
        data_check_type_id = -1
        data_check_type_name = 'UNITTEST_DATA_CHECK_TYPE'
        data_check_type = DataCheckType.standard_init(data_check_type_id, data_check_type_name, entity_type_id, sql, severity_level, fail_threshold)
        data_check_id = None
        data_check = DataCheck.pre_init(data_check_type_id)
        value_type = 'UNITTEST_VALUE_TYPE'
        data_check.data_check_values.append(DataCheckValue.pre_init(value_type, 'UNITTEST_EXPECTED_VALUE', 'UNITTEST_ACTUAL_VALUE', -1))
        data_check.data_check_values.append(DataCheckValue.pre_init(value_type, 'UNITTEST_EXPECTED_VALUE', 'UNITTEST_ACTUAL_VALUE', -2))

        try:
            # insert new entity type
            insert_test_entity_type(entity_type_id, entity_type_name)
            insert_test_data_check_type(data_check_type_id, data_check_type_name, entity_type_id, sql, severity_level, fail_threshold)

            # save the data check, retrieve id, set data_check_id on data_check_values
            data_check_id = self._SQL_data_repository.save_data_check(data_check)
            for data_check_value in data_check.data_check_values:
                data_check_value.data_check_id = data_check_id

            # get the data_check back from the db
            row = select_test_data_check(data_check_id)

            data_check_copy = DataCheck.standard_init(row.data_check_id, row.data_check_type_id, row.check_done, row.bad_data_rows)

            # get the data_check_values
            rows = select_test_data_check_values(data_check_id)
            for row in rows:
                data_check_copy.data_check_values.append(DataCheckValue.standard_init(row.data_check_value_id, row.data_check_id, row.value_type, row.expected_value, row.actual_value, row.entity_id))
            data_check.bad_data_rows = len(data_check.data_check_values)

            self.assertEqual(data_check, data_check_copy)
        except:
            raise
        finally:
            if data_check_id is not None:
                #delete_test_data_check_values(data_check_id)
                delete_test_data_check(data_check_id)
            delete_data_check_type(data_check_type_id)
            delete_test_entity_type(entity_type_id)

if __name__ == '__main__':
    unittest.main()