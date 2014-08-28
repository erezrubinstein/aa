
from common.helpers.common_dependency_helper\
    import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency
from core.service.svc_analytics.implementation.calc.engines.stores.\
    store_growth import StoreGrowth
import datetime
import unittest
import mox
from copy import deepcopy


class MonthlyStoreGrowthTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(MonthlyStoreGrowthTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)
        self.engine = StoreGrowth.__new__(StoreGrowth)
        self.mox.StubOutWithMock(StoreGrowth, "_fetch")

        self.data = [
            {
                "date": 'foo',
                "value": 6
            },
            {
                "date": 'bar',
                "value": 4
            },
            {
                "date": 'baz',
                "value": 2
            }
        ]

        self.expected = [
            {
                "date": 'foo',
                "value": 0.5
            },
            {
                "date": 'bar',
                "value": 1.0
            }
        ]

        self.engine.run_params = {
            "save": False,
            "return": True,
        }

    def test_calculate(self):

        self.engine.run_params['target_entity_ids'] = ['noob']
        self.engine.fetched_data = [['noob', self.data]]

        expected_results = {
            'noob': self.expected
        }

        self.engine._calculate()
        self.assertEqual(self.engine.results,  expected_results)

    def test_calculate_with_multiple_ids(self):

        self.engine.run_params['target_entity_ids'] = ['noob', 'boon']

        self.engine.fetched_data = [['noob', deepcopy(self.data)],
                                    ['boon', deepcopy(self.data)]]

        expected_results = {
            'noob': self.expected,
            'boon': self.expected
        }

        self.engine._calculate()
        self.assertEqual(self.engine.results,  expected_results)

if __name__ == '__main__':
    unittest.main()
