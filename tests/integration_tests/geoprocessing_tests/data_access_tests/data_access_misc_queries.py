"""
Created on Oct 21, 2012

@author: erezrubinstein
"""
from geoprocessing.business_logic.business_objects.store import Store
from common.utilities.inversion_of_control import Dependency, HasAttributes
from common.utilities.sql import sql_execute, sql_execute_on_db, sql_execute_with_parameters

#####################################################################################################################
################################################  Insert Statements  ################################################
#####################################################################################################################
from geoprocessing.business_logic.enums import CompetitionType


def insert_test_report_item(report_item, source):
    statement = ''' insert into data_items (name, description, type, source) values ('%s', '%s', '%s', '%s')''' % (report_item.name, report_item.description, report_item.value_type, source)
    sql_execute(statement)


def insert_test_competitive_store(competitive_company_id, trade_area_id, home_store_id, away_store_id, start_date, end_date):

    # insert dummy value into competitive_company_id, because we really don't care
    statement = """
    insert into competitive_stores (competitive_company_id, trade_area_id, home_store_id, away_store_id, start_date, end_date, created_at, updated_at)
    VALUES (%s, %s, %s, %s, ?, ?, getutcdate(), getutcdate())
    """ % (competitive_company_id, trade_area_id, home_store_id, away_store_id)

    sql_execute_with_parameters([start_date, end_date], statement)


def insert_test_monopoly(trade_area_id, store_id, monopoly_type_id = 2, start_date = None, end_date = None):

    # insert dummy value into competitive_company_id, because we really don't care
    statement = """
    insert into monopolies (trade_area_id, store_id, monopoly_type_id, start_date, end_date, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, getutcdate(), getutcdate())
    """

    sql_execute_with_parameters([trade_area_id, store_id, monopoly_type_id, start_date, end_date], statement)


def insert_test_demographic(trade_area_id, data_item_id, value, template_name = "woot"):
    statement = """
    insert into demographic_numvalues (trade_area_id, data_item_id, value, created_at, updated_at, segment_id, period_id, target_period_id, template_name)
    VALUES(%s, %s, %s, getutcdate(),  getutcdate(), NULL, 3, 3, '%s')
    """ % (str(trade_area_id), str(data_item_id), str(value), template_name)
    sql_execute(statement)

    # return the id that was just inserted
    statement2 = "select @@Identity"
    row = sql_execute(statement2)
    return int(row[0][0])


def insert_test_trade_area(trade_area):
    statement = ''' insert into trade_areas (store_id, threshold_id, created_at, updated_at)
                    values (%d, %d, GETUTCDATE(), GETUTCDATE())''' % (trade_area.store_id, trade_area.threshold_id)

    sql_execute(statement)


def insert_test_trade_area_raw(store_id, threshold_id):
    statement = ''' insert into trade_areas (store_id, threshold_id, created_at, updated_at)
                    values (%d, %d, GETUTCDATE(), GETUTCDATE())''' % (store_id, threshold_id)

    sql_execute(statement)

    # return the id that was just inserted
    statement2 = "select @@Identity"
    row = sql_execute(statement2)
    return int(row[0][0])


def insert_test_source_file(full_path, file_created_date, file_size_in_bytes):

    statement = ''' INSERT INTO source_files (full_path, file_created_date, file_modified_date, file_size_in_bytes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, GETUTCDATE(), GETUTCDATE()) '''
    parameters = [full_path, file_created_date, file_created_date, file_size_in_bytes]

    sql_execute_with_parameters(parameters, statement)
    statement2 = "select @@Identity"
    row = sql_execute(statement2)
    return int(row[0][0])

