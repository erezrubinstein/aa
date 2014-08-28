import unittest
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate

__author__ = 'erezrubinstein'


class GeographicalCoordinateTests(unittest.TestCase):
    def test_get_search_limits_simple(self):
        """
        Test that a simple coordinate calculates its search limit properly
        """
        point = GeographicalCoordinate(40, 40)

        #get search limit and assert results
        lat_longs = point.get_search_limits()
        #assert latitudes
        self.assertEqual(lat_longs["latitudes"].start, 39)
        self.assertEqual(lat_longs["latitudes"].stop, 41)
        #assert longitudes
        self.assertEqual(len(lat_longs["longitudes"]), 1)
        self.assertEqual(lat_longs["longitudes"][0].start, 39)
        self.assertEqual(lat_longs["longitudes"][0].stop, 41)

    def test_get_search_limits_90_degree_latitudes(self):
        """
        Test that coordinates with latitudes close to 90/-90 degrees
        calculates their search limit properly
        """
        point = GeographicalCoordinate(40, 89.75)

        #get search limit and assert results
        lat_longs = point.get_search_limits()
        #assert latitudes
        self.assertEqual(lat_longs["latitudes"].start, 88.75)
        self.assertEqual(lat_longs["latitudes"].stop, 90)
        #assert longitudes
        self.assertEqual(len(lat_longs["longitudes"]), 1)
        self.assertEqual(lat_longs["longitudes"][0].start, 39)
        self.assertEqual(lat_longs["longitudes"][0].stop, 41)

    def test_get_search_limits_negative_90_degree_latitudes(self):
        """
        Test that coordinates with latitudes close to 90/-90 degrees
        calculates their search limit properly
        """
        point = GeographicalCoordinate(40, -89.75)

        #get search limit and assert results
        lat_longs = point.get_search_limits()
        #assert latitudes
        self.assertEqual(lat_longs["latitudes"].start, -90)
        self.assertEqual(lat_longs["latitudes"].stop, -88.75)
        #assert longitudes
        self.assertEqual(len(lat_longs["longitudes"]), 1)
        self.assertEqual(lat_longs["longitudes"][0].start, 39)
        self.assertEqual(lat_longs["longitudes"][0].stop, 41)

    def test_get_search_limits_180_degree_longitude(self):
        """
        Test that coordinates with latitudes close to 180 degrees
        calculates their search limit properly
        """
        point = GeographicalCoordinate(179.75, 40)

        #get search limit and assert results
        lat_longs = point.get_search_limits()
        #assert latitudes
        self.assertEqual(lat_longs["latitudes"].start, 39)
        self.assertEqual(lat_longs["latitudes"].stop, 41)
        #assert longitudes
        self.assertEqual(len(lat_longs["longitudes"]), 2)
        self.assertEqual(lat_longs["longitudes"][0].start, 178.75)
        self.assertEqual(lat_longs["longitudes"][0].stop, 180)
        self.assertEqual(lat_longs["longitudes"][1].start, -180)
        self.assertEqual(lat_longs["longitudes"][1].stop, -179.25)

    def test_get_search_limits_negative_180_degree_longitude(self):
        """
        Test that coordinates with latitudes close to -180 degrees
        calculates their search limit properly
        """
        point = GeographicalCoordinate(-179.75, 40)

        #get search limit and assert results
        lat_longs = point.get_search_limits()
        #assert latitudes
        self.assertEqual(lat_longs["latitudes"].start, 39)
        self.assertEqual(lat_longs["latitudes"].stop, 41)
        #assert longitudes
        self.assertEqual(len(lat_longs["longitudes"]), 2)
        self.assertEqual(lat_longs["longitudes"][0].start, -180)
        self.assertEqual(lat_longs["longitudes"][0].stop, -178.75)
        self.assertEqual(lat_longs["longitudes"][1].start, 179.25)
        self.assertEqual(lat_longs["longitudes"][1].stop, 180)



if __name__ == '__main__':
    unittest.main()