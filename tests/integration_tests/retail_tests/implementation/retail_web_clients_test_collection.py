from __future__ import division
from retail.v010.data_access.controllers.client_controller import ClientController
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from requests.cookies import RequestsCookieJar
import uuid
import json


class RetailWebClientsTestCollection(ServiceTestCollection):

    test_client_counter = 0

    # Random number to avoid interfering with other test collections in the same suite
    test_client_start = 100

    def initialize(self):
        self.client_controller = ClientController()
        self.json_headers = {"accept": "application/json", "content-type": "application/json"}

        self.__get_default_users()
        self.admin_cooks = self.__login_test_user_get_cookies(self.user_test.email, self.config["TEST_USER_PASSWORD"])
        self.client_support_cooks = self.__login_test_user_get_cookies(self.user_client_support.email, self.config["TEST_USER_PASSWORD"])
        self.user_cooks = self.__login_test_user_get_cookies(self.user_normal.email, self.config["TEST_USER_PASSWORD"])

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def increment_test_client_counter(cls):
        cls.test_client_counter += 1

    ##------------------------------------ Private helpers --------------------------------------##

    def __login_test_user_get_cookies(self, email, password):
        params = {"email": email, "password": password}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params, time_out=1000)
        assert response.ok and isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    def __get_default_users(self):
        self.user_test = self.client_controller.User.get("test@nexusri.com")
        self.user_client_support = self.client_controller.User.get("client_support@nexusri.com")
        self.user_normal = self.client_controller.User.get("user@nexusri.com")

    def __create_test_client(self, actor_email='test@nexusri.com', serialize=True):

        client_dict = {
            'name': 'test_client_%s' % (self.test_client_counter + self.test_client_start),
            'description': 'company set out to take over the world',
            'contact_name': 'Thomas Aquinas',
            'contact_email': 'taquinas@nexusri.com',
            'contact_phone': '555-123-1234'
        }

        client = self.client_controller.create_client(actor_email, client_dict, serialize=serialize)
        self.increment_test_client_counter()
        return client

    ##------------------------------------ Tests --------------------------------------##

    def retail_test_get_clients(self):

        client1 = self.__create_test_client()
        self.__create_test_client()
        self.__create_test_client()
        self.__create_test_client()

        params = {
            "query": {
                "name": client1["name"]
            }
        }
        querystring = "params=%s" % json.dumps(params)

        # User with role 'user' cannot use this endpoint
        response = self.web_access.get("/api/clients", querystring, allow_redirects=False, cookies=self.user_cooks,
                                       headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # User with role 'client_support' cannot use this endpoint
        response = self.web_access.get("/api/clients", querystring, allow_redirects=False,
                                       cookies=self.client_support_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        results = self.web_access.get("/api/clients", querystring, cookies=self.admin_cooks,
                                      headers=self.json_headers).json()

        self.test_case.assertEqual(len(results["clients"]), 1)

        results = self.web_access.get("/api/clients", "", cookies=self.admin_cooks, headers=self.json_headers).json()
        self.test_case.assertTrue(len(results["clients"]) > self.test_client_counter)

    def retail_test_create_client(self):

        client_dict = {
            "name": "%s" % uuid.uuid4().hex,
            'description': 'description',
            "contact_email": "contact_email",
            'contact_name': 'contact_name',
            'contact_phone': 'contact_phone'
        }

        # User with role 'user' cannot use this endpoint
        response = self.web_access.post("/api/clients", json.dumps(client_dict), allow_redirects=False,
                                        cookies=self.user_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # User with role 'client_support' cannot use this endpoint
        response = self.web_access.post("/api/clients", json.dumps(client_dict), allow_redirects=False,
                                        cookies=self.client_support_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        results = self.web_access.post("/api/clients", json.dumps(client_dict), cookies=self.admin_cooks,
                                       headers=self.json_headers).json()
        self.test_case.assertDictContainsSubset(client_dict, results["client"])

    def retail_test_update_client(self):

        client = self.__create_test_client()

        client_dict = {
            'contact_phone': '1231231234'
        }

        # User with role 'user' cannot use this endpoint
        response = self.web_access.put("/api/clients/%s" % client["id"], json.dumps(client_dict), allow_redirects=False,
                                       cookies=self.user_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # User with role 'client_support' cannot use this endpoint
        response = self.web_access.put("/api/clients/%s" % client["id"], json.dumps(client_dict), allow_redirects=False,
                                       cookies=self.client_support_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        results = self.web_access.put("/api/clients/%s" % client["id"], json.dumps(client_dict),
                                      cookies=self.admin_cooks, headers=self.json_headers).json()
        self.test_case.assertEqual(client_dict["contact_phone"], results["client"]["contact_phone"])

    def retail_test_get_client(self):

        client = self.__create_test_client()

        # User with role 'user' cannot use this endpoint
        response = self.web_access.get("/api/clients/%s" % client["id"], "", allow_redirects=False,
                                       cookies=self.user_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # User with role 'client_support' cannot use this endpoint
        response = self.web_access.get("/api/clients/%s" % client["id"], "", allow_redirects=False,
                                       cookies=self.client_support_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        results = self.web_access.get("/api/clients/%s" % client["id"], "", cookies=self.admin_cooks,
                                      headers=self.json_headers).json()
        self.test_case.assertEqual(client["name"], results["client"]["name"])

    def retail_test_delete_client(self):

        client = self.__create_test_client()

        # User with role 'user' cannot use this endpoint
        response = self.web_access.delete("/api/clients/%s" % client["id"], "", allow_redirects=False,
                                          cookies=self.user_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # User with role 'client_support' cannot use this endpoint
        response = self.web_access.delete("/api/clients/%s" % client["id"], "", allow_redirects=False,
                                          cookies=self.client_support_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        results = self.web_access.delete("/api/clients/%s" % client["id"], "", cookies=self.admin_cooks,
                                         headers=self.json_headers).json()
        self.test_case.assertEqual(client["id"], results["id"])
