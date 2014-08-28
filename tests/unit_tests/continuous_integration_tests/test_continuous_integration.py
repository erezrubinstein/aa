from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from continuous_integration.run_continuous_integration import ContinuousIntegration
from core.service.svc_entity_matcher import entity_matcher_api
from core.service.svc_analytics import analytics_api
from core.service.svc_main import main_api
from core.service.svc_master_data_storage import mds_api
from core.service.svc_raw_data_storage import rds_api
from core.service.svc_workflow import workflow_api
from core.web.run_core_web import app as web_app
from retail.v010.retail_app_runner import app as retail_web_app
import unittest


__author__ = 'horacethomas'


class TestContinuousIntegration(unittest.TestCase):
    def setUp(self):
        # register dependencies
        register_common_mock_dependencies()

        # get deployment provider
        self.deployment_provider = Dependency("DeploymentProvider").value
        self.ci_provider = Dependency("ContinuousIntegrationProvider").value
        self.rest_provider = Dependency("RestProvider").value
        self.email_provider = Dependency("EmailProvider").value

        #create ci object
        self.ci = ContinuousIntegration()

        # make sure ci does not sleep long during tests...
        self.ci._sleep_time = 0.0001
        self._replaced_files = 12
        self._server_count = 11 # number of servers/processes
        self._db_count = 8 # number of databases


    def tearDown(self):
        dependencies.clear()

    def test_initialize(self):
        """
        Verify that the __init__ initializes our class variables correctly
        """
        # verify default environment
        self.assertEqual(self.ci._environment, "CONTINUOUS INTEGRATION")

        # verify testing folders
        self.assertEqual(self.ci._unit_tests_folder, self.ci._source_root + "/tests/unit_tests/")
        self.assertEqual(self.ci._integration_tests_folder, self.ci._source_root + "/tests/integration_tests/")

        # verify geoprocessing configs
        self.assertEqual(self.ci._geo_config_cloud_old, '/'.join([self.ci._source_root, "geoprocessing/config.yml"]))
        self.assertEqual(self.ci._geo_config_cloud_new, '/'.join([self.ci._source_root, "geoprocessing/config.cloud.continuous_integration.yml"]))

        # verify empty process list
        self.assertEqual(self.ci._processes, [])

        # verify service methods (i.e. all servers)
        self.assertEqual(set(self.ci._service_start_methods), { rds_api.run_api, workflow_api.run_api, mds_api.run_api,
                                                                entity_matcher_api.run_api, main_api.run_api, web_app.run_app,
                                                                retail_web_app.run_app, analytics_api.run_api })
        self.assertEqual(set(self.ci._servers_to_initialize_db),
                         {'http://localhost:15201', 'http://localhost:15202',
                          'http://localhost:15203', 'http://localhost:15205', 'http://localhost:15211',
                          'http://localhost:15213','http://localhost:15215', 'http://localhost:15207'})

        # verify we're emailing engineering
        self.assertIn('engineering@signaldataco.com', self.ci._to_email)

        # make sure error flag is initialized to 0
        self.assertEqual(self.ci._error, 0)


    def test_replace_configuration_files(self):
        # call function
        self.ci._replace_configuration_files()

        # make sure all configs were replaced
        self.assertEqual(len(self.deployment_provider.old_config_files), self._replaced_files)
        self.assertEqual(len(self.deployment_provider.new_config_files), self._replaced_files)

        # verify that all the configs were replaced correctly
        self.assertEqual(self.deployment_provider.old_config_files[0], '/'.join([self.ci._source_root, "geoprocessing/config.yml"]))
        self.assertEqual(self.deployment_provider.new_config_files[0], '/'.join([self.ci._source_root, "geoprocessing/config.cloud.continuous_integration.yml"]))
        self.assertEqual(self.deployment_provider.old_config_files[1], '/'.join([self.ci._source_root, "core/service/svc_main/config/main_config_integration_test.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[1], '/'.join([self.ci._source_root, "core/service/svc_main/config/main_config_continuous_integration.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[2], '/'.join([self.ci._source_root, "core/service/svc_entity_matcher/config/entity_matcher_config_integration_test.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[2], '/'.join([self.ci._source_root, "core/service/svc_entity_matcher/config/entity_matcher_config_continuous_integration.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[3], '/'.join([self.ci._source_root, "core/service/svc_master_data_storage/config/mds_config_integration_test.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[3], '/'.join([self.ci._source_root, "core/service/svc_master_data_storage/config/mds_config_continuous_integration.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[4], '/'.join([self.ci._source_root, "core/service/svc_raw_data_storage/config/rds_config_integration_test.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[4], '/'.join([self.ci._source_root, "core/service/svc_raw_data_storage/config/rds_config_continuous_integration.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[5], '/'.join([self.ci._source_root, "core/service/svc_workflow/config/workflow_config_integration_test.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[5], '/'.join([self.ci._source_root, "core/service/svc_workflow/config/workflow_config_continuous_integration.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[6], '/'.join([self.ci._source_root, "core/web/config/config_integration_test.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[6], '/'.join([self.ci._source_root, "core/web/config/config_continuous_integration.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[7], '/'.join([self.ci._source_root, "core/build/db/load_helper.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[7], '/'.join([self.ci._source_root, "core/build/db/load_helper_continuous_integration.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[8], '/'.join([self.ci._source_root, "core/service/svc_master_data_storage/config/mds_config_integration_test_with_validations.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[8], '/'.join([self.ci._source_root, "core/service/svc_master_data_storage/config/mds_config_continuous_integration_with_validations.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[9], '/'.join([self.ci._source_root, "core/service/svc_main/config/main_config_integration_test_with_validations.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[9], '/'.join([self.ci._source_root, "core/service/svc_main/config/main_config_continuous_integration_with_validations.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[10], '/'.join([self.ci._source_root, "retail/v010/config/config_integration_test.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[10], '/'.join([self.ci._source_root, "retail/v010/config/config_continuous_integration.py"]))
        self.assertEqual(self.deployment_provider.old_config_files[11], '/'.join([self.ci._source_root, "core/service/svc_analytics/config/analytics_config_integration_test.py"]))
        self.assertEqual(self.deployment_provider.new_config_files[11], '/'.join([self.ci._source_root, "core/service/svc_analytics/config/analytics_config_continuous_integration.py"]))

    def test_start_ci_core_servers(self):
        self.ci._start_ci_core_servers()

        service_start_methods = [(rds_api.run_api, "CONTINUOUS INTEGRATION"),
                                 (workflow_api.run_api, "CONTINUOUS INTEGRATION"),
                                 (mds_api.run_api, "CONTINUOUS INTEGRATION"),
                                 (entity_matcher_api.run_api, "CONTINUOUS INTEGRATION"),
                                 (main_api.run_api, "CONTINUOUS INTEGRATION"),
                                 (web_app.run_app, "CONTINUOUS INTEGRATION"),
                                 (retail_web_app.run_app, "CONTINUOUS INTEGRATION"),
                                 (analytics_api.run_api, "CONTINUOUS INTEGRATION"),
                                 (mds_api.run_api, "CONTINUOUS INTEGRATION WITH VALIDATION"),
                                 (main_api.run_api, "CONTINUOUS INTEGRATION WITH VALIDATION"),
                                 (workflow_api.run_api, "CONTINUOUS INTEGRATION WITH VALIDATION")]

        # verify all servers started
        self.assertEqual(len(self.ci_provider.servers_started), self._server_count)

        # verify all servers started are correct
        self.assertEqual(set(self.ci_provider.servers_started), set(service_start_methods))

        # verify that the ci remembered the six servers
        self.assertEqual(len(self.ci._processes), self._server_count)


    def test_initialize_databases__successful_delete(self):
        # call method
        self.ci._initialize_databases()

        # verify that "delete db" was called for each url
        self.assertEqual(len(self.rest_provider.actions_called), self._db_count)
        for index in range(0, self._db_count):
            self.assertEqual(self.rest_provider.actions_called[index]["action"], "delete")
            self.assertEqual(self.rest_provider.actions_called[index]["url"], self.ci._servers_to_initialize_db[index] + "/db")
            self.assertEqual(self.rest_provider.actions_called[index]["request"], None)


    def test_initialize_databases__error_deleting(self):
        # mock the rest provider to raise an exception
        self.rest_provider.returns_error = True

        # call method
        self.assertRaises(Exception, self.ci._initialize_databases)


    def test_run_tests__successful_run(self):
        # mock successful results
        self.ci_provider.test_results = (0, "Great Success!!!!")

        # run the tests
        self.ci._run_tests()

        # verify that unit tests and integration tests were both run
        self.assertEqual(len(self.ci_provider.tests_source_dirs), 2)
        self.assertEqual(len(self.ci_provider.tests), 2)
        self.assertEqual(self.ci_provider.tests_source_dirs[0], self.ci._source_root)
        self.assertEqual(self.ci_provider.tests[0], self.ci._source_root + "/tests/unit_tests/")
        self.assertEqual(self.ci_provider.tests_source_dirs[1], self.ci._source_root)
        self.assertEqual(self.ci_provider.tests[1], self.ci._source_root + "/tests/integration_tests/")

        # verify results are "good"
        self.assertEqual(self.ci._error, 0)

        # verify we keep track of std_error
        self.assertIn("Great Success!!!!", self.ci.test_results)


    def test_run_tests__successful_error(self):
        # mock successful results
        self.ci_provider.test_results = (1, "Failure!!!!")

        # run the tests
        self.ci._run_tests()

        # verify that unit tests and integration tests were both run
        self.assertEqual(len(self.ci_provider.tests_source_dirs), 2)
        self.assertEqual(len(self.ci_provider.tests), 2)
        self.assertEqual(self.ci_provider.tests_source_dirs[0], self.ci._source_root)
        self.assertEqual(self.ci_provider.tests[0], self.ci._source_root + "/tests/unit_tests/")
        self.assertEqual(self.ci_provider.tests_source_dirs[1], self.ci._source_root)
        self.assertEqual(self.ci_provider.tests[1], self.ci._source_root + "/tests/integration_tests/")

        # verify results are "not good"
        self.assertEqual(self.ci._error, 1)

        # verify we keep track of std_error
        self.assertIn("Failure!!!!", self.ci.test_results)


    def test_go_complete__success(self):
        # mock successful results
        self.ci_provider.test_results = (0, "Great Success!!!!")

        # go!
        self.ci.go()

        # verify configs were replaced
        self.assertEqual(len(self.deployment_provider.old_config_files), self._replaced_files)
        self.assertEqual(len(self.deployment_provider.new_config_files), self._replaced_files)

        # verify servers are started
        self.assertEqual(len(self.ci_provider.servers_started), self._server_count)
        self.assertEqual(len(self.ci._processes), self._server_count)

        # verify dbs are initialized
        self.assertEqual(len(self.rest_provider.actions_called), self._db_count)

        # verify tests are run
        self.assertEqual(len(self.ci_provider.tests), 2)
        self.assertEqual(self.ci_provider.tests[0], self.ci._source_root + "/tests/unit_tests/")
        self.assertEqual(self.ci_provider.tests[1], self.ci._source_root + "/tests/integration_tests/")

        # since this was successful, make sure no emails were sent
        self.assertIsNone(self.email_provider.subject)
        self.assertIsNone(self.email_provider.message)

        # verify that we stop the servers
        self.assertEqual(len(self.ci_provider.terminated_processes), self._server_count)
        self.assertEqual(self.ci_provider.terminated_processes, self.ci._processes)


    def test_go_complete__failure(self):
        # mock failed results
        self.ci_provider.test_results = (1, "Fail!!!!")

        # go!
        self.ci.go()

        # verify configs were replaced
        self.assertEqual(len(self.deployment_provider.old_config_files), self._replaced_files)
        self.assertEqual(len(self.deployment_provider.new_config_files), self._replaced_files)

        # verify servers are started
        self.assertEqual(len(self.ci_provider.servers_started), self._server_count)
        self.assertEqual(len(self.ci._processes), self._server_count)

        # verify dbs are initialized
        self.assertEqual(len(self.rest_provider.actions_called), self._db_count)

        # verify tests are run
        self.assertEqual(len(self.ci_provider.tests), 2)
        self.assertEqual(self.ci_provider.tests[0], self.ci._source_root + "/tests/unit_tests/")
        self.assertEqual(self.ci_provider.tests[1], self.ci._source_root + "/tests/integration_tests/")

        # since this failed, make sure the failure email is sent
        self.assertIn(self.email_provider.from_email.split('@')[0], self.ci._from_email_aliases)
        self.assertEqual(self.email_provider.to_email, self.ci._to_email)
        self.assertEqual(self.email_provider.subject, "Bond Failure!")
        self.assertIn("Fail!!!!", self.email_provider.message)

        # verify that we stop the servers
        self.assertEqual(len(self.ci_provider.terminated_processes), self._server_count)
        self.assertEqual(self.ci_provider.terminated_processes, self.ci._processes)


    def test_go_complete__exception(self):
        # mock first method to throw an exception
        def exception():
            raise Exception("Woot!")
        self.ci._initialize_databases = exception

        # go!
        self.ci.go()

        # since there was an exception, make sure an exception email is sent
        self.assertIn(self.email_provider.from_email.split('@')[0], self.ci._from_email_aliases)
        self.assertEqual(self.email_provider.to_email, self.ci._to_email)
        self.assertEqual(self.email_provider.subject, "Exception Raised!")
        self.assertIn("Woot!", self.email_provider.message)

        # verify that we stop the servers
        self.assertEqual(len(self.ci_provider.terminated_processes), self._server_count)
        self.assertEqual(self.ci_provider.terminated_processes, self.ci._processes)


    def test_go_unit_success(self):
        # mock successful results
        self.ci_provider.test_results = (0, "Great Success!!!!")

        # go!
        self.ci.go(tests="unit")

        # verify no configs were replaced
        self.assertEqual(len(self.deployment_provider.old_config_files), 0)
        self.assertEqual(len(self.deployment_provider.new_config_files), 0)

        # verify no servers  were started
        self.assertEqual(len(self.ci_provider.servers_started), 0)
        self.assertEqual(len(self.ci._processes), 0)

        # verify no dbs were initialized
        self.assertEqual(len(self.rest_provider.actions_called), 0)

        # verify that unit tests were run
        self.assertEqual(len(self.ci_provider.tests), 1)
        self.assertEqual(self.ci_provider.tests[0], self.ci._source_root + "/tests/unit_tests/")

        # since this was successful, make sure no emails were sent
        self.assertIsNone(self.email_provider.subject)
        self.assertIsNone(self.email_provider.message)

    def test_go_integration_success(self):
        # mock successful results
        self.ci_provider.test_results = (0, "Great Success!!!!")

        # go!
        self.ci.go(tests="integration")

        # verify configs were replaced
        self.assertEqual(len(self.deployment_provider.old_config_files), self._replaced_files)
        self.assertEqual(len(self.deployment_provider.new_config_files), self._replaced_files)

        # verify servers are started
        self.assertEqual(len(self.ci_provider.servers_started), self._server_count)
        self.assertEqual(len(self.ci._processes), self._server_count)

        # verify dbs are initialized
        self.assertEqual(len(self.rest_provider.actions_called), self._db_count)

        # verify tests are run
        self.assertEqual(len(self.ci_provider.tests), 1)
        self.assertEqual(self.ci_provider.tests[0], self.ci._source_root + "/tests/integration_tests/")

        # since this was successful, make sure no emails were sent
        self.assertIsNone(self.email_provider.subject)
        self.assertIsNone(self.email_provider.message)

        # verify that we stop the servers
        self.assertEqual(len(self.ci_provider.terminated_processes), self._server_count)
        self.assertEqual(self.ci_provider.terminated_processes, self.ci._processes)


if __name__ == '__main__':
    unittest.main()
