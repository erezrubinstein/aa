import datetime
from itertools import groupby
from common.utilities.sql import sql_execute_with_parameters
from geoprocessing.custom_analytics.reports.base_custom_analytics_report import BaseCustomAnalyticsReport
from geoprocessing.data_access.data_access_utilities import escape_string_clean_up, escape_date_clean_up
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies

__author__ = 'erezrubinstein'



class CustomAnalyticsDemographicsAggregateReport(BaseCustomAnalyticsReport):


    # ------------------ Implementation of the Template Methods ------------------ #

    def _get_table_name(self):
        return "ca_demographic_aggregates"


    def _get_excel_workbook_name(self):
        return "Demographic Screening"


    def _run_main_query(self):

        # keep results for all_stores, openings, and closings
        results = {
            "all_stores": {},
            "openings": {},
            "closings": {}
        }

        # run the query for every time period
        for index, time_period in enumerate(self._time_periods):

            # get cohort details
            time_period_label = time_period["label"]
            time_period_date = time_period["date"]

            # get the previous cohort date (if it exists).  This is for figuring out openings/closings
            previous_cohort_date = self._time_periods[index - 1]["date"] if index > 0 else None

            # run query and save results for every churn type, per cohort
            results["all_stores"][time_period_label] = self._run_time_period_query(time_period_date, previous_cohort_date, "all_stores")
            results["openings"][time_period_label] = self._run_time_period_query(time_period_date, previous_cohort_date, "openings")
            results["closings"][time_period_label] = self._run_time_period_query(time_period_date, previous_cohort_date, "closings")

        return results


    def _pre_process_results_for_save(self, results):

        # pretty array for return
        pretty_results = []

        # loop through all the churn types
        for churn_type in ["all_stores", "openings", "closings"]:

            # loop through cohorts and their details to their respective data sets
            for time_period in self._time_periods:

                # get cohort details
                time_period_label = time_period["label"]
                time_period_date = time_period["date"]

                # loop through sql results for this churn type, for this label
                for sql_row in results[churn_type][time_period_label]:

                    # add pretty results
                    pretty_results.append({
                        "company_id": str(sql_row.company_id),
                        "company_name": escape_string_clean_up(sql_row.company_name),
                        "trade_area_threshold": escape_string_clean_up(sql_row.trade_area_threshold),
                        "data_item_id": str(sql_row.data_item_id),
                        "demographic_name": escape_string_clean_up(sql_row.demographic_name),
                        "demographic_description": escape_string_clean_up(sql_row.demographic_description),
                        "time_period_label": escape_string_clean_up(time_period_label),
                        "time_period_date": escape_date_clean_up(time_period_date),
                        "churn_type": escape_string_clean_up(churn_type),
                        "avg": str(sql_row.avg),
                        "median": str(sql_row.med),
                        "min": str(sql_row.min),
                        "max": str(sql_row.max),
                        "stdev": str(sql_row.stdev),
                        "avg_competition_adjusted": str(sql_row.avg_competition_adjusted),
                        "median_competition_adjusted": str(sql_row.med_competition_adjusted),
                        "min_competition_adjusted": str(sql_row.min_competition_adjusted),
                        "max_competition_adjusted": str(sql_row.max_competition_adjusted),
                        "stdev_competition_adjusted": str(sql_row.stdev_competition_adjusted),
                    })

        return pretty_results


    def _get_excel_data_sets(self, db_results):

        # define data sets
        data_sets = []

        # sort by cohort labels, then churn type
        db_results = sorted(db_results, key = lambda row: (int(row.time_period_label[1:]), row.churn_type))

        # group the data by each churn_type/cohort so that we can create a tab for each
        for group_identifier, sql_rows in groupby(db_results, key = lambda row: (row.time_period_label, row.churn_type)):

            # get cohort date/label
            time_period_label = group_identifier[0]
            pretty_churn_type = group_identifier[1].replace("_", " ")

            # create nice looking tab name
            tab_name = " - ".join([time_period_label, pretty_churn_type])

            # sort the rows by company, trade_area, data_item_id asc
            # for trade area, assume that the first half is a number, so split it by space and convert to an int
            sql_rows = sorted(sql_rows, key = lambda row: (row.company_name, float(row.trade_area_threshold.split(" ")[0]), row.data_item_id))

            # create the data set
            data_sets.append({
                "headers" : ["Banner Name", "Trade Area", "Demographic", "Description", "Minimum", "Maximum", "Average", "Median",
                             "Competition Adjusted Min", "Competition Adjusted Max", "Competition Adjusted Avg", "Competition Adjusted Med"],
                "label": tab_name,
                "rows": [
                    {
                        "Banner Name": sql_row.company_name,
                        "Trade Area": sql_row.trade_area_threshold,
                        "Demographic": sql_row.demographic_name,
                        "Description": sql_row.demographic_description,
                        "Minimum": self._round(sql_row.min),
                        "Maximum": self._round(sql_row.max),
                        "Average": self._round(sql_row.avg),
                        "Median": self._round(sql_row.median),
                        "Competition Adjusted Min": self._round(sql_row.min_competition_adjusted),
                        "Competition Adjusted Max": self._round(sql_row.max_competition_adjusted),
                        "Competition Adjusted Avg": self._round(sql_row.avg_competition_adjusted),
                        "Competition Adjusted Med": self._round(sql_row.median_competition_adjusted)
                    }
                    for sql_row in sql_rows
                ]
            })



        # very nice
        return data_sets


    # ----------------------------- Private Helpers ------------------------------ #

    def _run_time_period_query(self, current_time_period, previous_time_period, churn_type):
        """
        For each company (and trade area), aggregate the demographics to get min/max/avg/med.  We calculate each aggregate as raw and as competition adjusted.
        """

        # define some dynamic filters to deal with openings/closings.
        if churn_type == "all_stores":

            # for all stores, just make sure the stores are active within this point
            store_date_query = "s.assumed_opened_date <= ? and (s.assumed_closed_date is null or s.assumed_closed_date > ?)"
            stores_date_param_1 = current_time_period
            stores_date_param_2 = current_time_period
            competition_date_param_1 = current_time_period
            competition_date_param_2 = current_time_period

        elif churn_type == "openings" and previous_time_period:

            # for openings, make sure the store opened between the previous time period and this time period
            # show competition from this period
            store_date_query = "s.assumed_opened_date > ? and s.assumed_opened_date <= ?"
            stores_date_param_1 = previous_time_period
            stores_date_param_2 = current_time_period
            competition_date_param_1 = current_time_period
            competition_date_param_2 = current_time_period

        elif churn_type == "closings" and previous_time_period:

            # for closings, make sure the store closed between the previous time period and this time period
            # and that we show competition from the previous period (when it was open)
            store_date_query = "s.assumed_closed_date > ? and s.assumed_closed_date <= ?"
            stores_date_param_1 = previous_time_period
            stores_date_param_2 = current_time_period
            competition_date_param_1 = previous_time_period
            competition_date_param_2 = previous_time_period

        elif churn_type in ["openings", "closings"] and previous_time_period is None:
            return []

        else:
            raise Exception("Incorrect churn type.")

        # define the query
        query = """

        -- create temp table for demographics, which we'll join multiple times
        create table #trade_area_demographics (company_id int, company_name nvarchar(255), trade_area_threshold varchar(50),data_item_id int, demographic_description varchar(255), demographic_name varchar(255), value decimal(21, 5), value_competition_adjusted decimal(21, 5), comp_count_plus_one int)

        -- cte for competition counts
        ;with trade_area_competition(trade_area_id, comp_count_plus_one) as
        (	
            select 
                t.trade_area_id,
                -- cast as float for floating point math
                -- add one to make it include the home trade area (for normalization)
		        cast(sum(isnull(cc.competition_strength, 0)) as float) + 1
            from trade_areas t
            -- left join to account for monopolies
            left join competitive_stores cs on cs.trade_area_id = t.trade_area_id and cs.start_date <= ? and (cs.end_date is null or cs.end_date > ?)
	        left join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
            group by t.trade_area_id
        )

        -- insert into the temp table
        insert into #trade_area_demographics (company_id, company_name, trade_area_threshold, data_item_id, demographic_description, demographic_name, value, value_competition_adjusted, comp_count_plus_one)
        select
            c.company_id,
            c.name as company_name,
            th.label as trade_area_threshold,
            di.data_item_id,
            di.description as demographic_description,
            di.name as demographic_name,
            d.value,
            d.value / comp.comp_count_plus_one as value_competition_adjusted,
            comp.comp_count_plus_one as comp_count_plus_one
        from companies c
        inner join stores s on s.company_id = c.company_id
        inner join trade_areas t on t.store_id = s.store_id
        inner join thresholds th on th.threshold_id = t.threshold_id
        inner join demographic_numvalues d on d.trade_area_id = t.trade_area_id
        inner join data_items di on di.data_item_id = d.data_item_id
        inner join trade_area_competition comp on comp.trade_area_id = t.trade_area_id
        where d.data_item_id > 10
            and %s
        
        
        select
            main.company_id,
            main.company_name,
            main.trade_area_threshold,
            main.data_item_id,
            main.demographic_description,
            main.demographic_name,
            isnull(main.avg, 0) as avg,
            isnull(median.median_value, 0) as med,
            isnull(main.min, 0) as min,
            isnull(main.max, 0) as max,
            isnull(main.stdev, 0) as stdev,
            isnull(main.avg_competition_adjusted, 0) as avg_competition_adjusted,
            isnull(median_competition_adjusted.median_value, 0) as med_competition_adjusted,
            isnull(main.min_competition_adjusted, 0) as min_competition_adjusted,
            isnull(main.max_competition_adjusted, 0) as max_competition_adjusted,
            isnull(main.stdev_competition_adjusted, 0) as stdev_competition_adjusted
        from
        (
            select
                dems.company_id,
                dems.company_name,
                dems.trade_area_threshold,
                dems.data_item_id,
                dems.demographic_description,
                dems.demographic_name,
                avg(dems.value) as avg,
                min(dems.value) as min,
                max(dems.value) as max,
                stdev(dems.value) as stdev,
                avg(dems.value_competition_adjusted) as avg_competition_adjusted,
                min(dems.value_competition_adjusted) as min_competition_adjusted,
                max(dems.value_competition_adjusted) as max_competition_adjusted,
                stdev(dems.value_competition_adjusted) as stdev_competition_adjusted
            from #trade_area_demographics dems
            group by dems.company_id, dems.company_name, dems.trade_area_threshold, dems.data_item_id, dems.demographic_description, dems.demographic_name
        ) main
        -- calculate median
        inner join
        (
            select 
                company_id,
                trade_area_threshold,
                data_item_id,
                AVG(value) as median_value
            from
            (
                select 
                    company_id,
                    trade_area_threshold,
                    data_item_id,
                    value,
                    ROW_NUMBER() over( partition by company_id, trade_area_threshold, data_item_id order by value asc) as row_num,
                    count(*) over (partition by company_id, trade_area_threshold, data_item_id) as count
                from #trade_area_demographics
            ) t
            where row_num in (count / 2 + 1, (count + 1) / 2)
            group by company_id, trade_area_threshold, data_item_id
        ) median on median.company_id = main.company_id and median.trade_area_threshold = main.trade_area_threshold 
            and median.data_item_id = main.data_item_id

        -- calculate median for competition adjusted
        inner join
        (
            select 
                company_id,
                trade_area_threshold,
                data_item_id,
                AVG(value) as median_value
            from
            (
                select 
                    company_id,
                    trade_area_threshold,
                    data_item_id,
                    value / comp_count_plus_one as value,
                    ROW_NUMBER() over( partition by company_id, trade_area_threshold, data_item_id order by value / comp_count_plus_one asc) as row_num,
                    count(*) over (partition by company_id, trade_area_threshold, data_item_id) as count
                from #trade_area_demographics
            ) t
            where row_num in (count / 2 + 1, (count + 1) / 2)
            group by company_id, trade_area_threshold, data_item_id
        ) median_competition_adjusted on median_competition_adjusted.company_id = main.company_id and median_competition_adjusted.trade_area_threshold = main.trade_area_threshold 
            and median_competition_adjusted.data_item_id = main.data_item_id

        -- drop the temp table
        drop table #trade_area_demographics
        """ % store_date_query

        return sql_execute_with_parameters([competition_date_param_1, competition_date_param_2, stores_date_param_1, stores_date_param_2], query)




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
    report = CustomAnalyticsDemographicsAggregateReport(time_periods)

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