from geoprocessing.business_logic.business_objects.trade_area import TradeArea
from common.utilities.sql import sql_execute, sql_execute_with_parameters
from geoprocessing.data_access.demographics_handler import get_data_item_id_by_name
from geoprocessing.data_access.store_handler import _construct_latitude_longitude_where_statement

__author__ = 'erezrubinstein'

"""
This module represents various data access methods for dealing with trade area tables
"""

def save_trade_area_surface_area(trade_area):


    surface_area_data_item_id = get_data_item_id_by_name('SurfaceArea')

    statement = '''if not exists (select trade_area_analytic_id from trade_area_analytics where trade_area_id = ? and period_id = ? and data_item_id = ?)
                   begin
                       insert into trade_area_analytics (trade_area_id, period_id, data_item_id, value, created_at, updated_at) values (?, ?, ?, ?, GETUTCDATE(), GETUTCDATE())
                   end
                   else
                   begin
                       update trade_area_analytics set value = ? where trade_area_id = ? and period_id = ? and data_item_id = ?
                   end
                '''

    parameters = [trade_area.trade_area_id, trade_area.period_id, surface_area_data_item_id, trade_area.trade_area_id, trade_area.period_id, surface_area_data_item_id, trade_area.area,
                  trade_area.area, trade_area.trade_area_id, trade_area.period_id, surface_area_data_item_id]

    sql_execute_with_parameters(parameters, statement)

def save_trade_area_overlap(trade_area_overlap):


    # trade area overlap is reflexive
    statement = '''if not exists (select trade_area_overlap_id from trade_area_overlaps where (home_trade_area_id = ? and away_trade_area_id = ?) or (home_trade_area_id = ? and away_trade_area_id = ?))

                   begin
                       insert into trade_area_overlaps (home_trade_area_id, away_trade_area_id, overlap_area, created_at, updated_at) values (?, ?, ?, GETUTCDATE(), GETUTCDATE())
                       insert into trade_area_overlaps (home_trade_area_id, away_trade_area_id, overlap_area, created_at, updated_at) values (?, ?, ?, GETUTCDATE(), GETUTCDATE())
                   end

                   else
                   begin
                       update trade_area_overlaps set overlap_area = ? where home_trade_area_id = ? and away_trade_area_id = ?
                       update trade_area_overlaps set overlap_area = ? where home_trade_area_id = ? and away_trade_area_id = ?
                   end
                '''
    parameters = [trade_area_overlap.home_trade_area_id, trade_area_overlap.away_trade_area_id,
                  trade_area_overlap.away_trade_area_id, trade_area_overlap.home_trade_area_id,
                  trade_area_overlap.home_trade_area_id, trade_area_overlap.away_trade_area_id, trade_area_overlap.overlap_area,
                  trade_area_overlap.away_trade_area_id, trade_area_overlap.home_trade_area_id, trade_area_overlap.overlap_area,
                  trade_area_overlap.overlap_area, trade_area_overlap.home_trade_area_id, trade_area_overlap.away_trade_area_id,
                  trade_area_overlap.overlap_area, trade_area_overlap.away_trade_area_id, trade_area_overlap.home_trade_area_id]

    sql_execute_with_parameters(parameters, statement)

def select_trade_area_force_insert(store_id, threshold_id):
    """
    This method selects a trade area.  if it doesn't exist, it inserts it
    """

    # get trade id from __store_id ASSUMING 1 trade_id / __store_id
    # create a trade area object

    command_insert = '''
                        IF NOT EXISTS (SELECT trade_area_id FROM trade_areas WHERE store_id = %d and threshold_id = %d)
                        BEGIN
                            INSERT INTO trade_areas (store_id, created_at, updated_at, threshold_id)
                            VALUES (%d, GETUTCDATE(), GETUTCDATE(), %d)
                        END;''' % (store_id, threshold_id, store_id, threshold_id)

    command_select = '''SELECT trade_area_id FROM trade_areas WHERE store_id = %d and threshold_id = %d''' % (store_id, threshold_id)

    sql_execute(command_insert)

    row = sql_execute(command_select)

    trade_area_id = row[0].trade_area_id

    trade_area = TradeArea()

    trade_area.trade_area_id = trade_area_id
    trade_area.store_id = store_id
    trade_area.threshold_id = threshold_id



    return trade_area


