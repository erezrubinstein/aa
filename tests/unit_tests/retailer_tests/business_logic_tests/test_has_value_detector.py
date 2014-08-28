import mox
from retailer.common.business_logic.has_value_detector import HasValueDetector
import unittest


class TestHasValueDetector(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(TestHasValueDetector, self).setUp()


    def doCleanups(self):
        # call parent clean up
        super(TestHasValueDetector, self).doCleanups()


    def test_constructor(self):
        """
        The constructor should take a list of non_values and convert only strings to upper case.
        """
        non_values = ["", "null", None]
        hvd = HasValueDetector(non_values)

        # make sure error registered
        self.assertEqual(hvd.non_values, ["", "NULL", None])


    def test_has_value__positive(self):
        non_values = ["", "null", None]
        hvd = HasValueDetector(non_values)

        # verify
        self.assertTrue(hvd.has_value("yes I am an actual value!!"))


    def test_has_value__negative(self):
        non_values = ["", "null", None]
        hvd = HasValueDetector(non_values)

        # verify
        self.assertFalse(hvd.has_value("NULL"))

if __name__ == '__main__':
    unittest.main()
