from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.stale_company_analytics_runner import StaleCompanyAnalyticsRunner
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from bson.objectid import ObjectId
import datetime
import uuid


__author__ = 'jsternberg'


class WFSStaleAnalyticsTestCollection(ServiceTestCollection):

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


    def wfs_test_stale_company_analytics_runner(self):

        max_needs_plan_b_companies = 3
        staleness_threshold_days = 60

        now = datetime.datetime.utcnow()
        is_stale_date_1 = now - datetime.timedelta(days=staleness_threshold_days + 2)
        is_stale_date_2 = now - datetime.timedelta(days=staleness_threshold_days + 1)
        not_stale_date =  now - datetime.timedelta(days=staleness_threshold_days - 1)

        ## positive tests

        # create a published banner that is stale because it has no data.analytics (i.e. pre Oct 2013)
        # should be returned 1st because null wins when sorting ascending
        banner1 = insert_test_company(type="retail_banner", workflow_status="published", use_new_json_encoder=True)
        # create a published banner that is stale -- should be marked, and returned 2nd since it's older than the next
        banner2 = insert_test_company(type="retail_banner", workflow_status="published", analytics_status={"status": "success", "end_time": is_stale_date_1}, use_new_json_encoder=True)
        # create a published parent that is stale -- should be marked, and returned 3rd since it's newer than the 2nd
        # also for this one, use a string date instead of datetime date
        parent1 = insert_test_company(type="retail_parent", workflow_status="published", analytics_status={"status": "success", "end_time": is_stale_date_2}, use_new_json_encoder=True)
        # link the parent to the banner, because we don't mark childless parents
        self.main_access.mds.call_add_link("company", banner2, "retail_segment", "company", parent1, "retail_parent", "retailer_branding", self.context)

        ## negative tests

        # create a published banner that is stale, but should not be marked because the previous 3 companies hit the limit
        banner3 = insert_test_company(type="retail_banner", workflow_status="published", analytics_status={"status": "success", "end_time": is_stale_date_2}, use_new_json_encoder=True)
        # create a published banner that is NOT stale -- should not be marked because not stale
        banner4 = insert_test_company(type="retail_banner", workflow_status="published", analytics_status={"status": "success", "end_time": not_stale_date}, use_new_json_encoder=True)
        # create a NOT published banner that is stale -- should not be marked because not published
        banner5 = insert_test_company(type="retail_banner", workflow_status="new", analytics_status={"status": "success", "end_time": is_stale_date_1}, use_new_json_encoder=True)
        # create an owner company that is stale -- should not be marked because owners aren't marked
        owner1 = insert_test_company(type="retail_owner", workflow_status="published", analytics_status={"status": "success", "end_time": is_stale_date_1}, use_new_json_encoder=True)

        runner = StaleCompanyAnalyticsRunner({
            "async": False,
            "max_needs_plan_b_companies": max_needs_plan_b_companies,
            "staleness_threshold_days": staleness_threshold_days,
            "context": self.context
        })
        results = runner.run()

        self.test_case.assertDictEqual(results, {
            "needs_plan_b_company_count_start": 0,
            "needs_plan_b_company_count_end": max_needs_plan_b_companies,
            "companies_marked_as_needing_plan_b": [str(banner1), str(banner2), str(parent1)]
        })

        # make sure that companies were marked properly
        query = {
            "_id": {
                "$in": map(ObjectId, [banner1, banner2, parent1])
            }
        }
        fields = [
            "_id",
            "data.workflow.analytics.status"
        ]
        sort = [["_id", 1]]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   sort=sort, as_list=True)["params"]
        companies = self.main_access.mds.call_find_entities_raw("company", params, self.context)

        expected_companies = [
            [banner1, "needs_plan_b"],
            [banner2, "needs_plan_b"],
            [parent1, "needs_plan_b"]
        ]
        self.test_case.assertEqual(companies, expected_companies)

        pass