def insert_trade_area_shape(trade_area_id, wkt_representation, period_id):

    # get trade id from __store_id ASSUMING 1 trade_id / __store_id
    # create a trade area object
    statement = '''
                        IF NOT EXISTS (SELECT trade_area_id, period_id FROM trade_area_shapes WHERE trade_area_id = %d and period_id = %d)
                        BEGIN
                            INSERT INTO trade_area_shapes (trade_area_id, period_id, wkt_shape, created_at, updated_at)
                            VALUES (%d, %d, '%s', GETUTCDATE(), GETUTCDATE())
                        END;''' % (trade_area_id, period_id, trade_area_id, period_id, str(wkt_representation))

    sql_execute(statement)

def select_trade_area_by_store_id_and_threshold_id(store_id, threshold_id):

    statement = '''
                    SELECT
                        trade_areas.store_id,
                        trade_areas.trade_area_id,
                        trade_areas.threshold_id,
                        trade_area_shapes.wkt_shape,
                        trade_area_shapes.period_id

                    FROM trade_areas
                    inner join trade_area_shapes on trade_area_shapes.trade_area_id = trade_areas.trade_area_id
                    WHERE trade_areas.store_id = %d and trade_areas.threshold_id = %d

                ''' % (store_id, threshold_id)

    row = sql_execute(statement)[0]



    trade_area = TradeArea()
    trade_area.trade_area_id = row.trade_area_id
    trade_area.store_id = row.store_id
    trade_area.threshold_id = row.threshold_id
    trade_area.__wkt_representation_linestring = row.wkt_shape
    trade_area.period_id = row.period_id

    return trade_area

def select_trade_areas_for_core_export(store_ids):

    additional_where_clause = ''
    if store_ids:
        additional_where_clause = 'and stores.store_id in (%s)' % store_ids

    # huge select - TODO: replace store_id with core_store_id
    statement = '''
                SELECT
                    stores.store_id,
                    trade_areas.trade_area_id,
                    trade_areas.threshold_id,
                    companies.name,
                    periods_actual.period_start_date,
                    periods_actual.period_end_date,
                    duration_types.name,
                    demographic_numvalues.value,
                    data_items.name,
                    data_items.description,
                    periods_target.period_start_date,
                    stores.core_store_id,
                    addresses.street_number,
                    addresses.street,
                    addresses.municipality,
                    addresses.governing_district,
                    addresses.postal_area,
                    addresses.longitude,
                    addresses.latitude,
                    stores.phone_number,
                    stores.assumed_opened_date,
                    stores.assumed_closed_date,
                    addresses.suite,
                    addresses.shopping_center_name
                FROM demographic_numvalues
                inner join trade_areas on trade_areas.trade_area_id = demographic_numvalues.trade_area_id
                inner join stores on stores.store_id = trade_areas.store_id
                inner join addresses on addresses.address_id = stores.address_id
                inner join companies on companies.company_id = stores.company_id
                inner join periods as periods_actual on periods_actual.period_id = demographic_numvalues.period_id
                inner join duration_types on duration_types.duration_type_id = periods_actual.duration_type_id
                inner join periods as periods_target on periods_target.period_id = demographic_numvalues.target_period_id
                inner join data_items on data_items.data_item_id = demographic_numvalues.data_item_id

                -- TOTPOP_CY, PCI_CY, TOTHH_CY, and HINC*_CY_P
                where demographic_numvalues.data_item_id in (13, 16, 48, 52, 56, 60, 64, 68, 72, 76, 80, 88) %s

    ''' % additional_where_clause
    return sql_execute(statement)

