from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.company_analytics_plan_b_runner import CompanyAnalyticsPlanBRunner
from core.common.business_logic.service_entity_logic import company_helper
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from bson.objectid import ObjectId
import datetime
import uuid
import mox
import unittest


__author__ = "vgold"


class TestCompanyAnalyticsPlanBRunner(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCompanyAnalyticsPlanBRunner, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies

        # various needed data
        self.context = {"user": "chicken_woot"}

        # main class to be tested
        self.mock = self.mox.CreateMock(CompanyAnalyticsPlanBRunner)
        self.mock.context = self.context
        self.mock.company_ids = [1, 2, 3]
        self.mock.max_pending_hours = 5
        self.mock.max_in_progress_hours = 18
        self.mock.company_ids_to_revert = {"pending": [], "in_progress": []}
        self.mock.main_access = Dependency("CoreAPIProvider").value
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value
        self.mock.logger = Dependency("FlaskLogger").value

    def doCleanups(self):

        # call parent clean up
        super(TestCompanyAnalyticsPlanBRunner, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_run__success(self):

        mock_results = "results"

        self.mock._get_currently_running_companies()
        self.mock._get_run_status_company_id_dict()
        self.mock._fix_expired_company_families("pending")
        self.mock._fix_expired_company_families("in_progress")

        self.mock._get_currently_running_companies()
        self.mock._get_company_families_in_need_of_plan_b()
        self.mock._create_plan_b_tasks_for_company_families()

        self.mock.company_ids_to_revert = {"pending": ["asdf"], "in_progress": ["pdq"]}
        self.mock.created_tasks = ["asdf"]
        self.mock.max_simultaneous_plan_bs_running = True

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = CompanyAnalyticsPlanBRunner.run(self.mock)

        # make sure results are good
        self.assertDictEqual(results, {
            "pending_company_ids_reverted": ["asdf"],
            "in_progress_company_ids_reverted": ["pdq"],
            "num_tasks_created": 1,
            "max_simultaneous_plan_bs_running": True
        })

    def test_run__fail(self):

        def raise_error(*args, **kwargs):
            raise Exception("HOOHAA")

        self.mock._get_currently_running_companies()
        self.mock._get_run_status_company_id_dict()
        self.mock._fix_expired_company_families("pending")
        self.mock._fix_expired_company_families("in_progress")

        self.mock._get_currently_running_companies()
        self.mock._get_company_families_in_need_of_plan_b().WithSideEffects(raise_error)

        # replay all
        self.mox.ReplayAll()

        with self.assertRaises(Exception):
            CompanyAnalyticsPlanBRunner.run(self.mock)

    def test_fix_expired_pending_company_families(self):

        cid1 = ObjectId()
        cid2 = ObjectId()
        cid3 = ObjectId()
        cid4 = ObjectId()

        run_id1 = str(uuid.uuid4())
        run_id2 = str(uuid.uuid4())
        run_id3 = str(uuid.uuid4())

        now = datetime.datetime.utcnow()
        ten_minutes = datetime.timedelta(minutes=10)
        ten_hours = datetime.timedelta(hours=10)

        self.mock.run_status_company_id_dict = {
            "pending": {
                run_id2: {
                    "creation_time": now - ten_minutes,
                    "company_ids": [cid3]
                },
                run_id3: {
                    "creation_time": now - ten_hours,
                    "company_ids": [cid4]
                }
            },
            "in_progress": {
                run_id1: {
                    "creation_time": now,
                    "company_ids": [cid1, cid2]
                }
            }
        }

        query = {
            "_id": {
                "$in": [cid4]
            },
            "data.workflow.analytics.status": "pending",
            "$or": [
                {
                    "data.workflow.analytics.creation_time": {
                        "$lt": mox.IgnoreArg()
                    }
                },
                {
                    "data.workflow.analytics.creation_time": {
                        "$lt": mox.IgnoreArg()
                    }
                }
            ]
        }

        operations = {
            "$set": {
                "data.workflow.analytics.status": "needs_plan_b",
                "data.workflow.analytics.creation_time": None,
                "data.workflow.analytics.run_id": None
            }
        }

        self.mock.main_access.mds.call_batch_update_entities("company", query, operations, self.context)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanBRunner._fix_expired_company_families(self.mock, "pending")

    def test_fix_expired_in_progress_company_families(self):

        cid1 = ObjectId()
        cid2 = ObjectId()
        cid3 = ObjectId()
        cid4 = ObjectId()

        run_id1 = str(uuid.uuid4())
        run_id2 = str(uuid.uuid4())
        run_id3 = str(uuid.uuid4())

        now = datetime.datetime.utcnow()
        ten_minutes = datetime.timedelta(minutes=10)
        twenty_hours = datetime.timedelta(hours=20)

        self.mock.run_status_company_id_dict = {
            "pending": {
                run_id2: {
                    "creation_time": now - ten_minutes,
                    "company_ids": [cid3]
                }
            },
            "in_progress": {
                run_id1: {
                    "creation_time": now,
                    "company_ids": [cid1, cid2]
                },
                run_id3: {
                    "creation_time": now - twenty_hours,
                    "company_ids": [cid4]
                }
            }
        }

        query = {
            "_id": {
                "$in": [cid4]
            },
            "data.workflow.analytics.status": "in_progress",
            "$or": [
                {
                    "data.workflow.analytics.creation_time": {
                        "$lt": mox.IgnoreArg()
                    }
                },
                {
                    "data.workflow.analytics.creation_time": {
                        "$lt": mox.IgnoreArg()
                    }
                }
            ]
        }

        operations = {
            "$set": {
                "data.workflow.analytics.status": "needs_plan_b",
                "data.workflow.analytics.creation_time": None,
                "data.workflow.analytics.run_id": None
            }
        }

        self.mock.main_access.mds.call_batch_update_entities("company", query, operations, self.context)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanBRunner._fix_expired_company_families(self.mock, "in_progress")

    def test_get_company_families_in_need_of_plan_b_positive(self):
        """
        If there are X company families currently running plan b,
        AND config throttles to Y company families,
        AND X is less than Y,
        then we should find Y - X company families to run.
        """
        self.mock.max_simultaneous_plan_bs = 5
        self.mock.currently_running_companies = [[1, "run_id"], [2, "run_id"], [3, "run_id"]]
        needs_plan_b_companies = [[4, None], [5, None], [6, None]]
        expected_number_of_tasks_to_create = 4
        expected_company_families_in_need_of_plan_b = [[4, None], [5, None]]

        self.mock._get_companies_in_need_of_plan_b().AndReturn(needs_plan_b_companies)
        self.mock._get_company_families_to_run(expected_number_of_tasks_to_create, needs_plan_b_companies).AndReturn(expected_company_families_in_need_of_plan_b)
        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanBRunner._get_company_families_in_need_of_plan_b(self.mock)

        self.assertEqual(self.mock.company_families_in_need_of_plan_b, expected_company_families_in_need_of_plan_b)
        self.assertEqual(self.mock.max_simultaneous_plan_bs_running, False)

    def test_get_company_families_in_need_of_plan_b_negative(self):
        """
        If there are X company families currently running plan b,
        AND config throttles to Y company families,
        AND Y is less than or equal Y,
        then we should find exactly 0 company families to run.
        """
        self.mock.max_simultaneous_plan_bs = 5
        self.mock.currently_running_companies = [[1, "run_id1"], [2, "run_id2"], [3, "run_id3"], [4, "run_id4"], [5, "run_id5"]]
        self.mock.company_families_in_need_of_plan_b = None

        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanBRunner._get_company_families_in_need_of_plan_b(self.mock)

        self.assertIsNone(self.mock.company_families_in_need_of_plan_b)
        self.assertEqual(self.mock.max_simultaneous_plan_bs_running, True)


    def test_mark_company_families_in_need_of_plan_b_as_pending(self):

        mock_family = ["family"]
        self.mock.company_families_in_need_of_plan_b = [mock_family]
        self.mock.created_company_family_run_id_dict = {}

        now = datetime.datetime.utcnow()

        self.mox.StubOutWithMock(uuid, "uuid4")
        self.mox.StubOutWithMock(datetime, "datetime")

        uuid.uuid4().AndReturn("UUID")
        datetime.datetime.utcnow().AndReturn(now)

        query = {
            "_id": {
                "$in": mock_family
            }
        }

        operations = {
            "$set": {
                "data.workflow.analytics.run_id": "UUID",
                "data.workflow.analytics.status": "pending",
                "data.workflow.analytics.creation_time": now.strftime("%Y-%m-%dT%H:%M:%S"),
                'data.workflow.analytics.start_time': None,
                'data.workflow.analytics.end_time': None,
                'data.workflow.analytics.exception': None
            }
        }

        self.mock.main_access.mds.call_batch_update_entities("company", query, operations, self.context)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanBRunner._mark_company_families_in_need_of_plan_b_as_pending(self.mock)

        self.assertDictEqual(self.mock.created_company_family_run_id_dict, {
            "family": "UUID"
        })

    def test_launch_plan_b_tasks(self):

        mock_family = ["family"]
        mock_tasks = "mock_tasks"
        self.mock.async = True
        self.mock.start_plan_b_tasks = True
        self.mock.spawn_analytics_calc_subtasks = True
        self.mock.store_count_subtask_threshold = 12
        self.mock.created_company_family_run_id_dict = {
            "family": "UUID"
        }
        self.mock.store_count_per_family = { "family": 10 }

        self.mock.company_families_in_need_of_plan_b = [mock_family]

        task_recs = [
            {
                'input': {
                    "company_id": mock_family[0],
                    "run_id": "UUID",
                    "store_count": 10,
                    "spawn_analytics_calc_subtasks": True,
                    "store_count_subtask_threshold": 12
                },
                'meta': {
                    'async': True,
                    'countdown': 0
                }
            }
        ]

        options = {
            "start_tasks": True
        }

        self.mock.main_access.wfs.call_task_batch_new("retail_analytics", "analytics", "company_analytics_plan_b",
                                                      task_recs, self.context, options=options).AndReturn(mock_tasks)
        # replay all
        self.mox.ReplayAll()

        # run, baby!
        CompanyAnalyticsPlanBRunner._launch_plan_b_tasks(self.mock)

        self.assertEqual(self.mock.created_tasks, mock_tasks)

    def test_get_run_status_company_id_dict(self):
        self.maxDiff = None

        runner = CompanyAnalyticsPlanBRunner.__new__(CompanyAnalyticsPlanBRunner)

        cid1 = ObjectId()
        cid2 = ObjectId()
        cid3 = ObjectId()
        cid4 = ObjectId()

        run_id1 = str(uuid.uuid4())
        run_id2 = str(uuid.uuid4())
        run_id3 = str(uuid.uuid4())

        now = datetime.datetime.utcnow()
        now -= datetime.timedelta(microseconds=now.microsecond)
        ten_minutes = datetime.timedelta(minutes=10)
        ten_hours = datetime.timedelta(hours=10)

        runner.currently_running_companies = [
            [str(cid1), run_id1, "in_progress", now.strftime("%Y-%m-%dT%H:%M:%S")],
            [str(cid2), run_id1, "in_progress", now.strftime("%Y-%m-%dT%H:%M:%S")],
            [str(cid3), run_id2, "pending", (now - ten_minutes).strftime("%Y-%m-%dT%H:%M:%S")],
            [str(cid4), run_id3, "pending", (now - ten_hours).strftime("%Y-%m-%dT%H:%M:%S")]
        ]

        run_status_company_id_dict = {
            "pending": {
                run_id2: {
                    "creation_time": now - ten_minutes,
                    "company_ids": [cid3]
                },
                run_id3: {
                    "creation_time": now - ten_hours,
                    "company_ids": [cid4]
                }
            },
            "in_progress": {
                run_id1: {
                    "creation_time": now,
                    "company_ids": [cid1, cid2]
                }
            }
        }

        # run, baby!
        runner._get_run_status_company_id_dict()

        self.assertEqual(runner.run_status_company_id_dict, run_status_company_id_dict)

    def test_get_companies_in_need_of_plan_b(self):

        query = {
            "data.workflow.analytics.status": "needs_plan_b",
            "$or": [
                {
                    "data.type": "retail_banner"
                },
                {
                    "data.type": "retail_parent",
                    "links.company.retailer_branding.entity_role_to": "retail_segment"
                }
            ]
        }
        fields = ["_id"]
        sort = [["data.workflow.analytics.needs_plan_b_date", 1]]
        limit = 100

        params = self.mock.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                        limit=limit, sort=sort, as_list=True)["params"]

        mock_results = "mock_results"
        self.mock.main_access.mds.call_find_entities_raw("company", params, self.context).AndReturn(mock_results)

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = CompanyAnalyticsPlanBRunner._get_companies_in_need_of_plan_b(self.mock)

        self.assertEqual(results, mock_results)

    def test_get_company_families_to_run_to_run(self):

        num_tasks_to_create = 2

        pid1 = ObjectId()
        bid11 = ObjectId()
        bid12 = ObjectId()

        bid21 = ObjectId()

        mock_companies = [
            [bid11],
            [bid21]
        ]

        self.mox.StubOutWithMock(company_helper, "get_company_family")

        company_helper.get_company_family(bid11, self.context).AndReturn(([bid11, bid12], pid1))
        company_helper.get_company_family(bid21, self.context).AndReturn(([bid21], None))

        # replay all
        self.mox.ReplayAll()

        # run, baby!
        results = CompanyAnalyticsPlanBRunner._get_company_families_to_run(self.mock, num_tasks_to_create,
                                                                           mock_companies)

        self.assertListEqual(results, [
            [pid1, bid11, bid12],
            [bid21]
        ])

    def test_get_company_family_id(self):

        runner = CompanyAnalyticsPlanBRunner.__new__(CompanyAnalyticsPlanBRunner)

        cid = ObjectId()
        pid = ObjectId()

        mock_company = [
            cid,
            [
                {
                    "entity_role_from": "asdf",
                    "entity_role_to": "retail_parent",
                    "entity_id_to": "asdf"
                },
                {
                    "entity_role_from": "retail_segment",
                    "entity_role_to": "asdf",
                    "entity_id_to": "asdf"
                },
                {
                    "entity_role_from": "retail_segment",
                    "entity_role_to": "retail_parent",
                    "entity_id_to": pid
                }
            ]
        ]

        result = runner._get_company_family_id(mock_company)

        self.assertEqual(result, str(pid))

        mock_company = [
            cid,
            [
                {
                    "entity_role_from": "asdf",
                    "entity_role_to": "retail_parent",
                    "entity_id_to": "asdf"
                },
                {
                    "entity_role_from": "retail_segment",
                    "entity_role_to": "asdf",
                    "entity_id_to": "asdf"
                }
            ]
        ]

        result = runner._get_company_family_id(mock_company)

        self.assertEqual(result, str(cid))


if __name__ == "__main__":
    unittest.main()
