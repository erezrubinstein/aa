import datetime
import json
import __builtin__
from fabric import operations
import mox
from mox import IgnoreArg, IsA
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.helpers.sysadmin_helper import get_host_name
from common.service_access import web_access
from common.utilities.inversion_of_control import Dependency, dependencies
from geoprocessing.build.geoprocessing_custom_analytics_executor import CustomAnalyticsExecutor
from geoprocessing.custom_analytics import run_custom_analytics_reports, run_custom_analytics_data_checks


__author__ = "erezrubinstein"

class TestCustomAnalyticsExecutor(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCustomAnalyticsExecutor, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get some mock dependencies
        self.mock_deployment_provider = Dependency("DeploymentProvider").value
        self.mock_cloud_provider = Dependency("CloudProviderNewEnvironment").value
        self.mock_logger = Dependency("LogManager").value
        self.mock_email_provider = Dependency("EmailProvider").value
        self.mock_config = Dependency("Config").value


    def doCleanups(self):

        # call parent clean up
        super(TestCustomAnalyticsExecutor, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_complete_run__success(self):

        # create executor
        executor = CustomAnalyticsExecutor()

        # stub out some stuff
        self.mox.StubOutWithMock(executor, "_update_path")
        self.mox.StubOutWithMock(executor, "_update_and_reset_config")
        self.mox.StubOutWithMock(executor, "_update_ca_run_status")
        self.mox.StubOutWithMock(executor, "_clear_log_file")
        self.mox.StubOutWithMock(executor, "_execute_controller")
        self.mox.StubOutWithMock(executor, "_run_data_checks")
        self.mox.StubOutWithMock(executor, "_run_custom_analytics")
        self.mox.StubOutWithMock(executor, "_upload_file_to_rds")
        self.mox.StubOutWithMock(executor, "_shrink_db")
        self.mox.StubOutWithMock(executor, "_send_success_email")
        self.mox.StubOutWithMock(executor, "_shut_down_worker_server")

        # begin recording
        executor._update_path()
        executor._update_and_reset_config().AndReturn(("fuzzy", "wuzzy-stripped", "was", "a", "bear", "chicken", "woot", "borat", "sagdiev"))
        executor._update_ca_run_status()
        executor._clear_log_file()
        executor._execute_controller()
        executor._run_data_checks("fuzzy", "wuzzy-stripped", "was", "a", "bear").AndReturn(True)
        executor._run_custom_analytics("chicken", "woot", "wuzzy stripped", "borat", "sagdiev")
        executor._upload_file_to_rds("fuzzy", "wuzzy stripped").AndReturn("PATH")
        executor._shrink_db("was")
        executor._update_ca_run_status("success", "success", "PATH", True)
        executor._send_success_email("fuzzy")
        executor._shut_down_worker_server()

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        executor.execute()

        # make sure the ca id set for the heart beat
        self.assertEqual(executor._custom_analytics_run_id, "fuzzy")


    def test_complete_run__success__data_checks_fail(self):

        # create executor
        executor = CustomAnalyticsExecutor()

        # stub out some stuff
        self.mox.StubOutWithMock(executor, "_update_path")
        self.mox.StubOutWithMock(executor, "_update_and_reset_config")
        self.mox.StubOutWithMock(executor, "_update_ca_run_status")
        self.mox.StubOutWithMock(executor, "_clear_log_file")
        self.mox.StubOutWithMock(executor, "_execute_controller")
        self.mox.StubOutWithMock(executor, "_run_data_checks")
        self.mox.StubOutWithMock(executor, "_run_custom_analytics")
        self.mox.StubOutWithMock(executor, "_upload_file_to_rds")
        self.mox.StubOutWithMock(executor, "_shrink_db")
        self.mox.StubOutWithMock(executor, "_send_success_email")
        self.mox.StubOutWithMock(executor, "_shut_down_worker_server")

        # begin recording
        executor._update_path()
        executor._update_and_reset_config().AndReturn(("fuzzy", "wuzzy", "was", "a", "bear", "chicken", "woot", "borat", "sagdiev"))
        executor._update_ca_run_status()
        executor._clear_log_file()
        executor._execute_controller()
        executor._run_data_checks("fuzzy", "wuzzy", "was", "a", "bear").AndReturn(False)
        executor._update_ca_run_status("data_checks_failed")
        executor._shut_down_worker_server()

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        executor.execute()

        # make sure the ca id set for the heart beat
        self.assertEqual(executor._custom_analytics_run_id, "fuzzy")


    def test_complete_run__early_error(self):

        # create executor
        executor = CustomAnalyticsExecutor()

        # create error and error method
        def raise_exception():
            raise Exception("yo mama")

        # stub out first method
        self.mox.StubOutWithMock(executor, "_update_path")
        self.mox.StubOutWithMock(executor, "_handle_error")
        self.mox.StubOutWithMock(executor, "_update_and_reset_config")
        self.mox.StubOutWithMock(executor, "_update_ca_run_status")
        self.mox.StubOutWithMock(executor, "_clear_log_file")
        self.mox.StubOutWithMock(executor, "_execute_controller")
        self.mox.StubOutWithMock(executor, "_run_data_checks")
        self.mox.StubOutWithMock(executor, "_run_custom_analytics")
        self.mox.StubOutWithMock(executor, "_upload_file_to_rds")
        self.mox.StubOutWithMock(executor, "_shrink_db")
        self.mox.StubOutWithMock(executor, "_send_success_email")
        self.mox.StubOutWithMock(executor, "_shut_down_worker_server")

        # begin recording
        executor._update_path().WithSideEffects(raise_exception)
        executor._handle_error("yo mama", IsA(basestring), "not set yet", "not set yet", "not set yet", "not set yet", "not set yet")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        executor.execute()


    def test_complete_run__late_error(self):

        # create executor
        executor = CustomAnalyticsExecutor()

        # create error and error method
        def raise_exception():
            raise Exception("yo mama")

        # stub out first method
        self.mox.StubOutWithMock(executor, "_update_path")
        self.mox.StubOutWithMock(executor, "_handle_error")
        self.mox.StubOutWithMock(executor, "_update_and_reset_config")
        self.mox.StubOutWithMock(executor, "_update_ca_run_status")
        self.mox.StubOutWithMock(executor, "_clear_log_file")
        self.mox.StubOutWithMock(executor, "_execute_controller")
        self.mox.StubOutWithMock(executor, "_run_data_checks")
        self.mox.StubOutWithMock(executor, "_run_custom_analytics")
        self.mox.StubOutWithMock(executor, "_upload_file_to_rds")
        self.mox.StubOutWithMock(executor, "_shrink_db")
        self.mox.StubOutWithMock(executor, "_send_success_email")
        self.mox.StubOutWithMock(executor, "_shut_down_worker_server")

        # begin recording (raise exception on geoprocessing controller)
        executor._update_path()
        executor._update_and_reset_config().AndReturn(("fuzzy", "wuzzy", "was", "a", "bear", "chicken", "woot", "borat", "sagdiev"))
        executor._update_ca_run_status()
        executor._clear_log_file()
        executor._execute_controller().WithSideEffects(raise_exception)
        executor._handle_error("yo mama", IsA(basestring), "fuzzy", "wuzzy", "was", "a", "bear")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        executor.execute()

        # make sure the ca id set for the heart beat
        self.assertEqual(executor._custom_analytics_run_id, "fuzzy")


    def test_update_path(self):

        # begin recording
        self.mock_deployment_provider.update_environmental_setting("PYTHONPATH", "/signal/python/geoprocessing")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        CustomAnalyticsExecutor()._update_path()


    def test_clear_log_file(self):

        # begin recording
        self.mock_deployment_provider.clear_log_file("/signal/python/geoprocessing", "log.txt")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        CustomAnalyticsExecutor()._clear_log_file()


    def test_execute_controller(self):

        # begin recording
        self.mock_deployment_provider.execute_controller("/signal/python/geoprocessing")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        CustomAnalyticsExecutor()._execute_controller()


    def test_run_data_checks(self):

        # stub out some stuff
        self.mox.StubOutClassWithMocks(run_custom_analytics_data_checks, "CustomAnalyticsDataCheckRunner")

        # begin recording
        mock_runner = run_custom_analytics_data_checks.CustomAnalyticsDataCheckRunner("fuzzy", "wuzzy", "was", "a", "bear", self.mock_logger)
        mock_runner.run_checks().AndReturn("chicken_woot")

        # replay all
        self.mox.ReplayAll()

        # go!
        self.assertEqual(CustomAnalyticsExecutor()._run_data_checks("fuzzy", "wuzzy", "was", "a", "bear"), "chicken_woot")


    def test_run_custom_analytics__no_comp_stores(self):

        # create fake time periods, company_settings
        mock_company_settings = "woot"
        mock_time_periods = [
            {
                "label": "t0",
                "date": "1900-01-01 00:00:00"
            },
            {
                "label": "t1",
                "date": "1900-02-01 00:00:00"
            }
        ]

        # expected time_periods
        expected_time_periods = [
            {
                "label": "t0",
                "date": datetime.datetime(1900, 1, 1)
            },
            {
                "label": "t1",
                "date": datetime.datetime(1900, 2, 1)
            }
        ]

        # begin stubbing
        self.mox.StubOutClassWithMocks(run_custom_analytics_reports, "CustomAnalyticsReportRunner")

        # begin recording
        mock_runner = run_custom_analytics_reports.CustomAnalyticsReportRunner(["base_reports"], expected_time_periods, "woot",
                                                                               "/signal/python/geoprocessing/custom_analytics/exports/",
                                                                               self.mock_logger, "stripped name", "blah")
        mock_runner.run_reports()
        mock_runner.export_report_to_excel()
        mock_runner.zip_up_reports()

        # replay all
        self.mox.ReplayAll()

        # go!
        CustomAnalyticsExecutor()._run_custom_analytics(mock_company_settings, mock_time_periods, "stripped name", False, "blah")


    def test_run_custom_analytics__with_comp_stores(self):

        # create fake time periods, company_settings
        mock_company_settings = "woot"
        mock_time_periods = [
            {
                "label": "t0",
                "date": "1900-01-01 00:00:00"
            },
            {
                "label": "t1",
                "date": "1900-02-01 00:00:00"
            }
        ]

        # expected time_periods
        expected_time_periods = [
            {
                "label": "t0",
                "date": datetime.datetime(1900, 1, 1)
            },
            {
                "label": "t1",
                "date": datetime.datetime(1900, 2, 1)
            }
        ]

        # begin stubbing
        self.mox.StubOutClassWithMocks(run_custom_analytics_reports, "CustomAnalyticsReportRunner")

        # begin recording
        mock_runner = run_custom_analytics_reports.CustomAnalyticsReportRunner(["base_reports", "comp_stores"], expected_time_periods, "woot",
                                                                               "/signal/python/geoprocessing/custom_analytics/exports/",
                                                                               self.mock_logger, "stripped name", "blah")
        mock_runner.run_reports()
        mock_runner.export_report_to_excel()
        mock_runner.zip_up_reports()

        # replay all
        self.mox.ReplayAll()

        # go!
        CustomAnalyticsExecutor()._run_custom_analytics(mock_company_settings, mock_time_periods, "stripped name", True, "blah")



    def test_upload_file_to_rds__success(self):

        # put mock values into config
        self.mock_config.custom_analytics_core_url = "chicken_woot"
        self.mock_config.custom_analytics_core_login = "chilly"
        self.mock_config.custom_analytics_core_password = "willy"

        # define expected data
        expected_login_params = { "email": "chilly", "password": "willy" }
        expected_form_data = {
            "fileName": "Custom Analytics Reports - test report.zip",
            "contentType": "application/zip",
            "fileType": "custom_analytics_reports"
        }
        expected_core_upload_url = "/api/files/custom_analytics/fried_chicken"

        # define some mock objects to return
        mock_login_response = self.mox.CreateMockAnything()
        mock_login_response.cookies = "MortyDog"
        mock_file_open = self.mox.CreateMockAnything()
        mock_upload_response = self.mox.CreateMockAnything()
        mock_upload_response_dict = { "message": "Great Success", "path": "PATH" }

        # begin stubbing
        self.mox.StubOutClassWithMocks(web_access, "CoreWebAccess")
        self.mox.StubOutWithMock(__builtin__, "open")

        # begin recording
        mock_core_access = web_access.CoreWebAccess("chicken_woot")
        mock_core_access.post("/login", expected_login_params, verify=False).AndReturn(mock_login_response)
        open("/signal/python/geoprocessing/custom_analytics/exports/Custom Analytics Reports.zip", "r").AndReturn(mock_file_open)
        mock_file_open.__enter__().AndReturn(mock_file_open)
        mock_core_access.post(expected_core_upload_url, expected_form_data, files={ "file": mock_file_open }, cookies="MortyDog", verify=False, time_out = 9999).AndReturn(mock_upload_response)
        mock_upload_response.json().AndReturn(mock_upload_response_dict)
        mock_file_open.__exit__(IgnoreArg(), IgnoreArg(), IgnoreArg())

        # replay all
        self.mox.ReplayAll()

        # go!
        self.assertEqual(CustomAnalyticsExecutor()._upload_file_to_rds("fried_chicken", "test report"), "PATH")


    def test_upload_file_to_rds__error(self):

        # put mock values into config
        self.mock_config.custom_analytics_core_url = "chicken_woot"
        self.mock_config.custom_analytics_core_login = "chilly"
        self.mock_config.custom_analytics_core_password = "willy"

        # define expected data
        expected_login_params = { "email": "chilly", "password": "willy" }
        expected_form_data = {
            "fileName": "Custom Analytics Reports - stripped name.zip",
            "contentType": "application/zip",
            "fileType": "custom_analytics_reports"
        }
        expected_core_upload_url = "/api/files/custom_analytics/fried_chicken"

        # define some mock objects to return
        mock_login_response = self.mox.CreateMockAnything()
        mock_login_response.cookies = "MortyDog"
        mock_file_open = self.mox.CreateMockAnything()
        mock_upload_response = self.mox.CreateMockAnything()
        mock_upload_response_dict = { "message": "scheisse" }

        # begin stubbing
        self.mox.StubOutClassWithMocks(web_access, "CoreWebAccess")
        self.mox.StubOutWithMock(__builtin__, "open")

        # begin recording
        mock_core_access = web_access.CoreWebAccess("chicken_woot")
        mock_core_access.post("/login", expected_login_params, verify=False).AndReturn(mock_login_response)
        open("/signal/python/geoprocessing/custom_analytics/exports/Custom Analytics Reports.zip", "r").AndReturn(mock_file_open)
        mock_file_open.__enter__().AndReturn(mock_file_open)
        mock_core_access.post(expected_core_upload_url, expected_form_data, files={ "file": mock_file_open }, cookies="MortyDog", verify=False, time_out = 9999).AndReturn(mock_upload_response)
        mock_upload_response.json().AndReturn(mock_upload_response_dict)
        mock_file_open.__exit__(IgnoreArg(), IgnoreArg(), IgnoreArg())

        # replay all
        self.mox.ReplayAll()

        # go!
        with self.assertRaises(Exception):
            CustomAnalyticsExecutor()._upload_file_to_rds("fried_chicken", "stripped name")


    def test_send_success_email(self):

        # put mock values into config
        self.mock_config.custom_analytics_retail_url = "chicken_woot"
        self.mock_config.custom_analytics_retail_login = "chilly"
        self.mock_config.custom_analytics_retail_password = "willy"

        # define expected data
        expected_login_params = { "email": "chilly", "password": "willy" }
        expected_email_url = "/api/custom_analytics/send_success_email/korean_fried_chicken"

        # define some mock objects to return
        mock_login_response = self.mox.CreateMockAnything()
        mock_login_response.cookies = "MortyDog"

        # begin stubbing
        self.mox.StubOutClassWithMocks(web_access, "CoreWebAccess")

        # begin recording
        mock_retail_access = web_access.CoreWebAccess("chicken_woot")
        mock_retail_access.post("/login", expected_login_params).AndReturn(mock_login_response)
        mock_retail_access.get(expected_email_url, cookies="MortyDog")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        CustomAnalyticsExecutor()._send_success_email("korean_fried_chicken")


    def test_shut_down_worker_server(self):

        # begin stubbing
        self.mox.StubOutWithMock(operations, "local")

        # begin recording
        operations.local("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id", True).AndReturn("chicken_woot")
        self.mock_cloud_provider.stop_ec2_instance("chicken_woot")

        # replay all
        self.mox.ReplayAll()

        # go
        CustomAnalyticsExecutor()._shut_down_worker_server()


    def test_handle_error(self):

        # create some mock values
        mock_start_date = datetime.datetime(2014, 3, 11, 0, 0, 0)
        mock_end_date = datetime.datetime(2014, 3, 11, 0, 0, 45)
        mock_subject = "Error running geoprocessing"
        mock_body = '\n'.join([
            "Source: Custom Analytics Executor"
            "Worker Machine: %s" % get_host_name(),
            "Build Start Time (UTC): %s" % str(mock_start_date),
            "Build End Time (UTC): %s" % str(mock_end_date),
            "Elapsed Time: 45.000000",
            "",
            "Client Name: a",
            "Client Email: bear",
            "Report Name: wuzzy",
            "Target Database Name: was",
            "CA Run ID: fuzzy",
            "",
            "Exception: woot",
            "Stack Trace: chicken"
        ])

        # mock some config values
        self.mock_config.email_settings_from_email = "chicken"
        self.mock_config.report_generator_email_recipients_developers = "woot"

        # stub out date time, which is used when creating the executor
        self.mox.StubOutWithMock(datetime, "datetime")

        # record the first datetime
        datetime.datetime.utcnow().AndReturn(mock_start_date)

        # replay all (early) to make sure the executor gets the right start date
        self.mox.ReplayAll()

        # create the executor
        executor = CustomAnalyticsExecutor()

        # reset the recordings so that we can rerecord the actual method execution
        self.mox.ResetAll()

        # begin stubbing
        self.mox.StubOutWithMock(executor, "_update_ca_run_status")

        # begin recording
        executor._update_ca_run_status("error", error_string = "woot", error_stack_trace = "chicken")
        datetime.datetime.utcnow().AndReturn(mock_end_date)
        self.mock_email_provider.send_email("chicken", "woot", mock_subject, mock_body)

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        executor._handle_error("woot", "chicken", "fuzzy", "wuzzy", "was", "a", "bear")


    def test_update_and_reset_config__set_values(self):

        # create mock configuration
        mock_configuration = json.dumps({
            "ca_run_id": "chicken",
            "demographic_template": "woot",
            "trade_areas": "chilly",
            "target_db": "willy",
            "target_db_logging": "mdog",
            "report_name": "arnie",
            "client_name": "arnold",
            "client_email": "arnold@arnie.com",
            "company_settings": "Morty",
            "time_periods": "Dog",
            "run_comp_stores_report": "borat",
            "comp_stores_periods": "sagdiev"
        })

        # begin recording
        self.mock_config.update_config_with_custom_analytics_settings("chicken", "woot", "chilly", "willy", "mdog", "arnie", "arnold", "arnold@arnie.com",
                                                                      "Morty", "Dog", "borat", "sagdiev").AndReturn("yo mama")

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        executor = CustomAnalyticsExecutor(mock_configuration)
        results = executor._update_and_reset_config()

        # make sure results are good
        self.assertEqual(results, ("chicken", "arnie", "willy", "arnold", "arnold@arnie.com", "Morty", "Dog", "borat", "sagdiev"))
        self.assertEqual(executor._config, "yo mama")


    def test_update_and_reset_config__do_not_set_values(self):

        # set some settings in the mock_config
        self.mock_config.custom_analytics_run_id = "chicken"
        self.mock_config.custom_analytics_report_name = "arnie"
        self.mock_config.db_database = "willy"
        self.mock_config.custom_analytics_client_name = "arnold"
        self.mock_config.custom_analytics_client_email = "arnold@arnie.com"
        self.mock_config.custom_analytics_company_settings = "Morty"
        self.mock_config.custom_analytics_time_periods = "Dog"
        self.mock_config.custom_analytics_run_comp_stores_report = "borat"
        self.mock_config.custom_analytics_comp_stores_periods = "sagdiev"

        # I love gooooooold
        results = CustomAnalyticsExecutor()._update_and_reset_config()

        # make sure results are good
        self.assertEqual(results, ("chicken", "arnie", "willy", "arnold", "arnold@arnie.com", "Morty", "Dog", "borat", "sagdiev"))