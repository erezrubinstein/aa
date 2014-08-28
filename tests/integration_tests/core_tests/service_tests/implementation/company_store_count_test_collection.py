from __future__ import division
from core.common.business_logic.service_entity_logic.company_store_count_helper import get_store_count
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_store
import cStringIO as StringIO
import datetime


__author__ = 'vgold'


class CompanyStoreCountTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "main_preset_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):

        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):

        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    ##------------------------------------------------##

    def store_count_test_get_company_store_count(self):

        company_id = insert_test_company(name='Store Count Tester')

        # open forever
        insert_test_store(company_id, None)

        # closed on 05/18/1990
        insert_test_store(company_id, [None, datetime.datetime(1990, 05, 18)])

        # opened on 05/18/1990
        insert_test_store(company_id, [datetime.datetime(1990, 05, 18), None])

        # opened on 11/13/1990
        insert_test_store(company_id, [datetime.datetime(1990, 11, 13), None])

        # opened on 05/18/1991, closed on 05/18/1992
        insert_test_store(company_id, [datetime.datetime(1991, 05, 18), datetime.datetime(1992, 05, 18)])

        #_____________________________ Test Cases ______________________________#

        # before 05/18/1990, count should be 2
        self.test_case.assertEqual(get_store_count(company_id, datetime.datetime(1989, 05, 18)), 2)
        self.test_case.assertEqual(get_store_count(company_id, '1989-05-18T00:00:00'), 2)

        # on 05/18/1990, count should still be 2 (one closed, one opened)
        self.test_case.assertEqual(get_store_count(company_id, datetime.datetime(1990, 05, 18)), 2)
        self.test_case.assertEqual(get_store_count(company_id, '1990-05-18T00:00:00'), 2)

        # on 05/19/1990, count should be still be 2
        self.test_case.assertEqual(get_store_count(company_id, datetime.datetime(1990, 05, 19)), 2)
        self.test_case.assertEqual(get_store_count(company_id, '1990-05-19T00:00:00'), 2)

        # on 11/13/1990, count should be 3 (store closes)
        self.test_case.assertEqual(get_store_count(company_id, datetime.datetime(1990, 11, 13)), 3)
        self.test_case.assertEqual(get_store_count(company_id, '1990-11-13T00:00:00'), 3)

        # on 05/18/1991, count should be 4 (store opens)
        self.test_case.assertEqual(get_store_count(company_id, datetime.datetime(1991, 05, 18)), 4)
        self.test_case.assertEqual(get_store_count(company_id, '1991-05-18T00:00:00'), 4)

        # on 05/18/1992, count should be 3 (store closes)
        self.test_case.assertEqual(get_store_count(company_id, datetime.datetime(1992, 05, 18)), 3)
        self.test_case.assertEqual(get_store_count(company_id, '1992-05-18T00:00:00'), 3)

        # on 05/19/1992, count should still be 3
        self.test_case.assertEqual(get_store_count(company_id, datetime.datetime(1992, 05, 19)), 3)
        self.test_case.assertEqual(get_store_count(company_id, '1992-05-19T00:00:00'), 3)

    def main_preset_test_upload_get_update_store_count_files(self):

        ######################################################
        # Setup
        ######################################################

        # Create company
        company_name = "company_name"
        company_id = insert_test_company(name=company_name)

        # Insert stores
        insert_test_store(company_id, [datetime.datetime(1994, 1, 1), datetime.datetime(1994, 12, 31)])
        insert_test_store(company_id, [datetime.datetime(1994, 1, 1), datetime.datetime(1994, 12, 31)])

        ######################################################
        # Upload store count file
        ######################################################

        year_1994 = datetime.datetime(1994, 6, 15)

        # Prepare data and file for store count file upload
        form_data = {
            "company_id": company_id,
            "company_name": company_name,
            "t_1": "%d/%d/%d" % (year_1994.year, year_1994.month, year_1994.day),
            "e_store_count_t_1": 2
        }

        filename = "year_1994.txt"
        posted_file = {
            filename: StringIO.StringIO("There are 2 stores in 1994.")
        }

        result = self.main_access.call_upload_store_count_file(form_data, posted_file, self.context)

        file_path = result["file_result"].keys()[0]
        mds_file_id1 = result["file_result"].values()[0]
        self.test_case.assertIn(filename, file_path)

        ######################################################
        # Update store count file
        ######################################################

        request_data = {
            "company_id": company_id,
            "e_store_count_t_1": 4,
            "f_A_t_1_needs_review": 1,
            "f_E_t_1_needs_review": 1
        }

        result = self.main_access.call_update_store_count_file(mds_file_id1, request_data, self.context)

        updated_file = result["file"]

        self.test_case.assertEqual(updated_file["name"], file_path)
        self.test_case.assertEqual(updated_file["data.e_store_count_t_1"], 4)
        self.test_case.assertEqual(updated_file["data.f_A_t_1_needs_review"], 1)
        self.test_case.assertEqual(updated_file["data.f_E_t_1_needs_review"], 1)
        self.test_case.assertEqual(updated_file["data.delta_end"], -2)
        self.test_case.assertEqual(updated_file["data.delta_end_percent"], -1.0)

        zero_pad = lambda x: "0%s" % x if x < 10 else x
        date_string = "%s-%s-%sT00:00:00" % (year_1994.year, zero_pad(year_1994.month), zero_pad(year_1994.day))
        self.test_case.assertEqual(updated_file["data.t_1"], date_string)

        ######################################################
        # Get store count file
        ######################################################

        result = self.main_access.call_get_store_count_files({}, self.context)
        self.test_case.assertEqual(len(result["results"]), 1)

        for file_key in updated_file.iterkeys():
            for i, field in enumerate(result["field_list"]):
                if field == file_key or (len(file_key) > 5 and field == file_key[5:]):
                    self.test_case.assertEqual(updated_file[file_key], result["results"][0][i])
                    break

        ######################################################
        # Insert more stores for 1994 and get store count files again to trigger time series maintenance
        ######################################################

        # Insert more stores
        insert_test_store(company_id, [datetime.datetime(1994, 1, 1), datetime.datetime(1994, 12, 31)])
        insert_test_store(company_id, [datetime.datetime(1994, 1, 1), datetime.datetime(1994, 12, 31)])

        result = self.main_access.call_get_store_count_files({}, self.context)
        self.test_case.assertEqual(len(result["results"]), 1)

        ######################################################
        # Upload another store count file
        ######################################################

        insert_test_store(company_id, [datetime.datetime(1996, 1, 1), datetime.datetime(1996, 12, 31)])
        insert_test_store(company_id, [datetime.datetime(1996, 1, 1), datetime.datetime(1996, 12, 31)])
        insert_test_store(company_id, [datetime.datetime(1996, 1, 1), datetime.datetime(1996, 12, 31)])
        insert_test_store(company_id, [datetime.datetime(1996, 1, 1), datetime.datetime(1996, 12, 31)])
        insert_test_store(company_id, [datetime.datetime(1996, 1, 1), datetime.datetime(1996, 12, 31)])
        insert_test_store(company_id, [datetime.datetime(1996, 1, 1), datetime.datetime(1996, 12, 31)])

        year_1996 = datetime.datetime(1996, 6, 15)

        # Prepare data and file for store count file upload
        form_data = {
            "company_id": company_id,
            "company_name": company_name,
            "t_1": "%d/%d/%d" % (year_1996.year, year_1996.month, year_1996.day),
            "e_store_count_t_1": 8
        }

        filename = "year_1996.txt"
        posted_file = {
            filename: StringIO.StringIO("There are 2 stores in 1996.")
        }

        result = self.main_access.call_upload_store_count_file(form_data, posted_file, self.context)

        file_path = result["file_result"].keys()[0]
        mds_file_id2 = result["file_result"].values()[0]
        self.test_case.assertIn(filename, file_path)

        ######################################################
        # Make sure time series is maintained
        ######################################################

        params = {
            "sortIndex": 2,
            "sortDirection": -1
        }

        result = self.main_access.call_get_store_count_files(params, self.context)
        self.test_case.assertEqual(len(result["results"]), 2)

        field_list = result["field_list"]

        entity1 = result["results"][1]

        self.test_case.assertEqual(entity1[field_list.index("e_store_count_t_0")], None)
        self.test_case.assertEqual(entity1[field_list.index("a_store_count_t_0")], None)
        self.test_case.assertEqual(entity1[field_list.index("e_store_count_t_1")], 4)
        self.test_case.assertEqual(entity1[field_list.index("a_store_count_t_1")], 4)
        self.test_case.assertEqual(entity1[field_list.index("delta_end")], 0)
        self.test_case.assertEqual(entity1[field_list.index("delta_end_percent")], 0)

        entity2 = result["results"][0]

        self.test_case.assertEqual(entity2[field_list.index("e_store_count_t_0")], 4)
        self.test_case.assertEqual(entity2[field_list.index("a_store_count_t_0")], 4)
        self.test_case.assertEqual(entity2[field_list.index("e_store_count_t_1")], 8)
        self.test_case.assertEqual(entity2[field_list.index("a_store_count_t_1")], 6)
        self.test_case.assertEqual(entity2[field_list.index("delta_end")], -2)
        self.test_case.assertEqual(entity2[field_list.index("delta_end_percent")], -2/6.)


###################################################################################################


