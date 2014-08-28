from __future__ import division
import pprint
from common.service_access.utilities.rec_helpers import is_rec_match
from common.utilities.inversion_of_control import Dependency
from core.web.implementation.core_entity_models import User
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from requests.cookies import RequestsCookieJar

from core.common.utilities.errors import *
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company

__author__ = 'jsternberg'

###################################################################################################

class CoreWebExportTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "web_export_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_test_user_get_cookies()

    def setUp(self):
        self.mds_access.call_delete_reset_database()
        self.main_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##

    def __login_test_user_get_cookies(self):

        params = {"email": "test@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok == True
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    ##------------------------------------ User Admin Tests ---------------------------------------##

    def web_test_get_export_companies_content(self):

        insert_test_company()
        insert_test_company()
        insert_test_company()

        results = self.web_access.get("/api/export/-export-preset-companies", cookies=self.cooks).json()

        self.test_case.assertIn("meta", results)
        self.test_case.assertIn("field_list", results)
        self.test_case.assertIn("field_meta", results)
        self.test_case.assertIn("id_field", results)
        self.test_case.assertIn("id_index", results)
        self.test_case.assertEqual(len(results["results"]), 3)

    def web_test_get_export_companies_csv(self):

        insert_test_company()
        insert_test_company()
        insert_test_company()

        results = self.web_access.get('/api/export/-export-preset-companies?params={"contentType":"csv"}', cookies=self.cooks)

        self.test_case.assertEqual(results.headers["content-type"], "application/csv")

