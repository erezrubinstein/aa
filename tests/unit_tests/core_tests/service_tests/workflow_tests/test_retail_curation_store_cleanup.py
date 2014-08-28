from copy import deepcopy
import datetime
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import parse_date
from common.utilities.inversion_of_control import dependencies
from core.service.svc_workflow.implementation.task.implementation.cleanup_tasks.retail_curation_store_cleanup import RetailCurationStoreCleanup

__author__ = 'kingneptune'

class TestRetailCurationStoreCleanup(mox.MoxTestBase):

    def setUp(self):

        super(TestRetailCurationStoreCleanup, self).setUp()
        register_common_mox_dependencies(self.mox)

        self.input_rec = {
            "context": "context",
            "task_id": "task_id",
            "scheduled": "scheduled"
        }

        self.rcsc = RetailCurationStoreCleanup(self.input_rec)
        self.rcsc.main_access = self.mox.CreateMockAnything()
        self.rcsc.main_access.mds = self.mox.CreateMockAnything()

    def doCleanups(self):

        super(TestRetailCurationStoreCleanup, self).doCleanups()
        dependencies.clear()

    def test_get_total_stores_to_delete(self):

        entity_fields = ["meta", "links"]
        query = {
            "$or":[
                {"links.address.address_assignment": []},
                {"links.retail_input_record.retail_input": []}
            ]
        }
        params = {"query": query, "entity_fields": entity_fields}

        self.mox.StubOutWithMock(self.rcsc.main_access.mds, "call_find_entities_raw")
        self.rcsc.main_access.mds.call_find_entities_raw("store", params).AndReturn("ok!")
        self.mox.ReplayAll()

        self.rcsc._get_potentially_bad_stores()
        self.assertEqual("ok!", self.rcsc._potentially_bad_stores)

    def test_delete_those_created_more_than_one_hour_ago(self):

        store_rec = {
            "_id": None,
            "meta": {"created_at": None}
        }
        bad_stores = []
        start = datetime.datetime(2013, 05, 18, 10, 0, 0)

        for i in range(7):

            minutes_to_add = i*15

            bad_store = deepcopy(store_rec)
            bad_store["_id"] = i
            bad_store["meta"]["created_at"] = start + datetime.timedelta(minutes = minutes_to_add)

            bad_stores.append(bad_store)

        run_time = datetime.datetime(2013, 05, 18, 12, 0, 0)

        # just to double double check
        for bad_store in bad_stores:

            if parse_date(bad_store["meta"]["created_at"]) <= run_time - datetime.timedelta(hours = 1):
                self.assertTrue(str(bad_store["_id"] in ["0", "1", "2", "3", "4"]))

            elif parse_date(bad_store["meta"]["created_at"]) > run_time - datetime.timedelta(hours = 1):
                self.assertTrue(str(bad_store["_id"] in ["5", "6"]))

            else:
                raise ValueError

        self.rcsc._potentially_bad_stores = bad_stores


        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn(run_time)


        self.mox.StubOutWithMock(self.rcsc.main_access.mds, "call_update_entity")
        self.rcsc.main_access.mds.call_update_entity("store", "0", self.input_rec["context"], "data.deleted_by", "RetailCurationStoreCleanup")
        self.rcsc.main_access.mds.call_update_entity("store", "1", self.input_rec["context"], "data.deleted_by", "RetailCurationStoreCleanup")
        self.rcsc.main_access.mds.call_update_entity("store", "2", self.input_rec["context"], "data.deleted_by", "RetailCurationStoreCleanup")
        self.rcsc.main_access.mds.call_update_entity("store", "3", self.input_rec["context"], "data.deleted_by", "RetailCurationStoreCleanup")
        self.rcsc.main_access.mds.call_update_entity("store", "4", self.input_rec["context"], "data.deleted_by", "RetailCurationStoreCleanup")

        self.mox.StubOutWithMock(self.rcsc.main_access.mds, "call_del_entity")
        self.rcsc.main_access.mds.call_del_entity("store", "0", error_if_absent = False)
        self.rcsc.main_access.mds.call_del_entity("store", "1", error_if_absent = False)
        self.rcsc.main_access.mds.call_del_entity("store", "2", error_if_absent = False)
        self.rcsc.main_access.mds.call_del_entity("store", "3", error_if_absent = False)
        self.rcsc.main_access.mds.call_del_entity("store", "4", error_if_absent = False)

        self.mox.ReplayAll()

        self.rcsc._delete_those_created_more_than_one_hour_ago()

        expected_results = {
            "summary_stats": {
                "timestamp": run_time.isoformat(),
                "stores_without_address_links": {
                    "created_less_than_one_hour_ago": {
                        "status": "not_deleted",
                        "store_ids": ["5", "6"]
                    },
                    "created_more_than_one_hour_ago": {
                        "status": "deleted",
                        "store_ids": ["0", "1", "2", "3", "4"]
                    }
                }
            }
        }

        self.assertEqual(expected_results, self.rcsc.result)













