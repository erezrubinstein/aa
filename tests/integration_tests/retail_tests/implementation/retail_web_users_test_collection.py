from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from retail.v010.data_access.models.reset_password_request import ResetPasswordRequest
from retail.v010.data_access.controllers.client_controller import ClientController
from retail.v010.data_access.controllers.user_controller import UserController
from requests.cookies import RequestsCookieJar
import datetime
import uuid
import json


class RetailWebUsersTestCollection(ServiceTestCollection):
    test_user_counter = 0
    test_client_counter = 0

    # Random number to avoid interfering with other test collections in the same suite
    test_user_start = 987
    test_client_start = 987

    def initialize(self):
        self.user_controller = UserController()
        self.client_controller = ClientController()
        self.json_headers = {"access": "application/json", "content-type": "application/json"}

        self.__get_default_users()
        self.admin_cooks = self.__login_test_user_get_cookies(self.user_test["email"], self.config["TEST_USER_PASSWORD"])
        self.client_support_cooks = self.__login_test_user_get_cookies(self.user_client_support["email"], self.config["TEST_USER_PASSWORD"])

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def increment_test_user_counter(cls):
        cls.test_user_counter += 1

    @classmethod
    def increment_test_client_counter(cls):
        cls.test_client_counter += 1

    ##------------------------------------ Private helpers --------------------------------------##

    def __login_test_user_get_cookies(self, email, password):
        params = {"email": email, "password": password}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params, time_out = 9999)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    def __get_default_users(self):
        self.user_test = self.user_controller.User.get("test@nexusri.com", serialize=True)
        self.user_client_support = self.user_controller.User.get("client_support@nexusri.com", serialize=True)
        self.client_signal = self.user_controller.Client.get("Signal Data", serialize=True)

    def __create_test_user(self, client_name, actor_email='test@nexusri.com', serialize=True):

        password = 'yoyoyoyo%s' % (self.test_user_counter + self.test_user_start)

        user_dict = {
            'name': "test_user_%s" % (self.test_user_counter + self.test_user_start),
            'email': "test_email_%s@nexusri.com" % (self.test_user_counter + self.test_user_start),
            'client': client_name,
            'roles': ['user'],
            "retail_access": True,
            "retailer_access": False
        }

        user = self.user_controller.create_user(actor_email, user_dict, serialize=False)
        user.update(active=True, password=password)
        self.increment_test_user_counter()
        updated_user = self.user_controller.User.get(user.email)

        # Return unhashed password separately, because it's not returned in user object
        return (updated_user.serialize() if serialize and updated_user else updated_user), password

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

    def retail_test_get_session_user(self):

        user = self.user_controller.User.get(self.user_test["email"], serialize=True)
        session_user = self.web_access.get("/api/session_user", cookies=self.admin_cooks).json()
        self.test_case.maxDiff = None
        self.test_case.assertDictEqual(user, session_user["user"])

    def retail_test_update_session_user(self):

        user, password = self.__create_test_user(self.client_signal["name"])

        cooks = self.__login_test_user_get_cookies(user["email"], password)

        new_phone = "1231231234"
        request = json.dumps({
            "phone": new_phone
        })

        session_user = self.web_access.put("/api/session_user", request, cookies=cooks,
                                           headers=self.json_headers).json()["user"]
        self.test_case.assertEqual(new_phone, session_user["phone"])

        new_name = "blah blah blah blah"
        request = json.dumps({
            "name": new_name
        })

        session_user = self.web_access.put("/api/session_user", request, cookies=cooks,
                                           headers=self.json_headers).json()["user"]

        # User with role 'user' cannot change own name
        self.test_case.assertNotEqual(new_name, session_user["name"])

    def retail_test_update_user(self):

        user, password = self.__create_test_user(self.client_signal["name"])
        cooks = self.__login_test_user_get_cookies(user["email"], password)

        new_phone = "1231231234"
        request = json.dumps({
            "phone": new_phone
        })

        # User with role 'user' cannot call this endpoint
        response = self.web_access.put("/api/users/%s" % user["id"], request, allow_redirects=False, cookies=cooks,
                                       headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        new_phone = "5634563456"
        new_name = "blah blah blah blah"
        request = json.dumps({
            "name": new_name,
            "phone": new_phone
        })

        session_user = self.web_access.put("/api/users/%s" % user["id"], request, cookies=self.admin_cooks,
                                           headers=self.json_headers).json()["user"]

        # User with role 'admin' can change user phone and name
        self.test_case.assertEqual(new_phone, session_user["phone"])
        self.test_case.assertEqual(new_name, session_user["name"])

    def retail_test_get_users(self):

        client = self.__create_test_client()

        user, password = self.__create_test_user(client["name"])
        cooks = self.__login_test_user_get_cookies(user["email"], password)

        # User with role 'user' cannot call this endpoint
        response = self.web_access.get("/api/users", allow_redirects=False, cookies=cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # User with role 'client_support' can use this endpoint
        users = self.web_access.get("/api/users", cookies=self.client_support_cooks,
                                    headers=self.json_headers).json()["users"]
        self.test_case.assertGreater(len(users), 4)

        params = {
            "query": {
                "client": client["name"]
            }
        }
        querystring = "params=%s" % json.dumps(params)
        users = self.web_access.get("/api/users", querystring, cookies=self.client_support_cooks,
                                    headers=self.json_headers).json()["users"]
        self.test_case.assertEqual(len(users), 1)

    def retail_test_get_user(self):

        self.test_case.maxDiff = None

        client = self.__create_test_client()

        test_user, password = self.__create_test_user(client["name"])
        cooks = self.__login_test_user_get_cookies(test_user["email"], password)

        # Get user again, because dict changes after logging in
        test_user = self.user_controller.User.get(test_user["email"], serialize=True)

        # User with role 'user' cannot use this endpoint
        response = self.web_access.get("/api/users/%s" % test_user["id"], allow_redirects=False, cookies=cooks,
                                       headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # Get user again, because session count & last activity date changes after hitting /api/users
        test_user = self.user_controller.User.get(test_user["email"], serialize=True)

        # User with role 'client_support' can use this endpoint
        user = self.web_access.get("/api/users/%s" % test_user["id"], cookies=self.client_support_cooks,
                                   headers=self.json_headers).json()["user"]
        self.test_case.assertDictEqual(test_user, user)

    def retail_test_delete_user(self):

        client = self.__create_test_client()

        test_user, password = self.__create_test_user(client["name"])
        cooks = self.__login_test_user_get_cookies(test_user["email"], password)

        # Get user again, because dict changes after logging in
        test_user = self.user_controller.User.get(test_user["email"], serialize=True)

        # User with role 'user' cannot use this endpoint
        response = self.web_access.delete("/api/users/%s" % test_user["id"], "", allow_redirects=False, cookies=cooks,
                                          headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # User with role 'client_support' cannot use this endpoint
        response = self.web_access.delete("/api/users/%s" % test_user["id"], "", allow_redirects=False,
                                          cookies=self.client_support_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        # User with role 'admin' can use this endpoint
        user_id = self.web_access.delete("/api/users/%s" % test_user["id"], "", cookies=self.admin_cooks,
                                         headers=self.json_headers).json()["id"]
        self.test_case.assertEqual(test_user["id"], user_id)

        # Get user again, because dict changes after logging in
        test_user = self.user_controller.User.get(test_user["email"], include_deleted=True, serialize=True)
        self.test_case.assertEqual(test_user["deleted"], True)

    def retail_test_create_user_and_reset_password_request(self):

        client = self.__create_test_client()

        user_email = "%s@nexusri.com" % uuid.uuid4().hex
        user_json = json.dumps({
            "email": user_email,
            "name": "Abc",
            "client": client["name"],
            "retail_access": True,
            "retailer_access": False
        })
        results = self.web_access.post("/api/users", user_json, cookies=self.admin_cooks,
                                       headers=self.json_headers).json()

        rpr = results["reset_password_request"]
        self.test_case.assertEqual(rpr["status"], "open")

        user = results["user"]
        rpr_code = results["reset_password_code"]

        rpr_json = json.dumps({
            "code": rpr_code,
            "password": "asdfasdfasdf1"
        })

        results = self.web_access.put("/api/reset_password/%s" % rpr["id"], rpr_json, headers=self.json_headers).json()
        self.test_case.assertEqual(results["reset_password_request"]["status"], "closed")

        updated_user = self.web_access.get("/api/users/%s" % user["id"], cookies=self.admin_cooks).json()
        self.test_case.assertEqual(updated_user["user"]["active"], True)

    def retail_test_create_user_and_reset_password_request__expired(self):

        client = self.__create_test_client()

        user_email = "%s@nexusri.com" % uuid.uuid4().hex
        user_json = json.dumps({
            "email": user_email,
            "name": "Abc",
            "client": client["name"],
            "retail_access": True,
            "retailer_access": False
        })
        results = self.web_access.post("/api/users", user_json, cookies=self.admin_cooks,
                                       headers=self.json_headers).json()

        rpr = results["reset_password_request"]
        self.test_case.assertEqual(rpr["status"], "open")

        rpr_code = results["reset_password_code"]
        rpr_id = rpr["id"]

        rpr = ResetPasswordRequest.find(id=rpr_id)
        rpr.created_at = datetime.datetime.utcnow() - datetime.timedelta(days=15)
        rpr.save()

        rpr_json = json.dumps({
            "code": rpr_code,
            "password": "asdfasdfasdf1"
        })

        response = self.web_access.put("/api/reset_password/%s" % rpr_id, rpr_json, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

        # Fix created_at date
        rpr.created_at = datetime.datetime.utcnow() - datetime.timedelta(days=13)
        rpr.save()

        rpr_json = json.dumps({
            "code": rpr_code,
            "password": "asdfasdfasdf1"
        })

        response = self.web_access.put("/api/reset_password/%s" % rpr_id, rpr_json, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 400)

    def retail_test_user_forgot_password(self):

        user_email = "%s@nexusri.com" % uuid.uuid4().hex
        user_json = json.dumps({
            "email": user_email,
            "name": "Def",
            "client": self.client_signal["name"],
            "retail_access": True,
            "retailer_access": False
        })
        results = self.web_access.post("/api/users", user_json, cookies=self.admin_cooks,
                                       headers=self.json_headers).json()

        user = results["user"]
        rpr = results["reset_password_request"]
        rpr_json = json.dumps({
            "code": results["reset_password_code"],
            "password": "asdfasdfasdf1"
        })
        self.web_access.put("/api/reset_password/%s" % rpr["id"], rpr_json, headers=self.json_headers).json()

        user_json = json.dumps({
            "email": user_email
        })
        results = self.web_access.post("/api/reset_password_requests", user_json, headers=self.json_headers).json()

        rpr = results["reset_password_request"]
        self.test_case.assertEqual(rpr["status"], "open")

        rpr = results["reset_password_request"]
        rpr_json = json.dumps({
            "code": results["reset_password_code"],
            "password": "123412341234"
        })
        results = self.web_access.put("/api/reset_password/%s" % rpr["id"], rpr_json, headers=self.json_headers).json()
        self.test_case.assertEqual(results["reset_password_request"]["status"], "closed")

        updated_user = self.web_access.get("/api/users/%s" % user["id"], cookies=self.admin_cooks).json()
        self.test_case.assertEqual(updated_user["user"]["active"], True)
