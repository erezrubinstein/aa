from bson.objectid import ObjectId
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.business_logic.entity import BusinessEntity
from core.common.utilities.errors import BadRequestError
from core.service.svc_master_data_storage.implementation.pair_entity_creator import PairEntityCreator
import datetime
import mox


__author__ = 'vgold'


class PairEntityCreatorTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(PairEntityCreatorTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on instance for calls to record
        self.mock = self.mox.CreateMock(PairEntityCreator)
        self.mock.db = self.mox.CreateMockAnything()
        self.mock.svc = self.mox.CreateMockAnything()
        self.mock.BusinessEntity = self.mox.CreateMockAnything()
        self.mock.ref_data = self.mox.CreateMockAnything()
        self.mock.pair_entity_helper = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        self.mock.context = {
            "user_id": "tester",
            "source": "test_pair_entity_creator.py"
        }

    def doCleanups(self):

        super(PairEntityCreatorTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # PairEntityCreator._validate_entity_types()

    def test_validate_entity_types(self):

        pec = PairEntityCreator.__new__(PairEntityCreator)
        pec.ref_data = self.mox.CreateMockAnything()

        pec.pair_entity_type = "pair_entity_type"
        pec.entity_type_from = "entity_type_from"
        pec.entity_type_to = "entity_type_to"

        pec.ref_data.entity_type_map = {
            pec.pair_entity_type: {
                "entity_type_from": "entity_type_from",
                "entity_type_to": "entity_type_to",
                "data_fields": [
                    "type"
                ]
            }
        }

        pec._validate_entity_types()

        pec.entity_type_to = "adsf"
        with self.assertRaises(BadRequestError):
            pec._validate_entity_types()

    ##########################################################################
    # PairEntityCreator._get_entity_ids()

    def test_get_entity_ids(self):

        pec = PairEntityCreator.__new__(PairEntityCreator)

        id1 = ObjectId()
        id2 = ObjectId()
        id3 = ObjectId()
        id4 = ObjectId()
        id5 = ObjectId()
        id6 = ObjectId()

        pec.entity_pairs = [
            {"to_id": id1, "from_id": id4},
            {"to_id": id2, "from_id": id5},
            {"to_id": id3, "from_id": id6}
        ]
        pec.entity_type_to = "entity_type"

        pec._get_entity_ids()

        self.assertItemsEqual(pec.entity_from_ids, [id4, id5, id6])
        self.assertItemsEqual(pec.entity_to_ids, [id1, id2, id3])

    ##########################################################################
    # PairEntityCreator._get_entities()

    def test_get_entities__different_entity_type(self):

        id1 = ObjectId()
        id2 = ObjectId()
        id3 = ObjectId()
        id4 = ObjectId()
        id5 = ObjectId()
        id6 = ObjectId()

        self.mock.entity_type_from = "entity_type_from"
        self.mock.entity_type_to = "entity_type_to"

        self.mock.entity_from_ids = [id1, id2, id3]
        self.mock.entity_to_ids = [id4, id5, id6]

        query = {"_id": {"$in": self.mock.entity_from_ids}}
        self.mock.db.find(self.mock.entity_type_from, query, {"meta": 0}).AndReturn([{"_id": id1, "stuff": {}},
                                                                                     {"_id": id2, "stuff": {}},
                                                                                     {"_id": id3, "stuff": {}}])

        query = {"_id": {"$in": self.mock.entity_to_ids}}
        self.mock.db.find(self.mock.entity_type_to, query, {"meta": 0}).AndReturn([{"_id": id4, "stuff": {}},
                                                                                   {"_id": id5, "stuff": {}},
                                                                                   {"_id": id6, "stuff": {}}])

        self.mox.ReplayAll()

        PairEntityCreator._get_entities(self.mock)

        expected_entities = {
            "entity_type_from": {
                str(id1): {"_id": id1, "stuff": {}},
                str(id2): {"_id": id2, "stuff": {}},
                str(id3): {"_id": id3, "stuff": {}}
            },
            "entity_type_to": {
                str(id4): {"_id": id4, "stuff": {}},
                str(id5): {"_id": id5, "stuff": {}},
                str(id6): {"_id": id6, "stuff": {}}
            }
        }

        self.assertEqual(self.mock.entities, expected_entities)


    def test_get_entities__different_entity_type(self):
        id1 = ObjectId()
        id2 = ObjectId()
        id3 = ObjectId()
        id4 = ObjectId()
        id5 = ObjectId()
        id6 = ObjectId()

        self.mock.entity_type_from = "entity_type"
        self.mock.entity_type_to = "entity_type"

        self.mock.entity_from_ids = [id1, id2, id3]
        self.mock.entity_to_ids = [id4, id5, id6]

        query = {"_id": {"$in": self.mock.entity_from_ids + self.mock.entity_to_ids}}
        self.mock.db.find(self.mock.entity_type_from, query, {"meta": 0}).AndReturn([{"_id": id1, "stuff": {}},
                                                                                     {"_id": id2, "stuff": {}},
                                                                                     {"_id": id3, "stuff": {}},
                                                                                     {"_id": id4, "stuff": {}},
                                                                                     {"_id": id5, "stuff": {}},
                                                                                     {"_id": id6, "stuff": {}}])

        self.mox.ReplayAll()

        PairEntityCreator._get_entities(self.mock)

        expected_entities = {
            "entity_type": {
                str(id1): {"_id": id1, "stuff": {}},
                str(id2): {"_id": id2, "stuff": {}},
                str(id3): {"_id": id3, "stuff": {}},
                str(id4): {"_id": id4, "stuff": {}},
                str(id5): {"_id": id5, "stuff": {}},
                str(id6): {"_id": id6, "stuff": {}}
            }
        }

        self.assertEqual(self.mock.entities, expected_entities)


    ##########################################################################
    # PairEntityCreator._create_pair_entities()

    def test_create_pair_entities__different_entities(self):

        from_id1 = ObjectId()
        to_id1 = ObjectId()

        self.mock.entities = {
            "company": {
                from_id1: "from_id1",
                to_id1: "to_id1"
            }
        }

        self.mock.pair_entity_type = "pair_entity_type"

        linked_entities = "linked_entities"
        self.mock.pair_entity_helper.get_linked_entities(self.mock.ref_data, self.mock.pair_entity_type,
                                                         self.mock.entities, self.mock.db).AndReturn(linked_entities)

        self.mock.entity_from = self.mox.CreateMockAnything()
        self.mock.entity_to = self.mox.CreateMockAnything()
        from_data = "from_data"
        to_data = "to_data"

        self.mox.StubOutWithMock(datetime, 'datetime')
        timestamp = "timestamp"
        datetime.datetime.utcnow().AndReturn(timestamp)

        self.mock.entity_pairs = [
            {
                'pair_interval_from_to': [None, None],
                'pair_interval_to_from': [None, None],
                'to_id': to_id1,
                'pair_data_to_from': {'competition_strength': 0.9},
                'pair_data_from_to': {'competition_strength': 0.9},
                'from_id': from_id1
            }
        ]

        self.mock.entity_type_from = self.mock.entity_type_to = "company"
        self.mock.upsert = False

        from_links = "from_links"
        to_links = "to_links"

        pair_entity_from_rec = {"_id": ObjectId()}
        pair_entity_to_rec = {"_id": ObjectId()}

        self.mock.pair_entity_type = "pair_entity_type"
        entity_fields = "entity_fields"
        self.mock.ref_data.entity_type_map = "entity_type_map"
        self.mock.pair_entity_helper.get_pair_entity_data_fields(self.mock.pair_entity_type,
                                                                 self.mock.ref_data.entity_type_map,
                                                                 initial_fields=True).AndReturn(entity_fields)

        entity_from_rec = self.mock.entities[self.mock.entity_type_from][from_id1]
        self.mock.pair_entity_helper.get_entity_data_for_fields(entity_from_rec, entity_fields).AndReturn(from_data)
        self.mock.pair_entity_helper.get_linked_entity_data(linked_entities, entity_from_rec).AndReturn(from_links)

        entity_to_rec = self.mock.entities[self.mock.entity_type_to][to_id1]
        self.mock.pair_entity_helper.get_entity_data_for_fields(entity_to_rec, entity_fields).AndReturn(to_data)
        self.mock.pair_entity_helper.get_linked_entity_data(linked_entities, entity_to_rec).AndReturn(to_links)

        self.mock._get_entity_record(from_data, to_data, from_links, to_links, self.mock.entity_pairs[0]["pair_data_from_to"],
                                     self.mock.entity_pairs[0]["pair_interval_from_to"],
                                     from_id1, to_id1, timestamp).AndReturn(pair_entity_from_rec)
        self.mock._get_entity_record(to_data, from_data, to_links, from_links, self.mock.entity_pairs[0]["pair_data_to_from"],
                                     self.mock.entity_pairs[0]["pair_interval_to_from"],
                                     to_id1, from_id1, timestamp).AndReturn(pair_entity_to_rec)

        self.mox.StubOutWithMock(BusinessEntity, 'add_link_to_entity')

        self.mox.ReplayAll()

        PairEntityCreator._create_pair_entities(self.mock)

    def test_create_pair_entities__same_entities(self):

        from_id1 = ObjectId()

        self.mock.entities = {
            "company": {
                from_id1: "from_id1"
            }
        }

        self.mock.pair_entity_type = "pair_entity_type"

        linked_entities = "linked_entities"
        self.mock.pair_entity_helper.get_linked_entities(self.mock.ref_data, self.mock.pair_entity_type,
                                                         self.mock.entities, self.mock.db).AndReturn(linked_entities)

        self.mock.entity_from = self.mox.CreateMockAnything()
        self.mock.entity_to = self.mox.CreateMockAnything()
        from_data = "from_data"

        self.mox.StubOutWithMock(datetime, 'datetime')
        timestamp = "timestamp"
        datetime.datetime.utcnow().AndReturn(timestamp)

        self.mock.entity_pairs = [
            {
                'pair_interval_from_to': [None, None],
                'pair_interval_to_from': [None, None],
                'to_id': from_id1,
                'pair_data_to_from': {'competition_strength': 0.9},
                'pair_data_from_to': {'competition_strength': 0.9},
                'from_id': from_id1
            }
        ]

        self.mock.entity_type_from = self.mock.entity_type_to = "company"

        from_links = "from_links"

        pair_entity_from_rec = {"_id": ObjectId()}

        self.mock.pair_entity_type = "pair_entity_type"
        entity_fields = "entity_fields"
        self.mock.ref_data.entity_type_map = "entity_type_map"
        self.mock.pair_entity_helper.get_pair_entity_data_fields(self.mock.pair_entity_type,
                                                                 self.mock.ref_data.entity_type_map,
                                                                 initial_fields=True).AndReturn(entity_fields)

        entity_from_rec = self.mock.entities[self.mock.entity_type_from][from_id1]
        self.mock.pair_entity_helper.get_entity_data_for_fields(entity_from_rec, entity_fields).AndReturn(from_data)
        self.mock.pair_entity_helper.get_linked_entity_data(linked_entities, entity_from_rec).AndReturn(from_links)

        self.mock._get_entity_record(from_data, from_data, from_links, from_links, self.mock.entity_pairs[0]["pair_data_from_to"],
                                     self.mock.entity_pairs[0]["pair_interval_from_to"],
                                     from_id1, from_id1, timestamp).AndReturn(pair_entity_from_rec)

        self.mox.ReplayAll()

        PairEntityCreator._create_pair_entities(self.mock)


    def test_batch_insert_pair_entities(self):
        self.mock.pair_entity_type = "pair_entity_type"
        self.mock.upsert = False
        self.mock.pair_entities_to_create = [1,2]
        self.mock.mongo_batch_insert_max_size = 1

        self.mock.db = self.mox.CreateMockAnything()
        self.mock.db.collections = {self.mock.pair_entity_type: self.mox.CreateMockAnything()}
        self.mock.db.collections[self.mock.pair_entity_type].insert([1]).AndReturn([1])
        self.mock.db.collections[self.mock.pair_entity_type].insert([2]).AndReturn([2])

        self.mox.ReplayAll()

        PairEntityCreator._batch_insert_pair_entities(self.mock)