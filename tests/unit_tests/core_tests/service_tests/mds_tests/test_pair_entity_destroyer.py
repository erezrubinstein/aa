from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import NotFoundError
from core.service.svc_master_data_storage.implementation.pair_entity_destroyer import PairEntityDestroyer
import mox


__author__ = 'vgold'


class PairEntityDestroyerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(PairEntityDestroyerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on instance for calls to record
        self.mock = self.mox.CreateMock(PairEntityDestroyer)
        self.mock.db = self.mox.CreateMockAnything()
        self.mock.svc = self.mox.CreateMockAnything()
        self.mock.BusinessEntity = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        self.mock.context = {
            "user_id": "tester",
            "source": "test_pair_entity_creator.py"
        }

    def doCleanups(self):

        super(PairEntityDestroyerTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # PairEntityDestroyer._get_pair_entities()

    def test_get_pair_entities__two_returned(self):

        self.mock.pair_entity_type = "pair_entity_type"
        self.mock.relation_type = "relation_type"

        self.mock.entity_type_from = "entity_type_from"
        self.mock.entity_id_from = "entity_id_from"
        self.mock.entity_role_from = "entity_role_from"

        self.mock.entity_type_to = "entity_type_to"
        self.mock.entity_id_to = "entity_id_to"
        self.mock.entity_role_to = "entity_role_to"

        self.mock.pair_link_desc = "pair_link_desc"

        projection = {
            "_id": 1
        }

        record_cursor = self.mox.CreateMockAnything()
        self.mock.db.find(self.mock.pair_entity_type, mox.IgnoreArg(), projection).AndReturn(record_cursor)

        record_cursor.count().AndReturn(2)

        self.mox.ReplayAll()

        result = PairEntityDestroyer._get_pair_entities(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(record_cursor, self.mock.record_cursor)

    def test_get_pair_entities__zero_returned(self):

        self.mock.pair_entity_type = "pair_entity_type"
        self.mock.relation_type = "relation_type"

        self.mock.entity_type_from = "entity_type_from"
        self.mock.entity_id_from = "entity_id_from"
        self.mock.entity_role_from = "entity_role_from"

        self.mock.entity_type_to = "entity_type_to"
        self.mock.entity_id_to = "entity_id_to"
        self.mock.entity_role_to = "entity_role_to"

        self.mock.pair_link_desc = "pair_link_desc"

        projection = {
            "_id": 1
        }

        record_cursor = self.mox.CreateMockAnything()
        self.mock.db.find(self.mock.pair_entity_type, mox.IgnoreArg(), projection).AndReturn(record_cursor)

        record_cursor.count().AndReturn(0)

        self.mox.ReplayAll()

        with self.assertRaises(NotFoundError):
            PairEntityDestroyer._get_pair_entities(self.mock)

    ##########################################################################
    # PairEntityDestroyer._delete_pair_entities()

    def test_delete_pair_entities(self):

        self.mock.record_cursor = [{"_id": 1}, {"_id": 2}]
        deleted_ids = [1, 2]
        self.mock.pair_entity_type = "pair_entity_type"

        self.mock.svc.del_entity(self.mock.pair_entity_type, deleted_ids[0], self.mock.context)
        self.mock.svc.del_entity(self.mock.pair_entity_type, deleted_ids[1], self.mock.context)

        self.mox.ReplayAll()

        result = PairEntityDestroyer._delete_pair_entities(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(deleted_ids, self.mock.deleted_ids)



