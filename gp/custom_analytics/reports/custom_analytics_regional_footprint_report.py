import datetime
from itertools import groupby
from common.utilities.misc_utilities import convert_entity_list_to_dictionary, DataAccessNamedRow
from common.utilities.sql import sql_execute_with_parameters, sql_execute
from geoprocessing.custom_analytics.reports.base_custom_analytics_report import BaseCustomAnalyticsReport
from geoprocessing.data_access.data_access_utilities import escape_string_clean_up, escape_date_clean_up
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies

__author__ = 'erezrubinstein'



class CustomAnalyticsRegionalFootprintReport(BaseCustomAnalyticsReport):


    # ------------------ Implementation of the Template Methods ------------------ #

    def _get_table_name(self):
        return None


    def _get_excel_workbook_name(self):
        return "Regional Footprint"


    def _run_main_query(self):

        results = {
            "data": {},
            "regions": self._get_all_regions_and_divisions(),
            "company_names": self._get_all_companies(),
            "cbsas": self._get_all_cbsas(),
            "counties": self._get_all_counties()
        }

        # run for every time period
        for index, time_period in enumerate(self._time_periods):

            # get cohort details
            time_period_label = time_period["label"]
            time_period_date = time_period["date"]

            # get the previous cohort date (if it exists).  This is for figuring out openings/closings
            previous_cohort_date = self._time_periods[index - 1]["date"] if index > 0 else None

            # run query for every cohort/time_period
            results["data"][time_period_label] = {
                "all": self._run_time_period_query(time_period_date, previous_cohort_date, "all"),
                "openings": self._run_time_period_query(time_period_date, previous_cohort_date, "openings"),
                "closings": self._run_time_period_query(time_period_date, previous_cohort_date, "closings")
            }

        return results


    def _get_excel_data_sets(self, db_results):

        # define data sets
        data_sets = []

        # get the time period keys, and sort them by time period (assume time period is of "t#" format)
        time_period_keys = db_results["data"].keys()
        time_period_keys = sorted(time_period_keys, key = lambda tp: int(tp[1:])) # tp, hahahahahahaha

        # group the data by each churn_type/cohort so that we can create a tab for each
        for time_period in time_period_keys:

            # get the cohorts and sort them
            cohorts = sorted(db_results["data"][time_period].keys())

            # cycle through all, openings, closings
            for cohort in cohorts:

                # get the sql rows
                sql_rows = db_results["data"][time_period][cohort]

                # only continue if there are indeed rows here
                if sql_rows:

                    # create pretty names for the detail/summary tabs
                    detail_tab_name = " - ".join([time_period, cohort.replace("_", " "), "detail"])
                    regional_summary_tab_name = " - ".join([time_period, cohort.replace("_", " "), "region summary"])
                    cbsa_summary_tab_name = " - ".join([time_period, cohort.replace("_", " "), "cbsa summary"])
                    county_summary_tab_name = " - ".join([time_period, cohort.replace("_", " "), "county summary"])

                    # sort the rows by company, region, division, state asc
                    # for trade area, assume that the first half is a number, so split it by space and convert to an int
                    sql_rows = sorted(sql_rows, key = lambda row: (row.company_name, row.region, row.division, row.state))

                    # create the detail data set
                    data_sets.append({
                        "headers": ["Banner Name", "Street Number", "Street", "City", "State", "Zip Code", "Region", "Division", "CBSA", "County", "Community Code", "Community Description"],
                        "label": detail_tab_name,
                        "rows": [
                            {
                                "Banner Name": sql_row.company_name,
                                "Street Number": sql_row.street_number,
                                "Street": sql_row.street,
                                "City": sql_row.city,
                                "State": sql_row.state,
                                "Zip Code": sql_row.zip_code,
                                "Region": sql_row.region,
                                "Division": sql_row.division,
                                "CBSA": sql_row.cbsa,
                                "County": sql_row.county,
                                "Community Code": self._convert_to_int_if_int(sql_row.community_code),
                                "Community Description": sql_row.community_description
                            }
                            for sql_row in sql_rows
                        ]
                    })

                    # extra columns for cbsa, county
                    cbsa_extra_columns = [
                        { "field": "population", "label": "Population" },
                        { "field": "pci", "label": "Per Capita Income"},
                        { "field": "agg_income", "label": "Aggregate Income" }
                    ]
                    county_extra_columns = [
                        { "field": "community_code", "label": "Community Code" },
                        { "field": "community_description", "label": "Community Description" },
                        { "field": "population", "label": "Population" },
                        { "field": "pci", "label": "Per Capita Income"},
                        { "field": "agg_income", "label": "Aggregate Income" }
                    ]

                    # create the summary and add it as a data set
                    data_sets.append(self._get_region_division_summary(sql_rows, regional_summary_tab_name, db_results["regions"], db_results["company_names"]))
                    data_sets.append(self._get_generic_regional_summary(sql_rows, "cbsa", cbsa_summary_tab_name, "CBSA Name", db_results["cbsas"], db_results["company_names"], cbsa_extra_columns))
                    data_sets.append(self._get_generic_regional_summary(sql_rows, "county", county_summary_tab_name, "County Name", db_results["counties"], db_results["company_names"], county_extra_columns))

        # booyakasha
        return data_sets


    # ----------------------------- Private Helpers ------------------------------ #

    def _convert_to_int_if_int(self, string):

        # voila
        try:
            return int(string)
        except:
            return string


    def _get_region_division_summary(self, sql_rows, summary_tab_name, all_regions, all_company_names):

        # create a dictionary of all company names
        company_names_left = { row.company_name: 1 for row in all_company_names }

        # crete the headers (which will be used for the summary and summary percent data sets)
        # two headers, regions first, then divisions
        headers = [
            [""] + [row.region for row in all_regions] + [""],
            ["Banner Name"] + [row.division for row in all_regions] + ["Total"]
        ]

        # create a summary report, which grouped by region, division
        summary_data_set = {
            "header": "Store Counts",
            "headers": headers,
            "rows": []
        }

        summary_percent_data_set = {# two headers, regions first, then divisions
            "header": "Percent of Total Stores",
            "headers": headers,
            "rows": []
        }

        # first sort by region, division so that we can group by them
        sql_rows = sorted(sql_rows, key = lambda row: row.company_name)

        # go company by company
        for company_name, stores in groupby(sql_rows, key = lambda row: row.company_name):

            # each company will be one row.  So create the base row with a zero for every region
            # create the base row, which is region, division, company name mapped to 0
            row = { sql_row.division: 0 for sql_row in all_regions }
            row["Banner Name"] = company_name
            row["Total"] = 0

            # remove company name from the dict
            del company_names_left[company_name]

            # sort stores by divisions so that they can group correctly
            stores = sorted(stores, key = lambda row: row.division)

            # run a grouped query by region/division
            for division, stores_in_region in groupby(stores, key = lambda row: row.division):

                # get the store count in this division
                store_count = len(list(stores_in_region))

                # set the store count for division and increment the total
                row[division] = store_count
                row["Total"] += store_count

            # once I finished creating the entire row for the company, calculate the percent row
            percent_row = {
                sql_row.division: self._get_percent_of(row[sql_row.division], row["Total"])
                for sql_row in all_regions
            }
            percent_row["Banner Name"] = company_name
            percent_row["Total"] = self._get_percent_of(row["Total"], row["Total"])

            # add the row to the data set
            summary_data_set["rows"].append(row)
            summary_percent_data_set["rows"].append(percent_row)


        # any company that had no stores, should be added with zeros
        for company_name in company_names_left:
            row = { row.division: 0 for row in all_regions }
            row["Banner Name"] = company_name
            row["Total"] = 0

            # add this row to both the summary and percent data sets
            summary_data_set["rows"].append(row)
            summary_percent_data_set["rows"].append(row)

        # make sure to re-sort everything by company name since we could have added some with zeros after the fact
        summary_data_set["rows"] = sorted(summary_data_set["rows"], key = lambda row: row["Banner Name"])
        summary_percent_data_set["rows"] = sorted(summary_percent_data_set["rows"], key = lambda row: row["Banner Name"])

        # return a multi data set which contains the raw numbers and percentages
        return {
            "label": summary_tab_name,
            "type": "multi_table",
            "tables": [
                summary_data_set,
                summary_percent_data_set
            ]
        }


    def _get_generic_regional_summary(self, sql_rows, sql_property_name, summary_tab_name, region_header_name, all_regions, all_company_names, other_region_fields = None):

        # create a dictionary of all cbsa names, so we can add the ones that aren't part of this set
        regions_left = convert_entity_list_to_dictionary(all_regions, lambda region: region.region_name)

        # add N/A with all the oter region fields
        n_a_fields = { field["field"]: "N/A" for field in other_region_fields } if other_region_fields else {}
        regions_left["N/A"] = DataAccessNamedRow(**n_a_fields)

        # create the headers, which are all the company names
        other_region_field_headers = [field["label"] for field in other_region_fields] if other_region_fields else []
        headers = [region_header_name] + other_region_field_headers + [row.company_name for row in all_company_names] + ["Total"]

        # create a summary data set and a percent data set
        summary_data_set = {
            "header": "Store Counts",
            "headers": headers,
            "headers_format": "vertical",
            # ignore the vertical for format for the region name and other field headers that are non companies
            "headers_indexes_to_ignore_format": [i for i in range(0, len(other_region_field_headers) + 1)],
            "rows": []
        }
        summary_percent_data_set = {
            "header": "Percent of Total Stores",
            "headers_format": "vertical",
            # ignore the vertical for format for the region name and other field headers that are non companies
            "headers_indexes_to_ignore_format": [i for i in range(0, len(other_region_field_headers) + 1)],
            "headers": headers,
            "rows": []
        }

        # create total rows for both data sets
        total_row = { row.company_name: 0 for row in all_company_names }
        total_row_percent = { row.company_name: 100 for row in all_company_names }
        total_row[region_header_name] = "Total"
        total_row_percent[region_header_name] = "Total"
        total_row["Total"] = 0
        total_row_percent["Total"] = 100
        total_row["meta"] = { "bold": True }
        total_row_percent["meta"] = { "bold": True }


        # first sort by cbsa, so that we can group properly
        sql_rows = sorted(sql_rows, key = lambda row: getattr(row, sql_property_name))

        # go company by cbsa
        for region_name, stores in groupby(sql_rows, key = lambda row: getattr(row, sql_property_name)):

            # get the region object
            region_object = regions_left[region_name]

            # delete this region from the ones left so that we know we already added it
            del regions_left[region_name]

            # add an empty record first
            row = { row.company_name: 0 for row in all_company_names }
            row[region_header_name] = region_name
            row["Total"] = 0

            # loop through every store adding one for that company
            for store in stores:
                row[store.company_name] += 1
                row["Total"] += 1

                # add to the total row
                total_row[store.company_name] += 1
                total_row["Total"] += 1

            # create the base percent row for this region, which includes just the raw number.
            percent_row = {
                company_row.company_name: row[company_row.company_name]
                for company_row in all_company_names
            }
            percent_row[region_header_name] = region_name
            percent_row["Total"] = row["Total"]

            # add any other fields, if there are any
            if other_region_fields:
                for field in other_region_fields:
                    row[field["label"]] = getattr(region_object, field["field"])
                    percent_row[field["label"]] = getattr(region_object, field["field"])
                    total_row[field["label"]] = "N/A"
                    total_row_percent[field["label"]] = "N/A"

            # add the row to the data set
            summary_data_set["rows"].append(row)
            summary_percent_data_set["rows"].append(percent_row)

        # finalize the percent rows, by dividing the raw number per company by all the stores in that company
        for row in summary_percent_data_set["rows"]:

            # calculate % for every company
            for company_row in all_company_names:
                row[company_row.company_name] = self._get_percent_of(row[company_row.company_name], total_row[company_row.company_name])

            # get the total for this region compared with all the stores
            row["Total"] = self._get_percent_of(row["Total"], total_row["Total"])

        # any cbsa that had no stores, should be added with zeros
        for region_name in regions_left:
            row = { row.company_name: 0 for row in all_company_names }
            row[region_header_name] = region_name
            row["Total"] = 0

            # add any other fields, if there are any
            if other_region_fields:
                region_object = regions_left[region_name]
                for field in other_region_fields:
                    row[field["label"]] = getattr(region_object, field["field"])

            # append the row
            summary_data_set["rows"].append(row)
            summary_percent_data_set["rows"].append(row)

        # sort the rows again to account for cbsas that were added just before
        summary_data_set["rows"] = sorted(summary_data_set["rows"], key = lambda row: row[region_header_name])
        summary_percent_data_set["rows"] = sorted(summary_percent_data_set["rows"], key = lambda row: row[region_header_name])

        # add the total rows after everything is sorted
        summary_data_set["rows"].append(total_row)
        summary_percent_data_set["rows"].append(total_row_percent)

        return {
            "label": summary_tab_name,
            "type": "multi_table",
            "tables": [
                summary_data_set,
                summary_percent_data_set
            ]
        }

    def _get_percent_of(self, value, total):

        if total:
            return self._round((value / float(total)) * 100)

        else:
            return 0

    def _run_time_period_query(self, current_time_period, previous_time_period, cohort_type):

        # define some dynamic filters to deal with openings/closings.
        if cohort_type == "all":

            # for all stores, just make sure the stores are active within this point
            date_query = "s.assumed_opened_date <= ? and (s.assumed_closed_date is null or s.assumed_closed_date > ?)"
            date_param_1 = current_time_period
            date_param_2 = current_time_period

        elif cohort_type == "openings" and previous_time_period:

            # for openings, make sure the store opened between the previous time period and this time period
            # show competition from this period
            date_query = "s.assumed_opened_date > ? and s.assumed_opened_date <= ?"
            date_param_1 = previous_time_period
            date_param_2 = current_time_period

        elif cohort_type == "closings" and previous_time_period:

            # for closings, make sure the store closed between the previous time period and this time period
            # and that we show competition from the previous period (when it was open)
            date_query = "s.assumed_closed_date > ? and s.assumed_closed_date <= ?"
            date_param_1 = previous_time_period
            date_param_2 = current_time_period

        elif cohort_type in ["openings", "closings"] and previous_time_period is None:
            return []

        else:
            raise Exception("Incorrect churn type.")

        # for each company, select the competition ratio
        query = """
        select
            c.company_id,
            c.name as company_name,
            store_id,
            a.street_number,
            a.street,
            a.municipality as city,
            a.governing_district as state,
            a.postal_area as zip_code,
            g.region as region,
            g.division as division,
            isnull(cb.name, 'N/A') as cbsa,
            -- add state to county, if not null
            case
                when cou.name is null then 'N/A'
                else cou.name + ', ' + cou.state
            end as county,
            isnull(cast(cou.community_code as nvarchar(5)), 'N/A') as community_code,
            isnull(cou.community_description, 'N/A') as community_description
        from stores s
        inner join companies c on c.company_id = s.company_id
        inner join addresses a on a.address_id = s.address_id
        inner join governing_districts g on g.governing_district = a.governing_district
        -- outer apply is key, in case something is in the middle and falls in two cbsas
        outer apply
        (
            select top 1 cbsa_id
            from cbsa_store_matches
            where store_id = s.store_id
        ) cbsa_matches
        -- outer apply is key, in case something is in the middle and falls in two couties
        outer apply
        (
            select top 1 county_id
            from county_store_matches
            where store_id = s.store_id
        ) county_matches
        left join cbsa cb on cb.cbsa_id = cbsa_matches.cbsa_id
        left join counties cou on cou.county_id = county_matches.county_id
        where %s
        """ % date_query

        return sql_execute_with_parameters([date_param_1, date_param_2], query)


    def _get_all_regions_and_divisions(self):

        sql = "select distinct region, division from governing_districts order by region, division"
        return sql_execute(sql)


    def _get_all_companies(self):

        # names should be distinct, but I'm forcing it so that we don't get any strange errors when converting to a dict.
        sql = "select distinct name as company_name from companies order by name"
        return sql_execute(sql)


    def _get_all_cbsas(self):

        # names should be distinct, but I'm forcing it so that we don't get any strange errors when converting to a dict.
        sql = "select name as region_name, population, pci, agg_income from cbsa"
        return sql_execute(sql)


    def _get_all_counties(self):

        # names should be distinct, but I'm forcing it so that we don't get any strange errors when converting to a dict.
        sql = "select name + ', ' + state as region_name, community_code, community_description, population, pci, agg_income from counties"
        return sql_execute(sql)

    def _get_store_count_per_company_name(self):
        pass




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
    report = CustomAnalyticsRegionalFootprintReport(time_periods)

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