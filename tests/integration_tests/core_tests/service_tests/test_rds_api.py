from __future__ import division
from core.service.svc_raw_data_storage.rds_api import app as rds_app
from tests.integration_tests.core_tests.service_tests.implementation.rds_test_collection import RDSTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
import unittest


###################################################################################################


class Test_RDS_API(ServiceTestCase):
    """
    Test case for Raw Data Service.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.svc_key = "RDS"
        cls.apps = {"RDS": rds_app}
        cls.test_colls = {"RDS": RDSTestCollection}

##############################################################################################################
##
## Test methods must adhere to a strict naming convention:
##   1)  Name of test method must have "test_" prepended to the actual name of the test method
##       from the test collection.
##
##   2)  The actual test that should run must be called from within the test method (obviously).
##
##   3)  The actual test's name must start with its lowercase service key and an underscore ("mds_",
##       "main_", "rds_", "wfs_", etc.).
##
##   **  NOTE: The values of these test methods are dynamically overwritten to execute the setUp and
##       tearDown methods from the test's collection before and after the actual test specified. This
##       was a design decision, because the test collection should know how to set up and tear down
##       each test it houses.
##
##############################################################################################################

    def test_rds_test_upload_files(self):
        self.tests["RDS"].rds_test_upload_files()

    def test_rds_test_update_path(self):
        self.tests["RDS"].test_rds_test_update_path()

    def test_rds_test_download_file_by_name(self):
        self.tests["RDS"].rds_test_download_file_by_name()

    def test_rds_test_download_file_by_id(self):
        self.tests["RDS"].rds_test_download_file_by_id()

    def test_rds_test_file_manager_listing(self):
        self.tests["RDS"].rds_test_file_manager_listing()

    def test_rds_test_get_file_info(self):
        self.tests["RDS"].rds_test_get_file_info()

    def test_rds_test_delete_file(self):
        self.tests["RDS"].rds_test_delete_file()

    def test_rds_test_delete_folder_recursive(self):
        self.tests["RDS"].rds_test_delete_folder_recursive()

    def test_rds_test_delete_file_that_does_not_exist_fails(self):
        self.tests["RDS"].rds_test_delete_file_that_does_not_exist_fails()

    def test_rds_test_upload_duplicate_file_md5_fails(self):
        self.tests["RDS"].rds_test_upload_duplicate_file_md5_fails()

    # for some reason this won't pass in continuous integration but it does everywhere else, commenting out until tomorrow
    # def test_rds_test_upload_duplicate_filename_fails(self):
    #     self.tests["RDS"].rds_test_upload_duplicate_filename_fails()


###################################################################################################


if __name__ == '__main__':
    unittest.main(verbosity = 2)
