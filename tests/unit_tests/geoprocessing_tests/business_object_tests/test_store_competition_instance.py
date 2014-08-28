from datetime import datetime
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance

__author__ = 'erezrubinstein'

import unittest

class StoreCompetitionInstanceTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_opened_date_property(self):
        # create three stores.  one with both dates, one with assumed date only, and one with no dates.
        # I kept end_dates in both just to verify the properties use the right internal field
        competition_use_opened_date = StoreCompetitionInstance.standard_init(1, 1, 1, 1, 1, 1, "2012-01-01", "2012-12-01", "2012-01-02", "2012-12-02", None, None)
        competition_use_assumed_opened_date = StoreCompetitionInstance.standard_init(1, 1, 1, 1, 1, 1, None, "2012-12-01", "2012-01-02", "2012-12-02", None, None)
        store_no_date = StoreCompetitionInstance.standard_init(1, 1, 1, 1, 1, 1, None, "2012-12-01", None, "2012-12-02", None, None)
        store_no_date_min_date = StoreCompetitionInstance.standard_init(1, 1, 1, 1, 1, 1, datetime(1900, 1, 1), None, datetime(2000, 1, 1), None, None, None)
        store_no_date_min_date_str = StoreCompetitionInstance.standard_init(1, 1, 1, 1, 1, 1, "1900-01-01", None, datetime(2000, 1, 1), None, None, None)

        # verify that each store has the right opened_date
        self.assertEqual(competition_use_opened_date.opened_date, "2012-01-01")
        self.assertEqual(competition_use_assumed_opened_date.opened_date, "2012-01-02")
        self.assertIsNone(store_no_date.opened_date)
        self.assertEqual(store_no_date_min_date.opened_date, datetime(2000, 1, 1))
        self.assertEqual(store_no_date_min_date_str.opened_date, datetime(2000, 1, 1))

    def test_closed_date_property(self):
        # create three stores.  one with both dates, one with assumed date only, and one with no dates.
        # I kept start_dates in both just to verify the properties use the right internal field
        competition_use_closed_date = StoreCompetitionInstance.standard_init(1, 1, 1, 1, 1, 1, "2012-01-01", "2012-12-01", "2012-01-02", "2012-12-02", None, None)
        store_use_assumed_closed_date = StoreCompetitionInstance.standard_init(1, 1, 1, 1, 1, 1, "2012-01-01", None, "2012-01-02", "2012-12-02", None, None)
        competition_no_date = StoreCompetitionInstance.standard_init(1, 1, 1, 1, 1, 1, "2012-01-01", None, "2012-01-02", None, None, None)

        # verify that each store has the right opened_date
        self.assertEqual(competition_use_closed_date.closed_date, "2012-12-01")
        self.assertEqual(store_use_assumed_closed_date.closed_date, "2012-12-02")
        self.assertIsNone(competition_no_date.closed_date)

if __name__ == '__main__':
    unittest.main()
