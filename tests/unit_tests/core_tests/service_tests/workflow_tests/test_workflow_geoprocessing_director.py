from copy import deepcopy
import datetime

from bson.objectid import ObjectId
import mox

from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.service.svc_workflow.implementation.task.implementation.geoprocessing_tasks.geoprocessing_director import GeoprocessingDirector


__author__ = 'spacecowboy et al.'


class WorkflowGeoprocessingDirectorTests(mox.MoxTestBase):

    def setUp(self):

        super(WorkflowGeoprocessingDirectorTests, self).setUp()

        register_common_mox_dependencies(self.mox)

        self._director = self.mox.CreateMock(GeoprocessingDirector)

        self._director._logger = Dependency('FlaskLogger').value
        self._director._main_access = self.mox.CreateMockAnything()
        self._director._main_params = self.mox.CreateMockAnything()
        self._director._main_params.mds = self.mox.CreateMockAnything()
        self._director._main_access.mds = self.mox.CreateMockAnything()
        self._director._main_access.wfs = self.mox.CreateMockAnything()

        self._director._task_id = ObjectId()
        self._director._context = {'user_id': ObjectId(), 'source': '/unit/tests'}
        self._director._trade_area_threshold = 'BoatTime10Hours'
        self._director._geoprocessing_methods = ['do_the_hustle', 'oh_yeah']
        self._director._companies = []
        self._director._exception = None
        self._director.result = {'worker_task_ids': {}}

    def doCleanups(self):

        super(WorkflowGeoprocessingDirectorTests, self).doCleanups()
        dependencies.clear()


    # ________________________________________________ run tests _____________________________________________________ #

    def test_run(self):

        self._director._initialize_result().AndReturn(None)
        self._director._update_task_start().AndReturn(None)
        self._director._find_all_trade_areas_that_need_gp().AndReturn(None)
        self._director._spawn_geoprocessing_workers().AndReturn(None)
        self._director._set_result().AndReturn(None)
        self._director._update_task_end().AndReturn(None)

        self.mox.ReplayAll()

        result = GeoprocessingDirector.run(self._director)

        self.assertEqual(result, {'worker_task_ids': {}})


    def test_initialize_result(self):

        GeoprocessingDirector._initialize_result(self._director)

        self.assertEqual(self._director.result['worker_task_ids'], {'do_the_hustle': [], 'oh_yeah': []})

    def test_set_result__success(self):

        start_time = datetime.datetime.utcnow()

        self._director._status = 'success'
        self._director._start_time = start_time

        end_time = datetime.datetime.utcnow()

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(end_time)

        self.mox.ReplayAll()

        GeoprocessingDirector._set_result(self._director)

        expected_result = {
            'start_time': self._director._start_time,
            'duration_seconds': (end_time - start_time).total_seconds(),
            'worker_task_ids': {}
        }

        self.assertEqual(expected_result, self._director.result)

    def test_set_result__failed(self):

        start_time = datetime.datetime.utcnow()

        self._director._status = 'failed'
        self._director._start_time = start_time
        self._director._exception = 'There is a dolphin in your computer'

        end_time = datetime.datetime.utcnow()

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(end_time)

        self.mox.ReplayAll()

        GeoprocessingDirector._set_result(self._director)

        expected_result = {
            'start_time': self._director._start_time,
            'duration_seconds': (end_time - start_time).total_seconds(),
            'worker_task_ids': {},
            'exception': 'There is a dolphin in your computer'
        }

        self.assertEqual(expected_result, self._director.result)

    # __________________________________________ spawn worker tests __________________________________________________#
    def test_find_all_trade_areas_that_need_gp(self):

        expected_query = {
            '$or': [
                {
                    'data.geoprocessing.needs_gp.do_the_hustle': True,
                    'data.geoprocessing.latest_attempt.do_the_hustle.result': {'$ne': 'in_progress'}
                },
                {
                    'data.geoprocessing.needs_gp.oh_yeah': True,
                    'data.geoprocessing.latest_attempt.oh_yeah.result': {'$ne': 'in_progress'}
                }
            ]
        }
        expected_sort = [["data.geoprocessing.latest_attempt.find_competition.start_timestamp", 1]]

        self._director._main_params.mds.create_params(resource = 'find_entities_raw',
                                                      entity_fields = ['_id', 'data'],
                                                      query = expected_query,
                                                      sort = expected_sort,
                                                      # throttled for now
                                                      limit = 20000).AndReturn({'params': 'params'})

        self._director._main_access.mds.call_find_entities_raw('trade_area', 'params').AndReturn('bob')

        self.mox.ReplayAll()

        GeoprocessingDirector._find_all_trade_areas_that_need_gp(self._director)
        self.assertEqual(self._director._trade_areas, 'bob')

    def test_spawn_geoprocessing_workers(self):
        ta_1 = {
            'data': {
                'geoprocessing': {
                    'needs_gp': {
                        'do_the_hustle': True,
                        'oh_yeah': True
                    }
                },
                'trade_area_threshold': 'chicken'
            },
            '_id': 1,

        }
        ta_2 = {
            'data': {
                'geoprocessing': {
                    'needs_gp': {
                        'do_the_hustle': True,
                        'oh_yeah': False
                    }
                },
                'trade_area_threshold': 'woot'
            },
            '_id': 2,
        }
        ta_3 = {
            'data': {
                'geoprocessing': {
                    'needs_gp': {
                        'do_the_hustle': False,
                        'oh_yeah': True
                    }
                },
                'trade_area_threshold': 'sauce'
            },
            '_id': 3,
        }
        self._director._trade_areas = [ta_1, ta_2, ta_3]

        expected_task_rec_struct = {
            'input': {
                'geoprocessing_method': None,
                'entity_id': None,
                'entity_type': 'trade_area'
            },
            'meta': {
                'async': True
            },
            'task_status': {
                'status': 'in_progress'
            }
        }

        expected_task_rec_1 = deepcopy(expected_task_rec_struct)
        expected_task_rec_1['input']['geoprocessing_method'] = 'do_the_hustle'
        expected_task_rec_1['input']['entity_id'] = '1'

        expected_task_rec_3 = deepcopy(expected_task_rec_struct)
        expected_task_rec_3['input']['geoprocessing_method'] = 'do_the_hustle'
        expected_task_rec_3['input']['entity_id'] = '2'

        expected_task_rec_4 = deepcopy(expected_task_rec_struct)
        expected_task_rec_4['input']['geoprocessing_method'] = 'oh_yeah'
        expected_task_rec_4['input']['entity_id'] = '3'

        tasks = {
            'do_the_hustle': [expected_task_rec_1, expected_task_rec_3],
            'oh_yeah': [expected_task_rec_4]
        }

        for method in tasks:
            self._director._main_access.wfs.call_task_batch_new('retail_analytics',
                                                               'geoprocessing',
                                                               'geoprocess',
                                                               tasks[method],
                                                               self._director._context).AndReturn([{'_id': '%s_tasks_launched' % method}])

        self.mox.ReplayAll()
        GeoprocessingDirector._initialize_result(self._director)
        GeoprocessingDirector._spawn_geoprocessing_workers(self._director)
        self.assertEqual({
            'worker_task_ids': {
                'do_the_hustle': ['do_the_hustle_tasks_launched'],
                'oh_yeah': ['oh_yeah_tasks_launched']
            }
        }, self._director.result)
