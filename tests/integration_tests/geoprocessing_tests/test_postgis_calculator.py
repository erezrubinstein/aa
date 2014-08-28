import unittest
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from common.utilities.signal_math import SignalDecimal
from geoprocessing.business_logic.config import Config
from geoprocessing.data_access.data_repository import PostgresDataRepository
from geoprocessing.helpers.postgis_calculator import GISCalculator

__author__ = 'spacecowboy'

class PostGISCalculatorTests(unittest.TestCase):

    def setUp(self):
        # set up dependencies
        self.config = Config().instance
        dependencies.register_dependency('Config', self.config)
        self.postgis_repo = PostgresDataRepository()
        dependencies.register_dependency('PostgresDataRepository', self.postgis_repo)
        dependencies.register_dependency('LogManager', LogManager(1000000))
        self.postgis_calculator = GISCalculator()

    def tearDown(self):
        dependencies.clear()

########################################### test private methods #######################################################

    def test_get_UTM_zone(self):
        # new yorkish
        centroid = GeographicalCoordinate(-74.00, 0)
        utm_zone = self.postgis_calculator._get_UTM_zone(centroid)
        self.assertEqual(utm_zone, '18N')

        # san francisco
        centroid = GeographicalCoordinate(-122.4183, 0)
        utm_zone = self.postgis_calculator._get_UTM_zone(centroid)
        self.assertEqual(utm_zone, '10N')

    def test_parse_geoocorddinate_from_string(self):

        point_string = 'POINT(-70.2342 4)'
        coordinate = self.postgis_calculator._parse_geocoordinate_from_point_string(point_string)
        self.assertEqual(coordinate.longitude, SignalDecimal(-70.2342))
        self.assertEqual(coordinate.latitude, SignalDecimal(4))

        point_string = 'POINT(-70.2342 -4.0)'
        coordinate = self.postgis_calculator._parse_geocoordinate_from_point_string(point_string)
        self.assertEqual(coordinate.longitude, SignalDecimal(-70.2342))
        self.assertEqual(coordinate.latitude, SignalDecimal(-4.0))

        point_string = 'POINT(1 2)'
        coordinate = self.postgis_calculator._parse_geocoordinate_from_point_string(point_string)
        self.assertEqual(coordinate.longitude, SignalDecimal(1))
        self.assertEqual(coordinate.latitude, SignalDecimal(2))

    def test_compute_midpoint(self):

        point_1 = GeographicalCoordinate(4, 4)
        point_2 = GeographicalCoordinate(6, 6)
        midpoint = self.postgis_calculator._compute_midpoint(point_1, point_2)
        self.assertEqual(midpoint.longitude, SignalDecimal(5))
        self.assertEqual(midpoint.latitude, SignalDecimal(5))

########################################### test public methods ########################################################

    def test_get_surface_area(self):

        shape_1 = 'LINESTRING(-74.000 40.000, -74.1000 40.0, -74.05 40.1, -74.000 40.000)'
        shape_2 = 'LINESTRING(-74.000 40.000, -74.0500 40.0, -74.05 40.1, -74.000 40.000)'

        sa_1 = self.postgis_calculator.get_surface_area(shape_1)
        sa_2 = self.postgis_calculator.get_surface_area(shape_2)

        # require precision to the 100 square centimeters (arbitrary)
        self.assertEqual(int(sa_1), int(47373426.3777178))
        self.assertEqual(int(sa_2), int(23689369.5304368))

    def test_get_centroid(self):

        shape = 'LINESTRING(71 40, 70 41, 69 40, 70 39, 71 40)'
        centroid = self.postgis_calculator.get_centroid(shape)
        self.assertEqual(centroid.longitude, 70)
        self.assertEqual(centroid.latitude, 40)

        shape = 'LINESTRING(71.10 0, 0 41.10, -71.10 0, 0 -41.10, 71.10 0)'
        centroid = self.postgis_calculator.get_centroid(shape)
        self.assertEqual(centroid.longitude, 0)
        self.assertEqual(centroid.latitude, 0)

    def test_determine_srid_from_centroid(self):

        # new yorkish
        centroid = GeographicalCoordinate(-74.00, 0)
        srid = self.postgis_calculator.determine_srid_from_geocoordinate(centroid)
        self.assertEqual(srid, 32618)

        # san francisco
        centroid = GeographicalCoordinate(-122.4183, 0)
        srid = self.postgis_calculator.determine_srid_from_geocoordinate(centroid)
        self.assertEqual(srid, 32610)

    def test_compute_overlap_fraction(self):
        shape_1 = 'LINESTRING(-74.000 40.000, -74.1000 40.0, -74.05 40.1, -74.000 40.000)'
        shape_2 = 'LINESTRING(-74.000 40.000, -74.0500 40.0, -74.05 40.1, -74.000 40.000)'

        o_12 = self.postgis_calculator.compute_overlap_area(shape_1, shape_2)
        o_21 = self.postgis_calculator.compute_overlap_area(shape_2, shape_1)

        self.assertAlmostEqual(o_12, 23689369.531, 2)
        self.assertAlmostEqual(o_21, 23689369.531, 2)

    def test_get_distance_between_points(self):
        point_1 = GeographicalCoordinate(-74.000, 40.000)
        point_2 = GeographicalCoordinate(-74.123, 40.123)
        distance = self.postgis_calculator.get_distance_between_points(point_1, point_2)
        self.assertAlmostEqual(distance, 17223.4992899359)

    ########################################## test private methods ########################################################

    def test_get_utm_zone(self):
        shape_1 = 'LINESTRING(-74.000 40.000, -74.1000 40.0, -74.05 40.1, -74.000 40.000)'
        shape_2 = 'LINESTRING(-74.000 40.000, -74.0500 40.0, -74.05 40.1, -74.000 40.000)'

        centroid_1 = self.postgis_calculator.get_centroid(shape_1)
        centroid_2 = self.postgis_calculator.get_centroid(shape_2)

        self.assertAlmostEqual(self.postgis_calculator._get_UTM_zone(centroid_1), '18N')
        self.assertAlmostEqual(self.postgis_calculator._get_UTM_zone(centroid_2), '18N')

    def test_shape_contains_point(self):
        point = GeographicalCoordinate(-73, 42).wkt_representation()
        shape = 'LINESTRING(-74 44, -72 44, -72 41, -74 41, -74 44)'
        self.assertTrue(self.postgis_calculator.shape_contains_point(shape, point))

    def test_shape_contains_point_negative(self):
        point = GeographicalCoordinate(-75, 40).wkt_representation()
        shape = 'LINESTRING(-74 44, -72 44, -72 41, -74 41, -74 44)'
        self.assertFalse(self.postgis_calculator.shape_contains_point(shape, point))