def insert_test_source_file_record(source_file_id, row_number, record, loader_record_id, street_number, street, city,
                                   state, zip, country_id, phone, longitude, latitude, suite, shopping_center_name,
                                   opened_date, source_date, note, store_format, company_generated_store_number):

    statement = '''insert into source_file_records (source_file_id,
                          row_number,
                          record,
                          loader_record_id,
                          street_number,
                          street,
                          city,
                          state,
                          zip,
                          country_id,
                          phone,
                          longitude,
                          latitude,
                          suite,
                          shopping_center_name,
                          opened_date,
                          source_date,
                          note,
                          store_format,
                          company_generated_store_number,
                          created_at,
                          updated_at)
                        values (?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?,
                            ?, GETUTCDATE(), GETUTCDATE())'''

    parameters = [source_file_id, row_number, record, loader_record_id, street_number, street, city, state,
                      zip, country_id, phone, longitude, latitude, suite, shopping_center_name, opened_date,
                      source_date, note, store_format, company_generated_store_number]

    sql_execute_with_parameters(parameters, statement)
    statement2 = "select @@Identity"
    row = sql_execute(statement2)
    return int(row[0][0])

def insert_test_company(ticker = '', name = 'UNITTESTCOMPANY'):
    statement = '''
    insert into companies (ticker, name, created_at, updated_at)
    VALUES(?, ?, GETUTCDATE(), GETUTCDATE()) '''
    parameters = [ticker, name]
    sql_execute_with_parameters(parameters, statement)
    statement2 = "select @@Identity"
    row = sql_execute(statement2)
    return int(row[0][0])
    
def insert_test_competitor(home_company_id, away_company_id, assumed_start_date = None, assumed_end_date = None, competition_strength = 1):
    assumed_end_date = __fix_date_value(assumed_end_date)
    assumed_start_date = __fix_date_value(assumed_start_date)

    statement = '''
insert into competitive_companies (home_company_id, away_company_id, competition_strength, created_at, updated_at, assumed_start_date, assumed_end_date)
VALUES (%d, %d, %s, GETUTCDATE(), GETUTCDATE(), %s, %s)
''' % (home_company_id, away_company_id, str(competition_strength), assumed_start_date, assumed_end_date)
    statement2 = "select @@Identity"
    rows = sql_execute(statement, statement2)
    return int(rows[0][0])
    
def insert_test_segment(minimum_age = 400, maximum_age = 404, gender = "F"):
    statement = '''
insert into demographic_segments (minimum_age, maximum_age, gender, created_at, updated_at)
VALUES (?, ?, ?, GETUTCDATE(), GETUTCDATE())'''
    statement2 = "select @@Identity"
    sql_execute_with_parameters([minimum_age, maximum_age, gender], statement)
    row = sql_execute(statement2)
    return int(row[0][0])
    
def insert_test_address(longitude, latitude, street_number = 0, street = 'UNITTEST', municipality = 'UNITTEST', governing_district = 'NY', postal_area = 11111):
    statement = '''
insert into addresses (street_number, street, municipality, governing_district, postal_area, country_id, latitude, longitude, created_at, updated_at)
VALUES(?, ?, ?, ?, ?, 840, ?, ?, getdate(), getdate())'''
    parameters = [street_number, street, municipality, governing_district, postal_area, latitude, longitude]
    sql_execute_with_parameters(parameters, statement)
    statement2 = "select @@Identity" 
    row = sql_execute(statement2)
    return int(row[0][0])
    
def insert_test_store(company_id, address_id, opened_date = None, closed_date = None, assumed_opened_date = None, assumed_closed_date = None, phone_number = '(000) 000-0000',
                      store_format = None, company_generated_store_number = None, note = None):
    statement = '''
    insert into stores (company_id, address_id, phone_number, store_format, company_generated_store_number, note, opened_date, closed_date, assumed_opened_date, assumed_closed_date, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE())'''
    parameters = [company_id, address_id, phone_number, store_format, company_generated_store_number, note, opened_date, closed_date, assumed_opened_date, assumed_closed_date]
    sql_execute_with_parameters(parameters, statement)
    statement2 = "select @@Identity"
    row = sql_execute(statement2)
    return int(row[0][0])

