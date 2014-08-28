from common.utilities.date_utilities import START_OF_WORLD, END_OF_WORLD
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from geoprocessing.business_logic.business_objects.monopoly import Monopoly
from geoprocessing.data_access.core_data_access.data_repository_core import CoreDataRepository
from tests.integration_tests.utilities.data_access_misc_queries import *
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection


__author__ = 'erezrubinstein'


class CoreMonopolyHandlerTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "core_monopoly_handler_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

        # create helper vars for this class
        self.store_helper = StoreHelper()
        self.data_repository = CoreDataRepository()

    def setUp(self):

        # create base data
        self.home_company_id = insert_test_company()
        self.home_store_id = create_store_with_rir(self.home_company_id)
        self.trade_area_id = insert_test_trade_area(self.home_store_id, self.home_company_id)

    def tearDown(self):

        # delete when ending
        self.mds_access.call_delete_reset_database()

    # -------------------------------------- Begin Testing!! -------------------

    def test_select_active_monopoly_record(self):

        # add a monopoly
        batch_monopolies_list = []
        self.data_repository.insert_monopoly(None, "Test1", self.trade_area_id, datetime.now(), batch_monopolies_list)

        # get the selected active monopoly and make sure it's correct
        active_monopoly = self.data_repository.select_active_monopoly_record(None, self.trade_area_id, batch_monopolies_list)
        self.test_case.assertEqual(active_monopoly, self._create_monopoly_record(None, self.trade_area_id, batch_monopolies_list[0]))

        # close the first, add a second monopoly
        self.data_repository.close_monopoly_record(None, self.trade_area_id, datetime.now(), batch_monopolies_list)
        self.data_repository.insert_monopoly(None, "Test2", self.trade_area_id, datetime.now(), batch_monopolies_list)

        # get the selected active monopoly and make sure it's the second item
        active_monopoly = self.data_repository.select_active_monopoly_record(None, self.trade_area_id, batch_monopolies_list)
        self.test_case.assertEqual(active_monopoly, self._create_monopoly_record(None, self.trade_area_id, batch_monopolies_list[1]))

    def test_insert_close_upsert__basic_stay_closed(self):

        # keep track of start/close date
        start_date = datetime(2012, 1, 1)
        end_date = datetime(2013, 1, 1)

        # base monopolies list
        batch_monopolies_list = []

        # add a monopoly, close it, and save
        self.data_repository.insert_monopoly(None, "Test1", self.trade_area_id, start_date, batch_monopolies_list)
        self.data_repository.close_monopoly_record(None, self.trade_area_id, end_date, batch_monopolies_list)
        self.data_repository.batch_upsert_monopolies(self.trade_area_id, batch_monopolies_list)

        # query the monopolies and verify that there's only one and that it's closed
        monopolies = select_monopolies(self.trade_area_id)
        self.test_case.assertEqual(monopolies, [self._create_monopoly_dict("Test1", start_date, end_date)])

    def test_insert_close_upsert__basic_stay_open(self):

        # keep track of start/close dates
        start_date = datetime(2012, 1, 1)
        end_date = datetime(2013, 1, 1)

        # base monopolies list
        batch_monopolies_list = []

        # add a monopoly, close it, add a second monopoly, and save
        self.data_repository.insert_monopoly(None, "Test1", self.trade_area_id, start_date, batch_monopolies_list)
        self.data_repository.close_monopoly_record(None, self.trade_area_id, end_date, batch_monopolies_list)
        self.data_repository.insert_monopoly(None, "Test2", self.trade_area_id, end_date, batch_monopolies_list)
        self.data_repository.batch_upsert_monopolies(self.trade_area_id, batch_monopolies_list)

        # query the monopolies and verify that there's only one and that it's closed
        monopolies = select_monopolies(self.trade_area_id)
        self.test_case.assertEqual(monopolies, [
            self._create_monopoly_dict("Test1", start_date, end_date),
            self._create_monopoly_dict("Test2", end_date, END_OF_WORLD)
        ])

    def test_insert_close_upsert__complex_series(self):

        # keep track of start/close dates
        start_date_1 = datetime(2012, 1, 1)
        end_date_1 = datetime(2012, 4, 5)
        start_date_2 = datetime(2012, 7, 8)
        end_date_2 = datetime(2013, 1, 1)
        start_date_3 = datetime(2013, 5, 1)

        # base monopolies list
        batch_monopolies_list = []

        # add and close several monopolies
        self.data_repository.insert_monopoly(None, "Test1", self.trade_area_id, start_date_1, batch_monopolies_list)
        self.data_repository.close_monopoly_record(None, self.trade_area_id, end_date_1, batch_monopolies_list)
        self.data_repository.insert_monopoly(None, "Test2", self.trade_area_id, start_date_2, batch_monopolies_list)
        self.data_repository.close_monopoly_record(None, self.trade_area_id, end_date_2, batch_monopolies_list)
        self.data_repository.insert_monopoly(None, "Test3", self.trade_area_id, start_date_3, batch_monopolies_list)
        self.data_repository.batch_upsert_monopolies(self.trade_area_id, batch_monopolies_list)

        # query the monopolies and verify that there's only one and that it's closed
        monopolies = select_monopolies(self.trade_area_id)
        self.test_case.assertEqual(monopolies, [
            self._create_monopoly_dict("Test1", start_date_1, end_date_1),
            self._create_monopoly_dict("Test2", start_date_2, end_date_2),
            self._create_monopoly_dict("Test3", start_date_3, END_OF_WORLD)
        ])

    # ---------------------------- Private Methods ----------------------------

    def _create_monopoly_record(self, store_id, trade_area_id, monopoly_dict):
        return Monopoly(store_id, monopoly_dict["monopoly_type"], trade_area_id, monopoly_dict["start_date"], monopoly_dict["end_date"])

    def _create_monopoly_dict(self, monopoly_type, start_date, end_date):
        return {
            "monopoly_type": monopoly_type,
            "start_date": start_date,
            "end_date": end_date
        }
