from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.retail_input_file_uploader import RetailInputFileUploader
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import BadRequestError, ForbiddenError, ServiceError
from core.common.utilities.helpers import generate_id
import datetime
import mox


__author__ = 'vgold'


class RetailInputFileUploaderTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RetailInputFileUploaderTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get several dependencies that we'll need in the class
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(RetailInputFileUploader)
        self.mock.excel_helper = self.mox.CreateMockAnything()
        self.mock.CompanyInfo = self.mox.CreateMockAnything()
        self.mock.WorkflowTaskGroup = self.mox.CreateMockAnything()
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_single_rir_adder.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

        self.mock.context = self.context

    def doCleanups(self):

        super(RetailInputFileUploaderTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # RetailInputFileUploader._validate_request_data()

    def test_validate_request_data(self):

        rif_uploader = RetailInputFileUploader.__new__(RetailInputFileUploader)
        rif_uploader.request_data = None
        self.assertRaises(BadRequestError, rif_uploader._validate_request_data)

        rif_uploader.request_data = {}
        self.assertRaises(BadRequestError, rif_uploader._validate_request_data)

        rif_uploader.request_data = {"company_id": None, "company_name": None, "is_comprehensive": None, "is_async": None}
        self.assertRaises(BadRequestError, rif_uploader._validate_request_data)

        rif_uploader.request_data = {"company_id": None, "company_name": "asdf", "is_comprehensive": True, "is_async": True}
        self.assertRaises(BadRequestError, rif_uploader._validate_request_data)

        rif_uploader.request_data = {"company_id": "asdf", "company_name": None, "is_comprehensive": True, "is_async": True}
        self.assertRaises(BadRequestError, rif_uploader._validate_request_data)

        rif_uploader.request_data = {"company_id": "asdf", "company_name": "asdf", "is_comprehensive": None, "is_async": True}
        self.assertRaises(BadRequestError, rif_uploader._validate_request_data)

        rif_uploader.request_data = {"company_id": "asdf", "company_name": "asdf", "is_comprehensive": True, "is_async": None}
        self.assertRaises(BadRequestError, rif_uploader._validate_request_data)

        rif_uploader.request_data = {"company_id": "asdf", "company_name": "asdf", "is_comprehensive": True, "is_async": True}
        result = rif_uploader._validate_request_data()

        self.assertEqual(result, rif_uploader)

        self.assertDictEqual({"company_id": "asdf", "company_name": "asdf", "is_comprehensive": True, "is_async": True},
                             {"company_id": rif_uploader.company_id, "company_name": rif_uploader.company_name,
                              "is_comprehensive": rif_uploader.is_comprehensive, "is_async": rif_uploader.is_async})

    ##########################################################################
    # RetailInputFileUploader._validate_request_file()

    def test_validate_request_file__invalid_files_dict(self):

        rif_uploader = RetailInputFileUploader.__new__(RetailInputFileUploader)
        rif_uploader.request_files = None
        self.assertRaises(BadRequestError, rif_uploader._validate_request_file)

        rif_uploader.request_files = {}
        self.assertRaises(BadRequestError, rif_uploader._validate_request_file)

        rif_uploader.request_files = {"asdf": "asdf"}
        self.assertRaises(BadRequestError, rif_uploader._validate_request_file)

    def test_validate_request_file__incorrect_company_name(self):

        filename = "a"
        company_name = "b"
        file_obj = self.mox.CreateMockAnything()
        request_files = {filename: file_obj}

        file_contents = "c"
        file_obj.read().AndReturn(file_contents)
        self.mock.excel_helper.get_company_name(None, file_contents = file_contents).AndReturn(company_name)
        file_obj.seek(0)

        self.mox.ReplayAll()

        self.mock.company_name = "z"
        self.mock.request_files = request_files

        self.assertRaises(BadRequestError, RetailInputFileUploader._validate_request_file, *(self.mock,))

    def test_validate_request_file(self):

        filename = "a"
        company_name = "b"
        file_obj = self.mox.CreateMockAnything()
        request_files = {filename: file_obj}

        file_contents = "c"
        file_obj.read().AndReturn(file_contents)
        self.mock.excel_helper.get_company_name(None, file_contents = file_contents).AndReturn(company_name)
        self.mock.excel_helper.get_as_of_date(filename).AndReturn(datetime.datetime.utcnow() - datetime.timedelta(days=1))
        file_obj.seek(0)

        self.mox.ReplayAll()

        self.mock.company_name = company_name
        self.mock.request_files = request_files

        result = RetailInputFileUploader._validate_request_file(self.mock)

        self.assertEqual(result, self.mock)

    def test_validate_request_file__future_date(self):

        filename = "a"
        company_name = "b"
        file_obj = self.mox.CreateMockAnything()
        request_files = {filename: file_obj}

        file_contents = "c"
        file_obj.read().AndReturn(file_contents)
        self.mock.excel_helper.get_company_name(None, file_contents = file_contents).AndReturn(company_name)
        self.mock.excel_helper.get_as_of_date(filename).AndReturn(datetime.datetime.utcnow() + datetime.timedelta(days=1))
        file_obj.seek(0)

        self.mox.ReplayAll()

        self.mock.company_name = company_name
        self.mock.request_files = request_files

        self.assertRaises(BadRequestError, RetailInputFileUploader._validate_request_file, *(self.mock,))

    ##########################################################################
    # RetailInputFileUploader._upload_retail_input_file()

    def test_upload_retail_input_file__bad_request_error_wrong_company_name(self):

        retail_input_file_obj = self.mox.CreateMockAnything()
        retail_input_file_obj.filename = "z"

        self.mock.main_access.call_add_files(mox.IgnoreArg(), self.context, mox.IgnoreArg(),
                                             additional_data = mox.IgnoreArg()).AndReturn({})

        self.mox.ReplayAll()

        self.mock.company_name = "a"
        self.mock.company_id = "b"
        self.mock.is_comprehensive = True
        self.mock.is_async = True
        self.mock.retail_input_file_obj = retail_input_file_obj

        self.assertRaises(BadRequestError, RetailInputFileUploader._upload_retail_input_file, *(self.mock,))

    def test_upload_retail_input_file(self):

        company_name = "a"
        filename = "z"
        retail_input_file_obj = self.mox.CreateMockAnything()
        retail_input_file_obj.filename = filename
        mds_file_id = generate_id()

        file_result = {
            "retail_input_files/%s/%s" % (company_name, filename): mds_file_id
        }

        self.mock.main_access.call_add_files(mox.IgnoreArg(), self.context, mox.IgnoreArg(),
                                             additional_data = mox.IgnoreArg()).AndReturn(file_result)

        self.mox.ReplayAll()

        self.mock.company_name = company_name
        self.mock.company_id = "b"
        self.mock.is_comprehensive = True
        self.mock.is_async = True
        self.mock.retail_input_file_obj = retail_input_file_obj

        result = RetailInputFileUploader._upload_retail_input_file(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(mds_file_id, self.mock.mds_file_id)

    ##########################################################################
    # RetailInputFileUploader._create_task_group()

    def test_create_task_group(self):

        filename = "filename"
        file_id = "file_id"
        company_id = "company_id"
        company_name = "company_name"

        as_of_date = "as_of_date"
        self.mock.CompanyInfo.get_date_from_name(filename).AndReturn(as_of_date)

        unique_key = {"source_id": file_id, "company_id": company_id, "as_of_date": as_of_date}
        task_group_data = {"source_name": filename, "company_name": company_name}

        task_group_rec = "task_group_rec"
        self.mock.WorkflowTaskGroup.get_retail_curation_structure(unique_key, ["input_sourcing"], task_group_data).AndReturn(task_group_rec)

        task_group = {"_id": generate_id()}
        self.mock.main_access.wfs.call_task_group_new(task_group_rec, self.context).AndReturn(task_group)

        self.mox.ReplayAll()

        self.mock.company_name = company_name
        self.mock.company_id = company_id
        self.mock.file_name = filename
        self.mock.mds_file_id = file_id

        result = RetailInputFileUploader._create_task_group(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(task_group, self.mock.task_group)

    ##########################################################################
    # RetailInputFileUploader._create_task()

    def test_create_task(self):

        filename = "filename"
        file_id = "file_id"
        company_id = "company_id"
        company_name = "company_name"
        is_async = True

        task_group = {"_id": generate_id()}
        task_rec = {"task_group_id": task_group["_id"], "input": {"mds_file_id": file_id}, "meta": {"async": is_async}}

        task = {"task_status": {"status": "stopped"}}
        self.mock.main_access.wfs.call_task_new("retail_curation", "input_sourcing", "parsing", task_rec, self.context).AndReturn(task)

        updated_task_group = "updated_task_group"
        self.mock.main_access.wfs.call_get_task_group_id(task_group["_id"], self.context).AndReturn(updated_task_group)

        self.mox.ReplayAll()

        self.mock.company_name = company_name
        self.mock.company_id = company_id
        self.mock.file_name = filename
        self.mock.mds_file_id = file_id
        self.mock.is_async = is_async
        self.mock.task_group = task_group

        result = RetailInputFileUploader._create_task(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(task, self.mock.task)
        self.assertEqual(updated_task_group, self.mock.task_group)

    ##########################################################################
    # RetailInputFileUploader._prepare_status_message()

    def test_prepare_status_message__is_async(self):

        rif_uploader = RetailInputFileUploader.__new__(RetailInputFileUploader)
        rif_uploader.is_async = True
        rif_uploader.message = None

        result = rif_uploader._prepare_status_message()

        self.assertEqual(result, rif_uploader)
        self.assertIsNotNone(rif_uploader.message)

    def test_prepare_status_message__not_async(self):

        rif_uploader = RetailInputFileUploader.__new__(RetailInputFileUploader)
        rif_uploader.is_async = False
        rif_uploader.message = None

        rif_uploader.task = {"task_status": {}}
        self.assertRaises(ServiceError, rif_uploader._prepare_status_message)

        rif_uploader.task = {"task_status": {"status": "started"}}
        self.assertRaises(ServiceError, rif_uploader._prepare_status_message)

        rif_uploader.task = {"task_status": {"status": "stopped"}}
        result = rif_uploader._prepare_status_message()

        self.assertEqual(result, rif_uploader)
        self.assertIsNotNone(rif_uploader.message)

