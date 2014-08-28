from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from requests.cookies import RequestsCookieJar
from tests.integration_tests.utilities.data_access_misc_queries import *
import datetime


__author__ = 'vgold'


class CoreWebStoresTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "web_stores_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_test_user_get_cookies()

    def setUp(self):
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##

    def __login_test_user_get_cookies(self):

        params = {"email": "test@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    ##------------------------------------ User Admin Tests ---------------------------------------##

    def web_test_delete_orphaned_store(self):

        company_id = insert_test_company()
        store_id = insert_test_store(company_id, [datetime.datetime.utcnow(), None])

        results = self.web_access.delete("/api/retail_output/stores/%s" % store_id, "", cookies=self.cooks).json()

        self.test_case.assertEqual(results["status"], 200)
        self.test_case.assertIn("message", results)


