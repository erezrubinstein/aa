from common.utilities.Logging.runtime_profiler import RunTimeProfiler
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from datetime import datetime
from time import sleep
import unittest


__author__ = 'erezrubinstein'


class TestSQLLoggingHandler(unittest.TestCase):

    def setUp(self):
        # register mocks
        register_mock_dependencies("DEBUG")

        # get other dependencies
        self.data_repository = Dependency("DataRepository").value

        # create config and change values before registering sql handler
        self._config = Dependency("Config").value
        # set the flush to be .5 seconds so that we can test quickly
        self._config.sql_logging_insert_timer = .1
        self._config.app_version = "9.9.9.9"
        self._config.environment = "unit test"

        # create logger with only SQLLoggingHandler
        self.logger = Dependency("LogManager").value
        self.logger.clear_logging_handlers()
        self.sql_handler = self.logger.add_sql_handler()

    def tearDown(self):
        self.sql_handler.wait_for_threads_to_finish()
        dependencies.clear()

    def test_basic_message(self):
        self.logger.debug("test message")

        # you need to sleep for one second so that the logger flushes correctly
        sleep(.3)

        # make sure only one record is present
        self.assertEqual(len(self.data_repository.logging_records), 1)

        # make sure values are correct
        record = self.data_repository.logging_records[0]
        self.assertEqual(record.log_entry_type_id, 5)
        self.assertEqual(record.version, "9.9.9.9")
        self.assertEqual(record.environment, "unit test")
        # process id is 234234234_process
        self.assertRegexpMatches(record.process_id, "\d*_.*")
        self.assertEqual(record.message.strip(), "test message")
        # compare timestamp without seconds
        utc = str(datetime.utcnow())
        self.assertEqual(utc.split()[0], record.time.split()[0])
        self.assertEqual(record.function_name, "test_sql_logging_handler.py__test_basic_message")
        self.assertIsNone(record.elapsed_time)

    def test_basic_message_with_elapsed_time(self):
        self.logger.debug("test message", elapsed_time=20.1)

        # you need to sleep for one second so that the logger flushes correctly
        sleep(.3)

        # make sure only one record is present
        self.assertEqual(len(self.data_repository.logging_records), 1)

        # make sure values are correct
        record = self.data_repository.logging_records[0]
        self.assertEqual(record.log_entry_type_id, 5)
        self.assertEqual(record.version, "9.9.9.9")
        self.assertEqual(record.environment, "unit test")
        # process id is 234234234_process
        self.assertRegexpMatches(record.process_id, "\d*_.*")
        self.assertEqual(record.message.strip(), "test message")
        # compare timestamp without seconds
        utc = str(datetime.utcnow())
        self.assertEqual(utc.split()[0], record.time.split()[0])
        self.assertEqual(record.function_name, "test_sql_logging_handler.py__test_basic_message_with_elapsed_time")
        self.assertEqual(record.elapsed_time, 20.1)

    def test_all_message_levels(self):
        """
        This test combines critical, error, warning, info, and debug together.
        This is done to save time since we have to wait for the flushing operation
        """
        self.logger.debug("test debug", elapsed_time=1.1)
        self.logger.info("test info", elapsed_time=2.2)
        self.logger.warning("test warning", elapsed_time=3.3)
        self.logger.error("test error", elapsed_time=4.4)
        self.logger.critical("test critical", elapsed_time=5.5)

        # you need to sleep for one second so that the logger flushes correctly
        sleep(.3)

        # make sure we have 5 records
        self.assertEqual(len(self.data_repository.logging_records), 5)

        # make sure every record's type is correct
        self.assertEqual(self.data_repository.logging_records[0].log_entry_type_id, 5)
        self.assertEqual(self.data_repository.logging_records[0].message.strip(), "test debug")
        self.assertEqual(self.data_repository.logging_records[0].elapsed_time, 1.1)
        self.assertEqual(self.data_repository.logging_records[1].log_entry_type_id, 4)
        self.assertEqual(self.data_repository.logging_records[1].message.strip(), "test info")
        self.assertEqual(self.data_repository.logging_records[1].elapsed_time, 2.2)
        self.assertEqual(self.data_repository.logging_records[2].log_entry_type_id, 3)
        self.assertEqual(self.data_repository.logging_records[2].message.strip(), "test warning")
        self.assertEqual(self.data_repository.logging_records[2].elapsed_time, 3.3)
        self.assertEqual(self.data_repository.logging_records[3].log_entry_type_id, 2)
        self.assertEqual(self.data_repository.logging_records[3].message.strip(), "test error")
        self.assertEqual(self.data_repository.logging_records[3].elapsed_time, 4.4)
        self.assertEqual(self.data_repository.logging_records[4].log_entry_type_id, 1)
        self.assertEqual(self.data_repository.logging_records[4].message.strip(), "test critical")
        self.assertEqual(self.data_repository.logging_records[4].elapsed_time, 5.5)

    def test_runtime_profiler_function_exception(self):
        """
        This test makes sure that any logging call from the RunTimeProfiler class does not write RunTimeProfiler.start/exit as its function.
        Instead, it goes one function out
        """
        with RunTimeProfiler("test message", self.logger):
            pass

        # you need to sleep for one second so that the logger flushes correctly
        sleep(.3)

        # make sure we have 5 records
        self.assertEqual(len(self.data_repository.logging_records), 2)
        # test the starting message
        self.assertEqual(self.data_repository.logging_records[0].log_entry_type_id, 5)
        self.assertEqual(self.data_repository.logging_records[0].message.strip(), "starting test message")
        self.assertEqual(self.data_repository.logging_records[0].function_name, "test_sql_logging_handler.py__test_runtime_profiler_function_exception")
        # test the ending message
        self.assertEqual(self.data_repository.logging_records[1].log_entry_type_id, 4)
        self.assertRegexpMatches(self.data_repository.logging_records[1].message.strip(), "ending test message.*")
        self.assertEqual(self.data_repository.logging_records[1].function_name, "test_sql_logging_handler.py__test_runtime_profiler_function_exception")


if __name__ == '__main__':
    unittest.main()
