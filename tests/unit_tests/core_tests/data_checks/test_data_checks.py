from bson.objectid import ObjectId
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency
from core.data_checks.main_data_checker import DataChecker
from common.utilities.date_utilities import format_timedelta, FastDateParser
from core.data_checks import base_data_check
from common.helpers import email_provider
from mox import IsA
import datetime
import unittest
import time
import mox
import os


__author__ = 'erezrubinstein'


class TestDataChecks(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestDataChecks, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.mock_mds_db = self.mox.CreateMockAnything()
        self.mock_mds_db.company = self.mox.CreateMockAnything()
        self.mock_mds_db.labor = self.mox.CreateMockAnything()

        self.data_checker = self.mox.CreateMock(DataChecker)
        self.data_checker.format_timedelta = format_timedelta

        self.data_checker.company_only = False
        self.data_checker.global_only = False
        self.data_checker.no_email = False
        self.data_checker.current_directory = "/"
        self.data_checker.test_mode = False
        self.data_checker.crap = -1
        self.data_checker.company_ids = []
        self.data_checker.update_companies = False
        self.data_checker.email_to_override = None
        self.data_checker.mds_db = self.mock_mds_db
        self.data_checker.simple_console = Dependency("FlaskLogger").value
        self.data_checker.date_parser = None

    def doCleanups(self):

        # call parent clean up
        super(TestDataChecks, self).doCleanups()

    def test_run__success(self):

        # create mocks
        mock_global_results = "woot"
        mock_company_results = "chicken"

        # stub out methods
        self.mox.StubOutWithMock(datetime, "datetime")
        self.mox.StubOutWithMock(os.path, "join")
        self.mox.StubOutWithMock(os.path, "exists")

        self.data_checker.format_timedelta = self.mox.CreateMockAnything()

        # begin recording
        os.path.join(mox.IgnoreArg(), mox.IgnoreArg()).AndReturn("asdf")
        os.path.exists("asdf").AndReturn(True)

        datetime.datetime.utcnow().AndReturn(1)

        datetime.datetime.utcnow().AndReturn(10)
        self.data_checker._run_global_checks().AndReturn(mock_global_results)
        datetime.datetime.utcnow().AndReturn(11)
        self.data_checker.format_timedelta(1)

        datetime.datetime.utcnow().AndReturn(20)
        self.data_checker._run_company_checks().AndReturn(mock_company_results)
        datetime.datetime.utcnow().AndReturn(21)
        self.data_checker.format_timedelta(1)

        datetime.datetime.utcnow().AndReturn(2)
        self.data_checker.format_timedelta(1).AndReturn(1)
        self.data_checker._create_report_html(mock_global_results, mock_company_results, 1)
        self.data_checker._send_email()
        self.data_checker.to_dict()

        # replay All
        self.mox.ReplayAll()

        # l'chaim
        DataChecker.run(self.data_checker)

    def test_run__failure(self):

        # create mocks
        mock_global_results = "woot"
        mock_exception = Exception("chicken")

        # raise Exception side effect
        def raise_exception_side_effect():
            raise mock_exception

        # stub out methods
        self.mox.StubOutWithMock(datetime, "datetime")
        self.mox.StubOutWithMock(os.path, "join")
        self.mox.StubOutWithMock(os.path, "exists")

        self.data_checker.format_timedelta = self.mox.CreateMockAnything()

        # begin recording
        os.path.join(mox.IgnoreArg(), mox.IgnoreArg()).AndReturn("asdf")
        os.path.exists("asdf").AndReturn(True)

        datetime.datetime.utcnow().AndReturn(1)

        datetime.datetime.utcnow().AndReturn(10)
        self.data_checker._run_global_checks().AndReturn(mock_global_results)
        datetime.datetime.utcnow().AndReturn(11)
        self.data_checker.format_timedelta(1)

        datetime.datetime.utcnow().AndReturn(20)
        self.data_checker._run_company_checks().WithSideEffects(raise_exception_side_effect)

        # replay All
        self.mox.ReplayAll()

        # l'chaim
        with self.assertRaises(Exception):
            DataChecker.run(self.data_checker)

    def test_run_global_check(self):

        # mock results
        result_1 = "woot"
        result_2 = "chicken"
        release = "global"

        # stub out methods / classes
        self.mox.StubOutClassWithMocks(base_data_check, "BaseDataCheck")

        # add some mock data checks
        self.data_checker.global_data_checks = [base_data_check.BaseDataCheck, base_data_check.BaseDataCheck]

        # begin recording
        data_check_1 = base_data_check.BaseDataCheck(self.mock_mds_db, self.data_checker.date_parser)
        self.data_checker._should_run_check(data_check_1).AndReturn(True)
        self.data_checker._run_individual_data_check(release, data_check_1).AndReturn(result_1)
        data_check_2 = base_data_check.BaseDataCheck(self.mock_mds_db, self.data_checker.date_parser)
        self.data_checker._should_run_check(data_check_2).AndReturn(True)
        self.data_checker._run_individual_data_check(release, data_check_2).AndReturn(result_2)

        # replay All
        self.mox.ReplayAll()

        # run!
        results = DataChecker._run_global_checks(self.data_checker)

        # make sure results are correct
        self.assertEqual(results, [result_1, result_2])

    def test_run_company_checks(self):

        # mock results
        result_1 = {"result": "woot"}
        result_2 = {"result": "woot"}
        result_3 = {"result": "woot"}
        result_4 = {"result": "woot"}
        result_5 = {"result": "woot"}
        company_id_1 = "1"
        company_id_2 = "2"
        company_id_3 = "3"
        company_name_1 = "Borat"
        company_name_2 = "Sagdiyev"
        company_name_3 = "Helomoto"
        company1 = {"_id": company_id_1, "name": company_name_1}
        company2 = {"_id": company_id_2, "name": company_name_2}
        company3 = {"_id": company_id_3, "name": company_name_3}
        mock_companies = [
            company1,
            company2,
            company3
        ]
        published_company_set = {str(company_id_1), str(company_id_2), str(company_id_3)}
        extra_data = {
            "min_unemployment_rate": 0,
            "max_unemployment_rate": 50
        }
        release_status = "release"
        pre_release_status = "pre_release"

        # stub out methods / classes
        self.mox.StubOutClassWithMocks(base_data_check, "BaseCompanyDataCheck")

        base_data_check.BaseCompanyDataCheck.engine_validity_keys = ["helo", "moto"]

        # add some mock data checks
        self.data_checker.release_company_data_checks = [
            base_data_check.BaseCompanyDataCheck
        ]
        self.data_checker.pre_release_company_data_checks = [
            base_data_check.BaseCompanyDataCheck
        ]

        # begin recording
        self.data_checker._get_companies_and_count().AndReturn((mock_companies, 2))
        self.data_checker._get_extra_data().AndReturn(extra_data)

        self.data_checker._check_if_company_has_ever_run_plan_b(company1).AndReturn(None)

        self.mock_mds_db.company.find({"data.workflow.current.status": "published"}, {"_id": 1}).AndReturn(mock_companies)

        self.data_checker._get_result_of_data_checks(release_status, self.data_checker.release_company_data_checks, company1,
                                                     published_company_set, extra_data).AndReturn(([result_1], {}))

        self.data_checker._get_result_of_data_checks(pre_release_status, self.data_checker.pre_release_company_data_checks, company1,
                                                     published_company_set, extra_data).AndReturn(([result_2], None))

        self.data_checker._check_if_company_has_ever_run_plan_b(company2).AndReturn(None)

        self.mock_mds_db.company.find({"data.workflow.current.status": "published"}, {"_id": 1}).AndReturn(mock_companies)

        self.data_checker._get_result_of_data_checks(release_status, self.data_checker.release_company_data_checks,
                                                     company2, published_company_set, extra_data).AndReturn(([result_3], {}))

        self.data_checker._get_result_of_data_checks(pre_release_status, self.data_checker.pre_release_company_data_checks, company2,
                                                     published_company_set, extra_data).AndReturn(([result_4], None))

        self.data_checker._check_if_company_has_ever_run_plan_b(company3).AndReturn(result_5)

        # replay All
        self.mox.ReplayAll()

        # run!
        checker_results = DataChecker._run_company_checks(self.data_checker)

        # make sure results are correct
        expected_results = [result_1, result_2, result_3, result_4, result_5]
        self.assertListEqual(checker_results, expected_results)
        self.assertAlmostEqual(self.data_checker.num_companies, 2)

    def test_run_company_checks__update_companies(self):

        self.data_checker.update_companies = True

        # mock results
        result_1 = {"result": "woot"}
        result_2 = {"result": "woot"}
        result_3 = {"result": "FAILURE"}
        result_4 = {"result": "FAILURE"}
        company_id_1 = "1"
        company_id_2 = "2"
        company_name_1 = "Borat"
        company_name_2 = "Sagdiyev"
        company1 = {"_id": company_id_1, "name": company_name_1}
        company2 = {"_id": company_id_2, "name": company_name_2}
        mock_companies = [
            company1,
            company2
        ]
        published_company_set = {str(company_id_1), str(company_id_2)}
        extra_data = {
            "min_unemployment_rate": 0,
            "max_unemployment_rate": 50
        }
        release_status = "release"
        pre_release_status = "pre_release"

        # stub out methods / classes
        self.mox.StubOutClassWithMocks(base_data_check, "BaseCompanyDataCheck")

        base_data_check.BaseCompanyDataCheck.engine_validity_keys = ["helo", "moto"]

        # add some mock data checks
        self.data_checker.release_company_data_checks = [
            base_data_check.BaseCompanyDataCheck
        ]
        self.data_checker.pre_release_company_data_checks = [
            base_data_check.BaseCompanyDataCheck
        ]

        # begin recording
        self.data_checker._get_companies_and_count().AndReturn((mock_companies, 2))
        self.data_checker._get_extra_data().AndReturn(extra_data)

        self.data_checker._check_if_company_has_ever_run_plan_b(company1).AndReturn(None)

        self.mock_mds_db.company.find({"data.workflow.current.status": "published"}, {"_id": 1}).AndReturn(mock_companies)

        self.data_checker._get_result_of_data_checks(release_status, self.data_checker.release_company_data_checks, company1,
                                                     published_company_set, extra_data).AndReturn(([result_1], {}))

        self.data_checker._update_company_analytics_validity(company_id_1, {})

        self.data_checker._get_result_of_data_checks(pre_release_status, self.data_checker.pre_release_company_data_checks, company1,
                                                     published_company_set, extra_data).AndReturn(([result_2], None))

        self.data_checker._check_if_company_has_ever_run_plan_b(company2).AndReturn(None)

        self.mock_mds_db.company.find({"data.workflow.current.status": "published"}, {"_id": 1}).AndReturn(mock_companies)

        self.data_checker._get_result_of_data_checks(release_status, self.data_checker.release_company_data_checks,
                                                     company2, published_company_set, extra_data).AndReturn(([result_3], {}))

        self.data_checker._update_company_analytics_validity(company_id_2, {})

        self.data_checker._get_result_of_data_checks(pre_release_status, self.data_checker.pre_release_company_data_checks, company2,
                                                     published_company_set, extra_data).AndReturn(([result_4], None))

        # replay All
        self.mox.ReplayAll()

        # run!
        results = DataChecker._run_company_checks(self.data_checker)

        # make sure results are correct
        self.assertEqual(results, [result_1, result_2, result_3, result_4])
        self.assertAlmostEqual(self.data_checker.num_companies, 2)

    def test_check_if_company_has_ever_run_plan_b__true(self):

        mock_company = {
            "data": {
                "workflow": {
                    "analytics": {
                        "plan_b_has_run": True
                    }
                }
            }
        }

        # replay All
        self.mox.ReplayAll()

        results = DataChecker._check_if_company_has_ever_run_plan_b(self.data_checker, mock_company)

        self.assertEqual(results, None)

    def test_check_if_company_has_ever_run_plan_b__false(self):

        mock_company = {
            "_id": "helo",
            "name": "moto",
            "data": {
                "workflow": {
                    "analytics": {
                        "plan_b_has_run": False
                    }
                }
            }
        }

        self.data_checker._format_data_check_result("prerequisite", "Make sure company has ever run Plan B.",
                                                    "FAILURE", "Missing key data.workflow.analytics.plan_b_has_run",
                                                    str(mock_company["_id"]), mock_company["name"]).AndReturn("HIYA!")

        # replay All
        self.mox.ReplayAll()

        results = DataChecker._check_if_company_has_ever_run_plan_b(self.data_checker, mock_company)

        self.assertEqual(results, "HIYA!")

    def test_check_if_company_has_ever_run_plan_b__none(self):

        mock_company = {
            "_id": "helo",
            "name": "moto"
        }

        self.data_checker._format_data_check_result("prerequisite", "Make sure company has ever run Plan B.",
                                                    "FAILURE", "Missing key data.workflow.analytics.plan_b_has_run",
                                                    str(mock_company["_id"]), mock_company["name"]).AndReturn("HIYA!")

        # replay All
        self.mox.ReplayAll()

        results = DataChecker._check_if_company_has_ever_run_plan_b(self.data_checker, mock_company)

        self.assertEqual(results, "HIYA!")

    def test_get_result_of_data_checks__succeed(self):

        result_1 = {"result": "woot"}
        result_2 = {"result": "woot"}
        company_id_1 = "1"
        company_name_1 = "Borat"
        company1 = {"_id": company_id_1, "name": company_name_1}
        published_company_set = {str(company_id_1)}
        extra_data = {
            "min_unemployment_rate": 0,
            "max_unemployment_rate": 50
        }
        release_status = "release"

        # stub out methods / classes
        self.mox.StubOutClassWithMocks(base_data_check, "BaseCompanyDataCheck")

        # add some mock data checks
        company_data_checks = [
            base_data_check.BaseCompanyDataCheck,
            base_data_check.BaseCompanyDataCheck
        ]

        # begin recording
        data_check_1 = base_data_check.BaseCompanyDataCheck(self.mock_mds_db, company1, published_company_set, extra_data, self.data_checker.date_parser)
        data_check_1.engine_validity_keys = ["helo"]
        self.data_checker._should_run_check(data_check_1).AndReturn(True)
        self.data_checker._run_individual_data_check(release_status, data_check_1, company_id_1, company_name_1).AndReturn(result_1)

        data_check_2 = base_data_check.BaseCompanyDataCheck(self.mock_mds_db, company1, published_company_set, extra_data, self.data_checker.date_parser)
        data_check_2.engine_validity_keys = ["moto"]
        self.data_checker._should_run_check(data_check_2).AndReturn(True)
        self.data_checker._run_individual_data_check(release_status, data_check_2, company_id_1, company_name_1).AndReturn(result_2)

        # replay All
        self.mox.ReplayAll()

        # run!
        results, company_validity_dict = DataChecker._get_result_of_data_checks(self.data_checker, release_status,
                                                                                company_data_checks, company1,
                                                                                published_company_set, extra_data)

        # make sure results are correct
        self.assertListEqual(results, [result_1, result_2])
        self.assertDictEqual(company_validity_dict, {
            "helo": True,
            "moto": True
        })

    def test_get_result_of_data_checks__fail(self):

        result_1 = {"result": "FAILURE"}
        result_2 = {"result": "woot"}
        company_id_1 = "1"
        company_name_1 = "Borat"
        company1 = {"_id": company_id_1, "name": company_name_1}
        published_company_set = {str(company_id_1)}
        extra_data = {
            "min_unemployment_rate": 0,
            "max_unemployment_rate": 50
        }
        release_status = "release"

        # stub out methods / classes
        self.mox.StubOutClassWithMocks(base_data_check, "BaseCompanyDataCheck")

        # add some mock data checks
        company_data_checks = [
            base_data_check.BaseCompanyDataCheck,
            base_data_check.BaseCompanyDataCheck
        ]

        # begin recording
        data_check_1 = base_data_check.BaseCompanyDataCheck(self.mock_mds_db, company1, published_company_set, extra_data, self.data_checker.date_parser)
        data_check_1.engine_validity_keys = ["helo"]
        self.data_checker._should_run_check(data_check_1).AndReturn(True)
        self.data_checker._run_individual_data_check(release_status, data_check_1, company_id_1, company_name_1).AndReturn(result_1)

        data_check_2 = base_data_check.BaseCompanyDataCheck(self.mock_mds_db, company1, published_company_set, extra_data, self.data_checker.date_parser)
        data_check_2.engine_validity_keys = ["moto"]
        self.data_checker._should_run_check(data_check_2).AndReturn(True)
        self.data_checker._run_individual_data_check(release_status, data_check_2, company_id_1, company_name_1).AndReturn(result_2)

        # replay All
        self.mox.ReplayAll()

        # run!
        results, company_validity_dict = DataChecker._get_result_of_data_checks(self.data_checker, release_status,
                                                                                company_data_checks, company1,
                                                                                published_company_set, extra_data)

        # make sure results are correct
        self.assertListEqual(results, [result_1, result_2])
        self.assertDictEqual(company_validity_dict, {
            "helo": False,
            "moto": True
        })

    def test_run_individual_data_check__success(self):

        # mock results
        mock_data_check = self.mox.CreateMock(base_data_check.BaseDataCheck)
        mock_name = "homer (not the Greek poet)"
        release = "release"
        mock_data_check.engine_validity_keys = ["helo", "moto"]

        self.mox.StubOutWithMock(time, 'time')

        # begin recording
        time.time().AndReturn(1)
        mock_data_check.check().AndReturn(True)
        time.time().AndReturn(2)
        mock_data_check.data_check_name().AndReturn(mock_name)
        self.data_checker._format_data_check_result(release, mock_name, "SUCCESS", mox.IsA(basestring), 1, None, 1,
                                                    validity_keys=["helo", "moto"]).AndReturn(None)

        # replay all
        self.mox.ReplayAll()

        # run
        results = DataChecker._run_individual_data_check(self.data_checker, release, mock_data_check, 1)

        # make sure results are correct
        self.assertEqual(results, None)

    def test_run_individual_data_check__failure(self):

        # mock results
        mock_data_check = self.mox.CreateMock(base_data_check.BaseDataCheck)
        mock_name = "homer (not the Greek poet)"
        mock_error_message = "woot"
        release = "release"
        mock_data_check.engine_validity_keys = ["helo", "moto"]
        mock_data_check.failure_difference = {}

        self.mox.StubOutWithMock(time, 'time')

        # begin recording
        time.time().AndReturn(1)
        mock_data_check.check().AndReturn(False)
        time.time().AndReturn(2)
        mock_data_check.data_check_name().AndReturn(mock_name)
        mock_data_check.error_message = mock_error_message
        self.data_checker._format_data_check_result(release, mock_name, "FAILURE", mox.IsA(basestring), 1, None, 1,
                                                    failure_difference=mock_data_check.failure_difference,
                                                    validity_keys=["helo", "moto"]).AndReturn(None)

        # replay all
        self.mox.ReplayAll()

        # run
        results = DataChecker._run_individual_data_check(self.data_checker, release, mock_data_check, 1)

        # make sure results are correct
        self.assertEqual(results, None)

    def test_run_individual_data_check__error(self):

        # mock results
        mock_data_check = self.mox.CreateMock(base_data_check.BaseDataCheck)
        mock_error_message = "woot"
        release = "release"
        mock_data_check.engine_validity_keys = ["helo", "moto"]

        # create exception side effect method
        def exception_side_effect():
            raise Exception(mock_error_message)

        # begin recording
        mock_data_check.data_check_name().WithSideEffects(exception_side_effect)
        self.data_checker._format_data_check_result(release, str(mock_data_check), "ERROR", mox.IsA(basestring), 1,
                                                    None, validity_keys=["helo", "moto"]).AndReturn(None)

        # replay all
        self.mox.ReplayAll()

        # run
        results = DataChecker._run_individual_data_check(self.data_checker, release, mock_data_check, 1)

        # make sure results are correct
        self.assertEqual(results, None)

    def test_update_company_analytics_validity(self):

        cid1 = ObjectId()
        valid_dict = {
            "helo": True,
            "moto": False
        }

        query = {"_id": cid1}
        update = {
            "$set": {
                "data.valid.v1_2.analytics.helo": True,
                "data.valid.v1_2.analytics.moto": False
            }
        }
        self.data_checker.mds_db.company.update(query, update)

        self.mox.ReplayAll()

        DataChecker._update_company_analytics_validity(self.data_checker, cid1, valid_dict)

    def test_send_email(self):

        # mock data
        self.data_checker.report = "<bold>It's all about the Pentiums, baby</bold>"
        self.data_checker.num_companies = 12
        mock_file_name = "jack_handy.py"

        # stub out stuff
        self.mox.StubOutClassWithMocks(email_provider, "EmailProvider")

        # begin recording
        mock_email_provider = email_provider.EmailProvider("smtp.1and1.com", "support@signaldataco.com",
                                                           "Signal_iguana_goat_now_1")
        self.data_checker._upload_report_to_s3(self.data_checker.report).AndReturn(mock_file_name)
        mock_email_provider.send_email("korki_buchek@signalDaTaco.com", ["engineering@signalDaTaco.com"],
                                       "Taco Delivery (12)", IsA(basestring))

        # replay all
        self.mox.ReplayAll()

        # run
        DataChecker._send_email(self.data_checker)

    def _format_data_check_result(self, data_check_name, result, error_message, entity_id=None, entity_name=None,
                                  timing_seconds=None):

        return {
            "data_check_name": data_check_name,
            "result": result,
            "error_message": error_message,
            "entity_id": str(entity_id),
            "entity_name": entity_name,
            "timing_seconds": round(timing_seconds, 3) if timing_seconds is not None else None,
        }


if __name__ == '__main__':
    unittest.main()
