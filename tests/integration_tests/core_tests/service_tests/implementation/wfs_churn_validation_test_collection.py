from __future__ import division
from common.service_access.utilities.errors import ServiceCallError
from common.utilities.inversion_of_control import Dependency
from core.common.business_logic.service_entity_logic import rir_helper
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from core.common.utilities.include import *
from core.common.utilities.helpers import ensure_id, parse_timestamp
from core.service.svc_main.implementation.service_endpoints.endpoint_field_data \
    import RETAIL_INPUT_CHURN_VALIDATION_MATCHES_DB_FIELDS, RETAIL_INPUT_VALIDATION_SEARCHALL_DB_FIELDS
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_rir
import StringIO


__author__ = "jsternberg"


class WFSChurnValidationTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = '1'
        self.source = "wfs_test_collection.py"
        self.context = {"user_id": self.user_id,
                        "source": self.source,
                        "team_industries": [],
                        "user": {"is_generalist": False}}

        self.sample_filenames_jcrew_full_line = ["J.CREW_Full_Line_2012_11_21.xlsx",
                                                 "J.CREW_Full_Line_2013_01_21.xlsx",
                                                 "J.CREW_Full_Line_2013_03_21.xlsx"]

        self.sample_filenames_99_cents = ["99_Cents_Only_Stores_2011_07_02.xlsx",
                                          "99_Cents_Only_Stores_2012_10_11.xlsx"]

        self.single_rir_filenames = ["J.CREW_Full_Line_Single_RIR_2011_11_21.xlsx",
                                     "J.CREW_Full_Line_Single_RIR_2011_12_21.xlsx"]

        self.dupe_rir_filenames = ["J.CREW_Full_Line_Dupe_RIR_2012_11_21.xlsx",
                                   "J.CREW_Full_Line_Dupe_RIR_2012_12_21.xlsx"]

        self.three_row_filenames = ["J.CREW_Full_Line_Three_Row_File_2012_11_21.xlsx",
                                    "J.CREW_Full_Line_Three_Row_File_2013_11_21.xlsx"]

        self.one_row_filenames = ["J.CREW_Full_Line_One_Row_File_2012_11_21.xlsx",
                                    "J.CREW_Full_Line_One_Row_File_2013_11_21.xlsx",
                                    "J.CREW_Full_Line_One_Row_File_2013_12_21.xlsx"]

        self.file_base_path = os.path.join(os.path.dirname(__file__), "data")

        self.main_param = Dependency("CoreAPIParamsBuilder").value
        self.store_helper = StoreHelper()

        self.async_mode = False         # Mode for new task creation (controlled from test_wfs_api)
        self.wait_secs = 30             # Max wait time for async tasks to complete

    def setUp(self):

        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.rds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##----------------------## Test Methods ##--------------------------##

    def wfs_test_retail_input_file_loader(self):

        # process the jcrew file
        company_name = 'J.Crew Full Line'
        company_id, file_entity = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[0], company_name = company_name)

        # query all the rirs and addresses
        fields = ["data"]
        params = self.main_param.create_params(resource = "get_data_entities", fields = fields)
        rirs = self.main_access.call_get_data_entities("retail_input_record", params = params["params"])
        addresses = self.main_access.call_get_data_entities("address", params = params["params"])
        stores = self.mds_access.call_find_entities_raw("store", params = {}, context = self.context)

        self.test_case.assertEqual(len(rirs["rows"]), 20)
        self.test_case.assertEqual(len(addresses["rows"]), 20)
        self.test_case.assertEqual(len(stores), 20)

        # verify the rirs
        for rir in rirs["rows"]:
            # make sure company_name, company_id, file_id, file_name are always in rir
            self.test_case.assertEqual(company_name, rir["data"]["company_name"])
            self.test_case.assertEqual(company_id, rir["data"]["company_id"])
            self.test_case.assertEqual(file_entity["_id"], rir["data"]["source_id"])
            self.test_case.assertEqual(file_entity["name"].rsplit('/', 1)[-1], self.sample_filenames_jcrew_full_line[0])
            self.test_case.assertEqual("file", rir["data"]["source_type"])

        # verify that the addresses always have all the correct fields
        for address in addresses["rows"]:
            self.test_case.assertIn("data", address)
            self.test_case.assertIn("street_number", address["data"])
            self.test_case.assertIn("street", address["data"])
            self.test_case.assertIn("city", address["data"])
            self.test_case.assertIn("state", address["data"])
            self.test_case.assertIn("zip", address["data"])
            self.test_case.assertIn("suite", address["data"])
            self.test_case.assertIn("country", address["data"])
            self.test_case.assertIn("shopping_center", address["data"])
            self.test_case.assertIn("latitude", address["data"])
            self.test_case.assertIn("longitude", address["data"])
            self.test_case.assertIn("geo", address["data"])

            # verify that lat/long geo are non-zero numbers
            self.test_case.assertNotEqual(address["data"]["latitude"], 0)
            self.test_case.assertNotEqual(address["data"]["longitude"], 0)
            self.test_case.assertNotEqual(address["data"]["geo"][0], 0)
            self.test_case.assertNotEqual(address["data"]["geo"][1], 0)

        # Should create rir-to-store links
        relation_types = [["retail_input", "retail_input_record", "store"]]
        params = self.main_param.create_params(resource = "get_data_entity_relationships",
                                               relation_types = relation_types)
        rir_store_rels = self.main_access.call_get_data_entity_relationships("retail_input_record", "store",
                                                                             params = params["params"])
        self.test_case.assertEqual(len(rir_store_rels["rows"]), 20)

        if company_id:
            self.__delete_rds_file(file_entity["name"])

        # trade area asserts
        trade_areas = self.mds_access.call_find_entities_raw("trade_area", params = {}, context = self.context)
        self.test_case.assertEqual(0, len(trade_areas))

    def wfs_test_retail_input_file_loader__auto_create_stores_first_time_only(self):

        # process the jcrew file
        company_name = 'J.Crew Full Line'
        company_id, file_entity = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[0], company_name = company_name)

        stores = self.mds_access.call_find_entities_raw("store", params = {}, context = self.context)
        rirs = self.mds_access.call_find_entities_raw("retail_input_record", params = {}, context = self.context)
        addresses = self.mds_access.call_find_entities_raw("address", params = {}, context = self.context)
        trade_areas = self.mds_access.call_find_entities_raw("trade_area", params = {}, context = self.context)

        self.test_case.assertEqual(len(rirs), 20)
        self.test_case.assertEqual(len(addresses), 20)
        self.test_case.assertEqual(len(stores), 20)
        self.test_case.assertEqual(0, len(trade_areas))

        company_id, file_entity = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[1], company_id = company_id)

        stores = self.mds_access.call_find_entities_raw("store", params = {}, context = self.context)
        rirs = self.mds_access.call_find_entities_raw("retail_input_record", params = {}, context = self.context)
        addresses = self.mds_access.call_find_entities_raw("address", params = {}, context = self.context)
        trade_areas = self.mds_access.call_find_entities_raw("trade_area", params = {}, context = self.context)

        self.test_case.assertEqual(len(rirs), 44)
        self.test_case.assertEqual(len(addresses), 20)
        self.test_case.assertEqual(len(stores), 20)
        self.test_case.assertEqual(0, len(trade_areas))

    def wfs_test_retail_input_record_churn_matching_jcrew_full_line(self):

        company_id, file_entity1 = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[0],
                                                                            company_name='J.Crew Full Line')
        company_id, file_entity2 = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[1],
                                                                            company_id=company_id)

        self.__run_and_test_churn_matching_task(company_id, file_entity2["data"]["as_of_date"], file_entity2["_id"])

        params = {"query": {"flow": "retail_curation",
                            "process": "input_sourcing",
                            "stage": "churn_validation",
                            "task_status.status": "open"}}

        tasks = self.wfs_access.call_task_find(self.context, params)

        self.test_case.assertEqual(len(tasks), 16)

    def wfs_test_retail_input_record_churn_matching__exact_match_closed_store_no_auto_link(self):

        # Upload first file
        company_id, file_entity1 = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[0],
                                                                            company_name='J.Crew Full Line')

        # Upload second file
        company_id, file_entity2 = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[1],
                                                                            company_id=company_id)

        entity_fields = ["_id"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=entity_fields,
                                                   as_list=True)["params"]
        stores = self.mds_access.call_find_entities_raw("store", params, self.context)
        store_id_list = [ensure_id(store[0]) for store in stores]

        # Set close date for store to one day BEFORE as of date for second file
        closing_date = parse_timestamp(file_entity2["data"]["as_of_date"]) - datetime.timedelta(days=1)

        query = {"_id": {"$in": store_id_list}}
        operations = {
            "$set": {
                "interval": [None, closing_date]
            }
        }
        self.mds_access.call_batch_update_entities("store", query, operations, self.context)

        for store_id in store_id_list:
            rir_helper.update_rirs_with_store_interval(str(store_id), self.context)

        # Churn match
        self.__run_and_test_churn_matching_task(company_id, file_entity2["data"]["as_of_date"], file_entity2["_id"])

        # Get RIRs created from second file
        query = {
            "data.source_id": file_entity2["_id"]
        }
        entity_fields = ["_id", "links.store.retail_input"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query,
                                                   entity_fields=entity_fields, as_list=True)["params"]

        rirs = self.mds_access.call_find_entities_raw("retail_input_record", params, self.context)

        # Links to stores would only be created by auto-linking, so make sure none exist
        for rir in rirs:
            self.test_case.assertEqual(rir[1], None)

    def wfs_test_retail_input_record_churn_validation_link_target(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.sample_filenames_jcrew_full_line[0],
                                                 self.sample_filenames_jcrew_full_line[1],
                                                 'J.Crew Full Line')

        # validate task group summary was set up properly

        expected_result = {"num_raw_records": 24, "num_rirs": 24, "num_stores_created": 0}
        self.__assert_input_sourcing_summary(task, "parsing", "success", "File parsing is complete.", expected_result)

        expected_result = {"num_exact_matches": 4, "num_auto_linkable_matches": 4, "num_inexact_matches": 12, "num_mismatches": 4}
        self.__assert_input_sourcing_summary(task, "churn_matching", "success", "Churn matching is complete.",
                                             expected_result)

        expected_result = {"num_in_progress": 1, "num_unvalidated": 16, "num_validated": 0, "num_validation_tasks": 16,
                           "percent_complete": 0.0}
        self.__assert_input_sourcing_summary(task, "churn_validation", "in_progress",
                                             "Churn validation is in progress.", expected_result)

        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "target",
                           "companyID": company_id,
                           "asOfDate": file_entity2["data"]["as_of_date"]}
        validation_result = self.__save_and_test_validation(validation_data)

        params = {
            "query": {
                "_id": ensure_id(target_rir_id)
            },
            "entity_fields": ["_id", "data.workflow.retail_curation.input_sourcing.churn_validation"],
            "options": {
                "as_list": True
            }
        }
        rir = self.main_access.mds.call_find_entities_raw("retail_input_record", params, self.context)[0]
        self.test_case.assertDictEqual(rir[1], {
            'asOfDate': '2013-01-21T00:00:00',
            'companyID': company_id,
            'dataToUse': 'target',
            'decision': 'link',
            'decision_editable': True,
            'rirLinkID': suggested_match_list[0]["_id"],
            'store_id': rir[1]["store_id"],
            'store_interval': None,
            'taskID': task["_id"],
            'timestamp': rir[1]["timestamp"]
        })

        # There should be 1 regular rir-to-store link for target_rir_id
        field_filters = {"to._id": target_rir_id}
        fields = ["to._id"]
        relation_types = [["retail_input", "store", "retail_input_record"]]
        params = self.main_param.create_params(resource="get_data_entity_relationships", relation_types=relation_types,
                                               field_filters=field_filters, fields=fields)
        links = self.main_access.call_get_data_entity_relationships("store", "retail_input_record",
                                                                    params=params["params"], context=self.context)
        self.test_case.assertEqual(len(links["rows"]), 1)

        # There should be 1 most correct rir-to-store link for target_rir_id
        field_filters = {"to._id": target_rir_id, "to.data.is_most_correct": True,
                         "to.data.workflow.current.stage": "churn_validation"}
        fields = ["to._id", "to.data.is_most_correct", "to.data.workflow.current.stage"]
        relation_types = [["retail_input", "store", "most_correct_record"]]
        params = self.main_param.create_params(resource="get_data_entity_relationships", relation_types=relation_types,
                                               field_filters=field_filters, fields=fields)
        links = self.main_access.call_get_data_entity_relationships("store", "retail_input_record",
                                                                    params=params["params"], context=self.context)
        self.test_case.assertEqual(len(links["rows"]), 1)

        # validate task group summary was updated properly
        expected_result = {"num_raw_records": 24, "num_rirs": 24, "num_stores_created": 0}
        self.__assert_input_sourcing_summary(task, "parsing", "success", "File parsing is complete.", expected_result)

        expected_result = {"num_exact_matches": 4, "num_auto_linkable_matches": 4, "num_inexact_matches": 12, "num_mismatches": 4}
        self.__assert_input_sourcing_summary(task, "churn_matching", "success", "Churn matching is complete.",
                                             expected_result)

        expected_result = {"num_in_progress": 0, "num_unvalidated": 15, "num_validated": 1, "num_validation_tasks": 16,
                           "percent_complete": 0.0625}
        self.__assert_input_sourcing_summary(task, "churn_validation", "in_progress",
                                             "Churn validation is in progress.", expected_result)

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_churn_validation_link_target_store_update(self):

        #prepare churn validation using 1-store only files
        (company_id,
        file_entity1,
        file_entity2,
        target_rir_id,
        suggested_match_list,
        task) = self.__prepare_churn_validation(self.one_row_filenames[0],
                                                 self.one_row_filenames[1],
                                                 'J.Crew Full Line')

        #query stores after churn validation prep
        store_entity_fields = ["data.note", "data.phone", "data.phone_clean", "data.store_format", "data.store_number"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=store_entity_fields,
                                                   query={}, as_list=False)["params"]
        result = self.main_access.mds.call_find_entities_raw("store", params)
        store_id = result[0]['_id']
        store_data_before = result[0]['data']
        expected_phone_number = store_data_before['phone']
        expected_phone_number_clean = store_data_before['phone_clean']

        #change the store phone number
        store_update_data = {
           "data.phone": "123-456-7890",
           "data.phone_clean": "123-4567890"
        }
        self.main_access.mds.call_update_entity("store", store_id, self.context, field_data=store_update_data)

        #link_target decision should fix the changed store phone number since we now update store fields using target RIR
        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "target",
                           "companyID": company_id,
                           "asOfDate": file_entity2["data"]["as_of_date"]}

        validation_result = self.__save_and_test_validation(validation_data)

        #retrive the store again and make sure phone number has been fixed
        params = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=store_entity_fields,
                                                   query={"_id": store_id}, as_list=False)["params"]
        result = self.main_access.mds.call_find_entities_raw("store", params)
        store_data_after = result[0]['data']
        self.test_case.assertEqual(store_data_after['phone'], expected_phone_number)
        self.test_case.assertEqual(store_data_after['phone_clean'], expected_phone_number_clean)


    def wfs_test_retail_input_record_churn_validation_link_existing(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.sample_filenames_jcrew_full_line[0], self.sample_filenames_jcrew_full_line[1],
                                                                 'J.Crew Full Line')

        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "existing",
                           "companyID": company_id,
                           "asOfDate": file_entity2["data"]["as_of_date"]}
        validation_result = self.__save_and_test_validation(validation_data)

        # There should be 1 regular rir-to-store link for target_rir_id
        field_filters = {"to._id": target_rir_id}
        fields = ["to._id"]
        relation_types = [["retail_input", "store", "retail_input_record"]]
        params = self.main_param.create_params(resource = "get_data_entity_relationships",
                                               relation_types = relation_types,
                                               field_filters = field_filters,
                                               fields = fields)
        links = self.main_access.call_get_data_entity_relationships("store", "retail_input_record",
                                                                    params = params["params"], context = self.context)
        self.test_case.assertEqual(len(links["rows"]), 1)

        # There should be 0 most correct rir-to-store link for target_rir_id
        field_filters = {"to._id": target_rir_id}
        fields = ["to._id"]
        relation_types = [["retail_input", "store", "most_correct_record"]]
        params = self.main_param.create_params(resource = "get_data_entity_relationships",
                                               relation_types = relation_types,
                                               field_filters = field_filters,
                                               fields = fields)
        links = self.main_access.call_get_data_entity_relationships("store", "retail_input_record",
                                                                    params = params["params"], context = self.context)
        self.test_case.assertEqual(len(links["rows"]), 0)

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_churn_validation_link_relocation(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.sample_filenames_jcrew_full_line[0],
                                                 self.sample_filenames_jcrew_full_line[1], 'J.Crew Full Line')

        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "relocation"}
        self.__save_and_test_validation(validation_data)

        # There should be 2 rir-to-store links for target_rir_id
        field_filters = {"to._id": suggested_match_list[0]["_id"]}
        fields = ["to._id", "from._id", "from.interval.1"]
        relation_types = [["retail_input", "store", "retail_input_record"],
                          ["retail_input", "store", "most_correct_record"]]
        params = self.main_param.create_params(resource="get_data_entity_relationships", fields=fields,
                                               relation_types=relation_types, field_filters=field_filters)
        links = self.main_access.call_get_data_entity_relationships("store", "retail_input_record",
                                                                    params=params["params"], context=self.context)

        self.test_case.assertEqual(len(links["rows"]), 2)
        self.test_case.assertEqual(links["rows"][0]["from.interval.1"], file_entity2["data"]["as_of_date"])
        old_store_id = links["rows"][0]["from._id"]

        # There should be 2 rir-to-store links for target_rir_id
        field_filters = {"to._id": target_rir_id}
        fields = ["to._id", "from._id", "from.interval.0"]
        relation_types = [["retail_input", "store", "retail_input_record"],
                          ["retail_input", "store", "most_correct_record"]]
        params = self.main_param.create_params(resource="get_data_entity_relationships", fields=fields,
                                               relation_types=relation_types, field_filters=field_filters)
        links = self.main_access.call_get_data_entity_relationships("store", "retail_input_record",
                                                                    params=params["params"], context=self.context)
        self.test_case.assertEqual(len(links["rows"]), 2)

        (new_store_open_date_string,
         new_rir_as_of_date_string) = self.__normalize_date_strings(links["rows"][0]["from.interval.0"],
                                                                    file_entity2["data"]["as_of_date"])
        self.test_case.assertEqual(new_store_open_date_string, new_rir_as_of_date_string)
        new_store_id = links["rows"][0]["from._id"]

        # Make sure we have two different stores
        self.test_case.assertTrue(new_store_id != old_store_id)

        # There should be 1 store-to-store retail_location link
        field_filters = {"to._id": new_store_id, "from._id": old_store_id}
        fields = ["to._id", "from._id"]
        relation_types = [["retail_relocation", "previous_location", "next_location"]]
        params = self.main_param.create_params(resource="get_data_entity_relationships", fields=fields,
                                               relation_types=relation_types, field_filters=field_filters)
        links = self.main_access.call_get_data_entity_relationships("store", "store", params=params["params"],
                                                                    context=self.context)
        self.test_case.assertEqual(len(links["rows"]), 1)

        # There should be 1 rir-to-rir retail_location link
        field_filters = {"to._id": target_rir_id, "from._id": suggested_match_list[0]["_id"]}
        fields = ["to._id", "from._id"]
        relation_types = [["retail_relocation", "previous_location", "next_location"]]
        params = self.main_param.create_params(resource="get_data_entity_relationships", fields=fields,
                                               relation_types=relation_types, field_filters=field_filters)
        links = self.main_access.call_get_data_entity_relationships("retail_input_record", "retail_input_record",
                                                                    params=params["params"], context=self.context)
        self.test_case.assertEqual(len(links["rows"]), 1)

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_churn_validation_no_link_open(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.sample_filenames_jcrew_full_line[0], self.sample_filenames_jcrew_full_line[1],
                                                                 'J.Crew Full Line')

        validation_data = {"taskID": task["_id"],
                           "decision": "no-link",
                           "downstream": "open"}
        validation_result = self.__save_and_test_validation(validation_data)

        # There should be 2 rir-to-store links for target_rir_id
        field_filters = {"to._id": target_rir_id}
        fields = ["to._id"]
        relation_types = [["retail_input", "store", "retail_input_record"],
                          ["retail_input", "store", "most_correct_record"]]
        params = self.main_param.create_params(resource = "get_data_entity_relationships",
                                               relation_types = relation_types,
                                               field_filters = field_filters,
                                               fields = fields)
        links = self.main_access.call_get_data_entity_relationships("store", "retail_input_record",
                                                                    params = params["params"], context = self.context)
        self.test_case.assertEqual(len(links["rows"]), 2)

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_churn_validation_complete_before_getting_next(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.sample_filenames_jcrew_full_line[0],
                                                 self.sample_filenames_jcrew_full_line[1],
                                                 'J.Crew Full Line')

        params = {"flow": "retail_curation",
                  "process": "input_sourcing",
                  "stage": "churn_validation"}
        result = self.main_access.call_get_retail_input_record_validation_next_target(params = params,
                                                                                      context = self.context)
        self.test_case.assertIn("rir", result)
        self.test_case.assertIn("task_rec", result)
        task_rec = result["task_rec"]
        new_target_rir_id = task_rec["input"]["target_rir_id"]
        self.test_case.assertEqual(new_target_rir_id, target_rir_id)

        params = {"flow": "retail_curation",
                  "process": "company_data_curation",
                  "stage": "closed_store_validation"}
        
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_get_retail_input_record_validation_next_target,
                                    *(params, self.context))

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_churn_validation_user_tries_to_get_validated_task(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.sample_filenames_jcrew_full_line[0],
                                                 self.sample_filenames_jcrew_full_line[1],
                                                 'J.Crew Full Line')

        params = {"flow": "retail_curation",
                  "process": "input_sourcing",
                  "stage": "churn_validation"}
        result = self.main_access.call_get_retail_input_record_validation_next_target(params = params,
                                                                                      context = self.context)
        self.test_case.assertIn("rir", result)
        self.test_case.assertIn("task_rec", result)
        task_rec = result["task_rec"]
        new_target_rir_id = task_rec["input"]["target_rir_id"]
        self.test_case.assertEqual(new_target_rir_id, target_rir_id)

        validation_data = {"taskID": task["_id"],
                           "decision": "no-link",
                           "downstream": "open"}
        self.__save_and_test_validation(validation_data)

        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(validation_data, self.context), async=False)

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_churn_validation_dupe_avoided_jit_entity_matching(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.single_rir_filenames[0], self.dupe_rir_filenames[1], 'J.Crew Full Line')

        # Validate with regular context
        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "target"}
        validation_result = self.main_access.call_post_retail_input_record_validation_save(validation_data, self.context, async=False)
        self.test_case.assertIn("task", validation_result)
        self.test_case.assertIn("rir", validation_result)

        # There should only be one most correct RIR
        fields = ["_id", "data.is_most_correct"]
        field_filters = {"data.is_most_correct": True}
        params = self.main_param.create_params(resource = "get_data_entities", fields = fields,
                                               field_filters = field_filters)
        rirs = self.main_access.call_get_data_entities("retail_input_record", params["params"])
        self.test_case.assertEqual(len(rirs["rows"]), 1)
        self.test_case.assertEqual(rirs["rows"][0]["_id"], target_rir_id)

        # Get the dupe with a new context
        params = {"flow": "retail_curation",
                  "process": "input_sourcing",
                  "stage": "churn_validation"}
        new_context = {"user_id": "2", "source": "wfs_test_collection.py"}

        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_get_retail_input_record_validation_next_target,
                                    *(params, new_context))

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_churn_validation_dupe_race_condition(self):
        self.__prepare_churn_validation(self.single_rir_filenames[0], self.dupe_rir_filenames[1], 'J.Crew Full Line')
        # Get the dupe with a new context
        params = {"flow": "retail_curation",
                  "process": "input_sourcing",
                  "stage": "churn_validation"}
        new_context = {"user_id": "2",
                       "source": "wfs_test_collection.py",
                       "team_industries": self.context["team_industries"],
                       "user": self.context["user"]}
        with self.test_case.assertRaises(ServiceCallError):
            self.main_access.call_get_retail_input_record_validation_next_target(params=params, context=new_context)

    def wfs_test_retail_input_create_qc_task(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.single_rir_filenames[0], self.dupe_rir_filenames[1], 'J.Crew Full Line')

        # Validate with regular context
        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "target"}
        self.main_access.call_post_retail_input_record_validation_save(validation_data, self.context, async=False)

        result = self.main_access.call_post_retail_input_validation_qc({"taskID": task["_id"]}, self.context)
        self.test_case.assertEqual(result["validation_type"], "new")
        self.test_case.assertIn("task_id", result)

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_closed_store_validation__close_store(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.single_rir_filenames[0], self.single_rir_filenames[1], 'J.Crew Full Line')

        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "target"}
        self.__save_and_test_validation(validation_data)

        # Create and start closed store search task
        params = {"query": {"unique_key.company_id": company_id,
                            "unique_key.as_of_date": file_entity2["data"]["as_of_date"],
                            "unique_key.source_id": file_entity2["_id"]}}
        task_group = self.main_access.wfs.call_task_group_find(self.context, params)[0]

        task_rec = {"task_group_id": task_group["_id"],
                    "input": {"company_recs": [{"company_id":company_id, "primary_industry_id":self.context["team_industries"][0]}]}}
        result = self.wfs_access.call_task_new("retail_curation", "company_data_curation",
                                               "closed_store_searching", task_rec, self.context)

        # There should be 1 task id in output rec of result
        self.test_case.assertEqual("stopped", result["task_status"]["status"])
        self.test_case.assertEqual(1, len(result["task_status"]["result"][company_id]["closed_store_validation_task_ids"]))

        # Double-check that there is 1 closed store validation tasks
        params = {"query": {"flow": "retail_curation", "process": "company_data_curation",
                            "stage": "closed_store_validation", "task_status.status": "open"}}
        tasks = self.wfs_access.call_task_find(self.context, params = params)
        self.test_case.assertEqual(len(tasks), 1)

        target_rir_id = self.__get_and_test_next_closed_store_validation_target_rir()
        suggested_match_list = self.__get_and_test_validation_matches(target_rir_id, company_id, tasks[0]["_id"])

        self.test_case.assertEqual(len(suggested_match_list), 0)

        all_rirs = self.__get_and_test_validation_searchall(target_rir_id, company_id, tasks[0]["_id"])
        self.test_case.assertEqual(len(all_rirs), 0)

        validation_data = {"taskID": tasks[0]["_id"],
                           "decision": "no-link",
                           "downstream": "close"}
        self.__save_and_test_validation(validation_data, stage = "closed_store_validation")

        fields = ["from._id", "to.interval.1"]
        field_filters = {"from._id": target_rir_id}
        relation_types = [["retail_input", "most_correct_record", "store"]]
        params = self.main_param.create_params(resource = "get_data_entity_relationships", fields = fields,
                                               field_filters = field_filters, relation_types = relation_types)
        rir_store_rels = self.main_access.call_get_data_entity_relationships("retail_input_record", "store",
                                                                             params = params["params"])
        self.test_case.assertEqual(len(rir_store_rels["rows"]), 1)

        (store_close_date_string,
         file_as_of_date) = self.__normalize_date_strings(rir_store_rels["rows"][0]["to.interval.1"],
                                                          file_entity2["data"]["as_of_date"])
        # temp hack
        todays_date = str(datetime.datetime.utcnow()).split(' ')[0]
        self.test_case.assertEqual(store_close_date_string.split(' ')[0], todays_date)

        if company_id:
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_retail_input_record_closed_store_validation__keep_store_open(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.single_rir_filenames[0], self.single_rir_filenames[1], 'J.Crew Full Line')

        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "target"}
        self.__save_and_test_validation(validation_data)

        # Create and start closed store search task
        params = {"query": {"unique_key.company_id": company_id,
                            "unique_key.as_of_date": file_entity2["data"]["as_of_date"],
                            "unique_key.source_id": file_entity2["_id"]}}
        task_group = self.main_access.wfs.call_task_group_find(self.context, params)[0]

        task_rec = {"task_group_id": task_group["_id"],
                    "input": {"company_recs": [{"company_id":company_id, "primary_industry_id":self.context["team_industries"][0]}]}}
        result = self.wfs_access.call_task_new("retail_curation", "company_data_curation",
                                               "closed_store_searching", task_rec, self.context)

        # There should be 1 task id in output rec of result
        self.test_case.assertEqual("stopped", result["task_status"]["status"])
        self.test_case.assertEqual(1, len(result["task_status"]["result"][company_id]["closed_store_validation_task_ids"]))

        # Double-check that there is 1 closed store validation tasks
        params = {"query": {"flow": "retail_curation", "process": "company_data_curation",
                            "stage": "closed_store_validation", "task_status.status": "open"}}
        tasks = self.wfs_access.call_task_find(self.context, params = params)
        self.test_case.assertEqual(len(tasks), 1)

        target_rir_id = self.__get_and_test_next_closed_store_validation_target_rir()
        suggested_match_list = self.__get_and_test_validation_matches(target_rir_id, company_id, tasks[0]["_id"])

        self.test_case.assertEqual(len(suggested_match_list), 0)

        all_rirs = self.__get_and_test_validation_searchall(target_rir_id, company_id, tasks[0]["_id"])
        self.test_case.assertEqual(len(all_rirs), 0)

        validation_data = {"taskID": tasks[0]["_id"],
                           "decision": "link",
                           "downstream": "close"}
        self.__save_and_test_validation(validation_data, stage = "closed_store_validation")

        fields = ["from._id", "to.interval.1"]
        field_filters = {"from._id": target_rir_id}
        relation_types = [["retail_input", "most_correct_record", "store"]]
        params = self.main_param.create_params(resource = "get_data_entity_relationships", fields = fields,
                                               field_filters = field_filters, relation_types = relation_types)
        rir_store_rels = self.main_access.call_get_data_entity_relationships("retail_input_record", "store",
                                                                             params = params["params"])
        self.test_case.assertEqual(len(rir_store_rels["rows"]), 1)
        self.test_case.assertEqual(rir_store_rels["rows"][0]["to.interval.1"], None)

        if company_id:
            self.__delete_rds_file(file_entity2["name"])

    def wfs_test_churn_validation_task_deletion(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.three_row_filenames[0], self.three_row_filenames[1], 'J.Crew Full Line')

        # Delete the task's target RIR
        self.main_access.mds.call_del_entity("retail_input_record", target_rir_id)

        # Get next task again
        params = {"flow": "retail_curation",
                  "process": "input_sourcing",
                  "stage": "churn_validation"}
        result = self.main_access.call_get_retail_input_record_validation_next_target(params = params,
                                                                                      context = self.context)

        # Make sure task is deleted
        try:
            self.main_access.wfs.call_get_task_id(task["_id"])
        except ServiceCallError as e:
            self.test_case.assertEqual(e.status_code, 404)
        else:
            assert False

        # make sure the task group's summary status has been updated properly
        expected_churn_validation_result = {"num_in_progress": 1, "num_unvalidated": 2, "num_validated": 0, "num_validation_tasks": 2, "percent_complete": 0.0}
        self.__assert_input_sourcing_summary(task, "churn_validation", "in_progress", "Churn validation is in progress.",
                                             expected_churn_validation_result)

    def wfs_test_churn_completion_fixer(self):

        # prepare churn validation with 1 row files
        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.one_row_filenames[0],
                                                 self.one_row_filenames[1],
                                                 'J.Crew Full Line')

        # complete validation
        validation_data = {"taskID": task["_id"],
                           "decision": "link",
                           "rirLinkID": suggested_match_list[0]["_id"],
                           "dataToUse": "target",
                           "companyID": company_id,
                           "asOfDate": file_entity2["data"]["as_of_date"]}
        validation_result = self.__save_and_test_validation(validation_data)

        # assert churn validation is complete
        expected_churn_validation_result = {
            "num_in_progress": 0,
            "num_unvalidated": 0,
            "num_validated": 1,
            "num_validation_tasks": 1,
            "percent_complete": 1.0
        }
        self.__assert_input_sourcing_summary(task, "churn_validation", "success", "Churn validation is complete.",
                                             expected_churn_validation_result)

        # upload another file, which produces another validation task
        (company_id,
         file_entity3,
         target_rir_id2,
         suggested_match_list2,
         task2) = self.__prepare_churn_validation_additional_file(self.one_row_filenames[2], company_id)

        # assert churn validation is in progress for the 2nd task
        expected_churn_validation_result2 = {
            "num_in_progress": 1,
            "num_unvalidated": 1,
            "num_validated": 0,
            "num_validation_tasks": 1,
            "percent_complete": 0.0
        }
        self.__assert_input_sourcing_summary(task2, "churn_validation", "in_progress",
                                             "Churn validation is in progress.", expected_churn_validation_result2)

        # mess up the completion data for both files to simulate db weirdness, race conditions, etc.
        summary_update_rec = {
            "summary": {
                "input_sourcing.churn_validation.result.num_unvalidated": 999,
                "input_sourcing.churn_validation.result.num_validated": 0,
                "input_sourcing.churn_validation.result.num_in_progress": -123,
                "input_sourcing.churn_validation.result.num_validation_tasks": 1024,
                "input_sourcing.churn_validation.result.percent_complete": 0.0
            }
        }
        self.main_access.wfs.call_update_task_group_id(task["task_group_id"], self.context, summary_update_rec)
        self.main_access.wfs.call_update_task_group_id(task2["task_group_id"], self.context, summary_update_rec)

        # call churn completion fixer, which should FIX IT!
        result = self.__run_and_test_churn_completion_fixer_task()

        # assert completion for file 1 has been fixed to 1.0 again
        self.__assert_input_sourcing_summary(task, "churn_validation", "success", "Churn validation is complete.",
                                             expected_churn_validation_result)

        # assert completion for file 1 has been fixed to 0.0 again
        self.__assert_input_sourcing_summary(task2, "churn_validation", "in_progress",
                                             "Churn validation is in progress.", expected_churn_validation_result2)




    ##------------------------## private methods ##------------------------##

    def __add_company(self, company_name):

        name = "NAICS2007_11111 - Soybean Farming"
        data = {"industry_level": 4,
                "source_vendor": "NAICS",
                "industry_code": "11111",
                "source_id": 4.0,
                "source_version": "2007",
                "industry_name": "Soybean Farming",
                "workflow": {"current": {"status": "new"}}}
        industry_id = self.mds_access.call_add_entity("industry", name, data, self.context)

        self.context["team_industries"].append(industry_id)

        data = {"type": "retail_parent",
                "ticker": "",
                "status": "operating",
                "description": company_name,
                "exchange": "None",
                "closure_confirmation_threshold_days": 270,
                "workflow": {"current": {"status": "new"}}}
        company_id = self.mds_access.call_add_entity("company", company_name, data, self.context)

        self.mds_access.call_add_link("company", company_id, "primary_industry_classification",
                                      "industry", industry_id, "primary_industry", "industry_classification",
                                      self.context)

        return company_id

    def __delete_entity(self, entity_type, entity_id):
        return self.mds_access.call_del_entity(entity_type, entity_id)

    def __delete_rds_file(self, filename):
        return self.rds_access.call_delete_file_by_name(filename, context = self.context)

    def __delete_mds_file(self, file_id):
        return self.rds_access.call_del_entity("company", file_id)

    def __upload_and_parse_file(self, filename, company_name = None, company_id = None):

        if company_name:
            company_id = self.__add_company(company_name)

        elif company_id:
            company_entity = self.main_access.call_get_entity_summary('company', company_id)["entity"]
            company_name = company_entity["name"]

        data = {"company_id": company_id,
                "company_name": company_name,
                "is_comprehensive": True,
                "is_async": False}

        upload_file_path = os.path.join(os.path.dirname(__file__), "data", filename)
        file_name = os.path.split(os.path.abspath(upload_file_path))[1]
        with open(upload_file_path, 'rb') as f:
            files = {file_name: StringIO.StringIO(f.read())}

        result = self.main_access.call_post_retail_input_file_upload(data, files, self.context)

        self.test_case.assertEqual(result["status"], 201)
        self.test_case.assertIn("task_group", result)
        self.test_case.assertIn("task", result)
        self.test_case.assertIn("input", result["task"])
        self.test_case.assertIn("mds_file_id", result["task"]["input"])
        mds_file_id = result["task"]["input"]["mds_file_id"]

        return company_id, mds_file_id, result["task"], result["task_group"]

    def __upload_and_test_retail_input_file(self, filename, company_name=None, company_id=None):

        company_id, file_id1, task, task_group = self.__upload_and_parse_file(filename, company_name=company_name,
                                                                              company_id=company_id)

        file_entity1 = self.main_access.call_get_entity_summary('file', file_id1)["entity"]

        self.test_case.assertEqual("retail_curation", task['flow'])
        self.test_case.assertEqual("input_sourcing", task['process'])
        self.test_case.assertEqual("parsing", task['stage'])

        self.test_case.assertIn("_id", task)
        self.test_case.assertEqual(file_id1, task["input"]["mds_file_id"])

        self.test_case.assertIn("output", task)
        self.test_case.assertEqual("stopped", task["task_status"]["status"])

        return company_id, file_entity1

    def __run_and_test_churn_matching_task(self, company_id, as_of_date, source_id):

        params = {"query": {"unique_key.company_id": company_id,
                            "unique_key.as_of_date": as_of_date,
                            "unique_key.source_id": source_id}}
        task_group = self.main_access.wfs.call_task_group_find(self.context, params)[0]

        rir_matcher_task_rec = {
            "task_group_id": task_group["_id"],
            "input": {"company_id": company_id, "as_of_date": as_of_date, "source_id": source_id, "spawn_async_tasks": False},
            "meta": {"async": False}
        }
        result = self.main_access.wfs.call_task_new("retail_curation", "input_sourcing", "churn_matching",
                                                    rir_matcher_task_rec, self.context)

        self.test_case.assertEqual(result["task_status"]["status"], "stopped")
        return result

    def __compare_and_test_jcrew_file1_vs_file2_results(self, matcher_result2, file_entity2):

        exact_match_id_set = {obj for obj in matcher_result2["task_status"]["result"]["match_summary"]["exact"]}
        self.test_case.assertEqual(len(exact_match_id_set), 4)

        auto_linkable_id_set = {obj for obj in matcher_result2["task_status"]["result"]["match_summary"]["auto_linkable"]}
        self.test_case.assertEqual(len(auto_linkable_id_set), 4)

        inexact_match_id_set = {obj for obj in matcher_result2["task_status"]["result"]["match_summary"]["inexact"]}
        self.test_case.assertEqual(len(inexact_match_id_set), 12)

        mismatch_id_set = {obj for obj in matcher_result2["task_status"]["result"]["match_summary"]["mismatch"]}
        self.test_case.assertEqual(len(mismatch_id_set), 4)

        # There should be 8 rir-to-store links for second group of RIRs (only exact matches)
        relation_types = [["retail_input", "store", "retail_input_record"]]
        field_filters = {"to.data.as_of_date": file_entity2["data"]["as_of_date"]}
        fields = ["to.data.as_of_date"]
        params = self.main_param.create_params(resource = "get_data_entity_relationships",
                                               relation_types = relation_types,
                                               field_filters = field_filters,
                                               fields = fields)
        links = self.main_access.call_get_data_entity_relationships("store", "retail_input_record",
                                                                    params = params["params"], context = self.context)
        self.test_case.assertEqual(len(links["rows"]), 8)

        # There should be 12 churn validation tasks for inexact matches
        params = {"query": {"flow": "retail_curation",
                            "process": "input_sourcing",
                            "stage": "churn_validation",
                            "task_status.status": "open"}}
        tasks = self.wfs_access.call_task_find(self.context, params = params)

        inexact_tasks = [task for task in tasks
                         if "match_type" in task["input"] and task["input"]["match_type"] == "inexact" and
                            task["task_status"]["status"] == "open"]
        self.test_case.assertEqual(len(inexact_tasks), 12)

        # There should be 4 churn validation tasks for mismatches
        mismatch_tasks = [task for task in tasks
                          if "match_type" in task["input"] and task["input"]["match_type"] == "mismatch" and
                             task["task_status"]["status"] == "open"]
        self.test_case.assertEqual(len(mismatch_tasks), 4)

        return exact_match_id_set, inexact_match_id_set, mismatch_id_set

    def __get_and_test_next_churn_validation_target_rir(self, inexact_and_mismatch_ids):

        # Use retail input endpoint to get next validation target
        timestamp = str(datetime.datetime.utcnow())
        params = {"flow": "retail_curation", "process": "input_sourcing", "stage": "churn_validation"}
        result = self.main_access.call_get_retail_input_record_validation_next_target(params = params, context = self.context)

        self.test_case.assertIn("rir", result)
        self.test_case.assertIn("task_rec", result)
        task_rec = result["task_rec"]
        target_rir_id = task_rec["input"]["target_rir_id"]
        if inexact_and_mismatch_ids:
            self.test_case.assertIn(target_rir_id, inexact_and_mismatch_ids)

        # Check task data
        params = {"has_metadata": True}
        task = self.wfs_access.call_get_task_id(task_rec["_id"], self.context, params = params)
        self.test_case.assertGreater(task["meta"]["updated_at"], timestamp)
        self.test_case.assertEqual(task["task_status"]["status"], "in_progress")
        self.test_case.assertEqual(task["context_data"]["user_id"], self.context["user_id"])

        return target_rir_id, task

    def __get_and_test_next_closed_store_validation_target_rir(self):
        """

        """
        # Use retail input endpoint to get next validation target
        timestamp = str(datetime.datetime.utcnow())
        params = {"flow": "retail_curation", "process": "company_data_curation", "stage": "closed_store_validation"}
        result = self.main_access.call_get_retail_input_record_validation_next_target(params = params, context = self.context)

        self.test_case.assertIn("rir", result)
        self.test_case.assertIn("task_rec", result)
        task_rec = result["task_rec"]
        target_rir_id = task_rec["input"]["target_rir_id"]

        # Check task data
        params = {"has_metadata": True}
        task = self.wfs_access.call_get_task_id(task_rec["_id"], self.context, params = params)
        self.test_case.assertGreater(task["meta"]["updated_at"], timestamp)
        self.test_case.assertEqual(task["task_status"]["status"], "in_progress")

        return target_rir_id

    def __get_and_test_validation_matches(self, target_rir_id, company_id, task_id, context = None):
        """
        Make sure the RIR validation matches preset sends some matches
        """
        # This field list comes directly from endpoint logic
        field_list = set(RETAIL_INPUT_CHURN_VALIDATION_MATCHES_DB_FIELDS)

        params = {"rirID": target_rir_id, "companyID": company_id, "taskID": task_id}
        context = self.context if not context else context
        inexact_match_list = self.main_access.call_get_data_preset_retail_input_record_validation_matches(params = params, context = context)["rows"]

        return inexact_match_list

    def __get_and_test_validation_searchall(self, target_rir_id, company_id, task_id):
        """
        Make sure the RIR validation searchall preset sends all RIRs that have been churn validated
        """
        field_list = set(RETAIL_INPUT_VALIDATION_SEARCHALL_DB_FIELDS)

        params = {"rirID": target_rir_id, "companyID": company_id, "taskID": task_id,
                  "pageSize": 100, "pageIndex": 0, "sortIndex": 0, "sortDirection": -1}
        all_results = self.main_access.call_get_data_preset_retail_input_record_validation_searchall(params = params, context = self.context)["rows"]

        for result in all_results:
            self.test_case.assertEqual(len(field_list & set(result.keys())), len(field_list))

        return all_results

    def __prepare_churn_validation(self, filename1, filename2, company_name):

        company_id, file_entity1 = self.__upload_and_test_retail_input_file(filename1, company_name = company_name)
        company_id, file_entity2 = self.__upload_and_test_retail_input_file(filename2, company_id = company_id)
        match_result = self.__run_and_test_churn_matching_task(company_id, file_entity2["data"]["as_of_date"],
                                                               file_entity2["_id"])

        if filename1 == self.sample_filenames_jcrew_full_line[0] and filename2 == self.sample_filenames_jcrew_full_line[1]:
            (exact_match_id_set,
             inexact_match_id_set,
             mismatch_id_set) = self.__compare_and_test_jcrew_file1_vs_file2_results(match_result, file_entity2)
            inexact_and_mismatch_ids = inexact_match_id_set | mismatch_id_set
        else:
            inexact_and_mismatch_ids = None

        target_rir_id, task = self.__get_and_test_next_churn_validation_target_rir(inexact_and_mismatch_ids)

        suggested_match_list = self.__get_and_test_validation_matches(target_rir_id, company_id, task["_id"])

        return company_id, file_entity1, file_entity2, target_rir_id, suggested_match_list, task

    def __prepare_churn_validation_additional_file(self, filename, company_id):
        """Similar to above, but just does one file. Runs matching, so this shouldn't be the first file for the company."""

        company_id, file_entity = self.__upload_and_test_retail_input_file(filename, company_id = company_id)

        match_result = self.__run_and_test_churn_matching_task(company_id, file_entity["data"]["as_of_date"],
                                                               file_entity["_id"])

        target_rir_id, task = self.__get_and_test_next_churn_validation_target_rir(None)

        suggested_match_list = self.__get_and_test_validation_matches(target_rir_id, company_id, task["_id"])

        return company_id, file_entity, target_rir_id, suggested_match_list, task

    def __save_and_test_validation(self, validation_data, stage = "churn_validation"):
        """
        Uses validation_data argument to test for errors if required fields are missing, and
        then submits the data and returns the result.

        Args:
            validation_data: Dictionary of data to send to RIR validation endpoint
                {
                    taskID: ID of task
                    decision: 'link', 'no-link', or 'ignore'
                    rirLinkID: ID of RIR to which to link target RIR (only required if decision == 'link')
                    dataToUse: 'existing' or 'target' or 'relocation', whether or not to mark target RIR
                                as most correct (required if decision == 'link')
                    downstream: 'open' or 'close', whether to mark store as new or closed (only required
                                if decision == 'no-link')
                }

        Returns:
            Dictionary result of call to validation save endpoint
        """
        self.__test_validation_invalid_validation_data(validation_data, stage)
        result = self.main_access.call_post_retail_input_record_validation_save(validation_data, self.context, async=False)
        self.test_case.assertIn("task", result)
        self.test_case.assertIn("rir", result)
        return result

    def __test_validation_invalid_validation_data(self, validation_data, stage):

        # reset the task_status.status to in_progress after each assertRaises
        reset_task={
            "query":{"_id":validation_data["taskID"]},
            "update":{"$set":{"task_status.status":"in_progress"}}}

        test_data = dict(validation_data, taskID="")
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(test_data, self.context), async=False)
        self.main_access.wfs.call_find_and_modify_task(params=reset_task)

        test_data = dict(validation_data, decision="")
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(test_data, self.context), async=False)
        self.main_access.wfs.call_find_and_modify_task(params=reset_task)

        if stage == "churn_validation":
            test_data = dict(validation_data, decision="link", rirLinkID="")
            self.test_case.assertRaises(ServiceCallError,
                                        self.main_access.call_post_retail_input_record_validation_save,
                                        *(test_data, self.context), async=False)
            self.main_access.wfs.call_find_and_modify_task(params=reset_task)

            test_data = dict(validation_data, decision="link", dataToUse="")
            self.test_case.assertRaises(ServiceCallError,
                                        self.main_access.call_post_retail_input_record_validation_save,
                                        *(test_data, self.context), async=False)
            self.main_access.wfs.call_find_and_modify_task(params=reset_task)

            test_data = dict(validation_data, decision="link", dataToUse="asdf")
            self.test_case.assertRaises(ServiceCallError,
                                        self.main_access.call_post_retail_input_record_validation_save,
                                        *(test_data, self.context), async=False)
            self.main_access.wfs.call_find_and_modify_task(params=reset_task)

        test_data = dict(validation_data, decision="no-link", downstream="")
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(test_data, self.context), async=False)
        self.main_access.wfs.call_find_and_modify_task(params=reset_task)

        test_data = dict(validation_data, decision="no-link", downstream="asdf")
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(test_data, self.context), async=False)
        self.main_access.wfs.call_find_and_modify_task(params=reset_task)

    def __run_and_test_churn_completion_fixer_task(self):

        fixer_task_rec = {
            "input": {"scheduled": False},
            "meta": {"async": False}
        }
        result = self.main_access.wfs.call_task_new("retail_curation", "input_sourcing", "churn_completion_fixer",
                                                    fixer_task_rec, self.context)

        self.test_case.assertEqual(result["task_status"]["status"], "stopped")
        return result

    def __assert_input_sourcing_summary(self, task, stage, status, message, result):

        task_group = self.wfs_access.call_get_task_group_id(task["task_group_id"], self.context)
        input_sourcing = task_group["summary"]["input_sourcing"]

        self.test_case.assertIn("start_time", input_sourcing[stage])
        self.test_case.assertIn("end_time", input_sourcing[stage])
        self.test_case.assertEqual(input_sourcing[stage]["status"], status)
        self.test_case.assertEqual(input_sourcing[stage]["message"], message)
        self.test_case.assertDictEqual(input_sourcing[stage]["result"], result)

    @staticmethod
    def __normalize_date_strings(*args):
        """
        Remove "T" from datetime strings so they will match (T just designates beginning of time segment of string)
        More info at http://www.w3.org/TR/NOTE-datetime
        """
        return tuple([date_string.replace("T", " ") for date_string in args])


###################################################################################################
