from common.utilities.sql import sql_execute
from geoprocessing.custom_analytics.data_checks.base_data_check import BaseCustomAnalyticsDataCheck

__author__ = 'erezrubinstein'

class CustomAnalyticsStoreCountsDataCheck(BaseCustomAnalyticsDataCheck):
    """
    This data check will make sure that no company has 0 stores
    """

    def _data_check_name(self):
        return "All Companies Have At Least One Store"

    def _run_data_check(self):

        # run the query and return the results
        return self._run_query()


    def _format_results(self, results):

        # default results to empty
        formatted_results = {}

        # only proceed if results are bigger than zero
        if results:

            # set results
            formatted_results = {
                "headers": ["Company Name", "Store Count"],
                "rows": [
                    {
                        "Company Name": sql_row.company_name,
                        "Store Count": 0
                    }
                    for sql_row in results
                ]
            }

        # bomboj for
        return formatted_results


    # --------------------------- Private Methods -------------------------- #

    def _create_sql(self):

        return """
        select c.company_id, c.name as company_name, store_counts.count as store_count
        from companies c
        cross apply
        (
            select count(*) as count
            from stores s
            where s.company_id = c.company_id
        ) store_counts
        where store_counts.count = 0
        order by c.name"""

    def _run_query(self):

        # get sql
        sql = self._create_sql()

        # run sql and return the results
        return sql_execute(sql)