"""
This module represents various data access methods for report generation
"""
from common.utilities.inversion_of_control import Dependency
from common.utilities.sql import sql_execute_on_db, sql_execute


def select_row_counts_from_tables(tables):
    config = Dependency("Config").value

    statement = '''
        SELECT OBJECT_NAME(OBJECT_ID) table_name, st.row_count
        FROM sys.dm_db_partition_stats st
        WHERE index_id < 2 and OBJECT_NAME(OBJECT_ID) in ('%s')
        order by OBJECT_NAME(OBJECT_ID)
        ''' % "','".join(tables)
    return sql_execute_on_db(config.db_server, config.db_database, config.build_db_data_checks_username,
        config.build_db_data_checks_password, statement)

