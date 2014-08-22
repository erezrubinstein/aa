from geoprocessing.business_logic.business_objects.monopoly import Monopoly
from common.utilities.sql import  sql_execute_with_parameters

__author__ = 'erezrubinstein'



"""
This module represents various data access methods for dealing with the monopoly tables
"""

def select_active_monopoly_record(store_id, trade_area_id):
    # set up sql and parameters
    statement = """
    SELECT store_id, monopoly_type_id, trade_area_id, start_date, end_date
    FROM monopolies
    WHERE store_id = ? AND trade_area_id = ? and end_date is null"""
    parameters = [store_id, trade_area_id]

    # execute
    rows = sql_execute_with_parameters(parameters, statement)

    if rows and len(rows) > 1:
        raise Exception("data error.  a store/trade_area should only have one monopoly.")
    elif rows and len(rows) == 1:
        # return a monopoly object
        return Monopoly(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4])
    else:
        return

def select_active_monopoly_record_postgis(store_id, trade_area_id):

    # set up sql and parameters
    statement = """
    SELECT store_id, monopoly_type_id, trade_area_id, start_date, end_date
    FROM monopolies_postgis
    WHERE store_id = ? AND trade_area_id = ? and end_date is null"""
    parameters = [store_id, trade_area_id]

    # execute
    rows = sql_execute_with_parameters(parameters, statement)

    if rows and len(rows) > 1:
        raise Exception("data error.  a store/trade_area should only have one monopoly.")
    elif rows and len(rows) == 1:
        # return a monopoly object
        return Monopoly(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4])
    else:
        return

    pass






def insert_monopoly(store_id, monopoly_type_id, trade_area_id, start_date, end_date = None):
    insert = '''
                INSERT INTO monopolies (store_id, created_at, updated_at, monopoly_type_id, trade_area_id, start_date, end_date)
                VALUES (?, GETUTCDATE(), GETUTCDATE(), ?, ?, ?, ?)'''
    parameters = [store_id, monopoly_type_id, trade_area_id, start_date, end_date]

    sql_execute_with_parameters(parameters, insert)

def insert_monopoly_postgis(store_id, monopoly_type_id, trade_area_id, start_date, end_date = None):
    insert = '''
                INSERT INTO monopolies_postgis (store_id, created_at, updated_at, monopoly_type_id, trade_area_id, start_date, end_date)
                VALUES (?, GETUTCDATE(), GETUTCDATE(), ?, ?, ?, ?)'''
    parameters = [store_id, monopoly_type_id, trade_area_id, start_date, end_date]

    sql_execute_with_parameters(parameters, insert)







def close_monopoly_record(store_id, trade_area_id, end_date):
    # set up sql and parameters
    statement = """
    UPDATE monopolies
    SET end_date = ?
    WHERE store_id = ? AND trade_area_id = ? AND end_date is NULL"""
    parameters = [end_date, store_id, trade_area_id]

    # execute
    sql_execute_with_parameters(parameters, statement)

def close_monopoly_record_postgis(store_id, trade_area_id, end_date):
    # set up sql and parameters
    statement = """
    UPDATE monopolies_postgis
    SET end_date = ?
    WHERE store_id = ? AND trade_area_id = ? AND end_date is NULL"""
    parameters = [end_date, store_id, trade_area_id]

    # execute
    sql_execute_with_parameters(parameters, statement)



def delete_from_monopolies(store_id, trade_area_id):
    # set up statement and parameters
    statement = "DELETE FROM monopolies WHERE store_id = ? and trade_area_id = ?"
    parameters = [store_id, trade_area_id]

    # execute
    sql_execute_with_parameters(parameters, statement)

def delete_from_monopolies_postgis(store_id, trade_area_id):
    # set up statement and parameters
    statement = "DELETE FROM monopolies_postgis WHERE store_id = ? and trade_area_id = ?"
    parameters = [store_id, trade_area_id]

    # execute
    sql_execute_with_parameters(parameters, statement)