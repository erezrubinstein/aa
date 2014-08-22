import datetime
from dateutil.relativedelta import relativedelta
import mox
from common.business_logic.company_info import Competitor
from common.helpers.common_dependency_helper import register_common_concrete_dependencies, _empty_stub
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import Dependency
from core.build.db.load_helper import config_dev
from core.common.business_logic.service_entity_logic import time_interval_helper
from geoprocessing.data_access import company_handler, address_handler, store_handler, company_competition_handler

__author__ = "erezrubinstein"

class CustomAnalyticsLoader(object):

    def __init__(self, target_db_name, company_settings):

        # init yo'self
        self.target_db_name = target_db_name
        self.company_settings = company_settings

        # get some dependencies
        self.mds_access = Dependency("CoreAPIProvider").value.mds
        self.mds_params = Dependency("CoreAPIParamsBuilder").value.mds
        
        # get some helpers
        self._fast_date_parser = FastDateParser()


    def load(self):
        """
        Main Load Method
        """

        # insert companies
        core_to_sql_id_mappings = self._insert_companies()

        # get stores for each company
        stores_to_insert = self._get_stores_by_company()

        # insert addresses
        self._insert_addresses(stores_to_insert)

        # figure out time period dates
        time_period_dates = self._get_time_period_dates()

        # insert stores
        self._insert_stores(stores_to_insert, core_to_sql_id_mappings, time_period_dates)

        # insert competitive companies
        self._insert_competitive_companies(core_to_sql_id_mappings)

        return time_period_dates



    # ---------------------------- Internal ---------------------------- #

    def _insert_companies(self):

        # keep track of the sql company ids in relation to their core ones
        core_id_to_sql_id_mappings = {}

        # loop through companies and insert them
        for company_id, company_settings in self.company_settings.iteritems():

            # insert the company
            company_name = company_settings["company_name"]
            sql_id = company_handler.select_company_id_force_insert(company_name, self.target_db_name)

            # insert and map the id
            core_id_to_sql_id_mappings[company_id] = sql_id

        return core_id_to_sql_id_mappings


    def _get_stores_by_company(self):

        stores_to_insert = {}

        # loop through every company
        for company_id, company in self.company_settings.iteritems():

            # create record for this company
            stores_to_insert[company_id] = {}

            # get date query
            query = self._get_date_query(company["time_periods"].values())

            # add company id to the filter
            query["data.company_id"] = company_id

            # get store and add to dict
            stores_to_insert[company_id] = self._query_stores(query)

        return stores_to_insert


    def _insert_addresses(self, stores):

        # join all the store arrays
        all_stores = []
        for company_id in stores:
            all_stores += stores[company_id]

        # create the address fields for each store in the dict
        addresses = [
            {
                "street_number": store["data"]["street_number"],
                "street": store["data"]["street"],
                "city": store["data"]["city"],
                "state": store["data"]["state"],
                "zip": store["data"]["zip"],
                "suite": store["data"]["suite"],
                "latitude": store["data"]["latitude"],
                "longitude": store["data"]["longitude"],
                "shopping_center_name": store["data"]["shopping_center"],
                "unique_store_identifier": store["_id"]
            }
            for store in all_stores
        ]
        
        # insert the addresses
        address_handler.batch_insert_addresses(addresses, self.target_db_name)


    def _get_time_period_dates(self):
        """
        Create a made up static date for every time period.  it doesn't really matter what the date is.
        """

        # helper vars
        time_period_dates = {}
        current_time_period_date = datetime.datetime(1900, 1, 1)

        # assume that all companies have the same number of time periods.
        time_period_labels = self.company_settings.values()[0]["time_periods"].keys()

        # sort the keys assuming a t# format
        time_period_labels = sorted(time_period_labels, key = lambda tp: int(tp[1:])) # tp, hahaha

        for time_period in time_period_labels:

            # set this time periods date
            time_period_dates[time_period] = current_time_period_date

            # increment the time period by one month
            current_time_period_date += relativedelta(months = 1)

        # return the mapping
        return time_period_dates



    def _insert_stores(self, stores_to_insert, core_to_sql_id_mappings, time_period_dates):

        # a collection for formatted and clean stores
        formatted_stores = []

        # loop through every company's stores
        for company_id, stores in stores_to_insert.iteritems():

            # get some company vars that we'll need soon
            company_sql_id = core_to_sql_id_mappings[company_id]
            company_time_periods = self.company_settings[company_id]["time_periods"]

            # convert the time periods to an array and sort it by time period (assuming a t# format).
            # also filter out non null dates
            # woa, what a killer one liner!!!
            company_time_periods = filter(
                lambda tp: tp["date"],
                sorted(
                    [
                        {
                            "label": time_period,
                            "date": self._fast_date_parser.parse_date(company_time_periods[time_period])
                        }
                        for time_period in company_time_periods
                    ],
                    key = lambda tp: int(tp["label"][1:]) # tp, hahahaha
                )
            )

            # loop through every store
            for store in stores:

                # get some helper vars for the store
                store_data = store["data"]
                opened_date = self._fast_date_parser.parse_date(store_data["store_opened_date"])
                closed_date = self._fast_date_parser.parse_date(store_data["store_closed_date"])

                # get a normalized start/end date for the store, based where it fits in its company's time periods
                opened_date, closed_date = self._get_normalized_store_dates(opened_date, closed_date, company_time_periods, time_period_dates)

                # this is a check that they're not both null.
                # if they're both null, than the failed the normalized store dates function and shouldn't be added.
                # a good case of this is if a user skips a few time periods and a store opens/closes in between  (i.e. doesn't actually belong in either)
                if opened_date or closed_date:

                    # add the formatted store
                    formatted_stores.append({
                        "company_id": company_sql_id,
                        "trade_area_id": store["_id"],
                        "core_store_id": store_data["store_id"],
                        "phone_number": store_data["phone"],
                        "opened_date": opened_date,
                        "closed_date": closed_date,
                        "assumed_opened_date": opened_date,
                        "assumed_closed_date": closed_date
                    })

        # insert the stores
        store_handler.batch_insert_stores__auto_get_addresses(formatted_stores, self.target_db_name)


    def _insert_competitive_companies(self, core_to_sql_id_mappings):

        # create a list of all company sql ids
        company_sql_ids = core_to_sql_id_mappings.values()

        # create a mapping of company sql ids to their weight
        company_weights = {
            core_to_sql_id_mappings[core_id]: self.company_settings[core_id]["weight"]
            for core_id in core_to_sql_id_mappings
        }

        # create an empty list of competitor objects
        competitors = []

        # define a function for the company to company mapping function
        def add_competitor_map(company_id_1):
            for company_id_2 in company_sql_ids:

                # add a competition record for every away company with the away company's weight
                competitors.append(Competitor.simple_init(company_id_1, company_id_2, company_weights[company_id_2], datetime.datetime(1900, 1, 1), None))

        # map companies to itself
        map(add_competitor_map, company_sql_ids)

        # insert the competitors
        company_competition_handler.insert_company_competition(competitors, self.target_db_name)



    # ---------------------------- Private ---------------------------- #


    def _get_normalized_store_dates(self, opened_date, closed_date, sorted_company_time_periods, time_period_dates):

        # init the store has being opened on the first date and never closed
        new_opened_date = None
        new_closed_date = None

        # if the passed in opened date is null, just assume it was open in the first time period
        if opened_date is None:
            new_opened_date = time_period_dates[sorted_company_time_periods[0]["label"]]

        # loop through all the company's time periods
        for index, tp in enumerate(sorted_company_time_periods):

            # get date helpers
            current_date = tp["date"]

            # if new opened date hasn't been set and it's before this time period, set it
            if new_opened_date is None and opened_date <= current_date:
                new_opened_date = time_period_dates[tp["label"]]

                # if we set the opened date, and closed date is null, than just break
                if closed_date is None:
                    break

                # this is an edge case.  If end_date is also before the current date, than something is wrong and this store doesn't belong
                # in that case, return null's for both
                elif closed_date <= current_date:
                    return None, None

            # if store closed before or on this date, than mark this date as the closed date
            elif closed_date and current_date >= closed_date:
                new_closed_date = time_period_dates[tp["label"]]

                # assume that this is it, no need to continue the loop
                break


        # this is a check to fix a bug that was found (RET 3476)
        if new_opened_date == new_closed_date:

            # this should never happen and making it none will make sure the store doesn't get inserted
            return None, None

        return new_opened_date, new_closed_date


    def _get_non_null_sorted_dates(self, time_period_dates):

        # filter out None values
        time_period_dates = filter(lambda value: value, time_period_dates)

        # make them into dates
        time_period_dates = [self._fast_date_parser.parse_date(date_str) for date_str in time_period_dates]

        # sort by date and return
        return sorted(time_period_dates)


    def _get_date_query(self, time_period_dates):

        # get sorted, non null dates
        time_period_dates = self._get_non_null_sorted_dates(time_period_dates)

        # if there's only one value, find all live stores during that time
        if len(time_period_dates) == 1:

            return time_interval_helper.active_as_of_analytics_date(time_period_dates[0])

        # otherwise, return the range of the first-last date
        else:
            dates = [time_period_dates[0], time_period_dates[-1]]
            return { "$or": time_interval_helper.live_entity_filter(dates, "interval", "$lte", "$gte") }


    def _query_stores(self, query):

        # create mds params
        entity_fields = ["_id", "data.street_number", "data.street", "data.city", "data.state", "data.zip", "data.suite", "data.phone",
                         "data.latitude", "data.longitude", "data.shopping_center", "data.store_opened_date", "data.store_closed_date",
                         "data.store_id"]
        params = self.mds_params.create_params(resource = "find_entities_raw", query = query, entity_fields = entity_fields)["params"]

        # run query
        return self.mds_access.call_find_entities_raw("trade_area", params)





