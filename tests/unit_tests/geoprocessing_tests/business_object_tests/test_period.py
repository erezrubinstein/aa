import unittest
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.config import Config
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository
from geoprocessing.business_logic.business_objects.period import Period
from geoprocessing.business_logic.enums import DurationTypes

__author__ = 'jsternberg'

class PeriodTests(unittest.TestCase):
    def setUp(self):
        # set up mock dependencies
        dependencies.register_dependency("Config", Config().instance)
        self._data_repository = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", self._data_repository)

    def tearDown(self):
        dependencies.clear()

    def test_standard_init(self):
        p = Period().standard_init(101, 1, '1900-01-01', '3000-01-01')
        self.assertEqual(p.period_id, 101)
        self.assertEqual(p.duration_type_id, 1)
        self.assertEqual(p.duration_type, DurationTypes.Year)
        self.assertEqual(p.start_date, '1900-01-01')
        self.assertEqual(p.end_date, '3000-01-01')

        p = Period().standard_init(102, 2, '1900-01-01', '3000-01-01')
        self.assertEqual(p.period_id, 102)
        self.assertEqual(p.duration_type_id, 2)
        self.assertEqual(p.duration_type, DurationTypes.HalfYear)
        self.assertEqual(p.start_date, '1900-01-01')
        self.assertEqual(p.end_date, '3000-01-01')

        p = Period().standard_init(103, 3, '1900-01-01', '3000-01-01')
        self.assertEqual(p.period_id, 103)
        self.assertEqual(p.duration_type_id, 3)
        self.assertEqual(p.duration_type, DurationTypes.Quarter)
        self.assertEqual(p.start_date, '1900-01-01')
        self.assertEqual(p.end_date, '3000-01-01')

        p = Period().standard_init(104, 4, '1900-01-01', '3000-01-01')
        self.assertEqual(p.period_id, 104)
        self.assertEqual(p.duration_type_id, 4)
        self.assertEqual(p.duration_type, DurationTypes.Month)
        self.assertEqual(p.start_date, '1900-01-01')
        self.assertEqual(p.end_date, '3000-01-01')

        p = Period().standard_init(105, 5, '1900-01-01', '3000-01-01')
        self.assertEqual(p.period_id, 105)
        self.assertEqual(p.duration_type_id, 5)
        self.assertEqual(p.duration_type, DurationTypes.Day)
        self.assertEqual(p.start_date, '1900-01-01')
        self.assertEqual(p.end_date, '3000-01-01')

        p = Period().standard_init(106, 6, '1900-01-01', '3000-01-01')
        self.assertEqual(p.period_id, 106)
        self.assertEqual(p.duration_type_id, 6)
        self.assertEqual(p.duration_type, DurationTypes.PointInTime)
        self.assertEqual(p.start_date, '1900-01-01')
        self.assertEqual(p.end_date, '3000-01-01')

        p = Period().standard_init(107, 7, '1900-01-01', '3000-01-01')
        self.assertEqual(p.period_id, 107)
        self.assertEqual(p.duration_type_id, 7)
        self.assertEqual(p.duration_type, DurationTypes.ArbitraryLength)
        self.assertEqual(p.start_date, '1900-01-01')
        self.assertEqual(p.end_date, '3000-01-01')


    def test_select_by_id(self):
        db_period = Period().standard_init(1024, 1, '1900-01-01', '3000-01-01')
        self._data_repository.periods[1024] = db_period
        test_period = Period.select_by_id(1024)
        self.assertEqual(test_period, db_period)