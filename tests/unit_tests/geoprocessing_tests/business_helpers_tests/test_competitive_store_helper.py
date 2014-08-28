import copy
from datetime import datetime
import unittest
from geoprocessing.business_logic.enums import CompetitionType
from geoprocessing.business_logic.business_helpers.competitive_store_helper import CompetitiveStoreHelper
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.business_logic.config import Config
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository

__author__ = 'erezrubinstein'


class CompetitiveStoreHelperTests(unittest.TestCase):
    def setUp(self):
        # set up dependencies
        register_mock_dependencies()
        self._data_repository = Dependency("DataRepository").value

        # set up fake store
        self._store = Store()
        self._store.store_id = 1
        self._store.company_id = 2

    def doCleanups(self):
        dependencies.clear()




    ################################################################################################################
    ###################################### sync competitive stores tests ###########################################
    ################################################################################################################


    def test_synchronize_competitive_stores__upserts_properly(self):
        """
        This test verifies that calling synchronize_competitive_stores_in_db will insert/update any competitive_stores are new or existing
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._opened_date = "2012-01-01"
        home_store._assumed_opened_date = "2012-01-01"

        # create three mock stores
        existing_competitor = StoreCompetitionInstance.basic_init(2, 2, -1, -1)
        new_competitor = StoreCompetitionInstance.basic_init(4, 4, -1, -1)

        # add the mock stores as existing competitive stores (by id)
        # !!!! VERY IMPORTANT TO DO A DEEP COPY.  This makes it work like a database (i.e. different objects) when doing set comparisons
        self._data_repository.competitive_stores[1] = [copy.deepcopy(existing_competitor)]

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [existing_competitor, new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that the right store was closed
        competitive_stores.synchronize_competitive_stores_in_db()
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [
            competitive_stores._create_batch_competition_structure(existing_competitor, datetime(2012, 01, 01), None, True, home_store.store_id),
            competitive_stores._create_batch_competition_structure(new_competitor, datetime(2012, 01, 01), None, True, home_store.store_id)
        ])
        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)








    ################################################################################################################
    ########################### sync competitive stores upserted Start/End date tests ##############################
    ################################################################################################################




    def test_synchronize_competitive_stores__upsert__away_store_closes_before_home_store_opens(self):
        """
        This verifies that nothing is inserted if stores' open/closed dates do not overlap
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._assumed_opened_date = "2012-01-01"
        home_store._opened_date = "2012-01-01"

        # create three mock stores
        new_competitor = StoreCompetitionInstance.standard_init(4, 4, -1, -1, None, None, "1900-01-01", "2011-01-01", "1900-01-01", "2011-01-01", None, None)

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that nothing was inserted
        competitive_stores.synchronize_competitive_stores_in_db()
        self.assertEqual(len(self._data_repository.upserted_away_stores), 0)
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [])
        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)


    def test_synchronize_competitive_stores__upsert__home_closes_before_away_opens(self):
        """
        This verifies that nothing is inserted if stores' open/closed dates do not overlap
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._assumed_closed_date = "2011-01-01"
        home_store._closed_date = "2011-01-01"

        # create three mock stores
        new_competitor = StoreCompetitionInstance.standard_init(4, 4, -1, -1, None, None, "2012-01-01", None, "2012-01-01", None, None, None)

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that the right store was inserted
        competitive_stores.synchronize_competitive_stores_in_db()
        self.assertEqual(len(self._data_repository.upserted_away_stores), 0)
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [])
        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)


    def test_synchronize_competitive_stores__stores_overlap_in_dates__away_store_opens_first(self):
        """
        This verifies it is inserted if stores' open/closed dates do overlap with away store opened first
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._assumed_opened_date = "2012-01-01"
        home_store._opened_date = "2012-01-01"
        home_store._assumed_closed_date = "2012-12-01"
        home_store._closed_date = "2012-12-01"

        # create three mock stores
        new_competitor = StoreCompetitionInstance.standard_init(4, 4, -1, -1, None, None, "2011-01-01", "2012-05-01", "2011-01-01", "2012-05-01", None, None)

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that the right store was inserted with the right dates
        competitive_stores.synchronize_competitive_stores_in_db()
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [
            competitive_stores._create_batch_competition_structure(new_competitor, datetime(2012, 01, 01), datetime(2012, 05, 01), True, home_store.store_id)
        ])
        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)


    def test_synchronize_competitive_stores__stores_overlap_in_dates__home_store_opens_first(self):
        """
        This verifies that it is inserted if stores' open/closed dates do overlap with home store opened first
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._assumed_opened_date = "2011-01-01"
        home_store._opened_date = "2011-01-01"
        home_store._assumed_closed_date = "2012-05-12"
        home_store._closed_date = "2012-05-12"

        # create three mock stores
        new_competitor = StoreCompetitionInstance.standard_init(4, 4, -1, -1, None, None, "2012-01-01", "2012-12-01", "2012-01-01", "2012-12-01", None, None)

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that the right store was inserted with the right dates
        competitive_stores.synchronize_competitive_stores_in_db()
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [
            competitive_stores._create_batch_competition_structure(new_competitor, datetime(2012, 01, 01), datetime(2012, 05, 12), True, home_store.store_id)
        ])
        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)


    def test_synchronize_competitive_stores__stores_overlap_in_dates__home_store_dates_within_away_store(self):
        """
        This verifies that it is inserted if stores' open/closed dates do overlap with home store contained between the away store dates
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._assumed_opened_date = "2011-01-01"
        home_store._opened_date = "2011-01-01"
        home_store._assumed_closed_date = "2011-12-01"
        home_store._closed_date = "2011-12-01"

        # create three mock stores
        new_competitor = StoreCompetitionInstance.standard_init(4, 4, -1, -1, None, None, "2010-01-01", "2012-12-01", "2010-01-01", "2012-12-01", None, None)

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that the right store was inserted with the right dates
        competitive_stores.synchronize_competitive_stores_in_db()
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [
            competitive_stores._create_batch_competition_structure(new_competitor, datetime(2011, 01, 01), datetime(2011, 12, 01), True, home_store.store_id)
        ])
        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)


    def test_synchronize_competitive_stores__competitive_company_instance_opens_after_closes_before(self):
        """
        This verifies that it is inserted if stores' open/closed dates do overlap with competitive_companies start/closed dates being after/before respectively
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._assumed_opened_date = "2009-01-01"
        home_store._opened_date = "2009-01-01"
        home_store._assumed_closed_date = "2012-12-01"
        home_store._closed_date = "2012-12-01"

        # create three mock stores
        new_competitor = StoreCompetitionInstance.standard_init(4, 4, -1, -1, None, None, "2009-01-01", "2012-12-01", "2009-01-01", "2012-12-01", "2010-01-01", "2010-12-01")

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that the right store was inserted with the right dates
        competitive_stores.synchronize_competitive_stores_in_db()

        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [
            competitive_stores._create_batch_competition_structure(new_competitor, datetime(2010, 01, 01), datetime(2010, 12, 01), True, home_store.store_id)
        ])


    def test_synchronize_competitive_stores__competitive_company_instance_opens_after_competitive_stores_close(self):
        """
        This verifies that NOTHING is inserted if stores' close before companies become competitive
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._assumed_opened_date = "2009-01-01"
        home_store._opened_date = "2009-01-01"
        home_store._assumed_closed_date = "2010-12-01"
        home_store._closed_date = "2010-12-01"

        # create three mock stores
        new_competitor = StoreCompetitionInstance.standard_init(4, 4, -1, -1, None, None, "2009-01-01", "2010-12-01", "2009-01-01", "2010-12-01", "2011-01-01", "2011-12-01")

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that the right store was inserted with the right dates
        competitive_stores.synchronize_competitive_stores_in_db()
        self.assertEqual(len(self._data_repository.upserted_away_stores), 0)
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [])
        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)


    def test_synchronize_competitive_stores__competitive_company_instance_opens_after_competitive_stores(self):
        """
        This verifies that it is inserted if stores' open/closed dates are still open but competitive_companies start after
        """
        # create a mock home store
        home_store = Store()
        home_store.store_id = 1
        home_store.company_id = 1
        home_store._assumed_opened_date = "1900-01-01"
        home_store._opened_date = "1900-01-01"
        home_store._assumed_closed_date = None
        home_store._closed_date = None

        # create three mock stores
        new_competitor = StoreCompetitionInstance.standard_init(4, 4, -1, -1, None, None, "1900-01-01", None, "1900-01-01", None, "2011-01-01", None)

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        away_stores = [new_competitor]
        competitive_stores = CompetitiveStoreHelper(home_store, away_stores, 10, self._data_repository)

        # call synchronize and verify that the right store was inserted with the right dates
        competitive_stores.synchronize_competitive_stores_in_db()
        self.assertEqual(self._data_repository.batch_upserted_competitive_stores, [
            competitive_stores._create_batch_competition_structure(new_competitor, datetime(2011, 1, 1), None, True, home_store.store_id)
        ])
        self.assertEqual(self._data_repository.batch_upserted_trade_area_id, 10)









    ################################################################################################################
    ####################################### sync Monopolies stores tests ###########################################
    ################################################################################################################


    def test_synchronize_monopolies__complete_monopoly_always(self):
        # create home store
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, datetime(2012, 2, 2), None, datetime(2012, 2, 2), None)

        # mock up empty competitive stores
        self._data_repository.competitive_stores[1] = []

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        competitive_stores = CompetitiveStoreHelper(home_store, [], 10, self._data_repository)

        # call synchronize
        competitive_stores.synchronize_monopolies_in_db()

        # old monopolies deleted
        self.assertTrue(self._data_repository.monopolies_deleted)

        # nothing closed
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)

        # absolute monopoly added
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 1)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.AbsoluteMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], trade_area_id)
        # verify dates
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(2012, 2, 2))

        # make sure the batch monopolies upsert was called
        self.assertEqual(self._data_repository.batch_upserted_monopolies_trade_area_id, 10)
        self.assertEqual(self._data_repository.batch_upserted_monopolies_list, [])


    def test_synchronize_monopolies__single_player_monopoly_always(self):
        # create home store
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, datetime(2012, 2, 2), None, datetime(2012, 2, 2), None)

        # mock up same company competitive store
        start_date = datetime(2012, 1, 1)
        self._data_repository.competitive_stores[1] = [ StoreCompetitionInstance.standard_init(2, 1, 1, 1, 1, 1, start_date, None, start_date, None, None, None) ]

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        competitive_stores = CompetitiveStoreHelper(home_store, [], 10, self._data_repository)

        # call synchronize
        competitive_stores.synchronize_monopolies_in_db()

        # old monopolies deleted
        self.assertTrue(self._data_repository.monopolies_deleted)

        # nothing closed
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)

        # monopoly added
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 1)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.SinglePlayerMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], trade_area_id)
        # verify dates
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(2012, 2, 2))

        # make sure the batch monopolies upsert was called
        self.assertEqual(self._data_repository.batch_upserted_monopolies_trade_area_id, 10)
        self.assertEqual(self._data_repository.batch_upserted_monopolies_list, [])


    def test_synchronize_monopolies__has_foreign_competitors_always(self):
        # create home store
        trade_area_id = 10
        start_date = datetime(2012, 1, 1)
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, datetime(2012, 2, 2), None, datetime(2012, 2, 2), None)

        # mock up different company competitive store
        start_date = datetime(2012, 1, 1)
        self._data_repository.competitive_stores[1] = [ StoreCompetitionInstance.standard_init(2, 2, 1, 1, 1, 1, start_date, None, start_date, None, None, None) ]

        # create existing set of competitive stores, which consists of only one of the mock stores and a new competitor
        competitive_stores = CompetitiveStoreHelper(home_store, [], 10, self._data_repository)

        # call synchronize
        competitive_stores.synchronize_monopolies_in_db()

        # old monopolies deleted
        self.assertTrue(self._data_repository.monopolies_deleted)

        # nothing closed
        self.assertEqual(len(self._data_repository.closed_monopolies), 0)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 0)

        # nothing added
        self.assertEqual(len(self._data_repository.upserted_monopolies), 0)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 0)

        # make sure the batch monopolies upsert was called
        self.assertEqual(self._data_repository.batch_upserted_monopolies_trade_area_id, 10)
        self.assertEqual(self._data_repository.batch_upserted_monopolies_list, [])


    def test_synchronize_monopolies__complex__one_same_company__one_separate_company(self):
        # this tests out the following timeline:
        # timeline:   ------- NONE ------- same company ------- NONE ------- separate company ------- NONE -------
        # Monopolies: -------  CM  -------     SPM      -------  CM  -------      HFC         -------  CM  -------


        # create home store
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, datetime(1989, 1, 1), None, datetime(1900, 1, 1), None)

        # mock up competitive stores
        self._data_repository.competitive_stores[1] = [
            # same company
            StoreCompetitionInstance.basic_init_with_dates(2, 1, datetime(2008, 1, 1), datetime(2008, 5, 5)),
            # different company
            StoreCompetitionInstance.basic_init_with_dates(3, 2, datetime(2009, 1, 1), datetime(2010, 1, 1))
        ]

        # go
        competitive_stores = CompetitiveStoreHelper(home_store, [], 10, self._data_repository)
        competitive_stores.synchronize_monopolies_in_db()

        # old monopolies deleted
        self.assertTrue(self._data_repository.monopolies_deleted)

        # closed at three different times
        self.assertEqual(len(self._data_repository.closed_monopolies), 3)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 3)
        self.assertEqual(self._data_repository.closed_monopolies[0], 1)
        self.assertEqual(self._data_repository.closed_monopolies[1], 1)
        self.assertEqual(self._data_repository.closed_monopolies[2], 1)
        self.assertEqual(self._data_repository.closed_monopolies_dates[0], datetime(2008, 1, 1))
        self.assertEqual(self._data_repository.closed_monopolies_dates[1], datetime(2008, 5, 5))
        self.assertEqual(self._data_repository.closed_monopolies_dates[2], datetime(2009, 1, 1))
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[0], 10)
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[1], 10)
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[2], 10)


        # opened at four different times
        self.assertEqual(len(self._data_repository.upserted_monopolies), 4)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 4)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies[1], 1)
        self.assertEqual(self._data_repository.upserted_monopolies[2], 1)
        self.assertEqual(self._data_repository.upserted_monopolies[3], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(1989, 1, 1))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[1], datetime(2008, 1, 1))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[2], datetime(2008, 5, 5))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[3], datetime(2010, 1, 1))
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[1], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[2], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[3], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.AbsoluteMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_types[1], CompetitionType.SinglePlayerMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_types[2], CompetitionType.AbsoluteMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_types[3], CompetitionType.AbsoluteMonopoly)

        # make sure the batch monopolies upsert was called
        self.assertEqual(self._data_repository.batch_upserted_monopolies_trade_area_id, 10)
        self.assertEqual(self._data_repository.batch_upserted_monopolies_list, [])


    def test_synchronize_monopolies__complex__two_same_company__two_separate_company__multiple_overlaps(self):
        # this tests out the following timeline:
        # timeline:   ------- NONE ------- same company ------ same company ----------separate company ------- NONE -------
        # timeline:   ---------------------------- separate company -------------------------------------------------------
        # Monopolies: -------  CM  --------- SPM ------  HFC ----  SPM  ------------------- HFC -------------- CM ---------


        # create home store
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, datetime(1989, 1, 1), None, datetime(1900, 1, 1), None)

        # mock up competitive stores
        self._data_repository.competitive_stores[1] = [
            # same company
            StoreCompetitionInstance.basic_init_with_dates(2, 1, datetime(2008, 1, 1), datetime(2008, 5, 5)),
            # different company (overlapping)
            StoreCompetitionInstance.basic_init_with_dates(3, 2, datetime(2008, 4, 4), datetime(2009, 4, 4)),
            # same company (overlapping)
            StoreCompetitionInstance.basic_init_with_dates(4, 1, datetime(2009, 1, 1), datetime(2010, 1, 1)),
            # different company (NOT overlapping)
            StoreCompetitionInstance.basic_init_with_dates(5, 2, datetime(2011, 6, 6), None)
        ]

        # go
        competitive_stores = CompetitiveStoreHelper(home_store, [], 10, self._data_repository)
        competitive_stores.synchronize_monopolies_in_db()

        # old monopolies deleted
        self.assertTrue(self._data_repository.monopolies_deleted)

        # closed at four different times
        self.assertEqual(len(self._data_repository.closed_monopolies), 4)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 4)
        self.assertEqual(self._data_repository.closed_monopolies[0], 1)
        self.assertEqual(self._data_repository.closed_monopolies[1], 1)
        self.assertEqual(self._data_repository.closed_monopolies[2], 1)
        self.assertEqual(self._data_repository.closed_monopolies[3], 1)
        self.assertEqual(self._data_repository.closed_monopolies_dates[0], datetime(2008, 1, 1))
        self.assertEqual(self._data_repository.closed_monopolies_dates[1], datetime(2008, 4, 4))
        self.assertEqual(self._data_repository.closed_monopolies_dates[2], datetime(2010, 1, 1))
        self.assertEqual(self._data_repository.closed_monopolies_dates[3], datetime(2011, 6, 6))
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[0], 10)
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[1], 10)
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[2], 10)
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[3], 10)

        # opens four different times
        self.assertEqual(len(self._data_repository.upserted_monopolies), 4)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 4)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies[1], 1)
        self.assertEqual(self._data_repository.upserted_monopolies[2], 1)
        self.assertEqual(self._data_repository.upserted_monopolies[3], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(1989, 1, 1))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[1], datetime(2008, 1, 1))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[2], datetime(2009, 4, 4))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[3], datetime(2010, 1, 1))
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[1], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[2], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[3], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.AbsoluteMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_types[1], CompetitionType.SinglePlayerMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_types[2], CompetitionType.SinglePlayerMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_types[3], CompetitionType.AbsoluteMonopoly)

        # make sure the batch monopolies upsert was called
        self.assertEqual(self._data_repository.batch_upserted_monopolies_trade_area_id, 10)
        self.assertEqual(self._data_repository.batch_upserted_monopolies_list, [])



    def test_synchronize_monopolies__complex__one_separate_company__home_company_closes(self):
        # this tests out the following timeline:
        # timeline:   ------- NONE ------- separate company ------- NONE ------- HOME CLOSED
        # Monopolies: -------  CM  -------      HFC         -------  CM  ------- XXXXXXXXXXX

        # create home store
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, datetime(1989, 1, 1), datetime(2010, 1, 1), datetime(1900, 1, 1), datetime(2010, 1, 1))

        # mock up competitive stores
        self._data_repository.competitive_stores[1] = [
            # different company
            StoreCompetitionInstance.basic_init_with_dates(2, 2, datetime(2008, 1, 1), datetime(2008, 5, 5))
        ]

        # go
        competitive_stores = CompetitiveStoreHelper(home_store, [], 10, self._data_repository)
        competitive_stores.synchronize_monopolies_in_db()

        # closed twice
        self.assertEqual(len(self._data_repository.closed_monopolies), 2)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 2)
        self.assertEqual(self._data_repository.closed_monopolies[0], 1)
        self.assertEqual(self._data_repository.closed_monopolies[1], 1)
        self.assertEqual(self._data_repository.closed_monopolies_dates[0], datetime(2008, 1, 1))
        self.assertEqual(self._data_repository.closed_monopolies_dates[1], datetime(2010, 1, 1))
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[0], 10)
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[1], 10)

        # opens twice
        self.assertEqual(len(self._data_repository.upserted_monopolies), 2)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list), 2)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies[1], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(1989, 1, 1))
        self.assertEqual(self._data_repository.upserted_monopolies_dates[1], datetime(2008, 5, 5))
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[1], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.AbsoluteMonopoly)
        self.assertEqual(self._data_repository.upserted_monopolies_types[1], CompetitionType.AbsoluteMonopoly)

        # make sure the batch monopolies upsert was called
        self.assertEqual(self._data_repository.batch_upserted_monopolies_trade_area_id, 10)
        self.assertEqual(self._data_repository.batch_upserted_monopolies_list, [])


    def test_synchronize_monopolies__complex__one_separate_company__home_company_closes__same_time(self):
        # this tests out the following timeline:
        # timeline:   ------- NONE ------- separate company - HOME CLOSED
        # Monopolies: -------  CM  -------      HFC         - XXXXXXXXXXX

        # create home store
        trade_area_id = 10
        home_store = Store.standard_init(1, 1, -1, -1, None, None, None, datetime(1989, 1, 1), datetime(2010, 1, 1), datetime(1900, 1, 1), datetime(2010, 1, 1))

        # mock up competitive stores
        self._data_repository.competitive_stores[1] = [
            # different company
            StoreCompetitionInstance.basic_init_with_dates(2, 2, datetime(2008, 1, 1), datetime(2010, 1, 1))
        ]

        # go
        competitive_stores = CompetitiveStoreHelper(home_store, [], 10, self._data_repository)
        competitive_stores.synchronize_monopolies_in_db()

        # closed twice
        self.assertEqual(len(self._data_repository.closed_monopolies), 2)
        self.assertEqual(len(self._data_repository.closed_monopolies_batch_list), 2)
        self.assertEqual(self._data_repository.closed_monopolies[0], 1)
        self.assertEqual(self._data_repository.closed_monopolies[1], 1)
        self.assertEqual(self._data_repository.closed_monopolies_dates[0], datetime(2008, 1, 1))
        self.assertEqual(self._data_repository.closed_monopolies_dates[1], datetime(2010, 1, 1))
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[0], 10)
        self.assertEqual(self._data_repository.closed_monopolies_trade_areas[1], 10)

        # opens once (second doesn't open because the store is closed)
        self.assertEqual(len(self._data_repository.upserted_monopolies), 1)
        self.assertEqual(len(self._data_repository.upserted_monopolies_batch_list),1)
        self.assertEqual(self._data_repository.upserted_monopolies[0], 1)
        self.assertEqual(self._data_repository.upserted_monopolies_dates[0], datetime(1989, 1, 1))
        self.assertEqual(self._data_repository.upserted_monopolies_trade_areas[0], 10)
        self.assertEqual(self._data_repository.upserted_monopolies_types[0], CompetitionType.AbsoluteMonopoly)

        # make sure the batch monopolies upsert was called
        self.assertEqual(self._data_repository.batch_upserted_monopolies_trade_area_id, 10)
        self.assertEqual(self._data_repository.batch_upserted_monopolies_list, [])

if __name__ == '__main__':
    unittest.main()