# --------------------- Main (testing) --------------------- #

def main():

    company_settings = {
        "518194954af8850754c759ab": {
            "company_name": "ALDI",
            "is_target": True,
            "time_periods": {
                "t0": None,
                "t1": "2012-05-05T00:00:00",
                "t2": None,
                "t3": None,
                "t4": None,
                "t5": "2013-03-18T00:00:00",
                "t6": None,
                "t7": None,
                "t8": "2013-12-19T00:00:00"
            },
            "weight": 1
        },
        "518347ea4af885658cf882aa": {
            "company_name": "Whole Foods Market",
            "is_target": True,
            "time_periods": {
                "t0": "2012-01-11T00:00:00",
                "t1": "2012-03-28T00:00:00",
                "t2": "2012-06-25T00:00:00",
                "t3": "2012-09-30T00:00:00",
                "t4": "2013-01-30T00:00:00",
                "t5": "2013-03-21T00:00:00",
                "t6": "2013-07-04T00:00:00",
                "t7": "2013-10-04T00:00:00",
                "t8": "2013-12-31T00:00:00"
            },
            "weight": 1
        },
        "51c011365892d073f4c5e074": {
            "company_name": "Creve Coeur Camera",
            "is_target": True,
            "time_periods": {
                "t0": None,
                "t1": None,
                "t2": None,
                "t3": None,
                "t4": "2013-01-05T00:00:00",
                "t5": "2013-05-02T00:00:00",
                "t6": None,
                "t7": None,
                "t8": None
            },
            "weight": 1
        },
        "51c115865892d00e498773c9": {
            "company_name": "Columbia Photo",
            "is_target": True,
            "time_periods": {
                "t0": None,
                "t1": None,
                "t2": None,
                "t3": None,
                "t4": "2013-01-24T00:00:00",
                "t5": None,
                "t6": "2013-06-24T08:51:15.798000",
                "t7": None,
                "t8": None
            },
            "weight": 1
        },
        "51e65cf95892d05bd02ff35b": {
            "company_name": "American Apparel",
            "is_target": True,
            "time_periods": {
                "t0": None,
                "t1": None,
                "t2": None,
                "t3": "2012-08-15T00:00:00",
                "t4": None,
                "t5": None,
                "t6": "2013-07-04T00:00:00",
                "t7": None,
                "t8": "2013-12-24T00:00:00"
            },
            "weight": 1
        },
        "525272003f0cd228d1092401": {
            "company_name": "Adidas",
            "is_target": True,
            "time_periods": {
                "t0": None,
                "t1": None,
                "t2": None,
                "t3": "2012-09-19T00:00:00",
                "t4": None,
                "t5": None,
                "t6": None,
                "t7": "2013-09-23T00:00:00",
                "t8": None
            },
            "weight": 1
        }
    }
    
    CustomAnalyticsLoader("ca_51ed900cf3d31bcca5653366_Dollar_Stores_Report_2014_03_10_5317855ef3d31b80ddcc958a", company_settings).load()

    print "done"


if __name__ == "__main__":

    # make logger
    logger = mox.Mox().CreateMockAnything()
    logger.debug = _empty_stub
    logger.info = _empty_stub
    logger.warning = _empty_stub
    logger.error = _empty_stub
    logger.critical = _empty_stub

    # register dependencies
    register_common_concrete_dependencies(svc_config = config_dev, logger = logger, retail_db_config = config_dev["RETAIL_MONGODB_CONN"])

    # run
    main()

