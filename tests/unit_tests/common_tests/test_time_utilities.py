# coding=utf-8
import unittest
from common.utilities.time_utilities import human_readable_time, human_readable_timediff

__author__ = 'imashhor'


class TimeUtilitiesTest(unittest.TestCase):
    def test_human_readable_timediff(self):
        start_time = 100000
        end_time = 101000

        self.assertListEqual(['16 minutes', '40 seconds'], human_readable_timediff(start_time, end_time))


    def test_human_readable_time(self):
        self.assertListEqual(['1 week', '5 hours'], human_readable_time(173, "hours"))
        self.assertListEqual(['1 year', '10 months', '2 weeks'], human_readable_time(90, "weeks"))
        self.assertListEqual(['4 hours', '48 minutes', '33 seconds'], human_readable_time(17313, "seconds"))
        self.assertListEqual(['4 hours', '48 minutes', '33 seconds'], human_readable_time(17313.234, "seconds"))
        self.assertListEqual(['3 years', '6 months'], human_readable_time(42, "months"))
        self.assertListEqual(['1 year', '5 months', '3 weeks', '3 days'], human_readable_time(500, "days"))

