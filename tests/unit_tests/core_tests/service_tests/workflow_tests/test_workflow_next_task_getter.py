from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.workflow_next_task_getter import WorkflowNextTaskGetter
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.service_access.utilities.errors import ServiceCallError
from common.utilities.inversion_of_control import dependencies, Dependency
from tests.unit_tests.core_tests.data_stub_helpers import *
from core.common.utilities.errors import BadRequestError, DataError, NotFoundError, ServiceError
from core.common.utilities.helpers import generate_id
import mox
import datetime
import unittest


__author__ = 'vgold'


class WorkflowNextTaskGetterTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(WorkflowNextTaskGetterTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get several dependencies that we'll need in the class
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(WorkflowNextTaskGetter)
        self.mock.em_access = self.mox.CreateMockAnything()
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_param.mds = self.mox.CreateMockAnything()
        self.mock.rir_helper = self.mox.CreateMockAnything()
        self.mock.store_helper = self.mox.CreateMockAnything()
        self.mock.retail_input_validation_helper = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_workflow_next_task_getter.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

        self.mock.context = self.context

    def doCleanups(self):

        super(WorkflowNextTaskGetterTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # WorkflowNextTaskGetter._validate_query_and_context()

    def test_validate_query_and_context(self):

        next_task_getter = WorkflowNextTaskGetter.__new__(WorkflowNextTaskGetter)
        correct_query1 = {"process": "input_sourcing", "stage": "churn_validation"}
        correct_query2 = {"process": "input_sourcing", "stage": "new_store_validation_qc"}
        correct_query3 = {"process": "company_data_curation", "stage": "closed_store_validation"}
        correct_query4 = {"process": "company_data_curation", "stage": "closed_store_validation_qc"}
        correct_context1 = {"user": {"is_generalist": True}, "team_industries": []}
        correct_context2 = {"user": {"is_generalist": False}, "team_industries": [1]}

        next_task_getter.query = None
        next_task_getter.context = None
        self.assertRaises(BadRequestError, next_task_getter._validate_query_and_context)

        next_task_getter.query = {}
        next_task_getter.context = correct_context1
        self.assertRaises(BadRequestError, next_task_getter._validate_query_and_context)

        # Missing stage and process
        next_task_getter.query = {"process": None, "stage": None}
        next_task_getter.context = correct_context1
        self.assertRaises(BadRequestError, next_task_getter._validate_query_and_context)

        # Incorrect stage for process
        next_task_getter.query = {"process": "input_sourcing", "stage": "closed_store_validation"}
        next_task_getter.context = correct_context1
        self.assertRaises(BadRequestError, next_task_getter._validate_query_and_context)

        # Missing user in context
        next_task_getter.query = correct_query1
        next_task_getter.context = {}
        self.assertRaises(BadRequestError, next_task_getter._validate_query_and_context)

        # Invalid user in context
        next_task_getter.query = correct_query1
        next_task_getter.context = {"user": None}
        self.assertRaises(BadRequestError, next_task_getter._validate_query_and_context)

        # Invalid team_industries value in context
        next_task_getter.query = correct_query1
        next_task_getter.context = {"user": {"is_generalist": False, "team_industries": None}}
        self.assertRaises(BadRequestError, next_task_getter._validate_query_and_context)

        next_task_getter.query = correct_query1
        next_task_getter.context = correct_context1
        next_task_getter._validate_query_and_context()

        next_task_getter.query = correct_query2
        next_task_getter.context = correct_context1
        next_task_getter._validate_query_and_context()

        next_task_getter.query = correct_query3
        next_task_getter.context = correct_context2
        next_task_getter._validate_query_and_context()

        next_task_getter.query = correct_query4
        next_task_getter.context = correct_context2
        next_task_getter._validate_query_and_context()

    ##########################################################################
    # WorkflowNextTaskGetter._check_for_in_progress_validation_tasks_for_user()

    def test_check_for_in_progress_validation_tasks_for_user__valid_task(self):

        query = "query"
        tasks = [1]
        self.mock._get_in_progress_validation_tasks().AndReturn(tasks)
        self.mock._validate_existing_task_based_on_query(query, tasks[0]).AndReturn(True)

        def assign_rir(*args, **kwargs):
            self.mock.rir = 1

        self.mock._get_target_rir_for_task().WithSideEffects(assign_rir)

        entity_matcher_results = "entity_matcher_results"
        self.mock._get_entity_matcher_results_for_rir_and_task().AndReturn(entity_matcher_results)

        self.mock._update_old_and_new_match_links()

        self.mox.ReplayAll()

        self.mock.query = query
        WorkflowNextTaskGetter._check_for_in_progress_validation_tasks_for_user(self.mock)

        self.assertEqual(self.mock.rir, 1)
        self.assertEqual(self.mock.task, 1)
        self.assertEqual(self.mock.entity_matcher_results, entity_matcher_results)


    def test_check_for_in_progress_validation_tasks_for_user__invalid_rir(self):

        query = "query"
        tasks = [1]
        self.mock._get_in_progress_validation_tasks().AndReturn(tasks)
        self.mock._validate_existing_task_based_on_query(query, tasks[0]).AndReturn(True)

        def assign_rir(*args, **kwargs):
            self.mock.rir = None

        self.mock._get_target_rir_for_task().WithSideEffects(assign_rir)

        self.mox.ReplayAll()

        self.mock.query = query
        WorkflowNextTaskGetter._check_for_in_progress_validation_tasks_for_user(self.mock)

        self.assertIsNone(self.mock.rir)
        self.assertEqual(self.mock.task, 1)

    def test_check_for_in_progress_validation_tasks_for_user__invalid_task(self):

        query = "query"
        tasks = [None]
        self.mock._get_in_progress_validation_tasks().AndReturn(tasks)
        self.mock._validate_existing_task_based_on_query(query, tasks[0])

        self.mox.ReplayAll()

        self.mock.query = query
        WorkflowNextTaskGetter._check_for_in_progress_validation_tasks_for_user(self.mock)

        self.assertFalse(hasattr(self.mock, "task"))
        self.assertFalse(hasattr(self.mock, "rir"))




    ##########################################################################
    # WorkflowNextTaskGetter._get_next_task_and_rir_if_necessary()

    def test_get_next_task_and_rir_if_necessary(self):

        def reset_keep_looking(*args, **kwargs):
            self.mock.keep_looking = True

        self.mock._process_next_potential_rir_and_task().WithSideEffects(reset_keep_looking)
        self.mock._process_next_potential_rir_and_task()

        self.mock.keep_looking = True

        self.mox.ReplayAll()
        WorkflowNextTaskGetter._get_next_task_and_rir_if_necessary(self.mock)

        self.assertFalse(self.mock.keep_looking)

    ##########################################################################
    # WorkflowNextTaskGetter._get_in_progress_validation_tasks()

    def test_get_rir_exact_match_from_entity_matcher_results(self):

        params = {"query": {"context_data.user_id": 1,
                            "flow": "retail_curation",
                            "process": {"$in": ["input_sourcing", "company_data_curation"]},
                            "stage": {"$in": ["churn_validation",
                                              "new_store_validation_qc",
                                              "closed_store_validation",
                                              "closed_store_validation_qc"]},
                            "task_status.status": "in_progress"},
                  "options": {"has_metadata": True}}

        self.mock.main_access.wfs.call_task_find(self.context, params).AndReturn([1])

        self.mox.ReplayAll()
        results = WorkflowNextTaskGetter._get_in_progress_validation_tasks(self.mock)
        self.assertEqual(results, [1])

    def test_get_rir_exact_match_from_entity_matcher_results__find_task_service_call_error(self):

        params = {"query": {"context_data.user_id": 1,
                            "flow": "retail_curation",
                            "process": {"$in": ["input_sourcing", "company_data_curation"]},
                            "stage": {"$in": ["churn_validation",
                                              "new_store_validation_qc",
                                              "closed_store_validation",
                                              "closed_store_validation_qc"]},
                            "task_status.status": {"$in":["in_progress","saving_validation"]}},
                  "options": {"has_metadata": True}}

        def raise_service_call_error(*args, **kwargs):
            raise ServiceCallError

        self.mock.main_access.wfs.call_task_find(self.context, params).WithSideEffects(raise_service_call_error)

        self.mox.ReplayAll()
        results = WorkflowNextTaskGetter._get_in_progress_validation_tasks(self.mock)
        self.assertEqual(results, [])

    ##########################################################################
    # WorkflowNextTaskGetter._get_target_rir_for_task()

    def test_get_target_rir_for_task__invalid_target_rir_id(self):

        next_task_getter = WorkflowNextTaskGetter.__new__(WorkflowNextTaskGetter)

        next_task_getter.task = {"_id": 1}
        self.assertRaises(DataError, next_task_getter._get_target_rir_for_task)

        next_task_getter.task = {"_id": 1, "input": None}
        self.assertRaises(DataError, next_task_getter._get_target_rir_for_task)

        next_task_getter.task = {"_id": 1, "input": {}}
        self.assertRaises(DataError, next_task_getter._get_target_rir_for_task)

        next_task_getter.task = {"_id": 1, "input": {"target_rir_id": None}}
        self.assertRaises(DataError, next_task_getter._get_target_rir_for_task)

    def test_get_target_rir_for_task__valid_rir(self):

        task_id = 1
        rir_id = 2
        self.mock.task = {"_id": task_id, "input": {"target_rir_id": rir_id}}

        rir = 3
        self.mock.main_access.mds.call_get_entity("retail_input_record", rir_id).AndReturn(rir)

        keep_looking = False

        self.mox.ReplayAll()
        result = WorkflowNextTaskGetter._get_target_rir_for_task(self.mock)

        self.assertEqual(keep_looking, self.mock.keep_looking)

    def test_get_target_rir_for_task__invalid_rir(self):

        task_id = 1
        rir_id = 2
        self.mock.task = {"_id": task_id, "input": {"target_rir_id": rir_id}}

        rir = None
        self.mock.main_access.mds.call_get_entity("retail_input_record", rir_id).AndReturn(rir)

        self.mock.main_access.wfs.call_delete_task_id(task_id)

        self.mox.ReplayAll()
        WorkflowNextTaskGetter._get_target_rir_for_task(self.mock)

        self.assertEqual(None, self.mock.task)
        self.assertEqual(None, self.mock.rir)

    ##########################################################################
    # WorkflowNextTaskGetter._process_next_potential_rir_and_task()

    def test_process_next_potential_rir_and_task__valid_task_and_rir__exact_match(self):

        self.mock._get_next_open_task().AndReturn(self.mock)

        rir_id = generate_id()
        as_of_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        self.mock.task = {"stage": "churn_validation"}
        self.mock.rir = {"_id": rir_id, "data": {"as_of_date": as_of_date}}

        self.mock._get_target_rir_for_task()

        match_id = generate_id()
        match_list = [(match_id, None)]
        entity_matcher_results = {"summary": {"exact": match_list}}
        self.mock._get_entity_matcher_results_for_rir_and_task().AndReturn(entity_matcher_results)

        self.mock._get_rir_exact_match_from_entity_matcher_results(rir_id, {"exact": match_list}).AndReturn(match_list)

        params = "params"
        self.mock.main_param.mds.create_params(resource="find_entities_raw", query=mox.IgnoreArg(),
                                               entity_fields=mox.IgnoreArg(), as_list=True).AndReturn({"params": params})

        interval = "interval"
        self.mock.main_access.mds.call_find_entities_raw("store", params, self.context).AndReturn([[None, interval]])

        self.mock.retail_input_validation_helper.rir_store_is_closed_for_as_of_date(
            interval,
            self.mock.rir["data"]["as_of_date"]
        ).AndReturn(False)

        self.mock._handle_exact_match_case(match_list[0][0])

        self.mox.ReplayAll()
        WorkflowNextTaskGetter._process_next_potential_rir_and_task(self.mock)

    def test_process_next_potential_rir_and_task__valid_task_and_rir__no_exact_match(self):

        self.mock._get_next_open_task().AndReturn(self.mock)

        rir_id = generate_id()

        def assign_task_and_rir(*args, **kwargs):
            self.mock.task = {"stage": "churn_validation"}
            self.mock.rir = {"_id": rir_id}

        self.mock._get_target_rir_for_task().WithSideEffects(assign_task_and_rir)

        match_list = []
        entity_matcher_results = {"summary": {"exact": match_list,
                                              "auto_linkable": [],
                                              "inexact": [1],
                                              "none": []}}
        self.mock._get_entity_matcher_results_for_rir_and_task().AndReturn(entity_matcher_results)

        self.mock._get_rir_exact_match_from_entity_matcher_results(rir_id, entity_matcher_results["summary"]).AndReturn(match_list)

        self.mock._handle_no_exact_match_case()

        self.mox.ReplayAll()
        WorkflowNextTaskGetter._process_next_potential_rir_and_task(self.mock)

    def test_process_next_potential_rir_and_task__valid_task_and_rir__no_exact_match__data_error(self):

        self.mock._get_next_open_task().AndReturn(self.mock)

        rir_id = generate_id()

        def assign_task_and_rir(*args, **kwargs):
            self.mock.task = {"stage": "churn_validation"}
            self.mock.rir = {"_id": rir_id}

        self.mock._get_target_rir_for_task().WithSideEffects(assign_task_and_rir)

        match_list = []
        entity_matcher_results = {"summary": {"exact": match_list,
                                              "auto_linkable": [],
                                              "inexact": [],
                                              "none": []}}
        self.mock._get_entity_matcher_results_for_rir_and_task().AndReturn(entity_matcher_results)

        self.mock._get_rir_exact_match_from_entity_matcher_results(rir_id, entity_matcher_results["summary"]).AndReturn(match_list)

        self.mox.ReplayAll()
        self.assertRaises(DataError, WorkflowNextTaskGetter._process_next_potential_rir_and_task, *(self.mock,))

    def test_process_next_potential_rir_and_task__invalid_task_and_rir(self):

        self.mock._get_next_open_task().AndReturn(self.mock)

        def assign_task_and_rir(*args, **kwargs):
            self.mock.task = None
            self.mock.rir = None
        self.mock._get_target_rir_for_task().WithSideEffects(assign_task_and_rir)

        self.mox.ReplayAll()
        WorkflowNextTaskGetter._process_next_potential_rir_and_task(self.mock)

    ##########################################################################
    # WorkflowNextTaskGetter._get_next_open_task()

    def test_get_next_open_task(self):

        query = 1
        task = 2
        self.mock.main_access.wfs.call_task_put_multi_workflow_next(query, self.context).AndReturn(task)

        self.mox.ReplayAll()

        self.mock.query = query
        WorkflowNextTaskGetter._get_next_open_task(self.mock)

        self.assertEqual(self.mock.task, 2)

    def test_get_next_open_task__not_found_error(self):

        query = 1
        task = None
        self.mock.main_access.wfs.call_task_put_multi_workflow_next(query, self.context).AndReturn(task)

        self.mox.ReplayAll()

        self.mock.query = query
        self.assertRaises(NotFoundError, WorkflowNextTaskGetter._get_next_open_task, *(self.mock,))

    ##########################################################################
    # WorkflowNextTaskGetter._validate_existing_task_based_on_query()

    def test_validate_existing_task_based_on_query(self):

        # Mismatching processes
        query = {"process": "input_sourcing", "stage": "churn_validation"}
        task = {"process": "company_data_curation", "stage": "churn_validation"}
        self.assertRaises(BadRequestError, WorkflowNextTaskGetter._validate_existing_task_based_on_query, *(query, task))

        # Wrong task stage for query
        query = {"process": "input_sourcing", "stage": "churn_validation"}
        task = {"process": "input_sourcing", "stage": "closed_store_validation"}
        self.assertRaises(BadRequestError, WorkflowNextTaskGetter._validate_existing_task_based_on_query, *(query, task))

        # Wrong task stage for query
        query = {"process": "input_sourcing", "stage": "churn_validation"}
        task = {"process": "input_sourcing", "stage": "closed_store_validation_qc"}
        self.assertRaises(BadRequestError, WorkflowNextTaskGetter._validate_existing_task_based_on_query, *(query, task))

        # Correct
        query = {"process": "input_sourcing", "stage": "churn_validation"}
        task = {"process": "input_sourcing", "stage": "churn_validation"}
        result = WorkflowNextTaskGetter._validate_existing_task_based_on_query(query, task)
        self.assertEqual(result, True)

        # Correct
        query = {"process": "input_sourcing", "stage": "churn_validation"}
        task = {"process": "input_sourcing", "stage": "new_store_validation_qc"}
        result = WorkflowNextTaskGetter._validate_existing_task_based_on_query(query, task)
        self.assertEqual(result, True)

        # Correct
        query = {"process": "company_data_curation", "stage": "closed_store_validation"}
        task = {"process": "company_data_curation", "stage": "closed_store_validation"}
        result = WorkflowNextTaskGetter._validate_existing_task_based_on_query(query, task)
        self.assertEqual(result, True)

        # Correct
        query = {"process": "company_data_curation", "stage": "closed_store_validation"}
        task = {"process": "company_data_curation", "stage": "closed_store_validation_qc"}
        result = WorkflowNextTaskGetter._validate_existing_task_based_on_query(query, task)
        self.assertEqual(result, True)

    ##########################################################################
    # WorkflowNextTaskGetter._get_entity_matcher_results_for_rir_and_task()

    def test_get_entity_matcher_results_for_rir_and_task(self):

        rir_id = generate_id()
        rir = {"_id": rir_id}
        task = 2
        query = "query"
        self.mock.retail_input_validation_helper.get_entity_matcher_query(rir, task).AndReturn(query)

        params = {"params": "params"}
        self.mock.main_param.mds.create_params(resource = "find_entities_raw", origin = "_get_entity_matcher_results",
                                               entity_fields = mox.IgnoreArg(), query = query, flatten = True).AndReturn(params)

        self.mock.em_access.call_match_entity_vs_set("retail_input_record", rir_id, params["params"]).AndReturn(1)

        self.mox.ReplayAll()

        self.mock.rir = rir
        self.mock.task = task
        result = WorkflowNextTaskGetter._get_entity_matcher_results_for_rir_and_task(self.mock)

        self.assertEqual(result, 1)

    ##########################################################################
    # WorkflowNextTaskGetter._handle_exact_match_case()

    def test_handle_exact_match_case__churn_validation_task(self):

        exact_match_id = 1
        task = {"stage": "churn_validation"}

        self.mock._link_exact_match_to_store_of_rir(exact_match_id)

        self.mox.ReplayAll()

        self.mock.task = task
        WorkflowNextTaskGetter._handle_exact_match_case(self.mock, exact_match_id)

        self.assertEqual(True, self.mock.keep_looking)
        self.assertEqual(None, self.mock.task)
        self.assertEqual(None, self.mock.rir)

    def test_handle_exact_match_case__closed_store_validation_task(self):

        exact_match_id = 1
        task_id = 2
        task = {"_id": task_id, "stage": "closed_store_validation"}
        commit_data = {"match_rir_id": exact_match_id}
        self.mock.main_access.wfs.call_task_commit(task_id, commit_data, self.context)

        self.mox.ReplayAll()

        self.mock.task = task
        WorkflowNextTaskGetter._handle_exact_match_case(self.mock, exact_match_id)

        self.assertEqual(True, self.mock.keep_looking)
        self.assertEqual(None, self.mock.task)
        self.assertEqual(None, self.mock.rir)

    def test_handle_exact_match_case__invalid_task(self):

        exact_match_id = 1
        task_id = 2
        task = {"_id": task_id, "stage": "asdf"}
        rir = {"_id": 3}

        self.mox.ReplayAll()

        self.mock.task = task
        self.mock.rir = rir
        self.assertRaises(ServiceError, WorkflowNextTaskGetter._handle_exact_match_case, *(self.mock, exact_match_id))

    ##########################################################################
    # WorkflowNextTaskGetter._handle_no_exact_match_case()

    def test_handle_no_exact_match_case__no_task_group_id(self):

        self.mock._update_old_and_new_match_links()

        task = {}

        self.mox.ReplayAll()

        self.mock.task = task
        WorkflowNextTaskGetter._handle_no_exact_match_case(self.mock)

    def test_handle_no_exact_match_case__invalid_stage(self):

        self.mock._update_old_and_new_match_links()

        task = {"stage": "closed_store_validation", "task_group_id": 1}

        self.mox.ReplayAll()

        self.mock.task = task
        WorkflowNextTaskGetter._handle_no_exact_match_case(self.mock)

    def test_handle_no_exact_match_case(self):

        self.mock._update_old_and_new_match_links()

        task = {"stage": "churn_validation", "task_group_id": 1}
        self.mock.main_access.wfs.call_increment_task_group_validation_in_progress(1, self.context)

        self.mox.ReplayAll()

        self.mock.task = task
        WorkflowNextTaskGetter._handle_no_exact_match_case(self.mock)

    ##########################################################################
    # WorkflowNextTaskGetter._update_old_and_new_match_links()

    def test_update_old_and_new_match_links(self):

        self.mox.StubOutWithMock(datetime, 'datetime')

        timestamp = "timestamp"
        datetime.datetime.utcnow().AndReturn(timestamp)

        rir_id1 = generate_id()
        rir_id2 = generate_id()
        rir_id3 = generate_id()

        existing_potential_match_dict = {rir_id3: 1}
        self.mock._get_existing_target_potential_match_dict().AndReturn(existing_potential_match_dict)

        rir = {"_id": rir_id1}
        entity_matcher_results = {"details": {rir_id1: {rir_id2: {"category": "inexact"}}}}

        self.mock._close_interval_for_obsolete_match_links({rir_id3}, existing_potential_match_dict, timestamp).AndReturn([1])

        self.mock._create_new_match_links_from_match_results({rir_id2}, timestamp).AndReturn([2])

        self.mox.ReplayAll()

        self.mock.rir = rir
        self.mock.entity_matcher_results = entity_matcher_results
        result = WorkflowNextTaskGetter._update_old_and_new_match_links(self.mock)
        self.assertListEqual(result, [1, 2])

    ##########################################################################
    # WorkflowNextTaskGetter._get_existing_target_potential_match_dict()

    def test_get_existing_target_potential_match_dict(self):

        rir_id1 = generate_id()
        rir_id2 = generate_id()
        rir = {"_id": rir_id1}

        params = "params"
        params_dict = {"params": params}

        self.mock.main_param.create_params(origin = "_update_old_and_new_match_links",
                                           resource = "get_data_entity_relationships",
                                           field = mox.IgnoreArg(),
                                           relation_types = mox.IgnoreArg(),
                                           field_filters = mox.IgnoreArg()).AndReturn(params_dict)

        results = {"rows": [{"to._id": rir_id1}, {"to._id": rir_id2}]}
        self.mock.main_access.call_get_data_entity_relationships("retail_input_record", "retail_input_record",
                                                                 params = params, context = self.context).AndReturn(results)

        self.mox.ReplayAll()

        self.mock.rir = rir
        result = WorkflowNextTaskGetter._get_existing_target_potential_match_dict(self.mock)
        self.assertEqual(result, {rir_id2: {"to._id": rir_id2}})

    ##########################################################################
    # WorkflowNextTaskGetter._close_interval_for_obsolete_match_links()

    def test_close_interval_for_obsolete_match_links(self):

        rir_id1 = generate_id()
        rir = {"_id": rir_id1}

        match_id = 1
        old_match_ids = {match_id}
        existing_potential_match_dict = {match_id: {"link.interval": None}}

        timestamp = "timestamp"

        self.mock.main_access.mds.call_update_link_without_id('retail_input_record', rir_id1, 'target',
                                                                          'retail_input_record', match_id,
                                                                          'potential_match', 'retail_input', self.context,
                                                                          link_interval = [None, timestamp]).AndReturn(1)

        self.mox.ReplayAll()

        self.mock.rir = rir
        result = WorkflowNextTaskGetter._close_interval_for_obsolete_match_links(self.mock, old_match_ids,
                                                                                 existing_potential_match_dict,
                                                                                 timestamp)
        self.assertEqual(result, [1])

    ##########################################################################
    # WorkflowNextTaskGetter._create_new_match_links_from_match_results()

    def test_create_new_match_links_from_match_results(self):

        rir_id1 = generate_id()
        rir = {"_id": rir_id1}

        match_id = 1
        new_match_ids = {match_id}
        entity_matcher_results = {"details": {rir_id1: {match_id: {"matcher_prediction": "match",
                                                                   "category": "inexact"}}}}

        timestamp = "timestamp"

        self.mock.main_access.mds.call_add_link('retail_input_record', rir_id1, 'target',
                                                            'retail_input_record', match_id,
                                                            'potential_match', 'retail_input', self.context,
                                                            link_data = mox.IgnoreArg(),
                                                            link_interval = [timestamp, None]).AndReturn(1)

        self.mox.ReplayAll()

        self.mock.rir = rir
        self.mock.entity_matcher_results = entity_matcher_results
        result = WorkflowNextTaskGetter._create_new_match_links_from_match_results(self.mock, new_match_ids, timestamp)
        self.assertEqual(result, [1])

    ##########################################################################
    # WorkflowNextTaskGetter._link_exact_match_to_store_of_rir()

    def test_link_exact_match_to_store_of_rir(self):
        """
        This tests the functionality of the _link_exact_match_to_store_of_rir method.
        This tests the fix to RET-1043 (https://nexusri.atlassian.net/browse/RET-1043)
        """
        # Create RetailInputEndpoints and various things it needs.
        # This re-mocks some things mocked in the header, but it makes it easier for this specific test.
        mock_date = "2011-01-01"
        mock_as_of_date = "2012_01-15"
        self.mock.rir = {
            "_id": "chilly_willy",
            "data": {
                "as_of_date": mock_as_of_date
            }
        }
        mock_exact_match_id = "chicken"
        self.mock.task = {
            "_id": "chicken_woot",
            "task_group_id": "wooday",
            "stage": "churn_validation"
        }
        mock_entity_matcher_results_details = { "woot": "danger_zone" }
        self.mock.entity_matcher_results = {
            "summary": { "exact": "chilly_billy" },
            "details": {
                "chilly_willy": {
                    "chicken": mock_entity_matcher_results_details
                }
            }
        }
        mock_match_data = dict(mock_entity_matcher_results_details, match_type = "exact", potential_match_rir_id = "chicken", target_rir_id = "chilly_willy", timestamp = mock_date)
        mock_store_id = "yoyoma"
        mock_field_data = {
            "data.match_type": "exact",
            "data.is_churn_matched": True,
            "data.is_churn_validated": True,
            "data.workflow.current.stage": "churn_validation",
            "data.workflow.retail_curation.input_sourcing.churn_matching.timestamp": mock_date
        }
        mock_commit_data = {"match_rir_id": "chicken"}

        # mock methods
        self.mox.StubOutWithMock(datetime, "datetime")

        # record
        datetime.datetime.utcnow().AndReturn(mock_date)
        self.mock.main_access.mds.call_add_link('retail_input_record', "chilly_willy", 'target', 'retail_input_record', "chicken",
                                                'potential_match', 'retail_input', self.context, link_data = mock_match_data)
        self.mock.rir_helper.get_linked_store_id(self.context, mock_exact_match_id).AndReturn(mock_store_id)
        self.mock.store_helper.add_rir_to_store(self.context, mock_store_id, "chilly_willy", True, mock_as_of_date)
        datetime.datetime.utcnow().AndReturn(mock_date)
        self.mock.main_access.mds.call_update_entity("retail_input_record", "chilly_willy", self.context, field_data = mock_field_data)
        self.mock.main_access.wfs.call_task_commit("chicken_woot", mock_commit_data, self.context)
        self.mock.main_access.wfs.call_increment_task_group_validation_count("wooday", self.context)

        # replay
        self.mox.ReplayAll()

        # bomboj for
        WorkflowNextTaskGetter._link_exact_match_to_store_of_rir(self.mock, mock_exact_match_id)

    ##########################################################################
    # WorkflowNextTaskGetter._get_rir_exact_match_from_entity_matcher_results()

    def test_get_rir_exact_match_from_entity_matcher_results(self):

        entity_matcher_results = get_entity_matcher_summary_results()
        results = WorkflowNextTaskGetter._get_rir_exact_match_from_entity_matcher_results(None, entity_matcher_results["summary"])
        self.assertEqual(len(results), 20)

        rir_id = entity_matcher_results["summary"]["exact"].values()[0][0][0]
        results = WorkflowNextTaskGetter._get_rir_exact_match_from_entity_matcher_results(rir_id, entity_matcher_results["summary"])
        self.assertEqual(len(results), 19)

        rir_id = entity_matcher_results["summary"]["auto_linkable"].values()[0][0][0]
        # making the other set match should cause one less distinct value to come back
        entity_matcher_results["summary"]["exact"] = entity_matcher_results["summary"]["auto_linkable"]
        results = WorkflowNextTaskGetter._get_rir_exact_match_from_entity_matcher_results(rir_id, entity_matcher_results["summary"])
        self.assertEqual(len(results), 18)


if __name__ == "__main__":
    unittest.main()