from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.cci_plan_b_workflow import CCIPlanBWorkflow
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.service.svc_workflow.helpers import celery_canvas_helpers
import mox


__author__ = "vgold"


class TestCCIPlanBWorkflow(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCCIPlanBWorkflow, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_logger = Dependency("FlaskLogger").value

        # various needed data
        self.company_id = "holla"
        self.context = {"user": "chicken_woot"}

        # main class to be tested
        self.mock = self.mox.CreateMock(CCIPlanBWorkflow)
        self.mock.context = self.context
        self.mock.company_ids = [1, 2, 3]
        self.mock.main_access = Dependency("CoreAPIProvider").value
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value

        self.mock.cci_task_name = 'asdf'

        self.mock.core_tasks = {
            self.mock.cci_task_name: self.mox.CreateMockAnything()
        }

    def doCleanups(self):

        # call parent clean up
        super(TestCCIPlanBWorkflow, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_run(self):

        self.mock._run_cci_updater(self.mock.company_ids).AndReturn("yoshi byebye")

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = CCIPlanBWorkflow.run(self.mock)

        # make sure results are good
        self.assertEqual(results, "yoshi byebye")

    def test_run_cci_updater(self):

        company_family_ids = [1, 2, 3]
        task_recs = [
            {"company_id": c, "context": self.context}
            for c in company_family_ids
        ]
        mock_result = "results"

        self.mox.StubOutWithMock(celery_canvas_helpers, 'run_task_groups')
        self.mox.StubOutWithMock(celery_canvas_helpers, 'aggregate_task_results')

        celery_canvas_helpers.run_task_groups(task_recs, self.mock.core_tasks[self.mock.cci_task_name]).AndReturn(mock_result)
        celery_canvas_helpers.aggregate_task_results(mock_result).AndReturn(mock_result)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = CCIPlanBWorkflow._run_cci_updater(self.mock, company_family_ids)

        # make sure results are good
        self.assertEqual(results, mock_result)
