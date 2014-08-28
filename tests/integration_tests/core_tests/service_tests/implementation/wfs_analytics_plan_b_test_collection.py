from __future__ import division
from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.company_analytics_plan_b_runner import CompanyAnalyticsPlanBRunner
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from bson.objectid import ObjectId
import datetime
import uuid


__author__ = "vgold"


class WFSAnalyticsPlanBTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "wfs_analytics_plan_b_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # some pycharm/unittest param that blocks you from seeing a diff failure in an assert statement if it's too long
        self.maxDiff = None
        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):

        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def wfs_test_company_analytics_plan_b_runner(self):

        now = datetime.datetime.utcnow()
        five_hours_ago = now - datetime.timedelta(hours=5)
        nineteen_hours_ago = now - datetime.timedelta(hours=19)

        def seconds_ago(date, seconds):
            return date - datetime.timedelta(seconds=seconds)

        # Create 4 company families that need plan b
        needs_plan_b_workflow = self.__make_plan_b_workflow("needs_plan_b", needs_plan_b_date=seconds_ago(now, 50))
        pid1 = insert_test_company(type="retail_parent", workflow=needs_plan_b_workflow)
        cid11 = insert_test_company(type="retail_banner", workflow=needs_plan_b_workflow)
        cid12 = insert_test_company(type="retail_banner", workflow=needs_plan_b_workflow)

        # Setting dates specifically for predictable results
        cid31 = insert_test_company(type="retail_banner", workflow=self.__make_plan_b_workflow("needs_plan_b", needs_plan_b_date=seconds_ago(now, 40)))
        cid41 = insert_test_company(type="retail_banner", workflow=self.__make_plan_b_workflow("needs_plan_b", needs_plan_b_date=seconds_ago(now, 30)))
        cid51 = insert_test_company(type="retail_banner", workflow=self.__make_plan_b_workflow("needs_plan_b", needs_plan_b_date=seconds_ago(now, 20)))

        # Create 1 company family that is pending and expired
        run_id = str(uuid.uuid4())
        pending_expired_plan_b_workflow = self.__make_plan_b_workflow("pending", needs_plan_b_date=five_hours_ago, creation_time=five_hours_ago, run_id=run_id)
        pid2 = insert_test_company(type="retail_parent", workflow=pending_expired_plan_b_workflow)
        cid21 = insert_test_company(type="retail_banner", workflow=pending_expired_plan_b_workflow)

        # Create 1 company family that is in_progress and expired
        run_id = str(uuid.uuid4())
        in_progress_expired_plan_b_workflow = self.__make_plan_b_workflow("in_progress", needs_plan_b_date=nineteen_hours_ago, creation_time=nineteen_hours_ago, run_id=run_id)
        pid8 = insert_test_company(type="retail_parent", workflow=in_progress_expired_plan_b_workflow)
        cid81 = insert_test_company(type="retail_banner", workflow=in_progress_expired_plan_b_workflow)

        # Create a company family that is pending -- no parent here
        cid61 = insert_test_company(type="retail_banner", workflow=self.__make_plan_b_workflow("pending"))

        # Create a company family that is in_progress, with two banners and one parent in the family
        run_id = "redlight-redlight-runit"
        pid7 = insert_test_company(type="retail_parent", workflow=self.__make_plan_b_workflow("in_progress", run_id=run_id))
        cid71 = insert_test_company(type="retail_banner", workflow=self.__make_plan_b_workflow("in_progress", run_id=run_id))
        cid72 = insert_test_company(type="retail_banner", workflow=self.__make_plan_b_workflow("in_progress", run_id=run_id))

        # Set up company families
        self.main_access.mds.call_add_link("company", cid11, "retail_segment", "company", pid1, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", cid12, "retail_segment", "company", pid1, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", cid21, "retail_segment", "company", pid2, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", cid81, "retail_segment", "company", pid8, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", cid71, "retail_segment", "company", pid7, "retail_parent",
                                           "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", cid72, "retail_segment", "company", pid7, "retail_parent",
                                           "retailer_branding", self.context)

        runner = CompanyAnalyticsPlanBRunner({
            "async": False,
            "start_plan_b_tasks": False,
            "max_simultaneous_plan_bs": 6,
            "context": self.context
        })
        results = runner.run()

        self.test_case.assertDictEqual(results, {
            "pending_company_ids_reverted": results["pending_company_ids_reverted"],
            "in_progress_company_ids_reverted": results["in_progress_company_ids_reverted"],
            "num_tasks_created": 4,
            "max_simultaneous_plan_bs_running": False
        })

        self.test_case.assertItemsEqual(results["pending_company_ids_reverted"], [pid2, cid21])
        self.test_case.assertItemsEqual(results["in_progress_company_ids_reverted"], [pid8, cid81])

        query = {
            "_id": {
                "$in": map(ObjectId, [pid1, cid11, cid12, cid31, cid41, cid51, pid2, cid21, cid61, cid71, pid8, cid81])
            }
        }
        fields = [
            "_id",
            "data.workflow.analytics.run_id",
            "data.workflow.analytics.status",
            "data.workflow.analytics.creation_time"
        ]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        companies = self.main_access.mds.call_find_entities_raw("company", params, self.context)
        company_dict = {
            str(c[0]): c
            for c in companies
        }

        self.test_case.assertDictEqual(company_dict, {
            str(pid1): [str(pid1), company_dict[str(pid1)][1], "pending", company_dict[str(pid1)][3]],
            str(cid11): [str(cid11), company_dict[str(cid11)][1], "pending", company_dict[str(cid11)][3]],
            str(cid12): [str(cid12), company_dict[str(cid12)][1], "pending", company_dict[str(cid12)][3]],
            str(pid2): [str(pid2), company_dict[str(pid2)][1], "pending", company_dict[str(pid2)][3]],
            str(cid21): [str(cid21), company_dict[str(cid21)][1], "pending", company_dict[str(cid21)][3]],
            str(cid31): [str(cid31), company_dict[str(cid31)][1], "pending", company_dict[str(cid31)][3]],
            str(cid41): [str(cid41), None, "needs_plan_b", None],
            str(cid51): [str(cid51), None, "needs_plan_b", None],
            str(cid61): [str(cid61), company_dict[str(cid61)][1], "pending", company_dict[str(cid61)][3]],
            str(cid71): [str(cid71), company_dict[str(cid71)][1], "in_progress", company_dict[str(cid71)][3]],
            str(pid8): [str(pid8), company_dict[str(pid8)][1], "pending", company_dict[str(pid8)][3]],
            str(cid81): [str(cid81), company_dict[str(cid81)][1], "pending", company_dict[str(cid81)][3]],
        })

        self.test_case.assertEqual(company_dict[str(pid1)][1], company_dict[str(cid11)][1], company_dict[str(cid12)][1])
        self.test_case.assertEqual(company_dict[str(pid2)][1], company_dict[str(cid21)][1])

        params = {
            "query": {
                "flow": "retail_analytics",
                "process": "analytics",
                "stage": "company_analytics_plan_b"
            },
            "fields": ["_id", "input.company_id"]
        }
        tasks = self.wfs_access.call_find_tasks(params, self.context)["rows"]

        task_company_ids = [
            t["input"]["company_id"]
            for t in tasks
        ]
        expected_company_ids = map(str, [pid1, pid2, cid31, pid8])
        self.test_case.assertItemsEqual(task_company_ids, expected_company_ids)

    def __make_plan_b_workflow(self, status, needs_plan_b_date=None, creation_time=None, start_time=None, run_id=None):

        data = {
            "analytics": {
                "status": status
            }
        }

        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

        if status in ["needs_plan_b", "pending", "in_progress"]:
            data["analytics"]["needs_plan_b_date"] = needs_plan_b_date.strftime("%Y-%m-%dT%H:%M:%S") if needs_plan_b_date else now
        if status in ["pending", "in_progress"]:
            data["analytics"]["creation_time"] = creation_time.strftime("%Y-%m-%dT%H:%M:%S") if creation_time else now
            data["analytics"]["run_id"] = run_id if run_id else str(uuid.uuid4())
        if status == "in_progress":
            data["analytics"]["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%S") if start_time else now

        return data


###################################################################################################