def insert_cbsa_store_match(cbsa_id, store_id):

    statement = "insert into cbsa_store_matches (store_id, cbsa_id) VALUES(?, ?)"
    sql_execute_with_parameters([store_id, cbsa_id], statement)
    statement2 = "select @@Identity"
    row = sql_execute(statement2)
    return int(row[0][0])

def insert_county_store_match(county_id, store_id):

    statement = "insert into county_store_matches (store_id, county_id) VALUES(?, ?)"
    sql_execute_with_parameters([store_id, county_id], statement)
    statement2 = "select @@Identity"
    row = sql_execute(statement2)
    return int(row[0][0])

def insert_and_return_test_period_id(period_id=5):
    statement = ''' INSERT INTO periods (duration_type_id, period_start_date, period_end_date) VALUES (%d, GETUTCDATE(), GETUTCDATE())''' % period_id
    statement2 = "SELECT @@Identity"
    row = sql_execute(statement, statement2)
    return int(row[0][0])

def insert_test_problem_address(store_id, longitude, latitude):
    store = Store().select_by_id(store_id)
    statement = '''INSERT INTO addresses_history (address_id, longitude, latitude, created_at, updated_at)
                   VALUES (%d, %f, %f, GETUTCDATE(), GETUTCDATE())
    ''' % (store.address_id, latitude, longitude)
    statement2 = "SELECT @@Identity"
    row = sql_execute(statement, statement2)
    return int(row[0][0])

def insert_test_entity_type(entity_type_id, name):
    statement = '''INSERT INTO entity_types (entity_type_id, name)
                   VALUES (?, ?)
                   '''
    parameters = [entity_type_id, name]
    sql_execute_with_parameters(parameters, statement)


def insert_test_data_check_type(data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold):
    statement = '''INSERT INTO data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
                   VALUES (?, ?, ?, ?, ?, ?)
                   '''
    parameters = [data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold]
    sql_execute_with_parameters(parameters, statement)

def insert_test_sector(sector_name):
    statement = """
    INSERT INTO sectors (name, created_at, updated_at)
    VALUES ('%s', GETUTCDATE(), GETUTCDATE())""" % sector_name
    statement2 = "SELECT @@Identity"

    return sql_execute(statement, statement2)[0][0]

def insert_test_company_sector(sector_id, company_id):
    statement = """
    INSERT INTO companies_sectors (sector_id, company_id, [primary], created_at, updated_at, assumed_start_date, assumed_end_date)
    VALUES(%d, %d, 1, GETUTCDATE(), GETUTCDATE(), NULL, NULL)""" % (sector_id, company_id)
    statement2 = "SELECT @@Identity"

    return sql_execute(statement, statement2)[0][0]

def insert_test_zip(zip_code, longitude, latitude):
    statement = """
    insert into zip_codes (zip_code, POP10, HU10, ALAND, AWATER, ALAND_SQLMI, AWATER_SQLMI, INTPTLONG, INTPTLAT)
    values ('%s', 1, 1, 1, 1, 1, 1, %f, %f)""" % (zip_code, longitude, latitude)
    statement2 = "select zip_code from zip_codes where zip_code = '%s'" % (zip_code)
    return sql_execute(statement, statement2)[0][0]


#####################################################################################################################
################################################  Select Statements  ################################################
#####################################################################################################################

def select_all_cbsas():
    return sql_execute("select name as cbsa_name, population, pci, agg_income from cbsa")

def select_all_counties_with_state():
    return sql_execute("select name + ', ' + state as county_name, community_code, community_description, population, pci, agg_income from counties")

def select_all_cbsa_matches():
    return sql_execute("select cbsa_id, store_id from cbsa_store_matches")

def select_all_county_matches():
    return sql_execute("select county_id, store_id from county_store_matches")

def select_cbsa_by_id(cbsa_id):

    # run this sucka
    statement = "select cbsa_id, name, points_json, max_degrees from cbsa where cbsa_id = ?"
    return sql_execute_with_parameters([cbsa_id], statement)[0]

