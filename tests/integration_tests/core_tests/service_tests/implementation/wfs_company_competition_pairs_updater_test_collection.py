from common.utilities.inversion_of_control import Dependency
from core.common.business_logic.service_entity_logic.analytics_helper import PRIMARY_COMPETITOR_WEIGHT_THRESHOLD
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_industry
from bson.objectid import ObjectId


__author__ = 'vgold'


class WFSCompanyCompetitionInstanceUpdaterTestCollection(ServiceTestCollection):

    def initialize(self):

        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            'user_id': ObjectId(),
            'source': 'wfs_company_competition_pairs_updater_test_collection.py'
        }

    def setUp(self):

        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def test_company_competition_pairs_updater__create(self):
        self._insert_test_companies_and_industries()
        self._run_company_pairs_updater_task()

        # Check task results
        task_result = self.wfs_access.call_get_task_id(self.task["_id"])
        self.test_case.assertEqual(len(task_result["output"]["created_pairs_to_ids"]), 3)
        self.test_case.assertEqual(task_result["output"]["num_created_pairs"], 3)
        self.test_case.assertEqual(task_result["output"]["deleted_pairs"], {})
        for cid in self.cids:
            self.test_case.assertIn(cid, task_result["output"]["created_pairs_to_ids"])

        ccis = self._get_ccis()

        # expected results defs:
        cci_expected_results = [{
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[0],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[0],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 1.0,
                    "competition_type": "cluster"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            }
        },
        {
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[1],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[0],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 0.9,
                    "competition_type": "primary"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK2"
                },
                "name": "Company 2"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            }
        },
        {
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[0],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[1],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 0.9,
                    "competition_type": "primary"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK2"
                },
                "name": "Company 2"
            }
        },
        {
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[2],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[0],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 0.5,
                    "competition_type": "secondary"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK3"
                },
                "name": "Company 3"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            }
        },
        {
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[0],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[2],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 0.5,
                    "competition_type": "secondary"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK3"
                },
                "name": "Company 3"
            }
        }]

        # Make sure IDs in task output rec and find results match up
        self.test_case.assertEqual(len(ccis), 5)
        for cci in ccis:
            del cci[1]["sync"]
            del cci[1]["to_links"]  # tested in pair_entity_test_collection.py
            del cci[1]["from_links"]  # tested in pair_entity_test_collection.py
            self.test_case.assertIn(cci[1], cci_expected_results)


    def test_company_competition_pairs_updater__create_twice_no_dupes(self):
        self._insert_test_companies_and_industries()
        self._run_company_pairs_updater_task()

        # run it twice!
        self._run_company_pairs_updater_task()

        # Check task results
        task_result = self.wfs_access.call_get_task_id(self.task["_id"])
        self.test_case.assertEqual(len(task_result["output"]["created_pairs_to_ids"]), 0)
        self.test_case.assertEqual(task_result["output"]["num_created_pairs"], 0)
        self.test_case.assertEqual(task_result["output"]["deleted_pairs"], {})

        ccis = self._get_ccis()

        # expected results defs:
        cci_expected_results = [{
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[0],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[0],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 1.0,
                    "competition_type": "cluster"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            }
        },
        {
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[1],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[0],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 0.9,
                    "competition_type": "primary"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK2"
                },
                "name": "Company 2"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            }
        },
        {
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[0],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[1],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 0.9,
                    "competition_type": "primary"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK2"
                },
                "name": "Company 2"
            }
        },
        {
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[2],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[0],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 0.5,
                    "competition_type": "secondary"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK3"
                },
                "name": "Company 3"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            }
        },
        {
            "pair": {
                "entity_type_from": "company",
                "entity_id_to": self.cids[0],
                "interval": [None, None],
                "entity_type_to": "company",
                "entity_role_from": "competitor",
                "entity_id_from": self.cids[2],
                "relation_type": "company_competition",
                "data": {
                    "competition_strength": 0.5,
                    "competition_type": "secondary"
                },
                "entity_role_to": "competitor"
            },
            "to": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK1"
                },
                "name": "Company 1"
            },
            "from": {
                "interval": None,
                "data": {
                    "status": "operating",
                    "type": "retail_banner",
                    "ticker": "TICK3"
                },
                "name": "Company 3"
            }
        }]

        # Make sure IDs in task output rec and find results match up
        self.test_case.assertEqual(len(ccis), 5)
        for cci in ccis:
            del cci[1]["sync"]
            del cci[1]["to_links"]  # tested in pair_entity_test_collection.py
            del cci[1]["from_links"]  # tested in pair_entity_test_collection.py
            self.test_case.assertIn(cci[1], cci_expected_results)

    def test_company_competition_pairs_updater__delete(self):
        self._insert_test_companies_and_industries()
        self._run_company_pairs_updater_task()

        # delete industry competition between industry 1 and 3
        self.mds_access.call_del_link_without_id("industry", self.ind1, "competitor",
                                                 "industry", self.ind3, "competitor", "industry_competition")

        # run task again, should have a deleted pair
        self._run_company_pairs_updater_task()

        # Check task results
        task_result = self.wfs_access.call_get_task_id(self.task["_id"])
        self.test_case.assertEqual(task_result["output"]["created_pairs_to_ids"], [])
        pairs_to_delete_from_to_ids = task_result["output"]["deleted_pairs"]["pairs_to_delete_from_ids"] + \
                                      task_result["output"]["deleted_pairs"]["pairs_to_delete_to_ids"]
        self.test_case.assertIn(self.cids[0], pairs_to_delete_from_to_ids)
        self.test_case.assertIn(self.cids[2], pairs_to_delete_from_to_ids)
        self.test_case.assertEqual(len(pairs_to_delete_from_to_ids), 2)
        self.test_case.assertEqual(task_result["output"]["num_created_pairs"], 0)

        ccis = self._get_ccis()
        self.test_case.assertEqual(len(ccis), 3)
        expected_names = ["From Company 1 To Company 1", "From Company 1 To Company 2", "From Company 2 To Company 1"]
        names = [cci[2] for cci in ccis]
        for name in expected_names:
            self.test_case.assertIn(name, names)


    def test_company_competition_pairs_updater__change_industry(self):
        self._insert_test_companies_and_industries()
        self._run_company_pairs_updater_task()

        # delete industry competition between industry 1 and 3
        self.mds_access.call_del_link_without_id("company", self.cids[0], "primary_industry_classification",
                                                 "industry", self.ind1, "primary_industry", "industry_classification")
        self.mds_access.call_add_link("company", self.cids[0], "primary_industry_classification",
                                      "industry", self.ind2, "primary_industry", "industry_classification", self.context)
        # run task again
        self._run_company_pairs_updater_task()

        # Check task results
        task_result = self.wfs_access.call_get_task_id(self.task["_id"])

        # should have recreated all pairs again, from self.cids[0]
        self.test_case.assertEqual(len(task_result["output"]["created_pairs_to_ids"]), 3)
        self.test_case.assertIn(self.cids[0], task_result["output"]["created_pairs_to_ids"])
        self.test_case.assertIn(self.cids[1], task_result["output"]["created_pairs_to_ids"])
        self.test_case.assertIn(self.cids[2], task_result["output"]["created_pairs_to_ids"])
        self.test_case.assertEqual(task_result["output"]["num_created_pairs"], 3)

        # should have deleted all pairs, from self.cids[0]
        self.test_case.assertEqual(len(task_result["output"]["deleted_pairs"]["pairs_to_delete_to_ids"]), 3)
        self.test_case.assertIn(self.cids[0], task_result["output"]["deleted_pairs"]["pairs_to_delete_to_ids"])
        self.test_case.assertIn(self.cids[1], task_result["output"]["deleted_pairs"]["pairs_to_delete_to_ids"])
        self.test_case.assertIn(self.cids[2], task_result["output"]["deleted_pairs"]["pairs_to_delete_to_ids"])
        self.test_case.assertEqual(len(task_result["output"]["deleted_pairs"]["pairs_to_delete_from_ids"]), 1)
        self.test_case.assertIn(self.cids[0], task_result["output"]["deleted_pairs"]["pairs_to_delete_from_ids"])

        # make sure the industries are correct
        ccis = self._get_ccis()
        self.test_case.assertEqual(len(ccis), 5)
        expected_names = ["From Company 1 To Company 1", "From Company 1 To Company 2", "From Company 2 To Company 1",
                          "From Company 1 To Company 3", "From Company 3 To Company 1"]
        names = [cci[2] for cci in ccis]
        expected_industries = {
            "From Company 1 To Company 1": [self.ind2, self.ind2],
            "From Company 1 To Company 2": [self.ind2, self.ind2],
            "From Company 1 To Company 3": [self.ind2, self.ind3],
            "From Company 2 To Company 1": [self.ind2, self.ind2],
            "From Company 3 To Company 1": [self.ind3, self.ind2]
        }
        for name in expected_names:
            self.test_case.assertIn(name, names)
        for cci in ccis:
            from_industry_id, to_industry_id = self._get_industry_ids_from_to(cci[1])
            self.test_case.assertEqual([from_industry_id, to_industry_id], expected_industries[cci[2]])

    def test_company_competition_pairs_updater__change_industry_competition_weights(self):
        self._insert_test_companies_and_industries()
        self._run_company_pairs_updater_task()

        # change ind1 -> ind3 from weight .5 to weight 2.0, changing it from secondary to primary
        self.mds_access.call_del_link_without_id("industry", self.ind1, "competitor",
                                                 "industry", self.ind3, "competitor", "industry_competition")
        self.comp_links.append(self.mds_access.call_add_link("industry", self.ind1, "competitor", "industry",
                                                        self.ind3, "competitor", "industry_competition", self.context,
                                                        link_data={"home_to_away":{"weight": 2.0}, "away_to_home": {"weight": 2.0}}))

        # run again to fix it
        self._run_company_pairs_updater_task()

        # make sure the task output looks right
        task_result = self.wfs_access.call_get_task_id(self.task["_id"])
        expected_updated_pairs = [
            {
                "competitor_id": str(self.cids[2]),
                "competition_type": "primary",
                "competition_strength": 2.0
            }
        ]
        self.test_case.assertEqual(task_result["output"]["updated_pairs"], expected_updated_pairs)

        # make sure the tasks says it didn't do anything else
        self.test_case.assertEqual(task_result["output"]["created_pairs_to_ids"], [])
        self.test_case.assertEqual(task_result["output"]["deleted_pairs"], {})

        # make sure the ccis are correct
        ccis = self._get_ccis()
        self.test_case.assertEqual(len(ccis), 5)
        for cci in ccis:
            from_industry_id, to_industry_id = self._get_industry_ids_from_to(cci[1])
            from_company_id, to_company_id = self._get_company_ids_from_to(cci[1])

            # We messed with industry 1 <--> 3 weights, so make sure those were changed.
            # Note, company_competition_pairs helper DOES NOT automatically adjust CCI weights in the opposite direction
            # The reason is because the Competition page dynamically queries CCIs. So if we change those opposite CCIs
            # without running analytics, the summary boxes and the main grid on the competition tab won't match.
            if from_industry_id == self.ind1 and to_industry_id == self.ind3:
                expected_weight, expected_type = 2.0, "primary"
            else:
                expected_weight = self.comp_weights[from_industry_id][to_industry_id]
                expected_type = self._get_competition_type(expected_weight, from_company_id, to_company_id)
            expected_pair_data = {
                "competition_strength": expected_weight,
                "competition_type": expected_type
            }
            self.test_case.assertEqual(cci[1]["pair"]["data"], expected_pair_data)


    def _get_company_ids_from_to(self, data):
        from_id = data["pair"]["entity_id_from"]
        to_id = data["pair"]["entity_id_to"]
        return from_id, to_id


    def _get_industry_ids_from_to(self, data):
        from_industry_id = data["from_links"]["industry"]["industry_classification"][0]["entity_id_to"]
        to_industry_id = data["to_links"]["industry"]["industry_classification"][0]["entity_id_to"]
        return from_industry_id, to_industry_id


    def _insert_test_companies_and_industries(self):
        # Create industries
        ind_data_1 = {
            "source_vendor": "NAICS",
            "industry_code": "111111",
            "industry_name": "Industry 1"
        }
        ind_data_2 = {
            "source_vendor": "NAICS",
            "industry_code": "222222",
            "industry_name": "Industry 2"
        }
        ind_data_3 = {
            "source_vendor": "NAICS",
            "industry_code": "333333",
            "industry_name": "Industry 3"
        }
        self.ind1 = insert_test_industry(data=ind_data_1)
        self.ind2 = insert_test_industry(data=ind_data_2)
        self.ind3 = insert_test_industry(data=ind_data_3)

        # Create companies
        self.cids = [
            insert_test_company(ticker="TICK1", name="Company 1", type="retail_banner", status="operating"),
            insert_test_company(ticker="TICK2", name="Company 2", type="retail_banner", status="operating"),
            insert_test_company(ticker="TICK3", name="Company 3", type="retail_banner", status="operating")
        ]

        # Create industry links
        self.mds_access.call_add_link("company", self.cids[0], "primary_industry_classification",
                                      "industry", self.ind1, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", self.cids[1], "primary_industry_classification",
                                      "industry", self.ind2, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", self.cids[2], "primary_industry_classification",
                                      "industry", self.ind3, "primary_industry", "industry_classification", self.context)

        # Create industry competition links
        self.comp_weights = {self.ind1:{}, self.ind2:{}, self.ind3:{}}

        # 1 <--> 2 == .9
        self.comp_weights[self.ind1][self.ind2] = .9
        self.comp_weights[self.ind2][self.ind1] = .9

        # 1 <--> 3 == .5
        self.comp_weights[self.ind1][self.ind3] = .5
        self.comp_weights[self.ind3][self.ind1] = .5

        # 2 <--> 3 == .8
        self.comp_weights[self.ind2][self.ind3] = .8
        self.comp_weights[self.ind3][self.ind2] = .8

        # industry to industry is always 1.0
        self.comp_weights[self.ind1][self.ind1] = 1.0
        self.comp_weights[self.ind2][self.ind2] = 1.0
        self.comp_weights[self.ind3][self.ind3] = 1.0

        self.comp_link_data = {self.ind1:{}, self.ind2:{}}
        self.comp_link_data[self.ind1][self.ind2] = {"home_to_away": {"weight": self.comp_weights[self.ind1][self.ind2]},
                                                     "away_to_home": {"weight": self.comp_weights[self.ind2][self.ind1]}}

        self.comp_link_data[self.ind2][self.ind3] = {"home_to_away": {"weight": self.comp_weights[self.ind2][self.ind3]},
                                                     "away_to_home": {"weight": self.comp_weights[self.ind3][self.ind2]}}

        self.comp_link_data[self.ind1][self.ind3] = {"home_to_away": {"weight": self.comp_weights[self.ind1][self.ind3]},
                                                     "away_to_home": {"weight": self.comp_weights[self.ind3][self.ind1]}}

        self.comp_links = []
        self.comp_links.append(self.mds_access.call_add_link("industry", self.ind1, "competitor", "industry",
                                                        self.ind2, "competitor", "industry_competition", self.context,
                                                        link_data=self.comp_link_data[self.ind1][self.ind2]))
        self.comp_links.append(self.mds_access.call_add_link("industry", self.ind2, "competitor", "industry",
                                                        self.ind3, "competitor", "industry_competition", self.context,
                                                        link_data=self.comp_link_data[self.ind1][self.ind2]))
        self.comp_links.append(self.mds_access.call_add_link("industry", self.ind1, "competitor", "industry",
                                                        self.ind3, "competitor", "industry_competition", self.context,
                                                        link_data=self.comp_link_data[self.ind1][self.ind3]))


    def _run_company_pairs_updater_task(self):
        # Form task record
        task_rec = {
            "input": {
                "company_id": self.cids[0]
            },
            "meta": {
                "async": False
            }
        }

        # Run task first time
        self.task = self.wfs_access.call_task_new("entity_updated", "company", "update_company_competition_pairs",
                                                  task_rec, self.context)

    def _get_ccis(self):
        params = self.main_params.mds.create_params(resource="find_entities_raw", entity_fields=["_id", "data", "name"],
                                                    sort=[["data.pair.entity_id_from",1],["data.pair.entity_id_to",1]],
                                                    as_list=True)["params"]
        return self.mds_access.call_find_entities_raw("company_competition_instance", params, self.context)

    def _get_competition_type(self, weight, from_id, to_id):
        if str(from_id) == str(to_id):
            return "cluster"
        elif float(weight) >= PRIMARY_COMPETITOR_WEIGHT_THRESHOLD:
            return "primary"
        else:
            return "secondary"