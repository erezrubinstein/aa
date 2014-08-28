from datetime import datetime, timedelta
import unittest
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from infrastructure.backup.back_up_mongo_db_verifier import MongoDBBackupVerifier

__author__ = 'erezrubinstein'

class MongoDBBackupTests(unittest.TestCase):
    def setUp(self):
        # set up mocks
        register_common_mock_dependencies()

        # get dependencies
        self.aws_provider = Dependency("CloudProvider").value
        self.mongodb_provider = Dependency("MongoDBProvider").value
        self.email_provider = Dependency("EmailProvider").value

        # logger
        logger = Dependency("SimpleConsole").value

        # set up verifier object
        self.verifier = MongoDBBackupVerifier(logger=logger)


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_initialization(self):
        """
        Verify that various variables are set up correctly
        """
        self.assertEqual(self.verifier.s3_bucket, "nri-bak-us")
        self.assertEqual(self.verifier.backup_file_prefix, "mongodb_core")
        self.assertEqual(self.verifier.backup_frequency, 12)
        self.assertEqual(self.verifier.backups_to_verify, [])


    def test_find_prod_dbs(self):
        # mock db names
        self.mongodb_provider.db_names = ["prod_test", "test", "dev_test", "prod_chicken"]

        # get prod dbs
        self.verifier._find_prod_dbs()

        # make sure only "prod_" dbs were found
        self.assertEqual(len(self.verifier.backups_to_verify), 2)
        self.assertIn("prod_test", self.verifier.backups_to_verify)
        self.assertIn("prod_chicken", self.verifier.backups_to_verify)


    def test_get_mongo_db_backup_files(self):
        """
        Test to make sure the right aws_method is called
        """
        # mock files
        expected_files = ["chicken", "woot", "danger_zone"]
        self.aws_provider.s3_files["nri-bak-us"]["mongodb_core"] = expected_files

        # verify we're getting the right files
        files = self.verifier._get_mongo_db_backup_files()
        self.assertEqual(files, expected_files)


    def test_parse_file_dates_and_filter(self):
        """
        Make sure filenames can be parsed correctly
        """
        # create files
        files = ["test_does_not_parse", "mongodb_core/mongodb_backup_test_mds_2013_03_20_21_12_02.tar.gz", "mongodb_core/mongodb_backup_test_prod_core_2013_05_20_07_00_02.tar.gz"]

        # get backups
        backups = self.verifier._parse_files_into_backups(files)

        # verify
        self.assertEqual(len(backups), 2)
        self.assertEqual(backups[0].db_name, "test_mds")
        self.assertEqual(backups[0].date, datetime(2013, 3, 20, 21, 12, 2))
        self.assertEqual(backups[1].db_name, "test_prod_core")
        self.assertEqual(backups[1].date, datetime(2013, 5, 20, 7, 0, 2))


    def test_filter_backups_to_last_x_hours__two_good_dbs(self):
        # create several good dates
        now = datetime.utcnow()
        good_date_1 = (now - timedelta(hours = 1)).strftime('%Y_%m_%d_%H_%M_%S')
        good_date_2 = (now - timedelta(hours = 1.5)).strftime('%Y_%m_%d_%H_%M_%S')
        bad_date_1 = (now - timedelta(hours = 8)).strftime('%Y_%m_%d_%H_%M_%S')
        bad_date_2 = (now - timedelta(hours = 8.5)).strftime('%Y_%m_%d_%H_%M_%S')

        # create files (one good, one bad per db)
        files = ["mongodb_core/mongodb_backup_core_%s.tar.gz" % bad_date_1, "mongodb_core/mongodb_backup_core_%s.tar.gz" % good_date_1,
                 "mongodb_core/mongodb_backup_mds_%s.tar.gz" % bad_date_2, "mongodb_core/mongodb_backup_mds_%s.tar.gz" % good_date_2]

        # get backup objects
        backups = self.verifier._parse_files_into_backups(files)
        good_backups = self.verifier._filter_backups_to_last_x_hours(2, backups)

        # verify
        self.assertEqual(len(good_backups), 2)
        self.assertEqual(good_backups["core"].strftime('%Y_%m_%d_%H_%M_%S'), good_date_1)
        self.assertEqual(good_backups["mds"].strftime('%Y_%m_%d_%H_%M_%S'), good_date_2)


    def test_filter_backups_to_last_x_hours__one_good_one_bad_db(self):
        # create several good dates
        now = datetime.utcnow()
        good_date_1 = (now - timedelta(hours = 1)).strftime('%Y_%m_%d_%H_%M_%S')
        bad_date_1 = (now - timedelta(hours = 8)).strftime('%Y_%m_%d_%H_%M_%S')
        bad_date_2 = (now - timedelta(hours = 8.5)).strftime('%Y_%m_%d_%H_%M_%S')

        # create files (one good, one bad per db)
        files = ["mongodb_core/mongodb_backup_core_%s.tar.gz" % bad_date_1, "mongodb_core/mongodb_backup_core_%s.tar.gz" % good_date_1,
                 "mongodb_core/mongodb_backup_mds_%s.tar.gz" % bad_date_1, "mongodb_core/mongodb_backup_mds_%s.tar.gz" % bad_date_2]

        # get backup objects
        backups = self.verifier._parse_files_into_backups(files)
        good_backups = self.verifier._filter_backups_to_last_x_hours(2, backups)

        # verify
        self.assertEqual(len(good_backups), 1)
        self.assertEqual(good_backups["core"].strftime('%Y_%m_%d_%H_%M_%S'), good_date_1)


    def test_verify_all_dbs_backed_up__missing_dbs(self):
        # mock set of dbs
        self.verifier.backups_to_verify = ["core", "prod_mds", "prod_rds", "prod_entity_matcher", "prod_main", "prod_wfs"]

        # create list of backed up dbs (mds should be prod_mds.  this is on purpose)
        good_dbs = {
            "core": datetime.utcnow(),
            "prod_wfs": datetime.utcnow(),
            "mds": datetime.utcnow()
        }

        # get list of dbs not backed
        bad_dbs = self.verifier._get_databases_not_backed_up(good_dbs)

        # make sure we're missing some.  Assume we're looking for the 6 main dbs.
        self.assertEqual(len(bad_dbs), 4)
        self.assertEqual({ "prod_mds", "prod_rds", "prod_entity_matcher", "prod_main" }, set(bad_dbs))


    def test_verify_all_dbs_backed_up__all_good(self):
        # create list of backed up dbs (mds should be prod_mds.  this is on purpose)
        good_dbs = {
            "core": datetime.utcnow(),
            "prod_wfs": datetime.utcnow(),
            "prod_mds": datetime.utcnow(),
            "prod_main": datetime.utcnow(),
            "prod_rds": datetime.utcnow(),
            "prod_entity_matcher": datetime.utcnow()
        }

        # get list of dbs not backed
        bad_dbs = self.verifier._get_databases_not_backed_up(good_dbs)

        # make sure we're missing some.  Assume we're looking for the 6 main dbs.
        self.assertEqual(len(bad_dbs), 0)


    def test_email_if_missing_dbs(self):
        # get html
        html, subject = self.verifier._get_missing_backups_email_html(["chicken", "woot"])

        # assert various parts are there
        self.assertGreater(len(html), 20)
        self.assertIn("<bold>Mongodb Backups Missing!</bold>", html)
        self.assertIn("Backups are missing for the following databases:", html)
        self.assertIn("<td bgcolor=red>chicken</td>", html)
        self.assertIn("<td bgcolor=red>woot</td>", html)


    def test_entire_run__missing_dbs(self):
        # mock prod dbs
        self.mongodb_provider.db_names = ["prod_woot", "prod_chicken", "prod_danger_zone", "prod_never_gonna"]

        # bad date
        hours_behind = 80
        bad_date = datetime.utcnow() - timedelta(hours = hours_behind)
        bad_backup_time = bad_date.strftime("%m %d, %H:%M (UTC)")
        bad_date_string = bad_date.strftime('%Y_%m_%d_%H_%M_%S')

        # bad date2
        hours_behind2 = 12
        bad_date2 = datetime.utcnow() - timedelta(hours = hours_behind2)
        bad_backup_time2 = bad_date2.strftime("%m %d, %H:%M (UTC)")
        bad_date_string2 = bad_date2.strftime('%Y_%m_%d_%H_%M_%S')

        # mock file for one db
        self.aws_provider.s3_files["nri-bak-us"]["mongodb_core"] = ["mongodb_core/mongodb_backup_prod_woot_%s.tar.gz" % datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S'),
                                                                    "mongodb_core/mongodb_backup_prod_danger_zone_%s.tar.gz" % bad_date_string,
                                                                    "mongodb_core/mongodb_backup_prod_never_gonna_%s.tar.gz" % bad_date_string2]

        # bomboj for
        self.verifier.start()

        # make sure we get email that one db is missing
        self.assertEqual(self.email_provider.html_from_email, "arnie@nexusri.com")
        self.assertEqual(self.email_provider.html_to_email, ["engineering@signaldataco.com"])
        self.assertEqual(self.email_provider.html_subject, "Mongodb Backups Missing! %s hours behind!" % hours_behind)

        # make sure good database is not in email and bad databases are (with correct times)
        self.assertIn("<td bgcolor=red>prod_chicken</td> <td bgcolor=red>never</td> <td bgcolor=red>No time</td>", self.email_provider.html_message)
        self.assertIn("<td bgcolor=red>prod_danger_zone</td> <td bgcolor=red>%s hrs, 0 min ago</td> <td bgcolor=red>%s</td>" % (hours_behind, bad_backup_time), self.email_provider.html_message)
        self.assertIn("<td bgcolor=yellow>prod_never_gonna</td> <td bgcolor=yellow>%s hrs, 0 min ago</td> <td bgcolor=yellow>%s</td>" % (hours_behind2, bad_backup_time2), self.email_provider.html_message)
        self.assertNotIn("prod_woot", self.email_provider.html_message)


    def test_entire_run__all_ok(self):
        # mock prod dbs
        self.mongodb_provider.db_names = ["prod_woot", "prod_chicken"]

        # mock file for both dbs
        self.aws_provider.s3_files["nri-bak-us"]["mongodb_core"] = ["mongodb_core/mongodb_backup_prod_woot_%s.tar.gz" % datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S'),
                                                                    "mongodb_core/mongodb_backup_prod_chicken_%s.tar.gz" % datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')]

        # bomboj for
        self.verifier.start()

        # make sure we get no email, since all is good!
        self.assertIsNone(self.email_provider.html_from_email)
        self.assertIsNone(self.email_provider.html_to_email)
        self.assertIsNone(self.email_provider.html_subject)
        self.assertIsNone(self.email_provider.html_message)


    def test_error_email_on_exception(self):
        # create fake method that always raises an exception
        def exception_method():
            raise Exception("Woot/Chicken/Danger-Zone!!")

        # mock one method to always raise exception
        self.verifier._find_prod_dbs = exception_method

        # bomboj for
        self.verifier.start()

        # verify the error email was sent
        self.assertEqual(self.email_provider.html_from_email, "arnie@nexusri.com")
        self.assertEqual(self.email_provider.html_to_email, ["engineering@signaldataco.com"])
        self.assertEqual(self.email_provider.html_subject, "Mongodb Backups Verification Error!")

        # chicken is missing and woot is good
        self.assertIn("Woot/Chicken/Danger-Zone!!", self.email_provider.html_message)

if __name__=="__main__":
    unittest.main()