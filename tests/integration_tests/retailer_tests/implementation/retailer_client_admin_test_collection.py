from __future__ import division
import json
from common.utilities.inversion_of_control import Dependency
from retail.v010.data_access.controllers.client_controller import ClientController
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from retail.v010.data_access.controllers.user_controller import UserController
from common.utilities.date_utilities import LAST_ANALYTICS_DATE, get_datetime_months_ago, parse_date
from core.common.utilities.errors import BadRequestError
from requests.cookies import RequestsCookieJar
import datetime
import copy


class RetailerClientAdminTestCollection(ServiceTestCollection):
    def initialize(self):
        self.user_controller = UserController()
        self.client_controller = ClientController()
        self.json_headers = {"accept": "application/json", "content-type": "application/json"}
        self.__get_default_users()
        self.admin_cooks = self.__login_test_user_get_cookies(self.user_test.email, self.config["TEST_USER_PASSWORD"])
        self.client_support_cooks = self.__login_test_user_get_cookies(self.user_client_support.email, self.config["TEST_USER_PASSWORD"])
        self.user_cooks = self.__login_test_user_get_cookies(self.user_normal.email, self.config["TEST_USER_PASSWORD"])
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        self.client_count_start = 45321
        self.client_incr = 0
        # first we have to set up the demo client so that the retailer_client_id value will be there to increment
        self.mds_access.call_add_entity("retailer_client", "Signal Demo", {"retailer_client_id": 0}, self.context)


    def setUp(self):
        self.client_incr += 1


    def tearDown(self):
        pass


    ##------------------------------------ Tests --------------------------------------##


    def add_new_retailer_client(self):
        self.__create_test_client()
        self.__create_retailer_client()

        # check MDS for the retailer_client entity
        fields = ["_id", "data", "name"]
        query = { "name": self.__get_retailer_client_name() }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query,
                                                    entity_fields = fields, has_metadata = False, as_list = True)["params"]
        retailer_client = self.mds_access.call_find_entities_raw('retailer_client', params, {})

        self.test_case.assertEqual(retailer_client[0][1:],
                                   [{u'key': u'peele', 'retailer_client_id': self.client_incr}, self.__get_retailer_client_name()])

        # make sure the client document got the retailer_client_id
        client = self.client_controller.get_client(self.__get_retailer_client_name())
        self.test_case.assertEqual(client["retailer_client_id"], self.client_incr)


    def get_retailer_client_by_id(self):
        self.__create_test_client()
        self.__create_retailer_client()

        # check MDS for the retailer_client entity id
        fields = ["_id", "data", "name"]
        query = { "name": self.__get_retailer_client_name() }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query,
                                                    entity_fields = fields, has_metadata = False, as_list = True)["params"]
        retailer_client = self.mds_access.call_find_entities_raw('retailer_client', params, {})
        retailer_client_id = retailer_client[0][0]

        # hit the api endpoint with a get and test the response
        response = self.web_access.get("/api/admin/retailer_client/id/%s" % retailer_client_id,
                                              cookies=self.user_cooks)
        self.test_case.assert200(response)
        self.test_case.assertIsNotNone(response.json())
        retailer_client = response.json()
        expected = {
            "_id": retailer_client_id,
            "name": self.__get_retailer_client_name(),
            "data": {
                "key": "peele",
                'retailer_client_id': self.client_incr
            }
        }
        self.test_case.assertEqual(retailer_client, expected)


    def get_retailer_client_by_name(self):
        self.__create_test_client()
        self.__create_retailer_client()

        # hit the api endpoint with a get and test the response
        response = self.web_access.get("/api/admin/retailer_client/name/%s" % self.__get_retailer_client_name(),
                                       cookies=self.user_cooks)
        self.test_case.assert200(response)
        self.test_case.assertIsNotNone(response.json())
        retailer_client = response.json()
        self.test_case.assertEqual(retailer_client["data"], { "key": "peele", 'retailer_client_id': self.client_incr })


    def update_retailer_client_by_id(self):
        self.__create_test_client()
        self.__create_retailer_client()

        # check MDS for the retailer_client entity id
        fields = ["_id", "data", "name"]
        query = { "name": self.__get_retailer_client_name() }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query,
                                                    entity_fields = fields, has_metadata = False, as_list = True)["params"]
        retailer_client = self.mds_access.call_find_entities_raw('retailer_client', params, {})
        retailer_client_id = retailer_client[0][0]

        # hit the api endpoint with a put and test the response
        update_dict = {
            "key": "whoa",
            "peele": "key",
            "retailer_client_id": self.client_incr
        }
        response = self.web_access.put("/api/admin/retailer_client/id/%s" % retailer_client_id,
                                       json.dumps(update_dict), cookies=self.admin_cooks)
        self.test_case.assert200(response)
        fields = ["_id", "data"]
        query = { "_id": retailer_client_id }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query,
                                                    entity_fields = fields, has_metadata = False, as_list = True)["params"]
        retailer_client = self.mds_access.call_find_entities_raw('retailer_client', params, {})
        updated_data = retailer_client[0][1]
        self.test_case.assertEqual(updated_data, update_dict)


    def update_retailer_client_by_name(self):
        self.__create_test_client()
        self.__create_retailer_client()

        # hit the api endpoint with a put and test the response
        update_dict = {
            "key": "whoa",
            "peele": "key",
            "retailer_client_id": self.client_incr
        }
        response = self.web_access.put("/api/admin/retailer_client/name/%s" % self.__get_retailer_client_name(),
                                       json.dumps(update_dict), cookies=self.user_cooks)
        self.test_case.assert200(response)
        fields = ["_id", "data"]
        query = { "name": self.__get_retailer_client_name() }
        params = self.main_params.mds.create_params(resource = "find_entities_raw", query = query,
                                                    entity_fields = fields, has_metadata = False, as_list = True)["params"]
        retailer_client = self.mds_access.call_find_entities_raw('retailer_client', params, {})
        updated_data = retailer_client[0][1]
        self.test_case.assertEqual(updated_data, update_dict)


    ##------------------------------------ Private helpers --------------------------------------##


    def __create_retailer_client(self):
        params = {
            "data" : {
                "key": "peele"
            },
            'name': self.__get_retailer_client_name()
        }
        # call the api to create a new retailer_client
        self.web_access.post("/api/admin/retailer_client/new", json.dumps(params), cookies=self.admin_cooks)


    def __create_test_client(self, actor_email='test@nexusri.com', serialize=True):
        client_dict = {
            'name': self.__get_retailer_client_name(),
            'description': 'company set out to take over the world',
            'contact_name': 'Thomas Aquinas',
            'contact_email': 'taquinas@nexusri.com',
            'contact_phone': '555-123-1234',
            'retailer_client_id': self.client_incr
        }
        client = self.client_controller.create_client(actor_email, client_dict, serialize=serialize)
        return client


    def __get_retailer_client_name(self):
        return 'test_retailer_client%d' % (self.client_count_start + self.client_incr)


    def __login_test_user_get_cookies(self, email, password):
        params = {"email": email, "password": password}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok and isinstance(response.cookies, RequestsCookieJar)
        return response.cookies


    def __get_default_users(self):
        self.user_test = self.user_controller.User.get("test@nexusri.com")
        self.user_client_support = self.user_controller.User.get("client_support@nexusri.com")
        self.user_normal = self.user_controller.User.get("user@nexusri.com")
