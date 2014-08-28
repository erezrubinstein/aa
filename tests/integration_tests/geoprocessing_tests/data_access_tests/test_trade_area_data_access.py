import unittest
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.trade_area import TradeAreaOverlap
from geoprocessing.business_logic.config import Config
from geoprocessing.business_logic.enums import TradeAreaThreshold
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.data_access.trade_area_handler import get_trade_area_by_id
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import delete_test_trade_area, select_surface_area_by_trade_area_id, delete_test_surface_area, select_count_trade_area_by_store, insert_test_store, insert_test_company, insert_test_address, insert_test_segment, delete_test_store, delete_test_address, delete_test_competitors, delete_test_company, delete_test_segment, delete_test_trade_area_shape, insert_and_return_test_period_id, delete_test_period_id, select_trade_area_overlap, delete_test_trade_area_overlap

__author__ = 'spacecowboy et al.'

class TradeAreaAccessTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):

        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)

        # insert test data
        cls._company_id = insert_test_company()
        cls._address_id = insert_test_address(-1, 1)
        cls._store_id = insert_test_store(cls._company_id, cls._address_id)
        cls._store = Store().select_by_id(cls._store_id)

        #create dummy segment
        cls._segment_id = insert_test_segment()
        cls._test_period_id = insert_and_return_test_period_id()

    @classmethod
    def tearDownClass(cls):

        if cls._store_id is not None:
            delete_test_store(cls._store_id)
        if cls._address_id is not None:
            delete_test_address(cls._address_id)
        if cls._company_id is not None:
            delete_test_competitors(cls._company_id)
        if cls._company_id is not None:
            delete_test_company(cls._company_id)
        if cls._segment_id is not None:
            delete_test_segment(cls._segment_id)
        if cls._test_period_id is not None:
            delete_test_period_id(cls._test_period_id)
            
        dependencies.clear()

    def test_save_trade_area_surface_area(self):
        trade_area = None
        try:
            trade_area = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, 1)
            trade_area.period_id = self._test_period_id
            trade_area.area = 13371337
            self.assertEqual(select_count_trade_area_by_store(self._store_id), 1)
            self._SQL_data_repository.save_trade_area_surface_area(trade_area)
            self.assertEqual(select_surface_area_by_trade_area_id(trade_area.trade_area_id), 13371337)

        except:
            raise
        finally:
            if trade_area is not None:
                delete_test_surface_area(trade_area.trade_area_id, trade_area.area)
                delete_test_trade_area(trade_area.store_id)

    def test_insert_trade_area(self):
        """
        Test to make sure we can successfully insert a trade area
        This also tests that a second insert of a store that already exists, will not re-insert it
        """
        trade_area = None
        try:
            # get count of trade areas to make sure it doesn't exist
            count_trade_area = select_count_trade_area_by_store((self._store_id))
            self.assertEqual(count_trade_area, 0)

            #insert trade area and verify it was inserted
            trade_area = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)
            count_trade_area = select_count_trade_area_by_store(self._store_id)
            self.assertEqual(count_trade_area, 1)

            #try to insert again and verify that it wasn't inserted again and that ids match
            trade_area2 = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)
            count_trade_area = select_count_trade_area_by_store(self._store_id)
            self.assertEqual(count_trade_area, 1)
            self.assertEqual(trade_area.trade_area_id, trade_area2.trade_area_id)

        except:
            raise
        finally:
            if trade_area is not None and trade_area.trade_area_id > 0:
                delete_test_trade_area(self._store_id)

    def select_trade_areas_by_store_id_require_shape(self):

        trade_area = None
        trade_area_2 = None
        try:

            # insert dummy trade area
            trade_area = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)
            trade_area_2 = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DriveTimeMinutes10)

            trade_area.period_id = self._test_period_id
            trade_area.wkt_representation(wkt_representation = 'LINESTRING(0 -1, 1 0, 0 1, -1 0)')
            self._SQL_data_repository.insert_trade_area_shape(trade_area.trade_area_id, trade_area.wkt_representation(), trade_area.period_id)

            trade_area_2.period_id = self._test_period_id
            trade_area_2.wkt_representation(wkt_representation = 'LINESTRING(-1 0, 0 1, 1 0, 0 -1)')
            self._SQL_data_repository.insert_trade_area_shape(trade_area_2.trade_area_id, trade_area_2.wkt_representation(), trade_area_2.period_id)

            # test the selects
            found_test_trade_areas = self._SQL_data_repository.select_trade_areas_by_store_id_require_shape(self._store_id)

            self.assertEqual(len(found_test_trade_areas), 2)

            self.assertEqual(TradeAreaThreshold.DistanceMiles10, found_test_trade_areas[0].threshold_id)
            self.assertEqual(TradeAreaThreshold.DriveTimeMinutes10, found_test_trade_areas[1].threshold_id)

            self.assertEqual(trade_area.wkt_representation(), found_test_trade_areas[0].wkt_representation())
            self.assertEqual(trade_area_2.wkt_representation(), found_test_trade_areas[1].wkt_representation())

            self.assertEqual(trade_area.period_id, found_test_trade_areas[0].period_id)
            self.assertEqual(trade_area_2.period_id, found_test_trade_areas[1].period_id)

        except:
            raise
        finally:
            if trade_area:
                delete_test_trade_area_shape(trade_area.trade_area_id)

            if trade_area_2:
                delete_test_trade_area_shape(trade_area_2.trade_area_id)

            delete_test_trade_area(self._store_id)

    def test_select_away_trade_areas_within_lat_long_range(self):



        pass

    def test_save_trade_area_overlap(self):

        trade_area = None
        trade_area_2 = None
        try:

            # insert dummy trade area
            trade_area = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)
            trade_area_2 = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DriveTimeMinutes10)

            trade_area.period_id = self._test_period_id
            trade_area.wkt_representation_linestring = 'LINESTRING(0 -1, 1 0, 0 1, -1 0)'
            self._SQL_data_repository.insert_trade_area_shape(trade_area.trade_area_id, trade_area.wkt_representation_linestring, trade_area.period_id)

            trade_area_2.period_id = self._test_period_id
            trade_area_2.wkt_representation_linestring = 'LINESTRING(-1 0, 0 1, 1 0, 0 -1)'
            self._SQL_data_repository.insert_trade_area_shape(trade_area_2.trade_area_id, trade_area_2.wkt_representation_linestring, trade_area_2.period_id)



            trade_area_overlap = TradeAreaOverlap()
            trade_area_overlap.home_trade_area_id = trade_area.trade_area_id
            trade_area_overlap.away_trade_area_id = trade_area.trade_area_id
            trade_area_overlap.overlap_area = 1.0

            self._SQL_data_repository.save_trade_area_overlap(trade_area_overlap)

            self.assertEqual(trade_area_overlap.overlap_area, select_trade_area_overlap(trade_area_overlap.home_trade_area_id, trade_area_overlap.away_trade_area_id))

        except:
            raise
        finally:
            if trade_area:
                delete_test_trade_area_overlap(trade_area.trade_area_id)
                delete_test_trade_area_shape(trade_area.trade_area_id)

            if trade_area_2:
                delete_test_trade_area_shape(trade_area_2.trade_area_id)

            delete_test_trade_area(self._store_id)



    def test_get_trade_area_by_id(self):
        trade_area = None
        try:
            #insert trade area and verify it was inserted
            trade_area = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)
            trade_area_from_db = get_trade_area_by_id(trade_area.trade_area_id)

            self.assertEqual(trade_area.trade_area_id, trade_area_from_db.trade_area_id)
            self.assertEqual(trade_area.store_id, trade_area_from_db.store_id)
            self.assertEqual(trade_area.threshold_id, trade_area_from_db.threshold_id)
        except:
            raise
        finally:
            if trade_area:
                delete_test_trade_area(self._store_id)

if __name__ == '__main__':
    unittest.main()