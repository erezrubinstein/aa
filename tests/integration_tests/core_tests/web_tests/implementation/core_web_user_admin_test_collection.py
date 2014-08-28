from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.service_access.utilities.rec_helpers import is_rec_match
from common.utilities.inversion_of_control import Dependency
from requests.cookies import RequestsCookieJar
import json


__author__ = 'jsternberg'


class CoreWebUserAdminTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "web_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_test_user_get_cookies()

    def setUp(self):
        pass

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

    def test_get_default_users(self):

        # we expect the core web site to be initialized with 2 default users: test and admin

        response = self.web_access.get("/api/users", cookies=self.cooks)
        self.test_case.assert200(response)
        self.test_case.assertIn("users", response.json())
        users = response.json()["users"]
        # at this point we should have at least 2 users: test and admin
        default_users = [u for u in users if u["email"] in [u'test@nexusri.com', u'admin@nexusri.com']]
        self.test_case.assertEqual(len(default_users), 2)
        for du in default_users:
            # default users should have the admin role
            self.test_case.assertIn("roles", du)
            self.test_case.assertIn("name", du["roles"][0])
            self.test_case.assertEqual(du["roles"][0]["name"], "admin")

    def test_create_user_and_login(self):

        # clear out the test user first, if it exists (double-check)
        user_access = Dependency("CoreUserProvider").value
        user = user_access.find_user({"email": "luke@sywalker.com"})
        if user:
            user_access.delete_user(user["id"])

        # test creating a new user account, and then login to the site as that user
        try:
            user_dict = {"email": "luke@sywalker.com", "password": "dagobah"}
            response = self.web_access.post("/api/users",
                                            json.dumps(user_dict),
                                            headers = {'content-type': 'application/json', 'accept': 'application/json'},
                                            cookies=self.cooks)
            self.test_case.assert201(response)

            expected_response = {u'user': {u'roles': [],
                                           u'confirmed_at': u'None',
                                           u'is_generalist': False,
                                           u'active': True,
                                           u'email': u'luke@sywalker.com'}}
            self.test_case.assertTrue(is_rec_match(response.json(), expected_response))

            # try to log in
            params = {"email":"luke@sywalker.com", "password":"dagobah"}
            response = self.web_access.post("/login", params)
            self.test_case.assert200(response)
            self.test_case.assertIn(u'Welcome to Signal Core.', response.text)

        finally:
            # delete the test user
            user = user_access.find_user({"email": "luke@sywalker.com"})
            if user:
                user_access.delete_user(user["id"])