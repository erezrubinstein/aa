from datetime import datetime
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import select_test_log_entry_count, select_test_log_entries, delete_test_log_entries
from common.utilities.Logging.sql_logging_handler import LogEntryType, LogEntry


__author__ = 'erezrubinstein'

import unittest

class StoreCompetitionAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)
        delete_test_log_entries()

    @classmethod
    def tearDownClass(cls):
        delete_test_log_entries()
        dependencies.clear()

    def test_insert_logging_records(self):
        try:
            # create fake logging records
            logging_records = [
                LogEntry(6, "version", "environment", "process", str(datetime.utcnow()), "unit test message", "class_func1", None, entity = None),
                LogEntry(6, "version", "environment", "process", str(datetime.utcnow()), "unit test message", "class_func2", 1.1, entity = None)
            ]

            # get count before
            count_before = select_test_log_entry_count()

            # insert into db
            self._SQL_data_repository.insert_logging_records(logging_records)

            # get count after
            count_after = select_test_log_entry_count()

            # make sure the count is incremented by two
            self.assertEqual(count_before + 2, count_after)

            # get values and assert them
            rows = select_test_log_entries()
            self.assertEqual(len(rows), 2)

            # first item
            self.assertGreater(rows[0][0], 0)
            self.assertEqual(rows[0][1], 6)
            self.assertEqual(rows[0][2], "version")
            self.assertEqual(rows[0][3], "environment")
            self.assertEqual(rows[0][4], "process")
            self.assertIsInstance(rows[0][5], datetime)
            self.assertEqual(rows[0][6], "unit test message")
            self.assertIsNone(rows[0][7])
            self.assertEqual(rows[0][8], "class_func1")

            # second item
            self.assertGreater(rows[1][0], 0)
            self.assertEqual(rows[1][1], 6)
            self.assertEqual(rows[1][2], "version")
            self.assertEqual(rows[1][3], "environment")
            self.assertEqual(rows[1][4], "process")
            # this verifies that there are 26 characters in the date string
            self.assertIsInstance(rows[1][5], datetime)
            self.assertEqual(rows[1][6], "unit test message")
            self.assertEqual(rows[1][7], 1.1)
            self.assertEqual(rows[1][8], "class_func2")

        except:
            raise
        finally:
            delete_test_log_entries()


    def test_select_logs_by_log_entry_type_ids(self):
        try:
            # create fake logging records
            logging_records = [
                LogEntry(1, "version", "environment", "process", str(datetime.utcnow()), "unit test message critical", "class_func1", None, entity = None),
                LogEntry(2, "version", "environment", "process", str(datetime.utcnow()), "unit test message error", "class_func2", None, entity = None),
                LogEntry(3, "version", "environment", "process", str(datetime.utcnow()), "unit test message warning", "class_func3", None, entity = None),
            ]

            # insert into db
            self._SQL_data_repository.insert_logging_records(logging_records)

            rows = self._SQL_data_repository.select_logs_by_log_entry_type_ids([LogEntryType.CRITICAL, LogEntryType.ERROR])
            self.assertTrue(self.check_log_entry_in_rows(1, 'process', 'unit test message critical', 'class_func1', rows))
            self.assertTrue(self.check_log_entry_in_rows(2, 'process', 'unit test message error', 'class_func2', rows))
            self.assertFalse(self.check_log_entry_in_rows(3, 'process', 'unit test message warning', 'class_func3', rows))
        except:
            raise
        finally:
            delete_test_log_entries()

    def test_select_function_performance(self):
        try:
            # create fake logging records
            logging_records = [
                LogEntry(6, "version", "environment", "process", str(datetime.utcnow()), "unit test message", "class_func9", 50000000000000, entity = None),
                LogEntry(6, "version", "environment", "process", str(datetime.utcnow()), "unit test message", "class_func9", 60000000000000, entity = None)
            ]

            # insert into db
            self._SQL_data_repository.insert_logging_records(logging_records)

            rows = self._SQL_data_repository.select_function_performance()

            self.assertTrue(self.check_performance_entry_in_rows('class_func9', 55000000000000, 2, rows))
        except:
            raise
        finally:
            delete_test_log_entries()



#####################################################################################################################
###############################################   Helper Methods  ###################################################
#####################################################################################################################

    def check_log_entry_in_rows(self, log_entry_type_id, process_id, message, function_name, rows):
        for row in rows:
            if row.log_entry_type_id == log_entry_type_id and \
                row.process_id == process_id and \
                row.message == message and \
                row.function_name == function_name:
                return True
        return False

    def check_performance_entry_in_rows(self, function_name, avg_secs, count, rows):
        for row in rows:
            if row.function_name == function_name and\
               row.avg_secs == avg_secs and\
               row.count == count:
                return True
        return False

if __name__ == '__main__':
    unittest.main()