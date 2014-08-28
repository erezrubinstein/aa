from common.utilities.inversion_of_control import Dependency
from core.common.utilities.helpers import ensure_id
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_industry
import pprint


__author__ = 'vgold'


class PairEntityTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "mds_pair_entity_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # create params builder
        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    #-----------------------------# Tests #-----------------------------#

    def pair_entity_create_delete(self):
        pair_id_dict_lists = []
        result = self.__insert_ccis()
        pair_id_dict_lists.append(result)

        # Validate structure of pair entities
        results = self.__get_all_ccis()
        self.test_case.assertEqual(len(results), 7)

        for result in results:
            if result[3]["pair"]["entity_id_from"] == self.cids[0] and result[3]["pair"]["entity_id_to"] == self.cids[0]:
                self.test_case.assertEqual(result[3]["from_links"]["industry"]["industry_classification"][0]["entity"]["name"], "Industry 0")
                self.test_case.assertEqual(result[3]["from_links"]["company"]["retailer_branding"][0]["entity"]["name"], "Parent 0")

        # Delete one set of pair entities
        self.mds_access.call_delete_pair_entities("company", self.cids[0], "competitor", "company", self.cids[3],
                                                  "competitor", "company_competition")

        # Make sure both from the pair were deleted
        results = self.__get_all_ccis()
        self.test_case.assertEqual(len(results), 5)


    def pair_entity_delete_batch_raw__entity_ids(self):
        self.__insert_ccis()
        pairs_to_delete = {
            "pairs_to_delete_from_ids": [self.cids[0]],
            "pairs_to_delete_to_ids": [self.cids[2], self.cids[3]]
        }
        self.mds_access.call_delete_pair_entities_batch_raw("company", "company", "company_competition",
                                                            "competitor", "competitor", pairs_to_delete, self.context)
        results = self.__get_all_ccis()
        self.test_case.assertEqual(len(results), 3)
        cci_names = [cci[1] for cci in results]
        self.test_case.assertIn("From Company 0 To Company 0", cci_names)
        self.test_case.assertIn("From Company 0 To Company 1", cci_names)
        self.test_case.assertIn("From Company 1 To Company 0", cci_names)


    def pair_entity_delete_batch_raw__links_industry_ids(self):
        self.__insert_ccis()
        pairs_to_delete = {
            "from_links": {"industry.industry_classification.entity_id_to": [self.inds[0]]},
            "to_links": {"industry.industry_classification.entity_id_to": [self.inds[2], self.inds[3]]}
        }
        self.mds_access.call_delete_pair_entities_batch_raw("company", "company", "company_competition",
                                                            "competitor", "competitor", pairs_to_delete, self.context)
        results = self.__get_all_ccis()
        self.test_case.assertEqual(len(results), 3)
        cci_names = [cci[1] for cci in results]
        self.test_case.assertIn("From Company 0 To Company 0", cci_names)
        self.test_case.assertIn("From Company 0 To Company 1", cci_names)
        self.test_case.assertIn("From Company 1 To Company 0", cci_names)


    def pair_entity_synchronize(self):

        ind_data = {
            "source_vendor": "TEST",
            "source_version": 2013,
            "industry_code": "1111",
            "industry_name": "HELO"
        }

        ind_id = insert_test_industry(name="Industry", data=dict(ind_data, industry_name="Industry"))
        parent_id = insert_test_company(ticker="P", name="Parent", type="retail_parent", status="operating")
        cid = ensure_id(insert_test_company(ticker="TICK", name="Company", type="retail_banner", status="operating"))

        self.mds_access.call_add_link("company", parent_id, "retail_parent", "company", cid, "retail_segment",
                                      "retailer_branding", self.context)
        self.mds_access.call_add_link("industry", ind_id, "primary_industry", "company", cid, "primary_industry_classification",
                                      "industry_classification", self.context)

        entity_pairs = [
            {
                'pair_interval_from_to': [None, None],
                'pair_interval_to_from': [None, None],
                'to_id': cid,
                'pair_data_to_from': {"competition_strength": 1.0},
                'pair_data_from_to': {"competition_strength": 1.0},
                'from_id': cid
            }
        ]

        self.mds_access.call_create_pair_entities(entity_pairs, "company", "competitor", "company",
                                                  "competitor", "company_competition", self.context)

        # Validate structure of pair entity
        results = self.__get_all_ccis()

        self.test_case.assertEqual(results[0][3]["from_links"]["company"]["retailer_branding"][0]["entity"]["name"], "Parent")

        # Update entities
        self.mds_access.call_update_entity("company", cid, self.context, field_data={"data.ticker": "NEWTICK"})
        self.mds_access.call_update_entity("industry", ind_id, self.context, field_data={"data.source_vendor": "NEW"})
        self.mds_access.call_update_entity("company", parent_id, self.context, field_data={"name": "New Name"})

        # Syncing parent should only update parent data in link of cci
        self.__run_pair_syncer("company", parent_id)
        results = self.__get_all_ccis()

        self.test_case.assertEqual(results[0][3]["from_links"]["company"]["retailer_branding"][0]["entity"]["name"], "New Name")
        self.test_case.assertEqual(results[0][3]["to_links"]["company"]["retailer_branding"][0]["entity"]["name"], "New Name")
        self.test_case.assertEqual(results[0][3]["from_links"]["industry"]["industry_classification"][0]["entity"]["data"]["source_vendor"], "TEST")
        self.test_case.assertEqual(results[0][3]["to_links"]["industry"]["industry_classification"][0]["entity"]["data"]["source_vendor"], "TEST")

        # Syncing company should update data and all links
        self.__run_pair_syncer("company", cid)
        results = self.__get_all_ccis()

        self.test_case.assertEqual(results[0][3]["from"]["data"]["ticker"], "NEWTICK")
        self.test_case.assertEqual(results[0][3]["to"]["data"]["ticker"], "NEWTICK")
        self.test_case.assertEqual(results[0][3]["from_links"]["industry"]["industry_classification"][0]["entity"]["data"]["source_vendor"], "NEW")
        self.test_case.assertEqual(results[0][3]["to_links"]["industry"]["industry_classification"][0]["entity"]["data"]["source_vendor"], "NEW")

        # Delete company retailer branding link and make sure link to parent goes away
        self.main_access.mds.call_del_link_without_id("company", cid, "retail_segment", "company", parent_id, "retail_parent", "retailer_branding")

        # Syncing company should remove invalid links
        self.__run_pair_syncer("company", cid)
        results = self.__get_all_ccis()

        self.test_case.assertEqual(results[0][3]["from_links"]["company"]["retailer_branding"], [])
        self.test_case.assertEqual(results[0][3]["to_links"]["company"]["retailer_branding"], [])

    #----------------------------# Private Helpers #----------------------------#

    def __insert_ccis(self):
        ind_data = {
            "source_vendor": "TEST",
            "source_version": 2013,
            "industry_code": "1111",
            "industry_name": "HELO"
        }

        self.inds = [
            insert_test_industry(name="Industry %s" % i, data=dict(ind_data, industry_name="Industry %s" % i))
            for i in range(4)
        ]

        parents = [
            insert_test_company(ticker="P%s" % i, name="Parent %s" % i, type="retail_parent", status="operating")
            for i in range(4)
        ]

        # Create companies
        self.cids = [
            ensure_id(insert_test_company(ticker="TICK%s" % i, name="Company %s" % i, type="retail_banner", status="operating"))
            for i in range(4)
        ]

        for i in range(4):
            self.mds_access.call_add_link("company", parents[i], "retail_parent", "company", self.cids[i],
                                          "retail_segment", "retailer_branding", self.context)
            self.mds_access.call_add_link("industry", self.inds[i], "primary_industry", "company", self.cids[i],
                                          "primary_industry_classification", "industry_classification", self.context)

        entity_pairs = [{
            'pair_interval_from_to': [None, None],
            'pair_interval_to_from': [None, None],
            'to_id': self.cids[0],
            'pair_data_to_from': {"competition_strength": 1.0},
            'pair_data_from_to': {"competition_strength": 1.0},
            'from_id': self.cids[0]
        }]

        for i, cid in enumerate(self.cids[1:]):
            entity_pairs.append({
                'pair_interval_from_to': [None, None],
                'pair_interval_to_from': [None, None],
                'to_id': cid,
                'pair_data_to_from': {"competition_strength": round(0.5 - i * 0.2, 1)},
                'pair_data_from_to': {"competition_strength": round(0.5 + i * 0.2, 1)},
                'from_id': self.cids[0]
            })

        return self.mds_access.call_create_pair_entities(entity_pairs, "company", "competitor", "company",
                                                           "competitor", "company_competition", self.context)

    def __get_all_ccis(self):

        fields = ["_id", "name", "interval", "data"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=fields, as_list=True)["params"]
        return self.mds_access.call_find_entities_raw("company_competition_instance", params, self.context)

    def __run_pair_syncer(self, entity_type, entity_id):

        task_rec = {
            "input": {
                "entity_type": entity_type,
                "entity_id": entity_id
            },
            "meta": {
                "async": False
            }
        }

        self.wfs_access.call_task_new("entity_updated", "pair_entity", "sync_pair_entities", task_rec, self.context)