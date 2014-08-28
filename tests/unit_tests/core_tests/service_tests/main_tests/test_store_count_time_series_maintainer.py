from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.service.svc_main.implementation.service_endpoints.endpoint_field_data import STORE_COUNT_DB_FIELDS
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.store_count_time_series_maintainer import StoreCountTimeSeriesMaintainer
import mox


__author__ = 'vgold'


class StoreCountTimeSeriesMaintainerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(StoreCountTimeSeriesMaintainerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(StoreCountTimeSeriesMaintainer)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_param.mds = self.mox.CreateMockAnything()
        self.mock.parse_date = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {
            "user_id": 1,
            "source": "test_store_count_time_series_maintainer.py"
        }

        self.mock.context = self.context

    def doCleanups(self):

        super(StoreCountTimeSeriesMaintainerTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # StoreCountTimeSeriesMaintainer._get_changed_company_files()

    def test_get_changed_company_files(self):

        changed_company_ids = [1]

        params = "params"
        self.mock.main_param.mds.create_params(origin="_maintain_store_count_timeseries", resource="find_entities_raw",
                                               query=mox.IgnoreArg(), entity_fields=mox.IgnoreArg(),
                                               as_list=True).AndReturn({"params": params})

        files = "files"
        self.mock.main_access.mds.call_find_entities_raw("file", params).AndReturn(files)

        self.mox.ReplayAll()

        self.mock.changed_company_ids = changed_company_ids
        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        result = StoreCountTimeSeriesMaintainer._get_changed_company_files(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(files, self.mock.files)

    ##########################################################################
    # StoreCountTimeSeriesMaintainer._make_changed_company_file_dict()

    def test_make_changed_company_file_dict(self):

        maintainer = StoreCountTimeSeriesMaintainer.__new__(StoreCountTimeSeriesMaintainer)

        maintainer.STORE_COUNT_DB_FIELDS = ["data.company_id"]

        maintainer.files = [
            [1],
            [2],
            [3],
            [2]
        ]

        result = maintainer._make_changed_company_file_dict()

        self.assertEqual(result, maintainer)

        company_file_dict = {
            1: [[1]],
            2: [[2], [2]],
            3: [[3]]
        }

        self.assertDictEqual(maintainer.changed_company_file_dict, company_file_dict)

    ##########################################################################
    # StoreCountFileGetter._maintain_store_count_timeseries()

    def test_maintain_store_count_timeseries__no_changed_companies(self):

        self.mox.ReplayAll()

        self.mock.changed_company_ids = []
        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        result = StoreCountTimeSeriesMaintainer._maintain_store_count_timeseries(self.mock)

        self.assertEqual(result, self.mock)

    def test_maintain_store_count_timeseries__with_changed_companies(self):

        STORE_COUNT_DB_FIELDS = [
            "_id",
            "name",
            "data.t_1"
        ]

        changed_company_ids = [1, 2, 3]

        changed_company_file_dict = {
            2: [[2, 2, 2], [222, 222, 222], [22, 22, 22]],
            3: [[33, 33, 33], [3, 3, 3]],
            1: [[1, 1, 1]]
        }

        self.mock._update_sorted_company_files([[1, 1, 1]], 0, 1)
        self.mock._update_sorted_company_files([[2, 2, 2], [22, 22, 22], [222, 222, 222]], 0, 1)
        self.mock._update_sorted_company_files([[3, 3, 3], [33, 33, 33]], 0, 1)

        self.mox.ReplayAll()

        self.mock.changed_company_ids = changed_company_ids
        self.mock.changed_company_file_dict = changed_company_file_dict
        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        result = StoreCountTimeSeriesMaintainer._maintain_store_count_timeseries(self.mock)

        self.assertEqual(result, self.mock)

    ##########################################################################
    # StoreCountTimeSeriesMaintainer._update_sorted_company_files()

    def test_update_sorted_company_files(self):

        record0 = [0, "name0"]
        record1 = [1, "name1"]
        record2 = [2, "name2"]
        sorted_files_data = [record0, record1, record2]

        # First iteration
        self.mock._make_store_count_record_from_file_entity(record0).AndReturn(record0)
        self.mock._make_store_count_record_from_file_entity(record1).AndReturn(record1)
        self.mock._update_and_save_first_record(record0[0], record0).AndReturn(record0)
        self.mock._update_and_save_next_record(record1[0], record1, record0[0], record0[1], record0)

        # Second iteration
        self.mock._make_store_count_record_from_file_entity(record1).AndReturn(record1)
        self.mock._make_store_count_record_from_file_entity(record2).AndReturn(record2)
        self.mock._update_and_save_next_record(record2[0], record2, record1[0], record1[1], record1)

        self.mox.ReplayAll()

        StoreCountTimeSeriesMaintainer._update_sorted_company_files(self.mock, sorted_files_data, 0, 1)

    ##########################################################################
    # StoreCountTimeSeriesMaintainer._update_and_save_first_record()

    def test_update_and_save_first_record(self):

        record_id = 1

        record_file_data = {
            "data.asdf": "asdf",
            "data.t_0": "asdf"
        }

        self.mock.main_access.mds.call_update_entity('file', record_id, self.context, field_data = record_file_data)

        self.mox.ReplayAll()

        result = StoreCountTimeSeriesMaintainer._update_and_save_first_record(self.mock, record_id, record_file_data)

        expected_file_data = {
            'data.e_store_count_t_0': None,
            'data.a_store_count_t_0': None,
            'data.t_0': None,
            'data.t_0_mds_file_id': None,
            'data.t_0_mds_file_name': None,
            'data.delta_start': None,
            'data.asdf': 'asdf'
        }

        self.assertDictEqual(result, expected_file_data)

    ##########################################################################
    # StoreCountTimeSeriesMaintainer._update_and_save_next_record()

    def test_update_and_save_next_record(self):

        next_record_id = 1
        next_file_data = {
            'data.a_store_count_t_1': 10,
            'data.e_store_count_t_1': 8
        }

        previous_record_id = 2
        previous_record_name = "name"
        previous_file_data = {
            'data.t_1': 1,
            'data.a_store_count_t_1': 20,
            'data.e_store_count_t_1': 15
        }

        expected_file_data = {
            'data.a_store_count_t_0': 20,
            'data.e_store_count_t_0': 15,
            'data.a_store_count_t_1': 10,
            'data.e_store_count_t_1': 8,
            'data.t_0': 1,
            'data.t_0_mds_file_id': 2,
            'data.t_0_mds_file_name': "name",
            'data.delta_start': 5,
            'data.delta_end': 2,
            'data.delta_end_percent': .2
        }

        self.mock.main_access.mds.call_update_entity('file', next_record_id, self.context, field_data = expected_file_data)

        self.mox.ReplayAll()

        result = StoreCountTimeSeriesMaintainer._update_and_save_next_record(self.mock, next_record_id, next_file_data, previous_record_id, previous_record_name, previous_file_data)

        self.assertDictEqual(result, expected_file_data)

    ##########################################################################
    # StoreCountTimeSeriesMaintainer._make_store_count_record_from_file_entity()

    def test_make_store_count_record_from_file_entity(self):

        maintainer = StoreCountTimeSeriesMaintainer.__new__(StoreCountTimeSeriesMaintainer)
        maintainer.STORE_COUNT_DB_FIELDS = ["_id", "name", "data.asdf"]

        record = [1, 2, "asdf"]

        result = maintainer._make_store_count_record_from_file_entity(record)

        expected_result = {
            'data.asdf': 'asdf'
        }

        self.assertDictEqual(result, expected_result)



