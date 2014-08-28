import datetime
import mox
from mox import IgnoreArg, IsA
from common.helpers import email_provider
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities import sql
from common.utilities.inversion_of_control import Dependency, dependencies
from common.web_helpers import logging_helper
from core.data_checks.config.config import email_settings
from core.service.svc_workflow.implementation.task.implementation.custom_analytics.custom_analytics_cleanup_job import CustomAnalyticsCleanupJob

__author__ = 'erezrubinstein'

class TestCustomAnalyticsCleanupJob(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCustomAnalyticsCleanupJob, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_retail_access = Dependency("RetailMongoAccess").value
        self.mock_logger = Dependency("FlaskLogger").value

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.task_rec = { "context": self.context }

        # create the scheduler
        self.cleanup_job = CustomAnalyticsCleanupJob(self.task_rec)


    def doCleanups(self):

        # call parent clean up
        super(TestCustomAnalyticsCleanupJob, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_complete_run__success(self):

        # begin mocking stuff
        self.mox.StubOutWithMock(self.cleanup_job, "_get_custom_analytics_jobs_to_clean_up")
        self.mox.StubOutWithMock(self.cleanup_job, "_back_up_target_db")
        self.mox.StubOutWithMock(self.cleanup_job, "_drop_target_and_logging_dbs")
        self.mox.StubOutWithMock(self.cleanup_job, "_mark_ca_run_as_cleaned_up")

        # begin recording
        self.cleanup_job._get_custom_analytics_jobs_to_clean_up().AndReturn(["chicken", "woot"])
        self.cleanup_job._back_up_target_db("chicken")
        self.cleanup_job._drop_target_and_logging_dbs("chicken")
        self.cleanup_job._mark_ca_run_as_cleaned_up("chicken")
        self.cleanup_job._back_up_target_db("woot")
        self.cleanup_job._drop_target_and_logging_dbs("woot")
        self.cleanup_job._mark_ca_run_as_cleaned_up("woot")

        # replay all
        self.mox.ReplayAll()

        # go!
        self.cleanup_job.run()


    def test_complete_run__exception(self):

        # define exception side effect method
        exception = Exception("yo mama")
        def raise_exception():
            raise exception

        # begin mocking stuff
        self.mox.StubOutWithMock(logging_helper, "log_exception")
        self.mox.StubOutWithMock(self.cleanup_job, "_get_custom_analytics_jobs_to_clean_up")
        self.mox.StubOutWithMock(self.cleanup_job, "_send_error_email")

        # begin recording
        self.cleanup_job._get_custom_analytics_jobs_to_clean_up().WithSideEffects(raise_exception)
        logging_helper.log_exception(self.mock_logger, "Error running CustomAnalyticsCleanupJob", exception, IgnoreArg())
        self.cleanup_job._send_error_email("yo mama", IsA(basestring))

        # replay all
        self.mox.ReplayAll()

        # go!
        self.assertRaises(Exception, self.cleanup_job.run)


    def test_send_error_email(self):

        # create mock ids
        mock_error = "I love goooooooold"

        # create expected email stuff
        mock_subject = "Error Running Custom Analytics Cleanup Job"
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
        self.cleanup_job._send_error_email(mock_error, "trace_stack")


    def test_get_custom_analytics_jobs_to_clean_up(self):

        # define some mocks and expected values
        expected_entity_fields = { "_id": 1, "target_db_name": 1, "logging_db_name": 1 }
        expected_query = {
            "$or": [
                { "database_deleted": { "$exists": False }},
                { "database_deleted": False }
            ],
            "target_db_name": { "$exists": True },
            "logging_db_name": { "$exists": True },
            "heart_beat" : { "$lt": datetime.datetime(2014, 2, 25) }
        }

        # begin stubbing
        self.mox.StubOutWithMock(self.cleanup_job, "_get_utc_now")

        # begin recording
        self.cleanup_job._get_utc_now().AndReturn(datetime.datetime(2014, 3, 25))
        self.mock_retail_access.find("custom_analytics_run", expected_query, expected_entity_fields).AndReturn(["woot"])

        # replay all
        self.mox.ReplayAll()

        # go
        self.assertEqual(self.cleanup_job._get_custom_analytics_jobs_to_clean_up(), ["woot"])


    def test_back_up_target_db(self):

        # create mocks
        mock_ca_run = { "target_db_name": "chicken_woot" }
        mock_sql_statement = """
        BACKUP DATABASE chicken_woot
        TO DISK = 'D:\SQLData\Backup\Custom Analytics\chicken_woot.bak'
            WITH FORMAT,
                COMPRESSION,
                MEDIANAME = 'D_SQLServerBackups',
                NAME = 'Full Backup of chicken_woot'
        """

        # begin stubbing
        self.mox.StubOutWithMock(sql, "sql_execute")

        # begin recording
        sql.sql_execute(mock_sql_statement, database_name = "chicken_woot")

        # replay all
        self.mox.ReplayAll()

        # go!
        self.cleanup_job._back_up_target_db(mock_ca_run)


    def test_drop_target_and_logging_dbs(self):

        # create mocks
        mock_ca_run = {
            "target_db_name": "chicken",
            "logging_db_name": "woot"
        }

        # begin stubbing
        self.mox.StubOutWithMock(sql, "sql_execute")

        # begin recording
        sql.sql_execute("alter database chicken set single_user with rollback immediate", database_name = "master")
        sql.sql_execute("alter database woot set single_user with rollback immediate", database_name = "master")
        sql.sql_execute("drop database chicken", database_name = "master")
        sql.sql_execute("drop database woot", database_name = "master")

        # replay all
        self.mox.ReplayAll()

        # go!
        self.cleanup_job._drop_target_and_logging_dbs(mock_ca_run)


    def test_mark_ca_run_as_cleaned_up(self):

        # create mocks and expected values
        mock_ca_run = { "_id": "Gold Member", "whatever": "whichever" }
        mock_query = { "_id": "Gold Member" }
        mock_operation = {
            "$set": {
                "database_deleted": True
            }
        }

        # begin recording
        self.mock_retail_access.update("custom_analytics_run", mock_query, mock_operation)

        # replay all
        self.mox.ReplayAll()

        # I love gooooold!
        self.cleanup_job._mark_ca_run_as_cleaned_up(mock_ca_run)
