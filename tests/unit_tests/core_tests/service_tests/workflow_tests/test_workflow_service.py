from bson.objectid import ObjectId
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import *
from core.common.utilities.helpers import generate_id
from core.service.svc_workflow.implementation.task.implementation.task_sorting_helper import get_queue_sort_key
from core.service.svc_workflow.implementation.workflow_service import WorkflowService
import unittest
import datetime
import mox


__author__ = 'vgold'


class WorkflowServiceTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(WorkflowServiceTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock_svc = self.mox.CreateMock(WorkflowService)
        self.mock_svc.mongo_access = self.mox.CreateMockAnything()
        self.mock_svc.AtomicWorkflowValidationTaskRetriever = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock_svc.cfg = Dependency("MoxConfig").value
        self.mock_svc.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {
            "user_id": 1,
            "source": "test_workflow_service.py",
            "user": { "user_id": 1, "is_generalist": False},
            "team_industries": ["asdf"]
        }

    def doCleanups(self):

        super(WorkflowServiceTests, self).doCleanups()
        dependencies.clear()

    ############################################################
    # WorkflowService.get_entity_workflow_statuses()

    def test_get_entity_workflow_statuses__no_reload_refdata__invalid_refdata(self):

        workflow_service = WorkflowService.__new__(WorkflowService)
        workflow_service.logger = self.mock_svc.logger
        workflow_service.refdata = False
        self.assertRaises(ServiceError, workflow_service.get_entity_workflow_statuses, *(False,))

    def test_get_entity_workflow_statuses__no_reload_refdata__valid_refdata(self):

        self.mock_svc.refdata = self.mox.CreateMockAnything()
        self.mock_svc.refdata.get_entity_workflow_status_map().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.get_entity_workflow_statuses(self.mock_svc, False)
        self.assertEqual(result, "helo")

    def test_get_entity_workflow_statuses__reload_refdata__invalid_refdata(self):

        self.mock_svc._WorkflowService__load_reference_data()
        self.mock_svc.refdata = False

        self.mox.ReplayAll()

        self.assertRaises(ServiceError, WorkflowService.get_entity_workflow_statuses, *(self.mock_svc, True))

    def test_get_entity_workflow_statuses__reload_refdata__valid_refdata(self):

        self.mock_svc._WorkflowService__load_reference_data()

        self.mock_svc.refdata = self.mox.CreateMockAnything()
        self.mock_svc.refdata.get_entity_workflow_status_map().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.get_entity_workflow_statuses(self.mock_svc, True)
        self.assertEqual(result, "helo")

    ############################################################
    # WorkflowService.get_task_stages()

    def test_get_task_stages__no_reload_refdata__invalid_refdata(self):

        workflow_service = WorkflowService.__new__(WorkflowService)
        workflow_service.logger = self.mock_svc.logger
        workflow_service.refdata = False
        self.assertRaises(ServiceError, workflow_service.get_task_stages, *(False,))

    def test_get_task_stages__no_reload_refdata__valid_refdata(self):

        self.mock_svc.refdata = self.mox.CreateMockAnything()
        self.mock_svc.refdata.get_task_stage_map().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.get_task_stages(self.mock_svc, False)
        self.assertEqual(result, "helo")

    def test_get_task_stages__reload_refdata__invalid_refdata(self):

        self.mock_svc._WorkflowService__load_reference_data()
        self.mock_svc.refdata = False

        self.mox.ReplayAll()

        self.assertRaises(ServiceError, WorkflowService.get_task_stages, *(self.mock_svc, True))

    def test_get_task_stages__reload_refdata__valid_refdata(self):

        self.mock_svc._WorkflowService__load_reference_data()

        self.mock_svc.refdata = self.mox.CreateMockAnything()
        self.mock_svc.refdata.get_task_stage_map().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.get_task_stages(self.mock_svc, True)
        self.assertEqual(result, "helo")

    ############################################################
    # WorkflowService.get_task()

    def test_get_task(self):

        # Create task record to return from mongo
        task_rec = self.__create_churn_validation_task_rec()
        self.mock_svc.mongo_access.get_task_by_id(task_rec["_id"], archived=False).AndReturn(task_rec)

        # Mock workflow stage dict
        task_stage_data = self.__get_task_stages_ref_data()
        self.mock_svc.get_task_stages().AndReturn(task_stage_data)

        # Mock WorkflowTask class
        MockWorkflowTask = self.mox.CreateMockAnything()
        self.mock_svc._WorkflowService__load_task_class("manual").AndReturn(MockWorkflowTask)
        MockWorkflowTask.dict_init(self.mock_svc.cfg, self.mock_svc.logger, None, task_rec).AndReturn("helo_task")

        self.mox.ReplayAll()

        # FTW!! Call get_task from the class and use the mock object as the instance!
        task_obj = WorkflowService.get_task(self.mock_svc, task_rec["_id"])
        self.assertEqual(task_obj, "helo_task")

    def test_get_task__not_found(self):

        task_id = generate_id()
        self.mock_svc.mongo_access.get_task_by_id(task_id, archived=False).AndReturn(None)

        self.mox.ReplayAll()

        self.assertRaises(NotFoundError, WorkflowService.get_task, *(self.mock_svc, task_id))

    ############################################################
    # WorkflowService.get_next_item()

    def test_get_next_item(self):

        task_rec = self.__create_churn_validation_task_rec()
        data = {"flow": task_rec["flow"], "process": task_rec["process"], "stage": task_rec["stage"]}

        self.mock_svc._WorkflowService__validate_task_stages(data["flow"], data["process"], data["stage"])

        mock_retriever = self.mox.CreateMockAnything()
        self.mock_svc.AtomicWorkflowValidationTaskRetriever(self.mock_svc.mongo_access, data["flow"], data["process"], data["stage"], self.context).AndReturn(mock_retriever)
        mock_retriever.retrieve_next_task().AndReturn(task_rec)

        # Mock workflow stage data
        task_stage_data = self.__get_task_stages_ref_data()
        self.mock_svc.get_task_stages().AndReturn(task_stage_data)

        # Mock WorkflowTask class
        MockWorkflowTask = self.mox.CreateMockAnything()
        self.mock_svc._WorkflowService__load_task_class("manual").AndReturn(MockWorkflowTask)

        mock_task = self.mox.CreateMockAnything()
        MockWorkflowTask.dict_init(self.mock_svc.cfg, self.mock_svc.logger, None, task_rec).AndReturn(mock_task)

        mock_task.get_status().AndReturn("status")

        self.mox.ReplayAll()

        status = WorkflowService.get_next_item(self.mock_svc, data, self.context)
        self.assertEqual(status, "status")

    ############################################################
    # WorkflowService.open_item()

    def test_open_item(self):

        task_id = generate_id()

        mock_task = self.mox.CreateMockAnything()
        mock_task.task_status = {"status": "in_progress"}

        self.mock_svc.get_task(task_id).AndReturn(mock_task)

        mock_task.update({"task_status.status": "open", "context_data": self.context})
        self.mock_svc.update_task(mock_task)
        mock_task.get_status().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.open_item(self.mock_svc, task_id, self.context)
        self.assertEqual(result, "helo")

    def test_open_item__bad_request(self):

        task_id = generate_id()

        mock_task = self.mox.CreateMockAnything()
        mock_task.task_status = {"status": "asdf"}

        self.mock_svc.get_task(task_id).AndReturn(mock_task)

        self.mox.ReplayAll()

        self.assertRaises(BadRequestError, WorkflowService.open_item, *(self.mock_svc, task_id, self.context))

    ############################################################
    # WorkflowService.commit_item()

    def test_commit_item(self):

        task_id = generate_id()

        mock_task = self.mox.CreateMockAnything()
        mock_task.task_status = {"status": "in_progress"}

        self.mock_svc.get_task(task_id).AndReturn(mock_task)

        commit_data = {"commit_data": "commit_data"}
        mock_task.update({"task_status.status": "closed",
                          "output": commit_data,
                          "task_status.result": commit_data,
                          "context_data": self.context})
        self.mock_svc.update_task(mock_task)
        mock_task.get_status().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.commit_item(self.mock_svc, task_id, commit_data, self.context)
        self.assertEqual(result, "helo")

    def test_commit_item__bad_request(self):

        task_id = generate_id()

        mock_task = self.mox.CreateMockAnything()
        mock_task.task_status = {"status": "asdf"}

        self.mock_svc.get_task(task_id).AndReturn(mock_task)

        self.mox.ReplayAll()

        self.assertRaises(BadRequestError, WorkflowService.commit_item, *(self.mock_svc, task_id, None, self.context))

    ############################################################
    # WorkflowService.skip_item()

    def test_skip_item(self):

        task_id = generate_id()

        mock_task = self.mox.CreateMockAnything()
        mock_task.task_status = {"status": "whatevs"}

        self.mock_svc.get_task(task_id).AndReturn(mock_task)

        mock_task.update({"task_status.status": "skipped", "context_data": self.context})
        self.mock_svc.update_task(mock_task)
        mock_task.get_status().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.skip_item(self.mock_svc, task_id, self.context)
        self.assertEqual(result, "helo")

    ############################################################
    # WorkflowService.add_task()

    def test_add_task(self):
        # create fake task
        task_rec = self.__create_churn_validation_task_rec()

        # start recording
        self.mock_svc._check_task_group_availability(task_rec["flow"], task_rec["process"], task_rec["stage"], task_rec["task_group_id"]).AndReturn(True)
        self.mock_svc.add_tasks(task_rec["flow"], task_rec["process"], task_rec["stage"], [task_rec], self.context, None, None).AndReturn(["asdf"])

        # replay all
        self.mox.ReplayAll()

        # call add and make sure the results match
        result = WorkflowService.add_task(self.mock_svc, task_rec["flow"], task_rec["process"], task_rec["stage"], task_rec, self.context, None)
        self.assertEqual(result, "asdf")

    def test_add_task__not_availble(self):
        # create fake task
        task_rec = self.__create_churn_validation_task_rec()

        # start recording.
        # make task not available
        self.mock_svc._check_task_group_availability(task_rec["flow"], task_rec["process"], task_rec["stage"], task_rec["task_group_id"]).AndReturn(False)

        # replay all
        self.mox.ReplayAll()

        # call add and make sure the results match
        with self.assertRaises(ConflictError) as error:
            WorkflowService.add_task(self.mock_svc, task_rec["flow"], task_rec["process"], task_rec["stage"], task_rec, self.context, None)
        self.assertEqual(error.exception.message, "Task is running.  Please wait.")

    ############################################################
    # WorkflowService.add_tasks()

    def test_add_tasks__bad_request(self):

        # Create task records
        task_recs = [self.__create_churn_validation_task_rec(),
                     self.__create_churn_validation_task_rec(),
                     self.__create_churn_validation_task_rec()]

        flow = task_recs[0]["flow"]
        process = task_recs[0]["process"]
        stage = task_recs[0]["stage"]

        self.assertRaises(BadRequestError, WorkflowService.add_tasks, *(self.mock_svc, flow, process, stage, [], self.context, None))
        self.assertRaises(BadRequestError, WorkflowService.add_tasks, *(self.mock_svc, flow, process, stage, [{}], self.context, None))
        self.assertRaises(BadRequestError, WorkflowService.add_tasks, *(self.mock_svc, flow, process, stage, [{}, {}, {}], self.context, None))

    def test_add_tasks__manual_tasks(self):

        # Create task records
        task_recs = [self.__create_churn_validation_task_rec(),
                     self.__create_churn_validation_task_rec(),
                     self.__create_churn_validation_task_rec()]

        flow = task_recs[0]["flow"]
        process = task_recs[0]["process"]
        stage = task_recs[0]["stage"]

        # Private method names get changed when calling from outside the module
        self.mock_svc._WorkflowService__validate_task_stages(flow, process, stage)

        # Mock workflow stage data
        task_stage_data = self.__get_task_stages_ref_data()
        self.mock_svc.get_task_stages(reload_refdata = True).AndReturn(task_stage_data)

        # Mock WorkflowTask class
        MockWorkflowTask = self.mox.CreateMockAnything()
        self.mock_svc._WorkflowService__load_task_class("manual").AndReturn(MockWorkflowTask)

        # Emulate looping in WorkflowService.add_tasks
        task_mocks = []
        for task in task_recs:
            mock_task = self.mox.CreateMockAnything()
            mock_task.meta = { "insert_wfs_task": True }
            MockWorkflowTask.dict_init(self.mock_svc.cfg, self.mock_svc.logger, None, task).AndReturn(mock_task)
            mock_task.to_dict().AndReturn(task)
            task_mocks.append(mock_task)

        # Mock mongo_access call
        task_ids = [task["_id"] for task in task_recs]
        self.mock_svc.mongo_access.insert("task", task_recs).AndReturn(task_ids)

        # Mock task_obj loop
        for i, task_mock in enumerate(task_mocks):
            task_mock.get_status().AndReturn(i)

        self.mox.ReplayAll()

        # FTW!! Call get_task from the class and use the mock object as the instance!
        statuses = WorkflowService.add_tasks(self.mock_svc, flow, process, stage, task_recs, self.context, None)
        self.assertEqual(statuses, range(len(task_recs)))

    def test_add_tasks__automatic_tasks(self):

        # Create task records
        task_recs = [self.__create_churn_matching_task_rec(),
                     self.__create_churn_matching_task_rec(),
                     self.__create_churn_matching_task_rec()]

        flow = task_recs[0]["flow"]
        process = task_recs[0]["process"]
        stage = task_recs[0]["stage"]

        # Private method names get changed when calling from outside the module
        self.mock_svc._WorkflowService__validate_task_stages(flow, process, stage)

        # Mock workflow stage data
        task_stage_data = self.__get_task_stages_ref_data()
        self.mock_svc.get_task_stages(reload_refdata = True).AndReturn(task_stage_data)

        # Mock WorkflowTask class
        MockWorkflowTask = self.mox.CreateMockAnything()
        self.mock_svc._WorkflowService__load_task_class("retail_input_record_churn_matcher").AndReturn(MockWorkflowTask)

        # Emulate looping in WorkflowService.add_tasks
        task_mocks = []
        for task in task_recs:
            mock_task = self.mox.CreateMockAnything()
            mock_task.meta = { "insert_wfs_task": True }
            MockWorkflowTask.dict_init(self.mock_svc.cfg, self.mock_svc.logger, None, task).AndReturn(mock_task)
            mock_task.to_dict().AndReturn(task)
            task_mocks.append(mock_task)

        # Mock mongo_access call
        task_ids = [task["_id"] for task in task_recs]
        self.mock_svc.mongo_access.insert("task", task_recs).AndReturn(task_ids)

        # Mock task_obj loop
        for i, task_mock in enumerate(task_mocks):
            task_mock.start()
            self.mock_svc.update_task(task_mock)
            task_mock.get_status().AndReturn(i)

        self.mox.ReplayAll()

        # FTW!! Call get_task from the class and use the mock object as the instance!
        statuses = WorkflowService.add_tasks(self.mock_svc, flow, process, stage, task_recs, self.context, None)
        self.assertEqual(statuses, range(len(task_recs)))

    ############################################################
    # WorkflowService.del_task()

    def test_del_task__not_manual(self):

        mock_task = self.mox.CreateMockAnything()
        mock_task.task_group_id = "asdf"
        mock_task.flow = "flow"
        mock_task.process = "process"
        mock_task.stage = "stage"
        mock_task.task_id = generate_id()

        mock_task_group = self.mox.CreateMockAnything()
        self.mock_svc.get_task_group("asdf").AndReturn(mock_task_group)

        manual = False
        self.mock_svc.get_task_stages(reload_refdata = True).AndReturn({"flow": {"process": {"stage": {"manual": manual}}}})

        mock_task_group.update({"summary": {"process.stage": {"result": {}}}})
        self.mock_svc.update_task_group(mock_task_group)

        self.mock_svc.mongo_access.remove("task", mock_task.task_id)

        mock_task.to_dict().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.del_task(self.mock_svc, mock_task)
        self.assertEqual(result, {"status": "deleted", "task": "helo"})

    def test_del_task__churn_validation(self):

        mock_task = self.mox.CreateMockAnything()
        mock_task.task_group_id = "asdf"
        mock_task.flow = "retail_curation"
        mock_task.process = "input_sourcing"
        mock_task.stage = "churn_validation"
        mock_task.task_id = generate_id()

        mock_task_group = self.mox.CreateMockAnything()
        self.mock_svc.get_task_group("asdf").AndReturn(mock_task_group)

        manual = True
        self.mock_svc.get_task_stages(reload_refdata = True).AndReturn({"retail_curation": {"input_sourcing": {"churn_validation": {"manual": manual}}}})

        mock_task_group.remove_churn_validation_task(mock_task)
        self.mock_svc.update_task_group(mock_task_group)

        self.mock_svc.mongo_access.remove("task", mock_task.task_id)

        mock_task.to_dict().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.del_task(self.mock_svc, mock_task)
        self.assertEqual(result, {"status": "deleted", "task": "helo"})

    def test_del_task__manual(self):

        mock_task = self.mox.CreateMockAnything()
        mock_task.task_group_id = "asdf"
        mock_task.flow = "flow"
        mock_task.process = "process"
        mock_task.stage = "stage"
        mock_task.task_id = generate_id()

        mock_task_group = self.mox.CreateMockAnything()
        self.mock_svc.get_task_group("asdf").AndReturn(mock_task_group)

        manual = True
        self.mock_svc.get_task_stages(reload_refdata = True).AndReturn({"flow": {"process": {"stage": {"manual": manual}}}})

        self.mock_svc.mongo_access.remove("task", mock_task.task_id)

        mock_task.to_dict().AndReturn("helo")

        self.mox.ReplayAll()

        result = WorkflowService.del_task(self.mock_svc, mock_task)
        self.assertEqual(result, {"status": "deleted", "task": "helo"})

    ############################################################
    # WorkflowService.update_task()

    def test_update_task(self):

        mock_task = self.mox.CreateMockAnything()
        mock_task.get_new_updates().AndReturn(True)

        mock_task.meta = {"updated_at": "now"}
        self.mock_svc._WorkflowService__task_updates_to_mongo_query(True, mock_task.meta["updated_at"]).AndReturn("update_doc")

        mock_task.task_id = generate_id()

        mongo_return_dict = {"err": None, "n": 1, "updatedExisting": True}
        self.mock_svc.mongo_access.update("task", {"_id": mock_task.task_id}, "update_doc").AndReturn(mongo_return_dict)

        self.mox.ReplayAll()

        WorkflowService.update_task(self.mock_svc, mock_task)


    ############################################################
    # WorkflowService._check_task_group_availability()

    def test_check_task_group_availability__default_true(self):
        # start recording.
        # nothing to record this task is ignored

        # replay all
        self.mox.ReplayAll()

        # call add and make sure the results match
        is_available = WorkflowService._check_task_group_availability(self.mock_svc, "flow", "process", "stage", "task_group_id")
        self.assertTrue(is_available)

    def test_check_task_group_availability__churn_matching__bad_structure(self):
        # create fake parameters
        query = { "_id": ObjectId("chicken_woot") }
        update = { "$set": { "summary.input_sourcing.churn_matching.is_available": False }}

        # set up mocks
        self.mock_svc.mongo_access = self.mox.CreateMockAnything()

        # start recording.
        # nothing to record this task is ignored
        self.mock_svc.mongo_access.find_and_modify("task", query = query, update = update).AndReturn("woot")

        # replay all
        self.mox.ReplayAll()

        # call add and make sure the results match
        is_available = WorkflowService._check_task_group_availability(self.mock_svc, "retail_curation", "input_sourcing", "churn_matching", "chicken_woot")
        self.assertTrue(is_available)

    def test_check_task_group_availability__churn_matching__available(self):
        # create fake parameters
        query = { "_id": ObjectId("chicken_woot") }
        update = { "$set": { "summary.input_sourcing.churn_matching.is_available": False }}
        task_group = {
            "summary": {
                "input_sourcing" : {
                    "churn_matching": {

                    }
                }
            }
        }

        # set up mocks
        self.mock_svc.mongo_access = self.mox.CreateMockAnything()

        # start recording.
        # nothing to record this task is ignored
        self.mock_svc.mongo_access.find_and_modify("task", query = query, update = update).AndReturn(task_group)

        # replay all
        self.mox.ReplayAll()

        # call add and make sure the results match
        is_available = WorkflowService._check_task_group_availability(self.mock_svc, "retail_curation", "input_sourcing", "churn_matching", "chicken_woot")
        self.assertTrue(is_available)

    def test_check_task_group_availability__churn_matching__not_available(self):
        # create fake parameters
        query = { "_id": ObjectId("chicken_woot") }
        update = { "$set": { "summary.input_sourcing.churn_matching.is_available": False }}
        task_group = {
            "summary": {
                "input_sourcing" : {
                    "churn_matching": {
                        "is_available": False
                    }
                }
            }
        }

        # set up mocks
        self.mock_svc.mongo_access = self.mox.CreateMockAnything()

        # start recording.
        # nothing to record this task is ignored
        self.mock_svc.mongo_access.find_and_modify("task", query = query, update = update).AndReturn(task_group)

        # replay all
        self.mox.ReplayAll()

        # call add and make sure the results match
        is_available = WorkflowService._check_task_group_availability(self.mock_svc, "retail_curation", "input_sourcing", "churn_matching", "chicken_woot")
        self.assertFalse(is_available)





    #----------------------------# Private Methods #----------------------------#

    def __create_task_rec(self, flow, process, stage, input_rec, extra = None):

        task_rec = {"_id": generate_id(),
                    "type": "task",
                    "flow": flow,
                    "process": process,
                    "stage": stage,
                    "task_group_id": generate_id(),
                    "input": input_rec,
                    "meta": {"async": False},
                    "task_status": {"status": "open", "result": None},
                    "context_data": self.context}

        if isinstance(extra, dict):
            task_rec = dict(task_rec, **extra)

        return task_rec

    def __create_churn_validation_task_rec(self):

        as_of_date = str(datetime.datetime.utcnow())
        input_rec = {"industry_id": "asdf",
                      "target_rir_id": "asdf",
                      "match_type": "mismatch",
                      "company_id": "asdf",
                      "as_of_date": as_of_date,
                      "source_id": "asdf"}
        extra = {"sort_key": get_queue_sort_key(as_of_date)}
        return self.__create_task_rec("retail_curation", "input_sourcing", "churn_validation", input_rec, extra)

    def __create_churn_matching_task_rec(self):

        as_of_date = str(datetime.datetime.utcnow())
        input_rec = {"source_id": "asdf",
                      "as_of_date": as_of_date,
                      "company_id": "asdf"}
        return self.__create_task_rec("retail_curation", "input_sourcing", "churn_matching", input_rec)

    def __get_task_stages_ref_data(self):

        return {
            "retail_curation": {
                "input_sourcing": {
                    "add_one": {"manual": False, "module": "add_one_retail_input_record"},
                    "parsing": {"manual": False, "module": "retail_input_file_loader"},
                    "churn_matching": {"manual": False, "module": "retail_input_record_churn_matcher"},
                    "churn_validation": {"manual": True, "module": "manual"},
                    "new_store_validation_qc": {"manual": True, "module": "manual"},
                    "churn_completion_fixer": {"manual": False, "module": "retail_input_churn_completion_fixer"}
                },
                "geocoding": {
                    "collection": {"manual": True, "module": "manual"},
                    "quality_control": {"manual": True, "module": "manual"}
                },
                "company_data_curation": {
                    "financial_data_collection": {"manual": True, "module": "manual"},
                    "closed_store_searching": {"manual": False, "module": "retail_input_closed_store_finder"},
                    "closed_store_validation": {"manual": True, "module": "manual"},
                    "closed_store_validation_qc": {"manual": True, "module": "manual"},
                    "input_file_deletion": {"manual": False, "module": "retail_input_file_deletion"},
                    "company_deletion": {"manual": False, "module": "company_deletion"}
                },
                "cleanup": {
                    "orphan_task_fixer": {"manual": False, "module": "retail_curation_orphan_task_fixer"}
                }
            }
        }

    def __get_entity_workflow_statuses(self):

        return {
            "new":{
                "display_name": "New",
                "description": "The entity has been created with initial data.",
                "viewable_by_role": {
                    "client": False
                },
                "editable_by_role": {
                    "investment": True,
                    "collection": False,
                    "qc": False
                }
            },
            "in_collection": {
                "display_name": "In Collection",
                "description": "Data for the entity is currently being collected by an analyst.",
                "viewable_by_role": {
                    "client": False
                },
                "editable_by_role": {
                    "investment": True,
                    "collection": True,
                    "qc": False
                }
            },
            "in_qc":{
                "display_name": "In QC",
                "description": "The entity is being reviewed for quality control.",
                "viewable_by_role": {
                    "client": False
                },
                "editable_by_role": {
                    "investment": True,
                    "collection": False,
                    "qc": True
                }
            },
            "published": {
                "display_name": "Published",
                "description": "The entity can be viewed by clients within external products.",
                "viewable_by_role": {
                    "client": True
                },
                "editable_by_role": {
                    "investment": True,
                    "collection": False,
                    "qc": True
                }
            }
        }


if __name__ == '__main__':
    unittest.main()