from core.service.svc_workflow.helpers.celery_canvas_helpers import run_task_groups, aggregate_task_results
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from celery import canvas
import mox


__author__ = "vgold"


class TestCeleryCanvasHelpers(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCeleryCanvasHelpers, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_logger = Dependency("FlaskLogger").value

        # various needed data
        self.company_id = "holla"
        self.context = {"user": "chicken_woot"}

    def doCleanups(self):

        # call parent clean up
        super(TestCeleryCanvasHelpers, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_run_task_groups(self):

        # define mocks
        mock_task_recs = [
            {"store_id": 0, "context": self.context},
            {"store_id": 1, "context": self.context}
        ]
        mock_results = [
            {"requires_gp7": False, "trade_area_id": "billy"},
            {"requires_gp7": True, "trade_area_id": "willy"}
        ]
        mock_task = self.mox.CreateMockAnything()
        mock_group = self.mox.CreateMockAnything()
        mock_group_results = self.mox.CreateMockAnything()

        # stub out some stuff
        self.mox.StubOutWithMock(canvas, "group")

        # begin recording
        mock_task.s(mock_task_recs[0]).AndReturn("shalom")
        mock_task.s(mock_task_recs[1]).AndReturn("hello")
        canvas.group(["shalom", "hello"]).AndReturn(mock_group)
        mock_group().AndReturn(mock_group_results)
        mock_group_results.get(propagate=False).AndReturn(mock_results)

        # replay all
        self.mox.ReplayAll()

        # go!
        results = run_task_groups(mock_task_recs, mock_task)

        # make sure results are correct
        self.assertEqual(results, mock_results)

    def test_aggregate_task_results(self):

        mock_results = [
            Exception("HEYO WHAT'S MY NAME-O"),
            "yoshi",
            "fire flower",
            Exception("KING KOOPA")
        ]

        results = aggregate_task_results(mock_results)

        # make sure results are correct
        self.assertEqual(len(results["succeeded"]), 2)
        self.assertEqual(len(results["failed"]), 2)
