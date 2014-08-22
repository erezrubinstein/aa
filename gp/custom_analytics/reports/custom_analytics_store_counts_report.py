import datetime
from common.utilities.sql import sql_execute_with_parameters, sql_execute
from geoprocessing.custom_analytics.reports.base_custom_analytics_report import BaseCustomAnalyticsReport
from geoprocessing.data_access.data_access_utilities import escape_string_clean_up, escape_date_clean_up
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies

__author__ = 'erezrubinstein'



class CustomAnalyticsStoreCountReport(BaseCustomAnalyticsReport):


    # ------------------ Implementation of the Template Methods ------------------ #

    def _get_table_name(self):
        return None


    def _get_excel_workbook_name(self):
        return "Store Counts"


    def _run_main_query(self):

        results = {}

        # run the query for every time period
        for index, time_period in enumerate(self._time_periods):

            # get cohort details
            time_period_label = time_period["label"]
            time_period_date = time_period["date"]

            # get the previous cohort date (if it exists).  This is for figuring out openings/closings
            previous_cohort_date = self._time_periods[index - 1]["date"] if index > 0 else None

            # run query and save results per cohort
            results[time_period_label] = self._run_time_period_query(time_period_date, previous_cohort_date)

        return results


    def _get_excel_data_sets(self, db_results):

        # traverse db results, and create this dictionary for easy lookups
        store_counts_dict = self._get_store_counts_per_time_period_per_company(db_results)

        # get a sorted list of time period labels (assume time periods is of the format (t#)
        sorted_time_periods = [t["label"] for t in self._time_periods]
        sorted_time_periods = sorted(sorted_time_periods, key = lambda t: int(t[1:]))

        # get all companies
        all_companies = self._get_all_companies()

        # create the summary data set
        data_sets = [self._create_summary_data_set(sorted_time_periods, store_counts_dict, all_companies)]

        # create all stores, openings, closings per time period
        data_sets += self._create_per_time_period_data_sets(sorted_time_periods, store_counts_dict, all_companies)

        # very nice
        return data_sets




    # ----------------------------- Private Helpers ------------------------------ #

    def _create_per_time_period_data_sets(self, sorted_time_periods, store_counts_dict, all_companies):

        # create base array
        data_sets = []

        # create a data set for all-stores, openings, and closings
        data_set_all_stores = self._create_base_time_period_data_set("all stores", sorted_time_periods)
        data_set_openings = self._create_base_time_period_data_set("openings", sorted_time_periods)
        data_set_closings = self._create_base_time_period_data_set("closings", sorted_time_periods)

        # create the total row for each data set
        total_row_all = self._get_detail_total_row(sorted_time_periods)
        total_row_openings = self._get_detail_total_row(sorted_time_periods)
        total_row_closings = self._get_detail_total_row(sorted_time_periods)

        # loop through all companies
        for company_name in all_companies:

            # create the company rows for each data set
            row_all = { "Banner Name": company_name }
            row_openings = { "Banner Name": company_name }
            row_closings = { "Banner Name": company_name }

            # loop through each time period
            for index, time_period in enumerate(sorted_time_periods):

                # get totals, openings, etc....
                store_count, openings, closings = self._get_store_counts(store_counts_dict, time_period, company_name)

                # set the counts
                row_all[time_period] = store_count
                row_openings[time_period] = openings
                row_closings[time_period] = closings

                # add to the totals
                total_row_all[time_period] += store_count
                total_row_openings[time_period] += openings
                total_row_closings[time_period] += closings

            # add the rows to the data set
            data_set_all_stores["rows"].append(row_all)
            data_set_openings["rows"].append(row_openings)
            data_set_closings["rows"].append(row_closings)

        # add the totals
        data_set_all_stores["rows"].append(total_row_all)
        data_set_openings["rows"].append(total_row_openings)
        data_set_closings["rows"].append(total_row_closings)

        # add the data sets to the main array
        data_sets.append(data_set_all_stores)
        data_sets.append(data_set_openings)
        data_sets.append(data_set_closings)

        return data_sets


    def _create_base_time_period_data_set(self, label, sorted_time_periods):
        return {
            "headers" : ["Banner Name"] + [period for period in sorted_time_periods],
            "label": label,
            "rows": []
        }

    def _get_detail_total_row(self, sorted_time_periods):

        # base row
        total_row = { "Banner Name": "Total", "meta": { "bold": True } }

        # add each time period as a zero
        for time_period in sorted_time_periods:
            total_row[time_period] = 0

        return total_row


    def _create_summary_data_set(self, sorted_time_periods, store_counts_dict, all_companies):

        # create the base data sets
        data_set = {
            "headers" : self._get_time_period_headers(sorted_time_periods),
            "label": "Summary",
            "description": "Store Count Summary",
            "rows": []
        }

        # loop through every company then every time period to make the rows
        # go through every company (from db, not from raw data) to account for ones that have no stores
        for company_name in all_companies:

            # create base row
            row = { "Banner Name": company_name }

            for index, time_period in enumerate(sorted_time_periods):

                # set defaults
                store_count, openings, closings = self._get_store_counts(store_counts_dict, time_period, company_name)

                # always add the store count
                row[time_period] = store_count

                # if index is greater than 0, add openings, closings, and growth rate
                if index > 0:
                    row["%s - Openings" % time_period] = openings
                    row["%s - Closings" % time_period] = closings

                    # calculate growth rate
                    previous_store_count = store_counts_dict[sorted_time_periods[index - 1]][company_name]["store_count"]
                    row["%s - Growth Rate" % time_period] = self._get_percent_growth(store_count, previous_store_count)

            # add the row
            data_set["rows"].append(row)


        # add the base total row
        total_row = {
            "Banner Name": "Total",
            "meta": {
                "bold": True
            }
        }

        # calculate the total row
        for index, time_period in enumerate(sorted_time_periods):

            # set defaults per time period
            total_store_count = 0
            total_openings = 0
            total_closings = 0

            if time_period in store_counts_dict and store_counts_dict[time_period]:

                # get actual values
                for company_name in store_counts_dict[time_period]:
                    store_count, openings, closings = self._get_store_counts(store_counts_dict, time_period, company_name)
                    total_store_count += store_count
                    total_openings += openings
                    total_closings += closings

            # always add the store count for each time period
            total_row[time_period] = total_store_count

            # add openings, closings, growth rate if this is not the first time period
            if index > 0:
                total_row["%s - Openings" % time_period] = total_openings
                total_row["%s - Closings" % time_period] = total_closings

                # calculate growth rate
                previous_total_store_count = total_row[sorted_time_periods[index - 1]]
                total_row["%s - Growth Rate" % time_period] = self._get_percent_growth(total_store_count, previous_total_store_count)

        # add the row
        data_set["rows"].append(total_row)

        return data_set


    def _get_total_row(self, sorted_time_periods, store_counts_dict):

        # create the base total row
        total_row = {
            "Banner Name": "Total",
            "meta": {
                "bold": True
            }
        }

        # calculate the total row
        for index, time_period in enumerate(sorted_time_periods):

            # set defaults per time period
            total_store_count = 0
            total_openings = 0
            total_closings = 0

            if time_period in store_counts_dict and store_counts_dict[time_period]:

                # get actual values
                for company_name in store_counts_dict[time_period]:
                    store_count, openings, closings = self._get_store_counts(store_counts_dict, time_period, company_name)
                    total_store_count += store_count
                    total_openings += openings
                    total_closings += closings

            # always add the store count for each time period
            total_row[time_period] = total_store_count

            # add openings, closings, growth rate if this is not the first time period
            if index > 0:
                total_row["%s - Openings" % time_period] = total_openings
                total_row["%s - Closings" % time_period] = total_closings

                # calculate growth rate
                previous_total_store_count = total_row[sorted_time_periods[index - 1]]
                total_row["%s - Growth Rate" % time_period] = self._get_percent_growth(total_store_count, previous_total_store_count)

    def _get_store_counts(self, store_counts_dict, time_period, company_name):

        # set defaults
        store_count = 0
        openings = 0
        closings = 0

        # get the company values for this time period (if it has any)
        if time_period in store_counts_dict and company_name in store_counts_dict[time_period]:
            company_data = store_counts_dict[time_period][company_name]
            store_count = company_data["store_count"]
            openings = company_data["openings"]
            closings = company_data["closings"]

        return store_count, openings, closings

    def _get_percent_growth(self, current_value, previous_value):

        if not previous_value:
            return 0

        return self._round(((current_value - previous_value) / float(previous_value)) * 100)


    def _get_store_counts_per_time_period_per_company(self, db_results):



        # traverse db results, and create this dictionary for easy lookups
        store_counts_dict = {}

        # loop through time periods
        for time_period in self._time_periods:

            # get cohort details
            time_period_label = time_period["label"]

            # create the data set for this cohort
            store_counts_dict[time_period_label] = {
                sql_row.company_name: {
                    "store_count": sql_row.store_count,
                    "openings": sql_row.openings_count,
                    "closings": sql_row.closings_count
                }
                for sql_row in db_results[time_period_label]
            }

        return store_counts_dict


    def _get_time_period_headers(self, sorted_time_periods):

        # create the base headers list
        headers = ["Banner Name"]

        # cycle through every time period adding it and openings, closings.
        for index, time_period in enumerate(sorted_time_periods):

            # don't add openings/closings for the first time period
            if index > 0:
                headers.append("%s - Openings" % time_period)
                headers.append("%s - Closings" % time_period)

            # add the main time period
            headers.append(time_period)

        # add growth rates for every period after the first
        for index, time_period in enumerate(sorted_time_periods):
            if index > 0:
                headers.append("%s - Growth Rate" % time_period)

        return headers


    def _run_time_period_query(self, current_time_period, previous_time_period):
        """
        Important query notes:
            - I use a left join on stores and count distinct store id so that we can properly display companies without stores.
        """

        # if there's no previous time period (i.e. this is the first), than use this simpler query
        if not previous_time_period:

            query = """
                select
                    c.company_id,
                    c.name as company_name,
                    count(distinct s.store_id) as store_count,
                    0 as openings_count,
                    0 as closings_count
                from companies c
                left join stores s on s.company_id = c.company_id and s.assumed_opened_date <= ? and (s.assumed_closed_date is null or s.assumed_closed_date > ?)
                group by c.name, c.company_id
            """

            parameters = [current_time_period, current_time_period]

        # otherwise, actually look for closings and openings
        else:

            query = """
                select
                    c.company_id,
                    c.name as company_name,
                    all_stores.count as store_count,
                    openings.count as openings_count,
                    closings.count as closings_count
                from companies c
                -- active stores in cohort
                cross apply
                (
                    select count(*) as count
                    from stores s
                    where s.company_id = c.company_id and s.assumed_opened_date <= ? and (s.assumed_closed_date is null or s.assumed_closed_date > ?)
                ) all_stores
                -- openings
                cross apply
                (
                    select count(*) as count
                    from stores so
                    where so.company_id = c.company_id and so.assumed_opened_date > ? and so.assumed_opened_date <= ?
                ) openings
                -- closing
                cross apply
                (
                    select count(*) as count
                    from stores sc
                    where sc.company_id = c.company_id and sc.assumed_closed_date > ? and sc.assumed_closed_date <= ?
                ) closings
            """

            parameters = [current_time_period, current_time_period, previous_time_period, current_time_period, previous_time_period, current_time_period]

        return sql_execute_with_parameters(parameters, query)


    def _get_all_companies(self):

        # names should be distinct, but I'm forcing it so that we don't get any strange errors when converting to a dict.
        sql = "select distinct name as company_name from companies order by name"
        return [c.company_name for c in sql_execute(sql)]



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

    # create company definitions
    company_definitions = {
		"518347ea4af885658cf882aa" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-11-28T00:00:00",
				"t1" : "2013-06-27T00:00:00"
			},
			"company_name" : "C. Wonder",
			"weight" : 1
		},
		"525272003f0cd228d1092401" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : None,
				"t1" : "2013-12-31T00:00:00"
			},
			"company_name" : "C. Wonder Outlet",
			"weight" : 1
		},
		"dfaer342adsf" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-12T00:00:00",
				"t1" : "2013-07-16T00:00:00"
			},
			"company_name" : "Coach",
			"weight" : 1
		},
		"51e65cf95892d05bd02ff35b" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-12T00:00:00",
				"t1" : "2013-07-16T00:00:00"
			},
			"company_name" : "Coach Factory Store",
			"weight" : 1
		},
		"51c115865892d00e498773c9" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-12T00:00:00",
				"t1" : "2013-07-16T00:00:00"
			},
			"company_name" : "Coach Men",
			"weight" : 1
		},
		"51c011365892d073f4c5e074" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-12T00:00:00",
				"t1" : "2013-07-16T00:00:00"
			},
			"company_name" : "Coach Men Factory",
			"weight" : 1
		},
		"518194954af8850754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-26T00:00:00",
				"t1" : "2013-07-01T00:00:00"
			},
			"company_name" : "Furla",
			"weight" : 1
		},
        "518194954af8850754c759a" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-11-30T00:00:00",
				"t1" : "2013-11-27T00:00:00"
			},
			"company_name" : "Furla Outlets",
			"weight" : 1
		},
        "518194954af8850754c759" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Kate Spade",
			"weight" : 1
		},
        "518194954af8850754c75" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Kate Spade Outlet",
			"weight" : 1
		},
        "518194954af8850754c7" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-01-11T00:00:00",
				"t1" : "2013-07-21T00:00:00"
			},
			"company_name" : "KORS-AuthDealers",
			"weight" : 1
		},
        "518194954af8850754" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-10-03T00:00:00",
				"t1" : "2013-07-03T00:00:00"
			},
			"company_name" : "Longchamp Authorized Dealers",
			"weight" : 1
		},
        "518194759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Marc By Marc Jacobs Women's Accessories",
			"weight" : 1
		},
        "5181949af8850754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-08-27T00:00:00",
				"t1" : "2013-07-01T00:00:00"
			},
			"company_name" : "Michael Kors",
			"weight" : 1
		},
        "5181949af80754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-08-27T00:00:00",
				"t1" : "2013-07-01T00:00:00"
			},
			"company_name" : "Michael Kors Outlet",
			"weight" : 1
		},
        "5181949a0754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-11-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Tory Burch",
			"weight" : 1
		},
        "5181949af8759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-11-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Tory Burch Outlet",
			"weight" : 1
		}
	}

    # create report
    report = CustomAnalyticsStoreCountReport(time_periods, company_definitions)

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