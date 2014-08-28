from bson.objectid import ObjectId
import mox

from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.industry_competition_pairs_updater import IndustryCompetitionPairsUpdater


class WorkflowIndustryCompetitionPairsUpdaterTests(mox.MoxTestBase):
    def setUp(self):
        super(WorkflowIndustryCompetitionPairsUpdaterTests, self).setUp()

        register_common_mox_dependencies(self.mox)

        self.mock = self.mox.CreateMock(IndustryCompetitionPairsUpdater)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.analytics = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value

        self.mock.context = {}
        self.mock.industry_ids = [ObjectId(), ObjectId(), ObjectId()]

        self.input_rec = {"task_id": "task_id", "industry_ids": self.mock.industry_ids, "context": self.mock.context}


    def doCleanups(self):
        super(WorkflowIndustryCompetitionPairsUpdaterTests, self).doCleanups()
        dependencies.clear()


    def test_search_industries(self):
        pipeline = [
            {"$match": {"data.type": "retail_banner",
                        "links.industry.industry_classification.entity_role_to": "primary_industry"}},
            {"$group": {"_id": "$links.industry.industry_classification.entity_id_to"}}
            ]
        industry_1_id = ObjectId()
        industry_2_id = ObjectId()
        industries = [{"_id": [industry_1_id]}, {"_id": [industry_2_id]}]
        self.mock.main_access.mds.call_aggregate_entities("company", pipeline,
                                                          context = self.mock.context).AndReturn(industries)

        self.mox.ReplayAll()

        IndustryCompetitionPairsUpdater._search_industries(self.mock)

        self.assertEqual([industry_1_id, industry_2_id], self.mock.industry_ids)


    def test_get_companies_with_same_primary_industry(self):
        industry_id = ObjectId()
        self.mock.company_ids_tasked = []
        query = {
            "data.type": "retail_banner",
            "links.industry.industry_classification.entity_id_to": industry_id
        }
        entity_fields = [
            "_id"
        ]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                        query=query, as_list=True)["params"]
        competing_company_ids = [[ObjectId()], [ObjectId()]]
        self.mock.main_access.mds.call_find_entities_raw("company", params, self.mock.context).AndReturn(competing_company_ids)

        self.mox.ReplayAll()

        IndustryCompetitionPairsUpdater._get_companies_with_same_primary_industry(self.mock, industry_id)

        self.assertEqual(self.mock.company_ids_in_industry, [company_id[0] for company_id in competing_company_ids])
        self.assertEqual(self.mock.company_ids_tasked, [company_id[0] for company_id in competing_company_ids])


    def test_get_competing_industries(self):
        industry_id = ObjectId()
        query = {
            "_id": industry_id
        }
        entity_fields = [
            "_id",
            "links.industry.industry_competition.entity_id_to"
        ]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                        query=query, as_list=True)["params"]
        competing_industry_1_id = ObjectId()
        competing_industry_2_id = ObjectId()
        competing_industries = [[industry_id, competing_industry_1_id], [industry_id, competing_industry_2_id],
                                [industry_id, industry_id]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params, self.mock.context).AndReturn(competing_industries)

        self.mox.ReplayAll()

        IndustryCompetitionPairsUpdater._get_competing_industries(self.mock, industry_id)

        self.assertEqual(self.mock.competing_industry_ids, [competing_industry_1_id, competing_industry_2_id])


    def test_get_competing_companies_in_other_industries(self):
        industry_id = ObjectId()
        self.mock.competing_industry_ids = [ObjectId(), ObjectId()]
        # get companies in these competing industries
        query = {
            "data.type": "retail_banner",
            "links.industry.industry_classification.entity_role_to": "primary_industry",
            "links.industry.industry_classification.entity_id_to": {"$in": self.mock.competing_industry_ids}
        }
        entity_fields = [
            "_id"
        ]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                        query=query, as_list=True)["params"]
        competing_company_ids = [[ObjectId()], [ObjectId()]]
        self.mock.main_access.mds.call_find_entities_raw("company", params, self.mock.context).AndReturn(competing_company_ids)
        self.mox.ReplayAll()

        IndustryCompetitionPairsUpdater._get_competing_companies_in_other_industries(self.mock, industry_id)

        self.assertEqual(self.mock.competing_company_ids_other_industry, [company_id[0] for company_id in competing_company_ids])


    def test_get_existing_company_competition_instances(self):
        industry_id = "ind1"
        company_id_1 = "co1"
        company_id_2 = "co2"
        self.mock.company_ids_in_industry = [company_id_1, company_id_2]
        query = {
            "data.pair.entity_id_from": {"$in": self.mock.company_ids_in_industry}
        }
        entity_fields = ["_id",
                         "data.pair.entity_id_from",
                         "data.pair.entity_id_to",
                         "data.to_links.industry.industry_classification"]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                        query=query, as_list=True)["params"]
        industry_classification = [{"entity_role_to": "primary_industry", "entity_id_to": industry_id}]
        existing_ccis = [[None, company_id_1, company_id_1, industry_classification],
                         [None, company_id_1, company_id_2, industry_classification],
                         [None, company_id_2, company_id_1, industry_classification],
                         [None, company_id_2, company_id_2, industry_classification]]
        self.mock.main_access.mds.call_find_entities_raw("company_competition_instance",
                                                         params, self.mock.context, timeout=mox.IsA(int), encode_and_decode_results=False).AndReturn(existing_ccis)

        self.mox.ReplayAll()

        icpu = IndustryCompetitionPairsUpdater(self.input_rec)
        icpu.company_ids_in_industry = self.mock.company_ids_in_industry
        icpu.main_access = self.mock.main_access
        icpu.main_param = self.mock.main_param

        icpu._get_existing_company_competition_instances()

        self.assertEqual(set(pair for pair in ["co1~co1~ind1", "co1~co2~ind1", "co2~co1~ind1", "co2~co2~ind1"]),
                         icpu.set_existing_pair_ids)


    def test_calculate_pairs_to_create_and_delete_per_company(self):
        company_1_id = ObjectId()
        company_2_id = ObjectId()
        company_3_id = ObjectId()
        company_4_id = ObjectId()
        company_5_id = ObjectId()
        industry_id = ObjectId()
        self.mock.company_ids_in_industry = [company_1_id, company_2_id, company_3_id]
        self.mock.competing_company_ids_other_industry = [company_4_id, company_5_id]
        self.mock.set_existing_pair_ids = set()
        self.mock.helper = self.mox.CreateMockAnything()

        self.mock.helper.get_pair_actions_with_specified_competitors(
            company_1_id, [company_1_id, company_2_id, company_3_id, company_4_id, company_5_id]).AndReturn(([], [], []))
        self.mock._IndustryCompetitionPairsUpdater__tally_pairs_we_need_to_create([])
        self.mock.helper.get_pair_actions_with_specified_competitors(
            company_2_id, [company_2_id, company_3_id, company_4_id, company_5_id]).AndReturn(([], [], []))
        self.mock._IndustryCompetitionPairsUpdater__tally_pairs_we_need_to_create([])
        self.mock.helper.get_pair_actions_with_specified_competitors(
            company_3_id, [company_3_id, company_4_id, company_5_id]).AndReturn(([], [], []))
        self.mock._IndustryCompetitionPairsUpdater__tally_pairs_we_need_to_create([])

        self.mox.ReplayAll()

        IndustryCompetitionPairsUpdater._calculate_pairs_to_create_per_company(self.mock)


    def test_calculate_pairs_to_delete_per_company(self):
        icpu = IndustryCompetitionPairsUpdater(self.input_rec)
        icpu.set_existing_pair_ids = set(pair for pair in ["co1~co1~ind1", "co1~co2~ind2", "co2~co1~ind1", "co2~co2~ind2"])
        icpu.set_competing_company_pair_ids = set(pair for pair in ["co1~co1~ind1"])

        icpu._calculate_pairs_to_delete_per_company("ind1")
        self.assertEqual(len(icpu.pairs_to_delete["pairs_to_delete_from_ids"]), 2)
        self.assertIn('co1', icpu.pairs_to_delete["pairs_to_delete_from_ids"])
        self.assertIn('co2', icpu.pairs_to_delete["pairs_to_delete_from_ids"])
        self.assertEqual(icpu.pairs_to_delete["pairs_to_delete_to_ids"], ['co2'])


    def test__tally_pairs_we_need_to_create(self):
        pairs = [{"from_id": "co1", "to_id": "co1", "to_industry_id": "ind1"},
                 {"from_id": "co1", "to_id": "co2", "to_industry_id": "ind2"},
                 {"from_id": "co3", "to_id": "co1", "to_industry_id": "ind1"},
                 {"from_id": "co4", "to_id": "co1", "to_industry_id": "ind1"},]
        icpu = IndustryCompetitionPairsUpdater(self.input_rec)
        icpu.pairs_to_create = []
        icpu.set_competing_company_pair_ids = set()
        icpu.set_existing_pair_ids = set(pair for pair in ["co1~co1~ind1", "co1~co2~ind2", "co2~co1~ind1", "co2~co2~ind2"])

        icpu._IndustryCompetitionPairsUpdater__tally_pairs_we_need_to_create(pairs)
        self.assertEqual(len(icpu.set_competing_company_pair_ids), 4)
        self.assertIn('co1~co1~ind1', icpu.set_competing_company_pair_ids)
        self.assertIn('co1~co2~ind2', icpu.set_competing_company_pair_ids)
        self.assertIn('co3~co1~ind1', icpu.set_competing_company_pair_ids)
        self.assertIn('co4~co1~ind1', icpu.set_competing_company_pair_ids)
        self.assertEqual(len(icpu.pairs_to_create), 2)
        self.assertIn({'to_id': 'co1', 'to_industry_id': 'ind1', 'from_id': 'co3'}, icpu.pairs_to_create)
        self.assertIn({'to_id': 'co1', 'to_industry_id': 'ind1', 'from_id': 'co4'}, icpu.pairs_to_create)

