import logging
import unittest
from geoprocessing.business_logic.business_helpers.competitive_store_helper import CompetitiveStoreHelper
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from geoprocessing.business_logic.business_objects.trade_area import TradeArea
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from geoprocessing.business_logic.config import Config
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.geoprocessors.competition.gp2_replica_postgis import GP2_Replica_PostGIS
from geoprocessing.helpers.postgis_calculator import GISCalculator
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_postgres_repository import MockPostgresDataRepository
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockRestProvider
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository, MockDataRepositorySpecializedForPostGIS
from common.utilities.Logging.log_manager import LogManager
from common.utilities.signal_math import SignalDecimal



#####################################################################################################################
###############################################   GeoProcessor Tests ################################################
#####################################################################################################################


class GP2ReplicaTests(unittest.TestCase):

    def setUp(self):
        # set up mock dependencies
        dependencies.register_dependency("Config", Config().instance)
        self._rest_provider = MockRestProvider()
        self._sql_provider = MockSQLDataRepository()
        self._sql_provider_postgis = MockDataRepositorySpecializedForPostGIS()
        self._postgres_repository = MockPostgresDataRepository()
        dependencies.register_dependency("RestProvider", self._rest_provider)
        dependencies.register_dependency("DataRepository", self._sql_provider)
        dependencies.register_dependency("LogManager", LogManager(logging.ERROR))
        dependencies.register_dependency('PostgresDataRepository', self._postgres_repository)
        dependencies.register_dependency('DataRepositorySpecializedForPostGIS', self._sql_provider_postgis)
        self._geoshape_calculator = GISCalculator()
        # Joseph A Bank
        self._store = Store.simple_init_with_address(43, 14107, -100.00, 45.00)
        self._sql_provider.stores[self._store.store_id] = self._store
        self._store.address_id = 10
        self._sql_provider.addresses[10] = self._store.address
        self._away_stores = {44: StoreCompetitionInstance.basic_init_with_competition(44, 14106, -73.54, 41.10, 1347901),
                             45: StoreCompetitionInstance.basic_init_with_competition(45, 14107, -80.40, 37.21, 1347884)}

    def tearDown(self):
        dependencies.clear()



    #####################################################################################################################
    #############################################   initialization Tests ################################################
    #####################################################################################################################
    def test_initialization_competition(self):
        """
        Verify that the GP2 initialization method sets its variables up correctly
        """
        # initialize mocks

        mock_trade_area = TradeArea()
        mock_trade_area.trade_area_id = self._store.store_id
        mock_trade_area.store_id = self._store.store_id
        mock_trade_area.threshold_id = 1
        mock_trade_area.wkt_representation('LINESTRING(1 0, 0 1, -1 0, 0 -1)')

        away_store_44_point = GeographicalCoordinate(self._away_stores[44].longitude, self._away_stores[44].latitude).wkt_representation()
        away_store_45_point = GeographicalCoordinate(self._away_stores[45].longitude, self._away_stores[45].latitude).wkt_representation()

        self._sql_provider.mock_trade_areas[(self._store.store_id, 1)] = mock_trade_area
        self._sql_provider.away_stores_within_range = self._away_stores
        self._postgres_repository.shape_point_booleans[(mock_trade_area, away_store_44_point)] = True
        self._postgres_repository.shape_point_booleans[(mock_trade_area, away_store_45_point)] = False

        # create geo processor and store
        gp2_processor = GP2_Replica_PostGIS(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self._store
        gp2_processor._initialize()

        # make sure the away stores and initiated correctly
        self.assertEqual(gp2_processor._home_store.store_id, 43)

        self.assertEqual(len(gp2_processor._away_stores), 2)

        # store 1
        self.assertEqual(gp2_processor._away_stores[44].away_store_id, 44)
        self.assertEqual(gp2_processor._away_stores[44].company_id, 14106)
        self.assertEqual(gp2_processor._away_stores[44].longitude, SignalDecimal(41.10))
        self.assertEqual(gp2_processor._away_stores[44].latitude, SignalDecimal(-73.54))
        self.assertEqual(gp2_processor._away_stores[44].competitive_company_id, 1347901)
        # store 2
        self.assertEqual(gp2_processor._away_stores[45].away_store_id, 45)
        self.assertEqual(gp2_processor._away_stores[45].company_id, 14107)
        self.assertEqual(gp2_processor._away_stores[45].longitude, SignalDecimal( 37.21))
        self.assertEqual(gp2_processor._away_stores[45].latitude, SignalDecimal(-80.40))
        self.assertEqual(gp2_processor._away_stores[45].competitive_company_id, 1347884)

        # make sure that the competition instance has the correct type and that the trade area is selected correctly
        self.assertEqual(gp2_processor._entity.trade_area_id, self._store.store_id)
        self.assertEqual(gp2_processor._entity.wkt_representation(), 'LINESTRING(1 0, 0 1, -1 0, 0 -1)')

    #####################################################################################################################
    #############################################   _preprocess_data_for_save Tests ##############################################
    #####################################################################################################################
    def test_preprocess_data_for_save(self):
        # mock up trade area
        mock_trade_area = TradeArea()
        mock_trade_area.trade_area_id = self._store.store_id
        mock_trade_area.store_id = self._store.store_id
        mock_trade_area.threshold_id = 1
        mock_trade_area.wkt_representation('LINESTRING(1 0, 0 1, -1 0, 0 -1)')

        away_store_44_point = GeographicalCoordinate(self._away_stores[44].longitude, self._away_stores[44].latitude).wkt_representation()
        away_store_45_point = GeographicalCoordinate(self._away_stores[45].longitude, self._away_stores[45].latitude).wkt_representation()

        self._sql_provider.mock_trade_areas[(self._store.store_id, 1)] = mock_trade_area
        self._sql_provider.away_stores_within_range = self._away_stores
        self._postgres_repository.shape_point_booleans[(mock_trade_area.wkt_representation(), away_store_44_point)] = True
        self._postgres_repository.shape_point_booleans[(mock_trade_area.wkt_representation(), away_store_45_point)] = False

        #set up fake data and process
        gp2_processor = GP2_Replica_PostGIS(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self._store
        gp2_processor._initialize()

        self.assertEqual(len(gp2_processor._away_stores), 2)

        gp2_processor._preprocess_data_for_save()
        gp2_processor._do_geoprocessing()

        #make sure the drive time for the store is what the mock data is setting it up to be
        self.assertEqual(len(gp2_processor._competitive_stores), 1)

    def test_save_processed_data(self):
        # mock up trade area
        mock_trade_area = TradeArea()
        mock_trade_area.trade_area_id = self._store.store_id
        mock_trade_area.store_id = self._store.store_id
        mock_trade_area.threshold_id = 1
        mock_trade_area.wkt_representation('LINESTRING(1 0, 0 1, -1 0, 0 -1)')

        away_store_44_point = GeographicalCoordinate(self._away_stores[44].longitude, self._away_stores[44].latitude).wkt_representation()
        away_store_45_point = GeographicalCoordinate(self._away_stores[45].longitude, self._away_stores[45].latitude).wkt_representation()

        self._sql_provider.mock_trade_areas[(self._store.store_id, 1)] = mock_trade_area
        self._sql_provider.away_stores_within_range = self._away_stores
        self._postgres_repository.shape_point_booleans[(mock_trade_area.wkt_representation(), away_store_44_point)] = True
        self._postgres_repository.shape_point_booleans[(mock_trade_area.wkt_representation(), away_store_45_point)] = False

        #set up fake data and process
        gp2_processor = GP2_Replica_PostGIS(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self._store
        gp2_processor._initialize()

        self.assertEqual(len(gp2_processor._away_stores), 2)

        gp2_processor._preprocess_data_for_save()
        gp2_processor._do_geoprocessing()
        gp2_processor._save_processed_data()


    #####################################################################################################################
    ###########################################   save_processed_data Tests #############################################
    #####################################################################################################################

    def test_save_processed_synchronizes_competitive_stores(self):
        """
        Test that gp1 calls the correct synchronize competitive_stores db method
        """
        #set up fake data and process it
        gp2_processor = GP2_Replica_PostGIS(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._competition_instance = CompetitiveStoreHelper(self._store, self._away_stores.values(), 100, self._sql_provider_postgis)
        gp2_processor._save_processed_data()

        #assert mock has correct data and tht both templates were saved
        self.assertEqual(self._sql_provider_postgis.home_store_id, self._store.store_id)
        self.assertEqual(self._sql_provider_postgis.batch_upserted_trade_area_id, 100)
        self.assertEqual(len(self._sql_provider_postgis.batch_upserted_competitive_stores), 2)
        self.assertEqual(self._sql_provider_postgis.batch_upserted_competitive_stores[0]["away_store_id"], 44)
        self.assertEqual(self._sql_provider_postgis.batch_upserted_competitive_stores[1]["away_store_id"], 45)

        # make sure the batch monopolies upsert was called
        self.assertEqual(self._sql_provider_postgis.batch_upserted_monopolies_trade_area_id, 100)
        self.assertEqual(self._sql_provider_postgis.batch_upserted_monopolies_list, [])

    def test_save_processed_synchronize_monopolies(self):
        """
        Test that gp1 calls the correct data access (insert_demographics) method with it's built in _demographics
        """
        #s et up fake data and process it
        gp2_processor = GP2_Replica_PostGIS(TradeAreaThreshold.DistanceMiles10)
        gp2_processor._home_store = self._store
        gp2_processor._competition_instance = CompetitiveStoreHelper(self._store, self._away_stores.values(), 100, self._sql_provider_postgis)

        # call save_processed_data()
        gp2_processor._save_processed_data()

        # assert mock has correct data and that both templates were saved
        self.assertEqual(self._sql_provider_postgis.home_store_id, self._store.store_id)

        # verify that the right away companies were upserted
        self.assertEqual(self._sql_provider_postgis.batch_upserted_trade_area_id, 100)
        self.assertEqual(len(self._sql_provider_postgis.batch_upserted_competitive_stores), 2)
        self.assertEqual(self._sql_provider_postgis.batch_upserted_competitive_stores[0]["away_store_id"], 44)
        self.assertEqual(self._sql_provider_postgis.batch_upserted_competitive_stores[1]["away_store_id"], 45)

        # verify that this is not a monopoly
        self.assertEqual(len(self._sql_provider_postgis.upserted_monopolies_postgis), 1)
        self.assertEqual(len(self._sql_provider_postgis.upserted_monopolies_postgis_batch_list), 1)