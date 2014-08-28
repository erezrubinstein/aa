from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from common.utilities.misc_utilities import process_input_query
from core.common.utilities.errors import *
from core.common.utilities.helpers import generate_id
from core.service.svc_master_data_storage.implementation.mds_service import MasterDataService
import unittest
import mox


__author__ = 'vgold'


class MDSServiceTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(MDSServiceTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock_svc = self.mox.CreateMock(MasterDataService)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock_svc.cfg = Dependency("MoxConfig").value
        self.mock_svc.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_mds_service.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

    def doCleanups(self):

        super(MDSServiceTests, self).doCleanups()
        dependencies.clear()

    ############################################################
    # MasterDataService.__process_input_query()

    def test_process_input_query(self):

        oid1 = generate_id()
        oid2 = generate_id()
        oid3 = generate_id()

        query = {"_id": str(oid1)}
        result = process_input_query(query)
        self.assertEqual(result["_id"], oid1)

        query = {"_id": {"oid": str(oid1)}}
        result = process_input_query(query)
        self.assertEqual(result["_id"]["oid"], oid1)

        query = {"_id": {"list": [str(oid1), str(oid2), str(oid3)]}}
        result = process_input_query(query)
        self.assertEqual(result["_id"]["list"], [oid1, oid2, oid3])

        query = {"_id": {"dict": {"list": [str(oid1), str(oid2), str(oid3)]}}}
        result = process_input_query(query)
        self.assertEqual(result["_id"]["dict"]["list"], [oid1, oid2, oid3])

        query = {"_id": {"dict1": {"dict2": {"list": [str(oid1), str(oid2), str(oid3)]}}}}
        self.assertRaises(InputError, process_input_query, *(query,))


    def test__build_delete_pair_entities_batch_queries(self):
        from_key_1 = [generate_id()]
        from_key_2 = [generate_id()]
        to_key_1 = [generate_id()]
        to_key_2 = [generate_id()]
        request_data = {
            "pairs_to_delete_from_ids": [generate_id(), generate_id()],
            "pairs_to_delete_to_ids": [generate_id(), generate_id()],
            "from_links": {"from_key_1": from_key_1, "from_key_2": from_key_2},
            "to_links": {"to_key_1": to_key_1, "to_key_2": to_key_2}
        }
        query, query_reverse = \
            MasterDataService._MasterDataService__build_delete_pair_entities_batch_queries(self.mock_svc, request_data)
        expected_query = {
            "data.to_links.to_key_2": {"$in": to_key_2},
            "data.to_links.to_key_1": {"$in": to_key_1},
            "data.pair.entity_id_from": {"$in": request_data["pairs_to_delete_from_ids"]},
            "data.from_links.from_key_1": {"$in": from_key_1},
            "data.pair.entity_id_to": {"$in": request_data["pairs_to_delete_to_ids"]},
            "data.from_links.from_key_2": {"$in": from_key_2}
        }
        expected_query_reverse = {
            "data.to_links.from_key_2": {"$in": from_key_2},
            "data.to_links.from_key_1": {"$in": from_key_1},
            "data.from_links.to_key_2": {"$in": to_key_2},
            "data.pair.entity_id_from": {"$in": request_data["pairs_to_delete_to_ids"]},
            "data.from_links.to_key_1": {"$in": to_key_1},
            "data.pair.entity_id_to": {"$in": request_data["pairs_to_delete_from_ids"]}
        }
        self.assertEqual(query, expected_query)
        self.assertEqual(query_reverse, expected_query_reverse)

if __name__ == '__main__':
    unittest.main()