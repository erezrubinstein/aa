from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import BadRequestError, NotFoundError, DataError
from core.common.utilities.helpers import generate_id
from core.service.svc_main.implementation.service_endpoints.endpoint_field_data import STORE_COUNT_DB_FIELDS
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.store_count_file_updater import StoreCountFileUpdater
import mox


__author__ = 'vgold'


class StoreCountFileUpdaterTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(StoreCountFileUpdaterTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(StoreCountFileUpdater)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_param.mds = self.mox.CreateMockAnything()
        self.mock.StoreCountTimeSeriesMaintainer = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {
            "user_id": 1,
            "source": "test_store_count_file_updater.py"
        }

        self.mock.context = self.context

    def doCleanups(self):

        super(StoreCountFileUpdaterTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # StoreCountFileUpdater._validate_request_data()

    def test_validate_request_data(self):

        updater = StoreCountFileUpdater.__new__(StoreCountFileUpdater)

        correct_request_data1 = {
            "company_id": 1,
            "e_store_count_t_1": 1,
            "f_A_t_1_needs_review": 1,
            "f_E_t_1_needs_review": 1
        }

        correct_request_data2 = {
            "company_id": 1,
            "e_store_count_t_1": "1",
            "f_A_t_1_needs_review": 1,
            "f_E_t_1_needs_review": 1
        }

        updater.request_data = {}
        with self.assertRaises(BadRequestError):
            updater._validate_request_data()

        updater.request_data = dict(correct_request_data1, company_id="")
        with self.assertRaises(BadRequestError):
            updater._validate_request_data()

        updater.request_data = dict(correct_request_data1, e_store_count_t_1="")
        with self.assertRaises(BadRequestError):
            updater._validate_request_data()

        updater.request_data = dict(correct_request_data1, f_A_t_1_needs_review="")
        with self.assertRaises(BadRequestError):
            updater._validate_request_data()

        updater.request_data = dict(correct_request_data1, f_E_t_1_needs_review="")
        with self.assertRaises(BadRequestError):
            updater._validate_request_data()

        updater.request_data = dict(correct_request_data1, e_store_count_t_1="asdf")
        with self.assertRaises(BadRequestError):
            updater._validate_request_data()

        updater.request_data = correct_request_data1
        result = updater._validate_request_data()
        self.assertEqual(result, updater)

        updater.request_data = correct_request_data2
        result = updater._validate_request_data()
        self.assertEqual(result, updater)

    ##########################################################################
    # StoreCountFileUpdater._get_store_count_file_to_update()

    def test_get_store_count_file_to_update__with_file(self):

        file_id = str(generate_id())
        company_id = str(generate_id())

        params = "params"
        self.mock.main_param.mds.create_params(origin="_get_store_count_file_to_update", resource="find_entities_raw",
                                               query=mox.IgnoreArg(), entity_fields=mox.IgnoreArg(), flatten=True).AndReturn({"params": params})

        mds_file = 'file'
        self.mock.main_access.mds.call_find_entities_raw("file", params).AndReturn([mds_file])

        self.mox.ReplayAll()

        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        self.mock.file_id = file_id
        self.mock.company_id = company_id
        result = StoreCountFileUpdater._get_store_count_file_to_update(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(mds_file, self.mock.file)

    def test_get_store_count_file_to_update__no_file(self):

        file_id = str(generate_id())
        company_id = str(generate_id())

        params = "params"
        self.mock.main_param.mds.create_params(origin="_get_store_count_file_to_update", resource="find_entities_raw",
                                               query=mox.IgnoreArg(), entity_fields=mox.IgnoreArg(), flatten=True).AndReturn({"params": params})

        self.mock.main_access.mds.call_find_entities_raw("file", params).AndReturn([])

        self.mox.ReplayAll()

        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        self.mock.file_id = file_id
        self.mock.company_id = company_id
        with self.assertRaises(NotFoundError):
            StoreCountFileUpdater._get_store_count_file_to_update(self.mock)

    def test_get_store_count_file_to_update__multiple_files(self):

        file_id = str(generate_id())
        company_id = str(generate_id())

        params = "params"
        self.mock.main_param.mds.create_params(origin="_get_store_count_file_to_update", resource="find_entities_raw",
                                               query=mox.IgnoreArg(), entity_fields=mox.IgnoreArg(), flatten=True).AndReturn({"params": params})

        self.mock.main_access.mds.call_find_entities_raw("file", params).AndReturn([1, 1])

        self.mox.ReplayAll()

        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        self.mock.file_id = file_id
        self.mock.company_id = company_id
        with self.assertRaises(DataError):
            StoreCountFileUpdater._get_store_count_file_to_update(self.mock)

    ##########################################################################
    # StoreCountFileUpdater._update_store_count_file()

    def test_update_store_count_file(self):

        a_store_count_t_1 = 8

        f_A_t_1_needs_review = 1
        f_E_t_1_needs_review = 1
        e_store_count_t_1 = 10

        _file = {
            'data.a_store_count_t_1': a_store_count_t_1
        }

        file_id = generate_id()

        file_data = {
            "data.f_A_t_1_needs_review": f_A_t_1_needs_review,
            "data.f_E_t_1_needs_review": f_E_t_1_needs_review,
            "data.e_store_count_t_1": e_store_count_t_1,
            "data.a_store_count_t_1": a_store_count_t_1,
            "data.delta_end": a_store_count_t_1 - e_store_count_t_1,
            "data.delta_end_percent": float(a_store_count_t_1 - e_store_count_t_1) / a_store_count_t_1
        }

        self.mock.main_access.mds.call_update_entity('file', file_id, self.context, field_data = file_data)

        self.mox.ReplayAll()

        self.mock.f_A_t_1_needs_review = f_A_t_1_needs_review
        self.mock.f_E_t_1_needs_review = f_E_t_1_needs_review
        self.mock.e_store_count_t_1 = e_store_count_t_1
        self.mock.file = _file
        self.mock.file_id = file_id
        result = StoreCountFileUpdater._update_store_count_file(self.mock)

        self.assertEqual(result, self.mock)

    ##########################################################################
    # StoreCountFileUpdater._maintain_store_count_time_series()

    def test_maintain_store_count_time_series(self):

        company_id = 1
        company_ids = [company_id]

        maintainer = self.mox.CreateMockAnything()
        self.mock.StoreCountTimeSeriesMaintainer(company_ids, self.context).AndReturn(maintainer)
        maintainer.run()

        self.mox.ReplayAll()

        self.mock.company_id = company_id
        result = StoreCountFileUpdater._maintain_store_count_time_series(self.mock)

        self.assertEqual(result, self.mock)

