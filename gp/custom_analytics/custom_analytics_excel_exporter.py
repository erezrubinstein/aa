from collections import defaultdict
import xlsxwriter

__author__ = 'erezrubinstein'

class CustomAnalyticsExcelExporter(object):

    def __init__(self, data_sets, report_name, worksheet_name = None):
        """
        Each data set represents a tab.
        You can include multiple tables within a dataset if you want multiple data points within one tab.
        """

        # class level vars
        self.data_sets = data_sets
        self.report_name = report_name
        self.worksheet_name = worksheet_name if worksheet_name else self.report_name

        # create the workbook and the worksheet
        self.workbook = xlsxwriter.Workbook(self.report_name)

        # create some common styling formats to be used on this workbook
        self.bold_style = self.workbook.add_format({ "bold": True })
        self.vertical_bold_style = self.workbook.add_format({ "bold": True, "rotation": 90 })
        self.header_style = self.workbook.add_format({ "bold": True, "font_size": 16 })


    def export(self):

        # add a table of contents
        self._create_table_of_contents()

        # for each data set, create a new worksheet
        for data_set in self.data_sets:

            # figure out the data set type.  Default to single table for backwards compatibility.
            data_set_type = data_set.get("type", "single_table")

            # create the new worksheet (i.e. tab)
            worksheet_name = data_set["label"]
            worksheet = self.workbook.add_worksheet(worksheet_name)

            # if it's one table, just write it
            if data_set_type == "single_table":

                # write the table to the worksheet
                self._write_dataset_table(worksheet, data_set, 0)

            # if it's a multi one, write in a loop
            elif data_set_type == "multi_table":

                # keep track of where to begin writing each table
                current_row_index = 0

                # loop through the tables and write them
                for table in data_set["tables"]:
                    current_row_index = self._write_dataset_table(worksheet, table, current_row_index)

            else:
                raise Exception("%s is an unknown data_set type." % data_set_type)

        # close the workbook
        self.workbook.close()




    # ---------------------------------- Private Helpers ---------------------------------- #

    def _create_table_of_contents(self):

        # create the worksheet
        worksheet = self.workbook.add_worksheet("Table Of Contents")

        # keep track of max chars
        column_max_character_count = defaultdict(int)

        # add the headers
        self._write_value(worksheet, 0, 0, "Link", self.header_style)
        self._write_value(worksheet, 0, 1, "Description", self.header_style)

        # loop through data sets
        for index, data_set in enumerate(self.data_sets):

            # get the label and description
            label = data_set["label"]
            description = data_set.get("description", label)

            # write label, description
            worksheet.write_url(index + 1, 0, "internal:'%s'!A1" % label, string = label)
            self._write_value(worksheet, index + 1, 1, description)# track the rows character count

            # keep track of max characters per
            self._track_max_character(column_max_character_count, 0, label)
            self._track_max_character(column_max_character_count, 1, description)

        # attempt to set auto width for each column
        self._set_auto_widths(worksheet, column_max_character_count)

    def _write_dataset_table(self, worksheet, table, row_starting_point):

        # figure out headers, rows, worksheet name, and other worksheet helpers
        table_header = table.get("header", None)
        headers = table["headers"]
        headers_comments = table.get("headers_comments", {})
        headers_comments_per_index = table.get("headers_comments_per_index", [])
        header_unique_mappings = table.get("unique_headers_mapping", {})
        rows = table["rows"]
        headers_format = table.get("headers_format", None)
        headers_indexes_to_ignore_format = table.get("headers_indexes_to_ignore_format", [])
        column_max_character_count = defaultdict(int)

        # if there's a header, write it, and keep track of it in the row_starting_point
        if table_header:

            # write the header
            self._write_table_header(worksheet, row_starting_point, table_header)

            # track the rows character count
            self._track_max_character(column_max_character_count, 0, table_header)

            row_starting_point += 1

        # write headers and see how many rows they took
        header_rows, headers_for_data_indexes = self._write_headers(headers, worksheet, column_max_character_count, row_starting_point,
                                                                    headers_format, headers_indexes_to_ignore_format, headers_comments,
                                                                    headers_comments_per_index)

        # write rows
        for row_index, row in enumerate(rows):

            # figure out the real row index based on where we are in the worksheet
            real_row_index = row_starting_point + header_rows + row_index

            # cycle through headers
            for col_index, header in enumerate(headers_for_data_indexes):

                # get meta settings for the row
                row_meta = row.get("meta", {})
                is_bold = row_meta.get("bold", False)

                # figure out styles based on meta
                style = None
                if is_bold:
                    style = self.bold_style

                # if there are header mappings, use those to get the value
                if header_unique_mappings:
                    value = row[header_unique_mappings[col_index]]
                else:
                    value = row[header]

                # add 1 (or how many rows in header) to row index to account for header
                self._write_value(worksheet, real_row_index, col_index, value, style)

                # track the rows character count
                self._track_max_character(column_max_character_count, col_index, value)

        # attempt to set auto width for each column
        self._set_auto_widths(worksheet, column_max_character_count)

        # the next row's index
        return row_starting_point + header_rows + len(rows) + 1


    def _write_headers(self, headers, worksheet, column_max_character_count, row_starting_point, headers_format, headers_indexes_to_ignore_format, headers_comments, headers_comments_per_index):

        # this is the simple header, if it's only one list of strings
        if isinstance(headers[0], basestring):
            for col_index, header in enumerate(headers):

                # write the header
                self._write_header_value(worksheet, row_starting_point, col_index, header, headers_format, headers_indexes_to_ignore_format,
                                         column_max_character_count, headers_comments, headers_comments_per_index)

            return 1, headers

        # this is the more complex double (or triple, etc..) header
        elif isinstance(headers[0], list):

            # loop through every header of every header row
            for row_index, header_list in enumerate(headers):
                for col_index, header in enumerate(header_list):

                    # since this is a multi row header, we need different comments per row
                    if headers_comments_per_index and len(headers_comments_per_index) > row_index:
                        headers_comments_per_index_instance = headers_comments_per_index[row_index]
                    else:
                        headers_comments_per_index_instance = []

                    # write the header
                    self._write_header_value(worksheet, row_starting_point + row_index, col_index, header, headers_format, headers_indexes_to_ignore_format,
                                             column_max_character_count, headers_comments, headers_comments_per_index_instance)

            # return the last header as the one to "index" by
            return len(headers), headers[len(headers) - 1]

        else:
            raise Exception("Unknown header format")


    def _write_header_value(self, worksheet, row_index, col_index, header, headers_format, headers_indexes_to_ignore_format, column_max_character_count, headers_comments,
                            headers_comments_per_index):

        # figure out style
        style, track_full_header_text = self._get_header_styles(headers_format, headers_indexes_to_ignore_format, col_index)

        # write header
        self._write_value(worksheet, row_index, col_index, header, style)

        # write comment, if there is one
        if header in headers_comments:
            worksheet.write_comment(row_index, col_index, headers_comments[header])
        elif col_index in headers_comments_per_index:
            worksheet.write_comment(row_index, col_index, headers_comments_per_index[col_index])

        # track the headers character count
        if track_full_header_text:
            self._track_max_character(column_max_character_count, col_index, header)
        else:

            # track smaller text, since it's vertical
            self._track_max_character(column_max_character_count, col_index, "ok")


    def _get_header_styles(self, headers_format, headers_indexes_to_ignore_format, header_index):

        # figure out style
        if headers_format == "vertical" and header_index not in headers_indexes_to_ignore_format:
            style = self.vertical_bold_style
            track_full_header_text = False
        else:
            style = self.bold_style
            track_full_header_text = True

        return style, track_full_header_text

    def _write_table_header(self, worksheet, row_starting_point, table_header):

        # write the header, but have take the entire width of the report and merge the cells
        self._write_value(worksheet, row_starting_point, 0, table_header, self.header_style)


    def _write_value(self, worksheet, row_index, col_index, value, style = None):

        # basic write method.
        worksheet.write(row_index, col_index, value, style)


    def _track_max_character(self, column_max_character_count, column_index, data):

        # convert non ints to strings to count the characters.
        string = data
        if not isinstance(string, basestring):
            string = str(string)

        # get the length of the data as a string (3 char minimum)
        char_length = max(len(string), 3)

        # compare to the current max and adjust if larger
        if char_length > column_max_character_count[column_index]:
            column_max_character_count[column_index] = char_length



    def _set_auto_widths(self, worksheet, column_max_character_count):

        # set auto widths according to max col lengths
        for column_index in column_max_character_count:

            # get max chars
            max_chars = column_max_character_count[column_index]

            # this is my (Erez) roughest attempt to estimate width based on char length.  It seems to work.
            width = max_chars

            # set the column width
            worksheet.set_column(column_index, column_index, width)
