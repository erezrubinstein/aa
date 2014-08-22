from common.utilities.sql import sql_execute
from geoprocessing.custom_analytics.data_checks.base_data_check import BaseCustomAnalyticsDataCheck

__author__ = 'erezrubinstein'

class CustomAnalyticsStoresHaveCountiesDataCheck(BaseCustomAnalyticsDataCheck):
    """
    This data check will make sure that no company has 0 stores
    """

    def _data_check_name(self):
        return "All Stores Have at least one county"

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
                "headers": ["Store ID", "County Matches"],
                "rows": [
                    {
                        "Store ID": sql_row.store_id,
                        "County Matches": 0

                    }
                    for sql_row in results
                ]
            }

        # bomboj for
        return formatted_results


    # --------------------------- Private Methods -------------------------- #

    def _create_sql(self):

        return """
        select s.store_id, county_matches.count as county_matches
        from stores s
        cross apply
        (
            select count(*) as count
            from county_store_matches
            where store_id = s.store_id
        ) county_matches
        where county_matches.count = 0
        order by s.store_id"""

    def _run_query(self):

        # get sql
        sql = self._create_sql()

        # run sql and return the results
        return sql_execute(sql)