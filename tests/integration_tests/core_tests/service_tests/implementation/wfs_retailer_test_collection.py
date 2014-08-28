from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_retailer_transaction, insert_test_retailer_file


class WFSRetailerTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "wfs_retailer_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # some pycharm/unittest param that blocks you from seeing a diff failure in an assert statement if it's too long
        self.maxDiff = None
        self.main_param = Dependency("CoreAPIParamsBuilder").value


    def setUp(self):
        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()


    def tearDown(self):
        pass


    def test_retailer_entity_dupe_checker(self):
        file1_id = insert_test_retailer_file(0)
        file2_id = insert_test_retailer_file(0)
        trx1_id = insert_test_retailer_transaction(0, "customer_id", 5, "date", transaction_id="trx_id", mds_file_id=file1_id)
        trx2_id = insert_test_retailer_transaction(0, "customer_id", 5, "date", transaction_id="trx_id", mds_file_id=file2_id)

        # Form task record
        task_rec = {
            "input": {
                "retailer_client_id": 0,
                "id_key": "data.transaction_id",
                "entity_type": "retailer_transaction"
            },
            "meta": {
                "async": False
            }
        }

        # Run task
        result = self.wfs_access.call_task_new("retailer_curation", "input_sourcing", "dupe_checking",
                                               task_rec, self.context)

        dupes = result["task_status"]["result"]["results"]

        self.test_case.assertEqual(len(dupes), 1)
        self.test_case.assertIn("trx_id", dupes)
        self.test_case.assertEqual(dupes["trx_id"]["count"], 2)
        dupe_ids = set(dupes["trx_id"]["_ids"])
        dupe_mds_file_ids = set(dupes["trx_id"]["mds_file_ids"])
        self.test_case.assertEqual(dupe_ids, set([str(trx1_id), str(trx2_id)]))
        self.test_case.assertEqual(dupe_mds_file_ids, set([str(file1_id), str(file2_id)]))
