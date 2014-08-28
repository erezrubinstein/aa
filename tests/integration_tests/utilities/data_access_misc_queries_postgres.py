from weather.helpers.pgsql_helper import PGSqlHelper
import datetime

__author__ = 'erezrubinstein'


# ------------------ Insert Methods ------------------ #

def insert_test_weather_station(code = "weather_station", latitude = 40, longitude = -80, station_name = "station_name"):

    sql = """
insert into weatherstation (code, longitude, latitude, geom, name, country, elev, gsnflag, hcnflag, datasource_id, inserted, state)
VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, 'US', 10.0, false, false, 1, %s, 'NY')
RETURNING weatherstation_id;
"""
    results = PGSqlHelper().execute(sql, [code, longitude, latitude, longitude, latitude, station_name, datetime.datetime.utcnow()])

    return results[0][0]


def insert_test_weather_var(var_name, data_source_id=1):

    sql = """
insert into weathervar (datasource_id, varname, standard_name, physical_name, units)
VALUES (%s, %s, %s, %s, %s)
RETURNING weathervar_id;
"""
    results = PGSqlHelper().execute(sql, [data_source_id, var_name, var_name, var_name, "woot"])

    return results[0][0]


def insert_test_source_file(filename, datasource_id=1):

    sql = """
insert into sourcefile (datasource_id, filename, created)
VALUES (%s, %s, %s)
RETURNING sourcefile_id;
"""
    results = PGSqlHelper().execute(sql, [datasource_id, filename, datetime.datetime.utcnow()])

    return results[0][0]


def insert_test_point_data(weather_var_id, weather_station_id, utc_time, value, source_file_id):

    sql = """
insert into pointdata (weathervar_id, weatherstation_id, utc_time, value, sourcefile_id, updated)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING pointdata_id;
"""
    results = PGSqlHelper().execute(sql, [weather_var_id, weather_station_id, utc_time, value, source_file_id, datetime.datetime.utcnow()])

    return results[0][0]


# ------------------ Delete Methods ------------------ #

def purge_weather_tables():

    # delete data from all the tables associated with weather
    # don't truncate, because there are foreign keys here
    sql = """
delete from pointdata;
delete from weatherstation;
delete from weathervar;
delete from sourcefile;
"""

    # run sql
    PGSqlHelper().execute(sql)

