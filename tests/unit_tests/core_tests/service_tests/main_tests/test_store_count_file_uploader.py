import datetime
from bson.objectid import ObjectId
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import BadRequestError
from core.common.utilities.helpers import generate_id
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.store_count_file_uploader import StoreCountFileUploader
import mox


__author__ = 'vgold'


class StoreCountFileUploaderTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(StoreCountFileUploaderTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(StoreCountFileUploader)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_param.mds = self.mox.CreateMockAnything()
        self.mock.company_store_count_helper = self.mox.CreateMockAnything()
        self.mock.StoreCountTimeSeriesMaintainer = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {
            "user_id": 1,
            "source": "test_store_count_file_uploader.py"
        }

        self.mock.context = self.context

    def doCleanups(self):

        super(StoreCountFileUploaderTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # StoreCountFileUploader._validate_request_data()

    def test_validate_request_data(self):

        uploader = StoreCountFileUploader.__new__(StoreCountFileUploader)

        correct_files = {
            1: 1
        }

        correct_request_data1 = {
            "company_id": 1,
            "company_name": 1,
            "e_store_count_t_1": 1,
            "t_1": "2013/01/01",
        }

        correct_request_data2 = {
            "company_id": 1,
            "company_name": 1,
            "e_store_count_t_1": "1",
            "t_1": "2013/01/01",
        }

        uploader.files = {}
        uploader.request_data = correct_request_data1
        with self.assertRaises(BadRequestError):
            uploader._validate_request_data()

        uploader.files = correct_files
        
        uploader.request_data = dict(correct_request_data1, company_id="")
        with self.assertRaises(BadRequestError):
            uploader._validate_request_data()

        uploader.request_data = dict(correct_request_data1, company_name="")
        with self.assertRaises(BadRequestError):
            uploader._validate_request_data()

        uploader.request_data = dict(correct_request_data1, e_store_count_t_1="")
        with self.assertRaises(BadRequestError):
            uploader._validate_request_data()

        uploader.request_data = dict(correct_request_data1, t_1="")
        with self.assertRaises(BadRequestError):
            uploader._validate_request_data()

        uploader.request_data = dict(correct_request_data1, t_1="asdf")
        with self.assertRaises(BadRequestError):
            uploader._validate_request_data()

        uploader.request_data = dict(correct_request_data1, t_1="asdf/asdf/asdf")
        with self.assertRaises(BadRequestError):
            uploader._validate_request_data()

        uploader.request_data = correct_request_data1
        result = uploader._validate_request_data()
        self.assertEqual(result, uploader)

        uploader.request_data = correct_request_data2
        result = uploader._validate_request_data()
        self.assertEqual(result, uploader)

    ##########################################################################
    # StoreCountFileUploader._get_company_store_count()
    
    def test_get_company_store_count(self):
        
        company_id = str(generate_id())
        datetime_t_1_date = datetime.datetime.utcnow()
        
        self.mock.company_store_count_helper.get_store_count(company_id, datetime_t_1_date).AndReturn(82)
    
        self.mox.ReplayAll()

        self.mock.company_id = company_id
        self.mock.datetime_t_1_date = datetime_t_1_date
        result = StoreCountFileUploader._get_company_store_count(self.mock)
    
        self.assertEqual(result, self.mock)
        self.assertEqual(82, self.mock.store_count)

    ##########################################################################
    # StoreCountFileUploader._add_file_to_company()

    def test_add_file_to_company(self):

        datetime_t_1_date = "datetime_t_1_date"
        e_store_count_t_1 = 2
        store_count = "1"
        company_id = "company_id"
        company_name = "company_name"

        path = 'retail_store_count_files/%s/' % company_name
        files = {"mock_file_name": 'some_werkzeug_data'}

        initial_data = {
            'file_type': 'store_count_collection_file',
            't_1': datetime_t_1_date,
            'e_store_count_t_1': e_store_count_t_1,
            'a_store_count_t_1': int(store_count),
            'delta_end': int(store_count) - e_store_count_t_1,
            'delta_start': None,
            'e_store_count_t_0': None,
            'a_store_count_t_0': None,
            't_0': None,
            't_0_mds_file_id': None,
            't_0_mds_file_name': None,
            'f_E_t_1_needs_review': -1,
            'f_A_t_1_needs_review': -1,
            'company_id': company_id,
            'company_name': company_name
        }

        mock_file_id = str(ObjectId())
        added_file = {"retail_store_count_files/company_name/mock_file_name": mock_file_id}

        self.mock.main_access.call_add_files(path, self.context, files, additional_data = initial_data).AndReturn(added_file)

        self.mock.main_access.mds.call_add_link('company',
                                                'company_id',
                                                'company',
                                                'file',
                                                mock_file_id,
                                                'store_count_file',
                                                'support_file',
                                                self.context).AndReturn(None)

        self.mox.ReplayAll()

        self.mock.files = files
        self.mock.datetime_t_1_date = datetime_t_1_date
        self.mock.e_store_count_t_1 = e_store_count_t_1
        self.mock.store_count = store_count
        self.mock.company_id = company_id
        self.mock.company_name = company_name
        result = StoreCountFileUploader._add_file_to_company(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(added_file, self.mock.added_file)

    ##########################################################################
    # StoreCountFileUploader._maintain_store_count_time_series()

    def test_maintain_store_count_time_series(self):

        company_id = 1
        company_ids = [company_id]

        maintainer = self.mox.CreateMockAnything()
        self.mock.StoreCountTimeSeriesMaintainer(company_ids, self.context).AndReturn(maintainer)
        maintainer.run()

        self.mox.ReplayAll()

        self.mock.company_id = company_id
        result = StoreCountFileUploader._maintain_store_count_time_series(self.mock)

        self.assertEqual(result, self.mock)

