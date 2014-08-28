__author__ = 'ujjwal'

import unittest
from common.helpers.mapnik.mapnik_helper import get_google_tile_lat_lon_bounds, WebMercator_Bounds


class TestMapnikHelper(unittest.TestCase):

    def test_get_google_tile_lat_lon_bounds(self):

        tile_x = -1
        tile_y = 2
        zoom = 3
        latlons = get_google_tile_lat_lon_bounds(tile_x, tile_y, zoom, precision=8)
        expected_latons = [135, 40.97989807, 180, 66.51326044]
        self.assertItemsEqual(latlons, expected_latons)

        tile_x = 0
        tile_y = 0
        zoom = 2
        latlons = get_google_tile_lat_lon_bounds(tile_x, tile_y, zoom, precision=9)
        expected_latons = [-180.0, 66.513260443, -90, 85.05112878]
        self.assertItemsEqual(latlons, expected_latons)

        tile_x = 245
        tile_y = 356
        zoom = 10
        latlons = get_google_tile_lat_lon_bounds(tile_x, tile_y, zoom, precision=9)
        expected_latons = [-93.8671875, 47.75409798, -93.515625, 47.989921667]
        self.assertItemsEqual(latlons, expected_latons)

        tile_x = 144583
        tile_y = 470370
        zoom = 21
        latlons = get_google_tile_lat_lon_bounds(tile_x, tile_y, zoom, precision=14)
        expected_latons = [-155.18068313598633, 69.9395466636361, -155.18051147460938, 69.9396055453679]
        self.assertItemsEqual(latlons, expected_latons)

        tile_x = 53
        tile_y = 5
        zoom = 3
        latlons = get_google_tile_lat_lon_bounds(tile_x, tile_y, zoom, precision=10)
        expected_latons = [45.0, -66.5132604431, 90.0, -40.9798980696]
        self.assertItemsEqual(latlons, expected_latons)

        tile_x = 0
        tile_y = 0
        zoom = 0
        latlons = get_google_tile_lat_lon_bounds(tile_x, tile_y, zoom, precision=8)
        expected_latons = [-180.0, -85.05112878, 180.0, 85.05112878]
        self.assertItemsEqual(latlons, expected_latons)

if __name__ == '__main__':

    unittest.main()