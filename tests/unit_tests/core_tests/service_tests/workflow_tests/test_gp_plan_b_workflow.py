from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.geoprocessing_plan_b_workflow import GeoprocessingPlanBWorkflow
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.service.svc_workflow.helpers import celery_canvas_helpers
import mox


__author__ = "vgold"


class TestGPPlanBWorkflow(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestGPPlanBWorkflow, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_logger = Dependency("FlaskLogger").value

        # various needed data
        self.company_id = "holla"
        self.context = {"user": "chicken_woot"}

        # main class to be tested
        self.mock = self.mox.CreateMock(GeoprocessingPlanBWorkflow)
        self.mock.context = self.context
        self.mock.company_ids = [1, 2, 3]
        self.mock.main_access = Dependency("CoreAPIProvider").value
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value

        self.mock.geoproc_worker_task_name = 'asdf'
        self.mock.geoproc_upserter_task_name = 'qwer'

        self.mock.core_tasks = {
            self.mock.geoproc_worker_task_name: self.mox.CreateMockAnything(),
            self.mock.geoproc_upserter_task_name: self.mox.CreateMockAnything()
        }

    def doCleanups(self):

        # call parent clean up
        super(TestGPPlanBWorkflow, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_run(self):

        stores = "stores"
        trade_area_ids_requiring_gp7 = "trade_area_ids_requiring_gp7"
        trade_area_ids = ["trade_area_ids"]
        mock_result = {
            "gp7_results": 1,
            "gp9_results": 2,
            "gp14_results": 3,
            "gp16_results": 4
            #"gp16_results": { "succeeded": [], "failed": [] }
        }

        self.mock._get_all_store_ids(self.mock.company_ids).AndReturn(stores)
        self.mock._upsert_all_trade_areas(stores).AndReturn(trade_area_ids_requiring_gp7)
        self.mock._get_trade_area_ids(self.mock.company_ids).AndReturn(trade_area_ids)

        self.mock._run_generic_gp(trade_area_ids_requiring_gp7, "get_demographics").AndReturn(1)
        self.mock._run_generic_gp(trade_area_ids, "find_competition").AndReturn(2)
        self.mock._run_generic_gp(trade_area_ids, "find_white_space_competition").AndReturn(3)
        self.mock._run_generic_gp(trade_area_ids, "get_weather").AndReturn(4)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = GeoprocessingPlanBWorkflow.run(self.mock)

        # make sure results are good
        self.assertEqual(results, mock_result)

    def test_get_all_store_ids(self):

        # define mocks
        mock_company_family_ids = ["yes", "sir"]
        mock_params = {
            "query": {"data.company_id": {"$in": mock_company_family_ids}},
            "entity_fields": ["_id"],
            "options": {"as_list": True}
        }
        mock_stores = [
            ["moon"],
            ["shine"]
        ]

        # begin recording
        self.mock.main_access.mds.call_find_entities_raw("store", mock_params, self.context).AndReturn(mock_stores)

        # replay all
        self.mox.ReplayAll()

        # go!
        results = GeoprocessingPlanBWorkflow._get_all_store_ids(self.mock, mock_company_family_ids)

        # make sure we get the ids back
        self.assertListEqual(results, [["moon"], ["shine"]])

    def test_upsert_all_trade_areas(self):

        stores = [[1], [2], [3]]
        task_recs = [
            {"store_id": s[0], "context": self.context}
            for s in stores
        ]
        results = [
            {"trade_area_id": 1, "requires_gp7": False},
            {"trade_area_id": 2, "requires_gp7": True},
            {"trade_area_id": 3, "requires_gp7": True}
        ]
        mock_result = [2, 3]

        self.mox.StubOutWithMock(celery_canvas_helpers, 'run_task_groups')

        celery_canvas_helpers.run_task_groups(task_recs, self.mock.core_tasks[self.mock.geoproc_upserter_task_name]).AndReturn(results)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = GeoprocessingPlanBWorkflow._upsert_all_trade_areas(self.mock, stores)

        # make sure results are good
        self.assertEqual(results, mock_result)

    def test_get_trade_area_ids(self):

        # define mocks
        mock_company_family_ids = ["yes", "sir"]
        mock_params = {
            "query": {"data.company_id": {"$in": mock_company_family_ids}},
            "entity_fields": ["_id"],
            "options": {"as_list": True}
        }
        mock_trade_areas = [
            ["moon"],
            ["shine"]
        ]

        # begin recording
        self.mock.main_access.mds.call_find_entities_raw("trade_area", mock_params,
                                                         self.context).AndReturn(mock_trade_areas)

        # replay all
        self.mox.ReplayAll()

        # go!
        results = GeoprocessingPlanBWorkflow._get_trade_area_ids(self.mock, mock_company_family_ids)

        # make sure we get the ids back
        self.assertListEqual(results, ["moon", "shine"])

    def test_run_generic_gp(self):

        trade_area_ids = [1, 2]
        method = "blah"

        self.mock._get_gp_worker_task_rec(1, "blah").AndReturn(None)
        self.mock._get_gp_worker_task_rec(2, "blah").AndReturn(None)

        self.mox.StubOutWithMock(celery_canvas_helpers, 'run_task_groups')
        self.mox.StubOutWithMock(celery_canvas_helpers, 'aggregate_task_results')

        celery_canvas_helpers.run_task_groups([None, None], self.mock.core_tasks[self.mock.geoproc_worker_task_name]).AndReturn("HIYA!")
        celery_canvas_helpers.aggregate_task_results("HIYA!").AndReturn("WOOSH!!")

        # replay all
        self.mox.ReplayAll()

        # go!
        results = GeoprocessingPlanBWorkflow._run_generic_gp(self.mock, trade_area_ids, method)

        # make sure we get the ids back
        self.assertEqual(results, "WOOSH!!")