def select_county_by_id(county_id):

    # run this sucka
    statement = "select county_id, name, points_json, max_degrees from counties where county_id = ?"
    return sql_execute_with_parameters([county_id], statement)[0]

def select_company_by_id(company_id):
    statement = "select company_id, ticker, name, created_at, updated_at from companies where company_id = ?"
    return sql_execute_with_parameters([company_id], statement)[0]

def select_competitive_companies_by_home_company_id(home_company_id):
    statement = """
select competitive_company_id, home_company_id, away_company_id, competition_strength, created_at, updated_at, assumed_start_date, assumed_end_date
from competitive_companies
where home_company_id = ?"""
    return sql_execute_with_parameters([home_company_id], statement)



def select_surface_area_by_trade_area_id(trade_area_id):

    statement = '''select value from trade_area_analytics
                   inner join data_items on data_items.data_item_id = trade_area_analytics.data_item_id
                   where data_items.name = 'SurfaceArea' and trade_area_analytics.trade_area_id = %d''' % trade_area_id
    row = sql_execute(statement)
    return row[0][0]

def select_count_trade_area_by_store(store_id):
    statement = "select count(*) from trade_areas where store_id = %d" % store_id
    row = sql_execute(statement)
    return row[0][0]
    
def select_trade_area_id_by_store(store_id):
    statement = "select trade_area_id from trade_areas where store_id = %d" % store_id
    row = sql_execute(statement)
    return row[0][0]

def select_count_data_items(report_item):
    statement = """
                    SELECT count(*) FROM data_items WHERE name = '%s' AND description = '%s' AND type = '%s'
                """ % (report_item.name, report_item.description, report_item.value_type)
    row = sql_execute(statement)
    return row[0][0]

def select_demographic_numvalues(trade_area_id, order_by_data_item = False):
    statement = """
select demographic_numvalue_id, data_item_id, value, target_period_id, period_id, template_name
from demographic_numvalues
where trade_area_id = %d""" % trade_area_id

    if order_by_data_item:
        statement += """
order by data_item_id, template_name"""

    return sql_execute(statement)

def select_demographic_strvalues(trade_area_id, order_by_data_item = False):
    statement = """
select demographic_strvalue_id, data_item_id, value, target_period_id, period_id, template_name
from demographic_strvalues
where trade_area_id = %d""" % trade_area_id

    if order_by_data_item:
        statement += """
order by data_item_id, template_name"""

    return sql_execute(statement)

def select_monopolies(store_id, trade_area_id):
    statement = '''
select store_id, trade_area_id, created_at, updated_at
from monopolies
where store_id = ? and trade_area_id = ?'''
    return sql_execute_with_parameters([store_id, trade_area_id], statement)

def select_monopolies_postgis(store_id, trade_area_id):
    statement = '''
select store_id, trade_area_id, created_at, updated_at
from monopolies_postgis
where store_id = ? and trade_area_id = ?'''
    return sql_execute_with_parameters([store_id, trade_area_id], statement)

def select_competitive_stores(store_id, trade_area_id):
    statement = """
select competitive_store_id, competitive_company_id, home_store_id, away_store_id, trade_area_id, travel_time, created_at, updated_at, start_date, end_date
from competitive_stores
where home_store_id = ? and trade_area_id = ?"""
    return sql_execute_with_parameters([store_id, trade_area_id], statement)

def select_competitive_stores_postgis(store_id, trade_area_id):

    statement = """
                    select competitive_store_id, competitive_company_id, home_store_id, away_store_id, trade_area_id, created_at, updated_at, start_date, end_date
                    from competitive_stores_postgis
                    where home_store_id = %d and trade_area_id = %d""" % (store_id, trade_area_id)

    return sql_execute(statement)

def select_test_log_entry_count():
    statement = "select count(*) from log_entries where message like '%unit%'"

    # get config for logging db credentials
    config = Dependency("Config", HasAttributes("logging_db_server", "logging_db_database",
        "logging_db_username", "logging_db_password")).value

    return sql_execute_on_db(config.logging_db_server, config.logging_db_database, config.logging_db_username,
        config.logging_db_password, statement)[0][0]

