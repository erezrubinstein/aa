import datetime
import mox
from mox import IgnoreArg, IsA
from common.helpers import email_provider
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from common.web_helpers import logging_helper
from core.data_checks.config.config import email_settings
from core.service.svc_workflow.implementation.task.implementation.custom_analytics.custom_analytics_scheduler import CustomAnalyticsScheduler

__author__ = 'erezrubinstein'

class TestCustomAnalyticsScheduler(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCustomAnalyticsScheduler, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_retail_access = Dependency("RetailMongoAccess").value
        self.mock_logger = Dependency("FlaskLogger").value
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.task_rec = { "context": self.context }

        # create the scheduler
        self.scheduler = CustomAnalyticsScheduler(self.task_rec)


    def doCleanups(self):

        # call parent clean up
        super(TestCustomAnalyticsScheduler, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_run__success__next_runs_plus_stuck(self):

        # begin stubbing
        self.mox.StubOutWithMock(self.scheduler, "_get_in_progress")
        self.mox.StubOutWithMock(self.scheduler, "_get_next_ca_run_ids")
        self.mox.StubOutWithMock(self.scheduler, "_update_statuses")
        self.mox.StubOutWithMock(self.scheduler, "_start_next_runs")
        self.mox.StubOutWithMock(self.scheduler, "_send_stuck_tasks_warning_email")

        # begin recording
        self.scheduler._get_in_progress().AndReturn((["woot"], ["chicken_woot"]))
        self.scheduler._get_next_ca_run_ids(2).AndReturn("chilly")
        self.scheduler._update_statuses("chilly")
        self.scheduler._start_next_runs("chilly")
        self.scheduler._update_statuses(["chicken_woot"], "queued", "queued")
        self.scheduler._send_stuck_tasks_warning_email(["chicken_woot"])

        # replay all
        self.mox.ReplayAll()

        # respect!
        self.scheduler.run()


    def test_run__success__no_room_to_run(self):

        # begin stubbing
        self.mox.StubOutWithMock(self.scheduler, "_get_in_progress")
        self.mox.StubOutWithMock(self.scheduler, "_get_next_ca_run_ids")
        self.mox.StubOutWithMock(self.scheduler, "_update_statuses")
        self.mox.StubOutWithMock(self.scheduler, "_start_next_runs")
        self.mox.StubOutWithMock(self.scheduler, "_send_stuck_tasks_warning_email")

        # begin recording
        self.scheduler._get_in_progress().AndReturn((["woot", "chilly", "willy"], []))

        # replay all
        self.mox.ReplayAll()

        # respect!
        self.scheduler.run()


    def test_run__exception(self):

        # define exception side effect method
        exception = Exception("yo mama")
        def raise_exception():
            raise exception

        # begin stubbing
        self.mox.StubOutWithMock(self.scheduler, "_get_in_progress")
        self.mox.StubOutWithMock(logging_helper, "log_exception")
        self.mox.StubOutWithMock(self.scheduler, "_send_error_email")

        # begin recording
        self.scheduler._get_in_progress().WithSideEffects(raise_exception)
        logging_helper.log_exception(self.mock_logger, "Error running CustomAnalyticsScheduler", exception, IgnoreArg())
        self.scheduler._send_error_email("yo mama", IsA(basestring))

        # replay all
        self.mox.ReplayAll()

        # respect!
        with self.assertRaises(Exception):
            self.scheduler.run()


    def test_get_in_progress(self):

        # create mock values
        mock_date_now = datetime.datetime(2014, 3, 17, 18, 30)

        # create expected values
        mock_date_expected = datetime.datetime(2014, 3, 17, 18, 20)
        expected_in_progress_query = { "internal_status": "in_progress", "heart_beat": { "$gt": mock_date_expected }}
        expected_in_progress_but_stuck_query = { "internal_status": "in_progress", "heart_beat": { "$lte": mock_date_expected }}
        expected_projection = { "_id": 1 }

        # begin stubbing things
        self.mox.StubOutWithMock(self.scheduler, "_get_utc_now")

        # begin recording
        self.scheduler._get_utc_now().AndReturn(mock_date_now)
        self.mock_retail_access.find("custom_analytics_run", expected_in_progress_query, expected_projection).AndReturn([{ "_id": "chicken" }])
        self.mock_retail_access.find("custom_analytics_run", expected_in_progress_but_stuck_query, expected_projection).AndReturn([{ "_id": "woot" }])

        # replay all
        self.mox.ReplayAll()

        # go!
        self.assertEqual(self.scheduler._get_in_progress(), (["chicken"], ["woot"]))


    def test_get_next_ca_run_ids(self):

        # define some mocks
        mock_cursor = self.mox.CreateMockAnything()
        mock_results = [
            { "_id": "chicken" },
            { "_id": "woot" }
        ]

        # begin recording
        self.mock_retail_access.find("custom_analytics_run", { "status": "queued" }, { "_id": 1 }).AndReturn(mock_cursor)
        mock_cursor.sort([["created_at", 1]]).AndReturn(mock_cursor)
        mock_cursor.limit(2).AndReturn(mock_results)

        # replay all
        self.mox.ReplayAll()

        # respect!
        self.assertEqual(self.scheduler._get_next_ca_run_ids(2), ["chicken", "woot"])


    def test_update_statuses(self):

        # create mocks
        mock_date_now = datetime.datetime.utcnow()
        mock_ca_run_ids = ["chilly", "willy"]
        mock_query = {
            "_id": {
                "$in": mock_ca_run_ids
            }
        }
        mock_operations = {
            "$set": {
                "status": "in_progress",
                "internal_status": "in_progress",
                "heart_beat": mock_date_now
            }
        }

        # begin stubbing
        self.mox.StubOutWithMock(datetime, "datetime")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_date_now)
        self.mock_retail_access.update("custom_analytics_run", mock_query, mock_operations, multi = True)

        # replay all
        self.mox.ReplayAll()

        # Judo chop!
        self.scheduler._update_statuses(mock_ca_run_ids)


    def test_update_statuses__empty(self):

        # make sure that there are no errors/web_calls if there's nothing to run
        self.scheduler._update_statuses([])


    def test_start_next_runs(self):

        # create some mocks
        mock_next_run_ids = ["chilly", "willy"]
        expected_task_recs = [
            {
                "input": {
                    "custom_analytics_run_id": "chilly",
                },
                "meta": {
                    "async": True
                }
            },
            {
                "input": {
                    "custom_analytics_run_id": "willy",
                },
                "meta": {
                    "async": True
                }
            }
        ]

        # begin recording
        self.mock_main_access.wfs.call_task_batch_new('custom_analytics', 'custom_analytics', "custom_analytics_runner", expected_task_recs, self.context)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.scheduler._start_next_runs(mock_next_run_ids)


    def test_start_next_runs__empty(self):

        # make sure that there are no errors/web_calls if there's nothing to run
        self.scheduler._start_next_runs([])


    def test_send_stuck_tasks_warning_email(self):

        # create mock ids
        mock_run_ids = ["David", "Hasselhoff", "Cheeseburger"]

        # create expected email stuff
        mock_subject = "Custom Analytics Stuck Tasks Warning"
        mock_body = 'The following custom analytics runs were "stuck" and have been re-queued:\n  - David\n  - Hasselhoff\n  - Cheeseburger'
        mock_from_email = "support@signaldataco.com"
        mock_to_email = ["engineering@signaldataco.com"]

        # replace email settings with mocks/stubs
        email_settings["smtp_server"] = "chicken"
        email_settings["username"] = "woot"
        email_settings["password"] = "Austin-Danger"

        # begin stubbing
        self.mox.StubOutClassWithMocks(email_provider, "EmailProvider")

        # begin recording
        mock_email_provider = email_provider.EmailProvider("chicken", "woot", "Austin-Danger")
        mock_email_provider.send_email(mock_from_email, mock_to_email, mock_subject, mock_body)

        # replay all
        self.mox.ReplayAll()

        # I love gooooold!
        self.scheduler._send_stuck_tasks_warning_email(mock_run_ids)


    def test_send_error_email(self):

        # create mock ids
        mock_error = "I love goooooooold"

        # create expected email stuff
        mock_subject = "Error Running Custom Analytics Scheduler"
        mock_body = "Error: I love goooooooold\nTrace Stack: trace_stack"
        mock_from_email = "support@signaldataco.com"
        mock_to_email = ["engineering@signaldataco.com"]

        # replace email settings with mocks/stubs
        email_settings["smtp_server"] = "chicken"
        email_settings["username"] = "woot"
        email_settings["password"] = "Austin-Danger"

        # begin stubbing
        self.mox.StubOutClassWithMocks(email_provider, "EmailProvider")

        # begin recording
        mock_email_provider = email_provider.EmailProvider("chicken", "woot", "Austin-Danger")
        mock_email_provider.send_email(mock_from_email, mock_to_email, mock_subject, mock_body)

        # replay all
        self.mox.ReplayAll()

        # I love gooooold!
        self.scheduler._send_error_email(mock_error, "trace_stack")