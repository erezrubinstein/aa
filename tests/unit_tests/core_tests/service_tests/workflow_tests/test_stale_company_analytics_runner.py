from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.stale_company_analytics_runner import StaleCompanyAnalyticsRunner
from core.common.business_logic.service_entity_logic import company_helper
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from bson.objectid import ObjectId
import datetime
import uuid
import mox
import unittest


__author__ = "jsternberg"


class TestStaleCompanyAnalyticsRunner(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestStaleCompanyAnalyticsRunner, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies

        # various needed data
        self.context = {"user": "chicken_woot"}

        # main class to be tested
        self.mock = self.mox.CreateMock(StaleCompanyAnalyticsRunner)
        self.mock.context = self.context
        self.mock.main_access = Dependency("CoreAPIProvider").value
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value
        self.mock.logger = Dependency("FlaskLogger").value

    def doCleanups(self):

        # call parent clean up
        super(TestStaleCompanyAnalyticsRunner, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_run__basic(self):

        self.mock._get_needs_plan_b_company_count("start")
        self.mock._find_stale_companies_to_run()
        self.mock._mark_companies_as_needing_plan_b()
        self.mock._get_needs_plan_b_company_count("end")

        # fake state
        self.mock.needs_plan_b_company_count_start = 0
        self.mock.stale_companies_to_run = ["asdf"]
        self.mock.needs_plan_b_company_count_end = 1

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = StaleCompanyAnalyticsRunner.run(self.mock)

        # make sure results are good
        self.assertDictEqual(results, {
            "needs_plan_b_company_count_start": 0,
            "needs_plan_b_company_count_end": 1,
            "companies_marked_as_needing_plan_b": ["asdf"]
        })

    def test_run__nothing_to_do(self):

        self.mock._get_needs_plan_b_company_count("start")
        self.mock._find_stale_companies_to_run()
        self.mock._get_needs_plan_b_company_count("end")

        # fake state
        self.mock.needs_plan_b_company_count_start = 0
        self.mock.stale_companies_to_run = []
        self.mock.needs_plan_b_company_count_end = 0

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = StaleCompanyAnalyticsRunner.run(self.mock)

        # make sure results are good
        self.assertDictEqual(results, {
            "needs_plan_b_company_count_start": 0,
            "needs_plan_b_company_count_end": 0,
            "companies_marked_as_needing_plan_b": []
        })

    def test_get_needs_plan_b_company_count(self):

        for run_type in ["start", "end"]:

            mock_company_count = 42 # of course
            query = {
                "data.workflow.analytics.status": "needs_plan_b"
            }

            self.mock.main_access.mds.call_count_entities("company", query).AndReturn(mock_company_count)

            # replay all
            self.mox.ReplayAll()

            # run, baby!
            StaleCompanyAnalyticsRunner._get_needs_plan_b_company_count(self.mock, run_type)

            if run_type == "start":
                self.assertEqual(self.mock.needs_plan_b_company_count_start, 42)
            else:
                self.assertEqual(self.mock.needs_plan_b_company_count_end, 42)

            self.mox.ResetAll()

    def test_find_stale_companies_to_run(self):

        self.mock.max_needs_plan_b_companies = 5
        self.mock.needs_plan_b_company_count_start = 0
        self.mock.staleness_threshold_days = 42 # of course

        limit = self.mock.max_needs_plan_b_companies - self.mock.needs_plan_b_company_count_start

        mock_now = datetime.datetime(2014,1,1)

        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn(mock_now)

        staleness_date = mock_now - datetime.timedelta(days=self.mock.staleness_threshold_days)
        query = {
            "$and": [
                {
                    "data.workflow.current.status": "published"
                },
                {
                    "$or": [
                        {
                            "data.workflow.analytics.status": "success",
                            "$or": [
                                {"data.workflow.analytics.end_time": {"$lt": staleness_date}},
                                {"data.workflow.analytics.end_time": {"$lt": staleness_date.isoformat()}}
                            ]
                        },
                        {
                            "data.workflow.analytics.status": {"$exists": False},
                            "data.workflow.analytics.end_time": {"$exists": False}
                        }
                    ]
                },
                {
                    "$or": [
                        {
                            "data.type": "retail_banner"
                        },
                        {
                            "data.type": "retail_parent",
                            "links.company.retailer_branding.entity_role_to": "retail_segment"
                        }
                    ]
                }
            ]
        }
        fields = ["_id"]
        sort = [["data.workflow.analytics.end_time", 1], ["_id", 1]]
        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   limit=limit, sort=sort, as_list=True)["params"]
        mock_companies = [["asdf"],["blahblahblah"]]
        mock_results = ["asdf","blahblahblah"]
        self.mock.main_access.mds.call_find_entities_raw("company", params, self.context).AndReturn(mock_companies)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        StaleCompanyAnalyticsRunner._find_stale_companies_to_run(self.mock)

        # needful
        self.assertEqual(self.mock.stale_companies_to_run, mock_results)


    def test_mark_companies_as_needing_plan_b(self):

        self.mox.StubOutWithMock(company_helper, "mark_as_needs_plan_b")
        self.mock.stale_companies_to_run = ["asdf"]
        company_helper.mark_as_needs_plan_b(self.mock.stale_companies_to_run, self.context).AndReturn(None)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        StaleCompanyAnalyticsRunner._mark_companies_as_needing_plan_b(self.mock)



if __name__ == "__main__":
    unittest.main()
