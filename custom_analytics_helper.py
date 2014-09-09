from collections import defaultdict
import datetime
from bson.objectid import ObjectId
from common.utilities.date_utilities import parse_date, FastDateParser, pretty_please
from common.utilities.inversion_of_control import Dependency
from common.utilities.misc_utilities import convert_entity_list_to_dictionary
from core.common.business_logic.service_entity_logic import company_helper
from retail.v010.data_access.models import custom_analytics_run


__author__ = 'erezrubinstein'



# ----------------------- Basic CRUD Methods ----------------------- #


def find_custom_analytic_runs(user_id):

    # get all non deleted objects for this user
    custom_analytics_run_objects = custom_analytics_run.CustomAnalyticsRun.objects(user_id = str(user_id), status__ne = "deleted")

    # sort by created date desc
    custom_analytics_run_objects = sorted(custom_analytics_run_objects, key = lambda run: run.created_at, reverse = True)

    # return each object in its serialized form
    return [obj.serialize() for obj in custom_analytics_run_objects]


def find_custom_analytics_run_by_id(ca_run_id):
    return custom_analytics_run.CustomAnalyticsRun.objects(pk = ObjectId(ca_run_id))[0].serialize()


def archive_custom_analytics_run(ca_run_id):

    ca_run = custom_analytics_run.CustomAnalyticsRun.objects(pk = ObjectId(ca_run_id))[0]
    ca_run.status = "deleted"
    ca_run.internal_status = "deleted"
    ca_run.save()


def create_new_analytics_run(report_name, trade_areas, demographic_template, companies, time_periods, run_comp_stores_report, comp_stores_periods, client_id, user_id):

    # remove any completely empty time periods
    # this will also remap any comp store periods that need to be remapped
    time_periods, comp_stores_periods = _remove_null_time_periods_and_remap_comp_stores(time_periods, run_comp_stores_report, comp_stores_periods)

    # join time periods, companies
    for company_id in time_periods:
        companies[company_id]["time_periods"] = time_periods[company_id]

    # create the mongo engine object
    params = {
        "report_name": report_name,
        "trade_areas": trade_areas,
        "demographic_template": demographic_template,
        "companies": companies,
        "client_id": str(client_id),
        "user_id": str(user_id),
        "status": "queued",
        "internal_status": "queued",
        "created_at": datetime.datetime.utcnow(),
        "run_comp_stores_report": run_comp_stores_report,
        "comp_stores_periods": comp_stores_periods
    }
    ca_run = custom_analytics_run.CustomAnalyticsRun(**params)

    # save
    ca_run.save()

    return ca_run




# ----------------------- UI Helpers ----------------------- #


def get_company_display_fields(company_ids):
    """
    for now, we're just getting the company's status
    """

    # get the dependencies
    main_access = Dependency("CoreAPIProvider").value
    main_params = Dependency("CoreAPIParamsBuilder").value

    # query the companies
    query = { "_id": { "$in": company_ids }}
    entity_fields = ["_id", "data.status"]
    params = main_params.mds.create_params(resource = "find_entities_raw", query = query, entity_fields = entity_fields)["params"]
    companies = main_access.mds.call_find_entities_raw("company", params)

    # convert into dictionary of raw values by company id and return
    return {
        c["_id"]: {
            "status": c["data"]["status"]
        }
        for c in companies
    }



def get_company_collection_dates_and_input_form_defaults(company_ids):
    """
    This returns all the collection dates per company along with the following:
        - maximum number of collections for all companies
        - default date placement per company.
            - this is a UI thing and will tell the UI which date to select for which time series
    """

    # create a fast date parser to speed things up
    date_parser = FastDateParser()

    # query the collection dates
    companies = company_helper.get_store_collection_dates(company_ids)

    # create a nicely formatted dictionary of the results by company_id
    results = {
        "collection_dates": {
            company["_id"]:
                # make sure the dates are sorted in ascending order
                sorted(company["data"].get("collection", {}).get("dates", {}).get("stores", []), key = lambda date: date_parser.parse_date(date))
            for company in companies
        }
    }

    # add a record for the longest collection dates array
    results["max_collection_length"] = _get_longest_collection_date_array(results["collection_dates"].values())

    # figure out default date placement for all of the companies
    results["default_time_periods"] = _get_default_date_periods(results["collection_dates"], date_parser)

    # return the results
    return results



# ----------------------- Validation Rules  ----------------------- #

