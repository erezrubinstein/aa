from common.utilities.misc_utilities import convert_entity_list_to_dictionary, split_up_list_into_smaller_partitions
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from geoprocessing.business_logic.business_objects.zip_code import ZipCode
from common.utilities.sql import sql_execute, sql_execute_with_parameters
from geoprocessing.data_access.data_access_utilities import comma_delimit_items, select_clean_up_string, escape_string, insert_clean_up_string

__author__ = 'erezrubinstein'


# This module represents various data access methods for dealing with store tables

def get_count_stores_by_company_id(company_id):
    statement = "SELECT COUNT(*) as count FROM stores WHERE company_id = ?"
    return sql_execute_with_parameters([company_id], statement)[0].count

def get_store_by_id(store_id):
    statement= """
                    SELECT store_id, company_id, address_id, phone_number, store_format, company_generated_store_number, note, opened_date, closed_date, assumed_opened_date, assumed_closed_date
                    FROM stores where store_id = ?
               """
    stores = sql_execute_with_parameters([store_id], statement)
    if len(stores) == 0:

        raise Exception("Store id %s does not exist in db: " % (store_id))

    else:
        store = stores[0]
        return Store.standard_init(store.store_id, store.company_id, store.address_id, store.phone_number, store.store_format, store.company_generated_store_number,
            store.note, store.opened_date, store.closed_date, store.assumed_opened_date, store.assumed_closed_date)

def select_address_id_by_core_store_id(core_store_id):

    # voila
    statement = "select address_id from stores where core_store_id = '%s'"% core_store_id
    rows = sql_execute(statement)

    if rows:
        return rows[0].address_id
    else:
        return None

def get_matched_open_store_from_db_by_core_store_id(core_store_id):

    statement = '''
        select
            s.store_id,
            s.company_id,
            s.address_id,
            s.phone_number,
            s.store_format,
            s.company_generated_store_number,
            s.note,
            s.opened_date,
            s.assumed_opened_date
        from stores s
        where core_store_id = '%s' and s.closed_date is null and s.assumed_closed_date is null''' % core_store_id

    db_store_params = sql_execute(statement)
    if len(db_store_params) > 0:
        db_store = Store()
        db_store.store_id = db_store_params[0].store_id
        db_store.company_id = db_store_params[0].company_id
        db_store.address_id = db_store_params[0].address_id
        db_store.phone_number = db_store_params[0].phone_number
        db_store._opened_date = db_store_params[0].opened_date
        db_store._assumed_opened_date = db_store_params[0].assumed_opened_date
        db_store.store_format = db_store_params[0].store_format
        db_store.company_generated_store_number = db_store_params[0].company_generated_store_number
        db_store.note = db_store_params[0].note
        return db_store
    else:
        return None

def get_matched_open_store_from_db(address_id, company_id, phone, store_format):

    statement = '''
        select
            s.store_id,
            s.company_id,
            s.address_id,
            s.phone_number,
            s.store_format,
            s.company_generated_store_number,
            s.note,
            s.opened_date,
            s.assumed_opened_date
        from stores s
        where s.address_id = %d and s.company_id = %d and s.phone_number %s and s.store_format %s
            and s.closed_date is null and s.assumed_closed_date is null''' % (address_id, company_id, select_clean_up_string(phone), select_clean_up_string(store_format))

    db_store_params = sql_execute(statement)

    if len(db_store_params) > 0:
        db_store = Store()
        db_store.store_id = db_store_params[0].store_id
        db_store.company_id = db_store_params[0].company_id
        db_store.address_id = db_store_params[0].address_id
        db_store.phone_number = db_store_params[0].phone_number
        db_store._opened_date = db_store_params[0].opened_date
        db_store._assumed_opened_date = db_store_params[0].assumed_opened_date
        db_store.store_format = db_store_params[0].store_format
        db_store.company_generated_store_number = db_store_params[0].company_generated_store_number
        db_store.note = db_store_params[0].note
        return db_store
    else:
        return None



