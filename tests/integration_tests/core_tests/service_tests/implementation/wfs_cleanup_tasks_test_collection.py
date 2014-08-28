from core.common.utilities.helpers import ensure_id
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_store, insert_test_rir, insert_test_company_competition_instance
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from common.service_access.utilities.errors import ServiceCallError
from bson.objectid import ObjectId


__author__ = "vgold"


class WFSCleanupTasksTestCollection(ServiceTestCollection):

    def initialize(self):

        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            "user_id": ObjectId(),
            "source": "wfs_cleanup_tasks_test_collection.py"
        }

    def setUp(self):

        self.mds_access.call_delete_reset_database()

    def test_most_correct_rir_fixer(self):

        cid = insert_test_company(type="retail_banner")

        sid1 = insert_test_store(cid, [None, None])
        sid2 = insert_test_store(cid, [None, None])
        sid3 = insert_test_store(cid, [None, None])
        sid4 = insert_test_store(cid, [None, None])
        sid5 = insert_test_store(cid, [None, None])

        rid1 = insert_test_rir(self.context, cid, is_most_correct=True)
        rid2 = insert_test_rir(self.context, cid)
        rid3 = insert_test_rir(self.context, cid)
        rid4 = insert_test_rir(self.context, cid, is_most_correct=True)
        rid5 = insert_test_rir(self.context, cid)

        self._link_rir_to_store(rid1, sid1, is_most_correct=True)
        self._link_rir_to_store(rid2, sid2, is_most_correct=True)
        self._link_rir_to_store(rid3, sid3, is_most_correct=True)
        self._link_rir_to_store(rid4, sid4)
        self._link_rir_to_store(rid5, sid5)

        # rub, baby, run!
        task_rec = {
            "input": { "scheduled": False },
            "meta": { "async": False }
        }
        self.main_access.wfs.call_task_new("retail_curation", "cleanup", "most_correct_rir_fixer", task_rec, self.context)

        # verify each rir is now correct... oy vey.
        self._verify_rir(rid1, True)
        self._verify_rir(rid2, True)
        self._verify_rir(rid3, True)
        self._verify_rir(rid4, False)
        self._verify_rir(rid5, False)

    def test_orphan_task_fixer(self):

        # create two test RIRs
        company_id = insert_test_company()
        rir1_id = insert_test_rir(self.context, company_id)
        rir2_id = insert_test_rir(self.context, company_id)

        # create validation tasks for the test RIRs
        tasks = []
        for rir_id in [rir1_id, rir2_id]:
            validation_task_rec = {
                "input": {"target_rir_id": rir_id},
                "meta": {"async": False}
            }
            task = self.wfs_access.call_task_new("retail_curation", "input_sourcing", "churn_validation",
                                                        validation_task_rec, self.context)

            # make the task in progress so that the fixer fixes it
            update_params = {"task_status.status":"in_progress"}
            self.wfs_access.call_update_task_id(task["_id"], self.context, params=update_params)
            task["task_status"]["status"] = "in_progress"

            tasks.append(task)

        # delete one of the test RIRs to make an orphan
        deleted = self.mds_access.call_del_entity("retail_input_record", rir1_id)

        # call orphan task fixer, which should FIX IT by archiving the first task and then deleting it
        # it should not touch the second task
        result = self.__run_and_test_orphan_task_fixer()

        # try to find the fixed task in archive collection
        archived_params = {"archived": True}
        archived_task = self.wfs_access.call_get_task_id(tasks[0]["_id"], self.context, archived_params)

        # check the IDs match (other tests are in test_wfs_archive_task
        self.test_case.assertEqual(tasks[0]["_id"], archived_task["original_id"])

        # try to find the task in the normal way, which should raise a 404 error since the task should be missing
        self.test_case.assertRaises(ServiceCallError,
                                    self.wfs_access.call_get_task_id,
                                    *(tasks[0]["_id"], self.context))


        # make sure the other task is still there in the regular collection and hasn't been changed
        untouched_task = self.wfs_access.call_get_task_id(tasks[1]["_id"], self.context)
        self.test_case.assertEqual(tasks[1], untouched_task)

        # try to find the task with an archived search, which should raise a 404 since the untouched task shouldn't have been archived
        self.test_case.assertRaises(ServiceCallError,
                                    self.wfs_access.call_get_task_id,
                                    *(tasks[1]["_id"], self.context, archived_params))

    def test_orphan_cci_fixer(self):

        # make test companies
        company_id1 = insert_test_company(name="ABC")
        company_id2 = insert_test_company(name="Easy as 123")
        company_id3 = insert_test_company(name="Do re mi")
        company_id4 = insert_test_company(name="You and me")

        # pair 'em up
        _ = insert_test_company_competition_instance(company_id1, company_id2)
        _ = insert_test_company_competition_instance(company_id3, company_id4)

        # make sure we have CCIs for the pairs
        query = {
            "$or":[
                {"data.pair.entity_id_from": ensure_id(company_id1), "data.pair.entity_id_to": ensure_id(company_id2)},
                {"data.pair.entity_id_from": ensure_id(company_id2), "data.pair.entity_id_to": ensure_id(company_id1)},
                {"data.pair.entity_id_from": ensure_id(company_id3), "data.pair.entity_id_to": ensure_id(company_id4)},
                {"data.pair.entity_id_from": ensure_id(company_id4), "data.pair.entity_id_to": ensure_id(company_id3)}
            ]
        }
        fields = ["_id", "name", "data"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields)["params"]
        ccis = self.main_access.mds.call_find_entities_raw("company_competition_instance", params, self.context)

         # should be 4 CCIs
        self.test_case.assertEqual(len(ccis), 4)

        # delete one of the companies
        self.main_access.mds.call_del_entity("company", company_id1)

        # run orphan cci fixer
        self.__run_and_test_orphan_cci_fixer()

        # make sure we have 2 CCIs left; the other two should be deleted
        query = {
            "$or":[
                {"data.pair.entity_id_from": ensure_id(company_id1), "data.pair.entity_id_to": ensure_id(company_id2)},
                {"data.pair.entity_id_from": ensure_id(company_id2), "data.pair.entity_id_to": ensure_id(company_id1)},
                {"data.pair.entity_id_from": ensure_id(company_id3), "data.pair.entity_id_to": ensure_id(company_id4)},
                {"data.pair.entity_id_from": ensure_id(company_id4), "data.pair.entity_id_to": ensure_id(company_id3)}
            ]
        }
        fields = ["_id", "name", "data"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields)["params"]
        ccis = self.main_access.mds.call_find_entities_raw("company_competition_instance", params, self.context)

         # should be 2 CCIs
        self.test_case.assertEqual(len(ccis), 2)



    # -------------------------- Private Helpers --------------------------- #

    def _verify_rir(self, rir_id, is_most_correct):

        # query rir
        query = { "_id": rir_id }
        fields = ["_id", "data.is_most_correct"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields)["params"]
        rir = self.main_access.mds.call_find_entities_raw("retail_input_record", params, self.context)[0]

        # sweet
        self.test_case.assertEqual(rir["data"]["is_most_correct"], is_most_correct)


    def _link_rir_to_store(self, rir_id, store_id, is_most_correct=False):

        self.main_access.mds.call_add_link("retail_input_record", rir_id, "retail_input_record", "store", store_id,
                                           "store", "retail_input", self.context)

        if is_most_correct:
            self.main_access.mds.call_add_link("retail_input_record", rir_id, "most_correct_record", "store", store_id,
                                               "store", "retail_input", self.context)

    def __run_and_test_orphan_task_fixer(self):

        fixer_task_rec = {
            "input": {"scheduled": False},
            "meta": {"async": False}
        }
        result = self.main_access.wfs.call_task_new("retail_curation", "cleanup", "orphan_task_fixer",
                                                    fixer_task_rec, self.context)

        self.test_case.assertEqual(result["task_status"]["status"], "stopped")
        return result

    def __run_and_test_orphan_cci_fixer(self):

        fixer_task_rec = {
            "input": {"scheduled": False},
            "meta": {"async": False}
        }
        result = self.main_access.wfs.call_task_new("retail_curation", "cleanup", "orphan_cci_fixer",
                                                    fixer_task_rec, self.context)

        self.test_case.assertEqual(result["task_status"]["status"], "stopped")
        return result