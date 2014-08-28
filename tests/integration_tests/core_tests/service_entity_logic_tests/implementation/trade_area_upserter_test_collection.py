import datetime
from common.service_access.utilities.json_helpers import APIEncoder_New
from common.utilities.inversion_of_control import Dependency
from core.common.business_logic.service_entity_logic.trade_area_upserter import TradeAreaUpserter
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection

__author__ = 'kingneptune'


class TradeAreaUpserterTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 42
        self.source = "trade_area_upserter_test_collection"
        self.context = {"user_id": self.user_id, "source": self.source}

        # get dependencies
        self.main_access = Dependency("CoreAPIProvider").value
        self.main_params = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        # delete when starting
        self.main_access.mds.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def test_upsert_trade_area__new(self):

        # add store
        store_data = {
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
        }
        store_id = self.main_access.mds.call_add_entity('store', 'name', store_data, self.context, [datetime.datetime(1990, 05, 18), None])

        # add address
        address_data = {
            'street_number': '42',
            'street': 'Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
        }
        address_id = self.main_access.mds.call_add_entity('address', 'name', address_data, self.context)

        # add a link between the two
        self.main_access.mds.call_add_link('store', store_id, 'subject', 'address', address_id, 'location', 'address_assignment', self.context)

        # upsert
        tau = TradeAreaUpserter(store_id)
        tau.initialize()
        tau.upsert('Here! I am a random threshold...')

        # get the trade area
        params = {'query': {'data.store_id': str(store_id)}, 'entity_fields': ['_id', 'interval', 'data']}
        entity_recs = self.main_access.mds.call_find_entities_raw('trade_area', params, encode_and_decode_results=False)

        self.test_case.assertEqual(len(entity_recs), 1)

        expected_ta_data = {
            'store_id': str(store_id),
            'address_id': str(address_id),
            'store_opened_date': datetime.datetime(1990, 05, 18),
            'store_closed_date': None,
            'trade_area_threshold': 'Here! I am a random threshold...',
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
            'street_number': '42',
            'street': 'Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
            'geo': [-1.0, -1.0]
        }

        expected_interval = [datetime.datetime(1990, 05, 18), None]
        self.test_case.maxDiff = None
        self.test_case.assertEqual(expected_ta_data, entity_recs[0]['data'])
        self.test_case.assertEqual(expected_interval, entity_recs[0]['interval'])

    def test_upsert_trade_area__same_threshold(self):

        # add store
        store_data = {
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
        }
        store_id = self.main_access.mds.call_add_entity('store', 'name', store_data, self.context, [datetime.datetime(1990, 05, 18), None])

        # add address
        address_data = {
            'street_number': '42',
            'street': 'Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
        }
        address_id = self.main_access.mds.call_add_entity('address', 'name', address_data, self.context)

        # add a link between the two
        self.main_access.mds.call_add_link('store', store_id, 'subject', 'address', address_id, 'location', 'address_assignment', self.context)

        # add a trade area
        ta_data = {
            'store_id': str(store_id),
            'address_id': str(address_id),
            'store_opened_date': datetime.datetime(1990, 05, 18),
            'store_closed_date': None,
            'trade_area_threshold': 'Here! I am a random threshold...',
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
            'street_number': '42',
            'street': 'Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
            'geo': [-1.0, -1.0]
        }

        trade_area_id = self.main_access.mds.call_add_entity('trade_area', '_', ta_data, self.context, [datetime.datetime(1990, 05, 18), None])

        # link to the store
        self.main_access.mds.call_add_link('store',
                                            store_id,
                                            'home_store',
                                            'trade_area',
                                            trade_area_id,
                                            'trade_area',
                                            'store_trade_area',
                                            self.context,
                                            link_interval = [datetime.datetime.utcnow(), None])

        # update the address
        self.main_access.mds.call_update_entity('address',
                                                str(address_id),
                                                self.context,
                                                field_name = 'data.street',
                                                field_value = 'Not Main St')

        # upsert
        tau = TradeAreaUpserter(store_id)
        tau.initialize()
        tau.upsert('Here! I am a random threshold...')

        # get the trade area
        params = {'query': {'data.store_id': str(store_id)}, 'entity_fields': ['_id', 'interval', 'data']}
        entity_recs = self.main_access.mds.call_find_entities_raw('trade_area', params, encode_and_decode_results=False)

        self.test_case.assertEqual(len(entity_recs), 1)

        expected_ta_data = {
            'store_id': str(store_id),
            'address_id': str(address_id),
            'store_opened_date': datetime.datetime(1990, 05, 18),
            'store_closed_date': None,
            'trade_area_threshold': 'Here! I am a random threshold...',
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
            'street_number': '42',
            'street': 'Not Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
            'geo': [-1.0, -1.0]
        }

        expected_interval = [datetime.datetime(1990, 05, 18), None]
        self.test_case.maxDiff = None
        self.test_case.assertEqual(expected_ta_data, entity_recs[0]['data'])
        self.test_case.assertEqual(expected_interval, entity_recs[0]['interval'])

    def test_upsert_trade_area__different_threshold(self):

        # add store
        store_data = {
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
        }
        store_id = self.main_access.mds.call_add_entity('store', 'name', store_data, self.context, [datetime.datetime(1990, 05, 18), None])

        # add address
        address_data = {
            'street_number': '42',
            'street': 'Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
        }
        address_id = self.main_access.mds.call_add_entity('address', 'name', address_data, self.context)

        # add a link between the two
        self.main_access.mds.call_add_link('store', store_id, 'subject', 'address', address_id, 'location', 'address_assignment', self.context)

        # add a trade area

        ta_data = {
            'store_id': str(store_id),
            'address_id': str(address_id),
            'store_opened_date': datetime.datetime(1990, 05, 18),
            'store_closed_date': None,
            'trade_area_threshold': 'Here! I am a random threshold...',
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
            'street_number': '42',
            'street': 'Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
            'geo': [-1.0, -1.0]
        }

        # use the new encoder to preserve the datetime data
        trade_area_id = self.main_access.mds.call_add_entity('trade_area', '_', ta_data, self.context, [datetime.datetime(1990, 05, 18), None], json_encoder=APIEncoder_New)

        # link to the store
        self.main_access.mds.call_add_link('store',
                                            store_id,
                                            'home_store',
                                            'trade_area',
                                            trade_area_id,
                                            'trade_area',
                                            'store_trade_area',
                                            self.context,
                                            link_interval = [datetime.datetime.utcnow(), None])

        # update the address
        self.main_access.mds.call_update_entity('address',
                                                str(address_id),
                                                self.context,
                                                field_name = 'data.street',
                                                field_value = 'Not Main St')

        # upsert
        tau = TradeAreaUpserter(store_id)
        tau.initialize()
        tau.upsert('Here! I am a random, but different threshold...')

        # get the trade area
        params = {'query': {'data.store_id': str(store_id)}, 'entity_fields': ['_id', 'interval', 'data']}
        entity_recs = self.main_access.mds.call_find_entities_raw('trade_area', params, encode_and_decode_results=False)

        self.test_case.assertEqual(len(entity_recs), 2)

        expected_ta_0_data = {
            'store_id': str(store_id),
            'address_id': str(address_id),
            'store_opened_date': datetime.datetime(1990, 05, 18),
            'store_closed_date': None,
            'trade_area_threshold': 'Here! I am a random threshold...',
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
            'street_number': '42',
            'street': 'Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
            'geo': [-1.0, -1.0]
        }

        expected_interval = [datetime.datetime(1990, 05, 18), None]
        self.test_case.maxDiff = None
        self.test_case.assertEqual(expected_ta_0_data, entity_recs[0]['data'])
        self.test_case.assertEqual(expected_interval, entity_recs[0]['interval'])


        expected_ta_1_data = {
            'store_id': str(store_id),
            'address_id': str(address_id),
            'store_opened_date': datetime.datetime(1990, 05, 18),
            'store_closed_date': None,
            'trade_area_threshold': 'Here! I am a random, but different threshold...',
            'company_name': 'Rob',
            'company_id': 42,
            'phone': '5555555555',
            'street_number': '42',
            'street': 'Not Main St',
            'city': 'NY',
            'state': 'NY',
            'zip': '10017',
            'suite': '811',
            'shopping_center': 'Grand Central',
            'longitude': -1.0,
            'latitude': -1.0,
            'geo': [-1.0, -1.0]
        }


        self.test_case.assertEqual(expected_ta_1_data, entity_recs[1]['data'])
        self.test_case.assertEqual(expected_interval, entity_recs[1]['interval'])