def validate_selected_time_periods(company_time_periods):

    results = {}

    # time periods have to be non-empty
    if not company_time_periods:
        raise Exception("No Time Periods")

    # cycle through every company
    for company_id in company_time_periods:

        # add error if there are no time periods
        if not company_time_periods[company_id]:
            results[company_id] = "No Time Periods"
            continue

        # some helper variables for verifications
        most_recent_date = None
        most_recent_time_period = None
        contains_date = False

        # sort the time periods by their numbers (assuming a t# format).
        time_periods = sorted(company_time_periods[company_id].keys(), key = lambda t: int(t[1:]))

        # loop through dates
        for time_period in time_periods:

            # helper vars
            # get date as a string and datetime.  That way we can see if something failed to parse from a string into a date (i.e. first check)
            current_date_str = company_time_periods[company_id][time_period]
            current_date = parse_date(current_date_str)

            # record and error if the date is not a date
            if current_date_str and not current_date:
                results[company_id] = "Time period %s contains an invalid date" % time_period
                break

            # if current date is before the most recent date (it's ok to be the same)
            if most_recent_date and current_date and most_recent_date > current_date:
                results[company_id] = "%s (%s) must be older than %s (%s)" % (most_recent_time_period, pretty_please(most_recent_date), time_period, pretty_please(current_date))
                break

            # if this is the most recent date, remember it so we can compare the next dates against it
            elif current_date:
                most_recent_date = current_date
                most_recent_time_period = time_period
                contains_date = True

        # if we don't have a date, and there's no other error, add one
        if not contains_date and company_id not in results:
            results[company_id] = "Must contain at least one date"

    return results


def validate_companies(companies):

    # begin with empty set
    results = {}

    # define error message, which is the same for each error
    error_message = "Invalid weight (must be a positive number)"

    if companies:

        for company_id, company in companies.iteritems():

            # get the weight
            weight = company.get("weight", None)

            # check if it's a number and assign an error
            if not _is_positive_number(weight):
                results[company_id] = error_message

    return results


def validate_comp_store_settings(run_comp_stores_report, comp_stores_periods, time_periods):
    """
    Here is a list of rules this validates:
    1) if comp stores enabled, you must have at least one period
    2) each cohort in every period must be filled in (i.e. not null)
    3) periods must be in ascending order (i.e. cp > pp > py)
    """

    # begin with empty set
    results = {}

    # remove any completely null time periods
    non_null_time_periods, null_time_periods = _separate_null_from_none_null_time_periods(time_periods)

    # convert null time periods for an easy lookup
    null_time_periods = { tp: 1 for tp in null_time_periods }

    # only proceed if run_comp_stores_report is enabled
    if run_comp_stores_report:

        if len(non_null_time_periods) < 3:
            results[0] = "Not enough time periods.  There must be at least 3 (non-None) time periods."

        # if there are no periods, return an error
        if not comp_stores_periods:
            results[0] = "At least one Period is required to run the Comp Stores report."

        # loop through each period
        for index, period in enumerate(comp_stores_periods):

            # verify that each period has each cohort filled in
            for cohort in ["CP", "PP", "PY"]:
                if cohort not in period or not period[cohort]:
                    results[index] = "Comp Stores Period %s is incomplete." % str(index)

                    # break the cohort loop since it's already invalid
                    break

            # if we've already failed the last check, skip the rest of the checks for this period (i.e. check next period)
            if index in results:
                continue

            # get the number representation of each cohort (e.g. t9 = 9)
            cp = int(period["CP"][1:])
            pp = int(period["PP"][1:])
            py = int(period["PY"][1:])

            # make sure that the periods are in the correct order (i.e. cp > pp > py)
            if cp <= pp:
                results[index] = "Period %s is incorrect.  CP should be later than PP." % str(index)

                # skip the rest, since it's already invalid
                continue
            elif pp <= py:
                results[index] = "Period %s is incorrect.  PP should be later than PY." % str(index)

                # skip the rest, since it's already invalid
                continue

            # if we've already failed the last check, skip the rest of the checks for this period (i.e. check next period)
            if index in results:
                continue

            # make sure that no cohort has a completely null time period
            if period["CP"] in null_time_periods:
                results[index] = "Period %s is incorrect.  CP has a time period with all Nones." % str(index)
            elif period["PP"] in null_time_periods:
                results[index] = "Period %s is incorrect.  PP has a time period with all Nones." % str(index)
            elif period["PY"] in null_time_periods:
                results[index] = "Period %s is incorrect.  PY has a time period with all Nones." % str(index)


    return results



# -------------------------- Private Helpers -------------------------- #

