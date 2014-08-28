from __future__ import division
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_industry
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from core.common.utilities.helpers import ensure_id


__author__ = "vgold"


class MainPlanBTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "main_plan_b_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):

        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def main_test_mark_as_needing_plan_b__companies(self):
        # some pycharm/unittest param that blocks you from seeing a diff failure in an assert statement if it's too long
        self.test_case.maxDiff = None

        pid1 = insert_test_company(type="retail_parent", workflow_status="published")
        bid11 = insert_test_company(type="retail_banner", workflow_status="published")
        bid12 = insert_test_company(type="retail_banner", workflow_status="published")

        pid2 = insert_test_company(type="retail_parent", workflow_status="published")
        bid21 = insert_test_company(type="retail_banner", workflow_status="published")

        bid31 = insert_test_company(type="retail_banner", workflow_status="published")

        bid41 = insert_test_company(type="retail_banner", workflow_status="new")

        oid1 = insert_test_company(type="retail_owner", workflow_status="published")
        cid1 = insert_test_company(type="retailer_cooperative", workflow_status="published")
        spid1 = insert_test_company(type="retail_parent", workflow_status="published")

        # Set up company families
        self.main_access.mds.call_add_link("company", bid11, "retail_segment", "company", pid1, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", bid12, "retail_segment", "company", pid1, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", bid21, "retail_segment", "company", pid2, "retail_parent",
                                           "retailer_branding", self.context)

        self.main_access.mds.call_add_link("company", oid1, "investment_firm", "company", pid1, "portfolio_company",
                                           "equity_investment", self.context)
        self.main_access.mds.call_add_link("company", cid1, "cooperative_parent_non_owner", "company", bid11,
                                           "cooperative_member_non_owner", "retailer_cooperatives", self.context)
        self.main_access.mds.call_add_link("company", bid11, "secondary_banner", "company", spid1, "secondary_parent",
                                           "retailer_branding", self.context)

        params = {
            "company_ids": map(str, [bid11, bid21, bid31, bid41, oid1, cid1, spid1])
        }
        self.main_access.call_needs_plan_b(params, self.context)

        query = {
            "_id": {
                "$in": map(ensure_id, [pid1, bid11, bid12, pid2, bid21, bid31, bid41, oid1, cid1, spid1])
            }
        }
        fields = ["_id", "data.workflow.analytics"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        companies = self.main_access.mds.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)
        company_dict = {
            c[0]: c
            for c in companies
        }

        # convert all entities to ObjectId because that's how find_raw returns them now...
        [pid1, bid11, bid12, pid2, bid21, bid31, bid41, oid1, cid1, spid1] = \
            map(ensure_id, [pid1, bid11, bid12, pid2, bid21, bid31, bid41, oid1, cid1, spid1])

        self.test_case.assertDictEqual(company_dict, {
            pid1: [pid1, self.__form_workflow_analytics_dict(company_dict[pid1][1]["needs_plan_b_date"])],
            bid11: [bid11, self.__form_workflow_analytics_dict(company_dict[bid11][1]["needs_plan_b_date"])],
            bid12: [bid12, self.__form_workflow_analytics_dict(company_dict[bid12][1]["needs_plan_b_date"])],
            pid2: [pid2, self.__form_workflow_analytics_dict(company_dict[pid2][1]["needs_plan_b_date"])],
            bid21: [bid21, self.__form_workflow_analytics_dict(company_dict[bid21][1]["needs_plan_b_date"])],
            bid31: [bid31, self.__form_workflow_analytics_dict(company_dict[bid31][1]["needs_plan_b_date"])],
            bid41: [bid41, None],
            oid1: [oid1, None],
            cid1: [cid1, None],
            spid1: [spid1, None]
        })

    def main_test_mark_as_needing_plan_b__industries(self):
        # some pycharm/unittest param that blocks you from seeing a diff failure in an assert statement if it's too long
        self.test_case.maxDiff = None

        pid1 = insert_test_company(type="retail_parent", workflow_status="published")
        bid11 = insert_test_company(type="retail_banner", workflow_status="published")
        bid12 = insert_test_company(type="retail_banner", workflow_status="published")

        pid2 = insert_test_company(type="retail_parent", workflow_status="published")
        bid21 = insert_test_company(type="retail_banner", workflow_status="published")

        bid31 = insert_test_company(type="retail_banner", workflow_status="published")

        bid41 = insert_test_company(type="retail_banner", workflow_status="new")

        oid1 = insert_test_company(type="retail_owner", workflow_status="published")
        cid1 = insert_test_company(type="retailer_cooperative", workflow_status="published")
        spid1 = insert_test_company(type="retail_parent", workflow_status="published")

        # Set up company families
        self.main_access.mds.call_add_link("company", bid11, "retail_segment", "company", pid1, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", bid12, "retail_segment", "company", pid1, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", bid21, "retail_segment", "company", pid2, "retail_parent",
                                           "retailer_branding", self.context)

        self.main_access.mds.call_add_link("company", oid1, "investment_firm", "company", pid1, "portfolio_company",
                                           "equity_investment", self.context)
        self.main_access.mds.call_add_link("company", cid1, "cooperative_parent_non_owner", "company", bid11,
                                           "cooperative_member_non_owner", "retailer_cooperatives", self.context)
        self.main_access.mds.call_add_link("company", bid11, "secondary_banner", "company", spid1, "secondary_parent",
                                           "retailer_branding", self.context)

        industry_id1 = insert_test_industry("Industry 1")

        self.main_access.mds.call_add_link("company", bid12, "primary_industry_classification", "industry",
                                           industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", bid21, "primary_industry_classification", "industry",
                                           industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", bid31, "primary_industry_classification", "industry",
                                           industry_id1, "primary_industry", "industry_classification", self.context)

        params = {
            "industry_ids": map(str, [industry_id1])
        }
        self.main_access.call_needs_plan_b(params, self.context)

        query = {
            "_id": {
                "$in": map(ensure_id, [pid1, bid11, bid12, pid2, bid21, bid31, bid41, oid1, cid1, spid1])
            }
        }
        fields = ["_id", "data.workflow.analytics"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        companies = self.main_access.mds.call_find_entities_raw("company", params, self.context, encode_and_decode_results=False)
        company_dict = {
            c[0]: c
            for c in companies
        }

        # convert all entities to ObjectId because that's how find_raw returns them now...
        [pid1, bid11, bid12, pid2, bid21, bid31, bid41, oid1, cid1, spid1] = \
            map(ensure_id, [pid1, bid11, bid12, pid2, bid21, bid31, bid41, oid1, cid1, spid1])

        self.test_case.assertDictEqual(company_dict, {
            pid1: [pid1, self.__form_workflow_analytics_dict(company_dict[pid1][1]["needs_plan_b_date"])],
            bid11: [bid11, self.__form_workflow_analytics_dict(company_dict[bid11][1]["needs_plan_b_date"])],
            bid12: [bid12, self.__form_workflow_analytics_dict(company_dict[bid12][1]["needs_plan_b_date"])],
            pid2: [pid2, self.__form_workflow_analytics_dict(company_dict[pid2][1]["needs_plan_b_date"])],
            bid21: [bid21, self.__form_workflow_analytics_dict(company_dict[bid21][1]["needs_plan_b_date"])],
            bid31: [bid31, self.__form_workflow_analytics_dict(company_dict[bid31][1]["needs_plan_b_date"])],
            bid41: [bid41, None],
            oid1: [oid1, None],
            cid1: [cid1, None],
            spid1: [spid1, None]
        })

    def __form_workflow_analytics_dict(self, needs_plan_b_date):

        return {
            "status": "needs_plan_b",
            "needs_plan_b_date": needs_plan_b_date,
            "run_id": None,
            "creation_time": None,
            "start_time": None,
            "end_time": None,
            "exception": None,
            "duration": None
        }


###################################################################################################
