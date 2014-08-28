import datetime

from bson.objectid import ObjectId
import mox

from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import geoprocessing_helper
from core.service.svc_workflow.implementation.task.implementation.geoprocessing_tasks.geoprocessing_worker import GeoprocessingWorker


__author__ = 'spacecowboy et al.'

class WorkflowGeorocessingWorkerTests(mox.MoxTestBase):

    def setUp(self):

        super(WorkflowGeorocessingWorkerTests, self).setUp()

        register_common_mox_dependencies(self.mox)

        self._mock_GeoProcess = self.mox.CreateMock(GeoprocessingWorker)

        self._mock_GeoProcess._logger = Dependency('FlaskLogger').value
        self._mock_GeoProcess._main_access = self.mox.CreateMockAnything()
        self._mock_GeoProcess._main_access.wfs = self.mox.CreateMockAnything()
        self._mock_GeoProcess._main_access.mds = self.mox.CreateMockAnything()
        self._mock_GeoProcess._main_params = self.mox.CreateMockAnything()
        self._mock_GeoProcess._main_params.mds = self.mox.CreateMockAnything()
        self._mock_GeoProcess._start_time = datetime.datetime(1990, 05, 18)
        self._mock_GeoProcess._exception = None
        self._mock_GeoProcess._geoprocessing_methods = {
            'get_demographics': self.mox.CreateMockAnything()
        }

        self._mock_GeoProcess._context = {'user_id': 42, 'source': 'unit tests'}
        self._mock_GeoProcess._task_id = 42
        self._mock_GeoProcess._run_gp_rules = True
        self._mock_GeoProcess.result = {}


    def doCleanups(self):

        super(WorkflowGeorocessingWorkerTests, self).doCleanups()
        dependencies.clear()

    def test_run_pass(self):

        self._mock_GeoProcess._entity_id = ObjectId()
        self._mock_GeoProcess._entity = { '_id': self._mock_GeoProcess._entity_id }
        self._mock_GeoProcess._entity_type = "trade_area"
        self._mock_GeoProcess._geoprocessing_method = 'get_demographics'
        self._mock_GeoProcess._update_task_start().AndReturn(None)
        self._mock_GeoProcess._get_entity().AndReturn(None)
        self._mock_GeoProcess._geoprocess().AndReturn(None)
        self._mock_GeoProcess._set_result().AndReturn(None)
        self._mock_GeoProcess._update_task_end().AndReturn(None)

        self.mox.ReplayAll()

        GeoprocessingWorker.run(self._mock_GeoProcess)
        self.assertEqual(self._mock_GeoProcess._status, 'success')

    def test_run_fail(self):

        def exception():
            raise ValueError('Oh no!!!')

        self._mock_GeoProcess._entity_id = ObjectId()
        self._mock_GeoProcess._entity = { '_id': self._mock_GeoProcess._entity_id }
        self._mock_GeoProcess._get_entity = exception
        self._mock_GeoProcess._entity_type = "trade_area"
        self._mock_GeoProcess._set_result().AndReturn(None)
        self._mock_GeoProcess._update_task_end().AndReturn(None)

        self.mox.ReplayAll()

        self.assertRaises(Exception, GeoprocessingWorker.run, self._mock_GeoProcess)




    def test_set_result_success(self):

        start = datetime.datetime(1990, 05, 18)
        end = datetime.datetime(1991, 05, 18)

        self._mock_GeoProcess._start_time = start
        self._mock_GeoProcess._status = 'success'
        self._mock_GeoProcess._entity_type = "trade_area"

        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn(end)

        self.mox.ReplayAll()

        # this should run with no exceptions or unexpected arguments
        GeoprocessingWorker._set_result(self._mock_GeoProcess)

        expected_result = {
            'start_time': start,
            'duration_seconds': (end - start).total_seconds()
        }

        self.assertEqual(expected_result, self._mock_GeoProcess.result)



    def test_set_results_failed(self):

        start = datetime.datetime(1990, 05, 18)
        end = datetime.datetime(1991, 05, 18)

        self._mock_GeoProcess._start_time = start
        self._mock_GeoProcess._status = 'failed'
        self._mock_GeoProcess._entity_type = "trade_area"
        self._mock_GeoProcess._exception = 'THERE ARE CHICKENS IN THE BUILDING'

        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn(end)

        self.mox.ReplayAll()

        # this should run with no exceptions or unexpected arguments
        GeoprocessingWorker._set_result(self._mock_GeoProcess)

        expected_result = {
            'exception': 'THERE ARE CHICKENS IN THE BUILDING',
            'start_time': start,
            'duration_seconds': (end - start).total_seconds()
        }

        self.assertEqual(expected_result, self._mock_GeoProcess.result)



class MockGP(object):
    def __init__(self):

        self._process_repository = None

    def process_entity(self, trade_area):
        self._process_repository = 'I processed'