import pprint
from common.utilities.time_series import TIME_SERIES_START, get_monthly_time_series
from core.service.svc_analytics.implementation.calc.engines.stores.store_churn import StoreChurn
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from common.utilities.date_utilities import FastDateParser, LAST_ANALYTICS_DATE
from bson.objectid import ObjectId
import unittest
import mox
import datetime


__author__ = 'vgold'


class StoreChurnTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(StoreChurnTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.maxDiff = None

    def doCleanups(self):

        super(StoreChurnTests, self).doCleanups()
        dependencies.clear()

    def test_calculate(self):

        # Make an instance without pesky __init__
        calc_engine = StoreChurn.__new__(StoreChurn)
        calc_engine.date_parser = FastDateParser()
        calc_engine.input = {
            "churn_type": "openings",
            "entity_type": "trade_area",
            "target_entity_field": "target_entity_field"
        }
        calc_engine.output = {
            "target_entity_type": "company"
        }

        calc_engine.main_access = self.mox.CreateMockAnything()
        calc_engine.main_access.mds = self.mox.CreateMockAnything()
        calc_engine.main_param = self.mox.CreateMockAnything()
        calc_engine.main_param.mds = self.mox.CreateMockAnything()

        calc_engine.child_to_parent_dict = None

        banner_id = ObjectId()

        calc_engine.banner_ids = [str(banner_id)]
        calc_engine.run_params = {
            "target_entity_ids": calc_engine.banner_ids
        }

        now = datetime.datetime.utcnow()

        entity_intervals = [
            [banner_id, [LAST_ANALYTICS_DATE.isoformat(), (LAST_ANALYTICS_DATE + datetime.timedelta(microseconds=1)).isoformat()]]
        ]

        params = "params"
        calc_engine.main_param.mds.create_params(resource="find_entities_raw", query=mox.IgnoreArg(),
                                                 entity_fields=mox.IgnoreArg(),
                                                 as_list=True).AndReturn({"params": params})
        calc_engine.main_access.mds.call_find_entities_raw(calc_engine.output['target_entity_type'],
                                                           params).AndReturn(entity_intervals)

        results = [
            {
                "_id": str(banner_id),
                "store_count": 3
            }
        ]

        calc_engine.main_access.mds.call_aggregate_entities(calc_engine.input['entity_type'], mox.IgnoreArg(),
                                                            timeout=900).AndReturn(results)

        self.mox.ReplayAll()

        # Do maths
        calc_engine._calculate()

        expected_result = {
            str(banner_id): [
                {
                    'date': LAST_ANALYTICS_DATE,
                    'value': 3,
                }
            ]
        }

        for month in get_monthly_time_series(TIME_SERIES_START, end=LAST_ANALYTICS_DATE)[1:]:
            expected_result[str(banner_id)].append({
                "date": month,
                "value": 0
            })

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate_parent(self):

        # Make an instance without pesky __init__
        calc_engine = StoreChurn.__new__(StoreChurn)
        calc_engine.date_parser = FastDateParser()
        calc_engine.input = {
            "churn_type": "openings",
            "entity_type": "trade_area",
            "target_entity_field": "target_entity_field"
        }
        calc_engine.output = {
            "target_entity_type": "company"
        }

        calc_engine.main_access = self.mox.CreateMockAnything()
        calc_engine.main_access.mds = self.mox.CreateMockAnything()
        calc_engine.main_param = self.mox.CreateMockAnything()
        calc_engine.main_param.mds = self.mox.CreateMockAnything()

        parent_id = ObjectId()
        banner_id1 = ObjectId()
        banner_id2 = ObjectId()

        calc_engine.child_to_parent_dict = {
            str(banner_id1): str(parent_id),
            str(banner_id2): str(parent_id)
        }

        calc_engine.banner_ids = [str(banner_id1), str(banner_id2)]
        calc_engine.run_params = {
            "target_entity_ids": [str(parent_id)]
        }

        now = datetime.datetime.utcnow()

        entity_intervals = [
            [banner_id1, [LAST_ANALYTICS_DATE.isoformat(), (LAST_ANALYTICS_DATE + datetime.timedelta(microseconds=1)).isoformat()]],
            [banner_id2, [LAST_ANALYTICS_DATE.isoformat(), (LAST_ANALYTICS_DATE + datetime.timedelta(microseconds=1)).isoformat()]]
        ]

        params = "params"
        calc_engine.main_param.mds.create_params(resource="find_entities_raw", query=mox.IgnoreArg(),
                                                 entity_fields=mox.IgnoreArg(),
                                                 as_list=True).AndReturn({"params": params})
        calc_engine.main_access.mds.call_find_entities_raw(calc_engine.output['target_entity_type'],
                                                           params).AndReturn(entity_intervals)

        results = [
            {
                "_id": str(banner_id1),
                "store_count": 3
            }
        ]

        calc_engine.main_access.mds.call_aggregate_entities(calc_engine.input['entity_type'], mox.IgnoreArg(),
                                                            timeout=900).AndReturn(results)

        results = [
            {
                "_id": str(banner_id2),
                "store_count": 3
            }
        ]

        calc_engine.main_access.mds.call_aggregate_entities(calc_engine.input['entity_type'], mox.IgnoreArg(),
                                                            timeout=900).AndReturn(results)

        self.mox.ReplayAll()

        # Do maths
        calc_engine._calculate()

        expected_result = {
            str(parent_id): [
                {
                    'date': LAST_ANALYTICS_DATE,
                    'value': 6,
                }
            ]
        }

        for month in get_monthly_time_series(TIME_SERIES_START, end=LAST_ANALYTICS_DATE)[1:]:
            expected_result[str(parent_id)].append({
                "date": month,
                "value": 0
            })

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()