import pprint
from common.service_access.utilities.json_helpers import APIDecoder, APIEncoder_New, APIEncoder
from core.common.utilities.helpers import ensure_id
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_rir, \
    insert_test_industry
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from common.service_access.params_builder.mds_params_builder import ParamsBuilderMDS
from common.utilities.misc_utilities import convert_entity_list_to_dictionary
from common.utilities.inversion_of_control import Dependency
from core.common.business_logic.entity import BusinessEntity
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta


__author__ = 'erezrubinstein'


class MDSTestCollectionWithVerification(ServiceTestCollection):

    def initialize(self, data_params = None):
        self.user_id = 'test@nexusri.com'
        self.source = "mds_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

        # create params builder
        self.params_builder = ParamsBuilderMDS(self.logger)
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        self.store_helper = StoreHelper()

    def setUp(self):
        # delete when starting
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    #-----------------------------# Generic Tests #-----------------------------#

    def mds_update__interval(self):
        """
        This verifies that updating using MDS, sets the intervals as dates, not strings
        """

        # add a new company with a real interval
        opened_date = datetime(2013, 1, 1)
        closed_date = datetime(2013, 6, 6) # 6 (da devil)
        company_id = ensure_id(self.mds_access.call_add_entity("company", "staines_massive", {}, self.context, [opened_date, closed_date]))

        # find the company, but verify that the interval is a date!
        query = {
            "_id": company_id,
            "interval": { "$size": 2 },
            "$or": [
                { "interval.0": {"$type": 9} },
                { "interval.1": {"$type": 9} }
            ]
        }
        fields = ["_id", "name", "interval"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields)["params"]
        company = self.mds_access.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)[0]

        # verify the company is correct
        self.test_case.assertEqual(company, {
            "_id": company_id,
            "name": "staines_massive",
            "interval": [opened_date, closed_date]
        })

        # also test via get_entity, without meta
        fields = {"company": ["_id", "name", "interval", "data", "links"]}
        params = self.main_params.mds.create_params(resource="get_entity", entity_fields=fields)["params"]
        company = self.mds_access.call_get_entity("company", company_id, params, self.context, json_encoder=APIEncoder_New, json_decoder=APIDecoder)
        self.test_case.assertEqual(company, {
            "_id": company_id,
            "name": "staines_massive",
            "interval": [opened_date, closed_date],
            "data": {},
            "links": {},
        })

        # update the company's interval.
        # define new dates as iso format, the way you would select them.
        opened_date2 = datetime(2013, 1, 2)
        closed_date2 = datetime(2013, 6, 7)
        field_data = {
            "name": "in_da_house",
            "interval": [opened_date2, closed_date2]
        }
        self.mds_access.call_update_entity("company", company_id, self.context, field_data=field_data, use_new_json_encoder=True)

        # find the company, but verify that the interval is still a date!
        query = {
            "_id": company_id,
            "interval": { "$size": 2 },
            "$or": [
                { "interval.0": {"$type": 9} },
                { "interval.1": {"$type": 9} }
            ]
        }
        fields = ["_id", "name", "interval"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields)["params"]
        company = self.mds_access.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)[0]

        # verify the company is correct
        self.test_case.assertEqual(company, {
            "_id": company_id,
            "name": "in_da_house",
            "interval": [opened_date2, closed_date2]
        })

        # also test via get_entity, without meta
        fields = {"company": ["_id", "name", "interval", "data", "links"]}
        params = self.main_params.mds.create_params(resource="get_entity", entity_fields=fields)["params"]
        company = self.mds_access.call_get_entity("company", company_id, params, self.context, json_encoder=APIEncoder_New, json_decoder=APIDecoder)
        self.test_case.assertEqual(company, {
            "_id": company_id,
            "name": "in_da_house",
            "interval": [opened_date2, closed_date2],
            "data": {},
            "links": {},
        })

    #-----------------------------# Store Helper Tests #-----------------------------#

    def mds_test_delete_most_correct_rir_first_in_chain(self):
        """
        If deleting any chain of most correct RIRs of size two or greater, like:
        A -> B -> C -> ...
        Removing A should result in:
        B -> C -> ...
        """
        # insert test data
        _company_id = insert_test_company()

        rir_id_A = ensure_id(insert_test_rir(self.context, _company_id, '1'))
        rir_id_B = ensure_id(insert_test_rir(self.context, _company_id, '2'))

        store_id = self.store_helper.create_new_store(self.context, rir_id_A, async=False)
        self.store_helper.add_rir_to_store(self.context, store_id, rir_id_B, True, async=False)

        self.store_helper.delete_rir_from_store(self.context, rir_id_A, store_id, is_most_correct=True, async=False)

        # test that rir A was actually deleted
        rir_deleted = False
        try:
            self.mds_access.call_get_entity('retail_input_record', rir_id_A)
        except Exception as ex:
            rir_deleted = 'NotFoundError' in ex.message
        self.test_case.assertTrue(rir_deleted)

        # test that the store is still there
        store = self.mds_access.call_get_entity('store', store_id)
        self.test_case.assertEqual(store['_id'], store_id)


    def mds_test_delete_most_correct_rir_middle_position(self):
        """
        If there are at least three most correct RIRs represented in a chain:
        A -> B -> C
        Removing the middle position B should result in:
        A -> C
        where B is removed the the replaced/replacement link created between A and C.
        """
        # insert test data
        _company_id = insert_test_company()

        rir_id_A = ensure_id(insert_test_rir(self.context, _company_id, '1'))
        rir_id_B = ensure_id(insert_test_rir(self.context, _company_id, '2'))
        rir_id_C = ensure_id(insert_test_rir(self.context, _company_id, '3'))

        store_id = self.store_helper.create_new_store(self.context, rir_id_A, async=False)
        self.store_helper.add_rir_to_store(self.context, store_id, rir_id_B, True, async=False)
        self.store_helper.add_rir_to_store(self.context, store_id, rir_id_C, True, async=False)

        self.mds_access.call_add_link("retail_input_record", str(rir_id_B), "potential_match", "retail_input_record",
                                      str(rir_id_C), "target", "retail_input", self.context)

        self.store_helper.delete_rir_from_store(self.context, rir_id_B, store_id, is_most_correct=True, async=False)

        # test that rir B was actually deleted
        rir_deleted = False
        try:
            self.main_access.mds.call_get_entity('retail_input_record', rir_id_B)
        except Exception as ex:
            rir_deleted = 'NotFoundError' in ex.message
        self.test_case.assertTrue(rir_deleted)

        # test that there is a replaced -> replacement link between A and C
        relation_types = [["retail_input", "replaced", "replacement"]]
        fields = ['to._id']
        params = self.main_params.create_get_data_entities_linked_from_params(relation_types=relation_types,
                                                                              fields=fields)['params']
        linked_mc_rir = self.main_access.call_get_data_entities_linked_from('retail_input_record',
                                                                            'retail_input_record',
                                                                            rir_id_A, params=params,
                                                                            context=self.context)['rows'][0]
        self.test_case.assertEqual(ensure_id(linked_mc_rir['to._id']), rir_id_C)

        # test that the store is still there
        store = self.main_access.mds.call_get_entity('store', store_id)
        self.test_case.assertEqual(store['_id'], store_id)


    def mds_test_delete_most_correct_rir_last_in_chain(self):
        """
        If deleting any chain of most correct RIRs of size two or greater, like:
        A -> B -> C
        Removing C should result in:
        A -> B
        * where B is the NEW most correct RIR *
        """
        # insert test data
        _company_id = insert_test_company()

        rir_id_A = ensure_id(insert_test_rir(self.context, _company_id, '1'))
        rir_id_B = ensure_id(insert_test_rir(self.context, _company_id, '2'))
        rir_id_C = ensure_id(insert_test_rir(self.context, _company_id, '3'))

        store_id = self.store_helper.create_new_store(self.context, rir_id_A, async=False)
        self.store_helper.add_rir_to_store(self.context, store_id, rir_id_B, True, async=False)
        self.store_helper.add_rir_to_store(self.context, store_id, rir_id_C, True, async=False)

        # sometimes the links come back with another link listed second - make sure it is filtered in the function
        self.mds_access.call_add_link("retail_input_record", str(rir_id_B), "potential_match", "retail_input_record",
                                      str(rir_id_C), "target", "retail_input", self.context)

        self.store_helper.delete_rir_from_store(self.context, rir_id_C, store_id, is_most_correct=True, async=False)

        # test that rir C was actually deleted
        rir_deleted = False
        try:
            self.main_access.mds.call_get_entity('retail_input_record', rir_id_C)
        except Exception as ex:
            rir_deleted = 'NotFoundError' in ex.message
        self.test_case.assertTrue(rir_deleted)

        # test that rir B is the new most correct
        new_most_correct_rir_id = self.store_helper.find_most_correct_rir(self.context, store_id)['entity_id_to']
        self.test_case.assertEqual(new_most_correct_rir_id, rir_id_B)

        # test that the store is still there
        store = self.main_access.mds.call_get_entity('store', store_id)
        self.test_case.assertEqual(store['_id'], store_id)


    def mds_test_delete_most_correct_rir_only_one(self):
        """
        If deleting a most correct RIR that is also the only RIR for a store, deleting this RIR should
        also delete the store with it.
        """
        # insert test data
        _company_id = insert_test_company()

        rir_id_A = ensure_id(insert_test_rir(self.context, _company_id, '1'))
        store_id = self.store_helper.create_new_store(self.context, rir_id_A, async=False)

        self.store_helper.delete_rir_from_store(self.context, rir_id_A, store_id, is_most_correct=True, async=False)

        # test that rir A was actually deleted
        rir_deleted = False
        try:
            self.main_access.mds.call_get_entity('retail_input_record', rir_id_A)
        except Exception as ex:
            rir_deleted = 'NotFoundError' in ex.message
        self.test_case.assertTrue(rir_deleted)

        # test that the store was actually deleted
        deleted_store = False
        try:
            self.main_access.mds.call_get_entity('store', store_id)
        except Exception as ex:
            deleted_store = 'NotFoundError' in ex.message
        self.test_case.assertTrue(deleted_store)

    def mds_test_delete_store_by_id_old_encoders(self):
        """
        Test that deleting a store deletes both the address and store, using the old JSON encoders
        """
        company_id = str(insert_test_company())
        rir_id = str(insert_test_rir(self.context, company_id))
        store_id = str(self.store_helper.create_new_store(self.context, rir_id, async=False))
        # find address id
        address_id = str(self.store_helper.get_store_address_id(self.context, store_id))

        # get the store and address from MDS
        store = self.main_access.mds.call_get_entity('store', store_id, json_encoder=APIEncoder, json_decoder=None)
        address = self.main_access.mds.call_get_entity('address', address_id, json_encoder=APIEncoder, json_decoder=None)

        self.test_case.assertEqual(store_id, store['_id'])
        self.test_case.assertEqual(address_id, address['_id'])

        # delete the store
        self.store_helper.delete_store_by_id(self.context, store_id, async=False)

        store_deleted = False
        try:
            self.main_access.mds.call_get_entity('store', store_id, json_encoder=APIEncoder, json_decoder=None)
        except Exception as ex:
            store_deleted = 'NotFoundError' in ex.message
        self.test_case.assertTrue(store_deleted)

        address_deleted = False
        try:
            self.main_access.mds.call_get_entity('address', address_id, json_encoder=APIEncoder, json_decoder=None)
        except Exception as ex:
            address_deleted = 'NotFoundError' in ex.message
        self.test_case.assertTrue(address_deleted)
        
    def mds_test_delete_store_by_id(self):
        """
        Test that deleting a store deletes both the address and store
        """
        company_id = ensure_id(insert_test_company())
        rir_id = ensure_id(insert_test_rir(self.context, company_id))
        store_id = ensure_id(self.store_helper.create_new_store(self.context, rir_id, async=False))
        # find address id
        address_id = ensure_id(self.store_helper.get_store_address_id(self.context, store_id))

        # get the store and address from MDS
        store = self.main_access.mds.call_get_entity('store', store_id, json_encoder=APIEncoder_New, json_decoder=APIDecoder)
        address = self.main_access.mds.call_get_entity('address', address_id, json_encoder=APIEncoder_New, json_decoder=APIDecoder)

        self.test_case.assertEqual(store_id, store['_id'])
        self.test_case.assertEqual(address_id, address['_id'])

        # delete the store
        self.store_helper.delete_store_by_id(self.context, store_id, async=False)

        store_deleted = False
        try:
            self.main_access.mds.call_get_entity('store', store_id, json_encoder=APIEncoder_New, json_decoder=APIDecoder)
        except Exception as ex:
            store_deleted = 'NotFoundError' in ex.message
        self.test_case.assertTrue(store_deleted)

        address_deleted = False
        try:
            self.main_access.mds.call_get_entity('address', address_id, json_encoder=APIEncoder_New, json_decoder=APIDecoder)
        except Exception as ex:
            address_deleted = 'NotFoundError' in ex.message
        self.test_case.assertTrue(address_deleted)


    def mds_test_batch_insert_entities(self):
        # create id to test insertion with id
        entity_id = ObjectId()

        # create two stores, one with an id and one without
        entities = [
            {
                "_id": entity_id,
                "name": "UNITTESTSTORE1",
                "data": {
                    "UNITTESTBATCH_INSERT": True
                }
            },
            {
                "name": "UNITTESTSTORE2",
                "data": {
                    "UNITTESTBATCH_INSERT": True
                }
            }
        ]

        # bomboj for
        ids_returned = self.mds_access.call_batch_insert_entities("store", entities, self.context)

        # select all the entities that have UNITTESTBATCH_INSERT = TRUE
        params = {
            "entity_filters": [
                {
                    "store": { "data.UNITTESTBATCH_INSERT": True }
                }
            ]
        }
        entities_returned = self.mds_access.call_find_entities("store", params = params, context = self.context)

        # make sure numbers add up
        self.test_case.assertEqual(len(entities_returned), 2)
        self.test_case.assertEqual(len(ids_returned), 2)

        # make sure first entity matches
        self.test_case.assertIn(str(entity_id), [str(e["_id"]) for e in entities_returned])

        for entity in entities_returned:
            self.test_case.assertIn(entity["name"], ["UNITTESTSTORE1", "UNITTESTSTORE2"])
            self.test_case.assertIn(entity["_id"], ids_returned)

            # make sure that extra parameters were added to each entity (i.e. type, meta, links)
            self.test_case.assertEqual(entity["entity_type"], "store")
            self.test_case.assertEqual(entity["links"], {})
            self.test_case.assertIn("meta", entity)


    def mds_test_batch_insert_entity_with_links(self):
        # create id a head of time
        entity_id = ObjectId()
        to_entity_id_1 = ObjectId()
        to_entity_id_2 = ObjectId()

        # create a base entity
        entities = [
            {
                "_id": entity_id,
                "name": "UNITTEST_ENTITY",
                "data": {
                    "UNITTEST_BATCH_INSERT_WITH_LINKS": True
                }
            }
        ]

        # add several links (to non existent objects).  This makes sure we can batch insert with two way links
        BusinessEntity.add_link_to_entity(entities[0], "store", entity_id, "UNITTEST_ROLE_FROM", "store", to_entity_id_1, "UNITTEST_ROLE_TO", "UNITTEST_RELATIONSHIP")
        BusinessEntity.add_link_to_entity(entities[0], "store", entity_id, "UNITTEST_ROLE_FROM", "store", to_entity_id_2, "UNITTEST_ROLE_TO", "UNITTEST_RELATIONSHIP")

        # bomboj for
        ids_returned = self.mds_access.call_batch_insert_entities("store", entities, self.context)

        # select the object
        entity_fields = ["_id", "entity_type", "name", "data", "links", "meta"]
        link_fields = ["_id", "entity_type_from", "entity_type_to", "entity_id_from", "entity_id_to", "entity_role_from", "entity_role_to", "relation_type", "interval", "data"]
        postproc_params = {
            "entity_fields": { "_all": entity_fields },
            "link_fields": { "_all": link_fields }
        }
        params =  {
            "link_filters": [["store", "store", "UNITTEST_RELATIONSHIP", { "fetch": True, "recursive": False }]],
            "postprocess": postproc_params
        }
        entity = self.mds_access.call_get_entity("store", str(entity_id), params)

        # basic verification
        self.test_case.assertEqual(len(ids_returned), 1)
        self.test_case.assertEqual(ids_returned[0], entity["_id"])
        self.test_case.assertEqual(entity["name"], "UNITTEST_ENTITY")
        self.test_case.assertTrue(entity["data"]["UNITTEST_BATCH_INSERT_WITH_LINKS"])

        # assert entity has correct link structure
        self.test_case.assertEqual(len(entity["links"]), 1)
        self.test_case.assertEqual(len(entity["links"]["store"]), 1)
        self.test_case.assertEqual(len(entity["links"]["store"]["UNITTEST_RELATIONSHIP"]), 2)
        self.test_case.assertEqual(len(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]), 10)

        # assert links
        self.test_case.assertGreater(len(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["_id"]), 10)
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["entity_type_from"], "store")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["entity_type_to"], "store")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["entity_id_from"], str(entity_id))
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["entity_id_to"], str(to_entity_id_1))
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["entity_role_from"], "UNITTEST_ROLE_FROM")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["entity_role_to"], "UNITTEST_ROLE_TO")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["relation_type"], "UNITTEST_RELATIONSHIP")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["interval"], None)
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][0]["data"], { "properties": { "ownership": False }})
        # second link
        self.test_case.assertGreater(len(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["_id"]), 10)
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["entity_type_from"], "store")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["entity_type_to"], "store")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["entity_id_from"], str(entity_id))
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["entity_id_to"], str(to_entity_id_2))
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["entity_role_from"], "UNITTEST_ROLE_FROM")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["entity_role_to"], "UNITTEST_ROLE_TO")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["relation_type"], "UNITTEST_RELATIONSHIP")
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["interval"], None)
        self.test_case.assertEqual(entity["links"]["store"]["UNITTEST_RELATIONSHIP"][1]["data"], { "properties": { "ownership": False }})


    def mds_test_batch_update_entities(self):
        # create three stores, only 2 will be updated
        entities = [
            {
                "name": "UNITTESTSTORE1",
                "data": {
                    "UNITTESTBATCH_Update1": True,
                    "UNITTESTBATCH_Update2": True,
                    }
            },
            {
                "name": "UNITTESTSTORE2",
                "data": {
                    "UNITTESTBATCH_Update1": True,
                    "UNITTESTBATCH_Update2": True,
                    }
            },
            {
                "name": "UNITTESTSTORE3",
                "data": {
                    "UNITTESTBATCH_Update1": True,
                    "UNITTESTBATCH_Update2": True,
                    }
            }
        ]

        # insert items
        ids_returned = self.mds_access.call_batch_insert_entities("store", entities, self.context)

        # create id query for first two entities
        query = { "_id": { "$in": ids_returned[:2] }}

        # create update operations
        update_operations = {
            "$set": {
                "data.UNITTESTBATCH_Update1": "woot",
                "data.UNITTESTBATCH_Update2": "chicken"
            }
        }

        # update items
        update_message = self.mds_access.call_batch_update_entities("store", query, update_operations, self.context)

        # basic asserts
        self.test_case.assertEqual(update_message, "Great Success")

        # select items to see what changed
        postproc_params = {
            "entity_fields": { "_all": ["_id", "entity_type", "name", "data", "links", "meta"] }
        }
        params = {
            "entity_filters": {
                "store": {
                    "_id": { "$in": [str(id) for id in ids_returned] }
                }
            },
            "postprocess": postproc_params,
            "options": {
                "include_meta_history": True
            }
        }
        entities = self.mds_access.call_find_entities("store", params)

        # assert that first two items were updated
        self.test_case.assertEqual(len(entities), 3)
        self.test_case.assertEqual(entities[0]["name"], "UNITTESTSTORE1")
        self.test_case.assertEqual(entities[0]["data"]["UNITTESTBATCH_Update1"], "woot")
        self.test_case.assertEqual(entities[0]["data"]["UNITTESTBATCH_Update2"], "chicken")
        self.test_case.assertEqual(entities[1]["name"], "UNITTESTSTORE2")
        self.test_case.assertEqual(entities[1]["data"]["UNITTESTBATCH_Update1"], "woot")
        self.test_case.assertEqual(entities[1]["data"]["UNITTESTBATCH_Update2"], "chicken")

        # assert that the last item didn't change
        self.test_case.assertEqual(entities[2]["name"], "UNITTESTSTORE3")
        self.test_case.assertEqual(entities[2]["data"]["UNITTESTBATCH_Update1"], True)
        self.test_case.assertEqual(entities[2]["data"]["UNITTESTBATCH_Update2"], True)


        self.test_case.assertEqual(entities[0]["meta"]["history"]["updates"], [])
        self.test_case.assertEqual(entities[1]["meta"]["history"]["updates"], [])

        params = {
            'query': {
                'entity_id': ObjectId(entities[0]['_id']),
            },
            'entity_fields': ['timestamp', 'field', 'old_value', 'new_value', 'entity_id', 'action', 'context'],
            'sort': [['field', 1]]
        }

        entity_1_meta_docs = self.main_access.mds.call_find_entities_raw('_meta', params)

        params['query']['entity_id'] = ObjectId(entities[1]['_id'])

        entity_2_meta_docs = self.main_access.mds.call_find_entities_raw('_meta', params)

        # make sure that the correct updates were registered in the meta field
        self.test_case.assertEqual(len(entity_1_meta_docs), 2)
        self.test_case.assertEqual(entity_1_meta_docs[0]["timestamp"], entities[0]["meta"]["updated_at"])
        self.test_case.assertEqual(entity_1_meta_docs[0]["field"], "data.UNITTESTBATCH_Update1")
        self.test_case.assertEqual(entity_1_meta_docs[0]["old_value"], "batch_update")
        self.test_case.assertEqual(entity_1_meta_docs[0]["new_value"], "woot")
        self.test_case.assertEqual(entity_1_meta_docs[0]["action"], "set")
        self.test_case.assertEqual(entity_1_meta_docs[0]["context"], self.context)

        self.test_case.assertEqual(entity_1_meta_docs[1]["timestamp"], entities[0]["meta"]["updated_at"])
        self.test_case.assertEqual(entity_1_meta_docs[1]["field"], "data.UNITTESTBATCH_Update2")
        self.test_case.assertEqual(entity_1_meta_docs[1]["old_value"], "batch_update")
        self.test_case.assertEqual(entity_1_meta_docs[1]["new_value"], "chicken")
        self.test_case.assertEqual(entity_1_meta_docs[1]["action"], "set")
        self.test_case.assertEqual(entity_1_meta_docs[1]["context"], self.context)
        # second item
        self.test_case.assertEqual(len(entity_2_meta_docs), 2)
        self.test_case.assertEqual(entity_2_meta_docs[0]["timestamp"], entities[0]["meta"]["updated_at"])
        self.test_case.assertEqual(entity_2_meta_docs[0]["field"], "data.UNITTESTBATCH_Update1")
        self.test_case.assertEqual(entity_2_meta_docs[0]["old_value"], "batch_update")
        self.test_case.assertEqual(entity_2_meta_docs[0]["new_value"], "woot")
        self.test_case.assertEqual(entity_2_meta_docs[0]["action"], "set")
        self.test_case.assertEqual(entity_2_meta_docs[0]["context"], self.context)
        self.test_case.assertEqual(entity_2_meta_docs[1]["timestamp"], entities[0]["meta"]["updated_at"])
        self.test_case.assertEqual(entity_2_meta_docs[1]["field"], "data.UNITTESTBATCH_Update2")
        self.test_case.assertEqual(entity_2_meta_docs[1]["old_value"], "batch_update")
        self.test_case.assertEqual(entity_2_meta_docs[1]["new_value"], "chicken")
        self.test_case.assertEqual(entity_2_meta_docs[1]["action"], "set")
        self.test_case.assertEqual(entity_2_meta_docs[1]["context"], self.context)

        # make sure third item has no update history
        self.test_case.assertEqual(len(entities[2]["meta"]["history"]["updates"]), 0)

        # update item one more time to make sure that a third update is added to meta without overriding
        update_message = self.mds_access.call_batch_update_entities("store", query, update_operations, self.context)


        params = {
            'query': {
                'entity_id': ObjectId(entities[0]['_id']),
            },
            'entity_fields': ['timestamp', 'field', 'old_value', 'new_value', 'entity_id'],
            'sort': [['field', 1]]
        }

        entity_1_meta_docs = self.main_access.mds.call_find_entities_raw('_meta', params)

        params['query']['entity_id'] = ObjectId(entities[1]['_id'])
        entity_2_meta_docs = self.main_access.mds.call_find_entities_raw('_meta', params)

        params['query']['entity_id'] = ObjectId(entities[2]['_id'])
        entity_3_meta_docs = self.main_access.mds.call_find_entities_raw('_meta', params)

        # verify counts of updates
        self.test_case.assertEqual(len(entity_1_meta_docs), 4)
        self.test_case.assertEqual(len(entity_2_meta_docs), 4)
        self.test_case.assertEqual(len(entity_3_meta_docs), 0)


    def mds_test_mds_test_upsert__insert(self):

        # create a fake parent company id
        company_id = ObjectId()
        query = { "data.company_id": str(company_id) }

        # find raw on it and verify that it has no child stores
        entity_fields = ["_id", "meta", "name", "data", "interval", "entity_type"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=entity_fields)["params"]
        stores = self.mds_access.call_find_entities_raw("store", params, self.context, encode_and_decode_results=False)
        self.test_case.assertEqual(len(stores), 0)

        # create two $set operations to insert via upsert, which uses new encoder, so keeps datetimes
        start_date = datetime(2012, 1, 1)
        end_date = datetime(2013, 1, 1)
        upsert_operations = {
            "$set": {
                "name": "austin_danger_powers",
                "data": {
                    "UNITTESTBATCH_Update1": True,
                    "UNITTESTBATCH_Update2": True,
                    "company_id": str(company_id) # we "normally" stringify this field, so test this way
                },
                "interval": [start_date, end_date]
            }
        }

        # upsert away
        results = self.mds_access.call_upsert_entities("store", query, upsert_operations, self.context)

        # make sure upsert worked
        self.test_case.assertEqual(results["status"], "Great Success - Inserted")
        self.test_case.assertGreater(len(results["_id"]), 10)

        # query again and verify that a store has been inserted
        query = {
            "data.company_id": str(company_id),
            # verify that the interval is not null and that both are date times even though they were passed as strings
            "interval": { "$size": 2 },
            "interval.0": {"$type": 9},
            "interval.1": {"$type": 9}
        }
        entity_fields = ["_id", "meta", "name", "data", "interval", "entity_type"]
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query, entity_fields = entity_fields)["params"]
        stores = self.mds_access.call_find_entities_raw("store", params, self.context, encode_and_decode_results=False)

        # find raw on it and verify that it has no child stores
        self.test_case.assertEqual(len(stores), 1)

        # verify that the store has the correct dates
        self.test_case.assertEqual(stores[0]["interval"], [start_date, end_date])

        # verify name and data
        self.test_case.assertEqual(stores[0]["name"], "austin_danger_powers")
        self.test_case.assertEqual(stores[0]["data"], {
            "UNITTESTBATCH_Update1": True,
            "UNITTESTBATCH_Update2": True,
            "company_id": str(company_id)
        })

        # verify that the store has correct meta fields
        self.test_case.assertIn("meta", stores[0])
        self.test_case.assertEqual(stores[0]["meta"]["created_by"], self.context)
        self.test_case.assertIn("created_at", stores[0]["meta"])
        self.test_case.assertIn("updated_at", stores[0]["meta"])
        self.test_case.assertEqual(stores[0]["meta"]["created_at"], stores[0]["meta"]["updated_at"])
        self.test_case.assertEqual(stores[0]["meta"]["history"], { "updates": [] })

        # verify entity type inserted
        self.test_case.assertEqual(stores[0]["entity_type"], "store")


    def test_mds_test_upsert__insert__data_dot(self):
        """
        Special case.  Test inserting with many data.field entries and make sure it works.
        """

        # create query and operation
        object_id = ObjectId()
        query = { "_id": object_id }
        upsert_operations = {
            "$set": {
                "data.erez": "yes!",
                "data.rob": "no!"
            }
        }

        # upsert away
        results = self.mds_access.call_upsert_entities("store", query, upsert_operations, self.context)

        # make sure upsert worked
        self.test_case.assertEqual(results["status"], "Great Success - Inserted")
        self.test_case.assertGreater(len(results["_id"]), 10)

        # query again and verify that a store has been inserted
        query = { "_id": results["_id"] }
        entity_fields = ["_id", "name", "data", "interval", "entity_type", "meta"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=entity_fields)["params"]
        stores = self.mds_access.call_find_entities_raw("store", params, self.context, encode_and_decode_results=False)

        # verify default interval, name, entity_type, meta, data
        self.test_case.assertEqual(stores[0]["interval"], None)
        self.test_case.assertEqual(stores[0]["entity_type"], "store")

        # verify that the data is correct
        self.test_case.assertEqual(stores[0]["data"], {
            "erez": "yes!",
            "rob": "no!"
        })

        # verify that the store has correct meta fields
        self.test_case.assertIn("meta", stores[0])
        self.test_case.assertEqual(stores[0]["meta"]["created_by"], self.context)
        self.test_case.assertIn("created_at", stores[0]["meta"])
        self.test_case.assertIn("updated_at", stores[0]["meta"])
        self.test_case.assertEqual(stores[0]["meta"]["created_at"], stores[0]["meta"]["updated_at"])
        self.test_case.assertEqual(stores[0]["meta"]["history"], { "updates": [] })


    def mds_test_mds_test_upsert__insert__no_name(self):
        """
        Special case.  test with no name and no interval make sure defaults are inserted.
        Also make sure that if we don't want to create meta, there is no meta.
        """

        # create query and operation
        object_id = ObjectId()
        query = { "_id": object_id }
        upsert_operations = { "$set": { "data.stuff": "kewl" }}

        # upsert away
        results = self.mds_access.call_upsert_entities("store", query, upsert_operations, self.context, insert_creation_meta=False)

        # make sure upsert worked
        self.test_case.assertEqual(results["status"], "Great Success - Inserted")
        self.test_case.assertGreater(len(results["_id"]), 10)

        # query again and verify that a store has been inserted
        query = { "_id": results["_id"] }
        entity_fields = ["_id", "name", "data", "interval", "entity_type", "meta"]
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query, entity_fields = entity_fields)["params"]
        stores = self.mds_access.call_find_entities_raw("store", params, self.context)

        # verify default interval, name (should not exist), and entity_type,
        self.test_case.assertEqual(stores[0]["interval"], None)
        self.test_case.assertNotIn("name", stores[0])
        self.test_case.assertEqual(stores[0]["entity_type"], "store")

        # verify that the store has an empty meta since we set insert_creation_meta to False
        self.test_case.assertNotIn("meta", stores[0])

        # verify the data is there
        self.test_case.assertEqual(stores[0]["data"], {"stuff": "kewl"})

    def mds_test_mds_test_upsert__update(self):

        # create a fake parent company id
        company_id = ObjectId()
        query = { "data.company_id": str(company_id) }

        # create two children stores
        entities = [
            {
                "name": "UNITTESTSTORE1",
                "data": {
                    "UNITTESTBATCH_Update1": True,
                    "UNITTESTBATCH_Update2": True,
                    "company_id": company_id
                }
            },
            {
                "name": "UNITTESTSTORE2",
                "data": {
                    "UNITTESTBATCH_Update1": True,
                    "UNITTESTBATCH_Update2": True,
                    "company_id": company_id
                }
            }
        ]
        self.mds_access.call_batch_insert_entities("store", entities, self.context)

        # find raw on it and verify that it has 2 child stores
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query)["params"]
        child_stores = self.mds_access.call_find_entities_raw("store", params, self.context)
        self.test_case.assertEqual(len(child_stores), 2)

        # update one of the stores (i.e. multi = False)
        upsert_operations = { "$set": { "data.update_count": 1 }}
        results = self.mds_access.call_upsert_entities("store", query, upsert_operations, self.context, multi = False)

        # make sure upsert worked
        self.test_case.assertEqual(results, { "status": "Great Success - Updated" })

        # query how many have an update_count of 1 and verify it's only one store
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = { "data.update_count": 1 })["params"]
        child_stores = self.mds_access.call_find_entities_raw("store", params, self.context)
        self.test_case.assertEqual(len(child_stores), 1)

        # update the both the stores using multi = True
        upsert_operations = { "$set": { "data.update_count": 2 }}
        self.mds_access.call_upsert_entities("store", query, upsert_operations, self.context, multi = True)

        # query how many have an update_count of 2 and verify it's both stores
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = { "data.update_count": 2 })["params"]
        child_stores = self.mds_access.call_find_entities_raw("store", params, self.context)
        self.test_case.assertEqual(len(child_stores), 2)

        # query how many stores have that parent id and verify that it's only two
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query)["params"]
        child_stores = self.mds_access.call_find_entities_raw("store", params, self.context)
        self.test_case.assertEqual(len(child_stores), 2)


    def mds_test_find_raw__date_filter__one_date(self):
        # create several fake companies with different date ranges
        companies = [
            self.__create_test_company_with_interval("test1", [datetime(2010, 1, 1), datetime(2010, 2, 1)], 1), # outside the range
            self.__create_test_company_with_interval("test2", [datetime(2010, 1, 1), datetime(2013, 2, 1)], 1), # encompasses entire range
            self.__create_test_company_with_interval("test3", [datetime(2013, 1, 1), datetime(2013, 2, 1)], 1), # outside the range
            self.__create_test_company_with_interval("test4", [None, datetime(2013, 2, 1)], 2),                 # inside the range
            self.__create_test_company_with_interval("test5", [datetime(2010, 1, 1), None], 3),                 # inside the range
            self.__create_test_company_with_interval("test6", [None, datetime(2011, 2, 1)], 2),                 # outside the range
            self.__create_test_company_with_interval("test7", [datetime(2013, 1, 1), None], 3),                 # outside the range
            self.__create_test_company_with_interval("test8", None, 1)                                          # inside the range
        ]
        self.mds_access.call_batch_insert_entities("company", companies, self.context)

        # query the fields using find_raw with one date parameter
        interval_filter = { "dates": [datetime(2012, 1, 1)] }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", interval_filter = interval_filter)["params"]
        entities_from_db = self.mds_access.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)
        entities_from_db = convert_entity_list_to_dictionary(entities_from_db)

        # make sure that only those within the range are in the db
        self.test_case.assertEqual(len(entities_from_db), 4)
        self.test_case.assertIn(companies[1]["_id"], entities_from_db)
        self.test_case.assertIn(companies[3]["_id"], entities_from_db)
        self.test_case.assertIn(companies[4]["_id"], entities_from_db)
        self.test_case.assertIn(companies[7]["_id"], entities_from_db)

        # query, but with two fields this time
        interval_filter = {
            "dates": [datetime(2012, 1, 1), datetime(2013, 1, 1)]
        }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", interval_filter = interval_filter)["params"]
        entities_from_db = self.mds_access.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)
        entities_from_db = convert_entity_list_to_dictionary(entities_from_db)

        # verify that the other expected companies are now returned
        self.test_case.assertEqual(len(entities_from_db), 6)
        self.test_case.assertIn(companies[1]["_id"], entities_from_db)
        self.test_case.assertIn(companies[2]["_id"], entities_from_db)
        self.test_case.assertIn(companies[3]["_id"], entities_from_db)
        self.test_case.assertIn(companies[4]["_id"], entities_from_db)
        self.test_case.assertIn(companies[6]["_id"], entities_from_db)
        self.test_case.assertIn(companies[7]["_id"], entities_from_db)


        # this tests a specific piece of logic inside the logic that makes sure we don't override the top level "$or"
        # I will add an "$or" to the query to make sure it ands it and the date query's $or
        query = {
            "$or": [
                { "data.test": 2 },
                { "data.test": 3 }
            ]
        }
        interval_filter = { "dates": [datetime(2012, 1, 1)] }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", interval_filter = interval_filter, query = query)["params"]
        entities_from_db = self.mds_access.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)
        entities_from_db = convert_entity_list_to_dictionary(entities_from_db)

        # make sure we only get 2 items (ones that are [2,3] and within the date range
        self.test_case.assertEqual(len(entities_from_db), 2)
        self.test_case.assertIn(companies[3]["_id"], entities_from_db)
        self.test_case.assertIn(companies[4]["_id"], entities_from_db)


    def mds_test_find_raw__date_filter__date_range(self):
        # create several fake companies with different date ranges one for every scenario
        companies = [
            self.__create_test_company_with_interval("test1", [datetime(2010, 1, 1), datetime(2010, 2, 1)], 1), # outside the range.  starts/ends left
            self.__create_test_company_with_interval("test2", [datetime(2013, 2, 1), datetime(2013, 3, 1)], 1), # outside the range.  starts/ends right
            self.__create_test_company_with_interval("test3", [datetime(2011, 1, 1), datetime(2012, 2, 1)], 1), # inside the range.  starts left, ends middle
            self.__create_test_company_with_interval("test4", [datetime(2012, 2, 1), datetime(2013, 2, 1)], 1), # inside the range.  starts middle, ends right
            self.__create_test_company_with_interval("test5", [datetime(2012, 2, 1), datetime(2012, 3, 1)], 1), # inside the range.  completely inside
            self.__create_test_company_with_interval("test6", [datetime(2011, 1, 1), datetime(2014, 1, 1)], 1), # inside the range.  encompasses completely
            self.__create_test_company_with_interval("test7", [None, datetime(2010, 1, 1)], 1),                 # outside the range.  starts left.
            self.__create_test_company_with_interval("test8", [datetime(2014, 1, 1), None], 1),                 # outside the range.  starts right.
            self.__create_test_company_with_interval("test9", [None, datetime(2012, 2, 1)], 2),                 # inside the range.  starts left, ends middle.
            self.__create_test_company_with_interval("test10", [datetime(2012, 2, 1), None], 3),                # inside the range.  starts middle, ends right.
            self.__create_test_company_with_interval("test11", [None, datetime(2014, 2, 1)], 2),                # inside the range.  starts never, ends after
            self.__create_test_company_with_interval("test12", [datetime(2012, 2, 1), None], 3),                # inside the range.  starts middle, ends never.
            self.__create_test_company_with_interval("test13", None, 2)                                         # inside the range.  never starts, never ends
        ]
        self.mds_access.call_batch_insert_entities("company", companies, self.context)


        # query the fields using find_raw with a date range
        interval_filter = { "date_range": [datetime(2012, 1, 1), datetime(2013, 1, 1)] }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", interval_filter = interval_filter)["params"]
        entities_from_db = self.mds_access.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)
        entities_from_db = convert_entity_list_to_dictionary(entities_from_db)

        # verify that only the ones inside were selected
        self.test_case.assertEqual(len(entities_from_db), 9)
        self.test_case.assertIn(companies[2]["_id"], entities_from_db)
        self.test_case.assertIn(companies[3]["_id"], entities_from_db)
        self.test_case.assertIn(companies[4]["_id"], entities_from_db)
        self.test_case.assertIn(companies[5]["_id"], entities_from_db)
        self.test_case.assertIn(companies[8]["_id"], entities_from_db)
        self.test_case.assertIn(companies[9]["_id"], entities_from_db)
        self.test_case.assertIn(companies[10]["_id"], entities_from_db)
        self.test_case.assertIn(companies[11]["_id"], entities_from_db)
        self.test_case.assertIn(companies[12]["_id"], entities_from_db)


        # this tests a specific piece of logic inside the logic that makes sure we don't override the top level "$nor"
        # I will add a "$nor" to the query to make sure it ands it and the date query's $nor
        query = {
            "$nor": [
                { "data.test": 2 },
                { "data.test": 3 }
            ]
        }
        interval_filter = { "date_range": [datetime(2012, 1, 1), datetime(2013, 1, 1)] }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", interval_filter = interval_filter, query = query)["params"]
        entities_from_db = self.mds_access.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)
        entities_from_db = convert_entity_list_to_dictionary(entities_from_db)

        # make sure we only get 4 items (everything but [2,3] and within the date range
        self.test_case.assertEqual(len(entities_from_db), 4)
        self.test_case.assertIn(companies[2]["_id"], entities_from_db)
        self.test_case.assertIn(companies[3]["_id"], entities_from_db)
        self.test_case.assertIn(companies[4]["_id"], entities_from_db)
        self.test_case.assertIn(companies[5]["_id"], entities_from_db)


    def mds_test_find_raw__query_as_list__unwinding_bug(self):
        """
        This tests a very specific bug that has been fixed.  The bug happened when a link has been deleted.
        It would try to unwind the link, but there was nothing there, so the row wouldn't be returned at all.
        """

        # create two industries
        industry_id1 = ensure_id(insert_test_industry())
        industry_id2 = ensure_id(insert_test_industry())

        # create two companies.  One has a valid industry link while the other has an empty industry link.
        company_id1 = ObjectId()
        company_id2 = ObjectId()
        entities = [
            {
                "_id": company_id1,
                "name": "Company1",
                "data": { }
            },
            {
                "_id": company_id2,
                "name": "Company2",
                "data": { }
            }
        ]

        # insert the companies
        self.mds_access.call_batch_insert_entities("company", entities, self.context)

        # add industry_1 to both and industry_2 to the second
        self.mds_access.call_add_link("company", company_id1, "primary_industry_classification", "industry", industry_id1, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", company_id2, "primary_industry_classification", "industry", industry_id1, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", company_id2, "primary_industry_classification", "industry", industry_id2, "primary_industry", "industry_classification", self.context )

        # remove the link from the first company
        self.mds_access.call_del_link_without_id("company", company_id1, "primary_industry_classification", "industry", industry_id1, "primary_industry", "industry_classification")

        # select these companies as a list (i.e. unwind the links)
        query = { "_id": { "$in": [company_id1, company_id2]}}
        entity_fields = ["_id", "name", "links.industry.industry_classification.entity_id_to"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=entity_fields, as_list=True)["params"]
        entities_returned = self.mds_access.call_find_entities_raw("company", params=params, context=self.context, encode_and_decode_results=False)

        # make sure the entities are correct and everything is unwound correctly.
        self.test_case.assertEqual(entities_returned, [
            [company_id1, "Company1", None],
            [company_id2, "Company2", industry_id1],
            [company_id2, "Company2", industry_id2]
        ])


    def mds_test_industry_competes_with_itself(self):

        # test same-industry competition
        # banners within an industry always compete with themselves, so this should be very common data
        # the idea is to have only 1 link subdoc when this happens, instead of the normal 2 (from and to copies)

        # create a test industry
        industry_id = insert_test_industry()

        self.mds_access.call_add_link("industry", industry_id, "competitor", "industry", industry_id, "competitor",
                                      "industry_competition", self.context, link_interval=None,
                                      link_data={"some_fake": "data"})

        # get the industry links data
        fields = {"industry":"links"}
        params = self.main_params.mds.create_params(resource="get_entity", entity_fields=fields)["params"]
        industry = self.mds_access.call_get_entity("industry", industry_id, params, self.context)

        # get the competition list and make sure it only has 1 item
        # this is because we expect that MDS is smart enough
        # so that it doesn't add reflexive link data to same-entity links
        competition_list = industry["links"]["industry"]["industry_competition"]
        self.test_case.assertEqual(len(competition_list), 1)


    def mds_test_batch_delete_entities(self):

        # insert test entities

        company_id = insert_test_company()
        rir_1 = ensure_id(insert_test_rir(self.context, company_id))
        rir_2 = ensure_id(insert_test_rir(self.context, company_id))

        # call batch delete
        query = {"data.company_id": company_id}
        self.mds_access.call_batch_delete_entities("retail_input_record", query, self.context)

        # make sure there are no rirs for this company now!
        rirs = self.mds_access.call_find_entities_raw("retail_input_record", params={"query":{}}, context=self.context)
        self.test_case.assertEqual(rirs, [])

        # make sure the entities were archived
        query = {"data.company_id": company_id}
        fields = ["data.company_id","original_id"]
        archived_rirs = self.mds_access.call_find_entities_raw("archive", params={"query": query, "entity_fields": fields},
                                                               context=self.context, encode_and_decode_results=False)

        # check that the entities have the proper data
        self.test_case.assertEqual({arch["data"]["company_id"] for arch in archived_rirs}, {company_id})
        self.test_case.assertEqual(sorted({arch["original_id"] for arch in archived_rirs}), sorted({rir_1, rir_2}))

    def mds_test_mds_add_audit(self):

        entity_id = ObjectId()  # audit does not verify entity exists... by design

        # get two audit dates, stripping out microseconds since mongo isn't that precise
        audit_date = datetime.utcnow() - timedelta(days=1)
        audit_date = audit_date - timedelta(microseconds=audit_date.microsecond)

        audit_date_2 = datetime.utcnow()
        audit_date_2 = audit_date_2 - timedelta(microseconds=audit_date_2.microsecond)

        # add the audits using slightly different interfaces
        self.mds_access.call_add_audit("company", entity_id, "data.name", "blah", "blurgh",
                                       audit_date=audit_date, context=self.context)

        self.mds_access.call_add_audit("company", entity_id, "data.name", "blurgh", "blatz",
                                       audit_date=audit_date_2, user_id="fred", source="wicked perl script")

        # make sure the audit were created, and retrieved in reverse chrono order (most recent first)
        audits = self.mds_access.call_get_audits("company", entity_id)

        expected = {
            'audit_date': audit_date_2,
            'audit_entity_id': entity_id,
            'audit_entity_type': 'company',
            'field': 'data.name',
            'old_value': 'blurgh',
            'new_value': 'blatz',
            'source': 'wicked perl script',
            'user_id': 'fred'
        }
        self.test_case.assertDictContainsSubset(expected, audits[0]["data"])
        self.test_case.assertIn("_id", audits[0])
        self.test_case.assertIsInstance(audits[0]["_id"], ObjectId)

        expected = {
            'audit_date': audit_date,
            'audit_entity_id': entity_id,
            'audit_entity_type': 'company',
            'field': 'data.name',
            'old_value': 'blah',
            'new_value': 'blurgh',
            'source': 'mds_test_collection.py',
            'user_id': 'test@nexusri.com'
        }
        self.test_case.assertDictContainsSubset(expected, audits[1]["data"])
        self.test_case.assertIn("_id", audits[1])
        self.test_case.assertIsInstance(audits[1]["_id"], ObjectId)


    # ------------------------------------ Private Methods ------------------------------------ #

    def __create_test_company_with_interval(self, name, interval, data_dot_test = None):
        company = {
            "_id": ObjectId(),
            "name": name,
            "interval": interval
        }

        if data_dot_test:
            company["data"] = {
                "test": data_dot_test
            }

        return company