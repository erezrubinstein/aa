import pprint
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.service.svc_main.implementation.service_endpoints.endpoint_field_data import STORE_COUNT_DB_FIELDS
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.store_count_file_getter import StoreCountFileGetter
import mox


__author__ = 'vgold'


class StoreCountFileGetterTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(StoreCountFileGetterTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(StoreCountFileGetter)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_param.mds = self.mox.CreateMockAnything()
        self.mock.parse_date = self.mox.CreateMockAnything()
        self.mock.StoreCountTimeSeriesMaintainer = self.mox.CreateMockAnything()
        self.mock.company_store_count_helper = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {
            "user_id": 1,
            "source": "test_store_count_file_getter.py"
        }

        self.mock.context = self.context

    def doCleanups(self):

        super(StoreCountFileGetterTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # StoreCountFileGetter._get_store_count_files()

    def test_get_store_count_files__no_query(self):

        user_params = {
            "sortIndex": 0,
            "sortDirection": 1,
            "pageIndex": 0,
            "pageSize": 10
        }

        sort = [["data.company_name", 1], ["data.t_1", 1]]

        params = "params"
        self.mock.main_param.mds.create_params(origin="get_company_store_collection", resource="find_entities_raw",
                                               sort=sort, limit=10, skip=0, as_list=True, query=mox.IgnoreArg(),
                                               entity_fields=mox.IgnoreArg(), has_metadata=True).AndReturn({"params": params})

        files = "files"
        results = {"rows": files}
        self.mock.main_access.mds.call_find_entities_raw('file', params).AndReturn(results)

        self.mox.ReplayAll()

        self.mock.user_params = user_params
        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        result = StoreCountFileGetter._get_store_count_files(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(results, self.mock.file_results)
        self.assertEqual(files, self.mock.files)

    def test_get_store_count_files__with_query(self):

        query = {"asdf": "asdf"}
        user_params = {
            "sortIndex": 0,
            "sortDirection": 1,
            "pageIndex": 0,
            "pageSize": 10,
            "query": query
        }

        sort = [["data.company_name", 1], ["data.t_1", 1]]

        self.mock._format_store_count_collection_query(query).AndReturn(query)

        params = "params"
        self.mock.main_param.mds.create_params(origin="get_company_store_collection", resource="find_entities_raw",
                                               sort=sort, limit=10, skip=0, as_list=True, query=mox.IgnoreArg(),
                                               entity_fields=mox.IgnoreArg(), has_metadata=True).AndReturn({"params": params})

        files = "files"
        results = {"rows": files}
        self.mock.main_access.mds.call_find_entities_raw('file', params).AndReturn(results)

        self.mox.ReplayAll()

        self.mock.user_params = user_params
        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        result = StoreCountFileGetter._get_store_count_files(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(results, self.mock.file_results)
        self.assertEqual(files, self.mock.files)

    ##########################################################################
    # StoreCountFileGetter._get_stores_for_file_companies()

    def test_get_stores_for_file_companies(self):

        STORE_COUNT_DB_FIELDS = ["data.company_id"]

        files = [
            [1],
            [2],
            [3]
        ]

        params = "params"
        self.mock.main_param.mds.create_find_entities_raw_params(query=mox.IgnoreArg(), entity_fields=mox.IgnoreArg(), as_list=True).AndReturn({"params": params})

        stores = [
            [1, 1, 1],
            [2, 2, 2],
            [3, 3, 3],
            [11, 11, 1]
        ]

        self.mock.main_access.mds.call_find_entities_raw("store", params).AndReturn(stores)

        self.mox.ReplayAll()

        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        self.mock.files = files
        result = StoreCountFileGetter._get_stores_for_file_companies(self.mock)

        self.assertEqual(result, self.mock)

        expected_stores_dict = {
            1: [[1, 1, 1], [11, 11, 1]],
            2: [[2, 2, 2]],
            3: [[3, 3, 3]]
        }
        self.assertEqual(expected_stores_dict, self.mock.company_stores_dict)

    ##########################################################################
    # StoreCountFileGetter._recalculate_store_counts()

    def test_recalculate_store_counts__no_changes(self):

        STORE_COUNT_DB_FIELDS = [
            '_id',
            'data.company_id',
            'data.t_1',
            'data.a_store_count_t_1',
            'data.e_store_count_t_1',
            'data.delta_end',
            'data.delta_end_percent'
        ]

        t_1 = "t_1"
        a_store_count_t_1 = 22

        files = [
            [1, 1, 1, 1, 1, 1, 1],
            [2, 2, t_1, a_store_count_t_1, 2, 2, 2]
        ]

        self.mock.parse_date(1).AndReturn(1)
        self.mock.parse_date(t_1).AndReturn(t_1)

        company_stores_dict = {
            2: "helo"
        }

        self.mock.company_store_count_helper.get_num_active_stores("helo", t_1).AndReturn(a_store_count_t_1)

        self.mox.ReplayAll()

        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        self.mock.company_stores_dict = company_stores_dict
        self.mock.files = files
        result = StoreCountFileGetter._recalculate_store_counts(self.mock)

        self.assertEqual(result, self.mock)

    def test_recalculate_store_counts__with_changes(self):

        STORE_COUNT_DB_FIELDS = [
            '_id',
            'data.company_id',
            'data.t_1',
            'data.a_store_count_t_1',
            'data.e_store_count_t_1',
            'data.delta_end',
            'data.delta_end_percent'
        ]

        t_1 = "t_1"
        a_store_count_t_1 = 22
        e_store_count_t_1 = 20

        files = [
            [1, 1, 1, 1, 1, 1, 1],
            [2, 2, t_1, a_store_count_t_1, e_store_count_t_1, 2, 2]
        ]

        self.mock.parse_date(1).AndReturn(1)
        self.mock.parse_date(t_1).AndReturn(t_1)

        company_stores_dict = {
            2: "helo"
        }

        num_active_stores = a_store_count_t_1 + 1
        self.mock.company_store_count_helper.get_num_active_stores("helo", t_1).AndReturn(num_active_stores)

        delta_end = num_active_stores - e_store_count_t_1
        delta_end_percent = float(num_active_stores - e_store_count_t_1) / num_active_stores

        field_data = {
            "data.a_store_count_t_1": num_active_stores,
            'data.delta_end': delta_end,
            'data.delta_end_percent': delta_end_percent
        }
        self.mock.main_access.mds.call_update_entity('file', 2, self.context, field_data = field_data)

        self.mox.ReplayAll()

        self.mock.STORE_COUNT_DB_FIELDS = STORE_COUNT_DB_FIELDS
        self.mock.company_stores_dict = company_stores_dict
        self.mock.files = files
        result = StoreCountFileGetter._recalculate_store_counts(self.mock)

        self.assertEqual(result, self.mock)

        updated_files = [
            [1, 1, 1, 1, 1, 1, 1],
            [2, 2, t_1, num_active_stores, e_store_count_t_1, 3, 3/23.]
        ]
        self.assertEqual(updated_files, self.mock.files)

    ##########################################################################
    # StoreCountFileGetter._maintain_store_count_time_series()

    def test_maintain_store_count_time_series__no_changed_companies(self):

        changed_company_ids = []

        self.mox.ReplayAll()

        self.mock.changed_company_ids = changed_company_ids
        result = StoreCountFileGetter._maintain_store_count_time_series(self.mock)

        self.assertEqual(result, self.mock)

    def test_maintain_store_count_time_series__with_changed_companies(self):

        changed_company_ids = [1]

        maintainer = self.mox.CreateMockAnything()
        self.mock.StoreCountTimeSeriesMaintainer(changed_company_ids, self.context).AndReturn(maintainer)
        maintainer.run()

        self.mox.ReplayAll()

        self.mock.changed_company_ids = changed_company_ids
        result = StoreCountFileGetter._maintain_store_count_time_series(self.mock)

        self.assertEqual(result, self.mock)

    ##########################################################################
    # StoreCountFileGetter._format_store_count_collection_query()

    def test_get_changed_company_file_dict__string_query(self):

        query = "asdf"
        result = StoreCountFileGetter._format_store_count_collection_query(query)

        expected = {
            "$or": [
                {'data.company_id': {"$regex": unicode(query), "$options": "i"}},
                {'data.company_name': {"$regex": unicode(query), "$options": "i"}},
                {'data.t_0': {"$regex": unicode(query), "$options": "i"}},
                {'data.t_1': {"$regex": unicode(query), "$options": "i"}}
            ]
        }

        self.assertDictEqual(result, expected)

    def test_get_changed_company_file_dict__string_query_with_special_characters(self):

        query = "asdf!-$"
        result = StoreCountFileGetter._format_store_count_collection_query(query)

        updated_query = "asdf..."
        expected = {
            "$or": [
                {'data.company_id': {"$regex": unicode(updated_query), "$options": "i"}},
                {'data.company_name': {"$regex": unicode(updated_query), "$options": "i"}},
                {'data.t_0': {"$regex": unicode(updated_query), "$options": "i"}},
                {'data.t_1': {"$regex": unicode(updated_query), "$options": "i"}}
            ]
        }

        self.assertDictEqual(result, expected)

    def test_get_changed_company_file_dict__int_query(self):

        query = "2"
        result = StoreCountFileGetter._format_store_count_collection_query(query)

        expected = {
            "$or": [
                {'data.e_store_count_t_1': int(query)},
                {'data.a_store_count_t_1': int(query)},
                {'data.delta_end': int(query)},
                {'data.e_store_count_t_0': int(query)},
                {'data.a_store_count_t_0': int(query)},
                {'data.company_id': {"$regex": unicode(query), "$options": "i"}},
                {'data.company_name': {"$regex": unicode(query), "$options": "i"}},
                {'data.t_0': {"$regex": unicode(query), "$options": "i"}},
                {'data.t_1': {"$regex": unicode(query), "$options": "i"}}
            ]
        }

        self.assertDictEqual(result, expected)
