import unittest
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import  delete_test_sector, select_count_sectors_by_name

__author__ = 'erezrubinstein'

class SectorDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._data_repository = DataRepository()

    @classmethod
    def tearDownClass(cls):
        dependencies.clear()

    def test_save_sector_name_get_id(self):
        sector_id = None
        try:
            sector_name = "UNITTEST_SECTOR"

            # verify sector does not exist
            count = select_count_sectors_by_name(sector_name)
            self.assertEqual(count, 0)

            # create a new test sector
            sector_id = self._data_repository.save_sector_name_get_id(sector_name)

            # verify sector was saved properly
            count = select_count_sectors_by_name(sector_name)
            self.assertEqual(count, 1)

            # get sector again, and verify id is the same and there's only one instance
            same_sector_id = self._data_repository.save_sector_name_get_id(sector_name)
            self.assertEqual(same_sector_id, sector_id)
            count = select_count_sectors_by_name(sector_name)
            self.assertEqual(count, 1)
        except:
            raise
        finally:
            delete_test_sector(sector_id)


if __name__ == '__main__':
    unittest.main()