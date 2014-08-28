import json
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.service.svc_analytics.implementation.calc.engines.retailer_transactions.aggregate_transactions_per_customer import AggregateTransactionsPerCustomer
from core.service.svc_analytics.implementation.calc.retailer_transaction_calc_engine_map_reduce import RetailerTransactionCalcEngineMapReduce
from core.service.svc_analytics.implementation.calc.calc_engine import CalcEngine
from retailer.common import ltm_helper
from bson.objectid import ObjectId
import unittest
import mox
import datetime


class AggregateTransactionsCalcEngineMapReduceTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AggregateTransactionsCalcEngineMapReduceTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)
        self.mock = self.mox.CreateMock(AggregateTransactionsPerCustomer)
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value
        self.mock.main_access = Dependency("CoreAPIProvider").value
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.context = {
            "the": "context"
        }

        self.maxDiff = None


    def doCleanups(self):
        super(AggregateTransactionsCalcEngineMapReduceTests, self).doCleanups()
        dependencies.clear()

    def test_validate_calc_params__normal(self):

        self.mock.retailer_client_id = 'rci'
        self.mock.run_params = {
            "entity_query": '{"cat": "coffee"}',
            "options": {"save":True, "overwrite":True}
        }
        self.mock.map = "a map function"
        self.mock.reduce = "a reduce function"
        self.mock.output = {
            "map_reduce_output_db": "jo mamma",
            "map_reduce_output_collection_stub": "so I says to Sally I says",
            "target_entity_type": "snow peas"
        }
        self.mock.calc_id = ObjectId()

        # begin recording
        self.mock._validate_and_set_retailer_client_id().AndReturn(None)
        CalcEngine._validate_calc_params(self.mock)

         # replay all
        self.mox.ReplayAll()

        RetailerTransactionCalcEngineMapReduce._validate_calc_params(self.mock)

        # assert yourself!
        self.assertEqual(self.mock.entity_type, "snow peas")

        # this is the map reduce parameters (aside from map, reduce, and finalize)
        output_collection_stub = self.mock.output["map_reduce_output_collection_stub"]
        output_collection = "{0}_{1}".format(output_collection_stub, self.mock.calc_id)
        output_db = self.mock.output["map_reduce_output_db"]
        output_action = self.mock.output.get("map_reduce_output_action", "replace")
        expected_out = [(output_action, output_collection), ("db", output_db)]
        self.assertEqual(self.mock.out, expected_out)

        #this should have been json decoded here
        self.assertEqual(self.mock.entity_query, {"cat": "coffee"})


    def test_build_match_query__normal_ltm(self):
        self.mock.retailer_client_id = 'rci'
        self.mock.entity_query = {"cat": "coffee"}
        self.mock.run_params = {}

        now = datetime.datetime.now()

        # begin recording
        self.mox.StubOutWithMock(ltm_helper, "get_default_ltm_end_date")
        ltm_helper.get_default_ltm_end_date(self.mock.context, self.mock.retailer_client_id).AndReturn(now)

        # replay all
        self.mox.ReplayAll()

        RetailerTransactionCalcEngineMapReduce._build_query(self.mock)

        expected = {
            "data.retailer_client_id": "rci",
            "data.transaction_date": {
                "$gte": now - datetime.timedelta(days=364),
                "$lte": now
            },
            "cat": "coffee"
        }

        self.assertEqual(self.mock.query, expected)


    def test_build_match_query__custom_time_interval(self):
        self.mock.input = {}
        self.mock.run_params = {
            "custom_time_interval": ['t0', 't1']
        }
        self.mock.retailer_client_id = "rci"
        self.mock.entity_query = None

        # begin recording


        # replay all
        self.mox.ReplayAll()

        RetailerTransactionCalcEngineMapReduce._build_query(self.mock)

        expected = {
            "data.retailer_client_id": "rci",
            "data.transaction_date": {
                "$gte": "t0",
                "$lte": "t1"
            }
        }

        self.assertEqual(self.mock.query, expected)


    def test_calculate(self):
        self.mock.input = {
            "entity_type": "et"
        }
        self.mock.output = {}
        self.mock.map = "map"
        self.mock.reduce = "reduce"
        self.mock.finalize = "finalize"

        # begin recording
        self.mock.out = [("replace", "ltmTrxPerCustomer"), ("db", "map_reduce")]
        self.mock.query = "query"

        self.mock._build_query()
        self.mock.main_access.mds.call_map_reduce("et", self.mock.map, self.mock.reduce, self.mock.out,
                                                  finalize=self.mock.finalize, query=self.mock.query)

        # replay all
        self.mox.ReplayAll()

        RetailerTransactionCalcEngineMapReduce._calculate(self.mock)


if __name__ == '__main__':
    unittest.main()