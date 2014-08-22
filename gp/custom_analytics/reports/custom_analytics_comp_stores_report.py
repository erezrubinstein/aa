import datetime
from itertools import groupby
from common.utilities.misc_utilities import convert_entity_list_to_dictionary
from common.utilities.sql import sql_execute
from geoprocessing.custom_analytics.reports.base_custom_analytics_report import BaseCustomAnalyticsReport
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies

__author__ = 'erezrubinstein'

class CustomAnalyticsCompStoresReport(BaseCustomAnalyticsReport):

    def __init__(self, time_periods, comp_store_periods, company_definitions = None, report_name = None):

        # call the base
        super(CustomAnalyticsCompStoresReport, self).__init__(time_periods, company_definitions, report_name)

        # set up the comp store settings
        self._comp_store_periods = comp_store_periods


    # ------------------ Implementation of the Template Methods ------------------ #

    def _get_table_name(self):
        return None


    def _get_excel_workbook_name(self):
        return "Comparable Stores"


    def _run_main_query(self):

        # create a dictionary structure of the time periods
        time_periods_dict = convert_entity_list_to_dictionary(self._time_periods, key = lambda tp: tp["label"]) # tp, hahahaha

        # data structure for keep track of the raw data
        results = {
            "data": [],
            "all_companies": self._get_all_companies()
        }

        # loop through every comp store period
        for cpp in self._comp_store_periods:

            # get dates for this period
            current_period_date = time_periods_dict[cpp["CP"]]["date"]
            prior_period_date = time_periods_dict[cpp["PP"]]["date"]
            prior_year_date = time_periods_dict[cpp["PY"]]["date"]

            results["data"].append(self._run_queries(current_period_date, prior_period_date, prior_year_date))

        return results


    def _get_excel_data_sets(self, db_results):

        # extract data from results
        main_data = db_results["data"]
        all_companies = db_results["all_companies"]

        # define empty data sets
        data_sets = [

            # comp store period definitions
            self._create_comp_store_period_definition_report(),

            # comp store counts report
            self._create_comp_store_counts_report(main_data, all_companies),

            # competitor competition ration report,
            self._create_competitor_competition_ratio_report(main_data, all_companies),

            # percent of comp stores that have competition net openings
            self._create_comp_stores_with_competition_net_openings_report(main_data, all_companies),

            # all comp stores
            self._create_all_raw_comp_stores_report(main_data, all_companies),

            # percent of comp stores that have competition net openings
            self._create_raw_stores_with_net_openings_report(main_data),

            # create the ccr attribution report
            self._create_ccr_attribution_report(main_data)
        ]

        # return the data sets
        return data_sets



    def _create_comp_store_period_definition_report(self):

        headers = ["Period", "Current Period (CP)", "Prior Period (PP)", "Prior Year (PY)"]

        # create the base rows
        rows = []

        # create the time period parts
        for index, period in enumerate(self._comp_store_periods):

            # create the period
            period = "Period %i" % index

            # add the values for this period
            rows.append({
                "Period": period,
                "Current Period (CP)": self._comp_store_periods[index]["CP"],
                "Prior Period (PP)": self._comp_store_periods[index]["PP"],
                "Prior Year (PY)": self._comp_store_periods[index]["PY"]
            })

        return {
            "headers": headers,
            "label": "Comparable Stores Settings",
            "rows": rows,
            "description": "Comparable Stores Report Settings"
        }


    # ----------------------------- Report Formatting ----------------------------- #

    def _create_comp_store_counts_report(self, main_data, all_companies):

        # create the headers dynamically based on how many comp store periods we have
        headers = ["Company Name"] + ["Period %i" % index for index in range(0, len(self._comp_store_periods))]

        # create a dict to hold company name and values for every period
        company_comp_store_counts = self._create_default_company_dict(all_companies, headers[1:])

        # loop through results (one for each time period)
        for index, time_period_results in enumerate(main_data):

            # create period
            period = "Period %i" % index

            # loop through results and fill in store count for every company
            for sql_row in time_period_results["comp_store_counts"]:
                company_comp_store_counts[sql_row.company_name][period] = sql_row.store_count

        # convert dict into rows
        rows = self._convert_company_value_dict_to_rows_and_sort(company_comp_store_counts)

        return {
            "headers": headers,
            "label": "Comparable Store Counts",
            "rows": rows
        }


    def _create_competitor_competition_ratio_report(self, main_data, all_companies):

        # create common headers for the sub tables
        headers = [
            ["", "N/A"] + ["Current Period"] * 3 + ["Prior Period"] * 3 + ["Prior Year"] * 3 + ["N/A"],
            ["Company Name", "Comp Store Count"] + ["Comp Instances", "Comp Ratio", "% Store Base Affected"] * 3 + ["CCR Growth Rate"]
        ]

        comments_per_index = [
            {},
            {
                1: "Number of comparable stores for this period",
                2: "Number of competitive instances (excluding same company stores) for the current period",
                3: "Ratio of current period Comp Instances divided by the Comp Store Count",
                4: "Percentage of the comparable stores for this period that have at least one current period competitive instance",
                5: "Number of competitive instances (excluding same company stores) for the prior period",
                6: "Ratio of prior period Comp Instances divided by the Comp Store Count",
                7: "Percentage of the comparable stores for this period that have at least one prior period competitive instance",
                8: "Number of competitive instances (excluding same company stores) for the prior year",
                9: "Ratio of prior year Comp Instances divided by the Comp Store Count",
                10: "Percentage of the comparable stores for this period that have at least one prior year competitive instance",
                11: "Percent growth of the current period competitive instances compared to the prior period's competitive instances"
            }
        ]

        # create a header mapping to make non-unique headers into unique ones
        unique_headers_mapping = ["Company Name", "store_count",
                                  "cp_comp_instances", "cp_comp_ratio", "cp_store_base_affected",
                                  "pp_comp_instances", "pp_comp_ratio", "pp_store_base_affected",
                                  "py_comp_instances", "py_comp_ratio", "py_store_base_affected",
                                  "ccr_growth_rate"]

        # create the tables array
        tables = []

        # loop through results, setting values
        for index, time_period_results in enumerate(main_data):

            # convert the store counts data set into a dict for easy lookups
            store_counts_dict = convert_entity_list_to_dictionary(time_period_results["comp_store_counts"], key = lambda sql_row: sql_row.company_name)

            # sort by trade area and then group by it.  sort by the number part of trade area
            sorted_competition_results = sorted(time_period_results["competitor_competition_instances"], key = lambda sql_row: float(sql_row.trade_area.split(" ")[0]))
            for trade_area, sql_rows in groupby(sorted_competition_results, key = lambda sql_row: sql_row.trade_area):

                # create the default dictionary of all companies to 0 records for every period
                company_comp_ratios = self._create_default_company_dict(all_companies, unique_headers_mapping[1:])

                # loop through results and fill in store count for every company
                for sql_row in sql_rows:

                    # get the store_counts for this company
                    store_counts = store_counts_dict[sql_row.company_name].store_count

                    # set the store count for this period
                    company_comp_ratios[sql_row.company_name]["store_count"] = store_counts

                    # set the comp instances
                    company_comp_ratios[sql_row.company_name]["cp_comp_instances"] = sql_row.cci_cp
                    company_comp_ratios[sql_row.company_name]["pp_comp_instances"] = sql_row.cci_pp
                    company_comp_ratios[sql_row.company_name]["py_comp_instances"] = sql_row.cci_py

                    # set the comp ratios
                    cp_ccr = self._get_ratio(sql_row.cci_cp, store_counts)
                    py_ccr = self._get_ratio(sql_row.cci_py, store_counts)
                    company_comp_ratios[sql_row.company_name]["cp_comp_ratio"] = cp_ccr
                    company_comp_ratios[sql_row.company_name]["pp_comp_ratio"] = self._get_ratio(sql_row.cci_pp, store_counts)
                    company_comp_ratios[sql_row.company_name]["py_comp_ratio"] = py_ccr

                    # set the % store base affected
                    company_comp_ratios[sql_row.company_name]["cp_store_base_affected"] = self._get_ratio(sql_row.home_stores_affected_cp, store_counts, 100)
                    company_comp_ratios[sql_row.company_name]["pp_store_base_affected"] = self._get_ratio(sql_row.home_stores_affected_pp, store_counts, 100)
                    company_comp_ratios[sql_row.company_name]["py_store_base_affected"] = self._get_ratio(sql_row.home_stores_affected_py, store_counts, 100)

                    # set the growth rate
                    company_comp_ratios[sql_row.company_name]["ccr_growth_rate"] = self._get_percent_of(cp_ccr, py_ccr)


                # convert dict into rows
                rows = self._convert_company_value_dict_to_rows_and_sort(company_comp_ratios)

                # append the period to the tables
                tables.append({
                    "header": "Period %i - %s Trade Area" % (index, trade_area),
                    "unique_headers_mapping": unique_headers_mapping,
                    "headers_comments_per_index": comments_per_index,
                    "headers": headers,
                    "rows": rows
                })

        # return the data set
        return {
            "label": "Competitor Competition Ratio",
            "type": "multi_table",
            "tables": tables
        }


    def _create_comp_stores_with_competition_net_openings_report(self, main_data, all_companies):

        # three headers with periods on top
        # base header below
        headers = [
            ["", "N/A"] + ["Current Period to Prior Period"] * 2 + ["Current Period to Prior Year"] * 2,
            ["Company Name", "Store Counts"] + ["Stores w/ Net Competitive Openings", "% w/ Net Competitive Openings"] * 2
        ]

        # create a header mapping to make non-unique headers into unique ones
        unique_headers_mapping = ["Company Name", "store_count", "cp_to_pp_store_count", "cp_to_pp_ratio", "cp_to_py_store_count", "cp_to_py_ratio"]

        # comments per index
        comments_per_index = [
            {},
            {
                1: "Number of comparable stores for this period",
                2: "Number of stores with at least one competitive opening (excluding same company stores) between the prior period and the current period",
                3: "Percent of stores with at least one competitive opening (excluding same company stores) between the prior period and the current period",
                4: "Number of stores with at least one competitive opening (excluding same company stores) between the prior year and the current period",
                5: "Percent of stores with at least one competitive opening (excluding same company stores) between the prior year and the current period",
            }
        ]

        # create the tables array
        tables = []

        # loop through results, setting values
        for index, time_period_results in enumerate(main_data):

            # create the default dictionary of all companies to 0 records for every period
            company_data_dict = self._create_default_company_dict(all_companies, unique_headers_mapping[1:])

            # sort by trade area and then group by it.  sort by the number part of trade area
            sorted_results = sorted(time_period_results["store_counts_with_cci_openings"], key = lambda sql_row: float(sql_row.trade_area.split(" ")[0]))
            for trade_area, sql_rows in groupby(sorted_results, key = lambda sql_row: sql_row.trade_area):

                # convert the store counts data set into a dict for easy lookups
                store_counts_dict = convert_entity_list_to_dictionary(time_period_results["comp_store_counts"], key = lambda sql_row: sql_row.company_name)

                # loop through results and fill in store count for every company
                for sql_row in sql_rows:

                    # get the store_counts for this company
                    store_counts = store_counts_dict[sql_row.company_name].store_count

                    # set the store count for this period
                    company_data_dict[sql_row.company_name]["store_count"] = store_counts

                    # set cp to pp
                    company_data_dict[sql_row.company_name]["cp_to_pp_store_count"] = sql_row.cci_net_openings_cp_to_pp
                    company_data_dict[sql_row.company_name]["cp_to_pp_ratio"] = self._get_ratio(sql_row.cci_net_openings_cp_to_pp, store_counts, 100)

                    # set cp to py
                    company_data_dict[sql_row.company_name]["cp_to_py_store_count"] = sql_row.cci_net_openings_cp_to_py
                    company_data_dict[sql_row.company_name]["cp_to_py_ratio"] = self._get_ratio(sql_row.cci_net_openings_cp_to_py, store_counts, 100)

                # convert dict into rows
                rows = self._convert_company_value_dict_to_rows_and_sort(company_data_dict)

                # append the period to the tables
                tables.append({
                    "header": "Period %i - %s Trade Area" % (index, trade_area),
                    "unique_headers_mapping": unique_headers_mapping,
                    "headers_comments_per_index": comments_per_index,
                    "headers": headers,
                    "rows": rows
                })

        # return the data set
        return {
            "label": "Pct With Net Comp Openings",
            "type": "multi_table",
            "tables": tables,
            "description": "Percent of Stores with Net Competition Openings"
        }


    def _create_all_raw_comp_stores_report(self, main_data, all_companies):

        # create headers
        headers = ["Company Name", "Address", "City", "State", "Zip"]

        # create the tables array
        tables = []

        # loop through results, setting values
        for index, time_period_results in enumerate(main_data):

            rows = []

            # loop through results and fill in store count for every company
            for sql_row in time_period_results["raw_comp_stores"]:

                # set the data
                rows.append({
                    "Company Name": sql_row.company_name,
                    "Address": sql_row.address,
                    "City": sql_row.city,
                    "State": sql_row.state,
                    "Zip": sql_row.zip
                })

            # append the period to the tables
            tables.append({
                "header": "Period %i" % index,
                "headers": headers,
                "rows": rows
            })

        # return the data set
        return {
            "label": "All Comparable Stores",
            "type": "multi_table",
            "tables": tables
        }



    def _create_raw_stores_with_net_openings_report(self, main_data):

        # create headers
        headers = ["Company Name", "Address", "City", "State", "Zip", "Net Competition Openings Current Period to Prior Period", "Net Competition Openings Current Period to Prior Year"]

        # create the tables array
        tables = []

        # comments per index
        headers_comments =  {
            "Net Competition Openings Current Period to Prior Period": "Net competition openings (openings - closings) for this store in between the prior period and the current period",
            "Net Competition Openings Current Period to Prior Year": "Net competition openings (openings - closings) for this store in between the prior year and the current period"
        }

        # loop through results, setting values
        for index, time_period_results in enumerate(main_data):

            # sort by trade area and then group by it.  sort by the number part of trade area
            sorted_results = sorted(time_period_results["raw_stores_with_cci_openings"], key = lambda sql_row: float(sql_row.trade_area.split(" ")[0]))
            for trade_area, sql_rows in groupby(sorted_results, key = lambda sql_row: sql_row.trade_area):

                rows = []

                # loop through results and fill in store count for every company
                for sql_row in sql_rows:

                    # set the data
                    rows.append({
                        "Company Name": sql_row.company_name,
                        "Address": sql_row.address,
                        "City": sql_row.city,
                        "State": sql_row.state,
                        "Zip": sql_row.zip,
                        "Net Competition Openings Current Period to Prior Period": sql_row.cci_net_openings_cp_to_pp,
                        "Net Competition Openings Current Period to Prior Year": sql_row.cci_net_openings_cp_to_py,
                    })

                # append the period to the tables
                tables.append({
                    "header": "Period %i - %s Trade Area" % (index, trade_area),
                    "headers_comments": headers_comments,
                    "headers": headers,
                    "rows": rows
                })

        # return the data set
        return {
            "label": "Stores Net Comp Openings",
            "type": "multi_table",
            "tables": tables,
            "description": "All Stores with Net Competition Openings"
        }


    def _create_ccr_attribution_report(self, main_data):

        # create common headers for the sub tables
        headers = [
            ["", "", "N/A"] + ["Current Period"] * 3 + ["Prior Period"] * 3 + ["Prior Year"] * 3 + ["N/A"],
            ["Home Company", "Away Company", "Home Store Count"] + ["Comp Instances", "Comp Ratio", "% Store Base Affected"] * 3 + ["CCR Growth Rate"]
        ]

        # create a header mapping to make non-unique headers into unique ones
        unique_headers_mapping = ["Home Company", "Away Company", "store_count",
                                  "cp_comp_instances", "cp_comp_ratio", "cp_store_base_affected",
                                  "pp_comp_instances", "pp_comp_ratio", "pp_store_base_affected",
                                  "py_comp_instances", "py_comp_ratio", "py_store_base_affected",
                                  "ccr_growth_rate"]

        # comments per index
        comments_per_index = [
            {},
            {
                2: "Number of comparable stores for this period (for the home company)",
                3: "Number of competitive instances (excluding same company stores) for the current period",
                4: "Ratio of current period Comp Instances divided by the Comp Store Count",
                5: "Percentage of the comparable stores for this period that have at least one current period competitive instance",
                6: "Number of competitive instances (excluding same company stores) for the prior period",
                7: "Ratio of prior period Comp Instances divided by the Comp Store Count",
                8: "Percentage of the comparable stores for this period that have at least one prior period competitive instance",
                9: "Number of competitive instances (excluding same company stores) for the prior year",
                10: "Ratio of prior year Comp Instances divided by the Comp Store Count",
                11: "Percentage of the comparable stores for this period that have at least one prior year competitive instance",
                12: "Percent growth of the current period competitive instances compared to the prior period's competitive instances"
            }
        ]

        # create the tables array
        tables = []

        # loop through results, setting values
        for index, time_period_results in enumerate(main_data):

            # convert the store counts data set into a dict for easy lookups
            store_counts_dict = convert_entity_list_to_dictionary(time_period_results["comp_store_counts"], key = lambda sql_row: sql_row.company_name)

            # sort by trade area and then group by it.  sort by the number part of trade area
            sorted_competition_results = sorted(time_period_results["ccr_attribution"], key = lambda sql_row: float(sql_row.trade_area.split(" ")[0]))
            for trade_area, sql_rows in groupby(sorted_competition_results, key = lambda sql_row: sql_row.trade_area):

                rows = []

                # loop through results and fill in store count for every company
                for sql_row in sql_rows:

                    # get the store_counts for this company
                    store_counts = store_counts_dict[sql_row.home_company].store_count
                    cp_ccr = self._get_ratio(sql_row.cci_cp, store_counts)
                    py_ccr = self._get_ratio(sql_row.cci_py, store_counts)

                    # append the row
                    rows.append({
                        "Home Company": sql_row.home_company,
                        "Away Company": sql_row.away_company,
                        "store_count": store_counts,
                        "cp_comp_instances": sql_row.cci_cp,
                        "pp_comp_instances": sql_row.cci_pp,
                        "py_comp_instances": sql_row.cci_py,
                        "cp_comp_ratio": cp_ccr,
                        "pp_comp_ratio": self._get_ratio(sql_row.cci_pp, store_counts),
                        "py_comp_ratio": py_ccr,
                        "cp_store_base_affected": self._get_ratio(sql_row.home_stores_affected_cp, store_counts, 100),
                        "pp_store_base_affected": self._get_ratio(sql_row.home_stores_affected_pp, store_counts, 100),
                        "py_store_base_affected": self._get_ratio(sql_row.home_stores_affected_py, store_counts, 100),
                        "ccr_growth_rate": self._get_percent_of(cp_ccr, py_ccr)
                    })

                # append the period to the tables
                tables.append({
                    "header": "Period %i - %s Trade Area" % (index, trade_area),
                    "unique_headers_mapping": unique_headers_mapping,
                    "headers_comments_per_index": comments_per_index,
                    "headers": headers,
                    "rows": rows
                })

        # return the data set
        return {
            "label": "Competition Ratio Attribution",
            "type": "multi_table",
            "tables": tables
        }

    # -------------------------------- SQL Methods -------------------------------- #

    def _run_queries(self, current_period_date, prior_period_date, prior_year_date):

        # to make this run faster, I'm declaring a temp table with all the comp stores in this period.
        queries = [

            # declare temp comp store ids table
            "create table #comp_store_ids(store_id int primary key, company_id int)",

            # populate the comp store ids table
            self._populate_comp_store_ids_table(current_period_date, prior_year_date),

            # get count comp stores per company
            self._get_count_stores_per_company(),

            # get competitor competition instances (cci)
            self._get_competitor_competition_instances(current_period_date, prior_period_date, prior_year_date),

            # get stores with cci net openings
            self._get_store_counts_with_net_cci_openings(current_period_date, prior_period_date, prior_year_date),

            # get all raw comp stores
            self._get_all_raw_comp_stores(),

            # get raw list of stores with cci net openings
            self._get_raw_stores_with_net_cci_openings(current_period_date, prior_period_date, prior_year_date),

            # get ccr attribution data
            self._get_ccr_attribution(current_period_date, prior_period_date, prior_year_date),

            # drop temp table
            "drop table #comp_store_ids"
        ]

        # execute all the queries with one connection
        results = sql_execute(*queries)

        # return the results in a nice looking dict
        return {
            "comp_store_counts": results[0],
            "competitor_competition_instances": results[1],
            "store_counts_with_cci_openings": results[2],
            "raw_comp_stores": results[3],
            "raw_stores_with_cci_openings": results[4],
            "ccr_attribution": results[5]
        }


    def _populate_comp_store_ids_table(self, current_period_date, prior_year_date):
        return {
            "sql": """
            insert into #comp_store_ids (store_id, company_id)
            select s.store_id, s.company_id
            from stores s
            where
                (s.assumed_opened_date is null or s.assumed_opened_date <= ?) AND
                (s.assumed_closed_date is null or s.assumed_closed_date > ?)
            """,
            "parameters": [prior_year_date, current_period_date]
        }


    def _get_count_stores_per_company(self):

        return """
        select
            c.company_id,
            c.name as company_name,
            store_counts.count as store_count
        from companies c
        cross apply(
            select count(*) as count
            from #comp_store_ids
            where company_id = c.company_id
        ) store_counts
        order by company_name
        """


    def _get_competitor_competition_instances(self, current_period_date, prior_period_date, prior_year_date):

        return {
            "sql": """
            select
                c.name as company_name,
                th.label as trade_area,
                -- competitor competition instances (weighed)
                isnull(sum(cci_cp.count), 0) as cci_cp,
                isnull(sum(cci_pp.count), 0) as cci_pp,
                isnull(sum(cci_py.count), 0) as cci_py,
                -- home stores affected
                isnull(SUM(cci_cp.home_stores_affected), 0) as home_stores_affected_cp,
                isnull(SUM(cci_pp.home_stores_affected), 0) as home_stores_affected_pp,
                isnull(SUM(cci_py.home_stores_affected), 0) as home_stores_affected_py
            from #comp_store_ids csi
            inner join companies c on c.company_id = csi.company_id
            inner join trade_areas t on t.store_id = csi.store_id
            inner join thresholds th on th.threshold_id = t.threshold_id
            cross apply (
                select
                    SUM(cc.competition_strength) as count,
		            COUNT(distinct cs.home_store_id) as home_stores_affected
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
		            cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    (cs.start_date is null or cs.start_date <= ?) AND
                    (cs.end_date is null or cs.end_date > ?)
            ) cci_cp
            cross apply (
                select
                    SUM(cc.competition_strength) as count,
		            COUNT(distinct cs.home_store_id) as home_stores_affected
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
		            cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    (cs.start_date is null or cs.start_date <= ?) AND
                    (cs.end_date is null or cs.end_date > ?)
            ) cci_pp
            cross apply (
                select
                    SUM(cc.competition_strength) as count,
		            COUNT(distinct cs.home_store_id) as home_stores_affected
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
		            cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    (cs.start_date is null or cs.start_date <= ?) AND
                    (cs.end_date is null or cs.end_date > ?)
            ) cci_py
            group by c.name, th.label
            order by c.name, th.label
            """,
            "parameters": [current_period_date, current_period_date, prior_period_date, prior_period_date, prior_year_date, prior_year_date]
        }


    def _get_store_counts_with_net_cci_openings(self, current_period_date, prior_period_date, prior_year_date):
        return {
            "sql": """
            select
                c.name as company_name,
                th.label as trade_area,
                sum(
                    case
                        when cci_openings_cp_to_pp.count - cci_closings_cp_to_pp.count >= 1 then 1
                        else 0
                    end
                ) as cci_net_openings_cp_to_pp,
                sum(
                    case
                        when cci_openings_cp_to_py.count - cci_closings_cp_to_py.count >= 1 then 1
                        else 0
                    end
                ) as cci_net_openings_cp_to_py
            from #comp_store_ids csi
            inner join companies c on c.company_id = csi.company_id
            inner join trade_areas t on t.store_id = csi.store_id
            inner join thresholds th on th.threshold_id = t.threshold_id
            cross apply (
                select count(*) as count
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
		            cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    cs.start_date < ? AND
                    cs.start_date >= ?
            ) cci_openings_cp_to_pp
            cross apply (
                select count(*) as count
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
		            cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    cs.end_date < ? AND
                    cs.end_date >= ?
            ) cci_closings_cp_to_pp
            cross apply (
                select count(*) as count
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
		            cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    cs.start_date < ? AND
                    cs.start_date >= ?
            ) cci_openings_cp_to_py
            cross apply (
                select count(*) as count
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
		            cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    cs.end_date < ? AND
                    cs.end_date >= ?
            ) cci_closings_cp_to_py
            group by c.name, th.label
            order by c.name, th.label
            """,
            "parameters": [current_period_date, prior_period_date, current_period_date, prior_period_date, current_period_date, prior_year_date, current_period_date, prior_year_date]
        }


    def _get_all_raw_comp_stores(self):
        return """
        select
            c.name as company_name,
            isnull(a.street_number, '') + ' ' + isnull(a.street, '') as address,
            a.municipality as city,
            a.governing_district as state,
            a.postal_area as zip
        from #comp_store_ids csi
        inner join stores s on s.store_id = csi.store_id
        inner join addresses a on a.address_id = s.address_id
        inner join companies c on c.company_id = csi.company_id
        order by c.name, csi.store_id
        """


    def _get_raw_stores_with_net_cci_openings(self, current_period_date, prior_period_date, prior_year_date):
        return {
            "sql": """
            select
                c.name as company_name,
                th.label as trade_area,
                isnull(a.street_number, '') + ' ' + isnull(a.street, '') as address,
                a.municipality as city,
                a.governing_district as state,
                a.postal_area as zip,
                cci_openings_cp_to_pp.count - cci_closings_cp_to_pp.count as cci_net_openings_cp_to_pp,
                cci_openings_cp_to_py.count - cci_closings_cp_to_py.count as cci_net_openings_cp_to_py
            from #comp_store_ids csi
            inner join stores s on s.store_id = csi.store_id
            inner join addresses a on a.address_id = s.address_id
            inner join companies c on c.company_id = csi.company_id
            inner join trade_areas t on t.store_id = csi.store_id
            inner join thresholds th on th.threshold_id = t.threshold_id
            cross apply (
                select count(*) as count
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
                    cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    cs.start_date < ? AND
                    cs.start_date >= ?
            ) cci_openings_cp_to_pp
            cross apply (
                select count(*) as count
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
                    cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    cs.end_date < ? AND
                    cs.end_date >= ?
            ) cci_closings_cp_to_pp
            cross apply (
                select count(*) as count
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
                    cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    cs.start_date < ? AND
                    cs.start_date >= ?
            ) cci_openings_cp_to_py
            cross apply (
                select count(*) as count
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
                    cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id != csi.company_id AND
                    cs.end_date < ? AND
                    cs.end_date >= ?
            ) cci_closings_cp_to_py
            where cci_openings_cp_to_pp.count - cci_closings_cp_to_pp.count > 0 or
                cci_openings_cp_to_py.count - cci_closings_cp_to_py.count  > 0
            order by c.name, csi.store_id, th.label
            """,
            "parameters": [current_period_date, prior_period_date, current_period_date, prior_period_date, current_period_date, prior_year_date, current_period_date, prior_year_date]
        }


    def _get_ccr_attribution(self, current_period_date, prior_period_date, prior_year_date):
        return {
            "sql": """
            select
                c.name as home_company,
                away_c.name as away_company,
                th.label as trade_area,
                -- competitor competition instances (weighed)
                isnull(sum(cci_cp.count), 0) as cci_cp,
                isnull(sum(cci_pp.count), 0) as cci_pp,
                isnull(sum(cci_py.count), 0) as cci_py,
                ---- home stores affected
                isnull(SUM(cci_cp.home_stores_affected), 0) as home_stores_affected_cp,
                isnull(SUM(cci_pp.home_stores_affected), 0) as home_stores_affected_pp,
                isnull(SUM(cci_py.home_stores_affected), 0) as home_stores_affected_py
            from #comp_store_ids csi
            cross join companies away_c
            inner join companies c on c.company_id = csi.company_id
            inner join trade_areas t on t.store_id = csi.store_id
            inner join thresholds th on th.threshold_id = t.threshold_id
            cross apply (
                select
                    SUM(cc.competition_strength) as count,
                    COUNT(distinct cs.home_store_id) as home_stores_affected
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
                    cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id = away_c.company_id AND
                    (cs.start_date is null or cs.start_date <= ?) AND
                    (cs.end_date is null or cs.end_date > ?)
            ) cci_cp
            cross apply (
                select
                    SUM(cc.competition_strength) as count,
                    COUNT(distinct cs.home_store_id) as home_stores_affected
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
                    cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id = away_c.company_id AND
                    (cs.start_date is null or cs.start_date <= ?) AND
                    (cs.end_date is null or cs.end_date > ?)
            ) cci_pp
            cross apply (
                select
                    SUM(cc.competition_strength) as count,
                    COUNT(distinct cs.home_store_id) as home_stores_affected
                from competitive_stores cs
                inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
                where
                    cs.trade_area_id = t.trade_area_id AND
                    cc.away_company_id = away_c.company_id AND
                    (cs.start_date is null or cs.start_date <= ?) AND
                    (cs.end_date is null or cs.end_date > ?)
            ) cci_py
            -- do not include your own companies
            where c.company_id != away_c.company_id
            group by c.name, th.label, away_c.name
            order by c.name, th.label, away_c.name
            """,
            "parameters": [current_period_date, current_period_date, prior_period_date, prior_period_date, prior_year_date, prior_year_date]
        }


    def _get_all_companies(self):

        # names should be distinct, but I'm forcing it so that we don't get any strange errors when converting to a dict.
        sql = "select distinct name as company_name from companies order by name"
        return sql_execute(sql)



    # ------------------------------------ Private ------------------------------------

    def _get_ratio(self, numerator, denominator, multiply_by = 1):

        if not denominator:
            return 0

        return self._round((numerator / float(denominator)) * multiply_by)

    def _get_percent_of(self, current_value, previous_value):

        if not previous_value:
            return 0

        return self._round((current_value - previous_value) / previous_value * 100)

    def _create_default_company_dict(self, all_companies, headers_to_map, default_value = 0):

        # create a dict to hold company name and values for every period
        return {

            # create default_value for every header of every company
            company.company_name: {
                header: default_value
                for header in headers_to_map
            }
            for company in all_companies
        }

    def _convert_company_value_dict_to_rows_and_sort(self, company_to_values_dict, company_name_label = "Company Name"):

        # defaults
        rows = []

        # convert dict into rows
        for company_name, company_record in company_to_values_dict.iteritems():

            # create the base row
            row = { company_name_label: company_name }

            for header in company_record:

                # add the store counts for the period
                row[header] = company_record[header]

            # add the row
            rows.append(row)

        # sort the rows by company name
        rows = sorted(rows, key = lambda row: row[company_name_label])

        # booya
        return rows



