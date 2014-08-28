from core.service.svc_analytics.implementation.calc.engines.stores.store_count import StoreCount
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from common.utilities.date_utilities import FastDateParser, LAST_ANALYTICS_DATE
from common.utilities.time_series import TIME_SERIES_START, get_monthly_time_series
from bson.objectid import ObjectId
import unittest
import datetime
import mox


__author__ = 'vgold'


class StoreCountTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(StoreCountTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.maxDiff = None

    def doCleanups(self):

        super(StoreCountTests, self).doCleanups()
        dependencies.clear()

    def test_calculate(self):

        # Make an instance without pesky __init__
        calc_engine = StoreCount.__new__(StoreCount)
        calc_engine.date_parser = FastDateParser()
        calc_engine.input = {
            "entity_type": "store",
            "target_entity_field": "target_entity_field"
        }
        calc_engine.output = {
            "target_entity_type": "company"
        }

        calc_engine.main_access = self.mox.CreateMockAnything()
        calc_engine.main_access.mds = self.mox.CreateMockAnything()

        calc_engine.child_to_parent_dict = None

        banner_id = ObjectId()

        calc_engine.banner_ids = [str(banner_id)]
        calc_engine.run_params = {
            "target_entity_ids": calc_engine.banner_ids
        }

        calc_engine.company_operating_dict = {
            banner_id: "operating"
        }

        for i, month in enumerate(get_monthly_time_series(TIME_SERIES_START, end=LAST_ANALYTICS_DATE)):

            if i == 0:
                results = [
                    {
                        "_id": str(banner_id),
                        "store_count": 3
                    }
                ]
            else:
                results = []

            calc_engine.main_access.mds.call_aggregate_entities(calc_engine.input['entity_type'],
                                                                mox.IgnoreArg()).AndReturn(results)

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

    def test_calculate__out_of_business(self):

        # Make an instance without pesky __init__
        calc_engine = StoreCount.__new__(StoreCount)
        calc_engine.date_parser = FastDateParser()
        calc_engine.input = {
            "entity_type": "store",
            "target_entity_field": "target_entity_field"
        }
        calc_engine.output = {
            "target_entity_type": "company"
        }

        calc_engine.main_access = self.mox.CreateMockAnything()
        calc_engine.main_access.mds = self.mox.CreateMockAnything()

        calc_engine.child_to_parent_dict = None

        banner_id = ObjectId()

        calc_engine.banner_ids = [str(banner_id)]
        calc_engine.run_params = {
            "target_entity_ids": calc_engine.banner_ids
        }

        calc_engine.company_operating_dict = {
            banner_id: "out_of_business"
        }

        for i, month in enumerate(get_monthly_time_series(TIME_SERIES_START, end=LAST_ANALYTICS_DATE)):

            if i == 3:
                results = [
                    {
                        "_id": str(banner_id),
                        "store_count": 3
                    }
                ]
            else:
                results = []

            calc_engine.main_access.mds.call_aggregate_entities(calc_engine.input['entity_type'],
                                                                mox.IgnoreArg()).AndReturn(results)

        self.mox.ReplayAll()

        # Do maths
        calc_engine._calculate()

        expected_result = {
            str(banner_id): []
        }

        for i, month in enumerate(get_monthly_time_series(TIME_SERIES_START, end=LAST_ANALYTICS_DATE)):
            if i == 3:
                expected_result[str(banner_id)].append({
                    "date": month,
                    "value": 3
                })
            elif i > 3:
                expected_result[str(banner_id)].append({
                    "date": month,
                    "value": 0
                })

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate_parent(self):

        # Make an instance without pesky __init__
        calc_engine = StoreCount.__new__(StoreCount)
        calc_engine.date_parser = FastDateParser()
        calc_engine.input = {
            "churn_type": "openings",
            "entity_type": "store",
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

        calc_engine.company_operating_dict = {
            parent_id: "operating"
        }

        for i, month in enumerate(get_monthly_time_series(TIME_SERIES_START, end=LAST_ANALYTICS_DATE)):

            if i == 0:
                results = [
                    {
                        "_id": str(banner_id1),
                        "store_count": 3
                    },
                    {
                        "_id": str(banner_id2),
                        "store_count": 3
                    }
                ]
            else:
                results = []

            calc_engine.main_access.mds.call_aggregate_entities(calc_engine.input['entity_type'],
                                                                mox.IgnoreArg()).AndReturn(results)

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