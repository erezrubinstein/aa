import datetime
from itertools import groupby
from common.utilities.sql import sql_execute_with_parameters
from geoprocessing.custom_analytics.reports.base_custom_analytics_report import BaseCustomAnalyticsReport
from geoprocessing.data_access.data_access_utilities import escape_string_clean_up, escape_date_clean_up
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies

__author__ = 'erezrubinstein'



class CustomAnalyticsCompetitionReport(BaseCustomAnalyticsReport):


    # ------------------ Implementation of the Template Methods ------------------ #

    def _get_table_name(self):
        return ["ca_competition", "ca_competition_summary"]


    def _get_excel_workbook_name(self):
        return "Competition"


    def _run_main_query(self):

        results = {
            "detail": {},
            "summary": {}
        }

        # run the query for every cohort
        for time_period in self._time_periods:

            # get cohort details
            time_period_label = time_period["label"]
            time_period_date = time_period["date"]

            # run query and save results per cohort
            results["detail"][time_period_label] = self._run_detail_query(time_period_date)
            results["summary"][time_period_label] = self._run_summary_query(time_period_date)

        return results


    def _pre_process_results_for_save(self, results):

        # pretty array for return
        pretty_detailed_results = []
        pretty_summary_results = []

        # loop through cohorts and their details to their respective data sets
        for time_period in self._time_periods:

            # get cohort details
            time_period_label = time_period["label"]
            time_period_date = time_period["date"]

            # loop through sql results to create the detailed table
            for sql_row in results["detail"][time_period_label]:

                # add pretty results
                pretty_detailed_results.append({
                    "home_company_id": str(sql_row.home_company_id),
                    "home_company_name": escape_string_clean_up(sql_row.home_company_name),
                    "away_company_id": str(sql_row.away_company_id),
                    "away_company_name": escape_string_clean_up(sql_row.away_company_name),
                    "trade_area_threshold": escape_string_clean_up(sql_row.trade_area_threshold),
                    "time_period_label": escape_string_clean_up(time_period_label),
                    "time_period_date": escape_date_clean_up(time_period_date),
                    "distinct_away_stores": str(sql_row.distinct_away_stores),
                    "competitive_instances": str(sql_row.competitive_instances),
                    "home_store_count": str(sql_row.home_store_count),
                    "competition_ratio": str(sql_row.competition_ratio),
                    "percent_store_base_affected": str(sql_row.percent_store_base_affected)
                })

            # loop through sql results
            for sql_row in results["summary"][time_period_label]:

                # add pretty results
                pretty_summary_results.append({
                    "home_company_id": str(sql_row.home_company_id),
                    "home_company_name": escape_string_clean_up(sql_row.home_company_name),
                    "trade_area_threshold": escape_string_clean_up(sql_row.trade_area_threshold),
                    "time_period_label": escape_string_clean_up(time_period_label),
                    "time_period_date": escape_date_clean_up(time_period_date),
                    "competition_ratio": str(sql_row.competition_ratio),
                    "percent_store_base_affected": str(sql_row.percent_store_base_affected)
                })

        return [pretty_detailed_results, pretty_summary_results]


    def _get_excel_data_sets(self, db_results):

        # define data sets
        data_sets = []

        # get the detailed/summary results, since this report has two result sets
        detail_db_results = db_results[0]
        summary_db_results = db_results[1]

        # calculate the summary db results
        data_sets.append(self._create_summary_dataset(summary_db_results))


        # calculate the detailed data sets for each time period
        # ..... below

        # sort the results by label, home company, trade_area_threshold, away_company
        detail_db_results = sorted(detail_db_results, key = lambda row: (int(row.time_period_label[1:]), float(row.trade_area_threshold.split(" ")[0]), row.home_company_name, row.away_company_name))

        # group the data by each cohort so that we can create a tab for each
        for time_period_label, sql_rows in groupby(detail_db_results, key = lambda sql_row: sql_row.time_period_label):

            # create the detail data set
            data_sets.append(self._create_detail_dataset(time_period_label, sql_rows))

        # very nice
        return data_sets



    # ----------------------------- Private Helpers ------------------------------ #

    def _create_summary_dataset(self, summary_db_results):

        # each sub table will have the same headers, so I'm creating them once up here
        headers = self._create_summary_headers()
        headers_comments = self._create_summary_header_comments()

        # create the tables array which will be used for excel sub tables for every trade area
        excel_tables = []

        # sort the sql rows by trade area so that we can group accordingly (assume trade areas have a number fist)
        summary_db_results = sorted(summary_db_results, key = lambda sql_row: float(sql_row.trade_area_threshold.split(" ")[0]))

        # group by trade area
        for trade_area, trade_area_sql_rows in groupby(summary_db_results, key = lambda sql_row: sql_row.trade_area_threshold):

            # create an empty table for each trade area
            trade_area_table = {
                "header": trade_area,
                "headers": headers,
                "headers_comments": headers_comments,
                "rows": []
            }

            # sort the trade area rows by home company so that we can group by that
            trade_area_sql_rows = sorted(trade_area_sql_rows, key = lambda sql_row: sql_row.home_company_name)

            # group by home company
            for home_company_name, home_company_rows in groupby(trade_area_sql_rows, key = lambda sql_row: sql_row.home_company_name):

                # create the base row for this company
                row = { "Banner": home_company_name }

                # sort the company rows by time period (assuming a t# format)
                home_company_rows = sorted(home_company_rows, key = lambda sql_row: int(sql_row.time_period_label[1:]))

                # loop through every home company row (should be one row per time period)
                for time_period_index, company_row in enumerate(home_company_rows):

                    # get some helper vars
                    time_period = company_row.time_period_label
                    competition_ratio = company_row.competition_ratio
                    percent_store_base_affected = company_row.percent_store_base_affected

                    # add competition_ratio and percent_store_base_affected, since they're always added for each time period
                    row["%s - Comp Ratio" % time_period] = self._round(competition_ratio)
                    row["%s - %% Store Base Affected" % time_period] = self._round(percent_store_base_affected)

                    # don't add the % change columns for the first time period because it doesn't qualify
                    if time_period_index > 0:

                        # get previous values
                        previous_competition_ratio = home_company_rows[time_period_index - 1].competition_ratio
                        previous_percent_store_base_affected = home_company_rows[time_period_index - 1].percent_store_base_affected

                        # calc the % change and add to the row
                        row["%s - Comp Ratio %% Change" % time_period] = self._get_percent_change(competition_ratio, previous_competition_ratio)
                        row["%s - %% Store Base Affected - Change" % time_period] = self._get_percent_change(percent_store_base_affected, previous_percent_store_base_affected)

                # done populating company row... phew... now add to the main table
                trade_area_table["rows"].append(row)

            # done populating trade area table... phew... now add to the tables list
            excel_tables.append(trade_area_table)


        # return the data set with all the tables
        return {
            "label": "Competition Summary",
            "type": "multi_table",
            "tables": excel_tables
        }

    def _create_summary_headers(self):

        # create a list of all time periods
        sorted_time_periods = [t["label"] for t in self._time_periods]
        sorted_time_periods = sorted(sorted_time_periods, key = lambda t: int(t[1:]))

        # begin with just company name
        headers = ["Banner"]

        # for each time period, add competition ratio
        for time_period in sorted_time_periods:
            headers.append("%s - Comp Ratio" % time_period)

        # for each time period, % Store Base Affected
        for time_period in sorted_time_periods:
            headers.append("%s - %% Store Base Affected" % time_period)

        # for each time period, add competition ratio % change
        for index, time_period in enumerate(sorted_time_periods):

            # don't add % change for the first time period, since it doesn't qualify
            if index > 0:
                headers.append("%s - Comp Ratio %% Change" % time_period)

        # for each time period, % Store Base Affected
        for index, time_period in enumerate(sorted_time_periods):

            # don't add % change for the first time period, since it doesn't qualify
            if index > 0:
                headers.append("%s - %% Store Base Affected - Change" % time_period)

        return headers

    def _create_summary_header_comments(self):

        # dict for comments
        comments = {}

        # create a list of all time periods
        sorted_time_periods = [t["label"] for t in self._time_periods]
        sorted_time_periods = sorted(sorted_time_periods, key = lambda t: int(t[1:]))

        for index, time_period in enumerate(sorted_time_periods):

            # add comment for comp ratio
            comments["%s - Comp Ratio" % time_period] = "Competition Ratio; equivalent to Competition Instances divided by Home Stores."

            # add comment for % store base affected
            comments["%s - %% Store Base Affected" % time_period] = "The percentage of the banner's store base that has at least one competition instance."

            # add comment for comp ratio % change
            if index > 0:
                comments["%s - Comp Ratio %% Change" % time_period] = "% change in between the previous period and this period's Comp Ratio."

            # add comment for % store base affected change
            if index > 0:
                comments["%s - %% Store Base Affected - Change" % time_period] = "% change in between the previous period and this period's % Store Base Affected."

        # booyakasha
        return comments

    def _create_detail_dataset(self, time_period_label, sql_rows):

        return {
            "headers" : ["Home Banner", "Away Banner", "Trade Area", "Distinct Away Stores", "Competitive Instances", "Home Stores", "Competition Ratio", "Percent Store Base Affected"],
            "headers_comments": {
                "Home Banner": "Competition metrics have a directionality. The home banner is the retailer that owns or operates the stores that experience competition from the away banner's stores. Competition metrics are generally represented with Home -> Away orientation.",
                "Away Banner": "Competition metrics have a directionality. The away banner is the retailer that is exerting competitive pressure on the home banner's stores. Competition metrics are generally represented with Home -> Away orientation.",
                "Distinct Away Stores": "Distinct away banner stores that compete with the home banner's stores.",
                "Competitive Instances": "The number of times that a competitor store competes with the stores of this banner.",
                "Home Stores": "The number of times that a competitor store competes with the stores of this banner.",
                "Competition Ratio": "Competition Instances divided by Home Stores.",
                "Percent Store Base Affected": "The percentage of the home banner's store base that has at least one competition instance with the away banner's stores."
            },
            "label": "%s - detail" % time_period_label,
            "rows": [
                {
                    "Home Banner": sql_row.home_company_name,
                    "Away Banner": sql_row.away_company_name,
                    "Trade Area": sql_row.trade_area_threshold,
                    "Distinct Away Stores": sql_row.distinct_away_stores,
                    "Competitive Instances": sql_row.competitive_instances,
                    "Home Stores": sql_row.home_store_count,
                    "Competition Ratio": self._round(sql_row.competition_ratio),
                    "Percent Store Base Affected": self._round(sql_row.percent_store_base_affected)
                }
                for sql_row in sql_rows
            ]
        }

    def _get_percent_change(self, current_value, previous_value):

        if not previous_value:
            return 0

        # no need to cast to float.  SQL Driver automatically makes it a decimal, which is actually better!
        return self._round(((current_value - previous_value) / previous_value) * 100)


    def _run_detail_query(self, time_period):

        # I pity the fool that tries to debug this query (or the one below)!
        query = """

            -- CTE for home store count
            ; WITH store_counts (company_id, store_count) as
            (
                select s.company_id, count(*) as store_count
                from stores s
                where s.assumed_opened_date <= ? and (s.assumed_closed_date is null or s.assumed_closed_date > ?)
                group by s.company_id
            ),
            -- CTE for all thresholds within this db
            trade_area_thresholds (trade_area_threshold) as
            (
                select distinct th.label as trade_area_threshold
                from trade_areas t
                inner join thresholds th on th.threshold_id = t.threshold_id
            ),
            -- CTE for raw competition counts and statistics
            competition (home_company_id, away_company_id, trade_area_threshold, distinct_away_stores, competitive_instances, distinct_home_stores_affected) as
            (
                select
                    hc.company_id as home_company_id,
                    ac.company_id as away_company_id,
                    th.label as trade_area_threshold,
                    count(distinct [as].store_id) as distinct_away_stores,
		            sum(cc.competition_strength) as competitive_instances,
                    count(distinct hs.store_id) as distinct_home_stores_affected
                from companies hc
                inner join stores hs on hs.company_id = hc.company_id
                inner join trade_areas t on t.store_id = hs.store_id
                inner join thresholds th on th.threshold_id = t.threshold_id
                inner join competitive_stores cs on cs.trade_area_id = t.trade_area_id and
                    cs.start_date <= ? and (cs.end_date is null or cs.end_date > ?)
                inner join stores [as] on [as].store_id = cs.away_store_id
                inner join companies ac on ac.company_id = [as].company_id
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where hs.assumed_opened_date <= ? and (hs.assumed_closed_date is null or hs.assumed_closed_date > ?)
                group by hc.company_id, ac.company_id, th.label
            )

            -- main query to cross join all companies/companies/thresholds and left join on competition
            select
                hc.company_id as home_company_id,
                hc.name as home_company_name,
                ac.company_id as away_company_id,
                ac.name as away_company_name,
                th.trade_area_threshold,
                isnull(c.distinct_away_stores, 0) as distinct_away_stores,
                isnull(c.competitive_instances, 0) as competitive_instances,
                isnull(scounts.store_count, 0) as home_store_count,
                isnull(cast(c.competitive_instances as float) / scounts.store_count, 0) as competition_ratio,
                isnull((cast(c.distinct_home_stores_affected as float) / scounts.store_count) * 100, 0) as percent_store_base_affected
            from companies hc
            cross join companies ac
            cross join trade_area_thresholds th
            left join store_counts scounts on scounts.company_id = hc.company_id
            left join competition c on c.home_company_id = hc.company_id and c.away_company_id = ac.company_id and th.trade_area_threshold = c.trade_area_threshold
            order by hc.name, ac.name, th.trade_area_threshold
        """

        return sql_execute_with_parameters([time_period, time_period, time_period, time_period, time_period, time_period], query)


    def _run_summary_query(self, time_period):

        # I pity the fool that tries to debug this query (or the one above)!
        query = """

            -- CTE for home store count
            ; WITH store_counts (company_id, store_count) as
            (
                select s.company_id, count(*) as store_count
                from stores s
                where s.assumed_opened_date <= ? and (s.assumed_closed_date is null or s.assumed_closed_date > ?)
                group by s.company_id
            ),
            -- CTE for all thresholds within this db
            trade_area_thresholds (trade_area_threshold) as
            (
                select distinct th.label as trade_area_threshold
                from trade_areas t
                inner join thresholds th on th.threshold_id = t.threshold_id
            ),
            -- CTE for raw competition counts and statistics
            competition (home_company_id, trade_area_threshold, competitive_instances, distinct_home_stores_affected) as
            (
                select
                    hc.company_id as home_company_id,
                    th.label as trade_area_threshold,
		            sum(cc.competition_strength) as competitive_instances,
                    count(distinct hs.store_id) as distinct_home_stores_affected
                from companies hc
                inner join stores hs on hs.company_id = hc.company_id
                inner join trade_areas t on t.store_id = hs.store_id
                inner join thresholds th on th.threshold_id = t.threshold_id
                inner join competitive_stores cs on cs.trade_area_id = t.trade_area_id and
                    cs.start_date <= ? and (cs.end_date is null or cs.end_date > ?)
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where hs.assumed_opened_date <= ? and (hs.assumed_closed_date is null or hs.assumed_closed_date > ?)
                group by hc.company_id, th.label
            )

            -- main query to cross join all companies/thresholds and left join on competition
            select
                hc.company_id as home_company_id,
                hc.name as home_company_name,
                th.trade_area_threshold,
                isnull(cast(c.competitive_instances as float) / scounts.store_count, 0) as competition_ratio,
                isnull((cast(c.distinct_home_stores_affected as float) / scounts.store_count) * 100, 0) as percent_store_base_affected
            from companies hc
            cross join trade_area_thresholds th
            left join store_counts scounts on scounts.company_id = hc.company_id
            left join competition c on c.home_company_id = hc.company_id and th.trade_area_threshold = c.trade_area_threshold
            order by hc.name, th.trade_area_threshold
        """

        return sql_execute_with_parameters([time_period, time_period, time_period, time_period, time_period, time_period], query)


# ----------------------------------- Main ------------------------------------ #


def main():

    # create cohorts
    time_periods = [
        {
            "label": "t0",
            "date": datetime.datetime(1900, 1, 1)
        },
        {
            "label": "t1",
            "date": datetime.datetime(2013, 7, 31)
        }
    ]

    # create report
    report = CustomAnalyticsCompetitionReport(time_periods)

    # run report
    report.lets_make_a_run_for_the_border()
    report.taco_flavored_kisses()
    results = report.omg_they_killed_kenny()
    report.mrs_garrisson(results)

    print "done"


if __name__ == "__main__":

    # register dependencies
    register_concrete_dependencies()

    main()