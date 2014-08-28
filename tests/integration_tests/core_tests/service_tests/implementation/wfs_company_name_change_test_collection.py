from common.utilities.inversion_of_control import Dependency
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from core.common.business_logic.service_entity_logic.trade_area_upserter import TradeAreaUpserter
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_rir
from bson.objectid import ObjectId
import StringIO
import os


__author__ = 'erezrubinstein'


class WFSCompanyNameChangeTestCollection(ServiceTestCollection):

    def initialize(self):

        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            'user_id': ObjectId(),
            'source': 'company_name_change_integration_tests'
        }

    def setUp(self):

        self.mds_access.call_delete_reset_database()
        self.rds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def test_complete_company_name_change(self):

        # -------------------------- Create Entities --------------------------

        # original company name
        test_company_name = "chick_woot_company"

        # create a test company
        company_id = insert_test_company(name = test_company_name)

        # insert a test rir
        rir_id = insert_test_rir(self.context, company_id, company_name = test_company_name)

        # insert a test store
        store_helper = StoreHelper()
        store_id = store_helper.create_new_store(self.context, rir_id, async=False)

        trade_area_upserter = TradeAreaUpserter(str(store_id))
        trade_area_upserter.initialize()
        trade_area_upserter.upsert('DistanceMiles10')

        # upload a file, which will create an mds file, an rds file, and a workflow task
        self._upload_test_file(company_id, test_company_name, "chicken_woot_company_2012_11_21.xlsx")

        # -------------------------- Verify original company name --------------------------

        # query simple objects
        company = self.main_access.mds.call_get_entity_summary("company", company_id)
        rir = self.main_access.mds.call_get_entity_summary("retail_input_record", rir_id)
        store = self.main_access.mds.call_get_entity_summary("store", store_id)

        # query trade area raw
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = { "data.store_id": store_id }, entity_fields = ["data"])["params"]
        trade_area = self.main_access.mds.call_find_entities_raw("trade_area", params)[0]

        # query file raw
        params = self.main_params.mds.create_params(resource = "find_entities_raw", entity_fields = ["data", "name"])["params"]
        mds_file = self.main_access.mds.call_find_entities_raw("file", params)[0]

        # query rds file
        rds_file = self.main_access.rds.call_get_file_info_by_name("retail_input_files/%s/chicken_woot_company_2012_11_21.xlsx" % test_company_name, self.context)

        # query task group
        task_group = self.main_access.wfs.call_task_group_find(self.context, params)[0]

        # verify their company names are the original
        self.test_case.assertEqual(company["entity"]["name"], test_company_name)
        self.test_case.assertEqual(rir["entity"]["data"]["company_name"], test_company_name)
        self.test_case.assertEqual(store["entity"]["data"]["company_name"], test_company_name)
        self.test_case.assertEqual(trade_area["data"]["company_name"], test_company_name)

        # make sure the mds/rds paths are correct
        self.test_case.assertEqual(mds_file["data"]["path"], "retail_input_files/%s/" % test_company_name)
        self.test_case.assertEqual(mds_file["name"], "retail_input_files/%s/chicken_woot_company_2012_11_21.xlsx" % test_company_name)
        self.test_case.assertEqual(rds_file["filename"], "retail_input_files/%s/chicken_woot_company_2012_11_21.xlsx" % test_company_name)
        self.test_case.assertEqual(rds_file["metadata"]["path"], "retail_input_files/%s/" % test_company_name)

        # make sure the task group path is correct
        self.test_case.assertEqual(task_group["data"]["company_name"], test_company_name)

        # -------------------------- Update company --------------------------

        # update the company
        new_company_name = "chilly_willy_company"
        query = { "_id": company_id }
        operation = { "$set": { "name": new_company_name }}
        self.main_access.mds.call_batch_update_entities("company", query, operation, self._context)

        # call the update company task
        company_name_change_rec = {
            'input': {
                "context": self._context,
                "company_id": company_id
            },
            'meta': {
                'async': False
            },
            'task_status': {
                'status': "in-progress"
            }
        }
        self.main_access.wfs.call_task_new('entity_updated', 'company', 'company_name_change', company_name_change_rec, self._context)


        # -------------------------- verify all entities are updated --------------------------

        # query simple objects
        company = self.main_access.mds.call_get_entity_summary("company", company_id)
        rir = self.main_access.mds.call_get_entity_summary("retail_input_record", rir_id)
        store = self.main_access.mds.call_get_entity_summary("store", store_id)

        # query trade area raw
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = { "data.store_id": store_id }, entity_fields = ["data"])["params"]
        trade_area = self.main_access.mds.call_find_entities_raw("trade_area", params)[0]

        # query file raw
        params = self.main_params.mds.create_params(resource = "find_entities_raw", entity_fields = ["data", "name"])["params"]
        mds_file = self.main_access.mds.call_find_entities_raw("file", params)[0]

        # query rds file
        rds_file = self.main_access.rds.call_get_file_info_by_name("retail_input_files/%s/chicken_woot_company_2012_11_21.xlsx" % new_company_name, self.context)

        # query task group
        task_group = self.main_access.wfs.call_task_group_find(self.context, params)[0]

        # verify their company names are the original
        self.test_case.assertEqual(company["entity"]["name"], new_company_name)
        self.test_case.assertEqual(rir["entity"]["data"]["company_name"], new_company_name)
        self.test_case.assertEqual(store["entity"]["data"]["company_name"], new_company_name)
        self.test_case.assertEqual(trade_area["data"]["company_name"], new_company_name)

        # make sure the mds/rds paths are correct
        self.test_case.assertEqual(mds_file["data"]["path"], "retail_input_files/%s/" % new_company_name)
        self.test_case.assertEqual(mds_file["name"], "retail_input_files/%s/chicken_woot_company_2012_11_21.xlsx" % new_company_name)
        self.test_case.assertEqual(rds_file["filename"], "retail_input_files/%s/chicken_woot_company_2012_11_21.xlsx" % new_company_name)
        self.test_case.assertEqual(rds_file["metadata"]["path"], "retail_input_files/%s/" % new_company_name)

        # make sure the task group path is correct
        self.test_case.assertEqual(task_group["data"]["company_name"], new_company_name)

    # ---------------------------------------- Upload File ----------------------------------------

    def _upload_test_file(self, company_id, company_name, file_name):

        # create data object
        data = {
            "company_id": company_id,
            "company_name": company_name,
            "is_comprehensive": True,
            "is_async": False
        }

        # read file
        upload_file_path = os.path.join(os.path.dirname(__file__), "data", file_name)
        file_name = os.path.split(os.path.abspath(upload_file_path))[1]
        with open(upload_file_path, 'rb') as f:
            files = {file_name: StringIO.StringIO(f.read())}

        # upload with main
        self.main_access.call_post_retail_input_file_upload(data, files, self.context)