def select_test_problem_long_lat(problem_address_id):
    statement = '''SELECT longitude, latitude FROM addresses_history WHERE id = %d''' % problem_address_id
    return sql_execute(statement)

def select_test_log_entries():
    statement = """
select *
from log_entries where message like '%unit%'"""

    # get config for logging db credentials
    config = Dependency("Config", HasAttributes("logging_db_server", "logging_db_database",
        "logging_db_username", "logging_db_password")).value

    return sql_execute_on_db(config.logging_db_server, config.logging_db_database, config.logging_db_username,
        config.logging_db_password, statement)

def select_last_period_id():
    statement = "select top 1 period_id from periods order by period_id desc"
    return sql_execute(statement)[0][0]

def select_test_data_check(data_check_id):
    statement = '''
    SELECT data_check_id, data_check_type_id, check_done, bad_data_rows
    FROM data_checks
    WHERE data_check_id = ?
    '''
    parameters = [data_check_id]
    return sql_execute_with_parameters(parameters, statement)[0]

def select_test_data_check_values(data_check_id):
    # get data check value objects ordered by data_check_value_id to facilitate list comparison
    statement = '''
    SELECT data_check_value_id, data_check_id, value_type, expected_value, actual_value, entity_id
    FROM data_check_values
    WHERE data_check_id = ?
    ORDER BY data_check_value_id
    '''
    parameters = [data_check_id]
    return sql_execute_with_parameters(parameters, statement)

def select_count_companies_by_name(company_name):
    statement = "select count(*) from companies where name = ?"
    return sql_execute_with_parameters([company_name], statement)[0][0]

def select_sectors_for_company(company_id):
    statement = "select id, sector_id, company_id, [primary], created_at, updated_at, assumed_start_date, assumed_end_date from companies_sectors where company_id = ?"
    return sql_execute_with_parameters([company_id], statement)

def select_company_sectors_by_id(sector_id):
    statement = "select id, sector_id, company_id, [primary], created_at, updated_at, assumed_start_date, assumed_end_date from companies_sectors where sector_id = ?"
    return sql_execute_with_parameters([sector_id], statement)

def select_count_sectors_by_name(sector_name):
    statement = "select count(*) as count from sectors where name = ?"
    return sql_execute_with_parameters([sector_name], statement)[0][0]

def select_address_by_address_id(address_id):
    statement = """
select
    address_id, street_number, street, municipality, governing_district, postal_area,
    country_id, latitude, longitude, created_at, updated_at, suite, shopping_center_name, min_source_date, max_source_date
from addresses where address_id = ?"""
    return sql_execute_with_parameters([address_id], statement)[0]

def select_store_by_store_id(store_id):
    statement = """
select store_id, company_id, address_id, phone_number, opened_date, note, assumed_opened_date, assumed_closed_date, created_at, updated_at
from stores
where store_id = ?"""
    return sql_execute_with_parameters([store_id], statement)[0]

def select_source_file_notes_by_id(source_file_id):
    statement = ''' select note from source_file_records where source_file_id = %d''' % source_file_id
    return sql_execute(statement)

def select_source_file_by_id(source_file_id):
    statement = """
select source_file_id, full_path, file_created_date, file_modified_date, file_size_in_bytes, created_at, updated_at
from source_files
where source_file_id = ?"""
    return sql_execute_with_parameters([source_file_id], statement)[0]

def select_stores_change_log_entries(source_file_id):
    statement = """
select store_id, log_date, change_type_id, comment, source_file_id, created_at, updated_at
from stores_change_log
where source_file_id = ?"""
    return sql_execute_with_parameters([source_file_id], statement)

def select_addresses_change_log_entries(source_file_id):
    statement = """
select address_id, log_date, change_type_id, comment, source_file_id, created_at, updated_at
from addresses_change_log
where source_file_id = ?"""
    return sql_execute_with_parameters([source_file_id], statement)

