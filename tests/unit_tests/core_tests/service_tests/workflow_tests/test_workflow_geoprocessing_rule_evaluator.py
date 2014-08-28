import datetime
import traceback
from bson.objectid import ObjectId
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import industry_helper
from core.common.business_logic.service_entity_logic.geoprocessing_rules.evaluate_need_for_geoprocessing import EvaluateNeedForGeoprocessing
from core.service.svc_workflow.implementation.task.implementation.geoprocessing_tasks.geoprocessing_rules_evaluator import GeoprocessingRulesEvaluator

__author__ = 'kingneptune'


class WorkflowGeoprocessingRulesEvaluatorTests(mox.MoxTestBase):

    def setUp(self):

        super(WorkflowGeoprocessingRulesEvaluatorTests, self).setUp()

        register_common_mox_dependencies(self.mox)

        self._gp_rules_evaluator = self.mox.CreateMock(GeoprocessingRulesEvaluator)

        self._gp_rules_evaluator._logger = Dependency('FlaskLogger').value
        self._gp_rules_evaluator._main_access = self.mox.CreateMockAnything()
        self._gp_rules_evaluator._main_params = self.mox.CreateMockAnything()
        self._gp_rules_evaluator._main_params.mds = self.mox.CreateMockAnything()
        self._gp_rules_evaluator._main_access.mds = self.mox.CreateMockAnything()
        self._gp_rules_evaluator._main_access.wfs = self.mox.CreateMockAnything()

        self._gp_rules_evaluator._task_id = ObjectId()
        self._gp_rules_evaluator._context = {'user_id': ObjectId(), 'source': '/unit/tests'}
        self._gp_rules_evaluator._entity_id = ObjectId()
        self._gp_rules_evaluator._entity_type = 'store'
        self._gp_rules_evaluator.result = {}
        self._gp_rules_evaluator._entity_ids_to_be_reevaluated = {}
        self._gp_rules_evaluator._bear_flags_asynchronously = True


    def doCleanups(self):

        super(WorkflowGeoprocessingRulesEvaluatorTests, self).doCleanups()
        dependencies.clear()


    # ________________________________________________ run tests _____________________________________________________ #
    def test_run__success(self):

        self._gp_rules_evaluator._update_entity_start()
        self._gp_rules_evaluator._evaluate_rules_for_geoprocessing()
        self._gp_rules_evaluator._evaluate_gp_rules_for_affected_trade_areas()
        self._gp_rules_evaluator._remove_own_flags_if_trade_area()
        self._gp_rules_evaluator._update_entity_end()
        self._gp_rules_evaluator._update_result_end()
        self._gp_rules_evaluator.result = 'result'
        self.mox.ReplayAll()

        result = GeoprocessingRulesEvaluator.run(self._gp_rules_evaluator)

        self.assertEqual('result', result)
        self.assertEqual('success', self._gp_rules_evaluator._status)


    def test_run__fail(self):

        self._gp_rules_evaluator._update_entity_start()
        self._gp_rules_evaluator._evaluate_rules_for_geoprocessing().AndRaise(Exception('There seems to be an issue'))

        self._gp_rules_evaluator._update_entity_end()
        self._gp_rules_evaluator._update_result_end()
        self._gp_rules_evaluator.result = 'result'

        self.mox.ReplayAll()
        try:
            GeoprocessingRulesEvaluator.run(self._gp_rules_evaluator)
        except Exception as e:
            exception = e

        self.assertIn('GeoprocessingRulesEvaluator.run(self._gp_rules_evaluator)', traceback.format_exc())
        self.assertEqual('result', self._gp_rules_evaluator.result)
        self.assertEqual('failed', self._gp_rules_evaluator._status)
        self.assertIn('There seems to be an issue', self._gp_rules_evaluator._exception)


    def test_update_result_end__failed(self):

        start_time = datetime.datetime(2001, 01, 01)

        self._gp_rules_evaluator._status = 'failed'
        self._gp_rules_evaluator._exception = 'exception'
        self._gp_rules_evaluator._start_time = start_time

        end_time = datetime.datetime.utcnow()

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(end_time)

        self.mox.ReplayAll()

        GeoprocessingRulesEvaluator._update_result_end(self._gp_rules_evaluator)

        self.assertEqual({
            'status': 'failed',
            'exception': 'exception',
            'start_time': start_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds()
        }, self._gp_rules_evaluator.result)


    def test_update_result_end__success(self):

        start_time = datetime.datetime(2001, 01, 01)

        self._gp_rules_evaluator._status = 'success'
        self._gp_rules_evaluator._start_time = start_time

        end_time = datetime.datetime.utcnow()

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(end_time)

        self.mox.ReplayAll()

        GeoprocessingRulesEvaluator._update_result_end(self._gp_rules_evaluator)

        self.assertEqual({
            'status': 'success',
            'start_time': start_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds()
        }, self._gp_rules_evaluator.result)


    def test_evaluate_rules_for_geoprocessing(self):

        self.mox.StubOutWithMock(EvaluateNeedForGeoprocessing, 'evaluate_need_for_geoprocessing')

        outcome = {
            'update_query': 'update me',
            'update_operations': 'do these operations',
            'flags': 'so many flags!!'
        }

        EvaluateNeedForGeoprocessing(self._gp_rules_evaluator._entity_type,
                                     self._gp_rules_evaluator._entity_id).evaluate_need_for_geoprocessing().AndReturn(outcome)

        self._gp_rules_evaluator._main_access.mds.call_batch_update_entities('store', 'update me', 'do these operations',
                                                                             self._gp_rules_evaluator._context)

        self._gp_rules_evaluator._bear_flags_to_affected_trade_areas('so many flags!!')
        self.mox.ReplayAll()

        GeoprocessingRulesEvaluator._evaluate_rules_for_geoprocessing(self._gp_rules_evaluator)

        self.assertEqual({
            'flags': 'so many flags!!',
            'update_query': 'update me',
            'update_operations': 'do these operations'
        }, self._gp_rules_evaluator.result)

    def test_group_flags_by_affected_trade_area_id__mixed_case(self):

        trade_area_id_1 = str(ObjectId())
        trade_area_id_2 = str(ObjectId())
        trade_area_id_3 = str(ObjectId())
        trade_area_id_4 = str(ObjectId())
        trade_area_id_5 = str(ObjectId())
        trade_area_id_6 = str(ObjectId())

        flag_1 = {
            "name": "A",
            "affected_trade_area_ids": [trade_area_id_1, trade_area_id_2, trade_area_id_3, trade_area_id_4]
        }

        flag_2 = {
            "name": "B",
            "affected_trade_area_ids": [trade_area_id_2, trade_area_id_3, trade_area_id_4]
        }

        flag_3 = {
            "name": "C",
            "affected_trade_area_ids": [trade_area_id_3, trade_area_id_4, trade_area_id_5, trade_area_id_6]
        }

        flag_4 = {
            "name": "B",
            "affected_trade_area_ids": [trade_area_id_1, trade_area_id_2, trade_area_id_3, trade_area_id_4]
        }

        flag_5 = {
            "name": "A",
            "affected_trade_area_ids": [trade_area_id_2, trade_area_id_3, trade_area_id_4]
        }

        flag_6 = {
            "name": "C",
            "affected_trade_area_ids": [trade_area_id_3, trade_area_id_4, trade_area_id_5, trade_area_id_6]
        }

        flag_7 = {
            "name": "D",
            "affected_trade_area_ids": [trade_area_id_2, trade_area_id_3]
        }

        flags = {
            "get_demographics": [
                flag_1,
                flag_2,
                flag_3
            ],
            "find_competition": [
                flag_4,
                flag_5,
                flag_6,
                flag_7
            ]
        }



        gp_re = GeoprocessingRulesEvaluator({
            "context": "context",
            "entity_id": 42,
            "entity_type": "fake",
            "task_id": 42,
            "bear_flags_asynchronously": False,
            "evaluate_trade_area_rules_asynchronously": False
        })

        # find competition batch updates

        self.mox.StubOutWithMock(gp_re, "_get_affected_trade_area_ids")

        update_query = {'_id': {'$in': [ObjectId(trade_area_id_1), ObjectId(trade_area_id_2), ObjectId(trade_area_id_3), ObjectId(trade_area_id_4)]}}
        update_command = {'$addToSet': {'data.flags.find_competition': 'B'}}
        gp_re._get_affected_trade_area_ids(flag_4['affected_trade_area_ids'], 'find_competition').AndReturn([ObjectId(trade_area_id_1), ObjectId(trade_area_id_2), ObjectId(trade_area_id_3), ObjectId(trade_area_id_4)])
        gp_re._main_access.mds.call_batch_update_entities('trade_area', update_query, update_command, gp_re._context)

        update_query = {'_id': {'$in': [ObjectId(trade_area_id_2), ObjectId(trade_area_id_3), ObjectId(trade_area_id_4)]}}
        update_command = {'$addToSet': {'data.flags.find_competition': 'A'}}
        gp_re._get_affected_trade_area_ids(flag_5['affected_trade_area_ids'], 'find_competition').AndReturn([ObjectId(trade_area_id_2), ObjectId(trade_area_id_3), ObjectId(trade_area_id_4)])
        gp_re._main_access.mds.call_batch_update_entities('trade_area', update_query, update_command, gp_re._context)

        update_query = {'_id': {'$in': [ObjectId(trade_area_id_3), ObjectId(trade_area_id_4), ObjectId(trade_area_id_5), ObjectId(trade_area_id_6)]}}
        update_command = {'$addToSet': {'data.flags.find_competition': 'C'}}
        gp_re._get_affected_trade_area_ids(flag_6['affected_trade_area_ids'], 'find_competition').AndReturn([ObjectId(trade_area_id_3), ObjectId(trade_area_id_4), ObjectId(trade_area_id_5), ObjectId(trade_area_id_6)])
        gp_re._main_access.mds.call_batch_update_entities('trade_area', update_query, update_command, gp_re._context)

        update_query = {'_id': {'$in': [ObjectId(trade_area_id_2), ObjectId(trade_area_id_3)]}}
        update_command = {'$addToSet': {'data.flags.find_competition': 'D'}}
        gp_re._get_affected_trade_area_ids(flag_7['affected_trade_area_ids'], 'find_competition').AndReturn([ObjectId(trade_area_id_2), ObjectId(trade_area_id_3)])
        gp_re._main_access.mds.call_batch_update_entities('trade_area', update_query, update_command, gp_re._context)

        # get demographics batch updates

        update_query = {'_id': {'$in': [ObjectId(trade_area_id_1), ObjectId(trade_area_id_2), ObjectId(trade_area_id_3), ObjectId(trade_area_id_4)]}}
        update_command = {'$addToSet': {'data.flags.get_demographics': 'A'}}
        gp_re._get_affected_trade_area_ids(flag_1['affected_trade_area_ids'], 'get_demographics').AndReturn([ObjectId(trade_area_id_1), ObjectId(trade_area_id_2), ObjectId(trade_area_id_3), ObjectId(trade_area_id_4)])
        gp_re._main_access.mds.call_batch_update_entities('trade_area', update_query, update_command, gp_re._context)

        update_query = {'_id': {'$in': [ObjectId(trade_area_id_2), ObjectId(trade_area_id_3), ObjectId(trade_area_id_4)]}}
        update_command = {'$addToSet': {'data.flags.get_demographics': 'B'}}
        gp_re._get_affected_trade_area_ids(flag_2['affected_trade_area_ids'], 'get_demographics').AndReturn([ObjectId(trade_area_id_2), ObjectId(trade_area_id_3), ObjectId(trade_area_id_4)])
        gp_re._main_access.mds.call_batch_update_entities('trade_area', update_query, update_command, gp_re._context)

        update_query = {'_id': {'$in': [ObjectId(trade_area_id_3), ObjectId(trade_area_id_4), ObjectId(trade_area_id_5), ObjectId(trade_area_id_6)]}}
        update_command = {'$addToSet': {'data.flags.get_demographics': 'C'}}
        gp_re._get_affected_trade_area_ids(flag_3['affected_trade_area_ids'], 'get_demographics').AndReturn([ObjectId(trade_area_id_3), ObjectId(trade_area_id_4), ObjectId(trade_area_id_5), ObjectId(trade_area_id_6)])
        gp_re._main_access.mds.call_batch_update_entities('trade_area', update_query, update_command, gp_re._context)


        self.mox.ReplayAll()

        gp_re._bear_flags_to_affected_trade_areas(flags)

        self.assertEqual([trade_area_id_1, trade_area_id_2, trade_area_id_3, trade_area_id_4, trade_area_id_5, trade_area_id_6], sorted(gp_re._trade_areas_to_reevaluate))


    def test_get_affected_trade_area_ids__one_flag_all_ta(self):

        register_common_mox_dependencies(self.mox)

        input_rec = {
            'entity_type': 'store',
            'entity_id': 'bob',
            'context': {
                'user_id': 42,
                'source': 'unit_tests'
            },
            'task_id': 42,
            'bear_flags_asynchronously': False,
            'evaluate_trade_area_rules_asynchronously': False
        }

        gre = GeoprocessingRulesEvaluator(input_rec)

        flag = {'affected_trade_area_ids': '_all_child_trade_areas'}



        ta_id_1 = ObjectId()
        ta_id_2 = ObjectId()
        ta_id_3 = ObjectId()

        gp_method = 'booyakasha'

        expected_params = {'query': {'$or': [
            {'data.geoprocessing.needs_gp.%s' % gp_method: False},
            {'data.geoprocessing.needs_gp.%s' % gp_method: {'$exists': False}}
        ], 'data.store_id': 'bob'}}

        ta_rec_1 = {
            '_id': ta_id_1,
            'data': {
                'geoprocessing': {
                    'needs_gp': {
                        gp_method: False
                    }
                }
            }
        }

        ta_rec_2 = {
            '_id': ta_id_2,
            'data': {
                'geoprocessing': {
                    'needs_gp': {
                        gp_method: False
                    }
                }
            }
        }

        ta_rec_3 = {
            '_id': ta_id_3,
            'data': {
                'geoprocessing': {
                    'needs_gp': {
                        gp_method: False
                    }
                }
            }
        }

        gre._main_access.mds.call_find_entities_raw('trade_area', expected_params).AndReturn([ta_rec_1, ta_rec_2, ta_rec_3])

        self.mox.ReplayAll()

        affected_trade_area_ids = gre._get_affected_trade_area_ids(flag['affected_trade_area_ids'], gp_method)

        expected_affected_trade_area_ids = [ta_id_1, ta_id_2, ta_id_3]

        self.assertEqual(expected_affected_trade_area_ids, affected_trade_area_ids)

    def test_get_affected_trade_area_ids__one_flag_all_ta__industry(self):

        register_common_mox_dependencies(self.mox)

        input_rec = {
            'entity_type': 'industry',
            'entity_id': 'bob',
            'context': {
                'user_id': 42,
                'source': 'unit_tests'
            },
            'task_id': 42,
            'bear_flags_asynchronously': False,
            'evaluate_trade_area_rules_asynchronously': False
        }

        gre = GeoprocessingRulesEvaluator(input_rec)

        flag = {'affected_trade_area_ids': '_all_child_trade_areas'}

        gp_method = 'bob_method'

        expected_params = {'query': {'$or': [
            {'data.geoprocessing.needs_gp.%s' % gp_method: False},
            {'data.geoprocessing.needs_gp.%s' % gp_method: {'$exists': False}}
        ], 'data.company_id': {'$in': [11, 22, 33]}}}

        self.mox.StubOutWithMock(industry_helper, 'get_company_ids_by_primary_industry_id')
        industry_helper.get_company_ids_by_primary_industry_id('bob').AndReturn([11, 22, 33])


        ta_id_1 = ObjectId()
        ta_id_2 = ObjectId()
        ta_id_3 = ObjectId()

        gre._main_access.mds.call_find_entities_raw('trade_area', expected_params).AndReturn([{'_id': ta_id_1}, {'_id': ta_id_2}, {'_id': ta_id_3}])

        self.mox.ReplayAll()

        affected_trade_area_ids = gre._get_affected_trade_area_ids(flag['affected_trade_area_ids'], gp_method)

        expected_affected_trade_area_ids = [ta_id_1, ta_id_2, ta_id_3]

        self.assertEqual(expected_affected_trade_area_ids, affected_trade_area_ids)




