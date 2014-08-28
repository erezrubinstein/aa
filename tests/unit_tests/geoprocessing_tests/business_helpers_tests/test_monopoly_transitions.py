from datetime import datetime
import unittest
from geoprocessing.business_logic.enums import CompetitionType
from geoprocessing.business_logic.business_helpers.monopoly_transitions.monopoly_transition_helper import MonopolyTransitionHelper
from geoprocessing.business_logic.business_objects.monopoly import Monopoly
from geoprocessing.business_logic.business_objects.store import Store
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.config import Config
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository

__author__ = 'erezrubinstein'


class MonopolyTransitionTests(unittest.TestCase):
    def setUp(self):
        # set up dependencies
        dependencies.register_dependency("Config", Config().instance)
        self._data_repository = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", self._data_repository)

        # set up fake store
        self._store = Store()
        self._store.store_id = 1
        self._store.company_id = 2


    def doCleanups(self):
        dependencies.clear()




    ################################################################################################################################################
    ##################################################### Foreign Competitor To * Transition #######################################################
    ################################################################################################################################################

    def test_foreign_competitor_to_single_player_monopoly_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        # same company
        new_away_stores = [Store.simple_init_with_address(2, 1, -1, 1)]
        # different company (i.e. foreign competitors)
        previous_away_stores = [
            Store.standard_init(3, 2, -1, 1, None, None, None, None, "2012-01-20", None, None),
            Store.standard_init(4, 2, -1, 1, None, None, None, None, "2012-01-01", None, None),
            Store.standard_init(5, 1, -1, 1, None, None, None, None, "2012-01-30", None, None)
        ]

        # sync monopolies and verify that a new one is inserted and none are closed
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 1)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.SinglePlayerMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], trade_area_id)
        # verify date matches the largest of the previous foreign away store.
        # this is a key check because there's another company who's not a foreign competitor with a later date!!!!!!!
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(2012, 01, 20))


    def test_foreign_competitor_to_absolute_monopoly_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        # no competitors
        new_away_stores = []
        # different company (i.e. foreign competitors)
        previous_away_stores = [
            Store.standard_init(3, 2, -1, 1, None, None, None, None, "2012-01-20", None, None),
            Store.standard_init(4, 2, -1, 1, None, None, None, None, "2012-01-01", None, None),
            Store.standard_init(5, 1, -1, 1, None, None, None, None, "2012-01-30", None, None)
        ]

        # sync monopolies and verify that a new one is inserted and none are closed
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 1)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.AbsoluteMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], trade_area_id)
        # verify date matches the largest of the previous away store
        # this is a key check because it verifies that it looks at all companies for the date (i.e. not just foreign competitors)
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(2012, 01, 30))


    def test_foreign_competitor_to_foreign_competitor_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        # still a foreign competitor
        new_away_stores = [Store.standard_init(3, 2, -1, 1, None, None, None, None, "2012-01-20", None, None)]
        # different company (i.e. foreign competitors)
        previous_away_stores = [
            Store.standard_init(3, 2, -1, 1, None, None, None, None, "2012-01-20", None, None),
            Store.standard_init(4, 2, -1, 1, None, None, None, None, "2012-01-01", None, None),
            Store.standard_init(5, 1, -1, 1, None, None, None, None, "2012-01-30", None, None)
        ]

        # sync monopolies and verify that nothing is done
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 0)





    ################################################################################################################################################
    ######################################################### New Store To * Transition ############################################################
    ################################################################################################################################################

    def test_new_store_to_single_player_monopoly_transition(self):
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, "2012-01-01", None, None, None)
        # competitor from same company
        new_away_stores = [Store.simple_init_with_address(2, 1, -1, 1)]
        previous_away_stores = []

        # sync monopolies and verify that a new one is inserted and none are closed
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 1)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.SinglePlayerMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], trade_area_id)
        # verify date matches the home store opening date
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(2012, 01, 01))


    def test_new_store_to_absolute_monopoly_transition(self):
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, "2012-01-01", None, None, None)
        new_away_stores = []
        previous_away_stores = []

        # sync monopolies and verify that a new one is inserted and none are closed
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 1)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.AbsoluteMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], trade_area_id)
        # verify date matches the home store opening date
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(2012, 01, 01))


    def test_new_store_to_foreign_competitor_transition(self):
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, "2012-01-01", None, None, None)
        # competitor from different company
        new_away_stores = [Store.simple_init_with_address(2, 2, -1, 1)]
        previous_away_stores = []

        # sync monopolies and verify that nothing happens
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 0)





    ################################################################################################################################################
    ################################################ Single Player Monopoly To * Transition ########################################################
    ################################################################################################################################################

    def test_single_player_to_single_player_monopoly_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        # same company
        new_away_stores = [Store.simple_init_with_address(2, 1, -1, 1)]
        # same company
        previous_away_stores = [Store.simple_init_with_address(2, 1, -1, 1)]

        # sync monopolies and verify that a new one is inserted and non are closed
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 0)


    def test_single_player_to_absolute_monopoly_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        new_away_stores = []
        # same company
        previous_away_stores = [
            Store.standard_init(2, 1, -1, 1, None, None, None, None, "2012-01-10", None, None),
            Store.standard_init(3, 1, -1, 1, None, None, None, None, "2012-01-30", None, None),
            Store.standard_init(4, 1, -1, 1, None, None, None, None, "2012-01-20", None, None)
        ]

        # sync monopolies and verify that a new one is inserted and non are closed
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        # one closed and one opened
        self.assertEqual(len(self._data_repository.closed_monopolies), 1)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 1)
        # new upserted is correct type
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.AbsoluteMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], trade_area_id)
        # verify start_date and end_date = latest close_date from previous stores
        self.assertEqual(self._data_repository.closed_monopolies_dates[0], datetime(2012, 01, 30))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(2012, 01, 30))


    def test_single_player_to_foreign_competitor_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        # has foreign company
        new_away_stores = [
            Store.standard_init(2, 1, -1, 1, None, None, None, "2012-01-20", None, None, None),
            Store.standard_init(3, 1, -1, 1, None, None, None, "2012-01-30", None, None, None),
            Store.standard_init(4, 1, -1, 1, None, None, None, "2012-01-01", None, None, None),
            Store.standard_init(5, 2, -1, 1, None, None, None, "2012-01-05", None, None, None)
        ]
        # same company
        previous_away_stores = [
            Store.simple_init_with_address(2, 1, -1, 1),
            Store.simple_init_with_address(3, 1, -1, 1),
            Store.simple_init_with_address(4, 1, -1, 1),
        ]

        # sync monopolies and verify that a new one is inserted and non are closed
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        # one closed and none opened
        self.assertEqual(len(self._data_repository.closed_monopolies), 1)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 0)
        # verify end_date = earliest start_date from new stores THAT ARE FOREIGN COMPETITORS
        self.assertEqual(self._data_repository.closed_monopolies_dates[0], datetime(2012, 01, 05))



    ################################################################################################################################################
    ################################################## Absolute Monopoly To * Transition ###########################################################
    ################################################################################################################################################

    def test_absolute_monopoly_to_single_player_monopoly_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        # same company
        new_away_stores = [
            Store.standard_init(2, 1, -1, 1, None, None, None, "2012-01-20", None, None, None),
            Store.standard_init(3, 1, -1, 1, None, None, None, "2012-01-01", None, None, None),
            Store.standard_init(4, 1, -1, 1, None, None, None, "2012-01-30", None, None, None)
        ]
        previous_away_stores = []

        # mock up active monopoly in the database to signal that this is not a new store
        self._data_repository.active_monopolies_stores[1] = Monopoly(1, CompetitionType.AbsoluteMonopoly, trade_area_id, None, None)

        # sync monopolies and verify that a new one is inserted and non are closed
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        # one closed and one opened
        self.assertEqual(len(self._data_repository.closed_monopolies), 1)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 1)
        # new upserted is correct type
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.SinglePlayerMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], trade_area_id)
        # verify start_date and end_date = earliest close_date from previous stores
        self.assertEqual(self._data_repository.closed_monopolies_dates[0], datetime(2012, 01, 01))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(2012, 01, 01))


    def test_absolute_monopoly_to_absolute_monopoly_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        new_away_stores = []
        previous_away_stores = []

        # mock up active monopoly in the database to signal that this is not a new store
        self._data_repository.active_monopolies_stores[1] = Monopoly(1, CompetitionType.AbsoluteMonopoly, trade_area_id, None, None)

        # sync monopolies and verify that nothing happens
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 0)


    def test_absolute_monopoly_to_foreign_competitor_transition(self):
        trade_area_id = 10
        home_store = Store.simple_init_with_address(1, 1, -1, -1)
        # different company
        new_away_stores = [
            Store.standard_init(2, 1, -1, 1, None, None, None, "2012-01-30", None, None, None),
            Store.standard_init(3, 1, -1, 1, None, None, None, "2012-01-01", None, None, None),
            Store.standard_init(4, 2, -1, 1, None, None, None, "2012-01-20", None, None, None)
        ]
        previous_away_stores = []

        # mock up active monopoly in the database to signal that this is not a new store
        self._data_repository.active_monopolies_stores[1] = Monopoly(1, CompetitionType.AbsoluteMonopoly, trade_area_id, None, None)

        # sync monopolies and verify that a new one is closed and none inserted
        MonopolyTransitionHelper.transition_monopoly_record(home_store, trade_area_id, new_away_stores, previous_away_stores, self._data_repository, [])
        # one closed and none opened
        self.assertEqual(len(self._data_repository.closed_monopolies), 1)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 0)
        # verify start_date and end_date = earliest close_date from previous stores
        # this is a key check because there's another company who's not a foreign competitor with a later date!!!!!!!
        self.assertEqual(self._data_repository.closed_monopolies_dates[0], datetime(2012, 01, 20))