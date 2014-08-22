from common.utilities.sql import sql_execute
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.custom_analytics.data_checks.base_data_check import BaseCustomAnalyticsDataCheck

__author__ = 'erezrubinstein'

class CustomAnalyticsTradeAreaCompetitionOrMonopoliesDataCheck(BaseCustomAnalyticsDataCheck):
    """
    This data check will read the geoprocessing config and make sure that every store has the correct trade area
    """

    def _data_check_name(self):
        return "All Trade Areas Have Competition or Monopolies"


    def _run_data_check(self):

        # run the sql and return the results
        return self._run_sql()


    def _format_results(self, results):

        # default the results to nothing
        formatted_results = {}

        # if there are results, than go from there
        if results:

            formatted_results = {
                "headers": ["# Incorrect Trade Areas", "SQL"],
                "rows": [
                    {
                        "# Incorrect Trade Areas": len(results),
                        "SQL": self._create_sql()
                    }
                ]
            }

        return formatted_results


    # --------------------------- Private Methods -------------------------- #

    def _create_sql(self):

        # return the sql
        return """
        select t.trade_area_id, competition.count as competition_count, monopolies.count as monopolies_count
        from trade_areas t
        cross apply
        (
            select count(*) as count
            from competitive_stores cs
            where cs.trade_area_id = t.trade_area_id
        ) competition
        cross apply
        (
            select count(*) as count
            from monopolies m
            where m.trade_area_id = t.trade_area_id
        ) monopolies
        where competition.count = 0 and monopolies.count = 0"""


    def _run_sql(self):

        # get the sql
        sql = self._create_sql()

        # run and return the results
        return sql_execute(sql)