def get_all_store_ids_with_company_ids():
    statement = '''SELECT store_id, company_id FROM stores'''
    return sql_execute(statement)

def get_all_store_ids_from_company_id(company_id):
    statement = '''SELECT store_id FROM stores WHERE company_id = %d order by store_id asc''' % company_id
    return sql_execute(statement)

def get_away_stores_within_lat_long_range(home_store, latitude_range, longitude_ranges):

    """
    ER - I'm splitting this query into two, because doing so reduced it from 100 seconds to 0 seconds on a large database
    """

    # create a query to get competitive compnies
    statement = """
        SELECT
            c.competitive_company_id,
            c.away_company_id,
            c.assumed_start_date as competitive_companies_start_date,
            c.assumed_end_date as competitive_companies_end_date
        FROM stores AS sh
        INNER JOIN competitive_companies AS c ON c.home_company_id = sh.company_id
        WHERE sh.store_id = ?
    """

    # get competitive companies
    competitive_companies = sql_execute_with_parameters([home_store.store_id], statement)

    # create dict to return
    away_stores = {}

    # only proceed to query stores/addresses if we have competitive stores
    if competitive_companies:

        # convert the competitive companies into 1) a company_id in clause and 2) a dictionary look up by company_id
        company_id_in_clause = ",".join([str(row.away_company_id) for row in competitive_companies])
        competitive_companies_dict = {
            row.away_company_id: {
                "competitive_company_id": row.competitive_company_id,
                "competitive_companies_start_date": row.competitive_companies_start_date,
                "competitive_companies_end_date": row.competitive_companies_end_date
            }
            for row in competitive_companies
        }

        # create long / lat statement
        lat_long_where_clause = _construct_latitude_longitude_where_statement(latitude_range, longitude_ranges)

        # do the second part of the query which gets away stores and their addresses
        away_companies_comm = """
            SELECT
                sa.company_id,
                sa.store_id ,
                a.longitude,
                a.latitude,
                sa.opened_date,
                sa.closed_date,
                sa.assumed_opened_date,
                sa.assumed_closed_date
            FROM stores sa
            INNER JOIN addresses AS a ON a.address_id = sa.address_id
            WHERE sa.company_id in (%s) AND sa.store_id != %s
                 %s
            ORDER BY sa.store_id asc
        """ % (company_id_in_clause, home_store.store_id, lat_long_where_clause)

        # run the second query
        stores = sql_execute(away_companies_comm)

        # make sure we get stores back
        if stores and len(stores) > 0:

            # cycle through results and create object
            for store in stores:

                # get the competitive_company details
                cc = competitive_companies_dict[store.company_id]

                away_store = StoreCompetitionInstance.standard_init(store.store_id, store.company_id, store.latitude, store.longitude,
                                                                    cc["competitive_company_id"], None, store.opened_date, store.closed_date,
                                                                    store.assumed_opened_date, store.assumed_closed_date,
                                                                    cc["competitive_companies_start_date"], cc["competitive_companies_end_date"])
                away_stores[away_store.away_store_id] = away_store

    return away_stores


def get_zips_within_lat_long_range(latitude_range, longitude_ranges):
    lat_long_where_clause = _construct_latitude_longitude_where_statement(latitude_range, longitude_ranges)
    sql = '''
        select * from (
        select zip_code, INTPTLAT as latitude, INTPTLONG as longitude
        from zip_codes ) as a
        where 1=1 %s
        ''' % (lat_long_where_clause)
    zip_codes = sql_execute(sql)
    zip_return = []
    for zip in zip_codes:
        zip_return.append(ZipCode.standard_init(zip.zip_code, GeographicalCoordinate(zip.longitude, zip.latitude)))
    return zip_return


def get_zip_by_zip_code(zip_code):
    sql = '''
        select zip_code, INTPTLONG as longitude, INTPTLAT as latitude
        from zip_codes
        where zip_code = '%s'
        ''' % (zip_code)
    zip = sql_execute(sql)[0]
    return ZipCode.standard_init(zip.zip_code, GeographicalCoordinate(zip.longitude, zip.latitude))

