from collections import namedtuple
import unittest
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from geoprocessing.business_logic.enums import TradeAreaThreshold
from common.utilities.inversion_of_control import dependencies, Dependency
from common.utilities.signal_math import SignalDecimal
from geoprocessing.geoprocessors.proximity.gp4_zipcode_proximity import GP4ZipCodeProximityProcessor
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.zip_code import ZipCode

__author__ = 'jsternberg'

class GP4ZipCodeProximityTests(unittest.TestCase):

    def setUp(self):
        # set up mock dependencies

        register_mock_dependencies()
        self._sql_provider = Dependency("DataRepository").value

        self._postgres_repository = Dependency('PostgresDataRepository').value
        self._threshold = TradeAreaThreshold.LatitudeLongitudeDecimal

        # set up test store
        self._company_id = 999
        self._store_id = 1024
        self._longitude = -100.00000
        self._latitude = 45.00000
        self._store_point = GeographicalCoordinate(self._longitude, self._latitude)
        self._store = Store.simple_init_with_address(self._store_id, self._company_id, self._longitude, self._latitude)
        self._store.address.zip_code = 12345
        self._sql_provider.stores[self._store.store_id] = self._store
        self._store.address_id = 10
        self._sql_provider.addresses[10] = self._store.address

        # set up mock data store centroids: 1 for the store, 1 other nearby zip code
        self._nearby_zip_code = '12346'
        self._nearby_zip_point = GeographicalCoordinate(self._longitude + 0.001, self._latitude + 0.001)
        self._zips = [ZipCode.standard_init(self._store.address.zip_code, self._store_point),
                      ZipCode.standard_init(self._nearby_zip_code, self._nearby_zip_point)]
        self._sql_provider.zips = self._zips

        self._store_zip_proximities = [{'store_id': self._store_id,
                                        'zip_code': self._store.address.zip_code,
                                        'threshold_id': self._threshold,
                                        'proximity': SignalDecimal(0.0)},
                                       {'store_id': self._store_id,
                                        'zip_code': self._nearby_zip_code,
                                        'threshold_id': self._threshold,
                                        'proximity': SignalDecimal(-0.001)}]




    def tearDown(self):
        dependencies.clear()

    def test_initialize(self):


        gp4 = GP4ZipCodeProximityProcessor(self._threshold)
        self.assertEqual(gp4._threshold, self._threshold)
        self.assertEqual(gp4._zips, None)

        self.assertEqual(gp4._store_zip_proximities, [])

        gp4._company_id = self._company_id
        gp4._store_id = self._store_id
        gp4._home_store = self._store

        # run the test function and assert
        gp4._initialize()
        self.assertEqual(gp4._zips, self._zips)

    def test_do_geoprocessing(self):
        gp4 = GP4ZipCodeProximityProcessor(self._threshold)
        gp4._company_id = self._company_id
        gp4._store_id = self._store_id
        gp4._home_store = self._store
        gp4._initialize()

        # set up what we expect from the mock
        expected_zip_proximities = self._store_zip_proximities
        coordinate_pair = namedtuple('coordinate_par', ['point_1', 'point_2'])

        self._postgres_repository.distance = {coordinate_pair(self._store_point.wkt_representation(), self._store_point.wkt_representation()): SignalDecimal(0.0),
                                              coordinate_pair(self._store_point.wkt_representation(), self._nearby_zip_point.wkt_representation()): SignalDecimal(-0.001)}
        # run the test function and assert
        gp4._do_geoprocessing()
        self.assertEqual(gp4._store_zip_proximities, expected_zip_proximities)

    def test_save_processed_date(self):

        # set up what we expect from the mock
        expected_saved_zip_proximities = self._store_zip_proximities
        coordinate_pair = namedtuple('coordinate_par', ['point_1', 'point_2'])

        self._postgres_repository.distance = {coordinate_pair(self._store_point.wkt_representation(), self._store_point.wkt_representation()): SignalDecimal(0.0),
                                              coordinate_pair(self._store_point.wkt_representation(), self._nearby_zip_point.wkt_representation()): SignalDecimal(-0.001)}

        gp4 = GP4ZipCodeProximityProcessor(self._threshold)
        gp4._company_id = self._company_id
        gp4._store_id = self._store_id
        gp4._home_store = self._store
        gp4._initialize()
        gp4._do_geoprocessing()


        # run the test function and assert
        gp4._save_processed_data()
        self.assertEqual(self._sql_provider.zip_proximities, expected_saved_zip_proximities)

    def test_process(self):
        # set up what we expect from the mock
        expected_saved_zip_proximities = self._store_zip_proximities
        coordinate_pair = namedtuple('coordinate_par', ['point_1', 'point_2'])

        self._postgres_repository.distance = {coordinate_pair(self._store_point.wkt_representation(), self._store_point.wkt_representation()): SignalDecimal(0.0),
                                              coordinate_pair(self._store_point.wkt_representation(), self._nearby_zip_point.wkt_representation()): SignalDecimal(-0.001)}
        # run the test function and assert
        GP4ZipCodeProximityProcessor(self._threshold).process(self._company_id, self._store_id)
        self.assertEqual(self._sql_provider.zip_proximities, expected_saved_zip_proximities)
