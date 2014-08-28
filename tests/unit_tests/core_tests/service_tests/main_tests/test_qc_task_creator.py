from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import BadRequestError
from core.common.utilities.helpers import generate_id
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.qc_task_creator import QCTaskCreator
import mox


__author__ = 'vgold'


class QCTaskCreatorTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(QCTaskCreatorTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(QCTaskCreator)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_param.mds = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_qc_task_creator.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

        self.mock.context = self.context

    def doCleanups(self):

        super(QCTaskCreatorTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # QCTaskCreator._validate_request_data_and_context()

    def test_validate_request_data_and_context(self):

        qc_task_creator = QCTaskCreator.__new__(QCTaskCreator)

        correct_request_data1 = {"taskID": "taskID"}
        correct_request_data2 = {"rirID": "rirID", "stage": "new_store_validation_qc"}
        correct_context1 = {"user": {"is_generalist": True}, "team_industries": []}
        correct_context2 = {"user": {"is_generalist": False}, "team_industries": [1]}

        # Invalid request_data
        qc_task_creator.request_data = None
        qc_task_creator.context = correct_context1
        self.assertRaises(BadRequestError, qc_task_creator._validate_request_data_and_context)

        # Empty request_data
        qc_task_creator.request_data = {}
        qc_task_creator.context = correct_context1
        self.assertRaises(BadRequestError, qc_task_creator._validate_request_data_and_context)

        # Invalid taskID
        qc_task_creator.request_data = {"taskID": None}
        qc_task_creator.context = correct_context1
        self.assertRaises(BadRequestError, qc_task_creator._validate_request_data_and_context)

        # Invalid context
        qc_task_creator.request_data = correct_request_data1
        qc_task_creator.context = None
        self.assertRaises(BadRequestError, qc_task_creator._validate_request_data_and_context)

        # Empty context
        qc_task_creator.request_data = correct_request_data1
        qc_task_creator.context = {}
        self.assertRaises(BadRequestError, qc_task_creator._validate_request_data_and_context)

        # Invalid user
        qc_task_creator.request_data = correct_request_data1
        qc_task_creator.context = {"user": None}
        self.assertRaises(BadRequestError, qc_task_creator._validate_request_data_and_context)

        # Invalid team industries
        qc_task_creator.request_data = correct_request_data1
        qc_task_creator.context = {"user": {"is_generalist": False}, "team_industries": []}
        self.assertRaises(BadRequestError, qc_task_creator._validate_request_data_and_context)

        # Correct
        qc_task_creator.request_data = correct_request_data1
        qc_task_creator.context = correct_context1
        result = qc_task_creator._validate_request_data_and_context()
        self.assertEqual(result, qc_task_creator)

        # Correct
        qc_task_creator.request_data = correct_request_data2
        qc_task_creator.context = correct_context1
        result = qc_task_creator._validate_request_data_and_context()
        self.assertEqual(result, qc_task_creator)

        # Correct
        qc_task_creator.request_data = correct_request_data1
        qc_task_creator.context = correct_context2
        result = qc_task_creator._validate_request_data_and_context()
        self.assertEqual(result, qc_task_creator)

        # Correct
        qc_task_creator.request_data = correct_request_data2
        qc_task_creator.context = correct_context2
        result = qc_task_creator._validate_request_data_and_context()
        self.assertEqual(result, qc_task_creator)

    ##########################################################################
    # QCTaskCreator._get_task_if_necessary()

    def test_get_task_if_necessary(self):
        
        task = self.__make_task()
        task_id = task["_id"]
        self.mock.main_access.wfs.call_get_task_id(task_id, context_rec = self.context, params = None).AndReturn(task)

        self.mock.request_data = {"taskID": task_id}
        self.mock.base_task_id = task_id

        self.mox.ReplayAll()
        result = QCTaskCreator._get_task_if_necessary(self.mock)
        
        self.assertEqual(result, self.mock)
        self.assertEqual(task, self.mock.base_task)

    def test_get_task_if_necessary__no_task_id(self):

        self.mock.request_data = {}
        self.mock.base_task_id = None
        self.mock.base_task = None

        self.mox.ReplayAll()
        result = QCTaskCreator._get_task_if_necessary(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(None, self.mock.base_task)

    ##########################################################################
    # QCTaskCreator._get_target_rir()

    def test_get_target_rir__no_target_rir_id(self):

        qc_task_creator = QCTaskCreator.__new__(QCTaskCreator)
        qc_task_creator.base_task = {"input": {"asdf": "asdf"}}
        self.assertRaises(BadRequestError, qc_task_creator._get_target_rir)

    def test_get_target_rir(self):
        self.mock.start_time = "start time"

        target_rir_id = generate_id()
        self.mock.base_task = {"input": {"target_rir_id": target_rir_id}}

        rir = {
            "data": {
                "is_churn_matched": True,
                "is_churn_validated": True,
                "is_in_qc": False
            }
        }
        self.mock.main_access.mds.call_get_entity("retail_input_record", target_rir_id, params = None, context = self.context).AndReturn(rir)

        self.mox.ReplayAll()
        result = QCTaskCreator._get_target_rir(self.mock)

        self.assertEqual(result, self.mock)

    def test_get_target_rir__no_base_task(self):
        self.mock.start_time = "start time"
        self.mock.target_rir_id = "target rir id"

        rir_id = generate_id()
        self.mock.base_task = None

        rir = {
            "data": {
                "is_churn_matched": True,
                "is_churn_validated": True,
                "is_in_qc": False
            }
        }
        self.mock.main_access.mds.call_get_entity("retail_input_record", rir_id, params = None, context = self.context).AndReturn(rir)

        self.mox.ReplayAll()

        self.mock.request_data = {"rirID": rir_id}
        result = QCTaskCreator._get_target_rir(self.mock)

        self.assertEqual(result, self.mock)

    def test_get_target_rir__invalid_rir_data(self):

        target_rir_id = generate_id()
        base_task = {"input": {"target_rir_id": target_rir_id}}

        rir = {
            "_id": target_rir_id,
            "data": {
                "is_churn_matched": False,
                "is_churn_validated": False,
                "is_in_qc": True
            }
        }
        self.mock.main_access.mds.call_get_entity("retail_input_record", target_rir_id, params = None, context = self.context).AndReturn(rir)

        self.mox.ReplayAll()
        self.mock.rir = rir
        self.mock.base_task = base_task
        self.assertRaises(BadRequestError, QCTaskCreator._get_target_rir, *(self.mock,))

    ##########################################################################
    # QCTaskCreator._validate_user_generalist_and_team_industries()

    def test_validate_user_generalist_and_team_industries__generalist_no_industries(self):

        context = {
            "user": {
                "is_generalist": True
            },
            "team_industries": []
        }

        company_id = generate_id()

        entity_fields = ["_id"]
        query = {"links.company.industry_classification.entity_id_to": company_id,
                 "links.company.industry_classification.entity_role_to": "primary_industry_classification"}

        params = "params"
        self.mock.main_param.mds.create_params(origin = "_get_target_rir", resource = "find_entities_raw",
                                               query = query, as_list = True, entity_fields = entity_fields).AndReturn({"params": params})

        industries = [[]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params = params, context = context).AndReturn(industries)

        self.mox.ReplayAll()

        self.mock.context = context

        self.mock.rir = {"data": {"company_id": str(company_id)}}
        result = QCTaskCreator._validate_user_generalist_and_team_industries(self.mock)

        self.assertEqual(result, self.mock)

    def test_validate_user_generalist_and_team_industries__non_generalist_correct_industry(self):

        context = {
            "user": {
                "is_generalist": False
            },
            "team_industries": [1]
        }

        company_id = generate_id()

        entity_fields = ["_id"]
        query = {"links.company.industry_classification.entity_id_to": company_id,
                 "links.company.industry_classification.entity_role_to": "primary_industry_classification"}

        params = "params"
        self.mock.main_param.mds.create_params(origin = "_get_target_rir", resource = "find_entities_raw",
                                               query = query, as_list = True, entity_fields = entity_fields).AndReturn({"params": params})

        industries = [[1]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params = params, context = context).AndReturn(industries)

        self.mox.ReplayAll()

        self.mock.context = context

        self.mock.rir = {"data": {"company_id": str(company_id)}}
        result = QCTaskCreator._validate_user_generalist_and_team_industries(self.mock)

        self.assertEqual(result, self.mock)

    def test_validate_user_generalist_and_team_industries__non_generalist_no_industries(self):

        context = {
            "user": {
                "is_generalist": False
            },
            "team_industries": []
        }

        company_id = generate_id()

        entity_fields = ["_id"]
        query = {"links.company.industry_classification.entity_id_to": company_id,
                 "links.company.industry_classification.entity_role_to": "primary_industry_classification"}

        params = "params"
        self.mock.main_param.mds.create_params(origin = "_get_target_rir", resource = "find_entities_raw",
                                               query = query, as_list = True, entity_fields = entity_fields).AndReturn({"params": params})

        industries = [[]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params = params, context = context).AndReturn(industries)

        self.mox.ReplayAll()

        self.mock.context = context

        self.mock.rir = {"data": {"company_id": str(company_id)}}
        self.assertRaises(BadRequestError, QCTaskCreator._validate_user_generalist_and_team_industries, *(self.mock,))

    def test_validate_user_generalist_and_team_industries__generalist_and_industries(self):

        context = {
            "user": {
                "is_generalist": True
            },
            "team_industries": [1]
        }

        company_id = generate_id()

        entity_fields = ["_id"]
        query = {"links.company.industry_classification.entity_id_to": company_id,
                 "links.company.industry_classification.entity_role_to": "primary_industry_classification"}

        params = "params"
        self.mock.main_param.mds.create_params(origin = "_get_target_rir", resource = "find_entities_raw",
                                               query = query, as_list = True, entity_fields = entity_fields).AndReturn({"params": params})

        industries = [[1]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params = params, context = context).AndReturn(industries)

        self.mox.ReplayAll()

        self.mock.context = context

        self.mock.rir = {"data": {"company_id": str(company_id)}}
        self.assertRaises(BadRequestError, QCTaskCreator._validate_user_generalist_and_team_industries, *(self.mock,))

    def test_validate_user_generalist_and_team_industries__non_generalist_invalid_industry(self):

        context = {
            "user": {
                "is_generalist": False
            },
            "team_industries": [1]
        }

        company_id = generate_id()

        entity_fields = ["_id"]
        query = {"links.company.industry_classification.entity_id_to": company_id,
                 "links.company.industry_classification.entity_role_to": "primary_industry_classification"}

        params = "params"
        self.mock.main_param.mds.create_params(origin = "_get_target_rir", resource = "find_entities_raw",
                                               query = query, as_list = True, entity_fields = entity_fields).AndReturn({"params": params})

        industries = [[2]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params = params, context = context).AndReturn(industries)

        self.mox.ReplayAll()

        self.mock.context = context

        self.mock.rir = {"data": {"company_id": str(company_id)}}
        self.assertRaises(BadRequestError, QCTaskCreator._validate_user_generalist_and_team_industries, *(self.mock,))

    ##########################################################################
    # QCTaskCreator._check_for_in_progress_tasks()

    def test_check_for_in_progress_tasks(self):

        tasks = []
        self.mock.main_access.wfs.call_task_find(self.context, mox.IgnoreArg()).AndReturn(tasks)

        self.mock.rir = {"_id": generate_id()}

        self.mox.ReplayAll()
        result = QCTaskCreator._check_for_in_progress_tasks(self.mock)

        self.assertEqual(result, self.mock)

    def test_check_for_in_progress_tasks__tasks_in_progress(self):

        tasks = [1]
        self.mock.main_access.wfs.call_task_find(self.context, mox.IgnoreArg()).AndReturn(tasks)

        self.mock.rir = {"_id": generate_id()}

        self.mox.ReplayAll()
        self.assertRaises(BadRequestError, QCTaskCreator._check_for_in_progress_tasks, *(self.mock,))

    ##########################################################################
    # QCTaskCreator._find_and_modify_rir_qc_flag()

    def test_find_and_modify_rir_qc_flag(self):
        self.mock.start_time = "start time"
        self.mock.target_rir_id = "target rir id"

        rirs = [1]
        self.mock.main_access.mds.call_find_and_modify_entity("retail_input_record", mox.IgnoreArg(), self.context).AndReturn(rirs)

        self.mock.rir = {"_id": generate_id()}

        self.mox.ReplayAll()
        result = QCTaskCreator._find_and_modify_rir_qc_flag(self.mock)

        self.assertEqual(result, self.mock)

    def test_find_and_modify_rir_qc_flag__no_result(self):

        rirs = []
        self.mock.main_access.mds.call_find_and_modify_entity("retail_input_record", mox.IgnoreArg(), self.context).AndReturn(rirs)

        self.mock.rir = {"_id": generate_id()}

        self.mox.ReplayAll()
        self.assertRaises(BadRequestError, QCTaskCreator._find_and_modify_rir_qc_flag, *(self.mock,))

    ##########################################################################
    # QCTaskCreator._create_qc_task()

    def test_create_qc_task__base_task__new_store_validation(self):
        self.mock.start_time = "start time"
        self.mock.target_rir_id = "target rir id"

        flow = "retail_curation"
        process = "input_sourcing"
        stage = "churn_validation"

        task_data = "task_data"
        self.mock.main_access.wfs.call_find_tasks(mox.IgnoreArg(), self.context).AndReturn(task_data)

        qc_task = "qc_task"
        self.mock.main_access.wfs.call_task_new(flow, process, "new_store_validation_qc", mox.IgnoreArg(), self.context).AndReturn(qc_task)

        self.mock.base_task = {
            "stage": stage,
            "process": process
        }

        self.mock.rir = {"_id": generate_id(), "data": { "company_id": "woot" }}

        self.mox.ReplayAll()
        result = QCTaskCreator._create_qc_task(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(qc_task, self.mock.qc_task)
        self.assertEqual("new", self.mock.validation_type)

    def test_create_qc_task__base_task__closed_store_validation(self):
        self.mock.start_time = "start time"
        self.mock.target_rir_id = "target rir id"
        flow = "retail_curation"
        process = "company_data_curation"
        stage = "closed_store_validation"

        task_data = {
            'rows': [{'input': {'most_recent_rir_as_of_date': 'asdf'}}]
        }
        self.mock.main_access.wfs.call_find_tasks(mox.IgnoreArg(), self.context).AndReturn(task_data)

        qc_task = "qc_task"
        self.mock.main_access.wfs.call_task_new(flow, process, "closed_store_validation_qc", mox.IgnoreArg(), self.context).AndReturn(qc_task)

        self.mock.base_task = {
            "stage": stage,
            "process": process
        }

        self.mock.rir = {"_id": generate_id(), "data": { "company_id": "woot" }}

        self.mox.ReplayAll()
        result = QCTaskCreator._create_qc_task(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(qc_task, self.mock.qc_task)
        self.assertEqual("closed", self.mock.validation_type)

    def test_create_qc_task__no_base_task__new_store_validation(self):
        self.mock.start_time = "start time"
        self.mock.target_rir_id = "target rir id"

        flow = "retail_curation"
        process = "input_sourcing"
        stage = "new_store_validation_qc"

        task_data = "task_data"
        self.mock.main_access.wfs.call_find_tasks(mox.IgnoreArg(), self.context).AndReturn(task_data)

        qc_task = "qc_task"
        self.mock.main_access.wfs.call_task_new(flow, process, "new_store_validation_qc", mox.IgnoreArg(), self.context).AndReturn(qc_task)

        self.mock.base_task = None
        self.mock.request_data = {
            "stage": stage
        }

        self.mock.rir = {"_id": generate_id(), "data": { "company_id": "woot" }}

        self.mox.ReplayAll()
        result = QCTaskCreator._create_qc_task(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(qc_task, self.mock.qc_task)
        self.assertEqual("new", self.mock.validation_type)

    def test_create_qc_task__no_base_task__closed_store_validation(self):
        self.mock.start_time = "start time"
        self.mock.target_rir_id = "target rir id"

        flow = "retail_curation"
        process = "company_data_curation"
        stage = "closed_store_validation_qc"

        task_data = {
            'rows': [{'input': {'most_recent_rir_as_of_date': 'asdf'}}]
        }
        self.mock.main_access.wfs.call_find_tasks(mox.IgnoreArg(), self.context).AndReturn(task_data)

        qc_task = "qc_task"
        self.mock.main_access.wfs.call_task_new(flow, process, "closed_store_validation_qc", mox.IgnoreArg(), self.context).AndReturn(qc_task)

        self.mock.base_task = None
        self.mock.request_data = {
            "stage": stage
        }

        self.mock.rir = {"_id": generate_id(), "data": { "company_id": "woot" }}

        self.mox.ReplayAll()
        result = QCTaskCreator._create_qc_task(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(qc_task, self.mock.qc_task)
        self.assertEqual("closed", self.mock.validation_type)

    #----------------------------# Private Helper #----------------------------#

    @staticmethod
    def __make_task():

        return {
            "_id": generate_id(),
            "input": {
                "target_rir_id": generate_id()
            },
            "output": {},
            "context_data": {"user_id": 1}
        }

