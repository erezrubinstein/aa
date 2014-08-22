from common.utilities.sql import sql_execute

__author__ = 'erezrubinstein'

def get_all_cbsas(all_fields = False):

    # only query these by default
    fields = "cbsa_id, name, points_json, max_degrees"

    # if we want more, query all
    if all_fields:
        fields = "*"

    statement = "select %s from cbsa" % fields
    return sql_execute(statement)


def get_all_counties(all_fields = False):

    # only query these by default
    fields = "county_id, name, points_json, max_degrees"

    # if we want more, query all
    if all_fields:
        fields = "*"

    statement = "select %s from counties" % fields
    return sql_execute(statement)


def delete_cbsa_store_matches(cbsa_id):

    # create the statement
    statement = "delete from cbsa_store_matches where cbsa_id = %s" % str(cbsa_id)

    # go for the gold!
    sql_execute(statement)


def delete_county_store_matches(county_id):

    # create the statement
    statement = "delete from county_store_matches where county_id = %s" % str(county_id)

    # go for the gold!
    sql_execute(statement)


def insert_cbsa_store_matches(cbsa_id, store_ids):

     # create the temp table insert statement
    temp_table_insert = [
        "SELECT %s, %s" % (str(store_id), str(cbsa_id))
        for store_id in store_ids
    ]
    temp_table_insert = " UNION ALL\n".join(temp_table_insert)

    # create the statement
    # use temp table to select from (instead of in clause) because there could be a lot of stores here.
    statement = """
        -- create temp table
        create table #temp_insert (store_id int, cbsa_id int)

        -- insert into temp table
        insert into #temp_insert (store_id, cbsa_id)
        %s

        -- select from stores/addresses
        insert into cbsa_store_matches (store_id, cbsa_id)
        select store_id, cbsa_id from #temp_insert

        -- drop the table
        drop table #temp_insert
    """ % temp_table_insert

    # go for the gold!
    sql_execute(statement)


def insert_county_store_matches(county_id, store_ids):

     # create the temp table insert statement
    temp_table_insert = [
        "SELECT %s, %s" % (str(store_id), str(county_id))
        for store_id in store_ids
    ]
    temp_table_insert = " UNION ALL\n".join(temp_table_insert)

    # create the statement
    # use temp table to select from (instead of in clause) because there could be a lot of stores here.
    statement = """
        -- create temp table
        create table #temp_insert (store_id int, county_id int)

        -- insert into temp table
        insert into #temp_insert (store_id, county_id)
        %s

        -- select from stores/addresses
        insert into county_store_matches (store_id, county_id)
        select store_id, county_id from #temp_insert

        -- drop the table
        drop table #temp_insert
    """ % temp_table_insert

    # go for the gold!
    sql_execute(statement)