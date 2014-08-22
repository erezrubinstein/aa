from common.utilities.inversion_of_control import Dependency
from geoprocessing.business_logic.business_helpers.monopoly_transitions.monopoly_transition_helper import MonopolyTransitionHelper
from common.utilities.date_utilities import get_later_date, get_earlier_date, END_OF_WORLD


class CompetitiveStoreHelper(object):
    """
    This class represents a set of competitive stores belonging to one home store and one trade area
    This is not a standard business object.  Rather, it is more like a cloud_provider, which helps us synchronize sets of competitive stores.
    """
    def __init__(self, home_store, away_stores, trade_area_id, data_repository):
        self.home_store = home_store
        self.away_stores = away_stores
        self.trade_area_id  = trade_area_id
        self.data_repository = data_repository
        self.is_sql_data_repository = hasattr(self.data_repository, "is_sql") and self.data_repository.is_sql

        # get dependencies
        self._log = Dependency("LogManager").value

        # query the current set of competitive stores, which we need to do the diffs
        self.previous_away_stores = self.data_repository.get_competitive_stores(self.home_store.store_id, self.trade_area_id)

    def synchronize_competitive_stores_in_db(self):
        """
        This method synchronizes the competitive stores:
           - new stores are added
           - existing stores are updated
           - deleted stores are marked with an end_date
        """

        # figure out if there are any stores whose competitive record "disappeared"
        stores_to_close = set(self.previous_away_stores) - set(self.away_stores)

        # if any competitive store disappeared, log an error.  Used to raise an exception, but we changed this for core.
        if len(stores_to_close) > 0:

            # log a warning.  no need to delete these, since core will "update" them away.  this does not happen in SQL
            self._log.warning("several away stores (%s) have disappeared from the list." % str([store.away_store_id for store in stores_to_close]))

        # insert/update new away stores
        batch_competitive_stores = []
        if self.away_stores and len(self.away_stores) > 0:
            batch_competitive_stores = self._upsert_new_away_stores()

        # !IMP! this is for forward compatibility (i.e. the core mongo code)
        # always call, even if it's an empty array
        self.data_repository.batch_upsert_competitive_stores(self.trade_area_id, batch_competitive_stores)


    def synchronize_monopolies_in_db(self):
        """
        This method synchronizes the monopoly record:
           - new monopoly is inserted
           - old monopoly is closed
           - updated monopoly is closed, and then a new one is inserted
        """

        # get all current competitive stores (include closed ones)
        competitive_store_instances = self.data_repository.get_competitive_stores(self.home_store.store_id, self.trade_area_id)

        # delete all monopolies
        self.data_repository.delete_from_monopolies(self.home_store.store_id, self.trade_area_id)

        # declare batch monopolies list for later insertion.  SQL Repository inserts one by one.  Only Core batches.
        batch_monopolies_list = []

        # if there are competitive store instances, figure out historical monopolies
        if competitive_store_instances:
            # figure out new monopoly date range
            transition_parameters = self._get_monopoly_transition_parameters(competitive_store_instances)

            # transition each range
            for transition in transition_parameters:
                # transitioning monopolies is very complex.  We are delegating it to a specific _cloud_provider file
                MonopolyTransitionHelper.transition_monopoly_record(self.home_store, self.trade_area_id, transition.away_stores, transition.previous_away_stores,
                    self.data_repository, batch_monopolies_list)

        # complete monopoly always!!!
        else:
            MonopolyTransitionHelper.transition_monopoly_record(self.home_store, self.trade_area_id, [], [],
                self.data_repository, batch_monopolies_list)


        # if home store closes, make sure to always close that monopoly
        # Erez - I feel like this should never need to happen, but I remember a certain scenario where we needed it
        if self.home_store._assumed_closed_date is not None and self.home_store._assumed_closed_date != END_OF_WORLD:
            self.data_repository.close_monopoly_record(self.home_store.store_id, self.trade_area_id, self.home_store._assumed_closed_date, batch_monopolies_list)


        # batch upsert monopolies (Only in core.  This does nothing in SQL data repository)
        self.data_repository.batch_upsert_monopolies(self.trade_area_id, batch_monopolies_list)



    # -------------------------------------------- Private Methods --------------------------------------------

    def _upsert_new_away_stores(self):

        batch_competitive_stores = []

        # !IMP! the for loop is for backwards compatibility for the SQL code.  CoreDataRepository ignores this.
        for away_store in self.away_stores:

            # figure out the opened date for the store (either it's the store's opened date or the home store's opened date.  whichever is later)
            opened_date = get_later_date(away_store._assumed_opened_date, self.home_store._assumed_opened_date)
            closed_date = get_earlier_date(away_store._assumed_closed_date, self.home_store._assumed_closed_date)

            # make sure you consider company opened/closed dates in the equation in case the company opened/closed before the store
            opened_date = get_later_date(opened_date, away_store.competitive_companies_assumed_start_date)
            closed_date = get_earlier_date(closed_date, away_store.competitive_companies_assumed_end_date)

            if opened_date is None or closed_date is None or opened_date < closed_date:

                # add to batch for core
                batch_competitive_stores.append(self._create_batch_competition_structure(away_store, opened_date, closed_date, self.is_sql_data_repository, self.home_store.store_id))

        return batch_competitive_stores


    def _get_monopoly_transition_parameters(self, competitive_store_instances):
        # get transition dates
        transition_dates = self._get_transition_dates(competitive_store_instances)

        # create transition parameters
        transition_parameters = []
        previous_away_stores = []
        for transition_date in transition_dates:

            # for non "infinity" end_dates
            if transition_date != END_OF_WORLD:
                # get all competitive_store records that are opened on or before the date and are not closed (non-inclusive)
                current_away_stores = [csi for csi in competitive_store_instances if
                                       csi.opened_date <= transition_date < (csi.closed_date or END_OF_WORLD)]
            else:
                current_away_stores = [csi for csi in competitive_store_instances if csi.closed_date is None or csi.closed_date == END_OF_WORLD]

            # create transition range
            transition_parameters.append(MonopolyTransitionParameter(current_away_stores, previous_away_stores))

            #set previous csi as current csi
            previous_away_stores = current_away_stores

        return transition_parameters

    def _get_transition_dates(self, competitive_store_instance):
        opened_dates = set([csi.opened_date for csi in competitive_store_instance])
        # null becomes 1/1/3000
        closed_dates = set([csi.closed_date or END_OF_WORLD for csi in competitive_store_instance])
        home_dates = { self.home_store._assumed_opened_date, self.home_store._assumed_closed_date or END_OF_WORLD }

        # get unique list of dates
        return sorted(opened_dates | closed_dates | home_dates)

    @classmethod
    def _create_batch_competition_structure(cls, away_store, opened_date, closed_date, is_sql_data_repository = False,
                                            home_store_id = None):
        """
        Class Method so that it can be called from outside as a helper
        """

        away_structure = {
            "away_store_id": away_store.away_store_id,
            "away_company_id": away_store.company_id,
            "start_date": opened_date,
            "end_date": closed_date,
            "weight": away_store.competitive_weight,
            "away_company_name": away_store.company_name,
            "away_street_number": away_store.street_number,
            "away_street": away_store.street,
            "away_city": away_store.city,
            "away_state": away_store.state,
            "away_zip": away_store.zip_code,
            "away_geo": [away_store.longitude, away_store.latitude],
            "away_lng": away_store.longitude,
            "away_lat": away_store.latitude
        }

        # add certain fields to sql data repository only
        if is_sql_data_repository:
            away_structure["home_store_id"] = home_store_id
            away_structure["competitive_company_id"] = away_store.competitive_company_id
            away_structure["travel_time"] = away_store.travel_time

        return away_structure



class MonopolyTransitionParameter(object):
    def __init__(self, away_stores, previous_away_stores):
        self.away_stores = away_stores
        self.previous_away_stores = previous_away_stores