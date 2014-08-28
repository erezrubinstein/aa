from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.service_access.utilities.errors import RecInputError
from common.utilities.inversion_of_control import Dependency, dependencies
from core.service.svc_workflow.implementation.task.task_group import WorkflowTaskGroup
import unittest
import mox
import copy
import datetime
import pprint
from tests.unit_tests.core_tests.data_stub_helpers import get_add_one_rir_task_group_update_params, get_input_sourcing_task_group_summary_dict

__author__ = 'vgold'


class WorkflowTaskGroupTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(WorkflowTaskGroupTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_workflow_service.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

    def doCleanups(self):

        super(WorkflowTaskGroupTests, self).doCleanups()
        dependencies.clear()

    def test_get_summary_structure_for_processes(self):

        input_sourcing_dict = get_input_sourcing_task_group_summary_dict()

        self.assertEqual(
            WorkflowTaskGroup._get_summary_structure_for_processes(["input_sourcing"]),
            input_sourcing_dict
        )
        self.assertEqual(
            WorkflowTaskGroup._get_summary_structure_for_processes(["asdf", "input_sourcing"]),
            input_sourcing_dict
        )
        self.assertEqual(WorkflowTaskGroup._get_summary_structure_for_processes(["asdf"]), {})

    def test_create_new_task_group_rec(self):

        unique_key = {"asdf": "jkl;"}
        processes = ["input_sourcing"]
        task_group_rec = dict(WorkflowTaskGroup.get_retail_curation_structure(unique_key, processes), context_data = self.context)
        task_stage_ref_data = self.__get_task_stage_ref_data()

        for required_field in WorkflowTaskGroup.required_fields:
            task_group = self.__get_dict_without_keys(task_group_rec, [required_field])
            self.assertRaises(RecInputError, WorkflowTaskGroup._create_new_task_group_rec, *(task_group, task_stage_ref_data))

        task_group = dict(task_group_rec, flow = "asdf")
        self.assertRaises(RecInputError, WorkflowTaskGroup._create_new_task_group_rec, *(task_group, task_stage_ref_data))

        task_group = dict(task_group_rec, unique_key = "asdf")
        self.assertRaises(RecInputError, WorkflowTaskGroup._create_new_task_group_rec, *(task_group, task_stage_ref_data))

        task_group = dict(task_group_rec, unique_key = {})
        self.assertRaises(RecInputError, WorkflowTaskGroup._create_new_task_group_rec, *(task_group, task_stage_ref_data))

        task_group = dict(task_group_rec, processes = "asdf")
        self.assertRaises(RecInputError, WorkflowTaskGroup._create_new_task_group_rec, *(task_group, task_stage_ref_data))

        task_group = dict(task_group_rec, processes = [])
        self.assertRaises(RecInputError, WorkflowTaskGroup._create_new_task_group_rec, *(task_group, task_stage_ref_data))

        task_group = dict(task_group_rec, processes = ["asdf"])
        self.assertRaises(RecInputError, WorkflowTaskGroup._create_new_task_group_rec, *(task_group, task_stage_ref_data))

        task_group = WorkflowTaskGroup._create_new_task_group_rec(task_group_rec, task_stage_ref_data)
        self.assertTrue(isinstance(task_group, dict))

    def test_determine_churn_validation_percent_complete(self):

        # __new__ creates the instance without running __init__
        task_group = WorkflowTaskGroup.__new__(WorkflowTaskGroup)
        task_group.summary = get_input_sourcing_task_group_summary_dict()

        percent_complete = WorkflowTaskGroup._determine_churn_validation_percent_complete(0, 1)
        self.assertEqual(percent_complete, 0.0)

        percent_complete = WorkflowTaskGroup._determine_churn_validation_percent_complete(1, 0)
        self.assertEqual(percent_complete, 1.0)

        percent_complete = WorkflowTaskGroup._determine_churn_validation_percent_complete(3, 9)
        self.assertEqual(percent_complete, 3.0 / 9.0)

    def __get_current_process_and_stage(self):

        # __new__ creates the instance without running __init__
        task_group = WorkflowTaskGroup.__new__(WorkflowTaskGroup)
        task_group._task_group_message_ref_data = self.__get_task_group_message_priority_ref_data()
        task_group.processes = ["input_sourcing"]
        task_group.summary = get_input_sourcing_task_group_summary_dict()

        proc, stage, is_manual = WorkflowTaskGroup._get_current_process_and_stage(task_group)
        self.assertEqual(proc, "input_sourcing")
        self.assertEqual(stage, "parsing")
        self.assertEqual(is_manual, False)

        task_group.summary["input_sourcing"]["churn_matching"]["status"] = "skipped"
        task_group.summary["input_sourcing"]["churn_matching"]["message"] = "Churn matching was skipped."

        stage = WorkflowTaskGroup._get_current_process_and_stage(task_group)
        self.assertEqual(proc, "input_sourcing")
        self.assertEqual(stage, "churn_matching")
        self.assertEqual(is_manual, False)

        task_group.summary["input_sourcing"]["churn_validation"]["status"] = "failure"
        task_group.summary["input_sourcing"]["churn_validation"]["message"] = "Churn validation failed."

        stage = WorkflowTaskGroup._get_current_process_and_stage(task_group)
        self.assertEqual(proc, "input_sourcing")
        self.assertEqual(stage, "churn_validation")
        self.assertEqual(is_manual, True)

    def test_determine_task_group_status__success_1(self):

        # __new__ creates the instance without running __init__
        task_group = WorkflowTaskGroup.__new__(WorkflowTaskGroup)
        task_group.summary = get_input_sourcing_task_group_summary_dict()
        task_group._task_group_status_ref_data = self.__get_task_group_status_ref_data()

        task_group._get_highest_priority_message = self.mox.CreateMockAnything()

        # Any stage with status "not_ready" is ignored
        message_dict = {"parsing": {"message": task_group.summary["input_sourcing"]["parsing"]["message"], "date": None}}
        task_group._get_highest_priority_message(message_dict).AndReturn(("helo", "there"))

        self.mox.ReplayAll()

        status, message, message_date = WorkflowTaskGroup._determine_group_status(task_group)
        self.assertEqual(status, "success")
        self.assertEqual(message, "helo")
        self.assertEqual(message_date, "there")

    def test_determine_task_group_status__success_2(self):

        # __new__ creates the instance without running __init__
        task_group = WorkflowTaskGroup.__new__(WorkflowTaskGroup)
        task_group.summary = get_input_sourcing_task_group_summary_dict()
        task_group._task_group_status_ref_data = self.__get_task_group_status_ref_data()

        task_message_date = datetime.datetime.utcnow()
        task_group.summary["input_sourcing"]["parsing"]["status"] = "success"
        task_group.summary["input_sourcing"]["parsing"]["message"] = "File parsing is ready."
        task_group.summary["input_sourcing"]["parsing"]["message_date"] = task_message_date

        task_group.summary["input_sourcing"]["churn_matching"]["status"] = "skipped"
        task_group.summary["input_sourcing"]["churn_matching"]["message"] = "Churn matching was skipped."
        task_group.summary["input_sourcing"]["churn_matching"]["message_date"] = task_message_date

        task_group.summary["input_sourcing"]["churn_validation"]["status"] = "skipped"
        task_group.summary["input_sourcing"]["churn_validation"]["message"] = "Churn validation was skipped."
        task_group.summary["input_sourcing"]["churn_validation"]["message_date"] = task_message_date

        task_group._get_highest_priority_message = self.mox.CreateMockAnything()
        message_dict = {"parsing": {"message": task_group.summary["input_sourcing"]["parsing"]["message"], "date": task_message_date},
                        "churn_matching": {"message": task_group.summary["input_sourcing"]["churn_matching"]["message"], "date": task_message_date},
                        "churn_validation": {"message": task_group.summary["input_sourcing"]["churn_validation"]["message"], "date": task_message_date}}
        task_group._get_highest_priority_message(message_dict).AndReturn((task_group.summary["input_sourcing"]["churn_matching"]["message"],
                                                                          task_group.summary["input_sourcing"]["churn_matching"]["message_date"]))

        self.mox.ReplayAll()

        status, message, message_date = WorkflowTaskGroup._determine_group_status(task_group)
        self.assertEqual(status, "success")
        self.assertEqual(message, task_group.summary["input_sourcing"]["churn_matching"]["message"])
        self.assertEqual(message_date, task_group.summary["input_sourcing"]["churn_matching"]["message_date"])

    def test_determine_task_group_status__in_progress(self):

        # __new__ creates the instance without running __init__
        task_group = WorkflowTaskGroup.__new__(WorkflowTaskGroup)
        task_group.summary = get_input_sourcing_task_group_summary_dict()

        task_message_date = datetime.datetime.utcnow()
        task_group.summary["input_sourcing"]["parsing"]["status"] = "in_progress"
        task_group.summary["input_sourcing"]["parsing"]["message"] = "Still parsing..."
        task_group.summary["input_sourcing"]["parsing"]["message_date"] = task_message_date

        task_group.summary["input_sourcing"]["churn_matching"]["status"] = "in_progress"
        task_group.summary["input_sourcing"]["churn_matching"]["message"] = "Still matching..."
        task_group.summary["input_sourcing"]["churn_matching"]["message_date"] = task_message_date

        task_group._task_group_status_ref_data = self.__get_task_group_status_ref_data()

        task_group._get_highest_priority_message = self.mox.CreateMockAnything()
        message_dict = {"parsing": {"message": task_group.summary["input_sourcing"]["parsing"]["message"], "date": task_message_date},
                        "churn_matching": {"message": task_group.summary["input_sourcing"]["churn_matching"]["message"], "date": task_message_date}}
        task_group._get_highest_priority_message(message_dict).AndReturn((task_group.summary["input_sourcing"]["churn_matching"]["message"],
                                                                          task_group.summary["input_sourcing"]["churn_matching"]["message_date"]))

        self.mox.ReplayAll()

        status, message, message_date = WorkflowTaskGroup._determine_group_status(task_group)
        self.assertEqual(status, "in_progress")
        self.assertEqual(message, task_group.summary["input_sourcing"]["churn_matching"]["message"])
        self.assertEqual(message_date, task_group.summary["input_sourcing"]["churn_matching"]["message_date"])

    def test_determine_task_group_status__failure(self):

        # __new__ creates the instance without running __init__
        task_group = WorkflowTaskGroup.__new__(WorkflowTaskGroup)
        task_group.summary = get_input_sourcing_task_group_summary_dict()

        end_date = datetime.datetime.utcnow()
        task_group.summary["input_sourcing"]["parsing"]["status"] = "failure"
        task_group.summary["input_sourcing"]["parsing"]["message"] = "Failed parsing..."
        task_group.summary["input_sourcing"]["parsing"]["message_date"] = end_date

        task_group.summary["input_sourcing"]["churn_matching"]["status"] = "failure"
        task_group.summary["input_sourcing"]["churn_matching"]["message"] = "Failed matching..."
        task_group.summary["input_sourcing"]["churn_matching"]["message_date"] = end_date

        task_group._task_group_status_ref_data = self.__get_task_group_status_ref_data()

        task_group._get_highest_priority_message = self.mox.CreateMockAnything()
        message_dict = {"parsing": {"message": task_group.summary["input_sourcing"]["parsing"]["message"], "date": end_date},
                        "churn_matching": {"message": task_group.summary["input_sourcing"]["churn_matching"]["message"], "date": end_date}}
        task_group._get_highest_priority_message(message_dict).AndReturn((task_group.summary["input_sourcing"]["churn_matching"]["message"],
                                                                          task_group.summary["input_sourcing"]["churn_matching"]["message_date"]))

        self.mox.ReplayAll()

        status, message, message_date = WorkflowTaskGroup._determine_group_status(task_group)
        self.assertEqual(status, "failure")
        self.assertEqual(message, task_group.summary["input_sourcing"]["churn_matching"]["message"])
        self.assertEqual(message_date, task_group.summary["input_sourcing"]["churn_matching"]["message_date"])

    def test_get_highest_priority_message(self):

        # __new__ creates the instance without running __init__
        task_group = WorkflowTaskGroup.__new__(WorkflowTaskGroup)
        task_group.summary = get_input_sourcing_task_group_summary_dict()
        task_group._task_group_message_ref_data = self.__get_task_group_message_priority_ref_data()

        message_dict = {"parsing": {"message": 1, "date": None},
                        "churn_validation": {"message": 3, "date": None},
                        "churn_matching": {"message": 2, "date": None},
                        "asdf": {"message": 4, "date": None}}
        message = WorkflowTaskGroup._get_highest_priority_message(task_group, message_dict)
        self.assertEqual(message, (3, None))

    def test_update(self):
        
        unique_key = {"asdf": "jkl;"}
        processes = ["input_sourcing"]
        task_group_rec = WorkflowTaskGroup.get_retail_curation_structure(unique_key, processes)
        task_group_rec = dict(task_group_rec, context_data = self.context)
        task_group = WorkflowTaskGroup.dict_init(self.cfg, self.logger, task_group_rec,
                                                 self.__get_task_group_status_ref_data(),
                                                 self.__get_task_group_message_priority_ref_data(),
                                                 self.__get_task_stage_ref_data())
        
        timestamp = datetime.datetime.now()
        task_group_params = get_add_one_rir_task_group_update_params(timestamp, False, True)
        task_group_params = dict(task_group_params, context_data = self.context)
        task_group.update(task_group_params)

        task_group_statuses = self.__get_task_group_status_ref_data()
        self.assertIn(task_group_params["summary"]["input_sourcing.churn_validation.status"], task_group_statuses[task_group.status])
        self.assertEqual(task_group.message, task_group_params["summary"]["input_sourcing.churn_validation.message"])

        # Company parsing summary
        self.assertEqual(task_group.summary["input_sourcing"]["parsing"]["start_time"],
                         task_group_params["summary"]["input_sourcing.parsing.start_time"])
        self.assertEqual(task_group.summary["input_sourcing"]["parsing"]["end_time"],
                         task_group_params["summary"]["input_sourcing.parsing.end_time"])
        self.assertEqual(task_group.summary["input_sourcing"]["parsing"]["result"],
                         task_group_params["summary"]["input_sourcing.parsing.result"])

        ###############################################
        # Update again
        timestamp = datetime.datetime.now()
        task_group_params = {"summary": {"input_sourcing.churn_matching.start_time": timestamp,
                                         "input_sourcing.churn_matching.end_time": timestamp,
                                         "input_sourcing.churn_matching.result": {"num_exact_matches": 4,
                                                                                  "num_inexact_matches": 2,
                                                                                  "num_mismatches": 3},
                                         "input_sourcing.churn_validation.start_time": timestamp,
                                         "input_sourcing.churn_validation.result": {"num_in_progress": 1,
                                                                                    "num_validation_tasks": 5,
                                                                                    "num_unvalidated": 4,
                                                                                    "num_validated": 1}}}

        task_group.update(task_group_params)

        # Company churn matching summary
        self.assertEqual(task_group.summary["input_sourcing"]["churn_matching"]["start_time"],
                         task_group_params["summary"]["input_sourcing.churn_matching.start_time"])
        self.assertEqual(task_group.summary["input_sourcing"]["churn_matching"]["end_time"],
                         task_group_params["summary"]["input_sourcing.churn_matching.end_time"])
        self.assertEqual(task_group.summary["input_sourcing"]["churn_matching"]["result"],
                         task_group_params["summary"]["input_sourcing.churn_matching.result"])

        # Company churn validation summary
        self.assertEqual(task_group.summary["input_sourcing"]["churn_validation"]["start_time"],
                         task_group_params["summary"]["input_sourcing.churn_validation.start_time"])
        self.assertEqual(task_group.summary["input_sourcing"]["churn_validation"]["result"],
                         task_group_params["summary"]["input_sourcing.churn_validation.result"])

        ###############################################
        # Update again

        task_group_params = {"summary": {"input_sourcing.churn_validation.result.num_in_progress": 0,
                                         "input_sourcing.churn_validation.result.num_unvalidated": 3,
                                         "input_sourcing.churn_validation.result.num_validated": 2}}

        task_group.update(task_group_params)
        self.assertEqual(task_group.summary["input_sourcing"]["churn_validation"]["result"]["num_validated"],
                         task_group_params["summary"]["input_sourcing.churn_validation.result.num_validated"])
        self.assertEqual(task_group.summary["input_sourcing"]["churn_validation"]["result"]["num_unvalidated"],
                         task_group_params["summary"]["input_sourcing.churn_validation.result.num_unvalidated"])
        self.assertEqual(task_group.summary["input_sourcing"]["churn_validation"]["result"]["num_in_progress"],
                         task_group_params["summary"]["input_sourcing.churn_validation.result.num_in_progress"])

    #-----------------------------# Private Helpers #-----------------------------#

    @staticmethod
    def __get_task_stage_ref_data():

        return {
            "retail_curation": {
                "input_sourcing": {
                    "add_one": {"manual": False, "module": "add_one_retail_input_record"},
                    "parsing": {"manual": False, "module": "retail_input_file_loader"},
                    "churn_matching": {"manual": False, "module": "retail_input_record_churn_matcher"},
                    "churn_validation": {"manual": True, "module": "manual"},
                    "store_count_validation": {"manual": True, "module": "manual"},
                    "quality_control": {"manual": True, "module": "manual"}
                },
                "geocoding": {
                    "collection": {"manual": True, "module": "manual"},
                    "quality_control": {"manual": True, "module": "manual"}
                },
                "company_data_curation": {
                    "financial_data_collection": {"manual": True, "module": "manual"},
                    "store_count_collection": {"manual": True, "module": "manual"},
                    "closed_store_searching": {"manual": False, "module": "retail_input_closed_store_finder"},
                    "closed_store_validation": {"manual": True, "module": "manual"}
                }
            }
        }

    @staticmethod
    def __get_task_group_status_ref_data():

        return {
            "success": ["ready", "skipped", "success"],
            "failure": ["failure"]
        }

    @staticmethod
    def __get_task_group_message_priority_ref_data():

        return {
            "flow": ["retail_curation"],
            "process": ["input_sourcing", "geocoding", "company_data_curation"],
            "stage": ["add_one", "parsing", "churn_matching", "churn_validation",
                      "quality_control", "collection", "quality_control", "financial_data_collection",
                      "closed_store_searching", "closed_store_validation"]
        }

    @staticmethod
    def __get_dict_without_keys(rec, keys_to_remove):
        rec_copy = copy.deepcopy(rec)
        return {k: v for k, v in rec_copy.iteritems() if k not in keys_to_remove}


if __name__ == '__main__':
    unittest.main()