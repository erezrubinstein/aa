from collections import namedtuple
import unittest
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from geoprocessing.business_logic.business_objects.trade_area import TradeArea, TradeAreaOverlap
from geoprocessing.geoprocessors.competition.gp3_geoshape_processor import GP3GeoShapeProcessor
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from geoprocessing.helpers.postgis_calculator import GISCalculator


__author__ = 'spacecowboy'

class GP3GeoShapeProcessorTests(unittest.TestCase):

    def setUp(self):
        # set up mock dependencies
        register_mock_dependencies()


        self._postgres_provider = Dependency('PostgresDataRepository').value
        self._sql_provider = Dependency("DataRepository").value


        # Joseph A Bank
        self._store = Store.simple_init_with_address(42, 14107, -100.00, 45.00)
        self._sql_provider.stores[self._store.store_id] = self._store
        self._store.address_id = 10
        self._sql_provider.addresses[10] = self._store.address
        self._away_stores = {44: StoreCompetitionInstance.basic_init_with_competition(44, 14106, -73.54, 41.10, 1347901),
                             46: StoreCompetitionInstance.basic_init_with_competition(46, 14107, -80.40, 37.21, 1347884)}

    def tearDown(self):
        dependencies.clear()

########################################################################################################################
######################################################   tests   #######################################################
########################################################################################################################

    def test_init(self):
        shape_processor = GP3GeoShapeProcessor(self._store.store_id)
        self.assertEqual(shape_processor._home_store, self._store)

    def test_get_home_and_away_trade_areas(self):

        geoshape_calculator = GISCalculator()

        # mock trade areas
        trade_area_1 = TradeArea()
        trade_area_1.trade_area_id = 42
        trade_area_1.store_id = 42
        trade_area_1.threshold_id = 1
        trade_area_1.period_id = 3
        trade_area_1.wkt_representation(wkt_representation = 'LINESTRING(1 0, 0 1, -1 0, 0 -1)')

        trade_area_2 = TradeArea()
        trade_area_2.trade_area_id = 43
        trade_area_2.store_id = 42
        trade_area_2.threshold_id = 2
        trade_area_2.period_id = 3
        trade_area_2.wkt_representation(wkt_representation = 'LINESTRING(2 0, 0 2, -2 0, 0 -2)')

        # mock trade areas
        trade_area_3 = TradeArea()
        trade_area_3.trade_area_id = 44
        trade_area_3.store_id = 44
        trade_area_3.threshold_id = 1
        trade_area_3.period_id = 3
        trade_area_3.wkt_representation(wkt_representation = 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)')

        trade_area_4 = TradeArea()
        trade_area_4.trade_area_id = 45
        trade_area_4.store_id = 44
        trade_area_4.threshold_id = 2
        trade_area_4.period_id = 3
        trade_area_4.wkt_representation(wkt_representation = 'LINESTRING(3 1, 1 3, -3 1, 1 -3)')

        # mock trade areas
        trade_area_5 = TradeArea()
        trade_area_5.trade_area_id = 46
        trade_area_5.store_id = 46
        trade_area_5.threshold_id = 1
        trade_area_5.period_id = 3
        trade_area_5.wkt_representation(wkt_representation = 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)')

        trade_area_6 = TradeArea()
        trade_area_6.trade_area_id = 47
        trade_area_6.store_id = 46
        trade_area_6.threshold_id = 2
        trade_area_6.period_id = 3
        trade_area_6.wkt_representation(wkt_representation = 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)')

        self._sql_provider.competitive_trade_areas = [trade_area_3, trade_area_4, trade_area_5, trade_area_6]
        self._sql_provider.trade_areas = [trade_area_1, trade_area_2, trade_area_3, trade_area_4, trade_area_5, trade_area_6]


        self._sql_provider.trade_area_shapes = {trade_area_1.trade_area_id: 'LINESTRING(1 0, 0 1, -1 0, 0 -1)',
                                                trade_area_2.trade_area_id: 'LINESTRING(2 0, 0 2, -2 0, 0 -2)',
                                                trade_area_3.trade_area_id: 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)',
                                                trade_area_4.trade_area_id: 'LINESTRING(3 1, 1 3, -3 1, 1 -3)',
                                                trade_area_5.trade_area_id: 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)',
                                                trade_area_6.trade_area_id: 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)'}



        Overlap = namedtuple('Overlap', ['shape_1', 'shape_2'])

        self._postgres_provider.overlap_areas = {Overlap(shape_1 = trade_area_1.wkt_representation(), shape_2 = trade_area_3.wkt_representation()): 1.0,
                                                 Overlap(shape_1 = trade_area_1.wkt_representation(), shape_2 = trade_area_5.wkt_representation()): 2.0,
                                                 Overlap(shape_1 = trade_area_2.wkt_representation(), shape_2 = trade_area_4.wkt_representation()): 3.0,
                                                 Overlap(shape_1 = trade_area_2.wkt_representation(), shape_2 = trade_area_6.wkt_representation()): 4.0}

        self._postgres_provider.shape_centroids = {trade_area_1.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_2.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_3.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_4.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_5.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_6.wkt_representation(): 'POINT(0 0)'}

        self._postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_1.wkt_representation())): 1,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_2.wkt_representation())): 2,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_3.wkt_representation())): 3,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_4.wkt_representation())): 4,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_5.wkt_representation())): 5,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_6.wkt_representation())): 6}

        shape_processor = GP3GeoShapeProcessor(self._store.store_id)
        shape_processor._initialize()
        shape_processor._do_geoprocessing()
        shape_processor._preprocess_data_for_save()
        self.assertEqual(shape_processor._home_trade_areas[0].trade_area_id, self._store.store_id)
        self.assertEqual(shape_processor._home_trade_areas[1].trade_area_id, self._store.store_id + 1)

        self.assertEqual(shape_processor._home_trade_areas[0].store_id, self._store.store_id)
        self.assertEqual(shape_processor._home_trade_areas[1].store_id, self._store.store_id)

        self.assertEqual(shape_processor._home_trade_areas[0].threshold_id, 1)
        self.assertEqual(shape_processor._home_trade_areas[1].threshold_id, 2)

        self.assertEqual(shape_processor._home_trade_areas[0].period_id, 3)
        self.assertEqual(shape_processor._home_trade_areas[1].period_id, 3)

        self.assertEqual(shape_processor._home_trade_areas[0].wkt_representation(), 'LINESTRING(1 0, 0 1, -1 0, 0 -1)')
        self.assertEqual(shape_processor._home_trade_areas[1].wkt_representation(), 'LINESTRING(2 0, 0 2, -2 0, 0 -2)')

        self.assertEqual(shape_processor._away_trade_areas, [trade_area_3, trade_area_4, trade_area_5, trade_area_6])

        self.assertEqual(shape_processor._away_trade_areas[0].wkt_representation(), 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)')
        self.assertEqual(shape_processor._away_trade_areas[1].wkt_representation(), 'LINESTRING(3 1, 1 3, -3 1, 1 -3)')
        self.assertEqual(shape_processor._away_trade_areas[2].wkt_representation(), 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)')
        self.assertEqual(shape_processor._away_trade_areas[3].wkt_representation(), 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)')

        self.assertEqual(shape_processor._away_trade_areas[0].period_id, 3)
        self.assertEqual(shape_processor._away_trade_areas[1].period_id, 3)
        self.assertEqual(shape_processor._away_trade_areas[2].period_id, 3)
        self.assertEqual(shape_processor._away_trade_areas[3].period_id, 3)

    def test_calculate_overlap_for_each_trade_area(self):

        geoshape_calculator = GISCalculator()

        # mock trade areas
        trade_area_1 = TradeArea()
        trade_area_1.trade_area_id = 42
        trade_area_1.store_id = 42
        trade_area_1.threshold_id = 1
        trade_area_1.period_id = 3
        trade_area_1.wkt_representation(wkt_representation = 'LINESTRING(1 0, 0 1, -1 0, 0 -1)')

        trade_area_2 = TradeArea()
        trade_area_2.trade_area_id = 43
        trade_area_2.store_id = 42
        trade_area_2.threshold_id = 2
        trade_area_2.period_id = 3
        trade_area_2.wkt_representation(wkt_representation = 'LINESTRING(2 0, 0 2, -2 0, 0 -2)')

        # mock trade areas
        trade_area_3 = TradeArea()
        trade_area_3.trade_area_id = 44
        trade_area_3.store_id = 44
        trade_area_3.threshold_id = 1
        trade_area_3.period_id = 3
        trade_area_3.wkt_representation(wkt_representation = 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)')

        trade_area_4 = TradeArea()
        trade_area_4.trade_area_id = 45
        trade_area_4.store_id = 44
        trade_area_4.threshold_id = 2
        trade_area_4.period_id = 3
        trade_area_4.wkt_representation(wkt_representation = 'LINESTRING(3 1, 1 3, -3 1, 1 -3)')

        # mock trade areas
        trade_area_5 = TradeArea()
        trade_area_5.trade_area_id = 46
        trade_area_5.store_id = 46
        trade_area_5.threshold_id = 1
        trade_area_5.period_id = 3
        trade_area_5.wkt_representation(wkt_representation = 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)')

        trade_area_6 = TradeArea()
        trade_area_6.trade_area_id = 47
        trade_area_6.store_id = 46
        trade_area_6.threshold_id = 2
        trade_area_6.period_id = 3
        trade_area_6.wkt_representation(wkt_representation = 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)')

        self._sql_provider.competitive_trade_areas = [trade_area_3, trade_area_4, trade_area_5, trade_area_6]
        self._sql_provider.trade_areas = [trade_area_1, trade_area_2, trade_area_3, trade_area_4, trade_area_5, trade_area_6]


        self._sql_provider.trade_area_shapes = {trade_area_1.trade_area_id: 'LINESTRING(1 0, 0 1, -1 0, 0 -1)',
                                                trade_area_2.trade_area_id: 'LINESTRING(2 0, 0 2, -2 0, 0 -2)',
                                                trade_area_3.trade_area_id: 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)',
                                                trade_area_4.trade_area_id: 'LINESTRING(3 1, 1 3, -3 1, 1 -3)',
                                                trade_area_5.trade_area_id: 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)',
                                                trade_area_6.trade_area_id: 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)'}


        Overlap = namedtuple('Overlap', ['shape_1', 'shape_2'])

        self._postgres_provider.overlap_areas = {Overlap(shape_1 = trade_area_1.wkt_representation(), shape_2 = trade_area_3.wkt_representation()): 1.0,
                                                 Overlap(shape_1 = trade_area_1.wkt_representation(), shape_2 = trade_area_5.wkt_representation()): 2.0,
                                                 Overlap(shape_1 = trade_area_2.wkt_representation(), shape_2 = trade_area_4.wkt_representation()): 3.0,
                                                 Overlap(shape_1 = trade_area_2.wkt_representation(), shape_2 = trade_area_6.wkt_representation()): 4.0}

        self._postgres_provider.shape_centroids = {trade_area_1.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_2.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_3.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_4.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_5.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_6.wkt_representation(): 'POINT(0 0)'}

        self._postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_1.wkt_representation())): 1,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_2.wkt_representation())): 2,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_3.wkt_representation())): 3,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_4.wkt_representation())): 4,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_5.wkt_representation())): 5,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_6.wkt_representation())): 6}


        shape_processor = GP3GeoShapeProcessor(self._store.store_id)
        shape_processor._initialize()
        shape_processor._do_geoprocessing()
        shape_processor._preprocess_data_for_save()

        overlap_1 = TradeAreaOverlap()
        overlap_1.home_trade_area_id = trade_area_1.trade_area_id
        overlap_1.away_trade_area_id = trade_area_3.trade_area_id
        overlap_1.overlap_area = 1.0

        overlap_2 = TradeAreaOverlap()
        overlap_2.home_trade_area_id = trade_area_1.trade_area_id
        overlap_2.away_trade_area_id = trade_area_5.trade_area_id
        overlap_2.overlap_area = 2.0

        overlap_3 = TradeAreaOverlap()
        overlap_3.home_trade_area_id = trade_area_2.trade_area_id
        overlap_3.away_trade_area_id = trade_area_4.trade_area_id
        overlap_3.overlap_area = 3.0

        overlap_4 = TradeAreaOverlap()
        overlap_4.home_trade_area_id = trade_area_2.trade_area_id
        overlap_4.away_trade_area_id = trade_area_6.trade_area_id
        overlap_4.overlap_area = 4.0

        self.assertEqual(len(shape_processor._trade_area_overlap_objects), 4)
        self.assertEqual(shape_processor._trade_area_overlap_objects[0].home_trade_area_id, overlap_1.home_trade_area_id)
        self.assertEqual(shape_processor._trade_area_overlap_objects[0].away_trade_area_id, overlap_1.away_trade_area_id)
        self.assertEqual(shape_processor._trade_area_overlap_objects[0].overlap_area, overlap_1.overlap_area)

        self.assertEqual(shape_processor._trade_area_overlap_objects[1].home_trade_area_id, overlap_2.home_trade_area_id)
        self.assertEqual(shape_processor._trade_area_overlap_objects[1].away_trade_area_id, overlap_2.away_trade_area_id)
        self.assertEqual(shape_processor._trade_area_overlap_objects[1].overlap_area, overlap_2.overlap_area)

        self.assertEqual(shape_processor._trade_area_overlap_objects[2].home_trade_area_id, overlap_3.home_trade_area_id)
        self.assertEqual(shape_processor._trade_area_overlap_objects[2].away_trade_area_id, overlap_3.away_trade_area_id)
        self.assertEqual(shape_processor._trade_area_overlap_objects[2].overlap_area, overlap_3.overlap_area)

        self.assertEqual(shape_processor._trade_area_overlap_objects[3].home_trade_area_id, overlap_4.home_trade_area_id)
        self.assertEqual(shape_processor._trade_area_overlap_objects[3].away_trade_area_id, overlap_4.away_trade_area_id)
        self.assertEqual(shape_processor._trade_area_overlap_objects[3].overlap_area, overlap_4.overlap_area)



    def test_save_geoshape_analytics(self):

        geoshape_calculator = GISCalculator()

        # mock trade areas
        trade_area_1 = TradeArea()
        trade_area_1.trade_area_id = self._store.store_id
        trade_area_1.store_id = self._store.store_id
        trade_area_1.threshold_id = 1
        trade_area_1.period_id = 3
        trade_area_1.wkt_representation(wkt_representation = 'LINESTRING(1 0, 0 1, -1 0, 0 -1)')

        trade_area_2 = TradeArea()
        trade_area_2.trade_area_id = self._store.store_id + 1
        trade_area_2.store_id = self._store.store_id
        trade_area_2.threshold_id = 2
        trade_area_2.period_id = 3
        trade_area_2.wkt_representation(wkt_representation = 'LINESTRING(2 0, 0 2, -2 0, 0 -2)')

        # mock trade areas
        trade_area_3 = TradeArea()
        trade_area_3.trade_area_id = 44
        trade_area_3.store_id = 44
        trade_area_3.threshold_id = 1
        trade_area_3.period_id = 3
        trade_area_3.wkt_representation(wkt_representation = 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)')

        trade_area_4 = TradeArea()
        trade_area_4.trade_area_id = 45
        trade_area_4.store_id = 44
        trade_area_4.threshold_id = 2
        trade_area_4.period_id = 3
        trade_area_4.wkt_representation(wkt_representation = 'LINESTRING(3 1, 1 3, -3 1, 1 -3)')

        # mock trade areas
        trade_area_5 = TradeArea()
        trade_area_5.trade_area_id = 46
        trade_area_5.store_id = 46
        trade_area_5.threshold_id = 1
        trade_area_5.period_id = 3
        trade_area_5.wkt_representation(wkt_representation = 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)')

        trade_area_6 = TradeArea()
        trade_area_6.trade_area_id = 47
        trade_area_6.store_id = 46
        trade_area_6.threshold_id = 2
        trade_area_6.period_id = 3
        trade_area_6.wkt_representation(wkt_representation = 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)')

        self._sql_provider.competitive_trade_areas = [trade_area_3, trade_area_4, trade_area_5, trade_area_6]
        self._sql_provider.trade_areas = [trade_area_1, trade_area_2, trade_area_3, trade_area_4, trade_area_5, trade_area_6]


        self._sql_provider.trade_area_shapes = {trade_area_1.trade_area_id: 'LINESTRING(1 0, 0 1, -1 0, 0 -1)',
                                                trade_area_2.trade_area_id: 'LINESTRING(2 0, 0 2, -2 0, 0 -2)',
                                                trade_area_3.trade_area_id: 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)',
                                                trade_area_4.trade_area_id: 'LINESTRING(3 1, 1 3, -3 1, 1 -3)',
                                                trade_area_5.trade_area_id: 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)',
                                                trade_area_6.trade_area_id: 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)'}

        self._postgres_provider.shape_areas = {trade_area_1.wkt_representation(): 4,
                                               trade_area_2.wkt_representation(): 16}

        Overlap = namedtuple('Overlap', ['shape_1', 'shape_2'])

        self._postgres_provider.overlap_areas = {Overlap(shape_1 = trade_area_1.wkt_representation(), shape_2 = trade_area_3.wkt_representation()): 1.0,
                                                 Overlap(shape_1 = trade_area_1.wkt_representation(), shape_2 = trade_area_5.wkt_representation()): 2.0,
                                                 Overlap(shape_1 = trade_area_2.wkt_representation(), shape_2 = trade_area_4.wkt_representation()): 3.0,
                                                 Overlap(shape_1 = trade_area_2.wkt_representation(), shape_2 = trade_area_6.wkt_representation()): 4.0}

        self._postgres_provider.shape_centroids = {trade_area_1.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_2.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_3.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_4.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_5.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_6.wkt_representation(): 'POINT(0 0)'}

        self._postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_1.wkt_representation())): 1,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_2.wkt_representation())): 2,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_3.wkt_representation())): 3,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_4.wkt_representation())): 4,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_5.wkt_representation())): 5,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_6.wkt_representation())): 6}

        self._sql_provider.saved_trade_areas = []
        self._sql_provider.saved_trade_area_overlap_objects = []
        shape_processor = GP3GeoShapeProcessor(self._store.store_id)
        shape_processor._initialize()
        shape_processor._do_geoprocessing()
        shape_processor._preprocess_data_for_save()
        shape_processor._save_processed_data()




        overlap_1 = TradeAreaOverlap()
        overlap_1.home_trade_area_id = trade_area_1.trade_area_id
        overlap_1.away_trade_area_id = trade_area_3.trade_area_id
        overlap_1.overlap_area = 1.0

        overlap_2 = TradeAreaOverlap()
        overlap_2.home_trade_area_id = trade_area_1.trade_area_id
        overlap_2.away_trade_area_id = trade_area_5.trade_area_id
        overlap_2.overlap_area = 2.0

        overlap_3 = TradeAreaOverlap()
        overlap_3.home_trade_area_id = trade_area_2.trade_area_id
        overlap_3.away_trade_area_id = trade_area_4.trade_area_id
        overlap_3.overlap_area = 3.0

        overlap_4 = TradeAreaOverlap()
        overlap_4.home_trade_area_id = trade_area_2.trade_area_id
        overlap_4.away_trade_area_id = trade_area_6.trade_area_id
        overlap_4.overlap_area = 4.0


        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[0].home_trade_area_id, overlap_1.home_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[0].away_trade_area_id, overlap_1.away_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[0].overlap_area, overlap_1.overlap_area)

        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[1].home_trade_area_id, overlap_2.home_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[1].away_trade_area_id, overlap_2.away_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[1].overlap_area, overlap_2.overlap_area)

        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[2].home_trade_area_id, overlap_3.home_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[2].away_trade_area_id, overlap_3.away_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[2].overlap_area, overlap_3.overlap_area)

        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[3].home_trade_area_id, overlap_4.home_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[3].away_trade_area_id, overlap_4.away_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[3].overlap_area, overlap_4.overlap_area)


    def test_process(self):

        geoshape_calculator = GISCalculator()

        # mock trade areas
        trade_area_1 = TradeArea()
        trade_area_1.trade_area_id = 42
        trade_area_1.store_id = 42
        trade_area_1.threshold_id = 1
        trade_area_1.period_id = 3
        trade_area_1.wkt_representation(wkt_representation = 'LINESTRING(1 0, 0 1, -1 0, 0 -1)')

        trade_area_2 = TradeArea()
        trade_area_2.trade_area_id = 43
        trade_area_2.store_id = 42
        trade_area_2.threshold_id = 2
        trade_area_2.period_id = 3
        trade_area_2.wkt_representation(wkt_representation = 'LINESTRING(2 0, 0 2, -2 0, 0 -2)')

        # mock trade areas
        trade_area_3 = TradeArea()
        trade_area_3.trade_area_id = 44
        trade_area_3.store_id = 44
        trade_area_3.threshold_id = 1
        trade_area_3.period_id = 3
        trade_area_3.wkt_representation(wkt_representation = 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)')

        trade_area_4 = TradeArea()
        trade_area_4.trade_area_id = 45
        trade_area_4.store_id = 44
        trade_area_4.threshold_id = 2
        trade_area_4.period_id = 3
        trade_area_4.wkt_representation(wkt_representation = 'LINESTRING(3 1, 1 3, -3 1, 1 -3)')

        # mock trade areas
        trade_area_5 = TradeArea()
        trade_area_5.trade_area_id = 46
        trade_area_5.store_id = 46
        trade_area_5.threshold_id = 1
        trade_area_5.period_id = 3
        trade_area_5.wkt_representation(wkt_representation = 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)')

        trade_area_6 = TradeArea()
        trade_area_6.trade_area_id = 47
        trade_area_6.store_id = 46
        trade_area_6.threshold_id = 2
        trade_area_6.period_id = 3
        trade_area_6.wkt_representation(wkt_representation = 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)')

        self._sql_provider.competitive_trade_areas = [trade_area_3, trade_area_4, trade_area_5, trade_area_6]
        self._sql_provider.trade_areas = [trade_area_1, trade_area_2, trade_area_3, trade_area_4, trade_area_5, trade_area_6]

        self._sql_provider.trade_area_shapes = {trade_area_1.trade_area_id: 'LINESTRING(1 0, 0 1, -1 0, 0 -1)',
                                                trade_area_2.trade_area_id: 'LINESTRING(2 0, 0 2, -2 0, 0 -2)',
                                                trade_area_3.trade_area_id: 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)',
                                                trade_area_4.trade_area_id: 'LINESTRING(3 1, 1 3, -3 1, 1 -3)',
                                                trade_area_5.trade_area_id: 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)',
                                                trade_area_6.trade_area_id: 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)'}

        self._postgres_provider.shape_1_area = 4
        self._postgres_provider.shape_2_area = 16

        self._postgres_provider.shape_areas = {trade_area_1.wkt_representation(): 4,
                                               trade_area_2.wkt_representation(): 16}

        Overlap = namedtuple('Overlap', ['shape_1', 'shape_2'])

        self._postgres_provider.overlap_areas = {Overlap(shape_1 = trade_area_1.wkt_representation(), shape_2 = trade_area_3.wkt_representation()): 1.0,
                                                 Overlap(shape_1 = trade_area_1.wkt_representation(), shape_2 = trade_area_5.wkt_representation()): 2.0,
                                                 Overlap(shape_1 = trade_area_2.wkt_representation(), shape_2 = trade_area_4.wkt_representation()): 3.0,
                                                 Overlap(shape_1 = trade_area_2.wkt_representation(), shape_2 = trade_area_6.wkt_representation()): 4.0}

        self._postgres_provider.shape_centroids = {trade_area_1.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_2.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_3.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_4.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_5.wkt_representation(): 'POINT(0 0)',
                                                   trade_area_6.wkt_representation(): 'POINT(0 0)'}

        self._postgres_provider.srids_UTMs_datums = {geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_1.wkt_representation())): 1,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_2.wkt_representation())): 2,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_3.wkt_representation())): 3,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_4.wkt_representation())): 4,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_5.wkt_representation())): 5,
                                                     geoshape_calculator._get_UTM_zone(geoshape_calculator.get_centroid(trade_area_6.wkt_representation())): 6}

        shape_processor = GP3GeoShapeProcessor(self._store.store_id)
        shape_processor.process()

        self.assertEqual(shape_processor._home_trade_areas[0].trade_area_id, self._store.store_id)
        self.assertEqual(shape_processor._home_trade_areas[1].trade_area_id, self._store.store_id + 1)

        self.assertEqual(shape_processor._home_trade_areas[0].store_id, self._store.store_id)
        self.assertEqual(shape_processor._home_trade_areas[1].store_id, self._store.store_id)

        self.assertEqual(shape_processor._home_trade_areas[0].threshold_id, 1)
        self.assertEqual(shape_processor._home_trade_areas[1].threshold_id, 2)

        self.assertEqual(shape_processor._home_trade_areas[0].period_id, 3)
        self.assertEqual(shape_processor._home_trade_areas[1].period_id, 3)

        self.assertEqual(shape_processor._home_trade_areas[0].wkt_representation(), 'LINESTRING(1 0, 0 1, -1 0, 0 -1)')
        self.assertEqual(shape_processor._home_trade_areas[1].wkt_representation(), 'LINESTRING(2 0, 0 2, -2 0, 0 -2)')


        self.assertEqual(shape_processor._away_trade_areas, [trade_area_3, trade_area_4, trade_area_5, trade_area_6])
        self.assertEqual(shape_processor._away_trade_areas[0].wkt_representation(), 'LINESTRING(1.5 0.5, 0.5 1.5, -1.5 0.5, 0.5 -1.5)')
        self.assertEqual(shape_processor._away_trade_areas[1].wkt_representation(), 'LINESTRING(3 1, 1 3, -3 1, 1 -3)')
        self.assertEqual(shape_processor._away_trade_areas[2].wkt_representation(), 'LINESTRING(0.5 -0.5, -0.5 0.5, -1.5 -0.5, -0.5 -1.5)')
        self.assertEqual(shape_processor._away_trade_areas[3].wkt_representation(), 'LINESTRING(1 -1, -1 1, -3 -1, -1 -3)')

        self.assertEqual(shape_processor._away_trade_areas[0].period_id, 3)
        self.assertEqual(shape_processor._away_trade_areas[1].period_id, 3)
        self.assertEqual(shape_processor._away_trade_areas[2].period_id, 3)
        self.assertEqual(shape_processor._away_trade_areas[3].period_id, 3)

        overlap_1 = TradeAreaOverlap()
        overlap_1.home_trade_area_id = trade_area_1.trade_area_id
        overlap_1.away_trade_area_id = trade_area_3.trade_area_id
        overlap_1.overlap_area = 1.0

        overlap_2 = TradeAreaOverlap()
        overlap_2.home_trade_area_id = trade_area_1.trade_area_id
        overlap_2.away_trade_area_id = trade_area_5.trade_area_id
        overlap_2.overlap_area = 2.0

        overlap_3 = TradeAreaOverlap()
        overlap_3.home_trade_area_id = trade_area_2.trade_area_id
        overlap_3.away_trade_area_id = trade_area_4.trade_area_id
        overlap_3.overlap_area = 3.0

        overlap_4 = TradeAreaOverlap()
        overlap_4.home_trade_area_id = trade_area_2.trade_area_id
        overlap_4.away_trade_area_id = trade_area_6.trade_area_id
        overlap_4.overlap_area = 4.0

        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[0].home_trade_area_id, overlap_1.home_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[0].away_trade_area_id, overlap_1.away_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[0].overlap_area, overlap_1.overlap_area)

        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[1].home_trade_area_id, overlap_2.home_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[1].away_trade_area_id, overlap_2.away_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[1].overlap_area, overlap_2.overlap_area)

        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[2].home_trade_area_id, overlap_3.home_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[2].away_trade_area_id, overlap_3.away_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[2].overlap_area, overlap_3.overlap_area)

        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[3].home_trade_area_id, overlap_4.home_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[3].away_trade_area_id, overlap_4.away_trade_area_id)
        self.assertEqual(self._sql_provider.saved_trade_area_overlap_objects[3].overlap_area, overlap_4.overlap_area)