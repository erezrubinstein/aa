from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company


class MDSTestCollection(ServiceTestCollection):

    def initialize(self, data_params=None):

        self.user_id = 'test@nexusri.com'
        self.source = "mds_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

        self.maxDiff = None

    def setUp(self):
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def test_mds_aggregate(self):

        data_A = {'team': 'A'}
        data_B = {'team': 'B'}
        data_C = {'team': 'C'}

        store_1_team_A_id = self.mds_access.call_add_entity('store', 'A', data_A, self.context)
        store_2_team_A_id = self.mds_access.call_add_entity('store', 'A', data_A, self.context)
        store_3_team_A_id = self.mds_access.call_add_entity('store', 'A', data_A, self.context)

        store_1_team_B_id = self.mds_access.call_add_entity('store', 'B', data_B, self.context)
        store_2_team_B_id = self.mds_access.call_add_entity('store', 'B', data_B, self.context)
        store_3_team_B_id = self.mds_access.call_add_entity('store', 'B', data_B, self.context)

        store_1_team_C_id = self.mds_access.call_add_entity('store', 'C', data_C, self.context)
        store_2_team_C_id = self.mds_access.call_add_entity('store', 'C', data_C, self.context)
        store_3_team_C_id = self.mds_access.call_add_entity('store', 'C', data_C, self.context)

        pipeline_A = {'$match': {'data.team': 'A'}}
        pipeline_B = {'$match': {'data.team': 'B'}}
        pipeline_C = {'$match': {'data.team': 'C'}}

        A_entities = self.mds_access.call_aggregate_entities('store', pipeline_A)
        B_entities = self.mds_access.call_aggregate_entities('store', pipeline_B)
        C_entities = self.mds_access.call_aggregate_entities('store', pipeline_C)

        A_ids = [str(entity['_id']) for entity in A_entities]
        B_ids = [str(entity['_id']) for entity in B_entities]
        C_ids = [str(entity['_id']) for entity in C_entities]

        self.test_case.assertEqual(set(A_ids), {store_1_team_A_id, store_2_team_A_id, store_3_team_A_id})
        self.test_case.assertEqual(set(B_ids), {store_1_team_B_id, store_2_team_B_id, store_3_team_B_id})
        self.test_case.assertEqual(set(C_ids), {store_1_team_C_id, store_2_team_C_id, store_3_team_C_id})


    def test_mds_count(self):

        # insert three companies
        company_id_1 = insert_test_company()
        company_id_2 = insert_test_company()
        company_id_3 = insert_test_company()

        # get count of all companies and verify
        count_all = self.main_access.mds.call_count_entities("company")
        self.test_case.assertEqual(count_all, 3)

        # get count of first two ids and verify
        query = { "_id": { "$in": [company_id_1, company_id_2] }}
        count = self.main_access.mds.call_count_entities("company", query)
        self.test_case.assertEqual(count, 2)


    def test_mds_aggregate__match_project(self):

        data_A = {'team': 'A', 'woot': 1, 'chicken': 2}
        data_B = {'team': 'B', 'woot': 2, 'chicken': 1}
        data_C = {'team': 'C', 'woot': 2, 'chicken': 1}

        store_1_team_A_id = self.mds_access.call_add_entity('store', 'A', data_A, self.context)
        store_2_team_A_id = self.mds_access.call_add_entity('store', 'A', data_A, self.context)
        store_3_team_A_id = self.mds_access.call_add_entity('store', 'A', data_A, self.context)

        # add a corrupt store that we do not want to come up in the query
        corrupt_data_A = {'team': 'A', 'woot': 2, 'chicken': 1}
        self.mds_access.call_add_entity('store', 'A', corrupt_data_A, self.context)

        self.mds_access.call_add_entity('store', 'B', data_B, self.context)
        self.mds_access.call_add_entity('store', 'B', data_B, self.context)
        self.mds_access.call_add_entity('store', 'B', data_B, self.context)

        self.mds_access.call_add_entity('store', 'C', data_C, self.context)
        self.mds_access.call_add_entity('store', 'C', data_C, self.context)
        self.mds_access.call_add_entity('store', 'C', data_C, self.context)

        project = {
            '$project': {
                'data.woot': 1,
                'data.chicken': 1,
                'chicken_greater_than_woot': {'$gt': ['$data.chicken', '$data.woot']}
            }
        }

        pipeline_A = [{'$match': {'data.team': 'A'}}, project, {'$match': {'chicken_greater_than_woot': True}}]
        pipeline_B = [{'$match': {'data.team': 'B'}}, project, {'$match': {'chicken_greater_than_woot': True}}]
        pipeline_C = [{'$match': {'data.team': 'C'}}, project, {'$match': {'chicken_greater_than_woot': True}}]

        A_entities = self.mds_access.call_aggregate_entities('store', pipeline_A)
        B_entities = self.mds_access.call_aggregate_entities('store', pipeline_B)
        C_entities = self.mds_access.call_aggregate_entities('store', pipeline_C)

        A_ids = [str(entity['_id']) for entity in A_entities]
        B_ids = [str(entity['_id']) for entity in B_entities]
        C_ids = [str(entity['_id']) for entity in C_entities]

        self.test_case.assertEqual(len(A_ids), 3)
        self.test_case.assertEqual(set(A_ids), {store_1_team_A_id, store_2_team_A_id, store_3_team_A_id})
        self.test_case.assertEqual(set(B_ids), set())
        self.test_case.assertEqual(set(C_ids), set())


###################################################################################################
