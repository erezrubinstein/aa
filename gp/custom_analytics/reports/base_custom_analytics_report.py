from common.utilities.date_utilities import pretty_please
from common.utilities.inversion_of_control import Dependency
from common.utilities.misc_utilities import split_up_list_into_smaller_partitions
from common.utilities.sql import sql_execute, sql_execute_on_db
from geoprocessing.custom_analytics.custom_analytics_excel_exporter import CustomAnalyticsExcelExporter

__author__ = 'erezrubinstein'

class BaseCustomAnalyticsReport(object):

    def __init__(self, time_periods, company_definitions = None, report_name = None):
        """
        Time Periods are required.  They should have the following format
            [
                {
                    "label": "t0",
                    "date": datetime.datetime(1900, 1, 1)
                },
                ...
            ]
        Company Definitions are optional.  If included, they will be outputted to each Excel report.  They have the following format:
            {
                company_id: {
                    company_name: name,
                    is_target: true/false,
                    weight: float,
                    time_periods: {
                        t0: "2012-03-28T00:00:00",
                        t1: "2013-07-04T00:00:00",
                        ....
                    }
                },
                ....
            }
        """

        # set class vars
        self._time_periods = time_periods
        self._company_definitions = company_definitions
        self._report_name = report_name

        # sort all the time periods, so that we run them in order (assume a t# format)
        self._time_periods = sorted(self._time_periods, key = lambda tp: tp["date"]) # tp, hahahaha


    # --------------------- Public Base Methods --------------------- #

    def taco_flavored_kisses(self):
        """
        Main Function For Running Things
        """

        # get the table name
        table_name = self._get_table_name()

        # some reports don't need to save because they're very simple joins
        # in that case, we don't need to run them at all until the "save" section
        if table_name:

            # run main query
            results = self._run_main_query()

            # pre-process the results
            results = self._pre_process_results_for_save(results)

            # if table is a string, we're saving one result set in
            if isinstance(table_name, basestring):

                # save the results
                self._save_results(results, table_name)

            # otherwise, assume it's an array where we're saving multiple result sets
            else:

                for index, table in enumerate(table_name):
                    self._save_results(results[index], table)


    def lets_make_a_run_for_the_border(self):
        """
        Main Method for Truncating the tables
        """

        self._truncate_table()


    def omg_they_killed_kenny(self, database_name = None):
        """
        Main Method for Querying the Data.
        This expects a database name because I'm assuming that it's called from retail, which has no concept of a "Main DB".
        The other methods are run at the report time and have a concept of a "Main DB"
        """

        return self._query_raw_report(database_name)


    def mrs_garrisson(self, db_results, folder_path = None):
        """
        Main Function for Exporting to Excel
        """
        self._export_xlsx(db_results, folder_path)


    # -------------------- Abstract Template Methods -------------------- #


    def _get_table_name(self):
        raise NotImplementedError("I pity the fool")

    def _run_main_query(self):
        raise NotImplementedError("I pity the fool")

    def _pre_process_results_for_save(self, results):
        raise NotImplementedError("I pity the fool")



    # ------------------ Protected Methods with Defaults ------------------ #

    def _get_excel_workbook_name(self):
        """
        Defaulted to the table name, but that should probably get changed...
        """
        return self._get_table_name()


    def _get_excel_data_sets(self, db_results):
        """
        Gets all columns and rows as is from the sql results.
        This is the base implementation, which you're highly encouraged to override.
        """

        # create one data set, which is the entire table.
        data_set = {
            "headers": [],
            "rows": [],
            # don't use more than 31 characters for an excel tab
            "label": self._get_table_name()[:31]
        }

        if db_results:

            # get headers definition from the first row (assuming they're all the same)
            header_definition = db_results[0]

            # loop through the cursor description adding the column names from the sql table as headers
            for column_definition in header_definition.cursor_description:

                # first item of the column definition is the name
                data_set["headers"].append(column_definition[0])

            # create rows with headers
            for row in db_results:

                # create header to row dict and append as row
                data_set["rows"].append({
                    header: getattr(row, header)
                    for header in data_set["headers"]
                })


        return [data_set]


    def _round(self, value):
        return round(value, 5)



    # --------------------- Private Base Methods --------------------- #

    def _save_results(self, results, table_name):
        """
        Generic Method of saving results to a table.
        Just pass in an array of dictionaries, where the following applies:
            1. Every key/value gets saved
            2. Every keys get mapped to column names and values are the values...
            3. Please preformat the values for saving (i.e. ints, strings, dates, etc...)
        """

        if results:

            # results could be huge, so let's split them into groups of 5000 or less results per batch save.
            batch_save_results = split_up_list_into_smaller_partitions(results, 5000)

            # save smaller batch sizes
            for result_set in batch_save_results:

                # create insert statement
                fields = result_set[0].keys()
                fields_string = ", ".join(fields)
                sql_statement = ["insert into %s" % table_name, "(", fields_string, ")"]

                # create select statements for insert
                select_statements = []

                # loop through results
                for row in result_set:

                    # create a comma separated values array in the same order as the fields in the insert part
                    select_values = ",".join([row[field] for field in fields])
                    select_values = " ".join(["SELECT", select_values])

                    # split values by comma and add to select statements
                    select_statements.append(select_values)

                # split select statements by "UNION ALL" and add to sql statement
                select_statements = " UNION ALL ".join(select_statements)
                sql_statement.append(select_statements)

                # make into string
                sql_statement = " ".join(sql_statement)

                # ignore unicode conversion here, which is ok with inline stuff.
                sql_command = {
                    "sql": sql_statement,
                    "ignore_unicode": True
                }

                # bomboj for, sucka!
                sql_execute(sql_command)


    def _truncate_table(self):

        # get table name
        table_name = self._get_table_name()

        # some queries are super simple and don't need to save a flattened version
        if table_name:

            if isinstance(table_name, basestring):

                # check yo'self before you wreck yo'self
                sql_execute("truncate table %s" % table_name)

            else:

                # assume it's an array and truncate all tables
                for table in table_name:
                    sql_execute("truncate table %s" % table)


    def _query_raw_report(self, database):

        # get the table
        table_name = self._get_table_name()

        # some reports are very simple and don't require saving.
        # in that case, just query their main instead of the flattened table
        if table_name:

            # little sub method to actually run the query
            def run_query(actual_table_name):

                # assuming that it's the same db server/settings as the main one, take the server/user/password from the settings
                config = Dependency("Config").value
                server = config.db_server
                username = config.db_username
                password = config.db_password

                # do a select *
                query = "select * from %s" % actual_table_name

                # run the query on main or other db
                if database:
                    return sql_execute_on_db(server, database, username, password, query)
                else:
                    return sql_execute(query)

            # if it's a string, just query and return
            if isinstance(table_name, basestring):
                return run_query(table_name)

            # otherwise, assume it's an array and return them all in an array
            else:
                return [run_query(table) for table in table_name]

        else:

            # just return raw main query as is
            return self._run_main_query()


    def _export_xlsx(self, db_results, folder_path = None):

        # get the report name
        report_name = self._get_excel_workbook_name()

        # if we have a set report_name, add it to the report name
        if self._report_name:
            report_name = "%s - %s" % (report_name, self._report_name)

        # always add the xlsx extension
        report_name += ".xlsx"

        # set the workbook name
        workbook_name = report_name

        # add the folder path, if it's there
        if folder_path:
            workbook_name = folder_path + workbook_name

        # figure out headers and rows
        data_sets = self._get_excel_data_sets(db_results)

        # add the custom analytics settings tab
        data_sets = self._add_custom_analytics_settings(data_sets)

        # run the report
        CustomAnalyticsExcelExporter(data_sets, workbook_name).export()


    def _add_custom_analytics_settings(self, data_sets):

        # if we have no company definitions, than just skip and return the original data sets
        if not self._company_definitions:
            return data_sets

        # get a sorted list of time period labels (assume time periods is of the format (t#)
        sorted_time_periods = [t["label"] for t in self._time_periods]
        sorted_time_periods = sorted(sorted_time_periods, key = lambda t: int(t[1:]))

        # create the data set
        settings_data_set = {
            "headers" : ["Company", "Is Target", "Weight"] + sorted_time_periods,
            "label": "Custom Analytics Settings",
            "rows": []
        }

        # cycle through companies to create the rows
        for company_id, company in self._company_definitions.iteritems():

            # create the time periods part of the row by dict comprehension
            row = {
                time_period_label: pretty_please(company["time_periods"][time_period_label], "None")
                for time_period_label in company["time_periods"]
            }

            # add the static items to the row
            row["Company"] = company["company_name"]
            row["Is Target"] = "Yes" if company["is_target"] else "No"
            row["Weight"] = company["weight"]

            # add the row to the data set
            settings_data_set["rows"].append(row)

        # sort the rows by company name
        settings_data_set["rows"] = sorted(settings_data_set["rows"], key = lambda row: row["Company"])

        # add the data set to the beginning of the data sets (i.e. first tab)
        return [settings_data_set] + data_sets
