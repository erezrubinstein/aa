from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
import unittest
import mox
from core.service.svc_analytics.implementation.calc.engines.retailer_transactions.aggregate_transactions_per_customer import AggregateTransactionsPerCustomer


class AggregateTransactionsPerCustomerTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AggregateTransactionsPerCustomerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)
        self.mock = self.mox.CreateMock(AggregateTransactionsPerCustomer)
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value
        self.mock.main_access = Dependency("CoreAPIProvider").value
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.context = {
            "the": "context"
        }

        self.mock.map = """function() {
                        var value = {
                            "count": 1,
                            "sum": this.data.sales,
                            "min": this.data.sales,
                            "max": this.data.sales
                        };
                        emit(this.data.customer_id, value);
                    }"""

        self.mock.reduce = """function(key, values) {
                        var result = {
                                "count": 0,
                                "sum": 0,
                                "min": values[0].min,
                                "max": values[0].max
                            };
                        values.forEach(function(v){
                            result.count += v.count;
                            result.sum += v.sum;
                            if (v.min < result.min) {
                                result.min = v.min;
                            }
                            if (v.max > result.max) {
                                result.max = v.max;
                            }
                        });
                        return result;
                    }"""

        self.mock.finalize = """function(key, reduced) {
                            reduced.avg = reduced.sum / reduced.count;
                            reduced.count = NumberInt(reduced.count);
                            return reduced;
                        }"""

        self.maxDiff = None


    def doCleanups(self):
        super(AggregateTransactionsPerCustomerTests, self).doCleanups()
        dependencies.clear()


    def test_calculate_per_customer(self):
        self.mock.input = {
            "entity_type": "et"
        }
        self.mock.output = {}

        # begin recording
        self.mock.out = [("replace", "ltmTrxPerCustomer"), ("db", "map_reduce")]
        self.mock.query = "query"
        self.mock._build_query()
        self.mock.main_access.mds.call_map_reduce("et", self.mock.map, self.mock.reduce, self.mock.out,
                                                  finalize=self.mock.finalize, query=self.mock.query)

        # replay all
        self.mox.ReplayAll()

        AggregateTransactionsPerCustomer._calculate(self.mock)



if __name__ == '__main__':
    unittest.main()