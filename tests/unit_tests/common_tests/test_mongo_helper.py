__author__ = 'horacethomas'

import unittest
import logging
from common.data_access.utilities.mongo_helper import AutoReconnectHandler
from common.data_access.utilities.errors import AutoReconnectRetriesFailed
from pymongo.errors import AutoReconnect


class MongoHelperTests(unittest.TestCase):

    def setUp(self):
        pass


    def test_auto_reconnect_handler(self):

        class Access(object):
            def __init__(self):
                self.tries = []

                # set a logger with low level to prevent display
                self.logger = logging.Logger("TESTLOGGER")
                hdler = logging.StreamHandler()
                hdler.setLevel(logging.CRITICAL)
                self.logger.addHandler(hdler)

            @AutoReconnectHandler(2, .1)
            def mongo_access_func(self):
                self.tries.append("yo")
                raise AutoReconnect

        ac = Access()

        self.assertRaises(AutoReconnectRetriesFailed, ac.mongo_access_func)
        self.assertEqual(len(ac.tries), 2)


if __name__ == '__main__':
    unittest.main()
