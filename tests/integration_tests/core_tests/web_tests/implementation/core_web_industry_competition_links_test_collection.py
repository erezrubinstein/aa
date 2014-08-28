from __future__ import division
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_industry
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from core.common.utilities.helpers import ensure_id
import string
import random


__author__ = 'vgold'


class CoreWebIndustryCompetitionLinksTestCollection(ServiceTestCollection):

    def initialize(self):

        self.main_param = Dependency("CoreAPIParamsBuilder").value

        self.user_id = 'test@nexusri.com'
        self.source = "core_web_industry_competition_links_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------ User Admin Tests ---------------------------------------##

    def web_test_create_delete_industry_competition_links(self):

        iid1 = insert_test_industry(name="Ind 1")
        iid2 = insert_test_industry(name="Ind 2")

        link_data = {
            'home_to_away': {
                "weight": 0.7
            },
            'away_to_home': {
                "weight": 0.7
            }
        }

        links = self.mds_access.call_add_link("industry", iid1, "competitor", "industry", iid2,
                                              "competitor", "industry_competition", self.context,
                                              link_data=link_data)

        self.test_case.assertEqual(links[0]["_id"], links[1]["_id"])

        query = {"_id": {"$in": [ensure_id(iid1), ensure_id(iid2)]}}
        fields = ["_id", "links.industry.industry_competition"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        results = self.mds_access.call_find_entities_raw("industry", params, self.context)

        link_id = results[0][1][0]["_id"]
        ind2_link_ids = [
            link["_id"]
            for link in results[1][1]
        ]

        self.test_case.assertIn(link_id, ind2_link_ids)

        self.mds_access.call_del_link_by_id_fo_ril("industry", iid1, "industry", iid2, links[0]["_id"])

        query = {"_id": {"$in": [ensure_id(iid1), ensure_id(iid2)]}}
        fields = ["_id", "links.industry.industry_competition"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        results = self.mds_access.call_find_entities_raw("industry", params, self.context)

        self.test_case.assertEqual(results[0][1], [])
        self.test_case.assertEqual(results[1][1], [])
