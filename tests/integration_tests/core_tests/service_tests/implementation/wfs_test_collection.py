from __future__ import division
from common.service_access.utilities.errors import ServiceCallError
from common.utilities.inversion_of_control import Dependency
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from core.common.utilities.include import *
from core.common.utilities.helpers import ensure_id
from core.service.svc_main.implementation.service_endpoints.endpoint_field_data import RETAIL_INPUT_CHURN_VALIDATION_MATCHES_DB_FIELDS
from core.service.svc_workflow.implementation.task.implementation.task_sorting_helper import get_queue_sort_key
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from core.service.svc_workflow.implementation.task.task_group import WorkflowTaskGroup
import StringIO
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_rir, insert_test_store, insert_test_trade_area, insert_test_white_space_cell_match, insert_test_company_competition_instance


__author__ = "jsternberg"


class WFSTestCollection(ServiceTestCollection):

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

        self.sample_filenames_test_co = [
            "Test_Co_2012_06_04.xlsx",
            "Test_Co_2013_08_30.xlsx"
        ]

        self.sample_filenames_99_cents = ["99_Cents_Only_Stores_2011_07_02.xlsx",
                                          "99_Cents_Only_Stores_2012_10_11.xlsx"]

        self.single_rir_filenames = ["J.CREW_Full_Line_Single_RIR_2011_11_21.xlsx",
                                     "J.CREW_Full_Line_Single_RIR_2011_12_21.xlsx"]

        self.dupe_rir_filenames = ["J.CREW_Full_Line_Dupe_RIR_2012_11_21.xlsx",
                                   "J.CREW_Full_Line_Dupe_RIR_2012_12_21.xlsx"]

        self.three_row_filenames = ["J.CREW_Full_Line_Three_Row_File_2012_11_21.xlsx",
                                    "J.CREW_Full_Line_Three_Row_File_2013_11_21.xlsx"]

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

    def wfs_test_reference_data_workflow_statuses(self):

        service_statuses = self.wfs_access.call_reference_data_entity_workflow_statuses()
        self.test_case.assertEqual(set(service_statuses.keys()), {"new", "in_collection", "in_qc", "published"})

        # check each expected status has the right control attributes
        expected_status_attributes = ["display_name", "description", "viewable_by_role", "editable_by_role"]
        for status in service_statuses:
            for attrib in expected_status_attributes:
                self.test_case.assertIn(attrib, service_statuses[status])

    def wfs_test_retail_input_record_summary_collections(self):

        company_id, file_entity1 = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[0],
                                                                            company_name = 'J.Crew Full Line')
        company_id, file_entity2 = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[1],
                                                                            company_id = company_id)
        task_groups = self.main_access.call_get_data_preset_retail_input_summary()["rows"]
        self.test_case.assertEqual(len(task_groups), 2)

        ########################################################################
        # First file is at index 0 because of ascending date sort
        task_group1 = task_groups[0]
        self.test_case.assertEqual(task_group1["status"],"success")
        self.test_case.assertEqual(task_group1["data"]["source_name"], self.sample_filenames_jcrew_full_line[0])
        self.test_case.assertEqual(task_group1["data"]["company_name"], file_entity1["data"]["company_name"])
        self.test_case.assertEqual(task_group1["unique_key"]["company_id"], file_entity1["data"]["company_id"])
        self.test_case.assertEqual(task_group1["unique_key"]["as_of_date"], file_entity1["data"]["as_of_date"])

        parsing = task_group1["summary"]["input_sourcing"]["parsing"]
        self.test_case.assertEqual(parsing["status"], "success")
        self.test_case.assertEqual(parsing["result"]["num_rirs"], 20)
        start, end = self.__normalize_date_strings(parsing["start_time"], parsing["end_time"])
        self.test_case.assertTrue(start <= end < str(datetime.datetime.utcnow()))

        ########################################################################
        # Second file is at index 1 because of ascending date sort
        task_group2 = task_groups[1]
        self.test_case.assertEqual(task_group2["status"],"success")
        self.test_case.assertEqual(task_group2["data"]["source_name"], self.sample_filenames_jcrew_full_line[1])
        self.test_case.assertEqual(task_group2["data"]["company_name"], file_entity2["data"]["company_name"])
        self.test_case.assertEqual(task_group2["unique_key"]["company_id"], file_entity2["data"]["company_id"])
        self.test_case.assertEqual(task_group2["unique_key"]["as_of_date"], file_entity2["data"]["as_of_date"])

        parsing = task_group2["summary"]["input_sourcing"]["parsing"]
        self.test_case.assertEqual(parsing["status"], "success")
        self.test_case.assertEqual(parsing["result"]["num_rirs"], 24)
        start, end = self.__normalize_date_strings(parsing["start_time"], parsing["end_time"])
        self.test_case.assertTrue(start <= end < str(datetime.datetime.utcnow()))

        # Run churn matching on second file
        self.__run_and_test_churn_matching_task(company_id, file_entity2["data"]["as_of_date"], file_entity2["_id"])

        task_groups = self.main_access.call_get_data_preset_retail_input_summary()["rows"]
        self.test_case.assertEqual(len(task_groups), 2)

        ########################################################################
        # Second file is at index 1 because of ascending date sort
        task_group2 = task_groups[1]
        self.test_case.assertEqual(task_group2["status"],"success")
        self.test_case.assertEqual(task_group2["data"]["source_name"], self.sample_filenames_jcrew_full_line[1])
        self.test_case.assertEqual(task_group2["data"]["company_name"], file_entity2["data"]["company_name"])
        self.test_case.assertEqual(task_group2["unique_key"]["company_id"], file_entity2["data"]["company_id"])
        self.test_case.assertEqual(task_group2["unique_key"]["as_of_date"], file_entity2["data"]["as_of_date"])

        churn_matching = task_group2["summary"]["input_sourcing"]["churn_matching"]
        self.test_case.assertEqual(churn_matching["status"], "success")
        self.test_case.assertEqual(churn_matching["result"]["num_exact_matches"], 4)
        self.test_case.assertEqual(churn_matching["result"]["num_auto_linkable_matches"], 4)
        self.test_case.assertEqual(churn_matching["result"]["num_inexact_matches"], 12)
        self.test_case.assertEqual(churn_matching["result"]["num_mismatches"], 4)
        start, end = self.__normalize_date_strings(churn_matching["start_time"], churn_matching["end_time"])
        self.test_case.assertTrue(start <= end < str(datetime.datetime.utcnow()))

    def wfs_test_task_group_deletion(self):

        self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[0],
                                                                            company_name = 'J.Crew Full Line')

        tasks = self.main_access.wfs.call_task_find(self.context, {})
        task_groups = self.main_access.wfs.call_task_group_find(self.context, {})

        task_group_id = task_groups[0]["_id"]

        self.test_case.assertEqual(len(tasks), 1)
        self.test_case.assertEqual(len(task_groups), 1)
        self.test_case.assertEqual(task_group_id, tasks[0]['task_group_id'])

        # deleting the group should also delete the task
        self.main_access.wfs.call_delete_task_group_id(task_groups[0]["_id"])

        # check that the deletion worked
        tasks = self.main_access.wfs.call_task_find(self.context, {})
        task_groups = self.main_access.wfs.call_task_group_find(self.context, {})

        self.test_case.assertEqual(len(tasks), 0)
        self.test_case.assertEqual(len(task_groups), 0)

    def wfs_test_task_deletion(self):

        refdata = self.main_access.wfs.call_reference_data_entity_task_stages()

        as_of_date = "2013-01-21 00:00:00"

        # add one of each manual task to the db
        for flow, processes in refdata.iteritems():
            for process, stages in processes.iteritems():
                for stage, meta in stages.iteritems():
                    if meta["manual"]:
                        sort_key = get_queue_sort_key(as_of_date)
                        #self.__call_task_new(flow, process, stage, {"sort_key": sort_key}, self.context)
                        self.main_access.wfs.call_task_new(flow, process, stage, {"sort_key": sort_key}, self.context)

        tasks = self.main_access.wfs.call_task_find(self.context, {})
        self.test_case.assertEqual(len(tasks), 7)
        for task in tasks:
            self.test_case.assertTrue("status" in task["task_status"])
            self.test_case.assertTrue("input" in task)
            self.test_case.assertTrue("task_group_id" in task)
            self.test_case.assertTrue(isinstance(task["sort_key"], int))

        # delete the tasks and see if anything is still there
        for task in tasks:
            self.main_access.wfs.call_delete_task_id(task["_id"])

        tasks = self.main_access.wfs.call_task_find(self.context, {})
        self.test_case.assertEqual(len(tasks), 0)

    def wfs_test_add_empty_task_raises_error(self):

        flow = "retail_curation"
        process = "input_sourcing"
        stage = "churn_validation"

        task_recs = [None, {}]

        for task_rec in task_recs:
            self.test_case.assertRaises(ServiceCallError,
                                        self.main_access.wfs.call_task_new,
                                        *(flow, process, stage, task_rec, self.context))

            self.test_case.assertRaises(ServiceCallError,
                                        self.main_access.wfs.call_task_batch_new,
                                        *(flow, process, stage, [task_rec], self.context))

    def wfs_test_retail_input_file_deletion_task(self):
        """
        Test that deleting a file deletes both the file in RDS and the MDS file entity, the task group,
        and most correct rirs that may belong to the file.
        """
        # clear the mds database to get rid of rogue test files
        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()
        self.rds_access.call_delete_folder_by_name('root/')

        name = "root/trunk/branches/leaves/Banana.txt"
        test_files = {"Banana.txt": StringIO.StringIO("Banana")}
        additional_data = {"this is": "a banana"}

        mds_response = self.main_access.call_add_files("root/trunk/branches/leaves/", self.context, test_files, additional_data)

        self.test_case.assertIn(name, mds_response)

        mds_file_id = mds_response[name]
        rds_file_response = self.rds_access.call_get_file_by_name(name, self.context)
        self.test_case.assertEqual("Banana", rds_file_response.content)

        # add a most correct rir that belongs to this file
        company_id = insert_test_company()
        rir_id_A = insert_test_rir(self.context, company_id, '1')
        store_id = self.store_helper.create_new_store(self.context, rir_id_A, async=False)

        # link rir_id_A to the file
        self.mds_access.call_add_link('file', mds_file_id, 'retail_input_file',
                                      'retail_input_record', rir_id_A, 'retail_input_record',
                                      'retail_input', self.context)

        # create a task group belonging to this file
        unique_key = {"source_id": mds_file_id}
        processes = ["input_sourcing"]
        task_group_rec = WorkflowTaskGroup.get_retail_curation_structure(unique_key, processes)
        task_group = self.wfs_access.call_task_group_new(task_group_rec, self.context)
        self.test_case.assertIsNotNone(task_group)

        # create a closed store task which doesn't have a task group
        task_rec = {
            "input": {
                "company_id": company_id,
                "source_id": mds_file_id,
                "filename": name,
                "spawn_async_tasks": False
            },
            "meta": {
                "async": False
            }
        }

        task = self.main_access.wfs.call_task_new("retail_curation", "company_data_curation",
                                                  "closed_store_validation", task_rec, self.context)

        # find the task group
        task_group_query = {'query': {'unique_key.source_id': mds_file_id}}
        task_group_id = self.wfs_access.call_task_group_find(self.context, task_group_query)[0]['_id']
        self.test_case.assertEqual(task_group_id, task_group['_id'])

        # find the task id
        task_query = {'query': {'input.source_id': mds_file_id}}
        task_id = self.wfs_access.call_task_find(self.context, task_query)[0]['_id']
        self.test_case.assertEqual(task_id, task['_id'])

        # we are good here, the file is in RDS and the file entity is in MDS, and the tasks are there
        # so we know the delete function has to work when we call it below
        self.wfs_access.call_task_new("retail_curation", "company_data_curation",
                                      "input_file_deletion", task_rec, self.context)

        # now check that the file entity is not in MDS
        with self.test_case.assertRaises(ServiceCallError) as cm:
            self.main_access.mds.call_get_entity('file', mds_response[name])
        self.test_case.assertIn('NotFoundError', cm.exception.message)

        # check that the file is not in RDS
        with self.test_case.assertRaises(ServiceCallError) as cm:
            self.rds_access.call_get_file_by_name(name, self.context)
            # NoFile is the GridFS official exception for missing files
        self.test_case.assertIn('NoFile', cm.exception.message)

        # check that the task group is gone gone gone
        task_group_result = self.wfs_access.call_task_group_find(self.context, task_group_query)
        self.test_case.assertEqual([], task_group_result)

        # check that the rir_id_A and store are gone
        with self.test_case.assertRaises(ServiceCallError) as cm:
            self.main_access.mds.call_get_entity('retail_input_record', rir_id_A)
        self.test_case.assertIn('NotFoundError', cm.exception.message)

        with self.test_case.assertRaises(ServiceCallError) as cm:
            self.main_access.mds.call_get_entity('store', store_id)
        self.test_case.assertIn('NotFoundError', cm.exception.message)

    def wfs_test_retail_input_file_deletion_task__deletes_qc_tasks(self):

        company_id, file_entity1 = self.__upload_and_test_retail_input_file(self.sample_filenames_test_co[0],
                                                                            company_name='Test Co')
        company_id, file_entity2 = self.__upload_and_test_retail_input_file(self.sample_filenames_test_co[1],
                                                                            company_id=company_id)

        # Create and start closed store search task
        params = {
            "query": {
                "unique_key.company_id": company_id,
                "unique_key.as_of_date": file_entity2["data"]["as_of_date"],
                "unique_key.source_id": file_entity2["_id"]
            }
        }
        task_group = self.main_access.wfs.call_task_group_find(self.context, params)[0]

        task_rec = {
            "task_group_id": task_group["_id"],
            "input": {
                "company_recs": [
                    {
                        "company_id": company_id,
                        "primary_industry_id": self.context["team_industries"][0]
                    }
                ]
            }
        }
        self.wfs_access.call_task_new("retail_curation", "company_data_curation",
                                      "closed_store_searching", task_rec, self.context)

        # Double-check that there is 1 closed store validation tasks
        params = {
            "query": {
                "flow": "retail_curation",
                "process": "company_data_curation",
                "stage": "closed_store_validation",
                "task_status.status": "open"
            }
        }
        tasks = self.wfs_access.call_task_find(self.context, params)

        # sort tasks by id so that the order is consistent
        tasks = sorted(tasks, key = lambda task: task["_id"])

        # Complete closed store validation task
        target_rir_id = self.__get_and_test_next_closed_store_validation_target_rir()
        validation_data = {
            "taskID": tasks[0]["_id"],
            "decision": "no-link",
            "downstream": "close"
        }
        result = self.__save_and_test_validation(validation_data, stage="closed_store_validation")

        # Create QC task for target RIR
        data = {
            "rirID": target_rir_id,
            "stage": "closed_store_validation_qc"
        }
        self.main_access.call_post_retail_input_validation_qc(data, self.context)

        # Create file deletion task for second file
        task_rec = {
            "input": {
                "company_id": company_id,
                "source_id": file_entity2["_id"],
                "filename": file_entity2["name"],
                "spawn_async_tasks": False
            },
            "meta": {
                "async": False
            }
        }
        self.wfs_access.call_task_new("retail_curation", "company_data_curation",
                                      "input_file_deletion", task_rec, self.context)

        # Create file deletion task for first file
        task_rec = {
            "input": {
                "company_id": company_id,
                "source_id": file_entity1["_id"],
                "filename": file_entity1["name"],
                "spawn_async_tasks": False
            },
            "meta": {
                "async": False
            }
        }
        self.wfs_access.call_task_new("retail_curation", "company_data_curation",
                                      "input_file_deletion", task_rec, self.context)

        # Make sure no stores remain
        params = {}
        stores = self.main_access.mds.call_find_entities_raw("store", params, self.context)
        self.test_case.assertEqual(stores, [])

        # Make sure no RIRs remain
        params = {}
        rirs = self.main_access.mds.call_find_entities_raw("retail_input_record", params, self.context)
        self.test_case.assertEqual(rirs, [])

        # Make sure no tasks remain
        params = {
            'query': {
                'flow': 'retail_curation'
            }
        }
        tasks = self.main_access.wfs.call_task_find(self.context, params)

        # File deletion tasks should not delete themselves
        self.test_case.assertEqual(len(tasks), 2)

    def wfs_test_file_deletion_does_not_delete_stores_before_last_rirs(self):

        # Upload first file
        company_id, file_entity1 = self.__upload_and_test_retail_input_file(self.sample_filenames_test_co[0],
                                                                            company_name='Test Co')

        # Upload second (duplicate) file
        company_id, file_entity2 = self.__upload_and_test_retail_input_file(self.sample_filenames_test_co[1],
                                                                            company_id=company_id)

        # Run match
        self.__run_and_test_churn_matching_task(company_id, file_entity2["data"]["as_of_date"], file_entity2["_id"])

        # Create file deletion task for second file
        task_rec = {
            "input": {
                "company_id": company_id,
                "source_id": file_entity2["_id"],
                "filename": file_entity2["name"],
                "spawn_async_tasks": False
            },
            "meta": {
                "async": False
            }
        }
        self.wfs_access.call_task_new("retail_curation", "company_data_curation",
                                      "input_file_deletion", task_rec, self.context)

        # Make sure multiple stores exist
        params = {}
        stores = self.main_access.mds.call_find_entities_raw("store", params, self.context)

        self.test_case.assertTrue(len(stores) > 0)

    def wfs_test_retail_input_file_deletion_task__multiple_files_deleted_out_of_order(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.single_rir_filenames[0], self.single_rir_filenames[1], 'J.Crew Full Line')

        # validate task group summary was set up properly
        self.wfs_access.call_get_task_group_id(task["task_group_id"], self.context)

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
                    "input": {"company_recs": [{"company_id": company_id, "primary_industry_id": self.context["team_industries"][0]}]}}
        self.wfs_access.call_task_new("retail_curation", "company_data_curation", "closed_store_searching", task_rec, self.context)

        # Double-check that there is 1 closed store validation tasks
        params = {"query": {"flow": "retail_curation", "process": "company_data_curation",
                            "stage": "closed_store_validation", "task_status.status": "open"}}
        tasks = self.wfs_access.call_task_find(self.context, params = params)

        self.__get_and_test_next_closed_store_validation_target_rir()
        validation_data = {"taskID": tasks[0]["_id"],
                           "decision": "qc",
                           "rirToQc": "target"}
        self.__save_and_test_validation(validation_data, stage = "closed_store_validation")

        company_id, file_entity2 = self.__upload_and_test_retail_input_file(self.single_rir_filenames[2], company_id = company_id)
        self.__run_and_test_churn_matching_task(company_id, file_entity2["data"]["as_of_date"],
                                                               file_entity2["_id"])

        target_rir_id, task = self.__get_and_test_next_churn_validation_target_rir(None)
        self.__get_and_test_validation_matches(target_rir_id, company_id, task["_id"])

        # Create file deletion task for second file
        task_rec = {
            "input": {
                "company_id": company_id,
                "source_id": file_entity2["_id"],
                "filename": file_entity2["name"],
                "spawn_async_tasks": False
            },
            "meta": {
                "async": False
            }
        }
        self.wfs_access.call_task_new("retail_curation", "company_data_curation", "input_file_deletion", task_rec, self.context)

        # Create file deletion task for second file
        task_rec = {
            "input": {
                "company_id": company_id,
                "source_id": file_entity1["_id"],
                "filename": file_entity1["name"],
                "spawn_async_tasks": False
            },
            "meta": {
                "async": False
            }
        }
        self.wfs_access.call_task_new("retail_curation", "company_data_curation", "input_file_deletion", task_rec, self.context)

        # Make sure no RIRs remain
        rirs = self.main_access.mds.call_find_entities_raw("retail_input_record", params = {}, context = self.context)
        self.test_case.assertEqual(rirs, [])

        # Make sure no tasks remain
        tasks = self.main_access.wfs.call_task_find(context_rec = self.context, params = {})
        self.test_case.assertEqual(tasks, [])

    def wfs_test_find_manual_tasks(self):

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

        self.main_access.call_post_retail_input_validation_qc({"taskID": task["_id"]}, self.context)

        params = {}
        tasks = self.wfs_access.call_find_manual_tasks(params, self.context)

        # 2 churn validation tasks created from RIRs in files
        self.test_case.assertEqual(len(tasks), 3)

        params = {"query": {"task_status.status": "in_progress"}}
        tasks = self.wfs_access.call_find_manual_tasks(params, self.context)
        self.test_case.assertEqual(len(tasks), 1)

        if company_id:
            self.__delete_rds_file(file_entity1["name"])
            self.__delete_rds_file(file_entity2["name"])

    def test_wfs_test_company_deletion(self):

        (company_id,
         file_entity1,
         file_entity2,
         target_rir_id,
         suggested_match_list,
         task) = self.__prepare_churn_validation(self.single_rir_filenames[0],
                                                 self.single_rir_filenames[1], 'J.Crew Full Line')

        # create a second published retail banner, for the cci
        company_id_2 = insert_test_company(ctype="retail_banner", workflow_status="published", use_new_json_encoder=True)

        # insert a test store
        store_id = insert_test_store(company_id, None)

        # insert a trade area
        insert_test_trade_area(store_id, company_id)

        # insert a to and a from cci - MDS creates the actual CCIs from the /pair call
        insert_test_company_competition_instance(company_id, company_id_2)

        # insert a whitespace match
        insert_test_white_space_cell_match(company_id, 2)

        initial_files = self.mds_access.call_find_entities_raw("file", {})
        self.test_case.assertTrue(len(initial_files) is 2)

        # Create company deletion task
        task_rec = {
            "input": {
                "company_id": company_id,
                "company_name": "J.Crew Full Line",
                "spawn_async_tasks": False
            },
            "meta": {
                "async": False
            }
        }
        task_result = self.wfs_access.call_task_new("retail_curation", "company_data_curation",
                                                    "company_deletion", task_rec, self.context)

        # make sure the company no longer exists -- get should return an error
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.mds.call_get_entity,
                                    *('company', company_id))

        # get related entities
        companies = self.mds_access.call_find_entities_raw("company", { "query": { "_id": company_id }})
        files = self.mds_access.call_find_entities_raw("file", {})
        rirs = self.mds_access.call_find_entities_raw("retail_input_record", {})
        addresses = self.mds_access.call_find_entities_raw("address", {})
        stores = self.mds_access.call_find_entities_raw("store", {}, self.context)
        trade_areas = self.mds_access.call_find_entities_raw("trade_area", {}, self.context)
        ccis = self.mds_access.call_find_entities_raw("company_competition_instance", {}, self.context)
        white_space_matches = self.mds_access.call_find_entities_raw("white_space_grid_cell_match", {}, self.context)

        # assert they are gone!
        self.test_case.assertEqual(companies, [])
        self.test_case.assertEqual(files, [])
        self.test_case.assertEqual(rirs, [])
        self.test_case.assertEqual(addresses, [])
        self.test_case.assertEqual(stores, [])
        self.test_case.assertEqual(trade_areas, [])
        self.test_case.assertEqual(ccis, [])
        self.test_case.assertEqual(white_space_matches, [])

        # make sure workflow is empty too
        tasks = self.wfs_access.call_task_find(self.context, {})
        task_groups = self.wfs_access.call_task_group_find(self.context, {})

        # get task stages
        task_stages = [task["stage"] for task in tasks]

        # verify tasks
        self.test_case.assertEqual(len(tasks), 1)
        self.test_case.assertTrue(task_stages, ["company_deletion"])
        self.test_case.assertEqual(task_groups, [])

        # make sure company was archived properly
        fields = ["_id", "original_id"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", entity_fields=fields)["params"]
        archived_companies = self.mds_access.call_find_entities_raw("archive", params)

        self.test_case.assertEqual(archived_companies[0]["_id"], task_result["task_status"]["result"]["archived_company_id"])
        self.test_case.assertEqual(archived_companies[0]["original_id"], company_id)

        # make sure the competitor company is marked as needing analytics
        query = { "_id": ensure_id(company_id_2) }
        fields = ["_id", "data"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields)["params"]
        companies_2 = self.mds_access.call_find_entities_raw("company", params)

        self.test_case.assertEqual(companies_2[0]["data"]["workflow"]["analytics"]["status"], "needs_plan_b")

    def test_wfs_test_update_task_group(self):

        # create a retail input file task group (the only one we have now)
        company_id, file_entity1 = self.__upload_and_test_retail_input_file(self.sample_filenames_jcrew_full_line[0], company_name = 'J.Crew Full Line')

        # get the first task group
        task_groups = self.main_access.wfs.call_task_group_find(self.context, {})
        task_group = task_groups[0]
        task_group_id = task_group["_id"]

        # make sure that the company is correct
        self.test_case.assertEqual(task_group["data"]["company_name"], 'J.Crew Full Line')

        # update the company name to be different
        params = { "data": { "company_name": "chicken_woot" }}
        self.main_access.wfs.call_update_task_group_id(task_group_id, self.context, params)

        # query again and verify that it hasn't changed
        task_groups = self.main_access.wfs.call_task_group_find(self.context, {})
        task_group = task_groups[0]

        # make sure that the company is correct
        self.test_case.assertEqual(task_group["data"]["company_name"], 'chicken_woot')

    def test_wfs_archive_task(self):

        # make a task
        task_rec = {"input":{"whatever":"stuff"}}
        task = self.__call_task_new("retail_curation", "input_sourcing", "churn_validation", task_rec, self.context)

        # archive it
        self.wfs_access.call_archive_task_id(task["_id"], self.context)

        # check to see that we can find it in the archive
        params = {"archived": True}
        archived_task = self.wfs_access.call_get_task_id(task["_id"], self.context, params)

        self.test_case.assertEqual(task["_id"], archived_task["original_id"])

        # swap out IDs in the archived task, remove the archiving keys
        archived_task["_id"] = archived_task["original_id"]
        del archived_task["original_id"]
        del archived_task["archived"]
        del task["archived"]
        del task["original_id"]

        # now compare entire dict -- they should be the same
        self.test_case.assertEqual(task, archived_task)


    ##------------------------## private methods ##------------------------##

    def __call_task_new(self, flow, process, stage, task_rec, context_rec):

        if "meta" not in task_rec:
            task_rec["meta"] = {}
        if "input" not in task_rec:
            task_rec["input"] = {}

        if self.async_mode:
            task_rec["meta"]["async"] = True

            result = self.main_access.wfs.call_task_new(flow, process, stage, task_rec, self.context)
            self.test_case.assertIn("task_status", result)

            self.logger.info("Submitted async task:\n%s\nResult:\n%s\n",
                             task_rec, result)

            task_id = ensure_id(result["_id"])

            self.test_case.assertEqual(result["task_status"], {"status": "in_progress", "result": None})

            tries = self.wait_secs
            while result["task_status"]["status"] == "in_progress" and tries > 0:
                tries -= 1
                time.sleep(1)
                result = self.main_access.wfs.call_get_task_id(task_id)
                self.test_case.assertIn("task_status", result)

            self.test_case.assertEqual(result["task_status"]["status"], "success")

        else:
            task_rec["meta"]["async"] = False

            result = self.main_access.wfs.call_task_new(flow, process, stage, task_rec, context_rec)
            self.test_case.assertIn("task_status", result)

            self.logger.info("Submitted sync task:\n%s\nResult:\n%s\n",
                             task_rec, result)

        return result

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

    def __upload_and_test_retail_input_file(self, filename, company_name = None, company_id = None):

        company_id, file_id1, task, task_group = self.__upload_and_parse_file(filename, company_name = company_name,
                                                                              company_id = company_id)

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

        return exact_match_id_set, auto_linkable_id_set, inexact_match_id_set, mismatch_id_set

    def __get_and_test_next_churn_validation_target_rir(self, inexact_and_mismatch_ids):
        """

        """
        # Use retail input endpoint to get next validation target
        timestamp = str(datetime.datetime.utcnow())
        params = {"flow": "retail_curation", "process": "input_sourcing", "stage": "churn_validation"}
        result = self.main_access.call_get_retail_input_record_validation_next_target(params, self.context)

        self.test_case.assertIn("rir", result)
        self.test_case.assertIn("task_rec", result)
        task_rec = result["task_rec"]
        target_rir_id = task_rec["input"]["target_rir_id"]
        if inexact_and_mismatch_ids:
            self.test_case.assertIn(target_rir_id, inexact_and_mismatch_ids)

        # Check task data
        params = {"has_metadata": True}
        task = self.wfs_access.call_get_task_id(task_rec["_id"], self.context, params)
        self.test_case.assertGreater(task["meta"]["updated_at"], timestamp)
        self.test_case.assertEqual(task["task_status"]["status"], "in_progress")

        return target_rir_id, task

    def __get_and_test_next_closed_store_validation_target_rir(self):
        """

        """
        # Use retail input endpoint to get next validation target
        timestamp = str(datetime.datetime.utcnow())
        params = {"flow": "retail_curation", "process": "company_data_curation", "stage": "closed_store_validation"}
        result = self.main_access.call_get_retail_input_record_validation_next_target(params, self.context)

        self.test_case.assertIn("rir", result)
        self.test_case.assertIn("task_rec", result)
        task_rec = result["task_rec"]
        target_rir_id = task_rec["input"]["target_rir_id"]

        # Check task data
        params = {"has_metadata": True}
        task = self.wfs_access.call_get_task_id(task_rec["_id"], self.context, params)
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

    def __prepare_churn_validation(self, filename1, filename2, company_name):

        company_id, file_entity1 = self.__upload_and_test_retail_input_file(filename1, company_name = company_name)
        company_id, file_entity2 = self.__upload_and_test_retail_input_file(filename2, company_id = company_id)
        match_result = self.__run_and_test_churn_matching_task(company_id, file_entity2["data"]["as_of_date"],
                                                               file_entity2["_id"])

        if filename1 == self.sample_filenames_jcrew_full_line[0] and filename2 == self.sample_filenames_jcrew_full_line[1]:
            (exact_match_id_set,
             auto_linkable_id_set,
             inexact_match_id_set,
             mismatch_id_set) = self.__compare_and_test_jcrew_file1_vs_file2_results(match_result, file_entity2)
            inexact_and_mismatch_ids = inexact_match_id_set | mismatch_id_set
        else:
            inexact_and_mismatch_ids = None

        target_rir_id, task = self.__get_and_test_next_churn_validation_target_rir(inexact_and_mismatch_ids)

        suggested_match_list = self.__get_and_test_validation_matches(target_rir_id, company_id, task["_id"])

        return company_id, file_entity1, file_entity2, target_rir_id, suggested_match_list, task

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

        test_data = dict(validation_data, taskID = "")
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(test_data, self.context), async=False)
        self.main_access.wfs.call_find_and_modify_task(params=reset_task)

        test_data = dict(validation_data, decision = "")
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(test_data, self.context), async=False)
        self.main_access.wfs.call_find_and_modify_task(params=reset_task)

        if stage == "churn_validation":
            test_data = dict(validation_data, decision = "link", rirLinkID = "")
            self.test_case.assertRaises(ServiceCallError,
                                        self.main_access.call_post_retail_input_record_validation_save,
                                        *(test_data, self.context), async=False)
            self.main_access.wfs.call_find_and_modify_task(params=reset_task)

            test_data = dict(validation_data, decision = "link", dataToUse = "")
            self.test_case.assertRaises(ServiceCallError,
                                        self.main_access.call_post_retail_input_record_validation_save,
                                        *(test_data, self.context), async=False)
            self.main_access.wfs.call_find_and_modify_task(params=reset_task)

            test_data = dict(validation_data, decision = "link", dataToUse = "asdf")
            self.test_case.assertRaises(ServiceCallError,
                                        self.main_access.call_post_retail_input_record_validation_save,
                                        *(test_data, self.context), async=False)
            self.main_access.wfs.call_find_and_modify_task(params=reset_task)

        test_data = dict(validation_data, decision = "no-link", downstream = "")
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(test_data, self.context), async=False)
        self.main_access.wfs.call_find_and_modify_task(params=reset_task)

        test_data = dict(validation_data, decision = "no-link", downstream = "asdf")
        self.test_case.assertRaises(ServiceCallError,
                                    self.main_access.call_post_retail_input_record_validation_save,
                                    *(test_data, self.context), async=False)
        self.main_access.wfs.call_find_and_modify_task(params=reset_task)

    @staticmethod
    def __normalize_date_strings(*args):
        """
        Remove "T" from datetime strings so they will match (T just designates beginning of time segment of string)
        More info at http://www.w3.org/TR/NOTE-datetime
        """
        return tuple([date_string.replace("T", " ") for date_string in args])




###################################################################################################
