from tests.integration_tests.retail_tests.implementation.retail_client_controller_test_collection import RetailClientControllerTestCollection
from tests.integration_tests.retail_tests.implementation.retail_user_controller_test_collection import RetailUserControllerTestCollection
from tests.integration_tests.retail_tests.implementation.retail_web_prospects_test_collection import RetailWebProspectsTestCollection
from tests.integration_tests.retail_tests.implementation.retail_web_clients_test_collection import RetailWebClientsTestCollection
from tests.integration_tests.retail_tests.implementation.retail_web_surveys_test_collection import RetailWebSurveysTestCollection
from tests.integration_tests.retail_tests.implementation.retail_web_users_test_collection import RetailWebUsersTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from retail.v010.retail_app_runner import app as retail_web_app
from core.service.svc_master_data_storage.mds_api import app as mds_app
import unittest


class RetailControllersTests(ServiceTestCase):
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {
            "RETAIL_WEB": retail_web_app,
            "MDS": mds_app
        }
        cls.svc_key = "RETAIL_WEB"
        cls.test_colls = {
            "RETAIL_USER_CONTROLLER": RetailUserControllerTestCollection,
            "RETAIL_CLIENT_CONTROLLER": RetailClientControllerTestCollection,
            "RETAIL_WEB_CLIENTS": RetailWebClientsTestCollection,
            "RETAIL_WEB_USERS": RetailWebUsersTestCollection,
            "RETAIL_WEB_SURVEYS": RetailWebSurveysTestCollection,
            "RETAIL_WEB_PROSPECTS": RetailWebProspectsTestCollection
        }
        cls.svc_main_exempt = {}

    #-----------------------# RETAIL_USER_CONTROLLER #-----------------------#

    def test_create_user(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_create_user()

    def test_get_user(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_get_user()

    def test_get_user__case_insensitive(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_get_user__case_insensitive()

    def test_find_user(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_find_user()

    def test_find_user__case_insensitive(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_find_user__case_insensitive()

    def test_find_users(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_find_users()

    def test_update_user(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_update_user()

    def test_delete_user(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_delete_user()

    def test_create_role(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_create_role()

    def test_get_role(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_get_role()

    def test_find_role(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_find_role()

    def test_find_roles(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_find_roles()

    def test_update_role(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_update_role()

    def test_delete_role(self):
        self.tests["RETAIL_USER_CONTROLLER"].test_delete_role()

    #-----------------------# RETAIL_CLIENT_CONTROLLER #-----------------------#

    def test_create_client(self):
        self.tests["RETAIL_CLIENT_CONTROLLER"].test_create_client()

    def test_get_client(self):
        self.tests["RETAIL_CLIENT_CONTROLLER"].test_get_client()

    def test_find_client(self):
        self.tests["RETAIL_CLIENT_CONTROLLER"].test_find_client()

    def test_find_clients(self):
        self.tests["RETAIL_CLIENT_CONTROLLER"].test_find_clients()

    def test_update_client(self):
        self.tests["RETAIL_CLIENT_CONTROLLER"].test_update_client()

    def test_delete_client(self):
        self.tests["RETAIL_CLIENT_CONTROLLER"].test_delete_client()

    #-----------------------# RETAIL_WEB_CLIENTS #-----------------------#

    def test_retail_test_get_clients(self):
        self.tests["RETAIL_WEB_CLIENTS"].retail_test_get_clients()

    def test_retail_test_create_client(self):
        self.tests["RETAIL_WEB_CLIENTS"].retail_test_create_client()

    def test_retail_test_update_client(self):
        self.tests["RETAIL_WEB_CLIENTS"].retail_test_update_client()

    def test_retail_test_get_client(self):
        self.tests["RETAIL_WEB_CLIENTS"].retail_test_get_client()

    def test_retail_test_delete_client(self):
        self.tests["RETAIL_WEB_CLIENTS"].retail_test_delete_client()

    #-----------------------# RETAIL_WEB_USERS #-----------------------#

    def test_retail_test_get_session_user(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_get_session_user()

    def test_retail_test_update_session_user(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_update_session_user()

    def test_retail_test_update_user(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_update_user()

    def test_retail_test_get_users(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_get_users()

    def test_retail_test_get_user(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_get_user()

    def test_retail_test_delete_user(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_delete_user()

    def test_retail_test_create_user_and_reset_password_request(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_create_user_and_reset_password_request()

    def test_retail_test_create_user_and_reset_password_request__expired(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_create_user_and_reset_password_request__expired()

    def test_retail_test_user_forgot_password(self):
        self.tests["RETAIL_WEB_USERS"].retail_test_user_forgot_password()

    #-----------------------# RETAIL_WEB_SURVEYS #-----------------------#

    def test_retail_test_get_survey_list(self):
        self.tests["RETAIL_WEB_SURVEYS"].retail_test_get_survey_list()

    def test_retail_test_get_survey_detail(self):
        self.tests["RETAIL_WEB_SURVEYS"].retail_test_get_survey_detail()

    def test_retail_test_get_survey_questions_detail(self):
        self.tests["RETAIL_WEB_SURVEYS"].retail_test_get_survey_questions_detail()

    def test_retail_test_post_user_survey_response(self):
        self.tests["RETAIL_WEB_SURVEYS"].retail_test_post_user_survey_response()

    #-----------------------# RETAIL_WEB_PROSPECTS #-----------------------#

    def test_retail_test_create_prospect(self):
        self.tests["RETAIL_WEB_PROSPECTS"].retail_test_create_prospect()


if __name__ == '__main__':
    unittest.main()
