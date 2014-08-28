# coding=utf-8
from core.service.svc_analytics.implementation.calc.engines.demographics.trade_area_aggregate_income import TradeAreaAggregateIncome
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import ANALYTICS_TARGET_YEAR
import unittest
import mox


class TradeAreaAggregateIncomeTests(mox.MoxTestBase):
    def setUp(self):
        super(TradeAreaAggregateIncomeTests, self).setUp()
        register_common_mox_dependencies(self.mox)

        # instantiate calc engine without init
        self.engine = TradeAreaAggregateIncome.__new__(TradeAreaAggregateIncome)


    def test_calculate(self):

        self.engine.output = {
            "description": "Aggregate Income"
        }

        # Some test fetched data
        self.engine.fetched_data = [
            [
                "test1",
                1000,
                3,
                ANALYTICS_TARGET_YEAR
            ],
            [
                "test2",
                2000,
                4,
                2012
            ]
        ]

        self.engine._calculate()

        self.assertEqual(3000, self.engine.results["test1"]["value"])
        self.assertEqual(ANALYTICS_TARGET_YEAR, self.engine.results["test1"]["target_year"])
        self.assertEqual("Aggregate Income", self.engine.results["test1"]["description"])

        self.assertEqual(8000, self.engine.results["test2"]["value"])
        self.assertEqual(2012, self.engine.results["test2"]["target_year"])
        self.assertEqual("Aggregate Income", self.engine.results["test2"]["description"])


if __name__ == '__main__':
    unittest.main()
