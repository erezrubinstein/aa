from common.utilities.inversion_of_control import HasAttributes, Dependency
from common.utilities.sql import sql_execute_on_db
from geoprocessing.data_access.data_access_utilities import escape_string, insert_clean_up, insert_clean_up_time

__author__ = 'erezrubinstein'


"""
This module represents various data access methods for dealing with the logging tables
"""



def insert_logging_records(logging_records):
    statement = "insert into log_entries"
    inserts = []
    for log in logging_records:

        if log.entity:
            entity_type = log.entity.entity_type
            entity_id = log.entity.entity_id
            # union several logging records

            inserts.append("\nSELECT %d, '%s', '%s', '%s', '%s', '%s', %s, '%s', %d, %d" % (log.log_entry_type_id, log.version, log.environment, log.process_id, insert_clean_up_time(log.time),
                                                                                            escape_string(log.message), insert_clean_up(log.elapsed_time), log.function_name, entity_type, entity_id))
        elif not log.entity:
            inserts.append("\nSELECT %d, '%s', '%s', '%s', '%s', '%s', %s, '%s', NULL, NULL" % (log.log_entry_type_id, log.version, log.environment, log.process_id, insert_clean_up_time(log.time),
                                                                                                escape_string(log.message), insert_clean_up(log.elapsed_time), log.function_name))

    full_statement = '\n'.join([statement, '\n union all'.join(inserts)])
    # get config for logging db credentials
    config = Dependency("Config", HasAttributes("logging_db_server", "logging_db_database",
        "logging_db_username", "logging_db_password")).value

    sql_execute_on_db(config.logging_db_server, config.logging_db_database, config.logging_db_username,
        config.logging_db_password, full_statement)


def select_logs_by_log_entry_type_ids(log_entry_type_ids):
    statement = '''
select top 100
	log_entry_type_id, process_id, time, message, function_name
from log_entries e
where e.log_entry_type_id in (%s)
order by time desc
    ''' % ','.join(str(id) for id in log_entry_type_ids)
    # get config for logging db credentials
    config = Dependency("Config", HasAttributes("logging_db_server", "logging_db_database",
        "logging_db_username", "logging_db_password")).value

    return sql_execute_on_db(config.logging_db_server, config.logging_db_database, config.logging_db_username,
        config.logging_db_password, statement)


def select_function_performance():
    statement = '''
select
	function_name,
	avg(elapsed_time) avg_secs,
	count(*) count
from log_entries
where elapsed_time is not null
group by function_name
order by avg(elapsed_time) desc
    '''

    # get config for logging db credentials
    config = Dependency("Config", HasAttributes("logging_db_server", "logging_db_database",
        "logging_db_username", "logging_db_password")).value

    return sql_execute_on_db(config.logging_db_server, config.logging_db_database, config.logging_db_username,
        config.logging_db_password, statement)

    ########################################################################################################
    ######################################### Internal Methods #############################################
    ########################################################################################################
