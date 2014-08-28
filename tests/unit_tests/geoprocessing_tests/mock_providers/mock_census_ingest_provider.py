__author__ = 'jsternberg'

class MockCensusIngestProvider(object):
    def __init__(self, census_year, table_name, file_path, db_file_path, db_format_file_path,
                 field_delimiter, column_list, skip_first_row, trim_double_quotes_from_columns):
        #ingest details
        self.census_year = census_year
        self.table_name = table_name
        self.file_path = file_path
        self.db_file_path = db_file_path
        self.db_format_file_path = db_format_file_path
        self.field_delimiter = field_delimiter
        self.column_list = column_list
        self.skip_first_row = skip_first_row
        self.trim_double_quotes_from_columns = trim_double_quotes_from_columns

        self.census_ingest_data = None

    def read_census_file(self, number_of_rows):
        #this stores the parsed data
        self.census_ingest_data = [['Ham', 'and', 'jam', 'and', 'spam-alot.'],
                                   ['Have', 'to', 'push', 'the', 'pram-alot.']]

    def get_census_ingest_data(self, start_row, number_of_rows):
        head = '\nTable: %s\n' % self.table_name
        rows = []
        end_row = start_row + number_of_rows + 1
        for row in self.census_ingest_data[start_row:end_row]:
            rows.append(str(row))
        return head + '\n'.join(rows)
