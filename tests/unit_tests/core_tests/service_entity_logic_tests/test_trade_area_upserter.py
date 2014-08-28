from copy import deepcopy
import json
from core.common.business_logic.service_entity_logic.trade_area_upserter import TradeAreaUpserter
from bson.objectid import ObjectId
import datetime
import mox


__author__ = 'kingneptune'


class TradeAreaUpserterTests(mox.MoxTestBase):

    def setUp(self):

        super(TradeAreaUpserterTests, self).setUp()

        self._trade_area_upserter = self.mox.CreateMock(TradeAreaUpserter)
        self._trade_area_upserter._main_access = self.mox.CreateMockAnything()
        self._trade_area_upserter._main_access.mds = self.mox.CreateMockAnything()
        self._trade_area_upserter._main_params = self.mox.CreateMockAnything()
        self._trade_area_upserter._main_params.mds = self.mox.CreateMockAnything()
        self._trade_area_upserter._start_time = datetime.datetime.utcnow()
        self._trade_area_upserter._context = {
            'source': 'TradeAreaUpserter UNIT TESTS',
            'user_id': 42
        }

        self._trade_area_upserter._trade_area_threshold = 'BoatTime10hours'

    def doCleanups(self):
        super(TradeAreaUpserterTests, self).doCleanups()

    def test_initialize(self):

        self.mox.StubOutWithMock(self._trade_area_upserter, '_get_store')
        self._trade_area_upserter._get_store()
        self.mox.StubOutWithMock(self._trade_area_upserter, '_get_address')
        self._trade_area_upserter._get_address()

        self.mox.ReplayAll()

        TradeAreaUpserter.initialize(self._trade_area_upserter)

    def test_upsert(self):

        def set_trade_area_doc(*args, **kwargs):
            self._trade_area_upserter._trade_area_id = 123
            self._trade_area_upserter._requires_gp7 = False

        self._trade_area_upserter._construct_trade_area_data().AndReturn({'mock': 'doc'})
        self._trade_area_upserter._upsert({'mock': 'doc'}).WithSideEffects(set_trade_area_doc)
        self._trade_area_upserter._sync_address_to_store()
        self.mox.ReplayAll()

        results = TradeAreaUpserter.upsert(self._trade_area_upserter, 'bob')
        self.assertEqual(results, {
            "trade_area_id": 123,
            "requires_gp7": False
        })

    def test_get_store(self):

        self._trade_area_upserter._store_id = str(ObjectId())
        expected_query = {'_id': ObjectId(self._trade_area_upserter._store_id)}
        expected_entity_fields = ['_id', 'data', 'interval', 'links.address.address_assignment.entity_id_to']

        self._trade_area_upserter._main_params.mds.create_params(resource = 'find_entities_raw',
                                                                 query = expected_query,
                                                                 entity_fields = expected_entity_fields).AndReturn({'params': 'params'})
        self._trade_area_upserter._main_access.mds.call_find_entities_raw('store', 'params', encode_and_decode_results=False).AndReturn([{'mock': 'store'}])

        self.mox.ReplayAll()

        TradeAreaUpserter._get_store(self._trade_area_upserter)

        self.assertEqual({'mock': 'store'}, self._trade_area_upserter._store)

    def test_upsert_new_trade_area(self):

        # create mocks
        trade_area_doc = {
            'store_id': 42,
            'trade_area_threshold': 'BoatTimeHours5'
        }

        self._trade_area_upserter._store = {
            '_id': 1,
            'interval': ['then', 'now']
        }

        query = {
            'data.store_id': trade_area_doc['store_id'],
            'data.trade_area_threshold': trade_area_doc['trade_area_threshold']
        }

        operations = {
            '$set': {
                'data.store_id': trade_area_doc['store_id'],
                'data.trade_area_threshold': trade_area_doc['trade_area_threshold'],
                'interval': ['then', 'now']
            }
        }
        inserted_id = "yeah!"
        mock_upsert_result = {'status': 'Great Success - Inserted', '_id': inserted_id}
        self._trade_area_upserter._start_time = 'now'

        # begin recording
        self._trade_area_upserter._construct_update_fields(trade_area_doc).AndReturn(deepcopy(query))
        self._trade_area_upserter._check_if_gp7_required(query)
        self._trade_area_upserter._main_access.mds.call_upsert_entities('trade_area', query, operations, self._trade_area_upserter._context, multi = False).AndReturn(mock_upsert_result)
        self._trade_area_upserter._main_access.mds.call_add_link('store', self._trade_area_upserter._store['_id'], 'home_store', 'trade_area',
                                                                 str(inserted_id), 'trade_area', 'store_trade_area', self._trade_area_upserter._context,
                                                                 link_interval = [self._trade_area_upserter._start_time, None])

        # replay all, sucka!
        self.mox.ReplayAll()

        # gp
        TradeAreaUpserter._upsert(self._trade_area_upserter, trade_area_doc)

        self.assertEqual(self._trade_area_upserter._trade_area_id, inserted_id)

    def test_upsert_existing_trade_area(self):

        # create mocks
        trade_area_doc = {
            'store_id': 42,
            'trade_area_threshold': 'BoatTimeHours5'
        }

        self._trade_area_upserter._store = {
            '_id': 1,
            'interval': ['then', 'now']
        }

        query = {
            'data.store_id': trade_area_doc['store_id'],
            'data.trade_area_threshold': trade_area_doc['trade_area_threshold']
        }

        operations = {
            '$set': {
                'data.store_id': trade_area_doc['store_id'],
                'data.trade_area_threshold': trade_area_doc['trade_area_threshold'],
                'interval': ['then', 'now']
            }
        }

        # begin recording
        self._trade_area_upserter._construct_update_fields(trade_area_doc).AndReturn(deepcopy(query))
        self._trade_area_upserter._check_if_gp7_required(query)
        self._trade_area_upserter._main_access.mds.call_upsert_entities('trade_area', query, operations, self._trade_area_upserter._context, multi = False).AndReturn({'status': 'updated'})

        self.mox.ReplayAll()

        TradeAreaUpserter._upsert(self._trade_area_upserter, trade_area_doc)

    def test_get_address(self):

        address_id = ObjectId()
        self._trade_area_upserter._store = {
            'links': {
                'address': {
                    'address_assignment': [{'entity_id_to': address_id}]
                }
            }
        }

        query = {'_id': ObjectId(self._trade_area_upserter._store['links']['address']['address_assignment'][0]['entity_id_to'])}

        self._trade_area_upserter._main_params.mds.create_params(resource = 'find_entities_raw', query = query, entity_fields = ['_id', 'data']).AndReturn({'params': 'mock params'})
        self._trade_area_upserter._main_access.mds.call_find_entities_raw('address', 'mock params', context=self._trade_area_upserter._context, encode_and_decode_results=False).AndReturn(['mock address'])

        self.mox.ReplayAll()

        TradeAreaUpserter._get_address(self._trade_area_upserter)

        self.assertEqual(self._trade_area_upserter._address, 'mock address')

    def test_construct_update_fields(self):

        trade_area_doc = {
            'woo': 'oooo',
            'chic': 'ken'
        }

        expected_update_fields = {
            'data.woo': 'oooo',
            'data.chic': 'ken'
        }

        update_fields = TradeAreaUpserter._construct_update_fields(self._trade_area_upserter, trade_area_doc)
        self.assertEqual(update_fields, expected_update_fields)

    def test_construct_store_data(self):

        # mock the store
        mock_store_id = ObjectId()
        mock_company_id = ObjectId()
        mock_store = {
            'interval': [datetime.datetime(1990, 05, 18), None],
            '_id': mock_store_id,
            'data': {
                'company_name': 'Rob',
                'company_id': str(mock_company_id),
                'phone': '555 555 5555'
            }
        }
        self._trade_area_upserter._store = mock_store

        returned_store_data = TradeAreaUpserter._construct_store_data(self._trade_area_upserter)

        expected_store_data = {
            'store_id': str(mock_store['_id']),
            'company_name': mock_store['data']['company_name'],
            'store_opened_date': datetime.datetime(1990, 05, 18),
            'store_closed_date': None,
            'company_id': mock_store['data']['company_id'],
            'phone': mock_store['data']['phone'],
        }

        self.maxDiff = None
        self.assertEqual(expected_store_data, returned_store_data)

    def test_construct_store_data__None_interval(self):

        # mock the store
        mock_store_id = ObjectId()
        mock_company_id = ObjectId()
        mock_store = {
            'interval': None,
            '_id': mock_store_id,
            'data': {
                'company_name': 'Rob',
                'company_id': str(mock_company_id),
                'phone': '555 555 5555'
            }
        }
        self._trade_area_upserter._store = mock_store

        returned_store_data = TradeAreaUpserter._construct_store_data(self._trade_area_upserter)

        expected_store_data = {
            'store_id': str(mock_store['_id']),
            'company_name': mock_store['data']['company_name'],
            'store_opened_date': None,
            'store_closed_date': None,
            'company_id': mock_store['data']['company_id'],
            'phone': mock_store['data']['phone'],
        }

        self.maxDiff = None
        self.assertEqual(expected_store_data, returned_store_data)

    def test_construct_address_data(self):

         # mock the address
        mock_address_id = ObjectId()
        mock_address = {
            '_id': mock_address_id,
            'data': {
                'street_number': '317',
                'street': 'Madison Ave',
                'city': 'Manhattan',
                'state': 'NY',
                'zip': '10017',
                'suite': '811',
                'shopping_center': 'Grand Central',
                'longitude': 1.0,
                'latitude': -1.0
            }
        }

        self._trade_area_upserter._address = mock_address

        returned_address_data = TradeAreaUpserter._construct_address_data(self._trade_area_upserter)

        expected_address_data = {
            'address_id': str(mock_address['_id']),
            'street_number': mock_address['data']['street_number'],
            'street': mock_address['data']['street'],
            'city': mock_address['data']['city'],
            'state': mock_address['data']['state'],
            'zip': mock_address['data']['zip'],
            'suite': mock_address['data']['suite'],
            'shopping_center': mock_address['data']['shopping_center'],
            'longitude': mock_address['data']['longitude'],
            'latitude': mock_address['data']['latitude'],
            'geo': [mock_address['data']['longitude'], mock_address['data']['latitude']]
        }

        self.maxDiff = None
        self.assertEqual(expected_address_data, returned_address_data)


    def test_construct_trade_area_data(self):

        mock_store_data = {
            'store_id': "123",
            'company_name': "Tacos Inc.",
            'store_opened_date': datetime.datetime(1990, 05, 18),
            'store_closed_date': None,
            'company_id': "456",
            'phone': "555-1212",
        }

        mock_address_data = {
            'address_id': "789",
            'street_number': "123",
            'street': "Fake St",
            'city': "Anytown",
            'state': "NY",
            'zip': 11017,
            'suite': 811,
            'shopping_center': None,
            'longitude': 1.11111,
            'latitude': 2.22222,
            'geo': [1.11111, 2.22222]
        }

        self._trade_area_upserter._construct_store_data().AndReturn(mock_store_data)
        self._trade_area_upserter._construct_address_data().AndReturn(mock_address_data)

        self.mox.ReplayAll()

        expected_trade_area_data = dict(
            [("trade_area_threshold", self._trade_area_upserter._trade_area_threshold)]
            + mock_store_data.items()
            + mock_address_data.items()
        )

        returned_trade_area_data = TradeAreaUpserter._construct_trade_area_data(self._trade_area_upserter)
        self.maxDiff = None
        self.assertEqual(expected_trade_area_data, returned_trade_area_data)

    def test_sync_address_to_store(self):

        self._trade_area_upserter._store_id = str(ObjectId())
        mock_address_data = {
            'address_id': "789",
            'street_number': "123",
            'street': "Fake St",
            'city': "Anytown",
            'state': "NY",
            'zip': 11017,
            'suite': 811,
            'shopping_center': None,
            'longitude': 1.11111,
            'latitude': 2.22222,
            'geo': [1.11111, 2.22222]
        }

        mock_field_data = {
            "data.{}".format(key): value
            for key, value in mock_address_data.iteritems()
        }

        self._trade_area_upserter._construct_address_data().AndReturn(mock_address_data)
        self._trade_area_upserter._main_access.mds.call_update_entity("store", self._trade_area_upserter._store_id,
                                                                      self._trade_area_upserter._context,
                                                                      field_data=mock_field_data)

        self.mox.ReplayAll()

        TradeAreaUpserter._sync_address_to_store(self._trade_area_upserter)
