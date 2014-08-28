import unittest
from common.utilities.unit_conversion import UnitConverter

__author__ = 'jsternberg'

class UnitConversionTests(unittest.TestCase):

    def test_meters_to_miles(self):

        uc = UnitConverter()

        miles = uc.meters_to_miles(1)
        # can be None if pint isn't installed
        if miles is not None:
            self.assertEqual(round(miles, 19), 0.0006213711922373339)

        miles = uc.meters_to_miles(1609.34)
        # can be None if pint isn't installed
        if miles is not None:
            self.assertEqual(round(miles, 2), 1.00)


    def test_miles_to_meters(self):

        uc = UnitConverter()

        meters = uc.miles_to_meters(1)
        # can be None if pint isn't installed
        if meters is not None:
            self.assertEqual(round(meters, 3), 1609.344)

        meters = uc.miles_to_meters(0.0006213711922373339)
        # can be None if pint isn't installed
        if meters is not None:
            self.assertEqual(round(meters, 2), 1.00)


if __name__ == '__main__':
    unittest.main()
