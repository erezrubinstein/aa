import json
import mox
import unittest
from collections import namedtuple
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from economics.helpers.helpers import EconRDSHelper, HomeDirCleaner

__author__ = 'clairseager'


class EconomicsRDSDownloaderCleanupTest(mox.MoxTestBase):

    def setUp(self):
        super(EconomicsRDSDownloaderCleanupTest, self).setUp()

        # set up mocks
        register_common_mox_dependencies(self.mox)
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.deployment_provider = Dependency("DeploymentProvider").value

        # logger
        logger = Dependency("SimpleConsole").value

        self.rds_directory = "monty/python" # e.g. "economics/unemployment"
        self.filename_part = "Dead_Parrot_" # e.g. "US_labor_data"
        self.downloader = EconRDSHelper(logger, self.rds_directory, self.filename_part, context=None)

        self.homedircleaner = HomeDirCleaner(logger, ["thisparrot","isnomore","ithasceasedtobe"])

    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()

    def test__get_latest_rds_file(self):
        mock_file_response = {
            'uploadDate': '2013-09-10T16:25:44.598000',
            '_id': '522f480845d3d8b42eecc289',
            'metadata': {
                'short_filename': 'Dead_Parrot_2013_06_01_as_of_2014-03-01.tar.gz',
                'path': 'monty/python',
            }
        }
        response = namedtuple("response", "content")
        r = response(json.dumps(mock_file_response))

        self.mock_main_access.rds.call_get_latest_in_path("monty/python").AndReturn(r)
        latest_id = mock_file_response.get("_id", None)
        as_of_date = "2013-06-01T00:00:00"

        self.mox.ReplayAll()

        self.downloader.filename = "Dead_Parrot_2013_06_01_as_of_2014-03-01.tar.gz"
        self.downloader.get_latest_rds_file_info()

        self.assertEqual(as_of_date, self.downloader.as_of_date)
        self.assertEqual(latest_id, self.downloader.file_id)
        self.assertEqual("Dead_Parrot_2013_06_01_as_of_2014-03-01.tar.gz", self.downloader.filename)


    def test_run_homedircleaner(self):
        self.homedircleaner.path = "derp/"

        # begin recording
        self.deployment_provider.delete_files_and_folders("derp/", "thisparrot")
        self.deployment_provider.delete_files_and_folders("derp/", "isnomore")
        self.deployment_provider.delete_files_and_folders("derp/", "ithasceasedtobe")

        # replay all
        self.mox.ReplayAll()

        # bumbaclot
        self.homedircleaner.run()

if __name__ == '__main__':
    unittest.main()
