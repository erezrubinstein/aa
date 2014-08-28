import datetime
import unittest
import logging

from common.utilities.Logging.log_manager import LogManager
from common.helpers.mock_providers.mock_logger import MockLogger

__author__ = 'jsternberg'

class LogManagerTests(unittest.TestCase):

    def setUp(self):
        self.msgs = [1, 10.24, "blah", datetime.datetime.utcnow()]
        self.expected_kwargs = {'extra': {'elapsed_time': None,
                                          'function': None,
                                          'entity': None}}

    def test_log_critical(self):
        expected_kwargs = self.expected_kwargs
        expected_kwargs["extra"]["function"] = 'test_log_manager.py__test_log_critical'
        logmgr = LogManager(logging.CRITICAL)
        logmgr._logger = MockLogger()
        logmgr._mongo_logger = MockLogger()
        for m in self.msgs:
            logmgr.critical("sub test: %s", m)
            self.assertIn("sub test: %s" % m, logmgr._logger.message)
            self.assertEqual(logmgr._logger.args, (m,))
            self.assertEqual(logmgr._logger.kwargs, expected_kwargs)

    def test_log_error(self):
        expected_kwargs = self.expected_kwargs
        expected_kwargs["extra"]["function"] = 'test_log_manager.py__test_log_error'
        logmgr = LogManager(logging.ERROR)
        logmgr._mongo_logger = MockLogger()
        logmgr._logger = MockLogger()
        for m in self.msgs:
            logmgr.error("sub test: %s", m)
            self.assertIn("sub test: %s" % m, logmgr._logger.message)
            self.assertEqual(logmgr._logger.args, (m,))
            self.assertEqual(logmgr._logger.kwargs, expected_kwargs)


    def test_log_warning(self):
        expected_kwargs = self.expected_kwargs
        expected_kwargs["extra"]["function"] = 'test_log_manager.py__test_log_warning'
        logmgr = LogManager(logging.WARNING)
        logmgr._mongo_logger = MockLogger()
        logmgr._logger = MockLogger()
        for m in self.msgs:
            logmgr.warning("sub test: %s", m)
            self.assertIn("sub test: %s" % m, logmgr._logger.message)
            self.assertEqual(logmgr._logger.args, (m,))
            self.assertEqual(logmgr._logger.kwargs, expected_kwargs)


    def test_log_info(self):
        expected_kwargs = self.expected_kwargs
        expected_kwargs["extra"]["function"] = 'test_log_manager.py__test_log_info'
        logmgr = LogManager(logging.INFO)
        logmgr._logger = MockLogger()
        logmgr._mongo_logger = MockLogger()
        for m in self.msgs:
            logmgr.info("sub test: %s", m)
            self.assertIn("sub test: %s" % m, logmgr._logger.message)
            self.assertEqual(logmgr._logger.args, (m,))
            self.assertEqual(logmgr._logger.kwargs, expected_kwargs)


    def test_log_debug(self):
        expected_kwargs = self.expected_kwargs
        expected_kwargs["extra"]["function"] = 'test_log_manager.py__test_log_debug'
        logmgr = LogManager(logging.DEBUG)
        logmgr._mongo_logger = MockLogger()
        logmgr._logger = MockLogger()
        for m in self.msgs:
            logmgr.debug("sub test: %s", m)
            self.assertIn("sub test: %s" % m, logmgr._logger.message)
            self.assertEqual(logmgr._logger.args, (m,))
            self.assertEqual(logmgr._logger.kwargs, expected_kwargs)


if __name__ == '__main__':
    unittest.main()
