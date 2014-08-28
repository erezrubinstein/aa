from bson.objectid import ObjectId
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import parse_date
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import company_helper
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from core.common.utilities.errors import *
from core.common.utilities.helpers import generate_id, parse_timestamp
import mox
import datetime


__author__ = 'vgold'


class StoreHelperTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(StoreHelperTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value
        self.main_access = Dependency("CoreAPIProvider").value
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_store_helper.py"}

        # Set up useful mocks
        self.mock_helper = self.mox.CreateMock(StoreHelper)
        self.mock_helper.logger = self.logger
        self.mock_helper.address_helper = self.mox.CreateMockAnything()
        self.mock_helper.rir_helper = self.mox.CreateMockAnything()
        self.mock_helper.parse_timestamp = self.mox.CreateMockAnything()
        self.mock_helper.is_first_date_later_than_second = self.mox.CreateMockAnything()
        self.mock_helper.main_access = self.mox.CreateMockAnything()
        self.mock_helper.main_access.mds = self.mox.CreateMockAnything()
        self.mock_helper.main_access.wfs = self.mox.CreateMockAnything()
        self.mock_helper.main_params = self.main_params
        self.mock_helper.geoprocessing_helper = self.mox.CreateMockAnything()
        self.mock_helper.trade_area_helper = self.mox.CreateMockAnything()
        self.mock_helper.fast_date_parser = self.mox.CreateMockAnything()

        self.previous_mc_rir = {
            '_id': generate_id(),
            'data': {'as_of_date': '2000-01-01'},
            'link._id': generate_id()
        }

        self.next_mc_rir = {
            '_id': generate_id(),
            'data': {'as_of_date': '2010-01-01'},
            'link._id': generate_id()
        }

        self.other_rir = {
            '_id': generate_id(),
            'data': {'as_of_date': '2013-01-01'},
            'link._id': generate_id()
        }

    def doCleanups(self):

        super(StoreHelperTests, self).doCleanups()
        dependencies.clear()

    def test_create_new_store(self):

        # Check params for call made to get rir
        rir_id = generate_id()
        rir_rec = {"data": {"auto_parsed_address": {"helo": "moto"},
                            "company_name": "company_name",
                            "company_id": "company_id",
                            "as_of_date": "as_of_date"}}
        entity_fields = {"retail_input_record": ["data"]}
        params = self.main_params.mds.create_get_entity_params(entity_fields = entity_fields)
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", rir_id, params["params"]).AndReturn(rir_rec)

        # Make sure return of last call is used for params of this call
        address_id = generate_id()
        self.mock_helper.address_helper.insert_new_address(self.context, rir_id, rir_rec["data"]["auto_parsed_address"], rir_rec["data"]["company_id"]).AndReturn(address_id)

        # Make sure rir data is used for this call
        store_data = {
            "store_number": "store_number",
            "company_id": "company_id",
            "company_name": "company_name"
        }
        self.mock_helper.create_store_data(rir_rec["data"], None).AndReturn(store_data)

        # Make sure return of last call is used for this call
        store_id = generate_id()
        self.mock_helper.main_access.mds.call_add_entity('store', 'company_name_' + str(store_data['store_number']), store_data, self.context,
                                             interval = [rir_rec["data"]['as_of_date'], None]).AndReturn(store_id)

        company_params = {"id": rir_rec["data"]["company_id"], "field_data":{"data.is_initialized_with_stores":True}}
        self.mock_helper.main_access.mds.call_find_and_modify_entity("company", params=company_params, context=self.context)

        # Make sure these calls are made with relevant IDs and rir data
        self.mock_helper.main_access.mds.call_add_link('store', store_id, 'subject', 'address', address_id, 'location', 'address_assignment', self.context)
        self.mock_helper.main_access.mds.call_add_link('company', rir_rec["data"]['company_id'], 'retail_parent', 'store', store_id, 'store', 'store_ownership', self.context)

        # Make sure this call is made with link data formed from calling datetime utcnow
        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn("timestamp")
        self.mock_helper.main_access.mds.call_add_link('store', store_id, 'store', 'retail_input_record', rir_id, 'retail_input_record',
                                           'retail_input', self.context, link_data = {"timestamp": "timestamp"})

        # Make sure this gets called with relevant IDs
        self.mock_helper.main_access.mds.call_add_link('store', store_id, 'store', 'retail_input_record', rir_id, 'most_correct_record', 'retail_input', self.context)

        # Make sure these fields are updated for RIR
        field_data = {"data.is_most_correct": True, "data.is_most_recent": True, "data.was_most_correct": True}
        self.mock_helper.main_access.mds.call_update_entity('retail_input_record', rir_id, self.context, field_data = field_data)
        self.mock_helper._determine_opened_date(rir_rec['data'], rir_rec['data']['company_id']).AndReturn(rir_rec['data']['as_of_date'])

        #self.mock_helper.geoprocessing_helper.evaluate_need_for_geoprocessing("store", store_id, self.context)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", store_id, self.context)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(store_id)
        self.mox.ReplayAll()

        # Call instance method from class with our mock object as first arg
        result = StoreHelper.create_new_store(self.mock_helper, self.context, rir_id, None, async=True)
        self.assertEqual(result, store_id)

    def test_add_rir_to_store__not_most_correct__no_rir_as_of_date__no_check_opened_date(self):

        # Make sure get_as_of_date is called
        rir_id = generate_id()

        self.mock_helper.rir_helper.get_linked_store_id(self.context, rir_id, error_if_absent = False).AndReturn(False)

        as_of_date = "as_of_date"
        self.mock_helper.fast_date_parser.parse_date(as_of_date).AndReturn(as_of_date)
        self.mock_helper.rir_helper.get_as_of_date(self.context, rir_id).AndReturn(as_of_date)

        # Make sure store is updated with timestamp from datetime utcnow
        store_id = generate_id()
        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn("timestamp")
        link_data = {"timestamp": "timestamp"}
        self.mock_helper.main_access.mds.call_add_link('store', store_id, 'store', 'retail_input_record', rir_id, 'retail_input_record',
                                                       'retail_input', self.context, link_data = link_data)

        # Make sure private method is called with output of get_as_of_date above
        self.mock_helper._StoreHelper__check_and_update_most_recent_rir(self.context, store_id, rir_id, as_of_date)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", store_id, self.context, rir_id_list=[rir_id])

        self.mox.ReplayAll()
        StoreHelper.add_rir_to_store(self.mock_helper, self.context, store_id, rir_id, False, rir_as_of_date_str = None, async=True)

    def test_add_rir_to_store__is_most_correct__rir_as_of_date__check_opened_date__does_not_belong_to_other_store(self):

        # Make some IDs
        rir_id = generate_id()
        store_id = generate_id()

        self.mock_helper.rir_helper.get_linked_store_id(self.context, rir_id, error_if_absent = False).AndReturn(False)

        # # Make sure method is called with proper args
        as_of_date = "as_of_date"
        self.mock_helper.fast_date_parser.parse_date(as_of_date).AndReturn(as_of_date)

        # Make sure call_add_link is called with proper params
        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn("timestamp")
        link_data = {"timestamp": "timestamp"}
        self.mock_helper.main_access.mds.call_add_link('store', store_id, 'store', 'retail_input_record', rir_id, 'retail_input_record',
                                                       'retail_input', self.context, link_data = link_data)

        # Make sure methods are called with proper params
        self.mock_helper._StoreHelper__check_and_update_most_recent_rir(self.context, store_id, rir_id, as_of_date)
        self.mock_helper._set_most_correct_rir(self.context, store_id, rir_id, as_of_date, False, None, None)
        self.mock_helper._modify_store_interval_based_on_most_correct_rir_reassignment(store_id, rir_id, None, None, self.context)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", store_id, self.context, rir_id_list=[rir_id])

        self.mox.ReplayAll()
        StoreHelper.add_rir_to_store(self.mock_helper, self.context, store_id, rir_id, True, rir_as_of_date_str = as_of_date, async=True)

    def test_add_rir_to_store_is_most_correct__rir_as_of_date__belongs_to_other_store(self):
        # Make some IDs
        rir_id = generate_id()
        store_id = generate_id()

        self.mock_helper.rir_helper.get_linked_store_id(self.context, rir_id, error_if_absent = False).AndReturn('curr')
        self.mock_helper.remove_rir_from_store(self.context, rir_id, 'curr')

        # # Make sure method is called with proper args
        as_of_date = "as_of_date"
        self.mock_helper.fast_date_parser.parse_date(as_of_date).AndReturn(as_of_date)

        # Make sure call_add_link is called with proper params
        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn("timestamp")
        link_data = {"timestamp": "timestamp"}
        self.mock_helper.main_access.mds.call_add_link('store', store_id, 'store', 'retail_input_record', rir_id, 'retail_input_record',
                                                       'retail_input', self.context, link_data = link_data)

        # Make sure methods are called with proper params
        self.mock_helper._StoreHelper__check_and_update_most_recent_rir(self.context, store_id, rir_id, as_of_date)
        self.mock_helper._set_most_correct_rir(self.context, store_id, rir_id, as_of_date, False, None, None)
        self.mock_helper._modify_store_interval_based_on_most_correct_rir_reassignment(store_id, rir_id, None, None, self.context)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", store_id, self.context, rir_id_list=[rir_id])

        self.mox.ReplayAll()
        StoreHelper.add_rir_to_store(self.mock_helper, self.context, store_id, rir_id, True, rir_as_of_date_str = as_of_date, async=True)

    def test_relocate_store__existing_earlier_than_target__store_does_not_exist(self):

        # Make some IDs
        existing_rir_id = generate_id()
        target_rir_id = generate_id()
        old_store_id = generate_id()

        # Make dicts to return from call_get_entity calls
        existing_rir = {"data": {"as_of_date": 0},
                        "links": self.__get_rir_to_store_link_structure(old_store_id, existing_rir_id)["links"]}
        target_rir = {"data": {"as_of_date": 1},
                      "_id": target_rir_id}

        # Make sure call_get_entity calls happen and return stub data
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", existing_rir_id, None, self.context).AndReturn(existing_rir)
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", target_rir_id, None, self.context).AndReturn(target_rir)

        new_store_rir_id, old_store_rir_id = target_rir_id, existing_rir_id
        new_store_id = generate_id()

        # Make sure methods get called with proper params
        self.mock_helper.rir_helper.get_linked_store_id(self.context, target_rir_id, error_if_absent = False).AndReturn(None)

        self.mock_helper.create_new_store(self.context, new_store_rir_id, async=True).AndReturn(new_store_id)
        self.mock_helper.main_access.mds.call_add_link('store', old_store_id, 'previous_location', 'store', new_store_id, 'next_location', 'retail_relocation', self.context)

        self.mock_helper.find_most_correct_rir(self.context, old_store_id).AndReturn({"entity_id_to": existing_rir_id})
        self.mock_helper.main_access.mds.call_add_link('retail_input_record', existing_rir_id, 'previous_location', 'retail_input_record', new_store_rir_id, 'next_location', 'retail_relocation', self.context)

        self.mock_helper.rir_helper.get_as_of_date(self.context, new_store_rir_id).AndReturn("as_of_date")
        self.mock_helper.close_store(self.context, old_store_id, "as_of_date", async=True)

        #self.mock_helper.geoprocessing_helper.evaluate_need_for_geoprocessing("store", new_store_id, self.context)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", new_store_id, self.context)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(old_store_id)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(new_store_id)
        self.mox.ReplayAll()
        StoreHelper.relocate_store(self.mock_helper, self.context, old_store_id, existing_rir_id, target_rir_id, async=True)


    def test_relocate_store__existing_earlier_than_target__store_exists(self):

        # Make some IDs
        existing_rir_id = generate_id()
        target_rir_id = generate_id()
        old_store_id = generate_id()

        # Make dicts to return from call_get_entity calls
        existing_rir = {"data": {"as_of_date": 0},
                        "links": self.__get_rir_to_store_link_structure(old_store_id, existing_rir_id)["links"]}
        target_rir = {"data": {"as_of_date": 1},
                      "_id": target_rir_id}

        # Make sure call_get_entity calls happen and return stub data
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", existing_rir_id, None, self.context).AndReturn(existing_rir)
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", target_rir_id, None, self.context).AndReturn(target_rir)

        new_store_rir_id, old_store_rir_id = target_rir_id, existing_rir_id
        new_store_id = generate_id()

        # Make sure methods get called with proper params
        self.mock_helper.rir_helper.get_linked_store_id(self.context, target_rir_id, error_if_absent = False).AndReturn(new_store_id)
        self.mock_helper.main_access.mds.call_add_link('store', old_store_id, 'previous_location', 'store', new_store_id, 'next_location', 'retail_relocation', self.context)

        self.mock_helper.find_most_correct_rir(self.context, old_store_id).AndReturn({"entity_id_to": existing_rir_id})
        self.mock_helper.main_access.mds.call_add_link('retail_input_record', existing_rir_id, 'previous_location', 'retail_input_record', new_store_rir_id, 'next_location', 'retail_relocation', self.context)

        self.mock_helper.rir_helper.get_as_of_date(self.context, new_store_rir_id).AndReturn("as_of_date")
        self.mock_helper.close_store(self.context, old_store_id, "as_of_date", async=True)

        #self.mock_helper.geoprocessing_helper.evaluate_need_for_geoprocessing("store", new_store_id, self.context)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", new_store_id, self.context)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(old_store_id)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(new_store_id)
        self.mox.ReplayAll()
        StoreHelper.relocate_store(self.mock_helper, self.context, old_store_id, existing_rir_id, target_rir_id, async=True)


    def test_relocate_store__existing_later_than_target__target_store_exists(self):
        # Make some IDs
        existing_rir_id = generate_id()
        target_rir_id = generate_id()
        old_store_id = generate_id()

        # Stub some data
        existing_rir = {"data": {"as_of_date": 1},
                        "links": self.__get_rir_to_store_link_structure(old_store_id, existing_rir_id)["links"],
                        "_id": existing_rir_id}
        target_rir = {"data": {"as_of_date": 0},
                      "_id": target_rir_id}
        target_store_id = generate_id()

        # Get stub entities
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", existing_rir_id, None, self.context).AndReturn(existing_rir)
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", target_rir_id, None, self.context).AndReturn(target_rir)

        self.mock_helper.rir_helper.get_linked_store_id(self.context, target_rir_id, error_if_absent = False).AndReturn(target_store_id)
        old_store_id = target_store_id
        new_store_rir_id, old_store_rir_id = existing_rir_id, target_rir_id

        new_store_id = generate_id()

        # Make sure to add link
        self.mock_helper.rir_helper.get_linked_store_id(self.context, new_store_rir_id, error_if_absent = False).AndReturn(None)
        self.mock_helper.create_new_store(self.context, new_store_rir_id, async=True).AndReturn(new_store_id)
        self.mock_helper.main_access.mds.call_add_link('store', old_store_id, 'previous_location', 'store', new_store_id, 'next_location', 'retail_relocation', self.context)

        self.mock_helper.find_most_correct_rir(self.context, old_store_id).AndReturn({"entity_id_to": existing_rir_id})
        self.mock_helper.main_access.mds.call_add_link('retail_input_record', existing_rir_id, 'previous_location', 'retail_input_record', new_store_rir_id, 'next_location', 'retail_relocation', self.context)

        self.mock_helper.rir_helper.get_as_of_date(self.context, new_store_rir_id).AndReturn("as_of_date")
        self.mock_helper.close_store(self.context, old_store_id, "as_of_date", async=True)

        #self.mock_helper.geoprocessing_helper.evaluate_need_for_geoprocessing("store", new_store_id, self.context)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", new_store_id, self.context)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(old_store_id)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(new_store_id)
        self.mox.ReplayAll()
        StoreHelper.relocate_store(self.mock_helper, self.context, old_store_id, existing_rir_id, target_rir_id, async=True)

    def test_relocate_store__existing_later_than_target__target_store_does_not_exist(self):
        # Make some IDs
        existing_rir_id = generate_id()
        target_rir_id = generate_id()
        old_store_id = generate_id()

        # Stub some data
        existing_rir = {"data": {"as_of_date": 1},
                        "links": self.__get_rir_to_store_link_structure(old_store_id, existing_rir_id)["links"],
                        "_id": existing_rir_id}
        target_rir = {"data": {"as_of_date": 0},
                      "_id": target_rir_id}

        # Get stub entities
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", existing_rir_id, None, self.context).AndReturn(existing_rir)
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", target_rir_id, None, self.context).AndReturn(target_rir)

        self.mock_helper.rir_helper.get_linked_store_id(self.context, target_rir_id, error_if_absent = False).AndReturn(None)

        # Make sure to delete old retail_input_record link and add new one
        retail_input_link = existing_rir["links"]["store"]["retail_input"][0]
        self.mock_helper.main_access.mds.call_del_link_without_id("retail_input_record", existing_rir_id, "retail_input_record", "store", old_store_id, "store", "retail_input")
        self.mock_helper.main_access.mds.call_add_link("retail_input_record", target_rir_id, "retail_input_record", "store", old_store_id, "store",
                                                       "retail_input", self.context, link_interval = retail_input_link["interval"], link_data = retail_input_link["data"])

        # Make sure to delete old most_correct_record link and add new one
        most_correct_link = existing_rir["links"]["store"]["retail_input"][1]
        self.mock_helper.main_access.mds.call_del_link_without_id("retail_input_record", existing_rir_id, "most_correct_record", "store", old_store_id, "store", "retail_input")
        self.mock_helper.main_access.mds.call_add_link("retail_input_record", target_rir_id, "most_correct_record", "store", old_store_id, "store",
                                                       "retail_input", self.context, link_interval = most_correct_link["interval"], link_data = most_correct_link["data"])

        new_store_rir, old_store_rir = existing_rir, target_rir

        new_store_id = generate_id()

        # Make sure to add link
        self.mock_helper.rir_helper.get_linked_store_id(self.context, new_store_rir['_id'], error_if_absent = False).AndReturn(None)
        self.mock_helper.create_new_store(self.context, new_store_rir['_id'], async=True).AndReturn(new_store_id)
        self.mock_helper.main_access.mds.call_add_link('store', old_store_id, 'previous_location', 'store', new_store_id, 'next_location', 'retail_relocation', self.context)

        self.mock_helper.find_most_correct_rir(self.context, old_store_id).AndReturn({"entity_id_to": existing_rir_id})
        self.mock_helper.main_access.mds.call_add_link('retail_input_record', existing_rir_id, 'previous_location', 'retail_input_record', new_store_rir['_id'], 'next_location', 'retail_relocation', self.context)

        self.mock_helper.rir_helper.get_as_of_date(self.context, new_store_rir['_id']).AndReturn("as_of_date")
        self.mock_helper.close_store(self.context, old_store_id, "as_of_date", async=True)

        #self.mock_helper.geoprocessing_helper.evaluate_need_for_geoprocessing("store", new_store_id, self.context)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", new_store_id, self.context)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(old_store_id)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(new_store_id)
        self.mox.ReplayAll()
        StoreHelper.relocate_store(self.mock_helper, self.context, old_store_id, existing_rir_id, target_rir_id, async=True)


    def test_close_store__no_close_date(self):

        store_id = generate_id()
        open_date = datetime.datetime(2012, 9, 4)
        open_date_str = str(open_date)
        close_date = datetime.datetime(2013, 9, 4)
        close_date_str = str(close_date)

        entity_fields = {"store": ["interval"]}
        params = self.main_params.mds.create_params(resource = "get_entity", entity_fields = entity_fields)

        store_entity = {"interval": [open_date_str, None]}
        self.mock_helper.main_access.mds.call_get_entity("store", store_id, params["params"]).AndReturn(store_entity)

        self.mock_helper.fast_date_parser.parse_date(close_date_str).AndReturn(close_date)
        self.mock_helper.fast_date_parser.parse_date(open_date_str).AndReturn(open_date)

        new_interval = [open_date, close_date]
        self.mock_helper.main_access.mds.call_update_entity("store", store_id, self.context, field_name="interval", field_value=new_interval)
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", store_id, self.context)
        #self.mock_helper.trade_area_helper.upsert_DistanceMiles10_trade_area(store_id)
        self.mox.ReplayAll()
        StoreHelper.close_store(self.mock_helper, self.context, store_id, close_date_str, async=True)


    def test_close_store__already_closed(self):
        store_id = generate_id()
        open_date = datetime.datetime(2012, 9, 4)
        open_date_str = str(open_date)
        close_date = datetime.datetime(2013, 9, 4)
        close_date_str = str(close_date)

        entity_fields = {"store": ["interval"]}
        params = self.main_params.mds.create_params(resource = "get_entity", entity_fields = entity_fields)

        store_entity = {"interval": [open_date_str, close_date_str]}
        self.mock_helper.main_access.mds.call_get_entity("store", store_id, params["params"]).AndReturn(store_entity)

        self.mock_helper.fast_date_parser.parse_date(close_date_str).AndReturn(close_date)
        self.mock_helper.fast_date_parser.parse_date(open_date_str).AndReturn(open_date)
        self.mock_helper.fast_date_parser.parse_date(close_date_str).AndReturn(close_date)

        self.mox.ReplayAll()
        StoreHelper.close_store(self.mock_helper, self.context, store_id, close_date_str)


    def test_create_store_data(self):
        """
        Make sure that a store is created wit hthe right data
        """

        # create a base rir data structure
        company_id = generate_id()
        base_rir_data = {
            "company_id": company_id,
            "company_name": "company_name",
            "phone": "phone123",
            "store_number": "woot",
            "store_format": "chicken",
            "note": "danger_zone"
        }
        additional_data = {}
        store_data = StoreHelper.create_store_data(base_rir_data, additional_data)
        expected_store_data = dict(base_rir_data, phone_clean = "123")
        self.assertEqual(store_data, expected_store_data)

        rir_data = dict(base_rir_data, **{"store_format": "store_format",
                                          "store_number": "store_number",
                                          "note": "note",
                                          "auth_dealer_name": "auth_dealer_name",
                                          "home_page_url": "home_page_url",
                                          "phone_clean": "123"})

        store_data = StoreHelper.create_store_data(dict(rir_data, asdf = "asdf"), additional_data)
        self.assertEqual(store_data, rir_data)

        additional_data = {"asdf": "asdf"}

        store_data = StoreHelper.create_store_data(dict(rir_data, asdf = "asdf"), additional_data)
        self.assertEqual(store_data, dict(rir_data, **additional_data))


    def test_remove_or_delete_rir_is_most_correct__execute_remove_or_delete_rir_from_store(self):
        """
        When calling __execute_remove_or_delete_rir_from_store, when is_most_correct = True,
        call StoreHelper__remove_or_delete_rir_from_store_with_mc_logic
        """
        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store_with_mc_logic(self.context, 'rir_id', 'store_id', True, async=True)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__execute_remove_or_delete_rir_from_store(self.mock_helper, self.context, 'rir_id', True,
                                                                          'store_id', is_most_correct = True)


    def test_remove_or_delete_rir_is_most_correct_called_as_false__execute_remove_or_delete_rir_from_store(self):
        """
        When calling __execute_remove_or_delete_rir_from_store, when is_most_correct = False,
        check if the rir is or was most correct, then call StoreHelper__remove_or_delete_rir_from_store_with_mc_logic
        """
        self.mock_helper._StoreHelper__check_if_rir_is_or_was_most_correct('rir_id').AndReturn(True)

        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store_with_mc_logic(self.context, 'rir_id', 'store_id', True, async=True)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__execute_remove_or_delete_rir_from_store(self.mock_helper, self.context, 'rir_id', True,
                                                                          'store_id', is_most_correct = False)


    def test_remove_or_delete_rir_is_not_most_correct__execute_remove_or_delete_rir_from_store(self):
        """
        When calling __execute_remove_or_delete_rir_from_store, when is_most_correct = False,
        check if the rir is or was most correct, then call _StoreHelper__remove_or_delete_rir_from_store
        """
        self.mock_helper._StoreHelper__check_if_rir_is_or_was_most_correct('rir_id').AndReturn(False)

        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store(self.context, 'rir_id', True, 'store_id')
        self.mock_helper.find_most_recent_rir_for_store(self.context, 'store_id')

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__execute_remove_or_delete_rir_from_store(self.mock_helper, self.context, 'rir_id', True,
                                                                          'store_id', is_most_correct = False)


    def test_delete_rir__remove_or_delete_rir_from_store(self):
        """
        If deleting the RIR entity, just mds delete that shizz
        """
        rir_id = 'rir_id'
        self.mock_helper.main_access.mds.call_del_entity('retail_input_record', rir_id)
        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_rir_from_store(self.mock_helper, self.context, rir_id,
                                                                  True, 'store_id')


    def test_remove_rir_no_store_id__remove_or_delete_rir_from_store(self):
        """
        If removing the RIR entity with no store_id, look that up first then remove
        """
        self.mock_helper.main_params = self.mox.CreateMockAnything()
        self.mock_helper.main_params.mds = self.mox.CreateMockAnything()

        rir_id = generate_id()
        store_id = 'store_id'
        self.mock_helper.rir_helper.get_linked_store_id(self.context, rir_id, False).AndReturn(store_id)
        self.__remove_rir_steps(rir_id, store_id)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_rir_from_store(self.mock_helper, self.context, rir_id, False)


    def test_remove_rir_with_store_id__remove_or_delete_rir_from_store(self):
        """
        If removing the RIR entity with no store_id, look that up first then remove
        """
        self.mock_helper.main_params = self.mox.CreateMockAnything()
        self.mock_helper.main_params.mds = self.mox.CreateMockAnything()

        rir_id = generate_id()
        store_id = 'store_id'
        self.__remove_rir_steps(rir_id, store_id)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_rir_from_store(self.mock_helper, self.context, rir_id, False, store_id)


    def __remove_rir_steps(self, rir_id, store_id):
        """
        Refactoring this to use across multiple tests for __remove_or_delete_rir_from_store
        """
        self.mock_helper.main_access.mds.call_del_link_without_id('retail_input_record', rir_id, 'retail_input_record',
                                                                  'store', store_id, 'store', 'retail_input')
        self.mock_helper.main_access.mds.call_del_link_without_id('retail_input_record', rir_id, 'most_correct_record',
                                                                  'store', store_id, 'store', 'retail_input')
        field_data = {"data.is_most_correct": False, "data.is_most_recent": False, "data.was_most_correct": False}
        self.mock_helper.main_access.mds.call_update_entity('retail_input_record', rir_id, self.context,
                                                            field_data = field_data)

        params = "params"
        self.mock_helper.main_params.mds.create_params(origin = "__remove_or_delete_rir_from_store",
                                                       resource = "find_entities_raw", query = mox.IgnoreArg(),
                                                       entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        linked_addresses = [[rir_id, 'id1', 'link_id1'], [rir_id, 'id2', 'link_id2']]
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', params = mox.IgnoreArg(),
                                                                context = self.context).AndReturn(linked_addresses)
        self.mock_helper.main_access.mds.call_del_link('retail_input_record', rir_id, 'address', 'id1', 'link_id1')
        self.mock_helper.main_access.mds.call_del_link('retail_input_record', rir_id, 'address', 'id2', 'link_id2')


    def test_remove_or_delete_mc_rir_middle__remove_or_delete_rir_from_store_with_mc_logic(self):
        """
        Remove/delete most correct RIR in the middle position of its most correct chain
        """
        mc_chain = {
            'position': 'middle',
            'previous_mc_rir': {},
            'next_mc_rir': {}
        }
        mc_rir_id = 'id'
        store_id = 'store_id'
        self.mock_helper._StoreHelper__check_most_correct_rir_chain_position(self.context, mc_rir_id).AndReturn(mc_chain)
        self.mock_helper._StoreHelper__remove_or_delete_most_correct_rir_middle(self.context, mc_rir_id, True,
                                                                                mc_chain['previous_mc_rir'],
                                                                                mc_chain['next_mc_rir'], store_id)
        self.mock_helper.find_most_recent_rir_for_store(self.context, store_id)
        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_rir_from_store_with_mc_logic(self.mock_helper, self.context,
                                                                                mc_rir_id, store_id, True)


    def test_remove_or_delete_mc_rir_first__remove_or_delete_rir_from_store_with_mc_logic(self):
        """
        Remove/delete most correct RIR in the first position of its most correct chain
        """
        mc_chain = {
            'position': 'first',
            'next_mc_rir': {}
        }
        mc_rir_id = 'id'
        store_id = 'store_id'
        self.mock_helper._StoreHelper__check_most_correct_rir_chain_position(self.context, mc_rir_id).AndReturn(mc_chain)
        self.mock_helper._StoreHelper__remove_or_delete_most_correct_rir_first(self.context, mc_rir_id, True,
                                                                               mc_chain['next_mc_rir'], store_id)
        self.mock_helper.find_most_recent_rir_for_store(self.context, store_id)
        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_rir_from_store_with_mc_logic(self.mock_helper, self.context,
                                                                                mc_rir_id, store_id, True)


    def test_remove_or_delete_mc_rir_last__remove_or_delete_rir_from_store_with_mc_logic(self):
        """
        Remove/delete most correct RIR in the last position of its most correct chain
        """
        mc_chain = {
            'position': 'last',
            'previous_mc_rir': {}
        }
        mc_rir_id = 'id'
        store_id = 'store_id'
        self.mock_helper._StoreHelper__check_most_correct_rir_chain_position(self.context, mc_rir_id).AndReturn(mc_chain)
        self.mock_helper._StoreHelper__remove_or_delete_most_correct_rir_last(self.context, mc_rir_id, True,
                                                                               mc_chain['previous_mc_rir'], store_id)
        self.mock_helper.find_most_recent_rir_for_store(self.context, store_id)
        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_rir_from_store_with_mc_logic(self.mock_helper, self.context,
                                                                                mc_rir_id, store_id, True)


    def test_remove_or_delete_mc_rir_only__remove_or_delete_rir_from_store_with_mc_logic(self):
        """
        Remove/delete most correct RIR, only RIR in most correct chain
        """
        mc_chain = {
            'position': 'only'
        }
        mc_rir_id = 'id'
        store_id = 'store_id'
        self.mock_helper._StoreHelper__check_most_correct_rir_chain_position(self.context, mc_rir_id).AndReturn(mc_chain)
        self.mock_helper._StoreHelper__remove_or_delete_most_correct_rir_only(self.context, mc_rir_id, True, store_id, async=True)
        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_rir_from_store_with_mc_logic(self.mock_helper, self.context,
                                                                                mc_rir_id, store_id, True)


    def test_check_mc_rir_chain_position_middle__check_most_correct_rir_chain_position(self):
        """
        When searching for replaced/replacement rels between rirs, returning a previous and next mc rir should result
        in a 'middle' position dictionary
        """
        self.mock_helper.main_params = self.mox.CreateMockAnything()
        self.mock_helper.main_params.mds = self.mox.CreateMockAnything()

        mc_rir_id = generate_id()
        params = "params"
        self.mock_helper.main_params.mds.create_params(origin = "__check_most_correct_rir_chain_position",
                                                       resource = "find_entities_raw", query = mox.IgnoreArg(),
                                                       entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        rir_with_links = [
            [mc_rir_id, self.other_rir['_id'], "other_link_role", self.other_rir['link._id']],
            [mc_rir_id, self.next_mc_rir['_id'], "replaced", self.next_mc_rir['link._id']],
            [mc_rir_id, self.previous_mc_rir['_id'], "target", self.previous_mc_rir['link._id']],
            [mc_rir_id, self.previous_mc_rir['_id'], "replacement", self.previous_mc_rir['link._id']]
        ]
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', mox.IgnoreArg(),
                                                                self.context).AndReturn(rir_with_links)

        self.mock_helper.main_params.mds.create_params(origin = "__check_most_correct_rir_chain_position",
                                                       resource = "find_entities_raw", query = mox.IgnoreArg(),
                                                       entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        mc_linked_to_rirs = [
            [self.next_mc_rir['_id'], self.next_mc_rir['data']],
            [self.previous_mc_rir['_id'], self.previous_mc_rir['data']]
        ]
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', mox.IgnoreArg(),
                                                                self.context).AndReturn(mc_linked_to_rirs)

        results = {
            'position': 'middle',
            'previous_mc_rir': self.previous_mc_rir,
            'next_mc_rir': self.next_mc_rir
        }
        self.mox.ReplayAll()

        test_results = StoreHelper._StoreHelper__check_most_correct_rir_chain_position(self.mock_helper, self.context,
                                                                                       mc_rir_id)
        self.assertDictEqual(results, test_results)


    def test_check_mc_rir_chain_position_first__check_most_correct_rir_chain_position(self):
        """
        When searching for replaced/replacement rels between rirs, returning only a next mc rir should result
        in a 'first' position dictionary
        """
        self.mock_helper.main_params = self.mox.CreateMockAnything()
        self.mock_helper.main_params.mds = self.mox.CreateMockAnything()

        mc_rir_id = generate_id()
        params = "params"
        self.mock_helper.main_params.mds.create_params(origin = "__check_most_correct_rir_chain_position",
                                                       resource = "find_entities_raw", query = mox.IgnoreArg(),
                                                       entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        rir_with_links = [
            [mc_rir_id, self.other_rir['_id'], "other_link_role", self.other_rir['link._id']],
            [mc_rir_id, self.next_mc_rir['_id'], "replaced", self.next_mc_rir['link._id']],
            [mc_rir_id, self.previous_mc_rir['_id'], "target", self.previous_mc_rir['link._id']]
        ]
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', mox.IgnoreArg(),
                                                                self.context).AndReturn(rir_with_links)

        self.mock_helper.main_params.mds.create_params(origin = "__check_most_correct_rir_chain_position",
                                                       resource = "find_entities_raw", query = mox.IgnoreArg(),
                                                       entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        mc_linked_to_rirs = [
            [self.next_mc_rir['_id'], self.next_mc_rir['data']]
        ]
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', mox.IgnoreArg(),
                                                                self.context).AndReturn(mc_linked_to_rirs)

        results = {
            'position': 'first',
            'previous_mc_rir': {},
            'next_mc_rir': self.next_mc_rir
        }
        self.mox.ReplayAll()

        test_results = StoreHelper._StoreHelper__check_most_correct_rir_chain_position(self.mock_helper, self.context, mc_rir_id)

        self.assertDictEqual(results, test_results)


    def test_check_mc_rir_chain_position_last__check_most_correct_rir_chain_position(self):
        """
        When searching for replaced/replacement rels between rirs, returning only a previous mc rir should result
        in a 'last' position dictionary
        """
        self.mock_helper.main_params = self.mox.CreateMockAnything()
        self.mock_helper.main_params.mds = self.mox.CreateMockAnything()

        mc_rir_id = generate_id()
        params = "params"
        self.mock_helper.main_params.mds.create_params(origin = "__check_most_correct_rir_chain_position",
                                           resource = "find_entities_raw", query = mox.IgnoreArg(),
                                           entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        rir_with_links = [
            [mc_rir_id, self.other_rir['_id'], "other_link_role", self.other_rir['link._id']],
            [mc_rir_id, self.previous_mc_rir['_id'], "replacement", self.previous_mc_rir['link._id']],
            [mc_rir_id, self.previous_mc_rir['_id'], "target", self.previous_mc_rir['link._id']],
        ]
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', mox.IgnoreArg(),
                                                                self.context).AndReturn(rir_with_links)

        self.mock_helper.main_params.mds.create_params(origin = "__check_most_correct_rir_chain_position",
                                           resource = "find_entities_raw", query = mox.IgnoreArg(),
                                           entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        mc_linked_to_rirs = [
            [self.previous_mc_rir['_id'], self.previous_mc_rir['data']]
        ]
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', mox.IgnoreArg(),
                                                                self.context).AndReturn(mc_linked_to_rirs)

        results = {
            'position': 'last',
            'next_mc_rir': {},
            'previous_mc_rir': self.previous_mc_rir
        }
        self.mox.ReplayAll()

        test_results = StoreHelper._StoreHelper__check_most_correct_rir_chain_position(self.mock_helper, self.context,
                                                                                       mc_rir_id)
        self.assertDictEqual(results, test_results)


    def test_check_mc_rir_chain_position_only__check_most_correct_rir_chain_position(self):
        """
        When searching for replaced/replacement rels between rirs, returning no mc rir's should result
        in an 'only' position dictionary
        """
        self.mock_helper.main_params = self.mox.CreateMockAnything()
        self.mock_helper.main_params.mds = self.mox.CreateMockAnything()

        mc_rir_id = generate_id()
        params = "params"
        self.mock_helper.main_params.mds.create_params(origin = "__check_most_correct_rir_chain_position",
                                           resource = "find_entities_raw", query = mox.IgnoreArg(),
                                           entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        rir_with_links = [
            [mc_rir_id, self.other_rir['_id'], "other_link_role", self.other_rir['link._id']],
            [mc_rir_id, self.previous_mc_rir['_id'], "replacement", self.previous_mc_rir['link._id']],
            [mc_rir_id, self.previous_mc_rir['_id'], "target", self.previous_mc_rir['link._id']],
        ]
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', mox.IgnoreArg(),
                                                                self.context).AndReturn(rir_with_links)

        self.mock_helper.main_params.mds.create_params(origin = "__check_most_correct_rir_chain_position",
                                           resource = "find_entities_raw", query = mox.IgnoreArg(),
                                           entity_fields = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})
        mc_linked_to_rirs = []
        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record', mox.IgnoreArg(),
                                                                self.context).AndReturn(mc_linked_to_rirs)

        results = {
            'position': 'only',
            'next_mc_rir': {},
            'previous_mc_rir': {}
        }
        self.mox.ReplayAll()

        test_results = StoreHelper._StoreHelper__check_most_correct_rir_chain_position(self.mock_helper, self.context,
                                                                                       mc_rir_id)
        self.assertDictEqual(results, test_results)


    def test_delete_mc_rir_middle__remove_or_delete_most_correct_rir_middle(self):
        """
        Delete a most correct RIR in the middle position
        """
        mc_rir_id = 'mc_id'
        prev_parsed_date = parse_timestamp(self.previous_mc_rir['data']['as_of_date'])
        next_parsed_date = parse_timestamp(self.next_mc_rir['data']['as_of_date'])

        self.mock_helper.main_access.mds.call_del_entity('retail_input_record', mc_rir_id)
        self.mock_helper.fast_date_parser.parse_date(self.previous_mc_rir['data']['as_of_date']).AndReturn(prev_parsed_date)
        self.mock_helper.fast_date_parser.parse_date(self.next_mc_rir['data']['as_of_date']).AndReturn(next_parsed_date)

        link_interval = (parse_timestamp(self.previous_mc_rir['data']['as_of_date']),
                         parse_timestamp(self.next_mc_rir['data']['as_of_date']))
        self.mock_helper.main_access.mds.call_add_link('retail_input_record', self.previous_mc_rir['_id'], 'replaced',
                                                       'retail_input_record', self.next_mc_rir['_id'],'replacement',
                                                       'retail_input', self.context, link_interval = link_interval)
        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_middle(self.mock_helper, self.context, mc_rir_id,
                                                                           True, self.previous_mc_rir, self.next_mc_rir)


    def test_remove_mc_rir_middle__remove_or_delete_most_correct_rir_middle(self):
        """
        Remove a most correct RIR in the middle position
        """
        mc_rir_id = 'mc_id'
        prev_parsed_date = parse_timestamp(self.previous_mc_rir['data']['as_of_date'])
        next_parsed_date = parse_timestamp(self.next_mc_rir['data']['as_of_date'])

        self.mock_helper.main_access.mds.call_del_link('retail_input_record', mc_rir_id,
                                                       'retail_input_record', self.next_mc_rir['_id'],
                                                       self.next_mc_rir['link._id'])
        self.mock_helper.main_access.mds.call_del_link('retail_input_record', mc_rir_id,
                                                       'retail_input_record', self.previous_mc_rir['_id'],
                                                       self.previous_mc_rir['link._id'])
        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store(self.context, mc_rir_id, False, None)

        self.mock_helper.fast_date_parser.parse_date(self.previous_mc_rir['data']['as_of_date']).AndReturn(prev_parsed_date)
        self.mock_helper.fast_date_parser.parse_date(self.next_mc_rir['data']['as_of_date']).AndReturn(next_parsed_date)

        link_interval = (parse_timestamp(self.previous_mc_rir['data']['as_of_date']),
                         parse_timestamp(self.next_mc_rir['data']['as_of_date']))
        self.mock_helper.main_access.mds.call_add_link('retail_input_record', self.previous_mc_rir['_id'], 'replaced',
                                                       'retail_input_record', self.next_mc_rir['_id'],'replacement',
                                                       'retail_input', self.context, link_interval = link_interval)
        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_middle(self.mock_helper, self.context, mc_rir_id,
                                                                           False, self.previous_mc_rir, self.next_mc_rir)


    def test_delete_mc_rir_first__remove_or_delete_most_correct_rir_first(self):
        """
        Delete a mc rir first in the chain
        """
        mc_rir_id = 'mc'
        self.mock_helper.main_access.mds.call_del_entity('retail_input_record', mc_rir_id)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_first(self.mock_helper, self.context, mc_rir_id,
                                                                          True, self.next_mc_rir)


    def test_remove_mc_rir_first__remove_or_delete_most_correct_rir_first(self):
        """
        Remove a mc rir first in the chain
        """
        mc_rir_id = 'mc'
        self.mock_helper.main_access.mds.call_del_link('retail_input_record', mc_rir_id,
                                                       'retail_input_record', self.next_mc_rir['_id'],
                                                       self.next_mc_rir['link._id'])
        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store(self.context, mc_rir_id, False, None)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_first(self.mock_helper, self.context, mc_rir_id,
                                                                          False, self.next_mc_rir)


    def test_delete_mc_rir_last_no_store_id__remove_or_delete_most_correct_rir_last(self):
        """
        Delete a mc rir first in the chain, no store_id given
        """
        store_id = 'store'
        mc_rir_id = 'mc'
        self.mock_helper.rir_helper.get_linked_store_id(self.context, mc_rir_id, False).AndReturn(store_id)
        self.mock_helper.main_access.mds.call_del_entity('retail_input_record', mc_rir_id)
        self.mock_helper._StoreHelper__link_store_to_most_correct_rir(self.context, store_id,
                                                                      self.previous_mc_rir['_id'])

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_last(self.mock_helper, self.context, mc_rir_id,
                                                                         True, self.previous_mc_rir)


    def test_delete_mc_rir_last_with_store_id__remove_or_delete_most_correct_rir_last(self):
        """
        Delete a mc rir first in the chain, store_id is given
        """
        store_id = 'store'
        mc_rir_id = 'mc'
        self.mock_helper.main_access.mds.call_del_entity('retail_input_record', mc_rir_id)
        self.mock_helper._StoreHelper__link_store_to_most_correct_rir(self.context, store_id,
                                                                      self.previous_mc_rir['_id'])

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_last(self.mock_helper, self.context, mc_rir_id,
                                                                         True, self.previous_mc_rir, store_id)


    def test_remove_mc_rir_last_no_store_id__remove_or_delete_most_correct_rir_last(self):
        """
        Remove a mc rir first in the chain, no store_id given
        """
        store_id = 'store'
        mc_rir_id = 'mc'
        self.mock_helper.rir_helper.get_linked_store_id(self.context, mc_rir_id, False).AndReturn(store_id)
        self.mock_helper.main_access.mds.call_del_link('retail_input_record', mc_rir_id,
                                           'retail_input_record', self.previous_mc_rir['_id'],
                                           self.previous_mc_rir['link._id'])
        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store(self.context, mc_rir_id, False, store_id)
        self.mock_helper._StoreHelper__link_store_to_most_correct_rir(self.context, store_id,
                                                                      self.previous_mc_rir['_id'])

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_last(self.mock_helper, self.context, mc_rir_id,
                                                                         False, self.previous_mc_rir)


    def test_remove_mc_rir_last_with_store_id__remove_or_delete_most_correct_rir_last(self):
        """
        Remove a mc rir last in the chain, store_id is given
        """
        store_id = 'store'
        mc_rir_id = 'mc'

        self.mock_helper.main_access.mds.call_del_link('retail_input_record', mc_rir_id,
                                           'retail_input_record', self.previous_mc_rir['_id'],
                                           self.previous_mc_rir['link._id'])
        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store(self.context, mc_rir_id, False, store_id)
        self.mock_helper._StoreHelper__link_store_to_most_correct_rir(self.context, store_id,
                                                                      self.previous_mc_rir['_id'])

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_last(self.mock_helper, self.context, mc_rir_id,
                                                                         False, self.previous_mc_rir, store_id)


    def test_remove_mc_rir_only_no_store_id__remove_or_delete_most_correct_rir_only(self):
        """
        Remove an mc rir, only one, no store_id given
        """
        store_id = 'store'
        mc_rir_id = 'mc'
        self.mock_helper.rir_helper.get_linked_store_id(self.context, mc_rir_id).AndReturn(store_id)
        self.mock_helper.delete_store_by_id(self.context, store_id, async=True)
        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store(self.context, mc_rir_id, False, store_id)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_only(self.mock_helper, self.context, mc_rir_id,
                                                                         False)


    def test_remove_mc_rir_only_with_store_id__remove_or_delete_most_correct_rir_only(self):
        """
        Remove an mc rir, only one, store_id given
        """
        store_id = 'store'
        mc_rir_id = 'mc'
        self.mock_helper.delete_store_by_id(self.context, store_id, async=True)
        self.mock_helper._StoreHelper__remove_or_delete_rir_from_store(self.context, mc_rir_id, False, store_id)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_only(self.mock_helper, self.context, mc_rir_id,
                                                                         False, store_id)


    def test_delete_mc_rir_only_no_store_id__remove_or_delete_most_correct_rir_only(self):
        """
        Delete an mc rir, only one, no store_id given
        """
        store_id = 'store'
        mc_rir_id = 'mc'
        self.mock_helper.rir_helper.get_linked_store_id(self.context, mc_rir_id).AndReturn(store_id)
        self.mock_helper.delete_store_by_id(self.context, store_id, async=True)
        self.mock_helper.main_access.mds.call_del_entity('retail_input_record', mc_rir_id)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_only(self.mock_helper, self.context, mc_rir_id,
                                                                         True)


    def test_delete_mc_rir_only_with_store_id__remove_or_delete_most_correct_rir_only(self):
        """
        Delete an mc rir, only one, store_id given
        """
        store_id = 'store'
        mc_rir_id = 'mc'
        self.mock_helper.delete_store_by_id(self.context, store_id, async=True)
        self.mock_helper.main_access.mds.call_del_entity('retail_input_record', mc_rir_id)

        self.mox.ReplayAll()

        StoreHelper._StoreHelper__remove_or_delete_most_correct_rir_only(self.mock_helper, self.context, mc_rir_id,
                                                                         True, store_id)

    def test_get_store_address_id(self):

        store_id = generate_id()
        address_id = generate_id()

        store_entity = [[1, address_id]]
        self.mock_helper.main_access.mds.call_find_entities_raw("store", params = mox.IgnoreArg(), context = mox.IgnoreArg(), encode_and_decode_results=False).AndReturn(store_entity)

        self.mox.ReplayAll()
        result = StoreHelper.get_store_address_id(self.mock_helper, self.context, store_id)
        self.assertEqual(result, address_id)

    def test_get_store_address_id__no_address(self):

        store_id = generate_id()

        store_entity = []
        self.mock_helper.main_access.mds.call_find_entities_raw("store", params = mox.IgnoreArg(), context = mox.IgnoreArg(), encode_and_decode_results=False).AndReturn(store_entity)

        self.mox.ReplayAll()
        result = StoreHelper.get_store_address_id(self.mock_helper, self.context, store_id)
        self.assertEqual(result, None)

    def test_delete_store_by_id(self):

        store_id = generate_id()
        address_id = generate_id()
        self.mock_helper.get_store_address_id(self.context, store_id).AndReturn(address_id)

        self.mock_helper.main_access.mds.call_del_entity("address", address_id, error_if_absent = False)

        self.mock_helper.main_access.mds.call_del_entity("store", store_id, error_if_absent = False).AndReturn("asdf")
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", store_id, self.context)

        self.mox.ReplayAll()
        result = StoreHelper.delete_store_by_id(self.mock_helper, self.context, store_id, async=True)
        self.assertEqual(result, "asdf")

    def test_delete_store_by_id__no_address(self):

        store_id = generate_id()
        self.mock_helper.get_store_address_id(self.context, store_id).AndReturn(None)

        self.mock_helper.main_access.mds.call_del_entity("store", store_id, error_if_absent = False).AndReturn("asdf")
        self.mock_helper._store_helper_async_task("update_rirs_with_store_interval", "store_id", store_id, self.context)

        self.mox.ReplayAll()
        result = StoreHelper.delete_store_by_id(self.mock_helper, self.context, store_id, async=True)
        self.assertEqual(result, "asdf")

    def test_find_most_correct_rir(self):

        store_id = generate_id()

        results = [[1, 2, "most_correct_record", 4]]
        self.mock_helper.main_access.mds.call_find_entities_raw('store', params = mox.IgnoreArg(), context = mox.IgnoreArg(), encode_and_decode_results=False).AndReturn(results)

        self.mox.ReplayAll()
        result = StoreHelper.find_most_correct_rir(self.mock_helper, self.context, store_id)
        self.assertEqual(result, {"entity_id_to": 2, "_id": 4})

    def test_find_most_correct_rir__no_most_correct(self):

        store_id = generate_id()

        results = []
        self.mock_helper.main_access.mds.call_find_entities_raw('store', params = mox.IgnoreArg(), context = mox.IgnoreArg(), encode_and_decode_results=False).AndReturn(results)

        self.mox.ReplayAll()
        self.assertRaises(DataError, StoreHelper.find_most_correct_rir, *(self.mock_helper, self.context, store_id))

    def test_find_most_correct_rir__multiple_most_correct(self):

        store_id = generate_id()

        results = [[1, 2, "most_correct_record", 4], [1, 9, "most_correct_record", 4]]
        self.mock_helper.main_access.mds.call_find_entities_raw('store', params = mox.IgnoreArg(), context = mox.IgnoreArg(), encode_and_decode_results=False).AndReturn(results)

        self.mox.ReplayAll()
        self.assertRaises(DataError, StoreHelper.find_most_correct_rir, *(self.mock_helper, self.context, store_id))

    def test_check_and_update_most_recent_rir(self):

        store_id = generate_id()
        rir_id = generate_id()
        rir_as_of_date = str(datetime.datetime(2013, 4, 4))

        mr_rir = {"_id": generate_id(), "as_of_date": str(datetime.datetime(2012, 9, 4))}
        self.mock_helper.find_most_recent_rir_for_store(self.context, store_id).AndReturn(mr_rir)

        self.mock_helper.main_access.mds.call_update_entity("retail_input_record", mr_rir['_id'], self.context, field_name = 'data.is_most_recent', field_value = False)
        self.mock_helper.main_access.mds.call_update_entity("retail_input_record", rir_id, self.context, field_name = 'data.is_most_recent', field_value = True)

        self.mox.ReplayAll()
        StoreHelper._StoreHelper__check_and_update_most_recent_rir(self.mock_helper, self.context, store_id, rir_id, rir_as_of_date)

    ##############################################################
    # StoreHelper.find_most_recent_rir_for_store()

    def test_find_most_recent_rir_for_store(self):

        store_id = generate_id()

        results = [[1, None, 3, 4]]
        self.mock_helper._get_most_recent_sorted_rirs_linked_to_from_store_and_repair_if_necessary(store_id, self.context).AndReturn(results)

        self.mox.ReplayAll()
        result = StoreHelper.find_most_recent_rir_for_store(self.mock_helper, self.context, store_id)
        self.assertDictEqual(
            result,
            {
                "_id": 1,
                "is_most_recent": 3,
                "source_type": 4
            }
        )

    def test_find_most_recent_rir_for_store__with_as_of_date(self):

        store_id = generate_id()

        results = [[1, 2, 3, 4]]
        self.mock_helper._get_most_recent_sorted_rirs_linked_to_from_store_and_repair_if_necessary(store_id, self.context).AndReturn(results)

        self.mock_helper.fast_date_parser.parse_date(2).AndReturn(2)

        self.mox.ReplayAll()
        result = StoreHelper.find_most_recent_rir_for_store(self.mock_helper, self.context, store_id)
        self.assertDictEqual(
            result,
            {
                "_id": 1,
                "as_of_date": 2,
                "is_most_recent": 3,
                "source_type": 4
            }
        )

    def test_get_most_recent_sorted_rirs_linked_to_from_store_and_repair_if_necessary(self):

        store_id = generate_id()

        id1 = ObjectId()
        id2 = ObjectId()
        id3 = ObjectId()
        id4 = ObjectId()

        id5 = ObjectId()
        id6 = ObjectId()
        id7 = ObjectId()
        id8 = ObjectId()

        results = [[id1, id2, id3, id4], [id5, id6, id7, id8]]
        self.mock_helper._get_rirs_linked_to_from_store(store_id, self.context).AndReturn(results)

        rows = sorted(results, key=lambda x: x[1])

        most_recent_rir = rows[-1]
        record = {"_id": most_recent_rir[0], "data": {"is_most_recent": True}}
        params = {"id": most_recent_rir[0], "field_data": {"data.is_most_recent": True}}
        self.mock_helper.main_access.mds.call_find_and_modify_entity("retail_input_record", params=params, context=self.context).AndReturn([record])

        erroneous_most_recent_rirs = [rir for rir in rows[:-1] if rir[2]]
        record = {"_id": erroneous_most_recent_rirs[0][0], "data": {"is_most_recent": False}}
        params = {"id": erroneous_most_recent_rirs[0][0], "field_data": {"data.is_most_recent": False}}
        self.mock_helper.main_access.mds.call_find_and_modify_entity("retail_input_record", params=params, context=self.context).AndReturn([record])

        self.mock_helper._get_rirs_linked_to_from_store(store_id, self.context).AndReturn(results)

        self.mox.ReplayAll()

        StoreHelper._get_most_recent_sorted_rirs_linked_to_from_store_and_repair_if_necessary(self.mock_helper, store_id, self.context)
        self.assertEqual(most_recent_rir[2], id7)
        self.assertEqual(len(erroneous_most_recent_rirs), 1)
        self.assertEqual(erroneous_most_recent_rirs[0][2], id3)

    def test_get_most_recent_sorted_rirs_linked_to_from_store_and_repair_if_necessary__no_rirs(self):

        store_id = generate_id()

        results = []
        self.mock_helper._get_rirs_linked_to_from_store(store_id, self.context).AndReturn(results)

        self.mox.ReplayAll()

        self.assertRaises(DataError, StoreHelper._get_most_recent_sorted_rirs_linked_to_from_store_and_repair_if_necessary, *(self.mock_helper, store_id, self.context))


    ##############################################################

    def test_set_most_correct_rir__no_most_correct_rir(self):

        store_id = generate_id()
        rir_id = generate_id()
        rir_as_of_date = str(datetime.datetime(2012, 9, 4))

        self.mock_helper.find_most_correct_rir(self.context, store_id).AndReturn({})
        self.mock_helper._StoreHelper__link_store_to_most_correct_rir(self.context, store_id, rir_id, False, None, None)

        self.mox.ReplayAll()
        StoreHelper._set_most_correct_rir(self.mock_helper, self.context, store_id, rir_id, rir_as_of_date, False, None, None)


    def test_set_most_correct_rir__most_correct_rir_exists(self):
        store_id = generate_id()
        rir_id = generate_id()
        rir_as_of_date = str(datetime.datetime(2012, 9, 4))

        mc_rir = {"entity_id_to": generate_id(), "_id": generate_id()}
        self.mock_helper.find_most_correct_rir(self.context, store_id).AndReturn(mc_rir)

        self.mock_helper._StoreHelper__replace_most_correct_rir(self.context, mc_rir['entity_id_to'], rir_id, mc_rir['_id'], store_id, rir_as_of_date, False)

        self.mock_helper._StoreHelper__link_store_to_most_correct_rir(self.context, store_id, rir_id, False, None, None)

        self.mox.ReplayAll()
        StoreHelper._set_most_correct_rir(self.mock_helper, self.context, store_id, rir_id, rir_as_of_date, False, None, None)

    def test_replace_most_correct_rir(self):

        store_id = generate_id()
        replaced_rir_id = generate_id()
        replacement_rir_id = generate_id()
        link_id = generate_id()
        replacement_rir_as_of_date = str(datetime.datetime(2012, 9, 4))

        self.mock_helper.main_access.mds.call_update_entity('retail_input_record', replaced_rir_id, self.context, field_name = 'data.is_most_correct', field_value = False)
        self.mock_helper.main_access.mds.call_del_link('store', store_id, 'retail_input_record', replaced_rir_id, link_id)

        self.mock_helper.rir_helper.get_as_of_date(self.context, replaced_rir_id).AndReturn("asdf1")
        self.mock_helper.fast_date_parser.parse_date(replacement_rir_as_of_date).AndReturn("asdf2")

        self.mock_helper.main_access.mds.call_add_link('retail_input_record', replaced_rir_id, 'replaced', 'retail_input_record', replacement_rir_id,'replacement',
                                                       'retail_input', self.context, link_interval = ("asdf1", "asdf2")).AndReturn("asdf3")

        self.mox.ReplayAll()
        result = StoreHelper._StoreHelper__replace_most_correct_rir(self.mock_helper, self.context, replaced_rir_id, replacement_rir_id,
                                                                    link_id, store_id, replacement_rir_as_of_date)

        self.assertEqual(result, "asdf3")

    def test_link_store_to_most_correct_rir(self):

        store_id = generate_id()
        rir_id = generate_id()
        address_id = generate_id()

        field_data = {"data.is_most_correct": True, "data.was_most_correct": True}

        self.mock_helper.main_access.mds.call_add_link('store', store_id, 'store', 'retail_input_record', rir_id, 'most_correct_record', 'retail_input', self.context)
        self.mock_helper.main_access.mds.call_update_entity('retail_input_record', rir_id, self.context, field_data = field_data)

        self.mock_helper.get_store_address_id(self.context, store_id).AndReturn(address_id)
        self.mock_helper.address_helper.update_address(self.context, address_id, rir_id, None)
        self.mock_helper._update_store_with_rir(self.context, store_id, rir_id, None)

        self.mox.ReplayAll()
        StoreHelper._StoreHelper__link_store_to_most_correct_rir(self.mock_helper, self.context, store_id, rir_id)

    def test_update_store_with_rir(self):
        # Check params for call made to get rir
        rir_id = generate_id()
        phone_number = "123-456-7890"
        clean_phone_number ="1234567890"
        rir_rec = {
                    "data":
                       {
                        "note": "hello",
                        "phone": phone_number,
                        "store_format":"Cafe",
                        "store_number":"314"
                        }
                    }

        entity_fields = {"retail_input_record": ["data"]}
        params = self.mock_helper.main_params.mds.create_get_entity_params(entity_fields=entity_fields)
        self.mock_helper.main_access.mds.call_get_entity("retail_input_record", rir_id, params["params"]).AndReturn(rir_rec)

        store_id = generate_id()
        self.mock_helper.clean_phone_format(phone_number).AndReturn(clean_phone_number)
        store_data = {
            "data.note": rir_rec["data"]["note"],
            "data.phone": rir_rec["data"]["phone"],
            "data.phone_clean": StoreHelper.clean_phone_format(rir_rec["data"]["phone"]),
            "data.store_format": rir_rec["data"]["store_format"],
            "data.store_number": rir_rec["data"]["store_number"]
        }

        self.mock_helper.main_access.mds.call_update_entity("store", store_id, self.context, field_data=store_data)
        self.mox.ReplayAll()

        StoreHelper._update_store_with_rir(self.mock_helper, self.context, store_id, rir_id)

    # ____________________________________________ Close Date Logic ___________________________________________ #

    def test_determine_close_date_no_comprehensive_file_for_company(self):

        self.mox.StubOutWithMock(company_helper, 'find_comprehensive_retail_input_files_for_company_on_interval')

        company_id = 1
        potential_closed_date = datetime.datetime(2013, 05, 18)
        store_as_of_date = datetime.datetime(2013, 05, 01)

        company_helper.find_comprehensive_retail_input_files_for_company_on_interval(company_id, [store_as_of_date, potential_closed_date]).AndReturn([])
        self.mox.ReplayAll()
        close_date = StoreHelper()._determine_closed_date(potential_closed_date, company_id, store_as_of_date)

        self.assertEqual(close_date, potential_closed_date)


    def test_determine_close_date_comprehensive_file_within_interval_for_company(self):

        self.mox.StubOutWithMock(company_helper, 'find_comprehensive_retail_input_files_for_company_on_interval')

        company_id = 1
        potential_closed_date = datetime.datetime(2013, 05, 18)
        store_as_of_date = datetime.datetime(2013, 05, 01)

        mock_file = {
            'data': {
                'as_of_date': datetime.datetime(2013, 05, 10)
            }
        }

        company_helper.find_comprehensive_retail_input_files_for_company_on_interval(company_id, [store_as_of_date, potential_closed_date]).AndReturn([mock_file])
        self.mox.ReplayAll()
        close_date = StoreHelper()._determine_closed_date(potential_closed_date, company_id, store_as_of_date)

        self.assertEqual(close_date, mock_file['data']['as_of_date'])

    # ____________________________________________ Open Date Logic ___________________________________________ #

    def test_determine_opened_date__has_certainty(self):

        company_id = 1
        rir_data = {
            'as_of_date': datetime.datetime(2013, 05, 18),
            'as_of_date_is_opened_date': True
        }

        open_date = StoreHelper()._determine_opened_date(rir_data, company_id)
        self.assertEqual(open_date, rir_data['as_of_date'])

    def test_determine_opened_date__no_comprehensive_file_for_company__no_certainty(self):

        self.mox.StubOutWithMock(company_helper, 'find_comprehensive_retail_input_files_for_company_on_interval')

        company_id = 1
        rir_data = {
            'as_of_date': datetime.datetime(2013, 05, 18),
            'as_of_date_is_opened_date': False
        }

        company_helper.find_comprehensive_retail_input_files_for_company_on_interval(company_id, [None, rir_data['as_of_date']]).AndReturn([])
        self.mox.ReplayAll()

        open_date = StoreHelper()._determine_opened_date(rir_data, company_id)
        self.assertEqual(open_date, None)

    def test_determine_opened_date__with_comprehensive_file_for_company__no_certainty(self):

        self.mox.StubOutWithMock(company_helper, 'find_comprehensive_retail_input_files_for_company_on_interval')

        company_id = 1
        rir_data = {
            'as_of_date': datetime.datetime(2013, 05, 18),
            'as_of_date_is_opened_date': False
        }
        mock_file = {
            'data': {
                'as_of_date': datetime.datetime(2013, 05, 10)
            }
        }


        company_helper.find_comprehensive_retail_input_files_for_company_on_interval(company_id, [None, rir_data['as_of_date']]).AndReturn([mock_file])
        self.mox.ReplayAll()

        open_date = StoreHelper()._determine_opened_date(rir_data, company_id)
        self.assertEqual(open_date, rir_data['as_of_date'])

    # __________________________________ Store Interval Reassignment Logic __________________________________ #

    def test_modify_store_interval_based_on_most_correct_rir_reassignment__has_certainty(self):

        rir_id = generate_id()

        rir_entity = {
            'data': {
                'as_of_date_is_opened_date': True,
                'as_of_date': '1990-05-18T00:00:00'
            }
        }

        entity_fields = ['_id', 'data']
        query = {'_id': ObjectId(rir_id)}
        params = self.main_params.mds.create_params(resource="find_entities_raw",
                                                    entity_fields = entity_fields,
                                                    query = query)['params']

        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record',
                                                                params = params,
                                                                context = self.context).AndReturn([rir_entity])

        store_id = generate_id()

        store_entity = {
            'interval': [None, None]
        }

        entity_fields = ['_id', 'interval', 'data']
        query = {'_id': ObjectId(store_id)}

        params = self.main_params.mds.create_params(resource="find_entities_raw",
                                                    entity_fields = entity_fields,
                                                    query = query)['params']

        self.mock_helper.main_access.mds.call_find_entities_raw('store',
                                                                params = params,
                                                                context = self.context).AndReturn([store_entity])

        expected_interval = [parse_date(rir_entity['data']['as_of_date']), None]
        self.mock_helper.main_access.mds.call_update_entity('store', store_id, self.context, field_name = 'interval', field_value = expected_interval)

        self.mox.ReplayAll()

        returned_interval = StoreHelper._modify_store_interval_based_on_most_correct_rir_reassignment(self.mock_helper, store_id, rir_id, None, None, self.context)

        self.assertEqual(expected_interval, returned_interval)

    def test_modify_store_interval_based_on_most_correct_rir_reassignment__no_certainty__no_change(self):

        rir_id = generate_id()

        rir_entity = {
            'data': {
                'as_of_date_is_opened_date': False,
                'as_of_date': '1990-05-18T00:00:00'
            }
        }

        entity_fields = ['_id', 'data']
        query = {'_id': ObjectId(rir_id)}
        params = self.main_params.mds.create_params(resource="find_entities_raw",
                                                    entity_fields = entity_fields,
                                                    query = query)['params']

        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record',
                                                                params = params,
                                                                context = self.context).AndReturn([rir_entity])

        store_id = generate_id()

        store_entity = {
            'interval': ['1989-05-18T00:00:00', None]
        }

        entity_fields = ['_id', 'interval', 'data']
        query = {'_id': ObjectId(store_id)}

        params = self.main_params.mds.create_params(resource="find_entities_raw",
                                                    entity_fields = entity_fields,
                                                    query = query)['params']

        self.mock_helper.main_access.mds.call_find_entities_raw('store',
                                                                params = params,
                                                                context = self.context).AndReturn([store_entity])

        expected_interval = store_entity['interval']

        self.mox.ReplayAll()

        returned_interval = StoreHelper._modify_store_interval_based_on_most_correct_rir_reassignment(self.mock_helper, store_id, rir_id, None, None, self.context)

        self.assertEqual(expected_interval, returned_interval)

    def test_modify_store_interval_based_on_most_correct_rir_reassignment__no_certainty__change(self):

        rir_id = generate_id()

        rir_entity = {
            'data': {
                'as_of_date_is_opened_date': False,
                'as_of_date': '1990-05-18T00:00:00'
            }
        }

        entity_fields = ['_id', 'data']
        query = {'_id': ObjectId(rir_id)}
        params = self.main_params.mds.create_params(resource="find_entities_raw",
                                                    entity_fields = entity_fields,
                                                    query = query)['params']

        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record',
                                                                params = params,
                                                                context = self.context).AndReturn([rir_entity])

        store_id = generate_id()

        store_entity = {
            'interval': ['1990-05-19T00:00:00', None],
            'data': {
                'company_id': generate_id()
            }
        }

        entity_fields = ['_id', 'interval', 'data']
        query = {'_id': ObjectId(store_id)}

        params = self.main_params.mds.create_params(resource="find_entities_raw",
                                                    entity_fields = entity_fields,
                                                    query = query)['params']

        self.mock_helper.main_access.mds.call_find_entities_raw('store',
                                                                params = params,
                                                                context = self.context).AndReturn([store_entity])

        self.mock_helper._determine_opened_date(rir_entity['data'], store_entity['data']['company_id']).AndReturn(rir_entity['data']['as_of_date'])

        expected_interval = [rir_entity['data']['as_of_date'], None]
        self.mock_helper.main_access.mds.call_update_entity('store', store_id, self.context, field_name = 'interval', field_value = expected_interval)

        self.mox.ReplayAll()

        returned_interval = StoreHelper._modify_store_interval_based_on_most_correct_rir_reassignment(self.mock_helper, store_id, rir_id, None, None, self.context)

        self.assertEqual(expected_interval, returned_interval)


    def test_modify_store_interval_based_on_most_correct_rir_reassignment__no_certainty__None_start_date(self):

        rir_id = generate_id()

        rir_entity = {
            'data': {
                'as_of_date_is_opened_date': False,
                'as_of_date': '1990-05-18T00:00:00'
            }
        }

        entity_fields = ['_id', 'data']
        query = {'_id': ObjectId(rir_id)}
        params = self.main_params.mds.create_params(resource="find_entities_raw",
                                                    entity_fields = entity_fields,
                                                    query = query)['params']

        self.mock_helper.main_access.mds.call_find_entities_raw('retail_input_record',
                                                                params = params,
                                                                context = self.context).AndReturn([rir_entity])

        store_id = generate_id()

        store_entity = {
            'interval': [None, None]
        }

        entity_fields = ['_id', 'interval', 'data']
        query = {'_id': ObjectId(store_id)}

        params = self.main_params.mds.create_params(resource="find_entities_raw",
                                                    entity_fields = entity_fields,
                                                    query = query)['params']

        self.mock_helper.main_access.mds.call_find_entities_raw('store',
                                                                params = params,
                                                                context = self.context).AndReturn([store_entity])

        expected_interval = store_entity['interval']

        self.mox.ReplayAll()

        returned_interval = StoreHelper._modify_store_interval_based_on_most_correct_rir_reassignment(self.mock_helper, store_id, rir_id, None, None, self.context)

        self.assertEqual(expected_interval, returned_interval)


    def test_store_helper_async_task(self):

        # create the mock task_rec
        mock_task_rec = {
            'input': {
                "command": "yeah_baby!",
                "austin": "powers",
                "context": self.context
            },
            'meta': {
                'async': False
            }
        }

        # record
        self.mock_helper.main_access.wfs.call_task_new('generic_background_workers', 'store','store_helper_async_helper', mock_task_rec, self.context, async_retries=10)

        # replay
        self.mox.ReplayAll()

        # go!
        StoreHelper._store_helper_async_task(self.mock_helper, "yeah_baby!", "austin", "powers", self.context)


    def test_store_helper_async_task__with_kwargs(self):

        # create the mock task_rec
        mock_task_rec = {
            'input': {
                "command": "yeah_baby!",
                "austin": "powers",
                "context": self.context,
                "chicken": "woot"
            },
            'meta': {
                'async': False
            }
        }

        # record
        self.mock_helper.main_access.wfs.call_task_new('generic_background_workers', 'store','store_helper_async_helper', mock_task_rec, self.context, async_retries=10)

        # replay
        self.mox.ReplayAll()

        # go!
        StoreHelper._store_helper_async_task(self.mock_helper, "yeah_baby!", "austin", "powers", self.context, chicken = "woot")


    def test_get_store_ids_for_banner(self):

        # set up mock data
        mock_banner_id = ObjectId()
        mock_store_ids = {ObjectId(), ObjectId(), ObjectId()}

        query = {
            "links.company.store_ownership.entity_id_to": mock_banner_id
        }

        # start recording
        self.mock_helper.main_access.mds.call_distinct_field_values("store", "_id", query=query, context=self.context).AndReturn(mock_store_ids)

        # replay All
        self.mox.ReplayAll()

        # go!
        store_ids = StoreHelper.get_store_ids_for_banner(self.mock_helper, mock_banner_id, self.context)

        self.assertEqual(store_ids, mock_store_ids)


    #----------------------------------# Private Helper Methods #----------------------------------#

    def __get_rir_to_store_link_structure(self, from_id, to_id, is_most_correct = True):

        links = {
            "links": {
                "store": {
                    "retail_input": [
                        {
                            "entity_type_from": "retail_input_record",
                            "entity_id_to": to_id,
                            "interval": None,
                            "relation_type": "retail_input",
                            "entity_role_from": "retail_input_record",
                            "entity_id_from": from_id,
                            "entity_type_to": "store",
                            "_id": generate_id(),
                            "data": {
                                "properties": {
                                    "ownership": False
                                }
                            },
                            "entity_role_to":"store"
                        }
                    ]
                }
            }
        }

        if is_most_correct:
            links["links"]["store"]["retail_input"].append(
                {
                    "entity_type_from": "retail_input_record",
                    "entity_id_to": to_id,
                    "interval": None,
                    "relation_type": "retail_input",
                    "entity_role_from": "most_correct_record",
                    "entity_id_from": from_id,
                    "entity_type_to": "store",
                    "_id": generate_id(),
                    "data": {
                        "properties": {
                            "ownership": False
                        }
                    },
                    "entity_role_to":"store"
                }
            )

        return links