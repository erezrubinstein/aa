from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.helpers import generate_id
from core.service.svc_main.implementation.data_helper import DataHelper
import unittest
import mox
import math


__author__ = 'vgold'


class MainDataHelperTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(MainDataHelperTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(DataHelper)
        self.mock.coll_data_cache = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_mds_service.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

    def doCleanups(self):

        super(MainDataHelperTests, self).doCleanups()
        dependencies.clear()

    ############################################################
    # MasterDataService.get_data_from_cache()

    def test_get_data_from_cache__row_format_dict__has_header(self):

        cache_id = generate_id()
        input_params = "input_params"
        output_params = "output_params"
        convert_rec_to_db = False
        sort_in_memory = True

        has_header = True
        row_format = "dict"
        has_metadata = True
        options = {"has_metadata": has_metadata,
                   "row_format": row_format,
                   "has_header": has_header}

        data = [{"a": 0, "b": 1, "c": 2}, {"a": 3, "b": 4, "c": 5}]
        count = len(data)
        output = {"meta": {"has_metadata": has_metadata,
                           "num_rows": count,
                           "num_pages": int(math.ceil(count / float(10))),
                           "page_size": 10,
                           "page_index": 0},
                  "rows": data}
        self.mock._fetch_data_from_cache(cache_id, input_params, output_params, convert_rec_to_db, sort_in_memory, has_header).AndReturn(output)

        header = ["a", "b", "c"]
        self.mock._get_results_header(row_format, output_params, data).AndReturn(header)

        output["header"] = header
        output["cache_id"] = cache_id

        self.mox.ReplayAll()
        results = DataHelper.get_data_from_cache(self.mock, cache_id, options, input_params, output_params, convert_rec_to_db, sort_in_memory)
        self.assertEqual(results, output)

    def test_get_data_from_cache__row_format_list__has_header(self):

        cache_id = generate_id()
        input_params = "input_params"
        output_params = "output_params"
        convert_rec_to_db = False
        sort_in_memory = True

        has_header = True
        row_format = "list"
        has_metadata = True
        options = {"has_metadata": has_metadata,
                   "row_format": row_format,
                   "has_header": has_header}

        data = [{"a": 0, "b": 1, "c": 2}, {"a": 3, "b": 4, "c": 5}]
        count = len(data)
        output = {"meta": {"has_metadata": has_metadata,
                           "num_rows": count,
                           "num_pages": int(math.ceil(count / float(10))),
                           "page_size": 10,
                           "page_index": 0},
                  "rows": data}
        self.mock._fetch_data_from_cache(cache_id, input_params, output_params, convert_rec_to_db, sort_in_memory, has_header).AndReturn(output)

        header = ["a", "b", "c"]
        self.mock._get_results_header(row_format, output_params, data).AndReturn(header)

        output["header"] = header

        list_data = [[0, 1, 2], [3, 4, 5]]
        self.mock._get_data_from_cache_row(data, header).AndReturn(list_data)

        self.mox.ReplayAll()
        results = DataHelper.get_data_from_cache(self.mock, cache_id, options, input_params, output_params, convert_rec_to_db, sort_in_memory)

        output["rows"] = list_data
        output["cache_id"] = cache_id

        self.assertEqual(results, output)

    ############################################################
    # MasterDataService._fetch_data_from_cache()

    def test_fetch_data_from_cache__sort_in_memory__list_of_lists(self):

        cache_id = generate_id()
        input_params = "input_params"
        output_params = "output_params"
        convert_rec_to_db = False
        sort_in_memory = True
        has_metadata = True

        (db_query,
         db_fields,
         db_sort,
         db_skip,
         db_limit) = "db_query", "db_fields", "db_sort", 0, 10

        self.mock._get_db_params(cache_id, input_params, output_params,
                                 convert_rec_to_db, sort_in_memory).AndReturn((db_query, db_fields, db_sort, db_skip, db_limit))

        data = [[0, 1, 2], [3, 4, 5]]
        count = len(data)
        cursor = [{"rec": item} for item in data]
        self.mock._get_total_count_and_final_cursor(db_query, db_fields, db_sort, db_skip, db_limit, sort_in_memory).AndReturn((count, cursor))

        db_params = {"fields": db_fields, "sort": db_sort}
        self.mock._sort_list_of_lists_data(data, db_params).AndReturn(data)

        self.mox.ReplayAll()

        results = DataHelper._fetch_data_from_cache(self.mock, cache_id, input_params, output_params, convert_rec_to_db, sort_in_memory, has_metadata)

        output = {"meta": {"has_metadata": has_metadata,
                           "num_rows": count,
                           "num_pages": int(math.ceil(count / float(db_limit))),
                           "page_size": db_limit,
                           "page_index": db_skip / db_limit},
                  "rows": data}
        self.assertEqual(results, output)

    def test_fetch_data_from_cache__list_of_dicts__convert_rec_to_db(self):

        cache_id = generate_id()
        input_params = "input_params"
        output_params = "output_params"
        convert_rec_to_db = True
        sort_in_memory = True
        has_metadata = True

        (db_query,
         db_fields,
         db_sort,
         db_skip,
         db_limit) = "db_query", "db_fields", "db_sort", 0, 10

        self.mock._get_db_params(cache_id, input_params, output_params,
                                 convert_rec_to_db, sort_in_memory).AndReturn((db_query, db_fields, db_sort, db_skip, db_limit))

        data = [{"a": 0, "b": 1, "c": 2}, {"d": 3, "e": 4, "f": 5}]
        count = len(data)
        cursor = [{"rec": item} for item in data]
        self.mock._get_total_count_and_final_cursor(db_query, db_fields, db_sort, db_skip, db_limit, sort_in_memory).AndReturn((count, cursor))

        for item in cursor:
            self.mock._DataHelper__rec_from_db(item["rec"]).AndReturn(item["rec"])

        db_params = {"fields": db_fields, "sort": db_sort}
        self.mock._sort_list_of_dicts_data(data, db_params, convert_rec_to_db).AndReturn(data)

        self.mox.ReplayAll()

        results = DataHelper._fetch_data_from_cache(self.mock, cache_id, input_params, output_params, convert_rec_to_db, sort_in_memory, has_metadata)

        output = {"meta": {"has_metadata": has_metadata,
                           "num_rows": count,
                           "num_pages": int(math.ceil(count / float(db_limit))),
                           "page_size": db_limit,
                           "page_index": db_skip / db_limit},
                  "rows": data}
        self.assertEqual(results, output)

    def test_fetch_data_from_cache__list_of_dicts__convert_rec_to_db__no_limit(self):

        cache_id = generate_id()
        input_params = "input_params"
        output_params = "output_params"
        convert_rec_to_db = True
        sort_in_memory = True
        has_metadata = True

        (db_query,
         db_fields,
         db_sort,
         db_skip,
         db_limit) = "db_query", "db_fields", "db_sort", 0, None

        self.mock._get_db_params(cache_id, input_params, output_params,
                                 convert_rec_to_db, sort_in_memory).AndReturn((db_query, db_fields, db_sort, db_skip, db_limit))

        data = [{"a": 0, "b": 1, "c": 2}, {"d": 3, "e": 4, "f": 5}]
        count = len(data)
        cursor = [{"rec": item} for item in data]
        self.mock._get_total_count_and_final_cursor(db_query, db_fields, db_sort, db_skip, db_limit, sort_in_memory).AndReturn((count, cursor))

        for item in cursor:
            self.mock._DataHelper__rec_from_db(item["rec"]).AndReturn(item["rec"])

        db_params = {"fields": db_fields, "sort": db_sort}
        self.mock._sort_list_of_dicts_data(data, db_params, convert_rec_to_db).AndReturn(data)

        self.mox.ReplayAll()

        results = DataHelper._fetch_data_from_cache(self.mock, cache_id, input_params, output_params, convert_rec_to_db, sort_in_memory, has_metadata)

        output = {"meta": {"has_metadata": has_metadata,
                           "num_rows": count},
                  "rows": data}
        self.assertEqual(results, output)

    def test_fetch_data_from_cache__list_of_dicts__convert_rec_to_db__no_skip(self):

        cache_id = generate_id()
        input_params = "input_params"
        output_params = "output_params"
        convert_rec_to_db = True
        sort_in_memory = True
        has_metadata = True

        (db_query,
         db_fields,
         db_sort,
         db_skip,
         db_limit) = "db_query", "db_fields", "db_sort", None, 10

        self.mock._get_db_params(cache_id, input_params, output_params,
                                 convert_rec_to_db, sort_in_memory).AndReturn((db_query, db_fields, db_sort, db_skip, db_limit))

        data = [{"a": 0, "b": 1, "c": 2}, {"d": 3, "e": 4, "f": 5}]
        count = len(data)
        cursor = [{"rec": item} for item in data]
        self.mock._get_total_count_and_final_cursor(db_query, db_fields, db_sort, db_skip, db_limit, sort_in_memory).AndReturn((count, cursor))

        for item in cursor:
            self.mock._DataHelper__rec_from_db(item["rec"]).AndReturn(item["rec"])

        db_params = {"fields": db_fields, "sort": db_sort}
        self.mock._sort_list_of_dicts_data(data, db_params, convert_rec_to_db).AndReturn(data)

        self.mox.ReplayAll()

        results = DataHelper._fetch_data_from_cache(self.mock, cache_id, input_params, output_params, convert_rec_to_db, sort_in_memory, has_metadata)

        output = {"meta": {"has_metadata": has_metadata,
                           "num_rows": count,
                           "num_pages": int(math.ceil(count / float(db_limit)))},
                  "rows": data}
        self.assertEqual(results, output)


if __name__ == '__main__':
    unittest.main()