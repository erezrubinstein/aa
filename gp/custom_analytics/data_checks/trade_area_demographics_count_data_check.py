from common.utilities.sql import sql_execute
from geoprocessing.custom_analytics.data_checks.base_data_check import BaseCustomAnalyticsDataCheck

__author__ = 'erezrubinstein'

class CustomAnalyticsTradeAreaDemographicCountsDataCheck(BaseCustomAnalyticsDataCheck):
    """
    This data check will make sure that every trade are has the same number of demographics
    """

    def _data_check_name(self):
        return "Trade Area Demographic Counts Check"

    def _run_data_check(self):

        # run the query
        results = self._run_query()

        # if not results, raise an error
        if not results:
            raise Exception("Couldn't find any demographics...")

        # since it's sorted by descending count, assume the first record has the "ideal" amount of demographics
        max_demographics_count = results[0].count

        # default incorrect count to 0
        incorrect_count = 0

        # loop through all trade areas and add those that don't match the count to the incorrect count
        for trade_area_demographics in results:
            if trade_area_demographics.count != max_demographics_count:
                incorrect_count += 1

        return incorrect_count


    def _format_results(self, results):

        # default results to empty
        formatted_results = {}

        # only proceed if results are bigger than zero
        if results > 0:

            # set results
            formatted_results = {
                "headers": ["# Incorrect Trade Areas", "SQL"],
                "rows": [
                    {
                        "# Incorrect Trade Areas": results,
                        "SQL": self._create_sql()
                    }
                ]
            }

        # bomboj for
        return formatted_results


    # --------------------------- Private Methods -------------------------- #

    def _create_sql(self):

        return """
        select t.trade_area_id, count(distinct d.data_item_id) as count
        from trade_areas t
        left join demographic_numvalues d on d.trade_area_id = t.trade_area_id
        group by t.trade_area_id
        order by count(distinct d.data_item_id) desc"""

    def _run_query(self):

        # get sql
        sql = self._create_sql()

        # run sql and return the results
        return sql_execute(sql)