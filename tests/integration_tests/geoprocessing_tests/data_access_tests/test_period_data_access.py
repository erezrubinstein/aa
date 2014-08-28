from datetime import datetime

from geoprocessing.business_logic.enums import DurationTypes
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.data_access.period_handler import PeriodDurations, select_period_id_force_insert
from geoprocessing.business_logic.business_objects.period import Period
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import select_last_period_id, delete_period, insert_and_return_test_period_id


__author__ = 'erezrubinstein'


__author__ = 'erezrubinstein'

import unittest

class DemographicsDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)

    @classmethod
    def tearDownClass(cls):
        dependencies.clear()


    def test_select_period_id_force_insert(self):
        """
        This method verifies that selecting a period that doesn't exist gets added.
        It also verifies that once added, it always returns the same period
        """
        period_id = None
        try:
            start_date = '20000101'
            end_date = '20900101'
            duration = PeriodDurations.YEAR
    
            # get current latest id to verify new item was inserted after it
            current_last_period_id = select_last_period_id()
    
            # insert new period and verify period_id is after the previous last one
            period_id = select_period_id_force_insert(start_date, end_date, duration)
            self.assertGreater(period_id, current_last_period_id)
    
            # insert again and assert the returned id is the same as before (i.e. no insert)
            same_period_id = select_period_id_force_insert(start_date, end_date, duration)
            self.assertEqual(same_period_id, period_id)
        except:
            raise
        finally:
            if period_id is not None:
                delete_period(period_id)

    def test_select_period_by_period_id(self):
        """
        Make sure we can get a period object from the db by it's period_id.
        This tests every duration type.
        """
        period_id = None
        try:
            before_insert_date_time = datetime.now()
            test_ids = [(insert_and_return_test_period_id(dt),dt) for dt in DurationTypes.get_values()]
            for test_id in test_ids:
                period = Period.select_by_id(test_id[0])
                self.assertEqual(period.period_id, test_id[0])
                # the helper always inserts duration type 5 and getdate() for start and end date
                self.assertEqual(period.duration_type_id, test_id[1])
                self.assertEqual(period.duration_type, test_id[1])
        except:
            raise
        finally:
            for test_id in test_ids:
                if test_id is not None:
                    delete_period(test_id[0])

if __name__ == '__main__':
    unittest.main()