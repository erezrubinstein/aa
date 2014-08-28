from collections import defaultdict
import datetime

import mox

from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import DataError
from core.common.utilities.helpers import generate_id
from core.service.svc_workflow.implementation.task.implementation.retail_input_tasks.retail_input_closed_store_finder import RetailInputClosedStoreFinder


__author__ = 'vgold'


class RetailInputClosedStoreFinderTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RetailInputClosedStoreFinderTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(RetailInputClosedStoreFinder)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value

        # Emulate init method
        self.mock.company_open_tasks = defaultdict(list)
        self.mock.closure_days = {}
        self.mock.last_confirmation_date = {}
        self.mock.most_recent_records = {}
        self.mock.most_correct_records = {}
        self.mock.potentially_closed_stores = {}
        self.mock.potential_closed_date = datetime.datetime.utcnow()
        self.mock.output = {}

        # Set mock attributes on mock instance for calls to ignore
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.mock.context = {"user_id": 1, "source": "test_workflow_service.py",
                             "user": {"user_id": 1, "is_generalist": False},
                             "team_industries": ["asdf"]}

    def doCleanups(self):

        super(RetailInputClosedStoreFinderTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # RetailInputClosedStoreFinder._get_current_validation_tasks()

    def test_get_current_validation_tasks(self):

        cid1 = generate_id()
        cid2 = generate_id()
        self.mock.company_ids = [cid1, cid2]

        task_query = {
            "query": {
                "input.company_id": {"$in": self.mock.company_ids},
                "task_status.status": {"$in": ["open", "in_progress"]},
                "flow": "retail_curation",
                "process": {"$in": ["input_sourcing", "company_data_curation"]},
                "stage": {"$in": ["parsing", "churn_matching", "churn_validation", "closed_store_validation",
                                  "closed_store_searching","input_file_deletion"]}
            }
        }

        tasks = [
            {
                "_id": generate_id(),
                "input": {"company_id": cid1},
                "stage": "churn_matching",
                "context": {},
                "status": "unknown"
            },
            {
                "_id": generate_id(),
                "input": {"company_id": cid2},
                "stage": "churn_matching",
                "context": {},
                "status": "unknown"
            }
        ]

        company_open_tasks = {
            cid1: [tasks[0]],
            cid2: [tasks[1]]
        }

        self.mock.main_access.wfs.call_task_find(self.mock.context, task_query).AndReturn(tasks)

        self.mox.ReplayAll()

        RetailInputClosedStoreFinder._get_current_validation_tasks(self.mock)

        self.assertEqual(self.mock.company_open_tasks, company_open_tasks)

    ##########################################################################
    # RetailInputClosedStoreFinder._filter_companies_with_open_tasks()

    def test_filter_companies_with_open_tasks__open_tasks(self):

        cid1 = generate_id()
        cid2 = generate_id()
        taskid1 = generate_id()
        taskid2 = generate_id()
        self.mock.company_ids = [cid1, cid2]

        tasks = [
            {
                "_id": taskid1,
                "input": {"company_id": cid1},
                "stage": "churn_matching",
                "context": {"user": "sally"},
                "status": "in_progress"
            },
            {
                "_id": taskid2,
                "input": {"company_id": cid2},
                "stage": "churn_matching",
                "context": {"user": "fred"},
                "status": "in_progress"
            }
        ]

        self.mock.company_open_tasks = {
            cid1: [tasks[0]],
            cid2: [tasks[1]]
        }

        self.mox.ReplayAll()

        RetailInputClosedStoreFinder._filter_companies_with_open_tasks(self.mock)

        self.assertIn(cid1, self.mock.output)
        self.assertIn(cid2, self.mock.output)
        self.assertEqual(len(self.mock.company_ids), 0)

    def test_filter_companies_with_open_tasks__no_open_tasks(self):

        cid1 = generate_id()
        cid2 = generate_id()
        self.mock.company_ids = [cid1, cid2]

        self.mock.company_open_tasks = {}

        self.mox.ReplayAll()

        RetailInputClosedStoreFinder._filter_companies_with_open_tasks(self.mock)

        self.assertEqual(len(self.mock.output), 0)
        self.assertIn(cid1, self.mock.company_ids)
        self.assertIn(cid2, self.mock.company_ids)

    ##########################################################################
    # RetailInputClosedStoreFinder._get_company_closure_threshold()

    def test_get_company_closure_threshold(self):

        cid1 = generate_id()
        cid2 = generate_id()
        cid3 = generate_id()
        cid4 = generate_id()
        cid5 = generate_id()
        self.mock.company_ids = [cid1, cid2, cid3, cid4, cid5]

        data = {"rows": [
            {
                "_id": cid1,
                "data.closure_confirmation_threshold_days": "-730"
            },
            {
                "_id": cid2,
                "data.closure_confirmation_threshold_days": "270"
            },
            {
                "_id": cid3,
                "data.closure_confirmation_threshold_days": "-2.678"
            },
            {
                "_id": cid4,
                "data.closure_confirmation_threshold_days": 14
            },
            {
                "_id": cid5,
                "data.closure_confirmation_threshold_days": "asdf"
            }
        ]}

        self.mock.main_access.call_get_data_entities(entity_type = "company", params = mox.IgnoreArg()).AndReturn(data)

        self.mock._get_date_number_of_days_ago(730).AndReturn(700)
        self.mock._get_date_number_of_days_ago(270).AndReturn(200)
        self.mock._get_date_number_of_days_ago(2).AndReturn(2)
        self.mock._get_date_number_of_days_ago(14).AndReturn(14)

        self.mox.ReplayAll()

        RetailInputClosedStoreFinder._get_company_closure_threshold(self.mock)


        self.assertEqual(len(self.mock.closure_days), 4)
        self.assertEqual(len(self.mock.last_confirmation_date), 4)

        self.assertEqual(self.mock.closure_days[cid1], 730)
        self.assertEqual(self.mock.closure_days[cid2], 270)
        self.assertEqual(self.mock.closure_days[cid3], 2)
        self.assertEqual(self.mock.closure_days[cid4], 14)
        self.assertEqual(self.mock.last_confirmation_date[cid1], 700)
        self.assertEqual(self.mock.last_confirmation_date[cid2], 200)
        self.assertEqual(self.mock.last_confirmation_date[cid3], 2)
        self.assertEqual(self.mock.last_confirmation_date[cid4], 14)

        self.assertEqual(len(self.mock.output), 1)

    ##########################################################################
    # RetailInputClosedStoreFinder._get_rirs()

    def test_get_rirs(self):

        rid1 = generate_id()
        rid2 = generate_id()
        rid3 = generate_id()
        rid4 = generate_id()

        data = [
            {
                "_id": rid1,
                "data": {
                    "is_most_correct": True,
                    "is_most_recent": True
                }
            },
            {
                "_id": rid2,
                "data": {
                    "is_most_correct": False,
                    "is_most_recent": True
                }
            },
            {
                "_id": rid3,
                "data": {
                    "is_most_correct": True,
                    "is_most_recent": False
                }
            },
            {
                "_id": rid4,
                "data": {
                    "is_most_correct": False,
                    "is_most_recent": False
                }
            }
        ]

        self.mock.main_access.mds.call_find_entities_raw("retail_input_record", params = mox.IgnoreArg(), context = self.mock.context).AndReturn(data)

        self.mock._get_store_id_from_rir(data[0]).AndReturn(data[0]["_id"])
        self.mock._get_store_id_from_rir(data[0]).AndReturn(data[0]["_id"])
        self.mock._get_store_id_from_rir(data[1]).AndReturn(data[1]["_id"])
        self.mock._get_store_id_from_rir(data[2]).AndReturn(data[2]["_id"])

        self.mox.ReplayAll()

        self.mock.company_ids = ['a', 'b']

        RetailInputClosedStoreFinder._get_rirs(self.mock)


        self.assertSetEqual(set(self.mock.most_correct_records), {rid1, rid3})
        self.assertSetEqual(set(self.mock.most_recent_records), {rid1, rid2})

    ##########################################################################
    # RetailInputClosedStoreFinder._get_store_id_from_rir(rec)

    def test_get_store_id_from_rir(self):

        store_id = generate_id()

        rec = {
            "links": {
                "store": {
                    "retail_input": [
                        {
                            "entity_id_to": store_id
                        }
                    ]
                }
            }
        }

        result = RetailInputClosedStoreFinder._get_store_id_from_rir(rec)
        self.assertEqual(result, store_id)

        rec = {
            "links": {
                "store": {
                    "retail_input": [
                        {
                            "asdf": store_id
                        }
                    ]
                }
            }
        }

        self.assertRaises(DataError, RetailInputClosedStoreFinder._get_store_id_from_rir, *(rec,))

    ##########################################################################
    # RetailInputClosedStoreFinder._get_stores_filter_closed()

    def test_get_stores_filter_closed(self):

        id1 = generate_id()
        id2 = generate_id()
        id3 = generate_id()
        id4 = generate_id()

        data = [
            {
                "_id": id1
            },
            {
                "_id": id2
            },
            {
                "_id": id3
            },
            {
                "_id": id4
            }
        ]

        self.mock.main_access.mds.call_find_entities_raw("store", params = mox.IgnoreArg(), context = self.mock.context).AndReturn(data)

        self.mock._store_is_closed(data[0]).AndReturn(True)
        self.mock._store_is_closed(data[1]).AndReturn(True)
        self.mock._store_is_closed(data[2]).AndReturn(False)
        self.mock._store_is_closed(data[3]).AndReturn(False)

        self.mox.ReplayAll()

        self.mock.company_ids = ['a', 'b']
        self.mock.most_correct_records = {id1: None, id3: None}
        self.mock.most_recent_records = {id1: None, id3: None}

        RetailInputClosedStoreFinder._get_stores_filter_closed(self.mock)

        self.assertSetEqual(set(self.mock.most_correct_records), {id3})
        self.assertSetEqual(set(self.mock.most_recent_records), {id3})

    ##########################################################################
    # RetailInputClosedStoreFinder._store_is_closed(store)

    def test_store_is_closed(self):

        store = None
        result = RetailInputClosedStoreFinder._store_is_closed(store)
        self.assertEqual(result, False)

        store = {"interval": None}
        result = RetailInputClosedStoreFinder._store_is_closed(store)
        self.assertEqual(result, False)

        store = {"interval": [None, None]}
        result = RetailInputClosedStoreFinder._store_is_closed(store)
        self.assertEqual(result, False)

        past_date_string = str(datetime.datetime.now() + datetime.timedelta(-10))
        store = {"interval": [None, past_date_string]}
        result = RetailInputClosedStoreFinder._store_is_closed(store)
        self.assertEqual(result, True)

        future_date_string = str(datetime.datetime.now() + datetime.timedelta(10))
        store = {"interval": [None, future_date_string]}
        result = RetailInputClosedStoreFinder._store_is_closed(store)
        self.assertEqual(result, False)

    ##########################################################################
    # RetailInputClosedStoreFinder._filter_potentially_closed_stores()

    def test_filter_potentially_closed_stores(self):
        pass

    ##########################################################################
    # RetailInputClosedStoreFinder._create_validation_tasks()

    def test_create_validation_tasks(self):
        pass