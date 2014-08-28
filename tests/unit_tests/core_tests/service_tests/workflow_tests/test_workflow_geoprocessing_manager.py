import datetime

import mox

from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.service.svc_workflow.implementation.task.implementation.geoprocessing_tasks.geoprocessing_manager import GeoprocessingManager
from geoprocessing.geoprocessors.demographics.gp7_core_trade_area_geo_processor import GP7CoreTradeAreaDemographics
from geoprocessing.geoprocessors.competition.gp9_core_trade_area_competition_geo_json import GP9CoreTradeAreaCompetition


__author__ = 'erezrubinstein'


class WorkflowGeoprocessingManagerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(WorkflowGeoprocessingManagerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_main_params = Dependency("CoreAPIParamsBuilder").value

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.task_id = "chilly_willy"
        self.company_id = "chicken"
        self.trade_area_threshold = "woot"
        self.geoprocessing_method = "danger_zone"
        self.mock_input_rec = {
            "company_id": self.company_id,
            "context": self.context,
            "trade_area_threshold": self.trade_area_threshold,
            "geoprocessing_method": self.geoprocessing_method,
            'follow_rules': True,
            "task_id": self.task_id
        }


    def doCleanups(self):
        # call parent clean up
        super(WorkflowGeoprocessingManagerTests, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_manager_init(self):

        # create manager object
        manager = GeoprocessingManager(self.mock_input_rec)

        # make sure it's setup correctly
        self.assertEqual(manager._company_id, self.company_id)
        self.assertEqual(manager._context, self.context)
        self.assertEqual(manager._trade_area_threshold, self.trade_area_threshold)
        self.assertEqual(manager._geoprocessing_method, "danger_zone")
        self.assertEqual(manager._task_id, self.task_id)

        # make sure it has all the correct gp methods
        self.assertEqual(manager._geoprocessing_methods["get_demographics"], GP7CoreTradeAreaDemographics)
        self.assertEqual(manager._geoprocessing_methods["find_competition"], GP9CoreTradeAreaCompetition)

        # make sure misc vars are correct
        self.assertEqual(manager._status, "in_progress")
        self.assertEqual(manager._task_rec, {
            'input': {
                'manager_id': manager._task_id,
                'entity_id': None,
                'entity_type': 'trade_area',
                'geoprocessing_method': self.geoprocessing_method,
            },
            'meta': {
                'async': True
            },
            'task_status': {
                'status': "in_progress"
            }
        })


    def test_manager_run__success(self):

        # create manager object
        manager = GeoprocessingManager(self.mock_input_rec)

        # stub out several methods
        self.mox.StubOutWithMock(manager, "_update_task_start")
        self.mox.StubOutWithMock(manager, "_get_store_ids")
        self.mox.StubOutWithMock(manager, "_spawn_geoprocessing_tasks_for_stores")
        self.mox.StubOutWithMock(manager, '_set_result')
        self.mox.StubOutWithMock(manager, "_update_task_end")

        # start recording
        manager._update_task_start()
        manager._get_store_ids()
        manager._spawn_geoprocessing_tasks_for_stores()
        manager._set_result()
        manager._update_task_end()

        # replay all
        self.mox.ReplayAll()

        # go
        manager.run()

        # verify results
        self.assertEqual(manager._status, "success")


    def test_manager_run__failure(self):

        # create manager object
        manager = GeoprocessingManager(self.mock_input_rec)

        # create fake method that raises exception
        ex = Exception("danger_zone")
        def ex_method():
            raise ex

        # set the first method to raise an exception
        manager._update_task_start = ex_method

        # stub out several methods
        self.mox.StubOutWithMock(manager, "_set_result")
        self.mox.StubOutWithMock(manager, "_update_task_end")

        # start recording (only one thing called)
        manager._set_result()
        manager._update_task_end()

        # replay all
        self.mox.ReplayAll()

        # go
        manager.run()

        # verify results
        self.assertEqual(manager._status, "failed"),
        self.assertEqual(manager._exception, ex)


    def test_manager_def_update_task_start(self):

        # create manager object
        manager = GeoprocessingManager(self.mock_input_rec)
        mock_datetime = datetime.datetime.utcnow()

        # create mock data
        params_task = {
            'task_status': {
                'status': 'in_progress',
                'result': {
                    'start_timestamp': mock_datetime.isoformat()
                }
            }
        }



        # stub out methods
        self.mox.StubOutWithMock(datetime, "datetime")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_datetime)
        self.mock_main_access.wfs.call_update_task_id(self.task_id, self.context, params_task)

        # replay all
        self.mox.ReplayAll()

        # go
        manager._update_task_start()


    def test_manager_get_stores(self):

        # create manager object
        manager = GeoprocessingManager(self.mock_input_rec)

        expected_store_query = {'data.company_id': manager._company_id}

        mock_store_recs = [
            {'_id': 1},
            {'_id': 2},
            {'_id': 3}
        ]

        expected_params = {'query': expected_store_query}

        # begin recording
        self.mock_main_access.mds.call_find_entities_raw('store', params = expected_params, context = self.context).AndReturn(mock_store_recs)

        # replay all
        self.mox.ReplayAll()

        # go
        manager._get_store_ids()

        # make sure the response is correct
        self.assertEqual(manager._store_ids, ['1', '2', '3'])


    def test_spawn_geoprocessing_tasks_for_stores(self):

        # create manager object
        manager = GeoprocessingManager(self.mock_input_rec)

        # create mock data
        mock_store_ids = [
            "chilly",
            "chicken"
        ]
        mock_response1 = { "_id": "willy" }
        mock_response2 = { "_id": "woot" }
        task_rec1 = {
            'input': {
                'manager_id': manager._task_id,
                'entity_id': 'chilly_trade_area_id',
                'entity_type': 'trade_area',
                'geoprocessing_method': self.geoprocessing_method,
            },
            'meta': {
                'async': True
            },
            'task_status': {
                'status': 'in_progress'
            }
        }
        task_rec2 = {
            'input': {
                'manager_id': manager._task_id,
                'entity_id': 'chicken_trade_area_id',
                'entity_type': 'trade_area',
                'geoprocessing_method': self.geoprocessing_method,
            },
            'meta': {
                'async': True
            },
            'task_status': {
                'status': 'in_progress'
            }
        }

        # begin recording
        self.mox.StubOutWithMock(manager, '_upsert_trade_area')
        manager._upsert_trade_area('chilly').AndReturn({ "trade_area_id": 'chilly_trade_area_id'})
        manager._upsert_trade_area('chicken').AndReturn({ "trade_area_id": 'chicken_trade_area_id'})

        self.mock_main_access.wfs.call_task_new('retail_analytics', 'geoprocessing', 'geoprocess', task_rec1, self.context).AndReturn(mock_response1)
        self.mock_main_access.wfs.call_task_new('retail_analytics', 'geoprocessing', 'geoprocess', task_rec2, self.context).AndReturn(mock_response2)

        # give the mock geoprocessor the list of mock store ids
        manager._store_ids = mock_store_ids

        # replay all
        self.mox.ReplayAll()

        # go
        manager._spawn_geoprocessing_tasks_for_stores()

        # make sure that the manager's output is correct
        self.assertEqual(manager.result, {
            "worker_task_ids_store_ids": {
                "willy": "chilly",
                "woot": "chicken"
            }
        })


    def test_update_task_end__success(self):

        # create manager object
        manager = GeoprocessingManager(self.mock_input_rec)
        manager.result = 'mock_result'
        # mock various parameters
        mock_status = manager._status = "success"
        params_task = {
            'task_status': {
                'status': mock_status,
                'result': 'mock_result'
            }
        }

        self.mock_main_access.wfs.call_update_task_id(self.task_id, self.context, params_task)

        # replay all
        self.mox.ReplayAll()

        # go!
        manager._update_task_end()


