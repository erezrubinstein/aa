import datetime
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.errors import BadRequestError
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.calc_engine import CalcEngine
import unittest
import mox


__author__ = 'vgold'


class CalcEngineTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(CalcEngineTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on instance for calls to record
        self.mock = self.mox.CreateMock(CalcEngine)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_param.mds = self.mox.CreateMockAnything()

        self.mock.context = self.context = {"stuff": True}

    def doCleanups(self):

        super(CalcEngineTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # CalcEngine._validate_calc_params()

    def test_validate_calc_params__no_save_or_save_with_overwrite(self):

        engine = CalcEngine.__new__(CalcEngine)

        engine.output = {
            "key": "asdf"
        }

        entity_id1 = generate_id()
        entity_id2 = generate_id()

        engine.run_params = {
            "target_entity_ids": [entity_id1, entity_id2],
            "target_entity_type": "steam",
            "options": {
                "save": True,
                "overwrite": True
            }
        }

        engine._validate_calc_params()

        engine.run_params = {
            "target_entity_ids": [entity_id1, entity_id2],
            "target_entity_type": "steam",
            "options": {
                "save": False,
                "overwrite": True
            }
        }

        engine._validate_calc_params()

        engine.run_params = {
            "target_entity_ids": [entity_id1, entity_id2],
            "target_entity_type": "steam",
            "options": {
                "save": False,
                "overwrite": False
            }
        }

        engine._validate_calc_params()

    def test_validate_calc_params__no_overwrite__no_existing_data(self):

        entity_id1 = generate_id()
        entity_id2 = generate_id()

        self.mock.run_params = {
            "target_entity_ids": [entity_id1, entity_id2],
            "target_entity_type": "steam",
            "options": {
                "save": True,
                "overwrite": False
            }
        }

        self.mock.output = {
            "key": "asdf"
        }

        params = "params"
        self.mock.main_param.mds.create_params(resource="find_entities_raw", query=mox.IgnoreArg(),
                                               entity_fields=mox.IgnoreArg(), as_list=True).AndReturn({"params": params})

        data = [
            [entity_id1, None],
            [entity_id2, None]
        ]
        self.mock.main_access.mds.call_find_entities_raw(self.mock.run_params["target_entity_type"],
                                                         params, self.context).AndReturn(data)

        self.mox.ReplayAll()
        CalcEngine._validate_calc_params(self.mock)

    def test_validate_calc_params__no_overwrite__existing_data(self):

        entity_id1 = generate_id()
        entity_id2 = generate_id()

        self.mock.run_params = {
            "target_entity_ids": [entity_id1, entity_id2],
            "target_entity_type": "steam",
            "options": {
                "save": True,
                "overwrite": False
            }
        }

        self.mock.output = {
            "key": "asdf"
        }

        params = "params"
        self.mock.main_param.mds.create_params(resource="find_entities_raw", query=mox.IgnoreArg(),
                                               entity_fields=mox.IgnoreArg(), as_list=True).AndReturn({"params": params})

        data = [
            [entity_id1, None],
            [entity_id2, 1]
        ]
        self.mock.main_access.mds.call_find_entities_raw(self.mock.run_params["target_entity_type"],
                                                         params, self.context).AndReturn(data)

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            CalcEngine._validate_calc_params(self.mock)

    ##########################################################################
    # CalcEngine._fetch()

    def test_fetch(self):

        entity_id1 = generate_id()
        entity_id2 = generate_id()

        self.mock.run_params = {
            "target_entity_ids": [entity_id1, entity_id2],
            "target_entity_type": "steam",
            "options": {
                "fetch": True
            }
        }

        self.mock.input = {
            "target_entity_field": "steam.punk.engine.yo",
            "entity_type": "punk",
            "entity_query": "{}",
            "fields": ["_id", ]
        }

        params = {}
        self.mock.main_param.mds.create_params(resource="find_entities_raw", query=mox.IgnoreArg(), sort=None,
                                               entity_fields=mox.IgnoreArg(), as_list=True, fields_to_flatten = None).AndReturn({"params": params})

        expected_fetched_data = [
            [entity_id1, None],
            [entity_id2, 1]
        ]
        self.mock.main_access.mds.call_find_entities_raw("punk", mox.IgnoreArg(), self.context, timeout=240,
                                                         encode_and_decode_results=False).AndReturn(expected_fetched_data)

        self.mox.ReplayAll()
        CalcEngine._fetch(self.mock)

        self.assertEqual(expected_fetched_data, self.mock.fetched_data)

    ##########################################################################
    # CalcEngine._save()

    def test_save(self):

        entity_id1 = generate_id()

        self.mock.results = {
            entity_id1: {
                "results": 1
            }
        }

        self.mock.run_params = {
            "target_entity_type": "steam",
            "options": {
                "save": True
            }
        }

        self.mock.output = {
            "key": "coal"
        }

        field_data = {
            "coal": self.mock.results[entity_id1]
        }
        operations = [
            {
                "query": {"_id": entity_id1},
                "operations": {"$set": field_data}
            }
        ]
        self.mock._update_entities("steam", operations, None)

        self.mox.ReplayAll()
        CalcEngine._save(self.mock)

    ##########################################################################
    # CalcEngine._update_entities()

    def test_update_entities(self):

        entity_id1 = generate_id()

        self.mock.results = {
            entity_id1: {
                "results": 1
            }
        }

        self.mock.output = {
            "key": "coal"
        }

        operations = [
            {
                "query": {"_id": entity_id1},
                "operations": {"$set": {"asdf": "asdf"}}
            }
        ]
        self.mock.main_access.mds.call_multi_batch_update_entities("steam", operations, self.context, timeout=None,
                                                                   force_skip_meta=True, use_new_json_encoder=True)

        self.mox.ReplayAll()
        CalcEngine._update_entities(self.mock, "steam", operations, None)

    ##########################################################################
    # CalcEngine._end_calc()

    def test_end_calc__success(self):

        self.mock.start_time = datetime.datetime(2012, 1, 1)
        end_time = datetime.datetime(2012, 1, 2)

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(end_time)

        self.mox.ReplayAll()
        CalcEngine._end_calc(self.mock)

        self.assertEqual(self.mock.status, "success")
        self.assertEqual(self.mock.end_time, end_time)

    def test_end_calc__failure(self):

        self.mock.start_time = datetime.datetime(2012, 1, 1)
        end_time = datetime.datetime(2012, 1, 2)

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(end_time)

        self.mox.ReplayAll()
        CalcEngine._end_calc(self.mock, "asdf")

        self.assertEqual(self.mock.status, "failure")
        self.assertEqual(self.mock.end_time, end_time)


if __name__ == '__main__':
    unittest.main()