def select_addresses_change_log_values(source_file_id):
    statement = """
    select v.addresses_change_log_id, v.value_type, v.from_value, v.to_value, v.created_at, v.updated_at
from addresses_change_log_values v
where exists (
    select 1 from addresses_change_log acl
    where acl.addresses_change_log_id = v.addresses_change_log_id
    and acl.source_file_id = ?)"""
    return sql_execute_with_parameters([source_file_id], statement)

def select_trade_area_overlap(home_trade_area_id, away_trade_area_id):

    statement = '''select overlap_area from trade_area_overlaps where home_trade_area_id = %d and away_trade_area_id = %d''' % (home_trade_area_id, away_trade_area_id)
    return sql_execute(statement)[0][0]



#####################################################################################################################
################################################  Delete Statements  ################################################
#####################################################################################################################

def delete_all_from_cbsa_store_matches():
    sql_execute("delete from cbsa_store_matches")

def delete_all_from_county_store_matches():
    sql_execute("delete from county_store_matches")

def delete_county_store_matches_for_stores(store_ids):
    store_ids_str = ', '.join([str(store_id) for store_id in store_ids])
    sql_execute("delete from county_store_matches where store_id in (%s)" % store_ids_str)

def delete_test_segment(segment_id):
    statement = '''delete from demographic_segments where demographic_segment_id = %d''' % segment_id
    sql_execute(statement)
    
def delete_demographic_num_and_str_values(trade_area_id):
    statement1 = """
delete from demographic_numvalues 
where trade_area_id = %d""" % trade_area_id
    statement2 = """
delete from demographic_strvalues 
where trade_area_id = %d""" % trade_area_id
    sql_execute(statement1, statement2)

def delete_demographic_num_value_by_demographics_id(demographic_num_value_id):
    statement = "delete from demographic_numvalues where demographic_numvalue_id = %d" % demographic_num_value_id
    sql_execute(statement)

def delete_test_address(address_id):
    statement = '''delete from addresses where address_id = %d''' % address_id
    sql_execute(statement)

def delete_test_problem_address(problem_address_id):
    statement = '''DELETE FROM addresses_history WHERE addresses_history_id = %d''' % problem_address_id
    sql_execute(statement)

def delete_test_trade_area(store_id):
    statement = '''delete from trade_areas where store_id = %d''' % store_id
    sql_execute(statement)

def delete_test_trade_area_shape(trade_area_id):
    statement = ''' delete from trade_area_shapes where trade_area_id = %d ''' % trade_area_id
    sql_execute(statement)

def delete_test_trade_area_overlap(trade_area_id):
    statement = ''' delete from trade_area_overlaps where home_trade_area_id = %d''' % trade_area_id
    sql_execute(statement)

def delete_test_trade_area_by_trade_area_id(trade_area_id):
    statement = '''delete from trade_areas where trade_area_id = %d''' % trade_area_id
    sql_execute(statement)

def delete_test_surface_area(trade_area_id, area = None):
    # create base statement
    statement = 'delete from trade_area_analytics where trade_area_id = %d' % trade_area_id

    # add area if specified
    if area:
        statement += ' and value = %d' % area

    # delete
    sql_execute(statement)
    
def delete_data_item(report_item):
    statement = '''
delete from data_items where name = '%s' and description = '%s'
and type = '%s' 
''' % (report_item.name, report_item.description, report_item.value_type)
    sql_execute(statement)

def delete_test_store(store_id):
    statement = '''delete from stores where store_id = %d''' % store_id
    sql_execute(statement)

def delete_test_company(company_id):
    statement = '''delete from companies where company_id = %d''' % company_id
    sql_execute(statement)

#def delete_test_data_check_type(data_check_type):
#    statement = '''DELETE FROM data_check_types WHERE name = '%s' ''' % data_check_type
#    sql_execute(statement)

def delete_test_data_check(data_check_id):
    statement_data_check_values = '''DELETE FROM data_check_values WHERE data_check_id = %d''' % data_check_id
    statement_data_check = '''DELETE FROM data_checks WHERE data_check_id = %d''' % data_check_id
    sql_execute(statement_data_check_values, statement_data_check)

