import Queue
from common.utilities.inversion_of_control import HasAttributes, Dependency
from common.utilities.sql import sql_execute, sql_execute_on_db
import threading

__author__ = 'jsternberg'

"""
This module represents various data access methods for ingesting census datasets
"""

def get_census_data_row_count(census_ingest_provider):
    """
    Get the count of rows in the db for the table that the census provider works with
    Used for verifying data inserted correctly after saving
    """
    sql = '''
    select count(*) as cnt from %s;
    ''' % census_ingest_provider.table_name
    rows = sql_execute(sql)
    return rows[0][0]

def insert_census_data(census_ingest_provider, rows_per_batch, max_threads):
    """
    Save data to the db in batches, in case the data is large
    Note this is deprecated by bulk insert, which is much much faster for large files
    """
    if max_threads > 0:
        __insert_census_data_threaded(census_ingest_provider, rows_per_batch, max_threads)
    else:
        __insert_census_data_single_thread(census_ingest_provider, rows_per_batch)


def __insert_census_data_threaded(census_ingest_provider, rows_per_batch, max_threads):
    """
    Save data to the db in batches, with a separate thread per batch, in case the data is large
    Using a queue pattern, launching as many worker threads as max_threads
    """
    __truncate_table(census_ingest_provider.table_name)
    total_rows = len(census_ingest_provider.census_ingest_data)
    start_row = 0

    # get a queue going
    queue = Queue.Queue()

    # fire up worker threads, each listening to the queue
    for i in range(max_threads):
        t = CensusBatchInserter(queue)
        t.setDaemon(True)
        t.start()

    # add data to the queue
    while start_row < total_rows:
        end_row = start_row + rows_per_batch + 1
        # copy out the data
        batch_data = list(census_ingest_provider.census_ingest_data[start_row:end_row])
        # add it to the queue, along with other params needed for data inserts
        work_item = (census_ingest_provider.table_name, census_ingest_provider.column_list, batch_data)
        queue.put(work_item)
        start_row += rows_per_batch + 1

    # wait on the queue for everything to be processed
    queue.join()


def __insert_census_data_single_thread(census_ingest_provider, rows_per_batch):
    """
    Save data to the db in batches, in case the data is large
    Does not use threads
    """
    __truncate_table(census_ingest_provider.table_name)
    total_rows = len(census_ingest_provider.census_ingest_data)
    r = 0
    while r < total_rows:
        sql = '''
        insert into %s (%s)
        %s
        ''' % (census_ingest_provider.table_name,
               ','.join(census_ingest_provider.column_list),
               __get_sql_select_union(census_ingest_provider.census_ingest_data,
                   census_ingest_provider.column_list, r, rows_per_batch))
        sql_execute(sql)
        r += rows_per_batch + 1


def __truncate_table(table_name):
    config = Dependency('Config', HasAttributes("db_server", "db_database", "build_db_bulk_operations_username", "build_db_bulk_operations_password")).value
    db_server = config.db_server
    db_database = config.db_database
    bulk_db_username = config.build_db_bulk_operations_username
    bulk_db_password = config.build_db_bulk_operations_password
    sql = 'truncate table %s;' % table_name
    sql_execute_on_db(db_server, db_database, bulk_db_username, bulk_db_password, sql)


def __get_sql_select_union(census_ingest_data, column_list, start_row, number_of_rows):
    """
    Get a sql formatted string that selects the data values
    Suitable for an insert statement
    """
    sql_list = []
    end_row = start_row + number_of_rows + 1
    for row in census_ingest_data[start_row:end_row]:
        sql_list.append('select ' + ', '.join(["'%s' as %s" % (z[1], z[0]) for z in zip(column_list, row)]))
    return ' union all \n'.join(sql_list)


############################################### Thread Class ###############################################

