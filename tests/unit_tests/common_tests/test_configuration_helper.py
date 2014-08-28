import unittest
from common.helpers.configuration_helper import get_mongodbo_host

__author__ = 'jsternberg'


class ConfigurationHelperTests(unittest.TestCase):
    def test_get_host_from_mongodb_host(self):
        config = {'MONGODB_HOST': 'testhost'}
        self.assertEqual('testhost', get_mongodbo_host(config))

    def test_get_host_from_mongodb_settings(self):
        config = {'MONGODB_SETTINGS': {'host': 'anotherhost'}}
        self.assertEqual('anotherhost', get_mongodbo_host(config))
