from common.utilities.sql import postgis_execute

__author__ = 'spacecowboy et al.'



def get_geoco_city_state_zip(geoco):
    statement = '''select city state zip from reverse_geocode_results where longitude = %f and latitude = %f ''' % (geoco.longitude, geoco.latitude)
    return postgis_execute(statement)[0]

def get_surface_area(shape, srid, wkid):
    statement = '''select st_area(st_transform(st_polygon(st_geomfromtext('%s', %d), %d), %d))''' % (shape, wkid, wkid, srid)

    surface_area = postgis_execute(statement)[0][0]
    return int(surface_area)

def get_centroid_point_string_from_shape(shape, wkid):
    statement = '''select st_astext(st_centroid(st_polygon(st_geomfromtext('%s', %d), %d)))''' % (shape, wkid, wkid)

    point_string = postgis_execute(statement)[0][0]
    return point_string

def determine_srid_from_UTM_and_datum(utm_zone, geodetic_network_datum):

    unit_requirement = ''.join(['%', 'units=m', '%'])
    # srtext example: "+proj=utm +zone=50 +south +ellps=bessel +towgs84=-377,681,-50,0,0,0,0 +units=m +no_defs"
    srtext_datum_requirement = ''.join(['%', geodetic_network_datum, ' / UTM zone ', utm_zone, '%'])

    # selects the closest srid to the trade area centroid
    statement = '''select srid from spatial_ref_sys where proj4text like '%s' and srtext like '%s' ''' % (unit_requirement, srtext_datum_requirement)

    srid = postgis_execute(statement)[0][0]
    return int(srid)

def shape_contains_point(shape, point, wkid):

    statement = ''' select st_covers(st_polygon(st_geomfromtext('%s', %d), %d), st_geomfromtext('%s', %d))''' % (shape, wkid, wkid, point, wkid)
    return postgis_execute(statement)[0][0]


def shape_contains_points(shape, points, wkid):

    # just in case...
    if not points:
        return []

    # build shapes CTE
    shapes_cte = """
    WITH shapes AS
    (
        SELECT st_polygon(st_geomfromtext('%s', %d), %d) as shape
    ), """ % (shape, wkid, wkid)

    # build points CTE
    points_sql = " UNION ALL ".join([
        "SELECT st_geomfromtext('%s', %d) AS point, '%s' as text" % (point, wkid, point)
        for point in points
    ])
    points_cte = """
    points AS
    (
         %s
    ) """ % points_sql

    # create main_statement
    main_select = """
    SELECT st_covers(s.shape, p.point) as is_contained_within, p.text as point
    from shapes s, points p"""
    statement = "".join([shapes_cte, points_cte, main_select])

    # Meat wad makes the money see
    return postgis_execute(statement)


def multi_shape_contain_points(shapes, points, wkid):

    # just in case...
    if not points or not shapes:
        return []

    # create the shape select statements
    shape_select_statements = [
        "SELECT st_polygon(st_geomfromtext('%s', %d), %d) as shape" % (shape, wkid, wkid)
        for shape in shapes
    ]
    shape_select_statements = " UNION ALL\n".join(shape_select_statements)

    # build shapes CTE
    shapes_cte = """
    WITH shapes AS
    (
        %s
    ), """ % shape_select_statements

    # build points CTE
    points_sql = " UNION ALL ".join([
        "SELECT st_geomfromtext('%s', %d) AS point, '%s'::text as text" % (point, wkid, point)
        for point in points
    ])
    points_cte = """
    points AS
    (
         %s
    ) """ % points_sql

    # create main_statement
    main_select = """
    SELECT bool_or(st_covers(s.shape, p.point)) as is_contained_within, p.text as point
    from shapes s, points p
    group by p.text
    """
    statement = "".join([shapes_cte, points_cte, main_select])

    # Meat wad makes the money see
    return postgis_execute(statement)


def compute_overlap_area(shape_1, shape_2, wkid, midpoint_srid):

    statement = '''select st_area(st_transform(st_intersection(
                                                                   st_polygon(st_geomfromtext('%s', %d), %d), st_polygon(st_geomfromtext('%s', %d),
                                                                   %d)), %d))''' % (shape_1, wkid, wkid, shape_2, wkid, wkid, midpoint_srid)
    area_overlap = postgis_execute(statement)[0][0]
    return area_overlap

def determine_intersecting_shape(shape_1, shape_2, wkid):

    statement = '''select ST_AsText(st_intersection(st_polygon(st_geomfromtext('%s', %d), %d),
                                                    st_polygon(st_geomfromtext('%s', %d), %d)))''' % (shape_1, wkid, wkid, shape_2, wkid, wkid)

    intersecting_shape = postgis_execute(statement)[0][0]
    return intersecting_shape

def determine_union_shape(shape_1, shape_2, wkid):
    statement = '''select ST_AsText(st_union(st_polygon(st_geomfromtext('%s', %d), %d),
                                             st_polygon(st_geomfromtext('%s', %d), %d)))''' % (shape_1, wkid, wkid, shape_2, wkid, wkid)
    union_shape = postgis_execute(statement)[0][0]
    return union_shape


def get_distance_between_points(wkt_point_1, wkt_point_2):

    statement = '''select st_distance(st_geographyfromtext('%s'), st_geographyfromtext('%s')) ''' % (wkt_point_1, wkt_point_2)
    distance = postgis_execute(statement)[0][0]
    return distance
