import datetime
from mox import IsA
from common.utilities import lox
from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks import analytics_data_checker, company_family_analytics_calculator, white_space_cell_analytics
from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.company_analytics_plan_b import CompanyAnalyticsPlanB
from core.common.business_logic.service_entity_logic import company_store_count_helper
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from celery import canvas
import unittest
import mox


__author__ = "erezrubinstein"


class TestCompanyAnalyticsPlanB(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCompanyAnalyticsPlanB, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_main_params_builder = Dependency("CoreAPIParamsBuilder").value
        self.mock_logger = Dependency("FlaskLogger").value

        # various needed data
        self.context = {"user": "chicken_woot"}
        self.company_id = "holla"

        # main class to be tested
        self.plan_b = self.mox.CreateMock(CompanyAnalyticsPlanB)
        self.plan_b.logger = self.mock_logger
        self.plan_b.company_id = self.company_id
        self.plan_b.banner_ids = ["taco", "bell"]
        self.plan_b.parent_id = "doritos"
        self.plan_b.context = self.context
        self.plan_b.no_korki_email = True

        self.plan_b.gp_workflow_name = 'gp'
        self.plan_b.cci_workflow_name = 'cci'

        self.plan_b.core_tasks = {
            self.plan_b.gp_workflow_name: self.mox.CreateMockAnything(),
            self.plan_b.cci_workflow_name: self.mox.CreateMockAnything()
        }

    def doCleanups(self):

        # call parent clean up
        super(TestCompanyAnalyticsPlanB, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_init(self):
        # there is a bunch of logic in init, so let's test it

        input_rec = {}
        plan_b_obj = CompanyAnalyticsPlanB(input_rec)

        self.assertIsNone(plan_b_obj.task_id)
        self.assertFalse(hasattr(plan_b_obj, "company_id"))
        self.assertFalse(hasattr(plan_b_obj, "run_id"))

        input_rec = {
            "task_id": "this is a unique task ID, yo",
            "company_id": "My job is to identify a company.",
            "context": "I was sitting at my desk, typing.",
            "run_id": "1234567890-900594yu985y6-ugdjbjdbjfbgjbfj-123",
            "no_korki_email": True,
            "spawn_analytics_calc_subtasks": True,
            "store_count": 777,
            "store_count_subtask_threshold": 100
        }
        plan_b_obj = CompanyAnalyticsPlanB(input_rec)

        self.assertEqual(plan_b_obj.task_id, "this is a unique task ID, yo")
        self.assertEqual(plan_b_obj.company_id, "My job is to identify a company.")
        self.assertEqual(plan_b_obj.context, "I was sitting at my desk, typing.")
        self.assertEqual(plan_b_obj.context_data, "I was sitting at my desk, typing.")
        self.assertEqual(plan_b_obj.run_id, "1234567890-900594yu985y6-ugdjbjdbjfbgjbfj-123")
        self.assertTrue(plan_b_obj.no_korki_email)
        self.assertTrue(plan_b_obj.spawn_analytics_calc_subtasks)
        self.assertEqual(plan_b_obj.store_count, 777)
        self.assertEqual(plan_b_obj.store_count_subtask_threshold, 100)
        self.assertEqual(plan_b_obj.input, {
            "company_id": plan_b_obj.company_id,
            "run_id": plan_b_obj.run_id,
            "no_korki_email": plan_b_obj.no_korki_email,
            "spawn_analytics_calc_subtasks": plan_b_obj.spawn_analytics_calc_subtasks,
            "store_count": plan_b_obj.store_count,
            "store_count_subtask_threshold": plan_b_obj.store_count_subtask_threshold
        })
        self.assertEqual(plan_b_obj.output, {})

    def test_run__success(self):

        # define mocks
        mock_result = "woot"
        mock_lock = self.mox.CreateMockAnything(lox.Lox)

        # stub out stuff
        self.mox.StubOutWithMock(lox, "Lox")

        # begin recording
        self.plan_b._get_company_banner_ids()
        lox.Lox("plan_b_lock", ["taco", "bell", "doritos"], (self.context,)).AndReturn(mock_lock)
        mock_lock.__enter__()
        self.plan_b._validate_company_family_workflow_analytics()
        self.plan_b._update_task_start()
        self.plan_b._update_company_family_plan_b_start()
        self.plan_b._update_task_message("compute_collection_dates")
        self.plan_b._compute_collection_dates()
        self.plan_b._update_task_message("get_latest_econ_month")
        self.plan_b._get_latest_econ_month()
        self.plan_b._update_task_message("run_geoprocessing_and_cci_update")
        self.plan_b._run_geoprocessing_and_cci_update()
        self.plan_b._update_task_message("run_company_family_analytics")
        self.plan_b._run_company_family_analytics()
        self.plan_b._update_task_message("run_white_space_analytics")
        self.plan_b._run_white_space_analytics()
        self.plan_b._update_task_message("update_store_collection_dates")
        self.plan_b._update_store_collection_dates()
        self.plan_b._update_task_message("update_company_family_date_ranges")
        self.plan_b._update_company_family_date_ranges()
        self.plan_b._update_task_message("run_company_family_data_checks")
        self.plan_b._run_company_family_data_checks()
        self.plan_b._update_company_family_plan_b_finish()
        self.plan_b._get_output_data().AndReturn({"output": "data"})
        self.plan_b._update_task_end()
        mock_lock.__exit__(None, None, None)

        self.plan_b.host = None
        self.plan_b.exception = None
        self.plan_b.collection_dates = None
        self.plan_b.gp7_results = None
        self.plan_b.gp9_results = None
        self.plan_b.gp14_results = None
        self.plan_b.gp16_results = None
        self.plan_b.cci_results = None
        self.plan_b.company_analytics_results = None
        self.plan_b.data_check_results = None
        self.plan_b.white_space_results = None
        self.plan_b.duration_seconds = None

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = CompanyAnalyticsPlanB.run(self.plan_b)

        # make sure results are good
        self.assertEqual(self.plan_b.status, "success")
        self.assertDictEqual(results, {
            "status": self.plan_b.status,
            "exception": self.plan_b.exception,
            "duration_seconds": results["duration_seconds"],
            "start_time": results["start_time"],
            "end_time": results["end_time"],
            "company_id": self.plan_b.company_id,
            "gp7_results": self.plan_b.gp7_results,
            "gp9_results": self.plan_b.gp9_results,
            "gp14_results": self.plan_b.gp14_results,
            "gp16_results": self.plan_b.gp16_results,
            "cci_results": self.plan_b.cci_results,
            "company_analytics_results": self.plan_b.company_analytics_results,
            "data_check_results": self.plan_b.data_check_results,
            "white_space_results": self.plan_b.white_space_results,
            "host": self.plan_b.host
        })
        self.assertDictEqual(self.plan_b.output, {"output": "data"})

    def test_run__fail(self):

        # define mocks
        mock_exception = Exception("BREAK YO'SELF")

        # create exception side effect
        def exception_side_effect(*args):
            raise mock_exception

        # begin recording
        self.plan_b._update_task_start().WithSideEffects(exception_side_effect)

        self.plan_b.logger.error(mox.IgnoreArg())
        self.plan_b._update_task_end()

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        with self.assertRaises(Exception):
            CompanyAnalyticsPlanB.run(self.plan_b)

        # make sure status is error
        self.assertEqual(self.plan_b.status, "error")

    def test_run_geoprocessing_and_cci_update__success(self):

        self.plan_b.banner_ids = "banner_ids"
        self.plan_b.context = "context"

        self.mox.StubOutWithMock(canvas, "group")

        input_rec = {
            "company_ids": self.plan_b.banner_ids,
            "context": self.plan_b.context
        }

        group_mock = self.mox.CreateMockAnything()

        canvas.group([
            self.plan_b.core_tasks[self.plan_b.gp_workflow_name].s(input_rec).AndReturn(None),
            self.plan_b.core_tasks[self.plan_b.cci_workflow_name].s(input_rec).AndReturn(None)
        ]).AndReturn(group_mock)

        result_mock = self.mox.CreateMockAnything()
        group_mock().AndReturn(result_mock)

        gp7res = {"succeeded": [], "failed": []}
        gp9res = {"succeeded": [], "failed": []}
        gp14res = {"succeeded": [], "failed": []}
        gp16res = {"succeeded": [], "failed": []}
        cci_res = {"succeeded": [], "failed": []}

        results = [
            {
                "gp7_results": gp7res,
                "gp9_results": gp9res,
                "gp14_results": gp14res,
                "gp16_results": gp16res
            },
            cci_res
        ]
        result_mock.get().AndReturn(results)

        # replay all
        self.mox.ReplayAll()

        CompanyAnalyticsPlanB._run_geoprocessing_and_cci_update(self.plan_b)

        self.assertDictEqual(self.plan_b.gp7_results, gp7res)
        self.assertDictEqual(self.plan_b.gp9_results, gp9res)
        self.assertDictEqual(self.plan_b.gp14_results, gp14res)
        self.assertDictEqual(self.plan_b.gp16_results, gp16res)
        self.assertDictEqual(self.plan_b.cci_results, cci_res)

    def test_run_geoprocessing_and_cci_update__failure(self):

        self.plan_b.banner_ids = "banner_ids"
        self.plan_b.context = "context"

        self.mox.StubOutWithMock(canvas, "group")

        input_rec = {
            "company_ids": self.plan_b.banner_ids,
            "context": self.plan_b.context
        }

        group_mock = self.mox.CreateMockAnything()

        canvas.group([
            self.plan_b.core_tasks[self.plan_b.gp_workflow_name].s(input_rec).AndReturn(None),
            self.plan_b.core_tasks[self.plan_b.cci_workflow_name].s(input_rec).AndReturn(None)
        ]).AndReturn(group_mock)

        result_mock = self.mox.CreateMockAnything()
        group_mock().AndReturn(result_mock)

        exception = Exception("YOSHI GO NIGHT NIGHT")

        gp7res = {"succeeded": [], "failed": [exception]}
        gp9res = {"succeeded": [], "failed": []}
        gp14res = {"succeeded": [], "failed": []}
        cci_res = {"succeeded": [], "failed": []}

        results = [
            {
                "gp7_results": gp7res,
                "gp9_results": gp9res,
                "gp14_results": gp14res
            },
            cci_res
        ]
        result_mock.get().AndReturn(results)

        # replay all
        self.mox.ReplayAll()

        with self.assertRaises(Exception):
            CompanyAnalyticsPlanB._run_geoprocessing_and_cci_update(self.plan_b)

    def test_run_white_space_analytics(self):

        # stub out stuff
        self.mox.StubOutClassWithMocks(white_space_cell_analytics, "WhiteSpaceCellAnalytics")
        self.mox.StubOutWithMock(company_store_count_helper, "get_company_analytics_store_counts")
        mock_store_count_time_series = [
            {"date":datetime.datetime(2013,12,1), "value": 12},
            {"date":datetime.datetime(2013,11,1), "value": 12}
        ]
        self.plan_b.collection_dates = {}

        # begin recording
        # taco, bell are set as the banner ids in the top of this class
        mock_analytics = white_space_cell_analytics.WhiteSpaceCellAnalytics({"company_id": "taco", "context": self.context })
        mock_analytics.run()
        mock_analytics = white_space_cell_analytics.WhiteSpaceCellAnalytics({"company_id": "bell", "context": self.context })
        mock_analytics.run()

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanB._run_white_space_analytics(self.plan_b)

    def test_run_company_family_analytics(self):

        self.plan_b.banner_ids = "banner_ids"
        self.plan_b.parent_id = "parent_id"
        self.plan_b.spawn_analytics_calc_subtasks = True
        self.plan_b.store_count = 4242
        self.plan_b.store_count_subtask_threshold = 12
        self.plan_b.latest_econ_month = datetime.datetime.utcnow()

        company_analytics_input_rec = {
            "parent_id": self.plan_b.parent_id,
            "banner_ids": self.plan_b.banner_ids,
            "engines": ["stores", "monopolies", "demographics", "competition", "economics"],
            "context": self.context,
            "spawn_calc_subtasks": self.plan_b.spawn_analytics_calc_subtasks,
            "store_count": self.plan_b.store_count,
            "store_count_subtask_threshold": self.plan_b.store_count_subtask_threshold,
            "latest_econ_month": self.plan_b.latest_econ_month
        }

        # stub out stuff
        self.mox.StubOutClassWithMocks(company_family_analytics_calculator, "CompanyFamilyAnalyticsCalculator")

        company_analytics_calc = company_family_analytics_calculator.CompanyFamilyAnalyticsCalculator(company_analytics_input_rec)
        company_analytics_calc.run().AndReturn("HEYO")

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanB._run_company_family_analytics(self.plan_b)

        self.assertEqual(self.plan_b.company_analytics_results, "HEYO")

    def test_run_company_family_data_checks(self):

        self.plan_b.config = {"ENVIRONMENT": "ASDF"}
        self.plan_b.company_family_ids = [1, 2, 3]

        input_rec = {
            "sample_size": -1,
            "company_only": True,
            "global_only": False,
            "company_ids": [1, 2, 3],
            "update_companies": True,
            "add_success_results_to_report": True,

            # Only send emails for production environments
            "no_email": True,
            "context": self.context
        }

        # stub out stuff
        self.mox.StubOutClassWithMocks(analytics_data_checker, "AnalyticsDataChecker")

        data_checker = analytics_data_checker.AnalyticsDataChecker(input_rec)
        data_checker.run().AndReturn("HEYO")

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanB._run_company_family_data_checks(self.plan_b)

        self.assertEqual(self.plan_b.data_check_results, "HEYO")

    def test_get_output_data(self):

        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds=1)

        self.plan_b.exception = "just exceptional"
        self.plan_b.start_time = start
        self.plan_b.end_time = end

        self.plan_b.gp7_results = "sljdbgjfbgjfbg"
        self.plan_b.gp9_results = "asdf"
        self.plan_b.gp14_results = None
        self.plan_b.gp16_results = -18181
        self.plan_b.cci_results = [{},{"weird"}, "stuff"]
        self.plan_b.company_analytics_results = False
        self.plan_b.data_check_results = "alllllll good"
        self.plan_b.white_space_results = "no room"

        output = CompanyAnalyticsPlanB._get_output_data(self.plan_b)

        self.assertDictEqual(output, {
            "exception": self.plan_b.exception,
            "duration_seconds": 1.0,
            "start_time": str(self.plan_b.start_time)[0:19],
            "end_time": str(self.plan_b.end_time)[0:19],
            "gp7_results": self.plan_b.gp7_results,
            "gp9_results": self.plan_b.gp9_results,
            "gp14_results": self.plan_b.gp14_results,
            "gp16_results": self.plan_b.gp16_results,
            "cci_results": self.plan_b.cci_results,
            "company_analytics_results": self.plan_b.company_analytics_results,
            "data_check_results": self.plan_b.data_check_results,
            "white_space_results": self.plan_b.white_space_results
        })


if __name__ == "__main__":
    unittest.main()