from core.common.business_logic.service_entity_logic.company_competition_pairs_helper import CompanyCompetitionPairsHelper
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from bson.objectid import ObjectId
import unittest
import mox


class CompanyCompetitionPairsHelperTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(CompanyCompetitionPairsHelperTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on instance for calls to record
        self.mock = self.mox.CreateMock(CompanyCompetitionPairsHelper)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.company_id = ObjectId()
        self.mock.company_industry_id = ObjectId()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value

        self.mock.context = {
            "user_id": "tester",
            "source": "test_company_competition_pairs_helper.py"
        }

        self.maxDiff = None

    def doCleanups(self):
        super(CompanyCompetitionPairsHelperTests, self).doCleanups()
        dependencies.clear()
        
    def test_get_pair_actions(self):
        """
        Just testing the order.
        """
        self.mock.pairs_to_create = self.mock.pairs_to_create_to_ids = self.mock.pairs_to_delete = self.mock.competition_weights_to_update = None
        self.mock._get_company()
        self.mock._get_competing_industries()
        self.mock._get_competing_companies_in_other_industries()
        self.mock._get_current_competing_companies()
        self.mock._check_if_company_industry_changed()
        self.mock._get_competition_weights_to_update()
        self.mock._calculate_pairs_to_create_and_delete()
        self.mock._create_company_competition_instance_records()

        self.mox.ReplayAll()

        CompanyCompetitionPairsHelper.get_pair_actions(self.mock, ObjectId())

    def test_get_pair_actions_with_specified_competitors(self):
        """
        Just testing the order and that certain self member variables get set properly.
        """
        company_id = ObjectId()
        self.mock.company_id = company_id
        competing_companies = ["a", "b", "c"]
        self.mock.pairs_to_create = self.mock.competition_weights_to_update = None
        self.mock._get_company()
        self.mock._get_competing_industries()
        self.mock._get_competing_companies_in_other_industries()
        self.mock._get_current_competing_companies()
        self.mock._check_if_company_industry_changed()
        self.mock._get_competition_weights_to_update()
        self.mock._create_company_competition_instance_records()

        self.mox.ReplayAll()

        CompanyCompetitionPairsHelper.get_pair_actions_with_specified_competitors(self.mock, company_id, competing_companies)

        self.assertEqual(self.mock.company_id, company_id)
        self.assertEqual(self.mock.pairs_to_create_to_ids, competing_companies)

    def test_execute_pair_actions__with_delete(self):
        """
        Just testing the order.
        """
        pairs_to_delete = ["a", "b", "c"]
        pairs_to_create = [{"asdf": "qwer"}]
        weights_to_update = []

        self.mock.main_access.mds.call_delete_pair_entities_batch_raw("company", "company", "company_competition",
                                                                 "competitor", "competitor", pairs_to_delete,
                                                                 self.mock.context, timeout=mox.IsA(int))
        self.mock.main_access.mds.call_create_pair_entities(pairs_to_create, "company", "competitor", "company",
                                                            "competitor", "company_competition", self.mock.context, timeout=mox.IsA(int))

        self.mox.ReplayAll()

        CompanyCompetitionPairsHelper.execute_pair_actions(self.mock, pairs_to_create, pairs_to_delete, weights_to_update)

    def test_execute_pair_actions__without_delete(self):
        """
        Just testing the order.
        """
        pairs_to_delete = None
        pairs_to_create = [{"asdf": "qwer"}]
        weights_to_update = []

        self.mock.main_access.mds.call_create_pair_entities(pairs_to_create, "company", "competitor", "company",
                                                            "competitor", "company_competition", self.mock.context, timeout=mox.IsA(int))

        self.mox.ReplayAll()

        CompanyCompetitionPairsHelper.execute_pair_actions(self.mock, pairs_to_create, pairs_to_delete, weights_to_update)

    def test_execute_pair_actions__with_weights(self):
        """
        Just testing the order. And the updates. And the hey-hey-hey.
        """
        pairs_to_delete = ["a", "b", "c"]
        pairs_to_create = [{"asdf": "qwer"}]

        self.mock.main_access.mds.call_delete_pair_entities_batch_raw("company", "company", "company_competition",
                                                                 "competitor", "competitor", pairs_to_delete,
                                                                 self.mock.context, timeout=mox.IsA(int))
        self.mock.main_access.mds.call_create_pair_entities(pairs_to_create, "company", "competitor", "company",
                                                            "competitor", "company_competition", self.mock.context, timeout=mox.IsA(int))

        # updates
        company_id = ObjectId()
        self.mock.company_id = str(company_id)
        competitor_id = ObjectId()
        weights_to_update = [{"competitor_id": competitor_id, "competition_strength": "impressive", "competition_type": "most impressive"}]
        query_operations_list = [
            {
                "query": {
                    "data.pair.entity_id_from": company_id,
                    "data.pair.entity_id_to": competitor_id,
                    "$or": [
                        {"data.pair.data.competition_strength": {"$ne": "impressive"}},
                        {"data.pair.data.competition_type": {"$ne": "most impressive"}}
                    ]
                },
                "operations": {
                    "$set": {
                        "data.pair.data.competition_strength": "impressive",
                        "data.pair.data.competition_type": "most impressive"
                    }
                }
            }
        ]
        self.mock.main_access.mds.call_multi_batch_update_entities("company_competition_instance", query_operations_list,
                                                                   self.mock.context, timeout=mox.IsA(int), use_new_json_encoder=True)

        self.mox.ReplayAll()

        CompanyCompetitionPairsHelper.execute_pair_actions(self.mock, pairs_to_create, pairs_to_delete, weights_to_update)


    def test_get_competing_industries__with_self_industry(self):
        query = {"_id": self.mock.company_industry_id}
        entity_fields = [
            "_id",
            "links.industry.industry_competition.entity_id_to",
            "links.industry.industry_competition.interval",
            "links.industry.industry_competition.data"
        ]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                        query=query, as_list=True)["params"]
        competing_industry_1_interval = [1,2]
        competing_industry_1_data = {"home_to_away": {"weight": 1.0}, "away_to_home": {"weight": 0.5}}
        competing_industry_2_id = ObjectId()
        competing_industry_2_interval = [3,4]
        competing_industry_2_data = {"home_to_away": {"weight": 0.9}, "away_to_home": {"weight": 0.6}}
        competing_industries = [[self.mock.company_industry_id, self.mock.company_industry_id, competing_industry_1_interval, competing_industry_1_data],
                                [self.mock.company_industry_id, competing_industry_2_id, competing_industry_2_interval, competing_industry_2_data],
                                [self.mock.company_industry_id, ObjectId(), [], None],
                                [self.mock.company_industry_id, None, [], competing_industry_1_data]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params, self.mock.context, encode_and_decode_results=False).AndReturn(competing_industries)

        self.mox.ReplayAll()

        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.main_access = self.mock.main_access
        ccph.main_param = self.mock.main_param
        ccph.company_industry_id = self.mock.company_industry_id

        ccph._get_competing_industries()

        expected_competing_industry_ids = [self.mock.company_industry_id, competing_industry_2_id]
        expected_competing_industries = {
            self.mock.company_industry_id: {"interval": competing_industry_1_interval, "data": competing_industry_1_data},
            competing_industry_2_id: {"interval": competing_industry_2_interval, "data": competing_industry_2_data}
        }

        self.assertEqual(ccph.competing_industry_ids, expected_competing_industry_ids)
        self.assertEqual(ccph.competing_industries, expected_competing_industries)

    def test_get_competing_industries__without_self_industry(self):
        query = {"_id": self.mock.company_industry_id}
        entity_fields = [
            "_id",
            "links.industry.industry_competition.entity_id_to",
            "links.industry.industry_competition.interval",
            "links.industry.industry_competition.data"
        ]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                        query=query, as_list=True)["params"]
        competing_industry_1_id = ObjectId()
        competing_industry_1_interval = [1,2]
        competing_industry_1_data = {"home_to_away": {"weight": 1.0}, "away_to_home": {"weight": 0.5}}
        competing_industry_2_id = ObjectId()
        competing_industry_2_interval = [3,4]
        competing_industry_2_data = {"home_to_away": {"weight": 0.9}, "away_to_home": {"weight": 0.6}}
        competing_industries = [[self.mock.company_industry_id, competing_industry_1_id, competing_industry_1_interval, competing_industry_1_data],
                                [self.mock.company_industry_id, competing_industry_2_id, competing_industry_2_interval, competing_industry_2_data],
                                [self.mock.company_industry_id, ObjectId(), [], None],
                                [self.mock.company_industry_id, None, [], competing_industry_1_data]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params, self.mock.context, encode_and_decode_results=False).AndReturn(competing_industries)

        self.mox.ReplayAll()

        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.main_access = self.mock.main_access
        ccph.main_param = self.mock.main_param
        ccph.company_industry_id = self.mock.company_industry_id

        ccph._get_competing_industries()

        expected_competing_industry_ids = [competing_industry_1_id, competing_industry_2_id,
                                           self.mock.company_industry_id]
        expected_competing_industries = {
            self.mock.company_industry_id: {"interval": [None, None], "data": {"home_to_away": {"weight": 1.0},
                                                                               "away_to_home": {"weight": 1.0}}},
            competing_industry_2_id: {"interval": competing_industry_2_interval, "data": competing_industry_2_data},
            competing_industry_1_id: {"interval": competing_industry_1_interval, "data": competing_industry_1_data}
        }

        self.assertEqual(ccph.competing_industry_ids, expected_competing_industry_ids)
        self.assertEqual(ccph.competing_industries, expected_competing_industries)

    def test_get_competing_industries_in_other_industries(self):
        competing_industry_id_1 = ObjectId()
        competing_industry_id_2 = ObjectId()
        self.mock.competing_industry_ids = [competing_industry_id_1, competing_industry_id_2]
        query = {
            "data.type": "retail_banner",
            "links.industry.industry_classification" : {
                "$elemMatch": {
                    "entity_role_to": "primary_industry",
                    "entity_id_to": { "$in": self.mock.competing_industry_ids }
                }
            }
        }
        entity_fields = [
            "_id",
            "links.industry.industry_classification.entity_id_to"
        ]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                        query=query, as_list=True)["params"]
        competing_company_id_1 = ObjectId()
        competing_company_id_2 = ObjectId()
        competing_company_ids = [[competing_company_id_1, competing_industry_id_1],
                                 [competing_company_id_2, competing_industry_id_2]]
        self.mock.main_access.mds.call_find_entities_raw("company", params, self.mock.context, encode_and_decode_results=False).AndReturn(competing_company_ids)

        self.mox.ReplayAll()

        CompanyCompetitionPairsHelper._get_competing_companies_in_other_industries(self.mock)

        expected_competing_companies = {
            competing_company_id_1: competing_industry_id_1,
            competing_company_id_2: competing_industry_id_2
        }
        self.assertEqual(self.mock.competing_companies, expected_competing_companies)
        self.assertEqual(len(self.mock.set_competing_company_ids), 2)
        self.assertIn(competing_company_id_1, self.mock.set_competing_company_ids)
        self.assertIn(competing_company_id_2, self.mock.set_competing_company_ids)

    def test_get_current_competing_companies(self):
        query = {
            "data.pair.entity_id_from": self.mock.company_id
        }
        entity_fields = [
            "_id",
            "data.pair.entity_id_to",
            "data.from_links.industry.industry_classification",
            "data.to_links.industry.industry_classification",
            "data.pair.data"
        ]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                        query=query, as_list=True)["params"]
        from_industry_id = ObjectId()
        to_industry_id = ObjectId()
        from_industry = [{"entity_role_to": "primary_industry", "entity_id_to": from_industry_id},
                         {"entity_role_to": "blah", "entity_id_to": ObjectId()}]
        to_industry = [{"entity_role_to": "primary_industry", "entity_id_to": to_industry_id},
                       {"entity_role_to": "blah", "entity_id_to": ObjectId()}]
        pair_data = {"impressive": "most impressive"}
        self.mock.competing_industry_ids = [to_industry_id]
        competing_company_id_1 = ObjectId()
        competing_company_id_2 = ObjectId()
        current_competing_company_ids = [["id1", competing_company_id_1, from_industry, to_industry, pair_data],
                                         ["id2", competing_company_id_2, from_industry, to_industry, pair_data]]
        self.mock.main_access.mds.call_find_entities_raw("company_competition_instance",
                                                         params, self.mock.context, encode_and_decode_results=False).AndReturn(current_competing_company_ids)

        self.mox.ReplayAll()

        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.main_access = self.mock.main_access
        ccph.main_param = self.mock.main_param
        ccph.company_id = self.mock.company_id

        ccph._get_current_competing_companies()

        expected_current_competing_companies = {
            competing_company_id_1: {"from_primary_industry_id": from_industry_id, "to_primary_industry_id": to_industry_id, "pair_data": pair_data},
            competing_company_id_2: {"from_primary_industry_id": from_industry_id, "to_primary_industry_id": to_industry_id, "pair_data": pair_data}
        }
        self.assertEqual(ccph.current_competing_companies, expected_current_competing_companies)
        self.assertEqual(len(ccph.set_current_competing_company_ids), 2)
        self.assertIn(competing_company_id_1, ccph.set_current_competing_company_ids)
        self.assertIn(competing_company_id_2, ccph.set_current_competing_company_ids)

    def test_check_if_company_industry_changed__true(self):
        competing_company_id_1 = ObjectId()
        competing_company_id_2 = ObjectId()
        from_industry_id = ObjectId()
        to_industry_id = ObjectId()

        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_industry_id = self.mock.company_industry_id
        ccph.current_competing_companies = {
            str(competing_company_id_1): {"from_primary_industry_id": from_industry_id, "to_primary_industry_id": to_industry_id},
            str(competing_company_id_2): {"from_primary_industry_id": from_industry_id, "to_primary_industry_id": to_industry_id}
        }
        ccph._check_if_company_industry_changed()
        self.assertTrue(ccph.company_industry_changed)

    def test_check_if_company_industry_changed__false(self):
        competing_company_id_1 = ObjectId()
        competing_company_id_2 = ObjectId()
        to_industry_id = ObjectId()

        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_industry_id = self.mock.company_industry_id
        ccph.current_competing_companies = {
            str(competing_company_id_1): {"from_primary_industry_id": self.mock.company_industry_id, "to_primary_industry_id": to_industry_id},
            str(competing_company_id_2): {"from_primary_industry_id": self.mock.company_industry_id, "to_primary_industry_id": to_industry_id}
        }
        ccph._check_if_company_industry_changed()
        self.assertFalse(ccph.company_industry_changed)

    def test_get_competition_weights_to_update__negative(self):

        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.current_competing_companies = []
        ccph._get_competition_weights_to_update()
        self.assertListEqual(ccph.competition_weights_to_update, [])

    def test_get_competition_weights_to_update__positive(self):
        competing_company_id_1 = ObjectId()
        competing_company_id_2 = ObjectId()
        to_industry_id_1 = ObjectId()
        to_industry_id_2 = ObjectId()

        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_id = self.mock.company_id
        ccph.current_competing_companies = {
            str(competing_company_id_1): {"from_primary_industry_id": self.mock.company_industry_id, "to_primary_industry_id": to_industry_id_1, "pair_data":{"competition_strength":1.0}},
            str(competing_company_id_2): {"from_primary_industry_id": self.mock.company_industry_id, "to_primary_industry_id": to_industry_id_2, "pair_data":{"competition_strength":1.0}}
        }
        competing_industry_data_1 = {"home_to_away": {"weight": 0.7}, "away_to_home": {"weight": 0.5}}
        competing_industry_data_2 = {"home_to_away": {"weight": 1.0}, "away_to_home": {"weight": 0.8}}
        ccph.competing_industries = {
            to_industry_id_1: {
                "interval": [1,2],
                "data": competing_industry_data_1
            },
            to_industry_id_2: {
                "interval": [1,2],
                "data": competing_industry_data_2
            }
        }
        # needful
        ccph._get_competition_weights_to_update()

        # only company 1 should be updated; the weights for company 2 didn't change
        self.assertEqual(ccph.competition_weights_to_update, [{
                                "competitor_id": str(competing_company_id_1),
                                "competition_strength": 0.7,
                                "competition_type": "primary"
                            }])

    def test_calculate_pairs_to_create_and_delete__industry_changed(self):
        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_industry_changed = True
        ccph.company_id = self.mock.company_id
        current_competing_company_id_1 = ObjectId()
        current_competing_company_id_2 = ObjectId()
        competing_company_id_1 = ObjectId()
        competing_company_id_2 = ObjectId()
        ccph.set_current_competing_company_ids = set(id for id in [current_competing_company_id_1,
                                                                   current_competing_company_id_2])
        ccph.set_competing_company_ids = set(id for id in [competing_company_id_1, competing_company_id_2])
        ccph._calculate_pairs_to_create_and_delete()

        self.assertEqual(ccph.pairs_to_delete["pairs_to_delete_from_ids"], [self.mock.company_id])
        self.assertEqual(len(ccph.pairs_to_delete["pairs_to_delete_to_ids"]), 2)
        self.assertIn(current_competing_company_id_1, ccph.pairs_to_delete["pairs_to_delete_to_ids"])
        self.assertIn(current_competing_company_id_2, ccph.pairs_to_delete["pairs_to_delete_to_ids"])

        self.assertEqual(len(ccph.pairs_to_create_to_ids), 2)
        self.assertIn(competing_company_id_1, ccph.pairs_to_create_to_ids)
        self.assertIn(competing_company_id_2, ccph.pairs_to_create_to_ids)

    def test_calculate_pairs_to_create_and_delete__industry_same(self):
        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_industry_changed = False
        ccph.company_id = self.mock.company_id
        competing_company_id_1 = ObjectId()
        competing_company_id_2 = ObjectId()
        current_competing_company_id_2 = ObjectId()
        ccph.set_current_competing_company_ids = set(id for id in [competing_company_id_1,
                                                                   current_competing_company_id_2])
        ccph.set_competing_company_ids = set(id for id in [competing_company_id_1, competing_company_id_2])
        ccph._calculate_pairs_to_create_and_delete()

        self.assertEqual(ccph.pairs_to_create_to_ids, [competing_company_id_2])
        self.assertEqual(ccph.pairs_to_delete["pairs_to_delete_from_ids"], [self.mock.company_id])
        self.assertEqual(ccph.pairs_to_delete["pairs_to_delete_to_ids"], [current_competing_company_id_2])

    def test_create_company_competition_instance_records(self):
        competing_company_id_1 = ObjectId()
        self.mock.pairs_to_create_to_ids = [self.mock.company_id, competing_company_id_1]
        self.mock.competing_companies = {
            competing_company_id_1: "to_industry_id"
        }
        self.mock._get_pair_from_to_items(self.mock.company_id).\
            AndReturn(("pair_data_from_to", "pair_data_to_from", "pair_interval_from_to", "pair_interval_to_from"))
        self.mock._get_pair_from_to_items(competing_company_id_1).\
            AndReturn(("pair_data_from_to2", "pair_data_to_from2", "pair_interval_from_to2", "pair_interval_to_from2"))
        expected_pairs_to_create = [
            {
                "from_id": self.mock.company_id,
                "to_id": self.mock.company_id,
                "pair_data_from_to": "pair_data_from_to",
                "pair_data_to_from": "pair_data_from_to",
                "pair_interval_from_to": [None, None],
                "pair_interval_to_from": [None, None],
                "to_industry_id": self.mock.company_industry_id
            },
            {
                "from_id": self.mock.company_id,
                "to_id": competing_company_id_1,
                "pair_data_from_to": "pair_data_from_to2",
                "pair_data_to_from": "pair_data_to_from2",
                "pair_interval_from_to": "pair_interval_from_to2",
                "pair_interval_to_from": "pair_interval_to_from2",
                "to_industry_id": "to_industry_id"
            }
        ]

        self.mox.ReplayAll()

        CompanyCompetitionPairsHelper._create_company_competition_instance_records(self.mock)
        self.assertEqual(expected_pairs_to_create, self.mock.pairs_to_create)

    def test__get_pair_from_to_items__self_compete_interval_provided(self):

        competing_industry_1_data = {"home_to_away": {"weight": 1.0}, "away_to_home": {"weight": 0.5}}
        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_id = self.mock.company_id
        ccph.competing_companies = {
            self.mock.company_id: self.mock.company_industry_id
        }
        ccph.competing_industries = {
            self.mock.company_industry_id: {
                "interval": [1,2],
                "data": competing_industry_1_data
            }
        }

        pair_data_from_to, pair_data_to_from, pair_interval_from_to, pair_interval_to_from = \
            ccph._get_pair_from_to_items(self.mock.company_id)

        self.assertEqual(pair_data_from_to, {"competition_strength": 1.0, "competition_type": "cluster"})
        self.assertEqual(pair_data_to_from, {})
        self.assertEqual(pair_interval_from_to, [1,2])
        self.assertEqual(pair_interval_to_from, [None, None])

    def test__get_pair_from_to_items__self_compete_interval_missing(self):

        competing_industry_1_data = {"home_to_away": {"weight": 1.0}, "away_to_home": {"weight": 0.5}}
        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_id = self.mock.company_id
        ccph.competing_companies = {
            self.mock.company_id: self.mock.company_industry_id
        }
        ccph.competing_industries = {
            self.mock.company_industry_id: {
                "interval": None,
                "data": competing_industry_1_data
            }
        }

        pair_data_from_to, pair_data_to_from, pair_interval_from_to, pair_interval_to_from = \
            ccph._get_pair_from_to_items(self.mock.company_id)

        self.assertEqual(pair_data_from_to, {"competition_strength": 1.0, "competition_type": "cluster"})
        self.assertEqual(pair_data_to_from, {})
        self.assertEqual(pair_interval_from_to, [None, None])
        self.assertEqual(pair_interval_to_from, [None, None])

    def test__get_pair_from_to_items__other_company_intervals_provided(self):

        competing_company_id_1 = ObjectId()
        competing_industry_1_data = {"home_to_away": {"weight": 1.0}, "away_to_home": {"weight": 0.5}}
        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_id = self.mock.company_id
        ccph.competing_companies = {
            competing_company_id_1: self.mock.company_industry_id
        }
        ccph.competing_industries = {
            self.mock.company_industry_id: {
                "interval": [1,2],
                "data": competing_industry_1_data
            }
        }

        pair_data_from_to, pair_data_to_from, pair_interval_from_to, pair_interval_to_from = \
            ccph._get_pair_from_to_items(competing_company_id_1)

        self.assertEqual(pair_data_from_to, {"competition_strength": 1.0, "competition_type": "primary"})
        self.assertEqual(pair_data_to_from, {"competition_strength": 0.5, "competition_type": "secondary"})
        self.assertEqual(pair_interval_from_to, [1,2])
        self.assertEqual(pair_interval_to_from, [1,2])

    def test__get_pair_from_to_items__other_company_intervals_missing(self):

        competing_company_id_1 = ObjectId()
        competing_industry_1_data = {"home_to_away": {"weight": 1.0}, "away_to_home": {"weight": 0.5}}
        ccph = CompanyCompetitionPairsHelper(self.mock.context)
        ccph.company_id = self.mock.company_id
        ccph.competing_companies = {
            competing_company_id_1: self.mock.company_industry_id
        }
        ccph.competing_industries = {
            self.mock.company_industry_id: {
                "interval": None,
                "data": competing_industry_1_data
            }
        }

        pair_data_from_to, pair_data_to_from, pair_interval_from_to, pair_interval_to_from = \
            ccph._get_pair_from_to_items(competing_company_id_1)

        self.assertEqual(pair_data_from_to, {"competition_strength": 1.0, "competition_type": "primary"})
        self.assertEqual(pair_data_to_from, {"competition_strength": 0.5, "competition_type": "secondary"})
        self.assertEqual(pair_interval_from_to, [None, None])
        self.assertEqual(pair_interval_to_from, [None, None])


if __name__ == '__main__':
    unittest.main()