def select_trade_areas_by_store_id_require_shape(store_id):

    statement = '''
                    SELECT
                        trade_areas.store_id,
                        trade_areas.trade_area_id,
                        trade_areas.threshold_id,
                        trade_area_shapes.wkt_shape,
                        trade_area_shapes.period_id

                    FROM trade_areas
                    inner join trade_area_shapes on trade_area_shapes.trade_area_id = trade_areas.trade_area_id
                    WHERE trade_areas.store_id = %d

                ''' % store_id

    rows = sql_execute(statement)

    trade_areas = []
    for row in rows:

        trade_area = TradeArea()
        trade_area.trade_area_id = row.trade_area_id
        trade_area.store_id = row.store_id
        trade_area.threshold_id = row.threshold_id
        trade_area.wkt_representation(wkt_representation = row.wkt_shape)
        trade_area.period_id = row.period_id

        trade_areas.append(trade_area)

    return trade_areas

def delete_trade_area_shape(trade_area):
    # delete shape
    statement = '''delete from trade_area_shapes where trade_area_id = ?'''
    parameters = [trade_area.trade_area_id]
    sql_execute_with_parameters(parameters, statement)

def delete_trade_area_analytics(trade_area):
    # delete analytics
    statement = '''delete from trade_area_analytics where trade_area_id = ?'''
    parameters = [trade_area.trade_area_id]
    sql_execute_with_parameters(parameters, statement)

def delete_trade_area(trade_area):
    statement = '''delete from trade_areas where trade_area_id = ?'''
    parameters = [trade_area.trade_area_id]
    sql_execute_with_parameters(parameters, statement)

def select_away_trade_areas_within_lat_long_range(home_store, longitude_ranges, latitude_range):

    lat_long_where_clause = _construct_latitude_longitude_where_statement(latitude_range, longitude_ranges)
    competitive_trade_areas_statement = '''
                                SELECT
                                    trade_areas.store_id,
                                    trade_areas.trade_area_id,
                                    trade_areas.threshold_id,
                                    trade_area_shapes.wkt_shape,
                                    trade_area_shapes.period_id
                                FROM trade_areas
                                INNER JOIN trade_area_shapes on trade_area_shapes.trade_area_id = trade_areas.trade_area_id
                                INNER JOIN stores ON stores.store_id = trade_areas.store_id
                                INNER JOIN addresses AS a ON a.address_id = stores.address_id
                                INNER JOIN companies on companies.company_id = stores.company_id
                                INNER JOIN competitive_companies on competitive_companies.away_company_id = companies.company_id
                                WHERE competitive_companies.home_company_id = %d
                                    %s
                                ORDER BY trade_areas.trade_area_id asc''' % (home_store.company_id, lat_long_where_clause)

    rows = sql_execute(competitive_trade_areas_statement)

    trade_areas = []
    for row in rows:
        trade_area = TradeArea()
        trade_area.trade_area_id = row.trade_area_id
        trade_area.threshold_id = row.threshold_id
        trade_area.store_id = row.store_id
        trade_area.__wkt_representation_linestring = row.wkt_shape
        trade_area.period_id = row.period_id
        trade_areas.append(trade_area)
    return trade_areas



def select_trade_area_shape_by_id(trade_area_id):

    statement = '''select wkt_shape from trade_area_shapes where trade_area_id = %d''' % int(trade_area_id)
    shape = sql_execute(statement)[0]
    return shape.wkt_shape

def select_period_id_from_trade_area_shapes_by_id(trade_area_id):

    statement = ''' select period_id from trade_area_shapes where trade_area_id = %d ''' % int(trade_area_id)
    shape = sql_execute(statement)[0]
    return shape.period_id


def get_trade_area_by_id(trade_area_id):
    statement = ''' select trade_area_id, store_id, created_at, updated_at, threshold_id from trade_areas
                    where trade_area_id = ? '''
    parameters = [int(trade_area_id)]
    row = sql_execute_with_parameters(parameters, statement)[0]
    return TradeArea.standard_init(row.trade_area_id, row.store_id, row.created_at, row.updated_at, row.threshold_id)