#def delete_test_data_check_values(data_check_id):
#    statement = '''DELETE FROM data_check_values WHERE data_check_id = '%d' ''' % data_check_id
#    sql_execute(statement)


def delete_test_competitors(home_company_id):
    statement = "delete from competitive_companies where home_company_id = %d" % home_company_id
    sql_execute(statement)

def delete_competitive_stores(store_id, trade_area_id):
    statement = "delete from competitive_stores where home_store_id = ? and trade_area_id = ? "
    sql_execute_with_parameters([store_id, trade_area_id], statement)

def delete_competitive_stores_postgis(store_id, trade_area_id):
    statement = "delete from competitive_stores_postgis where home_store_id = ? and trade_area_id = ? "
    sql_execute_with_parameters([store_id, trade_area_id], statement)

def delete_monopolies(store_id, trade_area_id):
    statement = "delete from monopolies where store_id = ? and trade_area_id = ?"
    sql_execute_with_parameters([store_id, trade_area_id], statement)

def delete_all_monopolies(trade_area_ids):
    if trade_area_ids:
        trade_area_in_string = ", ".join([str(ta_id) for ta_id in trade_area_ids])
        statement = "delete from monopolies where trade_area_id in (%s)" % trade_area_in_string
        sql_execute(statement)

def delete_monopolies_postgis(store_id, trade_area_id):
    statement = "delete from monopolies_postgis where store_id = ? and trade_area_id = ?"
    sql_execute_with_parameters([store_id, trade_area_id], statement)

def delete_test_log_entries():
    statement = "delete from log_entries where message like '%unit%'"

    # get config for logging db credentials
    config = Dependency("Config", HasAttributes("logging_db_server", "logging_db_database",
        "logging_db_username", "logging_db_password")).value

    sql_execute_on_db(config.logging_db_server, config.logging_db_database, config.logging_db_username,
        config.logging_db_password, statement)

def delete_period(period_id):
    statement = "delete from periods where period_id = ?"
    sql_execute_with_parameters([period_id], statement)

def delete_test_entity_type(entity_type_id):
    statement = '''DELETE FROM entity_types
                    WHERE entity_type_id = ?
                   '''
    parameters = [entity_type_id]
    sql_execute_with_parameters(parameters, statement)

def delete_test_period_id(period_id):
    statement = '''delete from periods where period_id = %d ''' % period_id
    sql_execute(statement)

def delete_data_check_type(data_check_type_id):
    statement = '''DELETE FROM data_check_types
                    WHERE data_check_type_id = ?
                   '''
    parameters = [data_check_type_id]
    sql_execute_with_parameters(parameters, statement)


def delete_test_sector(sector_id):
    statement = "delete from sectors where id = ?"
    return sql_execute_with_parameters([sector_id], statement)

def delete_test_company_sector(sector_id):
    statement = "delete from companies_sectors where sector_id = ?"
    return sql_execute_with_parameters([sector_id], statement)

def delete_test_source_file(source_file_id):
    statement = "delete from source_files where source_file_id = ?"
    sql_execute_with_parameters([source_file_id], statement)

def delete_test_source_file_record(source_file_record_id):
    statement = "delete from source_file_records where source_file_record_id = ?"
    sql_execute_with_parameters([source_file_record_id], statement)

def delete_store_change_logs_by_source_file_id(source_file_id):
    statement = "delete from stores_change_log where source_file_id = ?"
    sql_execute_with_parameters([source_file_id], statement)

def delete_addresses_change_logs_by_source_file_id(source_file_id):
    statement = "delete from addresses_change_log where source_file_id = ?"
    sql_execute_with_parameters([source_file_id], statement)

def delete_addresses_change_log_values_by_source_file_id(source_file_id):
    statement = """delete from addresses_change_log_values
    where addresses_change_log_id in (select addresses_change_log_id from addresses_change_log where source_file_id = ?)"""
    sql_execute_with_parameters([source_file_id], statement)

