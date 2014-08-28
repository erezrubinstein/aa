import mox
from retailer.common.business_logic.has_value_detector import HasValueDetector
import unittest
from search.indexing.store_indexer import StoreIndexer


class TestStoreIndexer(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(TestStoreIndexer, self).setUp()

    def doCleanups(self):
        # call parent clean up
        super(TestStoreIndexer, self).doCleanups()

    # TODO: Need a proper SearchProvider thingy first

if __name__ == '__main__':
    unittest.main()
