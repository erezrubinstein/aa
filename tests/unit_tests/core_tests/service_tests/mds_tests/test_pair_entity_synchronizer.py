from core.service.svc_master_data_storage.implementation.pair_entity_synchronizer import PairEntitySynchronizer
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from bson.objectid import ObjectId
import datetime
import mox


__author__ = 'vgold'


class PairEntitySynchronizerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(PairEntitySynchronizerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on instance for calls to record
        self.mock = self.mox.CreateMock(PairEntitySynchronizer)
        self.mock.mds_db = self.mox.CreateMockAnything()
        self.mock.mds_ref_data = self.mox.CreateMockAnything()
        self.mock.pair_entity_helper = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        self.mock.context = {
            "user_id": "tester",
            "source": "test_pair_entity_creator.py"
        }

    def doCleanups(self):

        super(PairEntitySynchronizerTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # PairEntitySynchronizer._get_entity()

    def test_get_entity(self):
        
        self.mock.entity_id = 1
        self.mock.entity_type = "entity_type"
        
        entity = "entity"
        self.mock.mds_db.find_one(self.mock.entity_type, {"_id": self.mock.entity_id}, {"meta": 0}).AndReturn(entity)

        self.mox.ReplayAll()

        PairEntitySynchronizer._get_entity(self.mock)

        self.assertEqual(self.mock.entity, entity)

    ##########################################################################
    # PairEntitySynchronizer._get_all_pair_entity_types()

    def test_get_all_pair_entity_types(self):

        self.mock.mds_ref_data.relation_type_map = {
            "rel1": [
                {
                    "pair_entity_type": "pet1"
                },
                {}
            ],
            "rel2": [
                {},
                {
                    "pair_entity_type": "pet2"
                }
            ]
        }

        self.mox.ReplayAll()

        result = PairEntitySynchronizer._get_all_pair_entity_types(self.mock)

        self.assertEqual(self.mock, result)

        self.assertItemsEqual(self.mock.all_pair_entity_types, ["pet1", "pet2"])

    ##########################################################################
    # PairEntitySynchronizer._get_pair_entity_fields()

    def test_get_pair_entity_fields(self):

        self.mock.entity_type = "company"

        self.mock.all_pair_entity_types = ["pair1", "pair2"]

        self.mock.mds_ref_data.entity_type_map = {
            "pair1": {
                "entity_type_from": self.mock.entity_type,
                "entity_type_to": self.mock.entity_type,
                "linked_entities": []
            },
            "pair2": {
                "entity_type_from": "asdf",
                "entity_type_to": "asdf",
                "linked_entities": [
                    {
                        "entity_type": self.mock.entity_type,
                        "relation_type": "rel1",
                        "entity_role_from": "role1",
                        "entity_role_to": "role2",
                        "fields": ["_id", "name"]
                    }
                ]
            }
        }

        self.mox.ReplayAll()

        result = PairEntitySynchronizer._get_pair_entity_fields(self.mock)

        self.assertEqual(self.mock, result)

        expected_field_map = {
            "pair1": [
                {
                    "type": "from",
                    "field": "data.pair.entity_id_from"
                },
                {
                    "type": "to",
                    "field": "data.pair.entity_id_to"
                }
            ],
            "pair2": [
                {
                    "type": "link",
                    "field": "links.adsf.rel1",
                    "link_fields": ["_id", "name"]
                }
            ]
        }

        self.assertItemsEqual(self.mock.pair_entity_field_map, expected_field_map)

    ##########################################################################
    # PairEntitySynchronizer._sync_pair_entity()

    def test_sync_pair_entity(self):

        link_field_map = {
            "type": "link",
            "relation_type": "rel1",
            "link_fields": ["_id", "name"]
        }

        self.mock.pair_entity_field_map = {
            "pair1": [
                {
                    "type": "from",
                },
                {
                    "type": "to",
                }
            ],
            "pair2": [link_field_map]
        }

        self.mock._update_pair_entities_by_base_field("pair1", "from")
        self.mock._update_pair_entities_by_base_field("pair1", "to")
        self.mock._update_pair_entities_by_link_fields("pair2", link_field_map)

        self.mox.ReplayAll()

        result = PairEntitySynchronizer._sync_pair_entity(self.mock)

        self.assertEqual(self.mock, result)

    ##########################################################################
    # PairEntitySynchronizer._get_pair_entities_by_base_field()

    def test_get_pair_entities_by_base_field(self):

        pair_entity_type = "pair_entity_type"
        field_type = "field_type"
        field = "field"

        self.mock.mds_ref_data.entity_type_map = "entity_type_map"

        entity_fields = "entity_fields"
        self.mock.pair_entity_helper.get_pair_entity_data_fields(pair_entity_type, self.mock.mds_ref_data.entity_type_map).AndReturn(entity_fields)

        self.mock.entity = "entity"
        entity_data = "entity_data"
        self.mock.pair_entity_helper.get_entity_data_for_fields(self.mock.entity, entity_fields).AndReturn(entity_data)

        self.mock.entity_type = "entity_type"
        self.mock.entity_id = "entity_id"

        entity_dict = {
            self.mock.entity_type: {
                self.mock.entity_id: self.mock.entity
            }
        }

        linked_entities = "linked_entities"
        self.mock.pair_entity_helper.get_linked_entities(self.mock.mds_ref_data, pair_entity_type, entity_dict, self.mock.mds_db).AndReturn(linked_entities)

        links = "links"
        self.mock.pair_entity_helper.get_linked_entity_data(linked_entities, self.mock.entity).AndReturn(links)

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn("now")

        # semantic variables
        pair_entity_id_key = "data.pair.entity_id_%s" % field_type
        data_key = "data.%s" % field_type
        links_key = "data.%s_links" % field_type

        query = {
             "$and": [
                {pair_entity_id_key: self.mock.entity_id},
                {
                    "$or": [
                        {data_key: {"$ne": entity_data}},
                        {links_key: {"$ne": links}}
                    ]
                }
            ]
        }

        update = {
            "$set": {
                data_key: entity_data,
                links_key: links,
                "data.sync.last_synced": "now"
            }
        }

        self.mock.mds_db.update(pair_entity_type, query, update, multi=True)

        self.mox.ReplayAll()

        PairEntitySynchronizer._update_pair_entities_by_base_field(self.mock, pair_entity_type, field_type)

    ##########################################################################
    # PairEntitySynchronizer._get_pair_entities_by_link_fields()

    def test_get_pair_entities_by_link_fields(self):

        pair_entity_type = "pair_entity_type"
        link_fields = "link_fields"

        link_field_map = {
            "relation_type": "relation_type",
            "entity_role_from": "entity_role_from",
            "entity_role_to": "entity_role_to",
            "link_fields": link_fields
        }

        self.mock.entity = "entity"

        entity_data = "entity_data"
        self.mock.pair_entity_helper.get_entity_data_for_fields(self.mock.entity, link_fields).AndReturn(entity_data)

        self.mox.StubOutWithMock(datetime, 'datetime')

        self.mock.entity_id = "entity_id"
        self.mock.entity_type = "entity_type"

        for direction in ["from", "to"]:

            datetime.datetime.utcnow().AndReturn("now")

            base_query_field = "data.%s_links.%s.%s" % (direction, self.mock.entity_type, link_field_map["relation_type"])

            # semantic variables
            entity_id_to_key = "%s.entity_id_to" % base_query_field
            entity_role_from_key = "%s.entity_role_from" % base_query_field
            entity_role_to_key = "%s.entity_role_to" % base_query_field
            update_field = "data.%s_links.%s.%s.$.entity" % (direction, self.mock.entity_type,
                                                             link_field_map["relation_type"])

            query = {
                entity_id_to_key: self.mock.entity_id,
                entity_role_from_key: link_field_map["entity_role_from"],
                entity_role_to_key: link_field_map["entity_role_to"],
                update_field: {"$ne": entity_data}
            }

            update = {
                "$set": {
                    update_field: entity_data,
                    "data.sync.last_synced": "now"
                }
            }

            self.mock.mds_db.update(pair_entity_type, query, update, multi=True)

        self.mox.ReplayAll()

        PairEntitySynchronizer._update_pair_entities_by_link_fields(self.mock, pair_entity_type, link_field_map)



