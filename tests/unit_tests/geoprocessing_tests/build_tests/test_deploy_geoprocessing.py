from datetime import datetime
import os
from geoprocessing.build.deploy_geoprocessing_python import GeoProcessingDeployer
from geoprocessing.business_logic.global_constants import GEOPROCESSING_IDENTIFIER
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.helpers.dependency_helper import register_mock_dependencies

__author__ = 'erezrubinstein'

import unittest

class DeployGeoprocessingTests(unittest.TestCase):
    def setUp(self):
        # register mocks
        register_mock_dependencies()

        # get dependencies for verification
        self.file_provider = Dependency("FileProvider").value
        self.deployment_provider = Dependency("DeploymentProvider").value
        self.cloud_provider = Dependency("CloudProviderNewEnvironment").value
        self.email_provider = Dependency("EmailProvider").value
        self.config = Dependency("Config").value

        # get vars for tests
        self.home = "/media/code/deploy"

    def doCleanups(self):
        # make sure correct config is loaded.  When running from nose tests, sometimes the config stays loaded with the staging.b (which is replaced in a test below)
        self._config = self.config.reload_from_different_file("config.yml")

        # clear dependencies
        dependencies.clear()


    def test_default_variables(self):
        """
        Verify that default deployment settings are correct
        """
        deployer = GeoProcessingDeployer()

        # make sure the default deployment setting are cloud/staging
        self.assertEqual(deployer._worker_server, "CLOUD")
        self.assertEqual(deployer._environment_config_file, "config.cloud.staging.a.yml")

        # make sure the path is correct and does not end with a slash
        self.assertEqual(deployer._root_directory, self.home)
        self.assertFalse(deployer._root_directory.endswith("/"))

        # test environmental variables
        self.assertEqual(deployer._git_repository, "ubuntu@ec2-54-243-223-89.compute-1.amazonaws.com:/mnt/nri_codeZ.git")
        self.assertEqual(deployer._s3_config_file, self.home + "/.s3cfg")
        self.assertEqual(deployer._loader_files_s3_directory, "s3://nri-repo/retail_loader_files/")
        self.assertEqual(deployer._census_files_s3_directory, "s3://nri-repo/census_data/")

        # verify the local folders
        self.assertEqual(deployer._local_signal_directory, self.home + "/signal")
        self.assertEqual(deployer._local_deploy_directory, self.home + "/signal/deploy")
        self.assertEqual(deployer._local_code_directory, self.home +  "/signal/deploy/code")
        self.assertEqual(deployer._local_loader_files_directory, self.home + "/signal/deploy/loader_files")
        self.assertEqual(deployer._local_census_data_directory, self.home + "/signal/deploy/census_data")
        self.assertEqual(deployer._local_dot_git_directory, self.home + "/signal/deploy/code/.git/")
        self.assertEqual(deployer._local_python_directory, self.home + "/signal/deploy/code/python")
        self.assertEqual(deployer._local_geoprocessing_directory, self.home + "/signal/deploy/code/python/geoprocessing")
        self.assertEqual(deployer._local_unit_tests_directory, self.home + "/signal/deploy/code/python/tests/unit_tests/geoprocessing_tests")
        self.assertEqual(deployer._local_integration_tests_directory, self.home + "/signal/deploy/code/python/tests/integration_tests/geoprocessing_tests")

        # verify build environment settings
        self.assertEqual(deployer._build_db_script, "build/db/build_db.py")
        self.assertEqual(deployer._update_config_script, "build/update_config_gis_servers.py")
        self.assertEqual(deployer._create_cloud_script, "build/amazon_cloud_formation/create_geo_processing_amazon_worker_server.py")
        self.assertEqual(deployer._cloud_template_gp_worker, self.home + "/signal/deploy/code/python/geoprocessing/build/amazon_cloud_formation/create_amazon_ubuntu_geo_processing_server.json")
        self.assertEqual(deployer._cloud_template_honkin_GIS, self.home + "/signal/deploy/code/python/geoprocessing/build/amazon_cloud_formation/create_amazon_ubuntu_honkin_GIS.json")
        self.assertEqual(deployer._create_cloud_script_output_gp_worker, "PublicDNS")
        self.assertEqual(deployer._create_cloud_script_output_honkin_GIS, "PrivateDNS")
        self.assertEqual(deployer._cloud_worker_name_gp_worker, "GeoProcessingWorker")
        self.assertEqual(deployer._cloud_worker_name_honkin_GIS, "HonkinGISWorker")
        self.assertEqual(deployer._honkin_GIS_sleep_seconds, 20)

        # verify remote vars
        self.assertEqual(deployer._remote_python_folder, "/signal/python")
        self.assertEqual(deployer._remote_unit_tests_folder, "/signal/python/tests/unit_tests/geoprocessing_tests")
        self.assertEqual(deployer._remote_integration_tests_folder, "/signal/python/tests/integration_tests/geoprocessing_tests")
        self.assertEqual(deployer._remote_loader_files_remote_directory, "/signal/loader_files")
        self.assertEqual(deployer._remote_census_files_remote_directory, "/signal/census_data")
        self.assertEqual(deployer._remote_execute_geo_processing_python, "/signal/python/geoprocessing/build/geoprocessing_executor.py")

        # verify loader file settings
        self.assertEqual(deployer._loader_files_next_run_directory, self.home + "/signal/deploy/loader_files/next_run_a")
        self.assertEqual(deployer._loader_files_temp_copy_directory, self.home + "/signal/deploy/loader_files/temp_copy_directory")

        # verify mis settings
        self.assertEqual(deployer._excel_file_format_regex, ".*\.xls[x]*$")

    def test_proper_directories_are_created(self):
        """
        Verify that the proper files are created
        """
        deployer = GeoProcessingDeployer()
        deployer._create_directory_structure()

        self.assertIn(self.home + "/signal", self.file_provider.directories_created)
        self.assertIn(self.home + "/signal/deploy", self.file_provider.directories_created)
        self.assertIn(self.home + "/signal/deploy/loader_files", self.file_provider.directories_created)
        self.assertIn(self.home + "/signal/deploy/census_data", self.file_provider.directories_created)
        self.assertIn(self.home + "/signal/deploy/code", self.file_provider.directories_created)

    def test_get_latest_from_git__no_repository(self):
        """
        Verify that the repository gets cloned if there's no .git folder
        """
        deployer = GeoProcessingDeployer()
        deployer._get_latest_from_git()

        # verify that it tried to clone the repository
        self.assertEqual(self.deployment_provider.git_clone_repository_address, "ubuntu@ec2-54-243-223-89.compute-1.amazonaws.com:/mnt/nri_codeZ.git")
        self.assertEqual(self.deployment_provider.git_clone_path, self.home + "/signal/deploy/code")

        # verify that it reset the repository and got latest
        self.assertEqual(self.deployment_provider.git_reset_path, self.home + "/signal/deploy/code")
        self.assertEqual(self.deployment_provider.git_get_latest_path, self.home + "/signal/deploy/code")


    def test_get_latest_from_git__repository_exists(self):
        """
        Verify that the repository does not get cloned if there is a .git folder
        """
        # mock up the .git folder
        self.file_provider.directories[self.home + "/signal/deploy/code/.git/"] = True

        deployer = GeoProcessingDeployer()
        deployer._get_latest_from_git()

        # verify that it tried to clone the repository
        self.assertFalse(hasattr(self.deployment_provider, "git_clone_repository_address"))
        self.assertFalse(hasattr(self.deployment_provider, "git_clone_path"))

        # verify that it reset the repository and got latest
        self.assertEqual(self.deployment_provider.git_reset_path, self.home + "/signal/deploy/code")
        self.assertEqual(self.deployment_provider.git_get_latest_path, self.home + "/signal/deploy/code")

    def test_update_python_path(self):
        deployer = GeoProcessingDeployer()
        deployer._update_python_path()
        self.assertEqual(len(self.deployment_provider.environmental_settings), 1)
        self.assertEqual(len(self.deployment_provider.environmental_values), 1)
        self.assertEqual(self.deployment_provider.environmental_settings[0], "PYTHONPATH")
        self.assertEqual(self.deployment_provider.environmental_values[0], self.home + "/signal/deploy/code/python")


    def test_run_unit_tests(self):
        """
        Verify that all the unit tests were run locally
        """
        deployer = GeoProcessingDeployer()
        deployer._run_unit_tests()

        # verify that we're testing the unit tests
        self.assertEqual(len(self.deployment_provider.python_unit_tests), 1)
        self.assertEqual(self.deployment_provider.python_unit_tests[0], self.home + "/signal/deploy/code/python/tests/unit_tests/geoprocessing_tests")


    def test_replace_local_configs_and_create_db(self):
        """
        Verify that the local configs are replaced correctly and that the create db script is run on the right db
        """
        deployer = GeoProcessingDeployer("test_server", "config.cloud.staging.b.yml")
        deployer._replace_local_configs_and_create_db()

        # make sure configs are correct
        self.assertEqual(self.deployment_provider.old_config_files[0], self.home + "/signal/deploy/code/python/geoprocessing/config.yml")
        self.assertEqual(self.deployment_provider.new_config_files[0], self.home + "/signal/deploy/code/python/geoprocessing/config.cloud.staging.b.yml")

        # make sure we use correct values from cloud config
        self.assertIn("next_run_b", deployer._loader_files_next_run_directory)

        # make sure correct db script is called
        self.assertEqual(self.deployment_provider.db_script_repository_path, self.home + "/signal/deploy/code/python/geoprocessing")
        self.assertEqual(self.deployment_provider.db_script, "build/db/build_db.py")


    def test_run_create_cloud_server(self):
        """
        Verify that using the default settings creates a worker on the cloud
        """
        # mock server address
        self.deployment_provider.cloud_address = "1.1.1.1"

        deployer = GeoProcessingDeployer()
        deployer._create_worker_server()

        # verify that the right address was returned and that the right template was used
        self.assertEqual(self.deployment_provider.server_template[0], deployer._cloud_template_gp_worker)
        self.assertEqual(self.deployment_provider.create_cloud_script_path[0], self.home + "/signal/deploy/code/python/geoprocessing")
        self.assertEqual(self.deployment_provider.create_cloud_script[0], "build/amazon_cloud_formation/create_geo_processing_amazon_worker_server.py")
        self.assertEqual(self.deployment_provider.create_cloud_script_output[0], "PublicDNS")
        self.assertEqual(self.deployment_provider.create_cloud_script_worker_name[0], "GeoProcessingWorker")
        self.assertEqual(deployer._server_ssh_address, "signal_deploy@1.1.1.1")
        self.assertEqual(deployer._server_root_rsync_path, "signal_deploy@1.1.1.1:/signal")
        self.assertEqual(deployer._server_loader_files_rsync_path, "signal_deploy@1.1.1.1:/signal/loader_files")
        self.assertEqual(deployer._server_census_files_rsync_path, "signal_deploy@1.1.1.1:/signal/census_data")


    def test_run_create_cloud_server__stopped_servers_exist(self):
        """
        Verify that using the default settings creates a worker on the cloud
        """
        # mock existing stopped servers
        self.cloud_provider.stopped_ec2_instance_ids[GEOPROCESSING_IDENTIFIER] = ["test_instance_id"]
        self.cloud_provider.ec2_public_dnses["test_instance_id"] = "public_dns"

        deployer = GeoProcessingDeployer()
        deployer._create_worker_server()

        # verify that the we didn't create a cloud server
        self.assertEqual(len(self.deployment_provider.create_cloud_script), 0)

        # verify that the addresses were set correctly from the dns
        self.assertEqual(deployer._server_ssh_address, "signal_deploy@public_dns")
        self.assertEqual(deployer._server_root_rsync_path, "signal_deploy@public_dns:/signal")
        self.assertEqual(deployer._server_loader_files_rsync_path, "signal_deploy@public_dns:/signal/loader_files")
        self.assertEqual(deployer._server_census_files_rsync_path, "signal_deploy@public_dns:/signal/census_data")


    def test_do_not_create_cloud_server__local(self):
        """
        Verify that using you can override creating a cloud worker
        """
        deployer = GeoProcessingDeployer("2.2.2.2")
        deployer._create_worker_server()

        # verify that create cloud was not created
        self.assertEqual(self.deployment_provider.server_template, [])
        self.assertEqual(deployer._server_ssh_address, "signal_deploy@2.2.2.2")
        self.assertEqual(deployer._server_root_rsync_path, "signal_deploy@2.2.2.2:/signal")
        self.assertEqual(deployer._server_loader_files_rsync_path, "signal_deploy@2.2.2.2:/signal/loader_files")
        self.assertEqual(deployer._server_census_files_rsync_path, "signal_deploy@2.2.2.2:/signal/census_data")


    def test_copy_geo_processing_code(self):
        """
        Verify that the copy geo processing code works
        """
        deployer = GeoProcessingDeployer("2.2.2.2")
        # run create server to fake the addresses
        deployer._create_worker_server()
        deployer._copy_geo_processing_code_to_server()

        self.assertEqual(len(self.deployment_provider.rsync_code_paths), 1)
        self.assertEqual(len(self.deployment_provider.rsync_server_paths), 1)
        self.assertEqual(self.deployment_provider.rsync_code_paths[0], self.home + "/signal/deploy/code/python")
        self.assertEqual(self.deployment_provider.rsync_server_paths[0], "signal_deploy@2.2.2.2:/signal")


    def test_run_unit_and_integration_tests_on_new_server(self):
        """
        Verify that setting the ssh host is correct
        """
        deployer = GeoProcessingDeployer("2.2.2.2")
        # run create server to fake the addresses
        deployer._create_worker_server()
        deployer._run_unit_and_integration_tests_on_new_server()

        # verify results
        self.assertEqual(self.deployment_provider.remote_geoprocessing_folders[0], "/signal/python")
        self.assertEqual(self.deployment_provider.remote_tests_folders[0], "/signal/python/tests/unit_tests/geoprocessing_tests")
        self.assertEqual(self.deployment_provider.remote_geoprocessing_folders[1], "/signal/python")
        self.assertEqual(self.deployment_provider.remote_tests_folders[1], "/signal/python/tests/integration_tests/geoprocessing_tests")


    def test_copy_loader_files_to_worker__no_next_run_folder(self):
        """
        Verify that everything is copied if there is no next_run folder
        """
        deployer = GeoProcessingDeployer('1.1.1.1')
        # run create server to fake the addresses
        deployer._create_worker_server()
        deployer._copy_loader_files_to_worker()

        # verify that the temp directory is always removed and recreated
        self.assertIn(self.home + "/signal/deploy/loader_files/temp_copy_directory", self.file_provider.removed_and_recreated_directories)

        # verify that the correct parameters are passed to s3 sync
        self.assertEqual(self.deployment_provider.s3_config_files[0], self.home + "/.s3cfg")
        self.assertEqual(self.deployment_provider.s3_directories[0], "s3://nri-repo/retail_loader_files/")
        self.assertEqual(self.deployment_provider.s3_local_directories[0], self.home + "/signal/deploy/loader_files/")

        # verify that it copied all files into the temp directory (since next_run is empty)
        self.assertEqual(self.file_provider.recursively_copy_from_directory, self.home + "/signal/deploy/loader_files")
        self.assertEqual(self.file_provider.recursively_copy_to_directory, self.home + "/signal/deploy/loader_files/temp_copy_directory")
        self.assertEqual(self.file_provider.recursively_copy_file_format, ".*\.xls[x]*$")

        # verify that rsync worked
        self.assertEqual(len(self.deployment_provider.rsync_code_paths), 1)
        self.assertEqual(len(self.deployment_provider.rsync_server_paths), 1)
        self.assertEqual(self.deployment_provider.rsync_code_paths[0], self.home + "/signal/deploy/loader_files/temp_copy_directory/")
        self.assertEqual(self.deployment_provider.rsync_server_paths[0], "signal_deploy@1.1.1.1:/signal/loader_files")


    def test_copy_loader_files_to_worker__empty_next_run_folder(self):
        """
        Verify that everything is copied if the next_run folder exists, but is empty
        """
        # mock up that next_run_folder exists
        self.file_provider.directories[self.home + "/signal/deploy/loader_files/next_run"] = True

        # run the deployer
        deployer = GeoProcessingDeployer('1.1.1.1')
        # run create server to fake the addresses
        deployer._create_worker_server()
        deployer._copy_loader_files_to_worker()

        # verify that the temp directory is always removed and recreated
        self.assertIn(self.home + "/signal/deploy/loader_files/temp_copy_directory", self.file_provider.removed_and_recreated_directories)

        # verify that the correct parameters are passed to s3 sync
        self.assertEqual(self.deployment_provider.s3_config_files[0], self.home + "/.s3cfg")
        self.assertEqual(self.deployment_provider.s3_directories[0], "s3://nri-repo/retail_loader_files/")
        self.assertEqual(self.deployment_provider.s3_local_directories[0], self.home + "/signal/deploy/loader_files/")

        # verify that it copied all files into the temp directory (since next_run is empty)
        self.assertEqual(self.file_provider.recursively_copy_from_directory, self.home + "/signal/deploy/loader_files")
        self.assertEqual(self.file_provider.recursively_copy_to_directory, self.home + "/signal/deploy/loader_files/temp_copy_directory")
        self.assertEqual(self.file_provider.recursively_copy_file_format, ".*\.xls[x]*$")

        # verify that rsync worked
        self.assertEqual(len(self.deployment_provider.rsync_code_paths), 1)
        self.assertEqual(len(self.deployment_provider.rsync_server_paths), 1)
        self.assertEqual(self.deployment_provider.rsync_code_paths[0], self.home + "/signal/deploy/loader_files/temp_copy_directory/")
        self.assertEqual(self.deployment_provider.rsync_server_paths[0], "signal_deploy@1.1.1.1:/signal/loader_files")


    def test_copy_loader_files_to_worker__populated_next_run_folder(self):
        """
        Verify that only the next_run folder is copied if it's populated with xlsx files
        """
        # mock up that next_run_folder exists
        self.file_provider.directories[self.home + "/signal/deploy/loader_files/next_run"] = True

        # run the deployer
        deployer = GeoProcessingDeployer('1.1.1.1')
        # run create server to fake the addresses
        deployer._create_worker_server()
        deployer._copy_loader_files_to_worker()

        # verify that the temp directory is always removed and recreated
        self.assertIn(self.home + "/signal/deploy/loader_files/temp_copy_directory", self.file_provider.removed_and_recreated_directories)

        # verify that the correct parameters are passed to s3 sync
        self.assertEqual(self.deployment_provider.s3_config_files[0], self.home + "/.s3cfg")
        self.assertEqual(self.deployment_provider.s3_directories[0], "s3://nri-repo/retail_loader_files/")
        self.assertEqual(self.deployment_provider.s3_local_directories[0], self.home + "/signal/deploy/loader_files/")

        # verify that it copied all files into the temp directory (since next_run is empty)
        self.assertEqual(self.file_provider.recursively_copy_from_directory, self.home + "/signal/deploy/loader_files")
        self.assertEqual(self.file_provider.recursively_copy_to_directory, self.home + "/signal/deploy/loader_files/temp_copy_directory")
        self.assertEqual(self.file_provider.recursively_copy_file_format, ".*\.xls[x]*$")

        # verify that rsync worked
        self.assertEqual(len(self.deployment_provider.rsync_code_paths), 1)
        self.assertEqual(len(self.deployment_provider.rsync_server_paths), 1)
        self.assertEqual(self.deployment_provider.rsync_code_paths[0], self.home + "/signal/deploy/loader_files/temp_copy_directory/")
        self.assertEqual(self.deployment_provider.rsync_server_paths[0], "signal_deploy@1.1.1.1:/signal/loader_files")


    def test_copy_census_files_to_server(self):
        """
        Verify that copying the census files works correctly
        """
        deployer = GeoProcessingDeployer('1.1.1.1')
        # run create server to fake the addresses
        deployer._create_worker_server()
        deployer._copy_census_files_to_server()

        # verify s3cmd params
        self.assertEqual(self.deployment_provider.s3_config_files[0], self.home + "/.s3cfg")
        self.assertEqual(self.deployment_provider.s3_directories[0], "s3://nri-repo/census_data/")
        self.assertEqual(self.deployment_provider.s3_local_directories[0], self.home + "/signal/deploy/census_data/")

        # verify that rsync worked
        self.assertEqual(len(self.deployment_provider.rsync_code_paths), 1)
        self.assertEqual(len(self.deployment_provider.rsync_server_paths), 1)
        self.assertEqual(self.deployment_provider.rsync_code_paths[0], self.home + "/signal/deploy/census_data/")
        self.assertEqual(self.deployment_provider.rsync_server_paths[0], "signal_deploy@1.1.1.1:/signal/census_data")


    def test_execute_geo_processing_remotely(self):
        """
        Verify that executing geo processing works correctly
        """
        deployer = GeoProcessingDeployer()
        deployer._execute_geo_processing_remotely(datetime(2012, 1, 1))

        self.assertEqual(self.deployment_provider.execute_geo_processing_python_script, "/signal/python/geoprocessing/build/geoprocessing_executor.py")
        self.assertEqual(self.deployment_provider.execute_geo_processing_run_directory, "/signal/python")
        self.assertEqual(self.deployment_provider.execute_geo_processing_start_time, datetime(2012, 1, 1))


    def test__deploy__complete_deployment(self):
        """
        Verify that calling deploy calls all the functions correctly and works properly
        """
        # mock up date
        self.deployment_provider.cloud_address = "1.1.1.1"

        # run deployer
        deployer = GeoProcessingDeployer()
        deployer.deploy()

        # verify that directory structure was created
        self.assertIn(self.home + "/signal", self.file_provider.directories_created)
        self.assertIn(self.home + "/signal/deploy", self.file_provider.directories_created)
        self.assertIn(self.home + "/signal/deploy/loader_files", self.file_provider.directories_created)
        self.assertIn(self.home + "/signal/deploy/census_data", self.file_provider.directories_created)
        self.assertIn(self.home + "/signal/deploy/code", self.file_provider.directories_created)

        # verify that we get latest from git
        self.assertEqual(self.deployment_provider.git_clone_repository_address, "ubuntu@ec2-54-243-223-89.compute-1.amazonaws.com:/mnt/nri_codeZ.git")
        self.assertEqual(self.deployment_provider.git_clone_path, self.home + "/signal/deploy/code")
        self.assertEqual(self.deployment_provider.git_reset_path, self.home + "/signal/deploy/code")
        self.assertEqual(self.deployment_provider.git_get_latest_path, self.home + "/signal/deploy/code")

        # verify local unit tests are run
        self.assertEqual(self.deployment_provider.python_unit_tests[0], self.home + "/signal/deploy/code/python/tests/unit_tests/geoprocessing_tests")

        # verify replace config and create db worked
        self.assertEqual(self.deployment_provider.old_config_files[0], self.home + "/signal/deploy/code/python/geoprocessing/config.yml")
        self.assertEqual(self.deployment_provider.new_config_files[0], self.home + "/signal/deploy/code/python/geoprocessing/config.cloud.staging.a.yml")
        self.assertEqual(self.deployment_provider.db_script_repository_path, self.home + "/signal/deploy/code/python/geoprocessing")
        self.assertEqual(self.deployment_provider.db_script, "build/db/build_db.py")

        # verify cloud server was created
        self.assertEqual(self.deployment_provider.server_template[0], deployer._cloud_template_gp_worker)
        self.assertEqual(self.deployment_provider.create_cloud_script_path[0], self.home + "/signal/deploy/code/python/geoprocessing")
        self.assertEqual(self.deployment_provider.create_cloud_script[0], "build/amazon_cloud_formation/create_geo_processing_amazon_worker_server.py")
        self.assertEqual(self.deployment_provider.create_cloud_script_output[0], "PublicDNS")
        self.assertEqual(self.deployment_provider.create_cloud_script_worker_name[0], "GeoProcessingWorker")
        self.assertEqual(deployer._server_ssh_address, "signal_deploy@1.1.1.1")
        self.assertEqual(deployer._server_root_rsync_path, "signal_deploy@1.1.1.1:/signal")
        self.assertEqual(deployer._server_loader_files_rsync_path, "signal_deploy@1.1.1.1:/signal/loader_files")
        self.assertEqual(deployer._server_census_files_rsync_path, "signal_deploy@1.1.1.1:/signal/census_data")

        # verify copy code to server
        self.assertEqual(self.deployment_provider.rsync_code_paths[0], self.home + "/signal/deploy/code/python")
        self.assertEqual(self.deployment_provider.rsync_server_paths[0], "signal_deploy@1.1.1.1:/signal")

        # verify run remote unit tests and integration tests
        self.assertEqual(self.deployment_provider.remote_geoprocessing_folders[0], "/signal/python")
        self.assertEqual(self.deployment_provider.remote_tests_folders[0], "/signal/python/tests/unit_tests/geoprocessing_tests")
        self.assertEqual(self.deployment_provider.remote_geoprocessing_folders[1], "/signal/python")
        self.assertEqual(self.deployment_provider.remote_tests_folders[1], "/signal/python/tests/integration_tests/geoprocessing_tests")

        # verify loader files copied locally, logic ran with temp/next_run folders, and everything copied to server
        self.assertIn(self.home + "/signal/deploy/loader_files/temp_copy_directory", self.file_provider.removed_and_recreated_directories)
        self.assertEqual(self.deployment_provider.s3_config_files[0], self.home + "/.s3cfg")
        self.assertEqual(self.deployment_provider.s3_directories[0], "s3://nri-repo/retail_loader_files/")
        self.assertEqual(self.deployment_provider.s3_local_directories[0], self.home + "/signal/deploy/loader_files/")
        self.assertEqual(self.file_provider.recursively_copy_from_directory, self.home + "/signal/deploy/loader_files")
        self.assertEqual(self.file_provider.recursively_copy_to_directory, self.home + "/signal/deploy/loader_files/temp_copy_directory")
        self.assertEqual(self.file_provider.recursively_copy_file_format, ".*\.xls[x]*$")
        self.assertEqual(self.deployment_provider.rsync_code_paths[1], self.home + "/signal/deploy/loader_files/temp_copy_directory/")
        self.assertEqual(self.deployment_provider.rsync_server_paths[1], "signal_deploy@1.1.1.1:/signal/loader_files")

        # verify census files copied correctly
        self.assertEqual(self.deployment_provider.s3_config_files[1], self.home + "/.s3cfg")
        self.assertEqual(self.deployment_provider.s3_directories[1], "s3://nri-repo/census_data/")
        self.assertEqual(self.deployment_provider.s3_local_directories[1], self.home + "/signal/deploy/census_data/")
        self.assertEqual(self.deployment_provider.rsync_code_paths[2], self.home + "/signal/deploy/census_data/")
        self.assertEqual(self.deployment_provider.rsync_server_paths[2], "signal_deploy@1.1.1.1:/signal/census_data")

        # verify geo processing was executed properly
        self.assertEqual(self.deployment_provider.execute_geo_processing_python_script, "/signal/python/geoprocessing/build/geoprocessing_executor.py")
        self.assertEqual(self.deployment_provider.execute_geo_processing_run_directory, "/signal/python")

        # make sure end time is larger (could be same because of unit test speed) as start time
        self.assertGreaterEqual(datetime.utcnow(), self.deployment_provider.execute_geo_processing_start_time)


    def test__deploy__failed_build_error_email(self):
        """
        Verify that failed build sends the right email
        """
        # run deployer
        deployer = GeoProcessingDeployer()
        # mock up a method to return an error
        def exception (): raise Exception("UNITTESTERROR")
        deployer._create_directory_structure = exception
        deployer.deploy()

        # verify the email contents
        self.assertEqual(self.email_provider.to_email, self.config.report_generator_email_recipients_developers)
        self.assertEqual(self.email_provider.from_email, self.config.email_settings_from_email)
        self.assertEqual(self.email_provider.subject, "Failed Build")

        # verify several parts of the email body
        self.assertRegexpMatches(self.email_provider.message, "Build Start Time \(UTC\): .*\n")
        self.assertRegexpMatches(self.email_provider.message, "Build End Time \(UTC\): .*\n")
        self.assertRegexpMatches(self.email_provider.message, "Elapsed Time: .*\..*")

        # make sure there is an error
        self.assertRegexpMatches(self.email_provider.message, "Exception: UNITTESTERROR*")


if __name__ == '__main__':
    unittest.main()
