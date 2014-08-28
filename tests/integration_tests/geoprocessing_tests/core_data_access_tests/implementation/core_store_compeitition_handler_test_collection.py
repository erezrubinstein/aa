from common.utilities.date_utilities import START_OF_WORLD, END_OF_WORLD
from geoprocessing.business_logic.business_helpers.competitive_store_helper import CompetitiveStoreHelper
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from geoprocessing.data_access.core_data_access.data_repository_core import CoreDataRepository
from tests.integration_tests.utilities.data_access_misc_queries import *
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection


__author__ = 'erezrubinstein'


class CoreStoreCompetitionHandlerTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "core_store_compeitition_handler_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

        # create helper vars for this class
        self.data_repository = CoreDataRepository()

    def setUp(self):

        # create base home/away data
        self.home_company_id = insert_test_company()
        self.away_company_id = insert_test_company()
        self.home_store_id = create_store_with_rir(self.home_company_id)
        self.trade_area_id = insert_test_trade_area(self.home_store_id, self.home_company_id)

    def tearDown(self):

        # delete when ending
        self.mds_access.call_delete_reset_database()



    # -------------------------------------- Begin Testing!! -------------------

    def test_get_competitive_stores(self):

        # create two away stores
        away_store_id_1 = create_store_with_rir(self.away_company_id)
        away_store_id_2 = create_store_with_rir(self.away_company_id)
        away_store_1 = StoreCompetitionInstance.basic_init_with_dates(away_store_id_1, self.away_company_id, datetime(2012, 1, 1), datetime(2013, 1, 1))
        away_store_2 = StoreCompetitionInstance.basic_init_with_dates(away_store_id_2, self.away_company_id, datetime(2012, 2, 2), datetime(2013, 2, 2))

        # insert the competitive stores by syncing the competitive store
        self.data_repository.batch_upsert_competitive_stores(self.trade_area_id, [
            CompetitiveStoreHelper._create_batch_competition_structure(away_store_1, datetime(2012, 1, 1), datetime(2013, 1, 1)),
            CompetitiveStoreHelper._create_batch_competition_structure(away_store_2, datetime(2012, 2, 2), datetime(2013, 2, 2))
        ])

        # select active competitive stores and make sure they match
        competitive_stores = self.data_repository.get_competitive_stores(None, self.trade_area_id)
        self.test_case.assertEqual(len(competitive_stores), 2)
        self.test_case.assertEqual(competitive_stores[0].away_store_id, away_store_id_1)
        self.test_case.assertEqual(competitive_stores[0].company_id, self.away_company_id)
        self.test_case.assertEqual(competitive_stores[0].opened_date, datetime(2012, 1, 1))
        self.test_case.assertEqual(competitive_stores[0].closed_date, datetime(2013, 1, 1))
        self.test_case.assertEqual(competitive_stores[1].away_store_id, away_store_id_2)
        self.test_case.assertEqual(competitive_stores[1].company_id, self.away_company_id)
        self.test_case.assertEqual(competitive_stores[1].opened_date, datetime(2012, 2, 2))
        self.test_case.assertEqual(competitive_stores[1].closed_date, datetime(2013, 2, 2))

    def test_batch_upsert_competitive_stores(self):

        # create an away store
        away_store_id_1 = create_store_with_rir(self.away_company_id)
        away_store_1 = StoreCompetitionInstance.basic_init_with_drive_time(away_store_id_1, self.away_company_id, 1, -1, None, None)


        # -------- Test Insert --------
        # insert the competitive stores by syncing the competitive store
        self.data_repository.batch_upsert_competitive_stores(self.trade_area_id, [CompetitiveStoreHelper._create_batch_competition_structure(away_store_1, START_OF_WORLD, END_OF_WORLD)])

        # select active competitive stores and make sure they match
        competitive_stores = self.data_repository.get_competitive_stores(None, self.trade_area_id)
        self.test_case.assertEqual(competitive_stores, [away_store_1])


        # -------- Test Update --------
        # update the away store end date
        away_store_1 = StoreCompetitionInstance.basic_init_with_drive_time(away_store_id_1, self.away_company_id, 1, -1, None, datetime(2013, 1, 1))
        self.data_repository.batch_upsert_competitive_stores(self.trade_area_id, [CompetitiveStoreHelper._create_batch_competition_structure(away_store_1, START_OF_WORLD, END_OF_WORLD)])

        # re select and verify update worked
        competitive_stores = self.data_repository.get_competitive_stores(None, self.trade_area_id)
        self.test_case.assertEqual(competitive_stores, [away_store_1])


        # -------- Test Insert Again --------

        # create a second store
        away_store_id_2 = create_store_with_rir(self.away_company_id)
        away_store_2 = StoreCompetitionInstance.basic_init_with_drive_time(away_store_id_2, self.away_company_id, 1, -1, None, None)

        # insert both first and second stores
        self.data_repository.batch_upsert_competitive_stores(self.trade_area_id, [
            CompetitiveStoreHelper._create_batch_competition_structure(away_store_1, START_OF_WORLD, END_OF_WORLD),
            CompetitiveStoreHelper._create_batch_competition_structure(away_store_2, START_OF_WORLD, END_OF_WORLD)
        ])

        # re select and verify second insert worked worked
        competitive_stores = self.data_repository.get_competitive_stores(None, self.trade_area_id)
        self.test_case.assertEqual(competitive_stores, [away_store_1, away_store_2])
