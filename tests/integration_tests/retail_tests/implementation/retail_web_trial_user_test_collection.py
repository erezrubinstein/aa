from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from requests.cookies import RequestsCookieJar
import cStringIO


__author__ = 'jsternberg'


class RetailWebTrialUserTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "retail_web_companies_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_trial_user_get_cookies()

    def setUp(self):
        self.rds_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##

    def __login_trial_user_get_cookies(self):
        params = {"email": "trial@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    ##------------------------------------ Retail Web Download File Tests ---------------------------------------##

    def retail_test_download_full_report_by_trial_user(self):

        test_file_path = "platform_research_reports"
        test_filename = "respect.txt"
        test_file_content = "Respect My Athorta!"
        test_file = cStringIO.StringIO(test_file_content)

        result = self.rds_access.call_post_file(test_file_path, {test_filename: test_file}, self.context)
        rds_file_id = result.values()[0]

        file_data = {
            "rds_file_id": rds_file_id,
            "report_type": "full_report"
        }
        mds_result = self.mds_access.call_add_entity("file", test_filename, file_data, self.context)
        self.test_case.assertIsNot(mds_result, None)

        # this should return HTTP 401, Not Authorized
        response = self.web_access.get('/api/files/download/%s' % rds_file_id, cookies=self.cooks, stream=True)
        self.test_case.assertFalse(response.ok)
        self.test_case.assertEqual(response.status_code, 401)