def save_zip_proximities(store_zip_proximities):
    sql_delete = 'delete from store_zip_proximities where store_id in (' +\
                 ','.join([str(szp['store_id']) for szp in store_zip_proximities]) + ');'
    sql_execute(sql_delete)

    sql_selects = []
    for szp in store_zip_proximities:
        sql_selects.append('''select %d, '%s', %d, %f''' % (szp['store_id'], szp['zip_code'], szp['threshold_id'], szp['proximity']))
    sql_insert = ''.join(['insert into store_zip_proximities (store_id, zip_code, threshold_id, proximity)\n',' union all\n'.join(sql_selects),';'])

    return sql_execute(sql_insert)

def get_open_store_ids_and_open_dates_for_company(company_info):
    statement = '''
                    SELECT
                        store_id,
                        opened_date,
                        assumed_opened_date
                    FROM stores
                    WHERE company_id = ? AND closed_date is null AND assumed_closed_date is null AND assumed_opened_date < ?'''
    row = sql_execute_with_parameters([company_info.company_id, company_info.as_of_date], statement)
    stores = []
    for store_triple in row:
        store = Store()
        store.store_id = store_triple.store_id
        store._opened_date = store_triple.opened_date
        store._assumed_opened_date = store_triple.assumed_opened_date
        stores.append(store)
    return stores

def insert_store_return_with_new_store_id(store):

    # workaround to weird problem I can't reproduce
    address_id = store.address_id
    if address_id and isinstance(address_id, list):
        address_id = address_id[0][0]
        store.address_id = address_id


    # insert
    statement = '''
        insert into stores (company_id, address_id, phone_number, store_format, company_generated_store_number, note, opened_date, assumed_opened_date, created_at, updated_at, core_store_id)
        values(?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE(), ?)'''
    parameters = [store.company_id, address_id, store.phone_number, store.store_format, store.company_generated_store_number, store.note, store._opened_date,
                  store._assumed_opened_date, store.core_store_id]
    sql_execute_with_parameters(parameters, statement)

    # select
    statement = '''
SELECT store_id
FROM stores
WHERE address_id = ? AND company_id = ? and phone_number %s and store_format %s and core_store_id %s
    ''' % (select_clean_up_string(store.phone_number), select_clean_up_string(store.store_format), select_clean_up_string(store.core_store_id))
    parameters = [address_id, store.company_id]
    row = sql_execute_with_parameters(parameters, statement)[0]

    # set id, return store
    store.store_id = row.store_id
    return store

def update_store(store):
    """
    This methods updates a store.  As of now, store_format and note are the only fields that we allow to update.
    """
    sql = '''
UPDATE stores
SET store_format = ?, note = ?
WHERE store_id = ?
'''
    parameters = [store.store_format, store.note, store.store_id]
    sql_execute_with_parameters(parameters, sql)


def close_old_stores(store_ids, assumed_closed_date):
    if store_ids:
        in_statement = comma_delimit_items(store_ids)
        statement = "UPDATE stores SET assumed_closed_date = ? WHERE store_id IN (%s)" % in_statement
        sql_execute_with_parameters([assumed_closed_date], statement)



