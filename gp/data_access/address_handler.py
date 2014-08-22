from decimal import Decimal
from common.utilities.misc_utilities import split_up_list_into_smaller_partitions
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from common.utilities.sql import sql_execute, sql_execute_with_parameters
from geoprocessing.data_access.data_access_utilities import select_clean_up, escape_string, insert_clean_up, insert_clean_up_string, escape_string_clean_up

__author__ = 'erezrubinstein'

"""
This module represents various data access methods for dealing with the address tables
"""

def get_address_by_id(address_id):

    statement = '''
    SELECT address_id, street_number, street, municipality, governing_district, postal_area, country_id, latitude, longitude, suite, shopping_center_name
    FROM addresses where address_id = ?'''
    record =  sql_execute_with_parameters([address_id], statement)[0]
    return Address.standard_init(record.address_id, record.street_number, record.street, record.municipality, record.governing_district, record.postal_area,
        record.country_id, record.latitude, record.longitude, record.suite, record.shopping_center_name)

def insert_new_address_get_id(address):
    # suite numbers can be a list of suites, empty list, or None
    # we format it twice because pyodbc needs "None" parameter instead of "is null"

    param_string_suite_numbers = __insert_param_select_string(address.suite_numbers)
    suite_numbers_param = param_string_suite_numbers[0]
    suite_numbers_string = param_string_suite_numbers[1]

    param_string_street = __insert_param_select_string(address.street)
    street_param = param_string_street[0]
    street_string = param_string_street[1]

    param_string_street_number = __insert_param_select_string(address.street_number)
    street_number_param = param_string_street_number[0]
    street_number_string = param_string_street_number[1]

    param_string_zip_code = __insert_param_select_string(address.zip_code)
    zip_code_param = param_string_zip_code[0]
    zip_code_string = param_string_zip_code[1]

    param_string_city = __insert_param_select_string(address.city)
    city_param = param_string_city[0]
    city_string = param_string_city[1]

    if address.complex:
        complex_insert_string = ''.join(["'", escape_string(address.complex), "'"])
        complex_select_string = ''.join(["= '", escape_string(address.complex), "'"])

    else:
        complex_insert_string = 'NULL'
        complex_select_string = 'IS NULL'

    rounded_longitude = address.longitude.quantize(Decimal(10) ** -6)
    rounded_latitude = address.latitude.quantize(Decimal(10) ** -6)

    statement = '''
                IF NOT EXISTS
                (
                    SELECT address_id
                    FROM addresses
                    WHERE street_number %s AND street %s AND municipality %s AND governing_district = ?
                        AND postal_area %s AND latitude = ? AND longitude = ? AND country_id %s AND suite %s AND shopping_center_name %s
                )
                BEGIN
                    INSERT INTO addresses (street_number, street, municipality, governing_district, postal_area, country_id, latitude, longitude, created_at,
                        updated_at, suite, shopping_center_name, min_source_date, max_source_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE(), ?, %s, ?, ?)
                END ''' % (street_number_string, street_string, city_string, zip_code_string, select_clean_up(address.country_id), suite_numbers_string, complex_select_string, complex_insert_string)

    # create insert parameters [sorry for long list :)]
    insert_parameters = [address.state, rounded_latitude, rounded_longitude,
                         street_number_param, street_param, city_param, address.state, zip_code_param, address.country_id, rounded_latitude, rounded_longitude,
                         suite_numbers_param, address.source_date, address.source_date]

    # insert address (if doesn't exist)
    sql_execute_with_parameters(insert_parameters, statement)

    # create select statement
    statement = '''
                    SELECT address_id
                    FROM addresses
                    WHERE street_number %s AND street %s AND municipality %s AND governing_district = ?
                        AND postal_area %s AND latitude = ? AND longitude = ? AND country_id %s  AND suite %s AND shopping_center_name %s
                        ''' % (street_number_string, street_string, city_string, zip_code_string, select_clean_up(address.country_id), suite_numbers_string, complex_select_string)
    # create insert parameters [sorry for long list :)]

    select_with_date_parameters = [address.state, rounded_latitude, rounded_longitude]

    # query and return address id
    row = sql_execute_with_parameters(select_with_date_parameters, statement)
    address.address_id = row[0].address_id

    return address

def __insert_param_select_string(attr):

    if attr and type(attr) == list:
        # for cases when the suite numbers = [u''] for bad loader records. eventually fix the bust in the address parser
        try:
            param = ', '.join(item for item in attr)
            string = ''.join(["= '", escape_string(param), "'"])
        # these are null suites
        except:
            param = None
            string = 'IS NULL'
    elif attr and type(attr) != list:
        param = attr
        string = ''.join(["= '", escape_string(attr), "'"])
    else:
        param = None
        string = 'IS NULL'

    return param, string



def get_problem_long_lat(store):
    long_lat_comm = ''' SELECT convert(decimal(9, 6), longitude) as longitude,
                        convert(decimal(9, 6), latitude) as latitude
                        FROM addresses_history
                        WHERE address_id = %d
                        ORDER BY created_at desc''' % store.address_id
    row = sql_execute(long_lat_comm)

    try:
        longitude = row[0][0]
        latitude = row[0][1]
        return GeographicalCoordinate(longitude, latitude)
    except:
        raise Exception('''Coordinate information not found for store %d''' % store.store_id)


