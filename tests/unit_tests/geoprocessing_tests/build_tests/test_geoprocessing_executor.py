import unittest
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from geoprocessing.build.geoprocessing_executor import GeoprocessingExecutor
from common.utilities.inversion_of_control import Dependency, dependencies
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from datetime import datetime

class ExecuteGeoprocessingTests(mox.MoxTestBase):
    """
    This test file is half the old way (mock providers) and half the new way (mox)
    """

    def setUp(self):

        # call parent set up
        super(ExecuteGeoprocessingTests, self).setUp()

        # register mocks
        register_mock_dependencies()

        # get dependencies for verification
        self._file_provider = Dependency("FileProvider").value
        self._deployment_provider = Dependency("DeploymentProvider").value
        self._email_provider = Dependency("EmailProvider").value
        self._config = Dependency("Config").value

        self._run_directory = "/signal/python/geoprocessing"

    def tearDown(self):

        # call parent clean up
        super(ExecuteGeoprocessingTests, self).tearDown()

        dependencies.clear()

    def test_clear_log(self):
        geo_ex = GeoprocessingExecutor('')
        geo_ex._clear_log_file()

        self.assertIn("/signal/python/geoprocessing", self._deployment_provider.clear_log_file_folder)
        self.assertIn("log.txt", self._deployment_provider.clear_log_file_file)

    def test_untar_census_data(self):
        geo_ex = GeoprocessingExecutor('')

        # mock stuff
        census_files = ['a.tar.gz', 'b.tar.gz', 'c.tar.gz']
        fake_census_files = ['fake.txt', 'fake.tar.gzzzz']
        self._file_provider.files[geo_ex._census_data_directory] = census_files + fake_census_files
        self._deployment_provider.deleted_files = []
        self._deployment_provider.untarred_files = []

        geo_ex._untar_census_data()

        # check that only census files were untarred and deleted
        self.assertEqual([''.join([geo_ex._census_data_directory, file]) for file in census_files],
            self._deployment_provider.untarred_files)
        self.assertEqual([''.join([geo_ex._census_data_directory, file]) for file in census_files],
            self._deployment_provider.deleted_files)


    def test_execute_loader(self):
        GeoprocessingExecutor('')._execute_loader()

        self.assertIn(self._run_directory, self._deployment_provider.execute_loader_folders)

    def test_execute_census_ingest(self):
        geo_ex = GeoprocessingExecutor('')
        geo_ex._execute_census_ingest()

        self.assertIn(geo_ex._run_directory, self._deployment_provider.execute_census_ingest_folders)

    def test_execute_controller(self):
        geo_ex = GeoprocessingExecutor('')
        geo_ex._execute_controller()

        self.assertEqual(self._deployment_provider.controller_input_files[geo_ex._run_directory], "yo mama")

    def test_execute_report_generator(self):
        geo_ex = GeoprocessingExecutor('')
        geo_ex._execute_report_generator()

        self.assertEqual(geo_ex._start_time_str, self._deployment_provider.report_generators[geo_ex._run_directory])

    def test_execute__complete_execution(self):

        # register the mox dependencies for this test only
        register_common_mox_dependencies(self.mox)

        # create executor
        start_time = str(datetime.utcnow())
        geo_ex = GeoprocessingExecutor(start_time)

        # begin stubbing
        self.mox.StubOutWithMock(geo_ex, "_clear_log_file")
        self.mox.StubOutWithMock(geo_ex, "_untar_census_data")
        self.mox.StubOutWithMock(geo_ex, "_execute_loader")
        self.mox.StubOutWithMock(geo_ex, "_execute_census_ingest")
        self.mox.StubOutWithMock(geo_ex, "_execute_controller")
        self.mox.StubOutWithMock(geo_ex, "_execute_report_generator")
        self.mox.StubOutWithMock(geo_ex, "_shrink_db")
        self.mox.StubOutWithMock(geo_ex, "_shut_down_worker_server")

        # begin recording
        geo_ex._deployment_provider.update_environmental_setting("PYTHONPATH", "/signal/python/geoprocessing")
        geo_ex._clear_log_file()
        geo_ex._untar_census_data()
        geo_ex._execute_loader()
        geo_ex._execute_census_ingest()
        geo_ex._execute_controller()
        geo_ex._execute_report_generator()
        geo_ex._shrink_db()
        geo_ex._shut_down_worker_server()

        # replay all
        self.mox.ReplayAll()

        # run
        geo_ex.execute()


    def test__execute__failed_build_error_email(self):
        """
        Verify that failed build sends the right email
        """
        start_time = str(datetime.utcnow())
        geo_ex = GeoprocessingExecutor(start_time)


        # mock up a method to return an error
        def exception (): raise Exception("UNITTESTERROR")
        geo_ex._untar_census_data = exception
        geo_ex.execute()

        # verify the email contents
        self.assertEqual(self._email_provider.to_email, self._config.report_generator_email_recipients_developers)
        self.assertIn("Successful build but error running geoprocessing", self._email_provider.subject)

        # verify several parts of the email body
        self.assertRegexpMatches(self._email_provider.message, "Exception")

if __name__ == '__main__':
    unittest.main()