def main():

    company_definitions = {
		"518347ea4af885658cf882aa" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-11-28T00:00:00",
				"t1": "2013-06-27T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "C. Wonder",
			"weight" : 1
		},
		"525272003f0cd228d1092401" : {
			"is_target" : True,
			"time_periods" : {
				"t0": None,
				"t1": "2013-12-31T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "C. Wonder Outlet",
			"weight" : 1
		},
		"dfaer342adsf" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-09-12T00:00:00",
				"t1": "2013-07-16T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Coach",
			"weight" : 0.7
		},

		"51e65cf95892d05bd02ff35b" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-09-12T00:00:00",
				"t1": "2013-07-16T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Coach Factory Store",
			"weight" : 0.7
		},
		"51c115865892d00e498773c9" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-09-12T00:00:00",
				"t1": "2013-07-16T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Coach Men",
			"weight" : 0.7
		},
		"51c011365892d073f4c5e074" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-09-12T00:00:00",
				"t1": "2013-07-16T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Coach Men Factory",
			"weight" : 0.7
		},
		"518194954af8850754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-09-26T00:00:00",
				"t1": "2013-07-01T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Furla",
			"weight" : 0.5
		},
        "518194954af8850754c759a" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-11-30T00:00:00",
				"t1": "2013-11-27T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Furla Outlets",
			"weight" : 0.5
		},
        "518194954af8850754c759" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-09-26T00:00:00",
				"t1": "2013-06-28T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Kate Spade",
			"weight" : 0.3
		},
        "518194954af8850754c75" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-09-26T00:00:00",
				"t1": "2013-06-28T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Kate Spade Outlet",
			"weight" : 0.3
		},
        "518194954af8850754c7" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-01-11T00:00:00",
				"t1": "2013-07-21T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "KORS-AuthDealers",
			"weight" : 0.3
		},
        "518194954af8850754" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-10-03T00:00:00",
				"t1": "2013-07-03T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Longchamp Authorized Dealers",
			"weight" : 0.3
		},
        "518194759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-09-26T00:00:00",
				"t1": "2013-06-28T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Marc By Marc Jacobs Women's Accessories",
			"weight" : 0.7
		},
        "5181949af8850754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-08-27T00:00:00",
				"t1": "2013-07-01T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Michael Kors",
			"weight" : 0.7
		},
        "5181949af80754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-08-27T00:00:00",
				"t1": "2013-07-01T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Michael Kors Outlet",
			"weight" : 0.7
		},
        "5181949a0754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-11-26T00:00:00",
				"t1": "2013-06-28T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Tory Burch",
			"weight" : 1.4
		},
        "5181949af8759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0": "2012-11-26T00:00:00",
				"t1": "2013-06-28T00:00:00",
                "t2": "2014-01-01T00:00:00",
                "t3": "2014-04-01T00:00:00"
			},
			"company_name" : "Tory Burch Outlet",
			"weight" : 1.5
		}
	}

    # create cohorts
    time_periods = [
        {
            "label": "t0",
            "date": datetime.datetime(1900, 1, 1)
        },
        {
            "label": "t1",
            "date": datetime.datetime(2013, 7, 31)
        },
        {
            "label": "t2",
            "date": datetime.datetime(2014, 1, 1)
        },
        {
            "label": "t3",
            "date": datetime.datetime(2014, 4, 1)
        }
    ]

    # create comp store periods
    comp_store_periods = [
        {
            "CP": "t2",
            "PP": "t1",
            "PY": "t0"
        },
        {
            "CP": "t3",
            "PP": "t2",
            "PY": "t1"
        }
    ]

    # create report
    report = CustomAnalyticsCompStoresReport(time_periods, comp_store_periods, company_definitions)

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