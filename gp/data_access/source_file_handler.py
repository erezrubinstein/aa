from common.utilities.Logging.runtime_profiler import RunTimeProfiler
from common.utilities.misc_utilities import split_up_list_into_smaller_partitions
from common.utilities.sql import sql_execute_with_parameters, sql_execute
from geoprocessing.data_access.data_access_utilities import escape_string_clean_up
from geoprocessing.business_logic.business_objects.source_file import SourceFile
from geoprocessing.business_logic.business_objects.source_file_record import SourceFileRecord

__author__ = 'spacecowboy et al.'

def delete_loader_records_for_current_file(company_info):
    statement = '''delete from source_file_records where source_file_id = %d''' % company_info.source_file_id
    sql_execute(statement)


def save_loader_records_and_parsed_addresses(company_info):

    # in order to avoid errors with data that's too large (RET 1119), we're breaking these down into groups of 10,000 parsed records
    partition_size = 10000
    list_of_parsed_records = split_up_list_into_smaller_partitions(company_info.parsed_records, partition_size)

    # row counter for "the row in the excel spread sheet"
    excel_row_counter = company_info.addreses_start_row

    # the counter for the row
    row_index_counter = 0

    for parsed_records in list_of_parsed_records:

        __batch_insert_source_file_records(parsed_records, company_info, excel_row_counter, row_index_counter)

        # add to "current row" counter
        excel_row_counter += partition_size
        row_index_counter += partition_size


def insert_source_file(file_path, file_created_date, file_size_in_bytes):
    statement = '''
        IF NOT EXISTS
        (
            SELECT source_file_id
            FROM source_files
            WHERE full_path = ?
        )
        BEGIN
            INSERT INTO source_files (full_path, file_created_date, file_modified_date, file_size_in_bytes, created_at, updated_at)
            VALUES (?, ?, ?, ?, GETUTCDATE(), GETUTCDATE())
        END
        ELSE
        BEGIN
            UPDATE source_files
            SET file_modified_date = ?, file_size_in_bytes = ?, updated_at = GETUTCDATE()
            WHERE full_path = ?
        END'''

    # create parameters and execute sql
    parameters = [file_path, file_path, file_created_date, file_created_date, file_size_in_bytes, file_created_date, file_size_in_bytes, file_path]
    sql_execute_with_parameters(parameters, statement)

    # select and return the source_file_id
    statement = '''SELECT source_file_id FROM source_files WHERE full_path = ?'''
    row = sql_execute_with_parameters([file_path], statement)[0]
    return row.source_file_id


def select_source_file_by_source_file_id(source_file_id):
    statement = '''
        select source_file_id, full_path, file_created_date, file_modified_date, file_size_in_bytes
        from source_files
        where source_file_id = ?;
        '''
    parameters = [source_file_id]
    row = sql_execute_with_parameters(parameters, statement)[0]
    return SourceFile.standard_init(row.source_file_id, row.full_path, row.file_created_date, row.file_modified_date, row.file_size_in_bytes)

def select_source_file_record_by_source_file_record_id(source_file_record_id):
    statement = '''
        select source_file_record_id, source_file_id, row_number, record, loader_record_id,
            street_number, street, city, state, zip, phone, country_id, latitude, longitude, suite, note,
            company_generated_store_number, store_format, opened_date, source_date, shopping_center_name
        from source_file_records
        where source_file_record_id = ?;
        '''
    parameters = [source_file_record_id]
    row = sql_execute_with_parameters(parameters, statement)[0]
    return SourceFileRecord.standard_init(row.source_file_record_id, row.source_file_id, row.row_number, row.record, row.loader_record_id,
        row.street_number, row.street, row.city, row.state, row.zip, row.phone, row.country_id, row.latitude, row.longitude, row.suite, row.note,
        row.company_generated_store_number, row.store_format, row.opened_date, row.source_date, row.shopping_center_name)



# --------------------------------- Private Methods ---------------------------------


def __batch_insert_source_file_records(parsed_records, company_info, excel_row_counter, row_index_counter):
    """
    This is done in smaller batches as to avoid running out of memory or sending statements that are "too large".
    Related to RET-1119
    """

    # array for keep track of individual statements
    sql_statements = []

    # create temp table to insert into.  This speeds up the insert tremendously because the SQL table insert will be done in batch with one transaction
    sql_statements.append('''
CREATE TABLE #temp_source_file_records(source_file_id int NOT NULL, row_number int NOT NULL, record nvarchar(max) NOT NULL, loader_record_id varchar(100) NULL,
street_number nvarchar(25) NULL, street nvarchar(255) NULL, city nvarchar(255) NULL, state nvarchar(255) NULL, zip nvarchar(255) NULL, phone nvarchar(255) NULL,
country_id int NULL, latitude decimal(9, 6) NULL, longitude decimal(9, 6) NULL, created_at datetime NULL, updated_at datetime NULL, suite nvarchar(100) NULL, note nvarchar(255) NULL,
company_generated_store_number nvarchar(255) NULL, store_format nvarchar(255) NULL, opened_date datetime NULL, source_date datetime NULL, shopping_center_name nvarchar(255) NULL)''')

    # create sql
    for address in parsed_records:

        # create statement.  This is compacted into one line on purpose.  It seems to finish much faster on large data sets
        sql_statements.append('''insert into #temp_source_file_records (source_file_id, row_number, record, loader_record_id, street_number, street, city, state, zip, country_id, phone, longitude, latitude, suite, shopping_center_name, opened_date, source_date, note, store_format, company_generated_store_number, created_at, updated_at)
values (%s, %d, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, GETUTCDATE(), GETUTCDATE())''' % (
            escape_string_clean_up(company_info.source_file_id),
            excel_row_counter,
            escape_string_clean_up(company_info.records[row_index_counter]),
            escape_string_clean_up(address.loader_record_id),
            escape_string_clean_up(address.street_number),
            escape_string_clean_up(address.street),
            escape_string_clean_up(address.city),
            escape_string_clean_up(address.state),
            escape_string_clean_up(address.zip_code),
            escape_string_clean_up(address.country_id),
            escape_string_clean_up(address.phone_number),
            escape_string_clean_up(address.longitude),
            escape_string_clean_up(address.latitude),
            escape_string_clean_up(address.suite_numbers),
            escape_string_clean_up(address.complex),
            escape_string_clean_up(address.loader_opened_on),
            escape_string_clean_up(address.source_date),
            escape_string_clean_up(address.note),
            escape_string_clean_up(address.store_format),
            escape_string_clean_up(address.company_generated_store_number)))

        # increment counters
        excel_row_counter += 1
        row_index_counter += 1

    # add insert into real table statements (from temp table)
    sql_statements.append('''
insert into source_file_records (source_file_id, row_number, record, loader_record_id, street_number, street, city, state, zip, country_id, phone, longitude, latitude, suite,
    shopping_center_name, opened_date, source_date, note, store_format, company_generated_store_number, created_at, updated_at)
select source_file_id, row_number, record, loader_record_id, street_number, street, city, state, zip, country_id, phone, longitude, latitude, suite, shopping_center_name,
    opened_date, source_date, note, store_format, company_generated_store_number, created_at, updated_at
from #temp_source_file_records''')

    # add drop temp table statement
    sql_statements.append("drop table #temp_source_file_records")

    big_statement = '; '.join(sql_statements)

    sql_execute(big_statement)