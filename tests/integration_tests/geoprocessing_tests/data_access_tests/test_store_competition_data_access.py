from datetime import datetime
from decimal import Decimal
from geoprocessing.business_logic.enums import CompetitionType
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.business_logic.business_helpers.competitive_store_helper import CompetitiveStoreHelper
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository, DataRepositorySpecializedForPostGIS
from geoprocessing.data_access.monopoly_handler import insert_monopoly, insert_monopoly_postgis
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import insert_test_store, delete_test_store, delete_test_address, delete_test_competitors, insert_test_address, insert_test_company, insert_test_competitor, delete_test_company, select_competitive_stores, select_monopolies, delete_competitive_stores, delete_test_trade_area, delete_monopolies, delete_test_trade_area_shape, select_competitive_stores_postgis, delete_competitive_stores_postgis, delete_monopolies_postgis, select_monopolies_postgis

__author__ = 'erezrubinstein'

import unittest

class StoreCompetitionAccessTests(unittest.TestCase):
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

        # away stores
        cls._away_store_1_company_id = insert_test_company()
        cls._away_store_2_company_id = insert_test_company()
        cls._competitive_company_id1 = insert_test_competitor(cls._company_id, cls._away_store_1_company_id)
        cls._competitive_company_id2 = insert_test_competitor(cls._company_id, cls._away_store_2_company_id)
        cls._away_store_1_address_id = insert_test_address(-1, 1)
        cls._away_store_2_address_id = insert_test_address(-1, 1)
        cls._away_store_1_id = insert_test_store(cls._away_store_1_company_id, cls._away_store_1_address_id)
        cls._away_store_2_id = insert_test_store(cls._away_store_2_company_id, cls._away_store_2_address_id)

        cls._away_stores = {
            cls._away_store_1_id : StoreCompetitionInstance.basic_init_with_drive_time(cls._away_store_1_id, cls._away_store_1_company_id, -1, 1, cls._competitive_company_id1, 1.1),
            cls._away_store_2_id : StoreCompetitionInstance.basic_init_with_drive_time(cls._away_store_2_id, cls._away_store_2_company_id, -2, 2, cls._competitive_company_id2, 2.2)
        }

        # create trade area
        cls._trade_area = cls._SQL_data_repository.select_trade_area_force_insert(cls._store.store_id, TradeAreaThreshold.DistanceMiles10)
        cls._SQL_data_repository.insert_trade_area_shape(cls._trade_area.trade_area_id, 'LINESTRING(0 0, 0 0, 0 0, 0 0)', 3)
        cls._start_date = datetime(2012, 01, 01)
        cls._end_date = datetime(2012, 12, 01)

    @classmethod
    def tearDownClass(cls):
        # delete test data
        if cls._store_id is not None:
            delete_monopolies(cls._store_id, cls._trade_area.trade_area_id)
            delete_test_trade_area_shape(cls._trade_area.trade_area_id)
            delete_test_trade_area(cls._store_id)
            delete_test_store(cls._store_id)
        if cls._address_id is not None:
            delete_test_address(cls._address_id)
        if cls._away_store_1_id is not None:
            delete_test_store(cls._away_store_1_id)
        if cls._away_store_2_id is not None:
            delete_test_store(cls._away_store_2_id)
        if cls._away_store_1_address_id is not None:
            delete_test_address(cls._away_store_1_address_id)
        if cls._away_store_2_address_id is not None:
            delete_test_address(cls._away_store_2_address_id)
        if cls._company_id is not None:
            delete_test_competitors(cls._company_id)
        if cls._away_store_1_company_id is not None:
            delete_test_company(cls._away_store_1_company_id)
        if cls._away_store_2_company_id is not None:
            delete_test_company(cls._away_store_2_company_id)
        if cls._company_id is not None:
            delete_test_company(cls._company_id)

        dependencies.clear()

    def test_get_competitive_stores(self):
        try:
            # synchronize competitors in order to insert them into the db
            competition_instance = CompetitiveStoreHelper(self._store, self._away_stores.values(), self._trade_area.trade_area_id, self._SQL_data_repository)
            competition_instance.synchronize_competitive_stores_in_db()

            # select active competitive stores and make sure they matched data inserted in class set up
            competitive_stores = self._SQL_data_repository.get_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)
            competitive_stores = sorted(competitive_stores, key = lambda store : store.away_store_id )
            self.assertEqual(len(competitive_stores), 2)
            self.assertEqual(self._away_store_1_id, competitive_stores[0].away_store_id)
            self.assertEqual(self._away_store_2_id, competitive_stores[1].away_store_id)
            self.assertEqual(self._away_store_1_company_id, competitive_stores[0].company_id)
            self.assertEqual(self._away_store_2_company_id, competitive_stores[1].company_id)

            # close one store by syncing one more time with a smaller away store array
            self._SQL_data_repository.close_competitive_stores_by_id(self._store_id, self._away_store_1_id, self._trade_area.trade_area_id, "20120101")

            # select active competitive stores again and verify that we still select it
            competitive_stores = self._SQL_data_repository.get_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)
            self.assertEqual(len(competitive_stores), 2)
        except:
            raise
        finally:
            # delete all the competitive instances we created
            self._SQL_data_repository.delete_from_competitive_stores(self._store.store_id, self._away_store_1_id)
            self._SQL_data_repository.delete_from_competitive_stores(self._store.store_id, self._away_store_2_id)



    def test_delete_from_competitive_stores(self):
        try:
            # synchronize competitors in order to insert them into the db
            competition_instance = CompetitiveStoreHelper(self._store, self._away_stores.values(), self._trade_area.trade_area_id, self._SQL_data_repository)
            competition_instance.synchronize_competitive_stores_in_db()

            # select active competitive stores and make sure they matched data inserted in class set up
            away_store_ids = self._SQL_data_repository.get_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)
            # sort for easy asserts
            away_store_ids = sorted(away_store_ids, key = lambda store : store.away_store_id )
            self.assertEqual(len(away_store_ids), 2)
            self.assertEqual(self._away_store_1_id, away_store_ids[0].away_store_id)
            self.assertEqual(self._away_store_2_id, away_store_ids[1].away_store_id)

            # delete competitive store
            self._SQL_data_repository.delete_from_competitive_stores(self._store.store_id, away_store_ids[0].away_store_id)
            self._SQL_data_repository.delete_from_competitive_stores(self._store.store_id, away_store_ids[1].away_store_id)

            # select active competitive store again and verify they've been deleted
            away_store_ids = self._SQL_data_repository.get_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)
            self.assertEqual(away_store_ids, [])
        except:
            raise
        finally:
            # delete all the competitive instances we created
            self._SQL_data_repository.delete_from_competitive_stores(self._store.store_id, self._away_store_1_id)
            self._SQL_data_repository.delete_from_competitive_stores(self._store.store_id, self._away_store_2_id)


    def test_batch_upsert_competitive_stores(self):
        """
        This test verifies the insert/update stores call
        """
        # make sure that there are no competitive stores to begin with
        try:
            competitive_stores = select_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)
            self.assertEqual(len(competitive_stores), 0)

            # insert and select
            away_store = CompetitiveStoreHelper._create_batch_competition_structure(self._away_stores[self._away_store_1_id], None, None, True, self._store.store_id)
            self._SQL_data_repository.batch_upsert_competitive_stores(self._trade_area.trade_area_id, [away_store])
            competitive_stores = select_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)

            # verify that that all the values were inserted correctly
            self.assertEqual(len(competitive_stores), 1)
            self.assertEqual(competitive_stores[0][2], self._store_id)
            self.assertEqual(competitive_stores[0][3], self._away_store_1_id)
            self.assertEqual(competitive_stores[0][4], self._trade_area.trade_area_id)
            self.assertEqual(competitive_stores[0][5], Decimal("1.10000"))
            self.assertEqual(competitive_stores[0].start_date, None)
            self.assertEqual(competitive_stores[0].end_date, None)


            # insert and select
            store_updated = StoreCompetitionInstance.basic_init_with_drive_time(self._away_store_1_id, self._away_store_1_company_id, -1, 1,
                                                                                self._away_stores[self._away_store_1_id].competitive_company_id, 7.7)
            away_store = CompetitiveStoreHelper._create_batch_competition_structure(store_updated, self._start_date, self._end_date, True, self._store.store_id)
            self._SQL_data_repository.batch_upsert_competitive_stores(self._trade_area.trade_area_id, [away_store])
            competitive_stores = select_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)

            # verify drive time was updated correctly
            self.assertEqual(len(competitive_stores), 1)
            self.assertEqual(competitive_stores[0][2], self._store_id)
            self.assertEqual(competitive_stores[0][3], self._away_store_1_id)
            self.assertEqual(competitive_stores[0][4], self._trade_area.trade_area_id)
            self.assertEqual(competitive_stores[0][5], Decimal("7.70000"))
            self.assertEqual(competitive_stores[0].start_date, "2012-01-01")
            self.assertEqual(competitive_stores[0].end_date, "2012-12-01")
        except:
            raise
        finally:
            delete_competitive_stores(self._store_id, self._trade_area.trade_area_id)


    def test_close_competitive_stores_by_id(self):
        """
        This test verifies that the close competitive stores method works properly
        """
        try:
            # insert a competitive store and select it
            away_store = CompetitiveStoreHelper._create_batch_competition_structure(self._away_stores[self._away_store_1_id], self._start_date, None, True, self._store.store_id)
            self._SQL_data_repository.batch_upsert_competitive_stores(self._trade_area.trade_area_id, [away_store])
            competitive_stores = select_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)

            # verify that the competitive store is active (i.e. no end date)
            self.assertEqual(len(competitive_stores), 1)
            self.assertEqual(competitive_stores[0].start_date, "2012-01-01")
            self.assertEqual(competitive_stores[0].end_date, None)

            # close the competitive store and select all competitive stores again
            self._SQL_data_repository.close_competitive_stores_by_id(self._store_id, self._away_store_1_id, self._trade_area.trade_area_id, self._end_date)
            competitive_stores = select_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)

            # verify that the competitive store is closed (i.e. has the end date)
            self.assertEqual(len(competitive_stores), 1)
            self.assertEqual(competitive_stores[0].start_date, "2012-01-01")
            self.assertEqual(competitive_stores[0].end_date, "2012-12-01")

        except:
            raise
        finally:
            delete_competitive_stores(self._store_id, self._trade_area.trade_area_id)


    def test_select_by_id(self):
        try:
            competitive_stores = select_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)
            self.assertEqual(len(competitive_stores), 0)

            # insert and select
            away_store = CompetitiveStoreHelper._create_batch_competition_structure(self._away_stores[self._away_store_1_id], self._start_date, self._end_date, True, self._store.store_id)
            self._SQL_data_repository.batch_upsert_competitive_stores(self._trade_area.trade_area_id, [away_store])
            competitive_store_id = select_competitive_stores(self._store.store_id, self._trade_area.trade_area_id)[0].competitive_store_id
            competitive_store = StoreCompetitionInstance.select_by_id(competitive_store_id)

            # run asserts
            self.assertEqual(competitive_store.home_store_id, self._store_id)
            self.assertEqual(competitive_store.away_store_id, self._away_store_1_id)
            self.assertEqual(competitive_store.trade_area_id, self._trade_area.trade_area_id)
            self.assertEqual(competitive_store.travel_time, Decimal("1.10000"))
        except:
            raise
        finally:
            delete_competitive_stores(self._store_id, self._trade_area.trade_area_id)


    ################################################################################################################
    ############################################### Monopoly Tests #################################################
    ################################################################################################################

    def test_select_active_monopoly_record(self):
        """
        This tests selecting an active monopoly record
        """
        try:
            # insert two monopolies, one closed and one active
            insert_monopoly(self._store_id, CompetitionType.AbsoluteMonopoly, self._trade_area.trade_area_id, self._start_date, self._end_date)
            insert_monopoly(self._store_id, CompetitionType.AbsoluteMonopoly, self._trade_area.trade_area_id, self._start_date)

            # select active monopolies and make sure it has no end date.  you should get exception if more than one record is returned
            monopoly = self._SQL_data_repository.select_active_monopoly_record(self._store_id, self._trade_area.trade_area_id, [])
            self.assertIsNotNone(monopoly)
            self.assertIsNone(monopoly.end_date)
        except:
            raise
        finally:
            delete_monopolies(self._store_id, self._trade_area.trade_area_id)

    def test_select_active_monopoly_record_raises_exception_for_multiple(self):
        """
        This tests verifies that the select_active_monopoly_record raises an exception if there are multiple monopoly records
        """
        try:
            # insert two monopolies, both active
            insert_monopoly(self._store_id, CompetitionType.AbsoluteMonopoly, self._trade_area.trade_area_id, self._start_date)
            insert_monopoly(self._store_id, CompetitionType.AbsoluteMonopoly, self._trade_area.trade_area_id, self._start_date)

            # select active monopolies and make sure it has no end date.  you should get exception if more than one record is returned
            exception_happened = False
            try:
                monopoly = self._SQL_data_repository.select_active_monopoly_record(self._store_id, self._trade_area.trade_area_id, [])
            except:
                exception_happened = True

            # make sure exception happened
            self.assertTrue(exception_happened)
        except:
            raise
        finally:
            delete_monopolies(self._store_id, self._trade_area.trade_area_id)

    def test_close_monopoly_record(self):
        """
        This test tests closing a monopoly record for a store
        """
        try:
            # insert a fake monopoly
            insert_monopoly(self._store_id, CompetitionType.AbsoluteMonopoly, self._trade_area.trade_area_id, self._start_date)

            # select active monopoly record to verify that it's active
            monopoly = self._SQL_data_repository.select_active_monopoly_record(self._store_id, self._trade_area.trade_area_id, [])
            self.assertIsNotNone(monopoly)

            # close the monopoly
            self._SQL_data_repository.close_monopoly_record(self._store_id, self._trade_area.trade_area_id, self._end_date, [])

            # select active monopoly record to verify that it's no longer active
            monopoly = self._SQL_data_repository.select_active_monopoly_record(self._store_id, self._trade_area.trade_area_id, [])
            self.assertIsNone(monopoly)
        except:
            raise
        finally:
            delete_monopolies(self._store_id, self._trade_area.trade_area_id)

    def test_insert_monopoly(self):
        """
        This tests the monopolies insert statement
        """
        try:
            #create monopoly
            self._SQL_data_repository.insert_monopoly(self._store_id, CompetitionType.AbsoluteMonopoly, self._trade_area.trade_area_id, self._start_date, [])

            #select and assert values
            monopoly_first = select_monopolies(self._store_id, self._trade_area.trade_area_id)
            self.assertEqual(len(monopoly_first), 1)
            self.assertEqual(monopoly_first[0][0], self._store_id)
            self.assertEqual(monopoly_first[0][1], self._trade_area.trade_area_id)
            self.assertIsInstance(monopoly_first[0][2], datetime)
            self.assertIsInstance(monopoly_first[0][3], datetime)
        except:
            raise
        finally:
            delete_monopolies(self._store_id, self._trade_area.trade_area_id)

    def test_delete_monopoly(self):
        """
        Test the monopoly delete method
        """
        # insert data
        self._SQL_data_repository.insert_monopoly(self._store_id, CompetitionType.AbsoluteMonopoly, self._trade_area.trade_area_id, self._start_date, [])

        # select data and assert it's in the db
        monopolies = select_monopolies(self._store.store_id, self._trade_area.trade_area_id)
        self.assertEqual(monopolies[0][0], self._store.store_id)

        # delete data and make sure it's gone
        self._SQL_data_repository.delete_from_monopolies(self._store_id, self._trade_area.trade_area_id)
        monopolies = select_monopolies(self._store.store_id, self._trade_area.trade_area_id)
        self.assertEqual(monopolies, [])



if __name__ == '__main__':
    unittest.main()