class CensusBatchInserter(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # get a work unit tuple from the queue
            work = self.queue.get()
            table_name = work[0]
            column_list = work[1]
            batch_data = work[2]

            sql = '''insert into %s (%s)
            %s''' % (table_name, ','.join(column_list), self.__get_sql_select_union(batch_data, column_list))
            sql_execute(sql)

            #mark this one done
            self.queue.task_done()

    def __get_sql_select_union(self, batch_data, column_list):
        """
        Get a sql formatted string that selects the data values
        Suitable for an insert statement
        """
        sql_list = []
        for row in batch_data:
            sql_list.append('select ' + ', '.join(["'%s' as %s" % (z[1], z[0]) for z in zip(column_list, row)]))
        return ' union all \n'.join(sql_list)

############################################### Bulk Insert ###############################################

def bulk_insert_census_data(census_ingest_provider, db_server, db_database, db_user_name, db_password):
    """
    Save data to the db using a bulk insert function.
    This is db vendor-specific!
    Current implementation is for MS SQL Server
    """
    # script out the foreign key create & drop statements so we can truncate
    FKs = __get_FKs(census_ingest_provider.table_name)

    # drop the keys
    __drop_FKs(FKs)
    __truncate_table(census_ingest_provider.table_name)

    # need to skip first row because of headers, sometimes
    if census_ingest_provider.skip_first_row:
        first_row = 2
    else:
        first_row = 1

    # do the bulk load here
    sql = '''bulk insert %s
        from '%s'
        with (formatfile='%s', firstrow = %d);
        ''' % (census_ingest_provider.table_name,
               census_ingest_provider.db_file_path,
               census_ingest_provider.db_format_file_path,
               first_row)
    sql_execute_on_db(db_server, db_database, db_user_name, db_password, sql)

    #trim double quotes for columns that need it
    if census_ingest_provider.trim_double_quotes_from_columns:
        for trim_column in census_ingest_provider.trim_double_quotes_from_columns:
            sql = '''update %s
                    set %s = replace(%s, '"','');
                    ''' % (census_ingest_provider.table_name, trim_column, trim_column)
            sql_execute_on_db(db_server, db_database, db_user_name, db_password, sql)

    # add back foreign keys
    __create_FKs(FKs)

def __get_FKs(table_name):
    """
    Scripts out sql for creating and dropping foreign key scripts that reference the given table
    Note this is specific to MS SQL Server
    """
    config = Dependency('Config', HasAttributes("db_server", "db_database", "build_db_bulk_operations_username", "build_db_bulk_operations_password")).value
    db_server = config.db_server
    db_database = config.db_database
    bulk_db_username = config.build_db_bulk_operations_username
    bulk_db_password = config.build_db_bulk_operations_password
    sql = '''with fks as(
            select fk.name as constraint_name
                , OBJECT_NAME(fk.parent_object_id) as parent_table_name
                , c1.name as parent_column_name
                , OBJECT_NAME(fk.referenced_object_id) as referenced_table_name
                , c2.name as referenced_column_name
            from sys.foreign_keys fk
            inner join sys.foreign_key_columns fkc on fkc.constraint_object_id = fk.object_id
            inner join sys.columns c1 on c1.object_id = fkc.parent_object_id and c1.column_id = fkc.parent_column_id
            inner join sys.types t1 on t1.system_type_id = c1.system_type_id
            inner join sys.columns c2 on c2.object_id = fkc.referenced_object_id and c2.column_id = fkc.referenced_column_id
            inner join sys.types t2 on t2.system_type_id = c2.system_type_id
            where fk.referenced_object_id=object_id('%s')
        )
        select 'alter table [' + parent_table_name + '] add constraint [' + constraint_name
                + '] foreign key ([' + parent_column_name + '])'
                + ' references [' + referenced_table_name + '] ([' + referenced_column_name + ']);' as create_script
                , 'alter table [' + parent_table_name + '] drop constraint [' + constraint_name + '];' as drop_script
        from fks;''' % (table_name)
    return sql_execute_on_db(db_server, db_database, bulk_db_username, bulk_db_password, sql)

def __drop_FKs(FKs):
    """
    Drops the FKs in the given list
    """
    if FKs:
        config = Dependency('Config', HasAttributes("db_server", "db_database", "build_db_bulk_operations_username", "build_db_bulk_operations_password")).value
        db_server = config.db_server
        db_database = config.db_database
        bulk_db_username = config.build_db_bulk_operations_username
        bulk_db_password = config.build_db_bulk_operations_password
        for FK in FKs:
            sql_execute_on_db(db_server, db_database, bulk_db_username, bulk_db_password, FK.drop_script)

def __create_FKs(FKs):
    """
    Add back the FKs in the given list
    """
    if FKs:
        config = Dependency('Config', HasAttributes("db_server", "db_database", "build_db_bulk_operations_username", "build_db_bulk_operations_password")).value
        db_server = config.db_server
        db_database = config.db_database
        bulk_db_username = config.build_db_bulk_operations_username
        bulk_db_password = config.build_db_bulk_operations_password
        for FK in FKs:
            sql_execute_on_db(db_server, db_database, bulk_db_username, bulk_db_password, FK.create_script)
