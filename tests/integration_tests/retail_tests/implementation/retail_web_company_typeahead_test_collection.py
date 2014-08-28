from __future__ import division
import pprint
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from requests.cookies import RequestsCookieJar


__author__ = 'vgold'


class RetailWebCompanyTypeaheadTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "retail_web_companies_test_collection.py"
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
        print self.config["SECURITY_LOGIN_URL"]
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    ##------------------------------------ Retail Web Download File Tests ---------------------------------------##

    def retail_test_company_typeahead(self):

        cids1 = [
            insert_test_company(name="COMPANY %s" % i, workflow_status="published")
            for i in range(80)
        ]

        cids2 = [
            insert_test_company(name="COMPANY %s" % i)
            for i in range(81, 100)
        ]

        response = self.web_access.get('/api/company_typeahead?query=c', cookies=self.cooks).json()

        self.test_case.assertEqual(response["companies"]["meta"]["num_rows"], 80)
        self.test_case.assertEqual(response["companies"]["meta"]["page_size"], 10)