def is_already_mopped(store):

    statement = '''
                    SELECT fixed FROM addresses_history
                    WHERE address_id = %d
                ''' % store.address_id

    row = sql_execute(statement)
    if len(row) > 0 and row[0][0] is not None:
        return 1
    else:
        return 0




def mark_as_mopped(store):

    statement = '''
    UPDATE addresses_history
    SET fixed = GETUTCDATE()
    WHERE address_id = %d
    ''' % store.address_id
    sql_execute(statement)

def select_addresses_within_range(longitude_ranges, latitude_range, company_id = None):
    longitude_insert = ' OR '.join('a.longitude between %f and %f' % (range.start, range.stop) for range in longitude_ranges)
    additional_where = ''
    if company_id:
        additional_where = 'AND s.company_id = %s' % company_id

    statement = '''
SELECT
    a.address_id,
    a.street_number,
    a.street,
    a.municipality,
    a.governing_district,
    a.postal_area,
    a.latitude,
    a.longitude,
    a.suite,
    a.max_source_date
FROM addresses a
INNER JOIN stores s on s.address_id = a.address_id
WHERE (a.latitude between ? and ?) AND (%s)
%s
ORDER BY a.max_source_date DESC
    ''' % (longitude_insert, additional_where)

    parameters = [latitude_range.start, latitude_range.stop]
    address_params_candidates = sql_execute_with_parameters(parameters, statement)

    candidate_addresses_from_db = []
    if address_params_candidates:
        for address_params_candidate in address_params_candidates:
            address = Address()
            address.address_id = address_params_candidate.address_id
            address.street_number = address_params_candidate.street_number
            address.street = address_params_candidate.street
            address.city = address_params_candidate.municipality
            address.state = address_params_candidate.governing_district
            address.zip_code = address_params_candidate.postal_area
            address.latitude = address_params_candidate.latitude
            address.longitude = address_params_candidate.longitude
            address.suite_numbers = address_params_candidate.suite
            address.source_date = address_params_candidate.max_source_date
            candidate_addresses_from_db.append(address)

    return candidate_addresses_from_db

def update_address(address):

    # look up address_match in the db, update if the date is newer for address
    statement = ''' UPDATE addresses SET street_number = ?, street = ?, municipality = ?, governing_district = ?,
                    postal_area = ?, latitude = ?, longitude = ?, country_id = ?, max_source_date = ?, suite = ?, shopping_center_name = ?
                    WHERE address_id = ?'''

    parameters = [address.street_number, address.street, address.city, address.state, address.zip_code, address.latitude,
                  address.longitude, address.country_id, address.source_date, address.suite_numbers, address.complex, address.address_id]

    sql_execute_with_parameters(parameters, statement)

    return address


def batch_insert_addresses(addresses, database_name):
    """
    Batch insert.  This is called from the custom analytics loader, so it's different from the ones above
    """

    # insert addresses in batches of 5000 so that we don't have too long of a statement
    list_of_addresses = split_up_list_into_smaller_partitions(addresses, 5000)

    for addresses in list_of_addresses:

        # create insert into temp table select statement
        temp_table_insert = [
            "select %s, %s, %s, %s, %s, 840, %s, %s, GETUTCDATE(), GETUTCDATE(), %s, %s, %s" % (
                insert_clean_up_string(address["street_number"]),
                insert_clean_up_string(address["street"]),
                insert_clean_up_string(address["city"]),
                insert_clean_up_string(address["state"]),
                insert_clean_up_string(address["zip"]),
                address["latitude"],
                address["longitude"],
                insert_clean_up_string(address["suite"]),
                insert_clean_up_string(address["shopping_center_name"]),
                insert_clean_up_string(address["unique_store_identifier"])
            )
            for address in addresses
        ]
        temp_table_insert = " UNION ALL ".join(temp_table_insert)

        statement = """
        -- create temp table
        create table #temp_addresses(street_number nvarchar(25) NULL, street nvarchar(255) NULL, municipality nvarchar(255) NULL,
        governing_district nvarchar(255) NULL, postal_area nvarchar(255) NULL, country_id int NULL,  latitude decimal(9, 6) NULL,
        longitude decimal(9, 6) NULL, created_at datetime NULL, updated_at datetime NULL, suite nvarchar(100) NULL,
        shopping_center_name nvarchar(255) NULL, unique_store_identifier nvarchar(255) NULL)

        -- insert into temp table
        insert into #temp_addresses (street_number, street, municipality, governing_district, postal_area, country_id, latitude, longitude, created_at, updated_at, suite, shopping_center_name, unique_store_identifier)
        %s

        -- insert into real table from temp table
        insert into addresses (street_number, street, municipality, governing_district, postal_area, country_id, latitude, longitude, created_at, updated_at, suite, shopping_center_name, unique_store_identifier)
        select street_number, street, municipality, governing_district, postal_area, country_id, latitude, longitude, created_at, updated_at, suite, shopping_center_name, unique_store_identifier
        from #temp_addresses

        -- drop temp table when done
        drop table #temp_addresses
        """ % temp_table_insert

        # go son
        sql_execute(statement, database_name = database_name)