def _remove_null_time_periods_and_remap_comp_stores(time_periods, run_comp_stores_report, comp_stores_periods):

    # helper vars
    time_period_has_data = {}
    time_period_mappings = {}
    new_time_periods = {}

    # loop through time periods for every company and see which ones don't have any data
    for company_id, company_time_periods in time_periods.iteritems():
        for time_period, date_str in company_time_periods.iteritems():

            # add to dict if it's not there
            if time_period not in time_period_has_data:
                time_period_has_data[time_period] = False

            # if this has a real date, than set it as having a date
            if date_str:
                time_period_has_data[time_period] = True


    # loop through time periods and remove those that don't have data
    for time_period in time_period_has_data:

        # if this time period has no data, remove it from all companies
        if not time_period_has_data[time_period]:
            for company_id in time_periods.keys():
                del time_periods[company_id][time_period]


    # re-create time_periods with in the correct ascending order
    for company_id, company_time_periods in time_periods.iteritems():

        # set up the company object
        new_time_periods[company_id] = {}

        # sort the time period keys in ascending order (assuming a t# format)
        sorted_time_periods = sorted(company_time_periods.keys(), key = lambda tp: int(tp[1:])) # tp, hahahahaha

        # loop through non-deleted time periods and add them to the new set starting with t0
        for index, time_period in enumerate(sorted_time_periods):

            # set the new label for this time period
            new_time_periods[company_id]["t%i" % index] = company_time_periods[time_period]

            # keep track of the mappings, which we'll use next to remap the comp store settings
            time_period_mappings[time_period] = "t%i" % index


    # if we have comp stores, than go a head and remap them after removing some time periods
    if run_comp_stores_report:

        # loop through every period
        for cp_period in comp_stores_periods:

            # map the cohorts
            cp_period["CP"] = time_period_mappings[cp_period["CP"]]
            cp_period["PP"] = time_period_mappings[cp_period["PP"]]
            cp_period["PY"] = time_period_mappings[cp_period["PY"]]

    return new_time_periods, comp_stores_periods


def _separate_null_from_none_null_time_periods(time_periods):

    # helper vars
    time_period_has_data = {}

    # loop through time periods for every company and see which ones don't have any data
    for company_id, company_time_periods in time_periods.iteritems():
        for time_period, date_str in company_time_periods.iteritems():

            # add to dict if it's not there
            if time_period not in time_period_has_data:
                time_period_has_data[time_period] = False

            # if this has a real date, than set it as having a date
            if date_str:
                time_period_has_data[time_period] = True


    # get the list of none null time periods
    non_null_time_periods = [
        time_period for time_period in time_period_has_data
        if time_period_has_data[time_period]
    ]

    # get the list of null time periods
    null_time_periods = [
        time_period for time_period in time_period_has_data
        if not time_period_has_data[time_period]
    ]

    # return them both
    return non_null_time_periods, null_time_periods


def _get_longest_collection_date_array(collection_dates_list):

    # default to 0
    longest = 0

    # loop and keep looking for the longest set of dates
    for collection_dates in collection_dates_list:
        if len(collection_dates) > longest:
            longest = len(collection_dates)

    return longest


def _get_default_date_periods(collection_dates_dict, date_parser):

    # default dict of company_id
    defaults = {
        company_id: {}
        for company_id in collection_dates_dict.keys()
    }

    if collection_dates_dict:

        # create a sorted list of company id and collection dates.
        company_list = _sort_companies_by_collection_dates_length(collection_dates_dict)

        # make the first company (with most collections) the one to match to
        comparable_collection_dates = company_list[0]["collection_dates"]

        # helper vars for the algorithm below
        max_time_periods = len(comparable_collection_dates)

        # loop through every company
        for company in company_list:

            # helper variables
            company_id = company["company_id"]
            collection_dates = company["collection_dates"]
            matches_left = len(collection_dates)
            collection_index = 0

            # loop through time periods and begin setting them
            for i in range(0, max_time_periods):

                # get current and next date for comparison
                current_comparable_date = comparable_collection_dates[i]
                next_comparable_date = comparable_collection_dates[i + 1] if i + 1 < max_time_periods else None

                # see how many periods are left
                periods_left = max_time_periods - i

                # if we need still have matches left
                #    AND
                #       if we no longer have empty spots to skip (i.e. we've skipped too many), than always match
                #       OR
                #       if this company's collection date is closer to this date, than the next date, than set it
                if matches_left > 0 and (periods_left == matches_left
                     or _is_collection_date_closer_to_current(collection_dates[collection_index], current_comparable_date, next_comparable_date, date_parser)):

                    defaults[company_id][_get_time_period_name(i)] = collection_dates[collection_index]
                    matches_left -= 1
                    collection_index += 1

                # otherwise, leave this time period as empty
                else:

                    defaults[company_id][_get_time_period_name(i)] = None

    return defaults


def _is_collection_date_closer_to_current(company_collection_date, current_comparable_date, next_comparable_date, date_parser):

    # this shouldn't happen because of the first clause that compares what's left, but let's keep it just in case...
    if not next_comparable_date:
        return True

    elif abs((date_parser.parse_date(company_collection_date) - date_parser.parse_date(current_comparable_date)).days) < \
            abs((date_parser.parse_date(company_collection_date) - date_parser.parse_date(next_comparable_date)).days):
        return True

    else:
        return False


def _sort_companies_by_collection_dates_length(collection_dates_dict):

    # create a list of company id to collection dates
    company_list = []
    for company_id, collection_dates in collection_dates_dict.iteritems():
        company_list.append({
            "company_id": company_id,

            # have
            "collection_dates": collection_dates
        })

    # sort the company list by descending collection dates length
    return sorted(company_list, key = lambda c: len(c["collection_dates"]), reverse = True)


def _get_time_period_name(index):
    return "t%i" % index


def _is_positive_number(s):
    try:
        number = float(s)
        return number > 0
    except:
        return False