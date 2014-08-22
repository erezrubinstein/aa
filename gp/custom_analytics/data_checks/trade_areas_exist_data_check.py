from common.utilities.sql import sql_execute
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.custom_analytics.data_checks.base_data_check import BaseCustomAnalyticsDataCheck

__author__ = 'erezrubinstein'

class CustomAnalyticsTradeAreaExistsDataCheck(BaseCustomAnalyticsDataCheck):
    """
    This data check will read the geoprocessing config and make sure that every store has the correct trade area
    """

    def _data_check_name(self):
        return "All Trade Areas Exist"


    def _run_data_check(self):

        # get the trade area ids that should exist
        trade_area_ids = [getattr(TradeAreaThreshold, threshold) for threshold in self._gp_config.trade_area_thresholds]

        # get the sql
        sql = self._create_sql(trade_area_ids)

        # run the sql and return the results
        return self._run_sql(sql)


    def _format_results(self, results):

        # get a count of how many stores are broken
        stores_missing_trade_areas = len(results)

        # default to no results
        formatted_results = {}

        if stores_missing_trade_areas > 0:

            # regenerate the sql to include in the report
            trade_area_ids = [getattr(TradeAreaThreshold, threshold) for threshold in self._gp_config.trade_area_thresholds]
            sql = self._create_sql(trade_area_ids)

            # set results
            formatted_results = {
                "headers": ["# Incorrect Stores", "SQL"],
                "rows": [
                    {
                        "# Incorrect Stores": stores_missing_trade_areas,
                        "SQL": sql
                    }
                ]
            }

        return formatted_results


    # --------------------------- Private Methods -------------------------- #

    def _create_sql(self, trade_area_ids):
        """
        Create the below statement dynamically for all trade areas:

            select s.store_id, t_1.threshold_id as t_1, t_4.threshold_id as t_4, t_5.threshold_id as t_5, t_13.threshold_id as t_13
            from stores s
            left join trade_areas t_1 on t_1.store_id = s.store_id and t_1.threshold_id = 1
            left join trade_areas t_4 on t_4.store_id = s.store_id and t_4.threshold_id = 4
            left join trade_areas t_5 on t_5.store_id = s.store_id and t_5.threshold_id = 5
            left join trade_areas t_13 on t_13.store_id = s.store_id and t_13.threshold_id = 13
            where t_1.threshold_id is null or t_4.threshold_id is null or t_5.threshold_id is null or t_13.threshold_id is null
        """


        # create the fields to select sql
        fields_to_select = ["t_%i.threshold_id" % ta for ta in trade_area_ids]
        fields_to_select = ", ".join(fields_to_select)

        # create a left join statement for every trade area
        left_joins_sql = [
            "left join trade_areas t_%i on t_%i.store_id = s.store_id and t_%i.threshold_id = %i" % (ta, ta, ta, ta)
            for ta in trade_area_ids
        ]
        left_joins_sql = "\n".join(left_joins_sql)

        # create the where clause dynamically
        where_statements = ["t_%s.threshold_id is null" % ta for ta in trade_area_ids]
        where_statements = " or ".join(where_statements)

        # create the main sql statement
        return """
        select s.store_id, %s
        from stores s
        %s
        where %s
        """ % (fields_to_select, left_joins_sql, where_statements)

    def _run_sql(self, sql):

        # execute this *!%$#
        return sql_execute(sql)