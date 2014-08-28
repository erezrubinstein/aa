from core.service.svc_main.implementation.service_endpoints.retail_input_endpoints import RetailInputEndpoints
from core.service.svc_main.implementation.service_endpoints.endpoint_field_data import *
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
import json
import mox


__author__ = 'vgold'


class RetailInputEndpointsTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RetailInputEndpointsTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get several dependencies that we'll need in the class
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(RetailInputEndpoints)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.em_access = self.mox.CreateMockAnything()
        self.mock.excel_helper = self.mox.CreateMockAnything()

        self.mock.cache_rec_options = {"has_metadata": True}

        self.mock.store_helper = self.mox.CreateMockAnything()
        self.mock.rir_helper = self.mox.CreateMockAnything()
        self.mock.address_helper = self.mox.CreateMockAnything()
        self.mock.WorkflowTaskGroup = self.mox.CreateMockAnything()
        self.mock.CompanyInfo = self.mox.CreateMockAnything()
        self.mock.SingleRirAdder = self.mox.CreateMockAnything()
        self.mock.QCTaskCreator = self.mox.CreateMockAnything()
        self.mock.RetailInputFileUploader = self.mox.CreateMockAnything()
        self.mock.WorkflowNextTaskGetter = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_main_retail_input_endpoints.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

    def doCleanups(self):

        super(RetailInputEndpointsTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # RetailInputEndpoints.get_preset_retail_input_summary_collections()

    def test_get_preset_retail_input_summary_collections(self):

        request = self.mox.CreateMockAnything()
        params = {"helo": "moto"}
        request.args = {"params": json.dumps(params), "context": json.dumps(self.context)}

        paging_params = {"paging_params": "paging_params"}
        self.mock._format_page_and_sort_params(params, field_list = RETAIL_INPUT_SUMMARY_TASK_GROUP_DB_FIELDS).AndReturn(paging_params)

        query = {"query": "query"}
        self.mock._format_query_from_field_filters(RETAIL_INPUT_SUMMARY_TASK_GROUP_SEARCHABLE_DB_FIELDS,
                                                   RETAIL_INPUT_SUMMARY_TASK_GROUP_SEARCHABLE_DB_FIELDS,
                                                   params).AndReturn(query)

        params = dict(paging_params, query = query, fields = RETAIL_INPUT_SUMMARY_TASK_GROUP_DB_FIELDS)
        data = "data"
        self.mock.main_access.wfs.call_task_group_data(self.context, params).AndReturn(data)

        self.mox.ReplayAll()
        results = RetailInputEndpoints.get_preset_retail_input_summary_collections(self.mock, request)
        self.assertEqual(results, data)

    ##########################################################################
    # RetailInputEndpoints.post_retail_input_add_one_record()

    def test_post_retail_input_add_one_record(self):

        data = "data"
        files = "files"

        single_rir_adder = self.mox.CreateMockAnything()
        self.mock.SingleRirAdder(data, files, self.context, async=True).AndReturn(single_rir_adder)
        single_rir_adder.run().AndReturn("a")

        self.mox.ReplayAll()

        results = RetailInputEndpoints.post_retail_input_add_one_record(self.mock, data, files, self.context, True)

        self.assertEqual('a', results)

    ##########################################################################
    # RetailInputEndpoints.post_retail_input_record_validation_create_qc()

    def test_post_retail_input_record_validation_create_qc(self):

        data = "data"

        qc_task_creator = self.mox.CreateMockAnything()
        self.mock.QCTaskCreator(data, self.context).AndReturn(qc_task_creator)
        qc_task_creator.run().AndReturn("a")

        self.mox.ReplayAll()

        results = RetailInputEndpoints.post_retail_input_record_validation_create_qc(self.mock, data, self.context)

        self.assertEqual('a', results)

    ##########################################################################
    # RetailInputEndpoints.post_retail_input_file_upload()

    def test_post_retail_input_file_upload(self):

        data = "data"
        files = "files"

        rif_uploader = self.mox.CreateMockAnything()
        self.mock.RetailInputFileUploader(data, files, self.context).AndReturn(rif_uploader)
        rif_uploader.run().AndReturn("a")

        self.mox.ReplayAll()

        results = RetailInputEndpoints.post_retail_input_file_upload(self.mock, data, files, self.context)

        self.assertEqual('a', results)

    ##########################################################################
    # RetailInputEndpoints.get_preset_retail_input_record_validation_next_target()

    def test_get_preset_retail_input_record_validation_next_target(self):

        query = "query"

        workflow_next_task_getter = self.mox.CreateMockAnything()
        self.mock.WorkflowNextTaskGetter(query, self.context).AndReturn(workflow_next_task_getter)
        workflow_next_task_getter.run().AndReturn("a")

        self.mox.ReplayAll()

        results = RetailInputEndpoints.get_preset_retail_input_record_validation_next_target(self.mock, query, self.context)

        self.assertEqual('a', results)