def batch_insert_stores__auto_get_addresses(stores, database_name):
    """
    Batch insert.  This is called from the custom analytics loader, so it's different from the ones above
    """

    # part one is to create a dictionary of core store id to sql address id
    addresses = sql_execute("select address_id, unique_store_identifier from addresses", database_name = database_name)
    addresses = convert_entity_list_to_dictionary(addresses, key = lambda a: a.unique_store_identifier)

    # insert stores in batches of 5000 so that we don't have too long of a statement
    list_of_stores = split_up_list_into_smaller_partitions(stores, 5000)

    for stores in list_of_stores:

        # create insert into temp table select statement
        temp_table_insert = [
            "select %s, %s, %s, %s, %s, %s, %s, %s, GETUTCDATE(), GETUTCDATE()" % (
                str(store["company_id"]),
                str(addresses[str(store["trade_area_id"])].address_id),
                insert_clean_up_string(store["phone_number"]),
                insert_clean_up_string(store["core_store_id"]),
                insert_clean_up_string(store["opened_date"]),
                insert_clean_up_string(store["closed_date"]),
                insert_clean_up_string(store["opened_date"]),
                insert_clean_up_string(store["closed_date"])
            )
            for store in stores
        ]
        temp_table_insert = " UNION ALL ".join(temp_table_insert)

        # create insert statement
        statement = """
        -- create temp table
        create table #temp_stores(company_id int NULL, address_id int NOT NULL, phone_number nvarchar(255) NULL, core_store_id nvarchar(50) NULL,
        opened_date datetime NULL, closed_date datetime NULL, assumed_opened_date datetime NULL, assumed_closed_date datetime NULL, created_at datetime NULL,
        updated_at datetime NULL)

        -- insert into temp table
        insert into #temp_stores (company_id, address_id, phone_number, core_store_id, opened_date, closed_date, assumed_opened_date, assumed_closed_date, created_at, updated_at)
        %s

        -- insert into real table from temp table
        insert into stores (company_id, address_id, phone_number, core_store_id, opened_date, closed_date, assumed_opened_date, assumed_closed_date, created_at, updated_at)
        select company_id, address_id, phone_number, core_store_id, opened_date, closed_date, assumed_opened_date, assumed_closed_date, created_at, updated_at
        from #temp_stores

        -- drop temp table when done
        drop table #temp_stores""" % temp_table_insert

        # bomboj for
        sql_execute(statement, database_name = database_name)


def get_store_points_by_store_ids(store_ids):

    # create the temp table insert statement
    temp_table_insert = ["insert into #temp_store_ids (store_id) VALUES(%s)" % str(store_id) for store_id in store_ids]
    temp_table_insert = "\n".join(temp_table_insert)

    # create the statement
    # use temp table to select from (instead of in clause) because there could be a lot of stores here.
    statements = [
        # create temp table
        "create table #temp_store_ids (store_id int)",

        # insert into temp table
        "%s" % temp_table_insert,

        # select from stores/addresses
        """
        select s.store_id, a.latitude, a.longitude
        from stores s
        inner join addresses a on a.address_id = s.address_id
        where s.store_id in (select store_id from #temp_store_ids)
        """,

        # drop the table
        "drop table #temp_store_ids"
    ]

    # bomboj for
    return sql_execute(*statements)


def get_all_store_points():

    # here's the sql
    statement = """
    select s.store_id, a.latitude, a.longitude
    from stores s
    inner join addresses a on a.address_id = s.address_id
    """

    # bomboj for
    return sql_execute(statement)


########################################################################################################
########################################## Private Methods #############################################
########################################################################################################


def _construct_latitude_longitude_where_statement(latitude_range, longitude_ranges):
    where_clause = ' '

    if latitude_range is not None:
        where_clause = where_clause.join(['', 'AND (a.latitude between %f AND %f) ' %
                                              (latitude_range.start, latitude_range.stop)])

    if longitude_ranges is not None:
        if len(longitude_ranges) == 1:
            where_clause = where_clause.join(['', 'AND (a.longitude between %f AND %f)' %
                                                  (longitude_ranges[0].start, longitude_ranges[0].stop)])
        elif len(longitude_ranges) == 2:
            where_clause = where_clause.join(['', '''
                                                        AND
                                                        (
                                                            a.longitude between %f AND %f
                                                            OR a.longitude between %f AND %f
                                                        )
                                                        ''' % (longitude_ranges[0].start, longitude_ranges[0].stop,
                                                               longitude_ranges[1].start, longitude_ranges[1].stop)])

    return where_clause