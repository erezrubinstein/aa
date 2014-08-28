from __future__ import division
from retail.v010.data_access.controllers.white_space_competition_set_controller import WhiteSpaceCompetitionSetController
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from retail.v010.data_access.controllers.user_controller import UserController
from common.utilities.date_utilities import LAST_ANALYTICS_DATE, get_datetime_months_ago, parse_date
from core.common.utilities.errors import BadRequestError
from requests.cookies import RequestsCookieJar
import datetime
import copy


class RetailWebWhiteSpaceCompetitionSetTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_controller = UserController()
        self.wscomp_controller = WhiteSpaceCompetitionSetController()
        self.json_headers = {"accept": "application/json", "content-type": "application/json"}

    def setUp(self):
        self.__get_default_users()
        self.admin_cooks = self.__login_test_user_get_cookies(self.user_test.email, self.config["TEST_USER_PASSWORD"])
        self.client_support_cooks = self.__login_test_user_get_cookies(self.user_client_support.email, self.config["TEST_USER_PASSWORD"])
        self.user_cooks = self.__login_test_user_get_cookies(self.user_normal.email, self.config["TEST_USER_PASSWORD"])
        self.test_case.maxDiff = None

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

    def retail_test_create_white_space_competition_set(self):
        
        good_company_analytics = {
            "stores": {
                "monthly": {
                    "store_counts": [
                        {
                            "date": LAST_ANALYTICS_DATE.strftime("%Y-%m-%dT%H:%M:%S"),
                            "value": 1
                        }
                    ]
                }
            }
        }
        
        bad_company_analytics1 = copy.deepcopy(good_company_analytics)
        bad_company_analytics1["stores"]["monthly"]["store_counts"][0]["date"] = \
            get_datetime_months_ago(1, start=LAST_ANALYTICS_DATE).strftime("%Y-%m-%dT%H:%M:%S")

        bad_company_analytics2 = copy.deepcopy(good_company_analytics)
        bad_company_analytics2["stores"]["monthly"]["store_counts"][0]["value"] = 0
        
        cid1 = insert_test_company(name="C1", ctype="retail_banner", analytics=good_company_analytics)
        cid2 = insert_test_company(name="C2", ctype="retail_banner", analytics=good_company_analytics)
        cid3 = insert_test_company(name="C3", ctype="retail_banner", analytics=good_company_analytics)

        banner_id = cid1
        competition_set = [
            {"id": cid2, "name": "C2", "weight": 0.8, "enabled": True},
            {"id": cid3, "name": "C3", "weight": 1, "enabled": False}
        ]

        wscomp1 = self.wscomp_controller.create_white_space_competition_set(self.user_test, banner_id, competition_set)
        self.test_case.assertDictEqual(wscomp1, {
            "id": wscomp1["id"],
            "user": wscomp1["user"],
            "banner_id": banner_id,
            "competition_set": competition_set,
            "modified_date": wscomp1["modified_date"],
            "creation_date": wscomp1["creation_date"]
        })

        creation_date1 = parse_date(wscomp1["creation_date"])
        self.test_case.assertTrue(creation_date1 <= datetime.datetime.utcnow())

        wscomp2 = self.wscomp_controller.create_white_space_competition_set(self.user_test, banner_id, competition_set)

        # get the test user again to account for session activity date & count changes
        self.user_test = self.user_controller.User.get("test@nexusri.com")

        # Same ID as before (updated, not re-created), same creation date, and same user
        self.test_case.assertDictEqual(wscomp2, {
            "id": wscomp1["id"],
            "user": self.user_test.serialize(),
            "banner_id": banner_id,
            "competition_set": competition_set,
            "modified_date": wscomp2["modified_date"],
            "creation_date": wscomp1["creation_date"]
        })
