from collections import namedtuple

__author__ = 'spacecowboy'

class MockPostgresDataRepository(object):

    def __init__(self):
        self.shape_1_area = None
        self.shape_2_area = None
        self.distance = {}
        self.overlap_areas = {}
        self.shape_point_booleans = {}
        self.shape_centroids = {}
        self.srids_UTMs_datums = {}
        self.shape_areas = {}

    def get_surface_area(self, shape, srid, wkid):
        return self.shape_areas[shape]

    def compute_overlap_area(self, shape_1, shape_2, wkid, midpoint_srid):

        overlap = namedtuple('overlap', ['shape_1', 'shape_2'])
        return self.overlap_areas[overlap(shape_1 = shape_1, shape_2 = shape_2)]

    def get_distance_between_points(self, point_1, point_2):

        coordinate_pair = namedtuple('coordinate_par', ['point_1', 'point_2'])
        return self.distance[coordinate_pair(point_1 = point_1, point_2 = point_2)]

    def shape_contains_point(self, shape, point, wkid):
        if (shape, point) in self.shape_point_booleans.keys():
            return self.shape_point_booleans[(shape, point)]

    def shape_contains_points(self, shape, points, wkid):

        # create array of matches
        matches = []

        # create named tuple
        match = namedtuple('match', ['is_contained_within', 'point'])

        # add all points with a true, false for matches
        for point in points:

            matches.append(match(is_contained_within = self.shape_point_booleans.get((shape, point), False), point = point))

        return matches

    def get_centroid_point_string_from_shape(self, shape, wkid):
        return self.shape_centroids[shape]

    def determine_srid_from_UTM_and_datum(self, utm_zone, geodetic_network_datum):
        return self.srids_UTMs_datums[utm_zone]