from time import strptime
from dateutil import parser
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from common.utilities.sql import sql_execute, sql_execute_with_parameters
from geoprocessing.data_access.data_access_utilities import insert_clean_up_string, select_clean_up_string, insert_clean_up

__author__ = 'erezrubinstein'



"""
This module represents various data access methods for dealing with the competitive store tables
"""

def get_competitive_stores(home_store_id, trade_area_id):
    """
    This selects competitive_store ids (include historical)
    """
    statement = '''
SELECT
	cs.away_store_id,
	s.company_id,
	cs.start_date,
	cs.end_date
FROM competitive_stores cs
INNER JOIN stores s on s.store_id = cs.away_store_id
WHERE cs.home_store_id = ? AND cs.trade_area_id = ?'''
    parameters = [home_store_id, trade_area_id]

    competitive_stores = sql_execute_with_parameters(parameters, statement)
    away_stores = []
    if competitive_stores and len(competitive_stores) > 0:
        #return a list of store instance competitions
        for store in competitive_stores:
            # convert dates to datetimes
            start_date = None
            end_date = None
            if store.start_date:
                start_date = parser.parse(store.start_date)
            if store.end_date:
                end_date = parser.parse(store.end_date)

            away_stores.append(StoreCompetitionInstance.standard_init(
                store.away_store_id, store.company_id, None, None, None, None, start_date, end_date, start_date, end_date, None, None))

    return away_stores

def get_competitive_stores_postgis(home_store_id, trade_area_id):
    """
    This selects competitive_store ids (include historical)
    """

    statement = '''
                    SELECT
                        cs.away_store_id,
                        s.company_id,
                        cs.start_date,
                        cs.end_date
                    FROM competitive_stores_postgis cs
                    INNER JOIN stores s on s.store_id = cs.away_store_id
                    WHERE cs.home_store_id = ? AND cs.trade_area_id = ?
                '''

    parameters = [home_store_id, trade_area_id]

    competitive_stores = sql_execute_with_parameters(parameters, statement)
    away_stores = []
    if competitive_stores and len(competitive_stores) > 0:
        #return a list of store instance competitions
        for store in competitive_stores:
            # convert dates to datetimes
            start_date = None
            end_date = None
            if store.start_date:
                start_date = parser.parse(store.start_date)
            if store.end_date:
                end_date = parser.parse(store.end_date)

            away_stores.append(StoreCompetitionInstance.standard_init(store.away_store_id, store.company_id, None, None, None, None,
                start_date, end_date, start_date, end_date, None, None))

    return away_stores


def close_competitive_stores_by_id(home_store_id, away_store_id, trade_area_id, end_date):
    # set up sql and parameters
    statement = """
    UPDATE competitive_stores
    SET end_date = ?
    WHERE home_store_id = ? AND trade_area_id = ?
        AND away_store_id = ?"""
    parameters = [end_date, home_store_id, trade_area_id, away_store_id]

    # execute
    sql_execute_with_parameters(parameters, statement)

def close_competitive_stores_by_id_postgis(home_store_id, away_store_id, trade_area_id, end_date):
    # set up sql and parameters
    statement = """
                    UPDATE competitive_stores_postgis
                    SET end_date = ?
                    WHERE home_store_id = ? AND trade_area_id = ? AND away_store_id = ?
                """

    parameters = [end_date, home_store_id, trade_area_id, away_store_id]

    # execute
    sql_execute_with_parameters(parameters, statement)


def batch_upsert_competitive_stores(trade_area_id, competitive_stores):

    # first, delete all competition associated with this trade area
    statement = "delete from competitive_stores where trade_area_id = ?"
    sql_execute_with_parameters([trade_area_id], statement)

    # ---- now, create a batch insert statement: ----

    # array for keep track of individual statements
    sql_statements = []

    # create temp table to insert into.  This speeds up the insert tremendously because the SQL table insert will be done in batch with one transaction
    sql_statements.append('''
DECLARE @temp_competitive_stores table (competitive_company_id int, home_store_id int, away_store_id int, travel_time float, created_at datetime, updated_at datetime,
trade_area_id int, start_date datetime, end_date datetime)''')

    # create sql
    for away_store in competitive_stores:

        # create statement.  This is compacted into one line on purpose.  It seems to finish much faster on large data sets
        sql_statements.append('''insert into @temp_competitive_stores (competitive_company_id, home_store_id, away_store_id, travel_time, created_at, updated_at, trade_area_id, start_date, end_date)
VALUES (%d, %d, %d, %s, GETUTCDATE(), GETUTCDATE(), %d, %s, %s)''' % (
            away_store["competitive_company_id"],
            away_store["home_store_id"],
            away_store["away_store_id"],
            insert_clean_up_string(away_store["travel_time"]),
            trade_area_id,
            insert_clean_up_string(away_store["start_date"]),
            insert_clean_up_string(away_store["end_date"])))

    # add insert into real table statements (from temp table)
    sql_statements.append('''
insert into competitive_stores (competitive_company_id, home_store_id, away_store_id, travel_time, created_at, updated_at, trade_area_id, start_date, end_date)
select competitive_company_id, home_store_id, away_store_id, travel_time, created_at, updated_at, trade_area_id, start_date, end_date
from @temp_competitive_stores''')

    # join statements and execute
    big_statement = '; '.join(sql_statements)
    sql_execute(big_statement)


def get_competitive_store_by_id(competitive_store_id):
    statement = '''
    SELECT competitive_store_id, competitive_company_id, home_store_id, away_store_id, travel_time, created_at, updated_at,
    trade_area_id, start_date, end_date
    FROM competitive_stores
    WHERE competitive_store_id = ?
    '''
    parameters = [competitive_store_id]
    row = sql_execute_with_parameters(parameters, statement)[0]
    if row is not None:
        competitive_store = StoreCompetitionInstance()
        competitive_store.competitive_store_id = row.competitive_store_id
        competitive_store.competitive_company_id = row.competitive_company_id
        competitive_store.home_store_id = row.home_store_id
        competitive_store.away_store_id = row.away_store_id
        competitive_store.travel_time = row.travel_time
        competitive_store.created_at = row.created_at
        competitive_store.updated_at = row.updated_at
        competitive_store.trade_area_id = row.trade_area_id
        return competitive_store



## !!!!!! **************************************************************************************************************
# THIS IS A VERY DANGEROUS METHOD.  IT SHOULD REALLY NEVER BE USED.
# Instead, you should call the synchronize competitors method, which marks old competitors with an end date
## !!!!!! **************************************************************************************************************
def delete_from_competitive_stores(home_store_id, away_store_id):
    comm_comp_delete = '''
    DELETE FROM competitive_stores WHERE home_store_id = ? AND away_store_id = ?
    '''
    parameters = [home_store_id, away_store_id]
    sql_execute_with_parameters(parameters, comm_comp_delete)

def delete_from_competitive_stores_postgis(home_store_id, away_store_id):
    comm_comp_delete = '''
    DELETE FROM competitive_stores_postgis WHERE home_store_id = ? AND away_store_id = ?
    '''
    parameters = [home_store_id, away_store_id]
    sql_execute_with_parameters(parameters, comm_comp_delete)