def delete_test_zip(zip_code):
    statement = "delete from zip_codes where zip_code = ?"
    sql_execute_with_parameters([zip_code], statement)

def delete_test_companies_and_competitive_companies():
    # a couple of delete statements for foreign keys (just in case there's unclean data in the db)

    statement_addresses = """delete addresses
from addresses a
inner join stores s on s.address_id = a.address_id
inner join companies co on s.company_id = co.company_id
and co.name like '%unittest_%'"""

    statement_demograhpic_strvalues = """delete demographic_strvalues
from demographic_strvalues d
inner join trade_areas t on t.trade_area_id = d.trade_area_id
inner join stores s on s.store_id = t.store_id
inner join companies co on s.company_id = co.company_id
and co.name like '%unittest_%'"""

    statement_demograhpic_numvalues = """delete demographic_numvalues
from demographic_numvalues d
inner join trade_areas t on t.trade_area_id = d.trade_area_id
inner join stores s on s.store_id = t.store_id
inner join companies co on s.company_id = co.company_id
and co.name like '%unittest_%'"""

    statement_trade_area_analytics = """delete trade_area_analytics
from trade_area_analytics ta
inner join trade_areas t on t.trade_area_id = ta.trade_area_id
inner join stores s on s.store_id = t.store_id
inner join companies co on s.company_id = co.company_id
and co.name like '%unittest_%'"""

    statement_trade_area_shapes = """delete trade_area_shapes
from trade_area_shapes ta
inner join trade_areas t on t.trade_area_id = ta.trade_area_id
inner join stores s on s.store_id = t.store_id
inner join companies co on s.company_id = co.company_id
and co.name like '%unittest_%'"""

    statement_trade_areas = """delete trade_areas
from trade_areas t
inner join stores s on s.store_id = t.store_id
inner join companies co on s.company_id = co.company_id
and co.name like '%unittest_%'"""

    statement_stores = """delete stores
from stores s
inner join companies co on s.company_id = co.company_id
and co.name like '%unittest_%'"""

    statement_competitive_companies = """delete competitive_companies
from competitive_companies cc
inner join companies co on cc.home_company_id = co.company_id
and co.name like '%unittest_%'"""

    statement_companies = "delete from companies where name like '%unittest_%'"
    sql_execute(statement_demograhpic_strvalues, statement_demograhpic_numvalues, statement_trade_area_shapes, statement_trade_area_analytics, statement_trade_areas,
                statement_stores, statement_addresses, statement_competitive_companies, statement_companies)

def delete_all_competitive_stores(store_ids):
    store_ids_str = ", ".join(str(id) for id in store_ids)
    sql_execute("delete from competitive_stores where home_store_id in (%s) or away_store_id in (%s)" % (store_ids_str, store_ids_str))

def delete_all_trade_areas(store_ids):
    store_ids_str = ", ".join(str(id) for id in store_ids)
    sql_execute("delete from trade_areas where store_id in (%s)" % store_ids_str)

def delete_all_demographic_numvalues(trade_area_ids):
    trade_area_ids_str = ", ".join(str(id) for id in trade_area_ids)
    sql_execute("delete from demographic_numvalues where trade_area_id in (%s)" % trade_area_ids_str)

def delete_all_stores(company_id):
    sql_execute("delete from stores where company_id = %s" % str(company_id))

def delete_all_companies():
    sql_execute("delete from companies")



#####################################################################################################################
################################################  Update Statements  ################################################
#####################################################################################################################

def update_competitive_companies_close(home_company_id,close_date):
    statement = "UPDATE competitive_companies SET assumed_end_date = ? WHERE home_company_id = ?"
    sql_execute_with_parameters([close_date, home_company_id], statement)






#####################################################################################################################
####################################################  Internal  #####################################################
#####################################################################################################################

def __fix_date_value(date_string):
    if date_string is None:
        return "NULL"
    else:
        return "'%s'" % date_string

