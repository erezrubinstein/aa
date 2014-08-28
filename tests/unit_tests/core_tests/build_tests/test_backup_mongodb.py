import os
from common.utilities.inversion_of_control import dependencies, Dependency
from infrastructure.backup.back_up_mongo_db import MongoDBBackup
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
import unittest
import mox

__author__ = 'erezrubinstein'


class MongoDBBackupTests(mox.MoxTestBase):

    def setUp(self):
        super(MongoDBBackupTests, self).setUp()

        # set up mocks
        register_mock_dependencies()
        self.amazon_provider = Dependency("CloudProvider").value
        self.deployment_provider = Dependency("DeploymentProvider").value
        self.file_provider = Dependency("FileProvider").value
        self.email_provider = Dependency("EmailProvider").value

        # logger
        logger = Dependency("SimpleConsole").value

        # set up mongo deployer
        self.deployer = MongoDBBackup("localhost", 123, "test_db", "yoyoma", "password", logger=logger)

    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()

    def test_backup_mongo_db(self):
        # go
        self.deployer._back_up_and_zip()

        # verify correct parameters were passed in
        self.assertEqual(self.deployment_provider.mongodb_host, "localhost:123")
        self.assertEqual(self.deployment_provider.mongodb_database, "test_db")
        self.assertEqual(self.deployment_provider.mongodb_username, "yoyoma")
        self.assertEqual(self.deployment_provider.mongodb_password, "password")

        # verify filename matches regex (date_format = year_month_day_hour_minutes_seconds)
        self.assertRegexpMatches(self.deployment_provider.mongodb_output_file, "mongodb_backup_test_db_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+")

        # verify file was zipped
        self.assertEqual(self.deployment_provider.tar_filename, self.deployment_provider.mongodb_output_file)
        self.assertEqual(self.deployment_provider.tar_zipped_file_name, self.deployment_provider.mongodb_output_file + ".tar.gz")

    def test_upload_to_s3(self):
        # go
        self.deployer._upload_to_s3()

        # get expected config file
        expected_s3_config_file = os.getenv("HOME") + "/.s3cfg"

        # assert s3 config
        self.assertEqual(len(self.deployment_provider.s3_config_files), 0)

        # assert s3 directory
        self.assertEqual(len(self.deployment_provider.s3_directories), 0)

        # assert file
        self.assertEqual(len(self.amazon_provider.s3_files), 1)

    def test_cleanup_files(self):
        # go
        self.deployer._cleanup_files()

        # verify output directory was deleted
        self.assertEqual(len(self.file_provider.deleted_directories), 1)
        self.assertRegexpMatches(self.file_provider.deleted_directories[0], "mongodb_backup_test_db_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+")

        # verify zipped file was deleted
        self.assertEqual(len(self.file_provider.deleted_files), 1)
        self.assertRegexpMatches(self.file_provider.deleted_files[0], "mongodb_backup_test_db_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+\.tar\.gz")

    def test_complete_run(self):
        # go
        self.deployer.backup_and_upload_to_s3()

        # verify back ups
        self.assertEqual(self.deployment_provider.mongodb_host, "localhost:123")
        self.assertEqual(self.deployment_provider.mongodb_database, "test_db")
        self.assertEqual(self.deployment_provider.mongodb_username, "yoyoma")
        self.assertEqual(self.deployment_provider.mongodb_password, "password")
        self.assertRegexpMatches(self.deployment_provider.mongodb_output_file, "mongodb_backup_test_db_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+")
        self.assertEqual(self.deployment_provider.tar_filename, self.deployment_provider.mongodb_output_file)
        self.assertEqual(self.deployment_provider.tar_zipped_file_name, self.deployment_provider.mongodb_output_file + ".tar.gz")

        # verify s3 uploads
        expected_s3_config_file = os.getenv("HOME") + "/.s3cfg"
        self.assertEqual(len(self.deployment_provider.s3_config_files), 0)
        self.assertEqual(len(self.deployment_provider.s3_directories), 0)
        self.assertEqual(len(self.deployment_provider.s3_files), 0)

        self.assertEqual(len(self.amazon_provider.s3_files), 1)
        self.assertRegexpMatches(self.amazon_provider.s3_files["nri-bak-us"]["mongodb_core"][0], "mongodb_backup_test_db_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+\.tar\.gz")


        # verify cleanup
        self.assertEqual(len(self.file_provider.deleted_directories), 1)
        self.assertRegexpMatches(self.file_provider.deleted_directories[0], "mongodb_backup_test_db_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+")
        self.assertEqual(len(self.file_provider.deleted_files), 1)
        self.assertRegexpMatches(self.file_provider.deleted_files[0], "mongodb_backup_test_db_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+_(\d)+\.tar\.gz")

        # make sure no email sent
        self.assertIsNone(self.email_provider.to_email)
        self.assertIsNone(self.email_provider.from_email)
        self.assertIsNone(self.email_provider.subject)
        self.assertIsNone(self.email_provider.message)

    def test_backup_not_designated_backup_machine(self):
        def not_designated(name): return False
        self.deployment_provider.machine_is_designated_backer_upper = not_designated

        # go and don't do anything because it's not primary
        self.deployer.backup_and_upload_to_s3()

        # verify back ups never happened
        self.assertFalse(hasattr(self.deployment_provider, 'mongodb_host'))
        self.assertFalse(hasattr(self.deployment_provider, 'mongodb_database'))
        self.assertFalse(hasattr(self.deployment_provider, 'mongodb_username'))
        self.assertFalse(hasattr(self.deployment_provider, 'mongodb_password'))
        self.assertFalse(hasattr(self.deployment_provider, 'mongodb_output_file'))
        self.assertFalse(hasattr(self.deployment_provider, 'tar_filename'))
        self.assertFalse(hasattr(self.deployment_provider, 'tar_zipped_file_name'))

        # verify s3 uploads are not present
        expected_s3_config_file = os.getenv("HOME") + "/.s3cfg"
        self.assertEqual(len(self.deployment_provider.s3_config_files), 0)
        self.assertEqual(len(self.deployment_provider.s3_directories), 0)
        self.assertEqual(len(self.deployment_provider.s3_files), 0)

        # verify cleanup
        self.assertEqual(len(self.file_provider.deleted_directories), 0)
        self.assertEqual(len(self.file_provider.deleted_files), 0)

        # make sure no email sent
        self.assertIsNone(self.email_provider.to_email)
        self.assertIsNone(self.email_provider.from_email)
        self.assertIsNone(self.email_provider.subject)
        self.assertIsNone(self.email_provider.message)

    def test_error_sends_email(self):
        # update a method with an exception
        def exception():
            raise Exception("UNITTESTERROR")
        self.deployer._back_up_and_zip = exception

        # go
        self.deployer.backup_and_upload_to_s3()

        # make sure email sent
        self.assertEqual(self.email_provider.to_email, self.deployer.config['report_generator']['email_recipients_developers'])
        self.assertEqual(self.email_provider.from_email, "arnie@nexusri.com")
        self.assertEqual(self.email_provider.subject, "MongoDB Backup Error!!!")

        # make sure body contains the error
        self.assertIn("UNITTESTERROR", self.email_provider.message)


if __name__ == '__main__':
    unittest.main()
