from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from retail.v010.data_access.controllers.user_controller import UserController
from common.utilities.date_utilities import parse_date
from requests.cookies import RequestsCookieJar
import datetime
import copy
import json
import re


class RetailWebProspectsTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_controller = UserController()
        self.json_headers = {"accept": "application/json", "content-type": "application/json"}

        self.__get_default_users()
        self.admin_cooks = self.__login_test_user_get_cookies(self.user_test.email, self.config["TEST_USER_PASSWORD"])
        self.client_support_cooks = self.__login_test_user_get_cookies(self.user_client_support.email, self.config["TEST_USER_PASSWORD"])
        self.user_cooks = self.__login_test_user_get_cookies(self.user_normal.email, self.config["TEST_USER_PASSWORD"])

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ##------------------------------------ Private helpers --------------------------------------##

    def __login_test_user_get_cookies(self, email, password):
        params = {"email": email, "password": password}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params, time_out=1000)
        assert response.ok and isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    def __get_default_users(self):
        self.user_test = self.user_controller.User.get("test@nexusri.com")
        self.user_client_support = self.user_controller.User.get("client_support@nexusri.com")
        self.user_normal = self.user_controller.User.get("user@nexusri.com")

    ##------------------------------------ Tests --------------------------------------##

    def retail_test_create_prospect(self):
        self.test_case.maxDiff = None

        good_request_data1 = {
            "name": "Batman",
            "email": "batman@batman.batman",
            "listOptIn": "y",
            "organization": "Justice League",
            "phone": "555-1212",
            "referrer": "bat cave"
        }

        good_request_data2 = {
            "name": "Batman",
            "email": "batman@batman.batman",
            "listOptIn": "y",
            "organization": "Justice League",
            "phone": "555-1212"
        }

        ############# good_request_data1 without session
        query_string = "?asdf=asdf&qwer=1234&qwer=5678"
        request_data = copy.copy(good_request_data1)
        response = self.web_access.post("/api/prospects%s" % query_string, json.dumps(request_data),
                                        headers=self.json_headers, time_out = 9999)
        self.test_case.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.test_case.assertIn("prospect", response_data)
        prospect = response_data["prospect"]

        self.test_case.assertDictEqual(prospect, {
            "id": prospect["id"],
            "name": "Batman",
            "email": "batman@batman.batman",
            "listOptIn": True,
            "organization": "Justice League",
            "phone": "555-1212",
            "referrer": "bat cave",
            "ip_address": prospect["ip_address"],
            "user_agent": prospect["user_agent"],
            "user": None,
            "creation_date": prospect["creation_date"],
            "query_params": {
                "asdf": ["asdf"],
                "qwer": ["1234", "5678"]
            }
        })

        ############# good_request_data2 with session
        request_data = copy.copy(good_request_data2)
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers, cookies=self.admin_cooks)
        self.test_case.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.test_case.assertIn("prospect", response_data)
        prospect = response_data["prospect"]

        # get test user again so we can check session variables like last_activity_date
        self.user_test = self.user_controller.User.get("test@nexusri.com")

        self.test_case.assertDictEqual(prospect, {
            "id": prospect["id"],
            "name": "Batman",
            "email": "batman@batman.batman",
            "listOptIn": True,
            "organization": "Justice League",
            "phone": "555-1212",
            "referrer": None,
            "ip_address": prospect["ip_address"],
            "user_agent": prospect["user_agent"],
            "user": self.user_test.serialize(),
            "creation_date": prospect["creation_date"],
            "query_params": {}
        })

        ############# No Name Key
        request_data = copy.copy(good_request_data1)
        del request_data["name"]
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        ############# Empty Name
        request_data = copy.copy(good_request_data1)
        request_data["name"] = ""
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        ############# No Email Key
        request_data = copy.copy(good_request_data1)
        del request_data["email"]
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        ############# Empty Email
        request_data = copy.copy(good_request_data1)
        request_data["email"] = ""
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        ############# Invalid Email
        request_data = copy.copy(good_request_data1)
        request_data["email"] = "batman@batman"
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        ############# No Organization Key
        request_data = copy.copy(good_request_data1)
        del request_data["organization"]
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        ############# Empty Organization
        request_data = copy.copy(good_request_data1)
        request_data["organization"] = ""
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        ############# No Phone Key
        request_data = copy.copy(good_request_data1)
        del request_data["phone"]
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        ############# Empty Phone
        request_data = copy.copy(good_request_data1)
        request_data["phone"] = ""
        response = self.web_access.post("/api/prospects", json.dumps(request_data), headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

