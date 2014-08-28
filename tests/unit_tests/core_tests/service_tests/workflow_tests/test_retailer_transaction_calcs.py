import json
import mox
from mox import IsA
import unittest
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.errors import BadRequestError
from core.service.svc_workflow.implementation.task.implementation.retailer_tasks.retailer_transaction_calcs import RetailerTransactionCalcs


__author__ = 'jsternberg'


class TestRetailerTransactionCalcs(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestRetailerTransactionCalcs, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_logger = Dependency("FlaskLogger").value

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.input_rec = {
            "task_id": "cheeese",
            "retailer_client_id": 42,
            "context": self.context
        }


    def test_get_calcs_to_run__no_transactions_query(self):

        # create company deletion object
        self.retailer_trans_calc_task = RetailerTransactionCalcs(self.input_rec)

        # we expect a call to analytics to find calcs
        mock_calc_records = ["earmuffs", "FRANK THE TANK"]
        self.mock_main_access.analytics.call_find_calcs_ordered(self.context, timeout=IsA(int),
                                                                engines=["retailer_transactions"]).AndReturn(mock_calc_records)

        self.mox.ReplayAll()

        self.retailer_trans_calc_task._get_calcs_to_run()

        expected_calc_run_params = {
            "wfs_task_id": self.input_rec["task_id"],
            "retailer_client_id": self.input_rec["retailer_client_id"],
            "options": {
                "fetch": False,
                "save": True,
                "return": False,
                "update_workflow": True
            }
        }

        self.assertEqual(self.retailer_trans_calc_task.calc_run_params, expected_calc_run_params)
        self.assertEqual(self.retailer_trans_calc_task.calc_runs, [])


    def test_get_calcs_to_run__good_transactions_query(self):

        # create company deletion object
        self.input_rec["transactions_query"] = json.dumps({"blue": "you're my boy"})
        self.retailer_trans_calc_task = RetailerTransactionCalcs(self.input_rec)

        # we expect a call to analytics to find calcs
        mock_calc_records = ["earmuffs", "FRANK THE TANK"]
        self.mock_main_access.analytics.call_find_calcs_ordered(self.context, timeout=IsA(int),
                                                                engines=["retailer_transactions"]).AndReturn(mock_calc_records)

        self.mox.ReplayAll()

        self.retailer_trans_calc_task._get_calcs_to_run()

        expected_calc_run_params = {
            "wfs_task_id": self.input_rec["task_id"],
            "retailer_client_id": self.input_rec["retailer_client_id"],
            "entity_query": self.input_rec["transactions_query"],
            "options": {
                "fetch": False,
                "save": True,
                "return": False,
                "update_workflow": True
            }
        }

        self.assertEqual(self.retailer_trans_calc_task.decoded_transactions_query, {"blue": "you're my boy"})
        self.assertEqual(self.retailer_trans_calc_task.calc_run_params, expected_calc_run_params)
        self.assertEqual(self.retailer_trans_calc_task.calc_runs, [])


    def test_get_calcs_to_run__bad_transactions_query(self):

        # create company deletion object
        # make query a regular dict, not a json encoded dict
        transactions_query = {"blue": "you're my boy"}
        self.input_rec["transactions_query"] = transactions_query
        self.retailer_trans_calc_task = RetailerTransactionCalcs(self.input_rec)

        # we expect a call to analytics to find calcs
        mock_calc_records = ["earmuffs", "FRANK THE TANK"]
        self.mock_main_access.analytics.call_find_calcs_ordered(self.context, timeout=IsA(int),
                                                                engines=["retailer_transactions"]).AndReturn(mock_calc_records)

        self.mox.ReplayAll()

        expected_error_message = "RetailerTransactionCalcs - 'transactions_query' must be a json encoded dict. " \
                                 "Received: %s" % str(transactions_query)

        with self.assertRaises(BadRequestError) as cm:
            self.retailer_trans_calc_task._get_calcs_to_run()

        self.assertEqual(self.retailer_trans_calc_task.decoded_transactions_query, None)
        self.assertEqual(cm.exception.message, expected_error_message)
        self.assertIsNone(self.retailer_trans_calc_task.calc_runs)


    def test_get_calcs_to_run__specific_entity_type(self):

        # create company deletion object
        self.input_rec["entity_type"] = "phat beats"
        self.retailer_trans_calc_task = RetailerTransactionCalcs(self.input_rec)

        # we expect a call to analytics to find calcs
        mock_calc_records = [{"name":"snoop", "output":{"target_entity_type": "mad rhymes"}},
                             {"name":"dre", "output":{"target_entity_type": "phat beats"}},]
        self.mock_main_access.analytics.call_find_calcs_ordered(self.context, timeout=IsA(int),
                                                                engines=["retailer_transactions"]).AndReturn(mock_calc_records)

        self.mox.ReplayAll()

        self.retailer_trans_calc_task._get_calcs_to_run()

        expected_calc_records = [{"name":"dre", "output":{"target_entity_type": "phat beats"}}]

        self.assertEqual(self.retailer_trans_calc_task.calc_records, expected_calc_records)
        self.assertEqual(self.retailer_trans_calc_task.calc_runs, [])


if __name__ == '__main__':
    unittest.main()