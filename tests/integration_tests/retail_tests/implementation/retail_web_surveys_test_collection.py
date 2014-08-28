from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from retail.v010.data_access.controllers.user_controller import UserController
from retail.v010.data_access.models.survey_question import SurveyQuestion
from retail.v010.data_access.models.survey_answer import SurveyAnswer
from retail.v010.data_access.models.survey import Survey
from requests.cookies import RequestsCookieJar
import json


class RetailWebSurveysTestCollection(ServiceTestCollection):

    # Random number to avoid interfering with other test collections in the same suite
    test_user_start = 54648
    test_user_counter = 0

    @classmethod
    def increment_test_user_counter(cls):
        cls.test_user_counter += 1

    def initialize(self):
        self.user_controller = UserController()
        self.json_headers = {"accept": "application/json", "content-type": "application/json"}

        self.__get_default_users()
        self.admin_cooks = self.__login_test_user_get_cookies(self.user_test.email, self.config["TEST_USER_PASSWORD"])
        self.client_support_cooks = self.__login_test_user_get_cookies(self.user_client_support.email, self.config["TEST_USER_PASSWORD"])
        self.user_cooks = self.__login_test_user_get_cookies(self.user_normal.email, self.config["TEST_USER_PASSWORD"])

    def setUp(self):
        self.__create_test_survey()

    def tearDown(self):
        pass

    ##------------------------------------ Private helpers --------------------------------------##

    def __login_test_user_get_cookies(self, email, password):
        params = {"email": email, "password": password}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params, time_out=1000)
        assert response.ok and isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    def __get_default_users(self):
        self.client_signal = self.user_controller.Client.get("Signal Data")
        self.user_test = self.user_controller.User.get("test@nexusri.com")
        self.user_client_support = self.user_controller.User.get("client_support@nexusri.com")
        self.user_normal = self.user_controller.User.get("user@nexusri.com")

    def __create_test_user(self, serialize=False):
        password = 'yoyoyoyo%s' % (self.test_user_counter + self.test_user_start)
        user_dict = {
            'name': "test_user_%s" % (self.test_user_counter + self.test_user_start),
            'email': "test_email_%s@nexusri.com" % (self.test_user_counter + self.test_user_start),
            'password': password,
            'active': True,
            'client': self.client_signal.name,
            'retail_access': True,
            'retailer_access': False,
            'roles': ['user']
        }
        user = self.user_controller.create_user('test@nexusri.com', user_dict, serialize=False)
        user.update(active=True, password=user_dict["password"])
        updated_user = self.user_controller.User.get(user.email, serialize=False)
        self.increment_test_user_counter()
        # Return unhashed password separately, because it's not returned in user object
        return (updated_user.serialize() if updated_user and serialize else updated_user), password

    def __create_test_survey(self):
        Survey.drop_collection()
        SurveyQuestion.drop_collection()
        SurveyAnswer.drop_collection()

        s1 = Survey.create(key="test_survey1", title="Test Survey", description="You know, for testing...", completion_type="multiple")

        q1 = SurveyQuestion.create(survey=s1, key="test_q1", text="Q1", index=0, type="single_choice")
        q1.update(answers=[
            SurveyAnswer.create(survey=s1, question=q1, key="test_a11", text="A11", index=0, branch="branch1"),
            SurveyAnswer.create(survey=s1, question=q1, key="test_a12", text="A12", index=1, branch="branch2"),
            SurveyAnswer.create(survey=s1, question=q1, key="test_a13", text="A13", index=2)
        ])

        q2 = SurveyQuestion.create(survey=s1, key="test_q2", text="Q2", index=1, type="single_choice", branch="branch1")
        q2.update(answers=[
            SurveyAnswer.create(survey=s1, question=q2, key="test_a21", text="A21", index=0),
            SurveyAnswer.create(survey=s1, question=q2, key="test_a22", text="A22", index=1),
            SurveyAnswer.create(survey=s1, question=q2, key="test_a23", text="A23", index=2)
        ])

        q3 = SurveyQuestion.create(survey=s1, key="test_q3", text="Q3", index=1, type="single_choice", branch="branch2")
        q3.update(answers=[
            SurveyAnswer.create(survey=s1, question=q3, key="test_a31", text="A31", index=0, branch="branch3"),
            SurveyAnswer.create(survey=s1, question=q3, key="test_a32", text="A32", index=1),
            SurveyAnswer.create(survey=s1, question=q3, key="test_a33", text="A33", index=2)
        ])

        q4 = SurveyQuestion.create(survey=s1, key="test_q4", text="Q4", index=2, type="single_choice", branch="branch3")
        q4.update(answers=[
            SurveyAnswer.create(survey=s1, question=q4, key="test_a41", text="A41", index=0),
            SurveyAnswer.create(survey=s1, question=q4, key="test_a42", text="A42", index=1),
            SurveyAnswer.create(survey=s1, question=q4, key="test_a43", text="A43", index=2)
        ])

        Survey.create(key="test_survey2", title="Test Survey 2", description="You know, for testing...")

    ##------------------------------------ Tests --------------------------------------##

    def retail_test_get_survey_list(self):

        response = self.web_access.get("/api/surveys", "", allow_redirects=False, cookies=self.user_cooks, headers=self.json_headers)
        self.test_case.assertEqual(response.status_code, 302)

        response = self.web_access.get("/api/surveys", "params={\"sort\":\"key\"}", cookies=self.client_support_cooks, headers=self.json_headers).json()
        self.test_case.assertEqual(len(response["surveys"]), 2)
        self.test_case.assertEqual(response["surveys"][0]["key"], "test_survey1")
        self.test_case.assertEqual(response["surveys"][1]["key"], "test_survey2")

        response = self.web_access.get("/api/surveys", "params={\"sort\":\"-key\"}", cookies=self.admin_cooks, headers=self.json_headers).json()
        self.test_case.assertEqual(len(response["surveys"]), 2)
        self.test_case.assertEqual(response["surveys"][0]["key"], "test_survey2")
        self.test_case.assertEqual(response["surveys"][1]["key"], "test_survey1")

    def retail_test_get_survey_detail(self):

        user, pw = self.__create_test_user()
        cooks = self.__login_test_user_get_cookies(user.email, pw)

        response = self.web_access.get("/api/surveys/test_survey1", "", cookies=cooks, headers=self.json_headers).json()

        self.test_case.assertIn("survey", response)

    def retail_test_get_survey_questions_detail(self):

        user, pw = self.__create_test_user()
        cooks = self.__login_test_user_get_cookies(user.email, pw)

        response = self.web_access.get("/api/survey_questions/test_survey1", "", cookies=cooks, headers=self.json_headers).json()

        self.test_case.assertEqual(len(response["survey_questions"]), 4)
        self.test_case.assertEqual(len(response["survey_answers"]), 12)

    def retail_test_post_user_survey_response(self):

        user, pw = self.__create_test_user()
        cooks = self.__login_test_user_get_cookies(user.email, pw)

        question_answer_maps = [
            {
                "test_q1": "test_a11",
                "test_q2": "test_a21"
            },
            {
                "test_q1": "test_a12",
                "test_q3": "test_a31",
                "test_q4": "test_a41"
            },
            {
                "test_q1": "test_a12",
                "test_q3": "test_a32"
            },
            {
                "test_q1": "test_a13",
                # Extra unnecessary stuff
                "asdf1": "asdf1",
                "asdf2": "test_a22",
                "test_q2": "asdf",
                "test_q3": "test_a31"
            }
        ]

        for qam in question_answer_maps:
            self._validate_user_survey_responses_against_question_answer_map(qam, cooks)

    def _validate_user_survey_responses_against_question_answer_map(self, question_answer_map, cooks):

        data = json.dumps({
            "survey_key": "test_survey1",
            "question_answer_map": question_answer_map
        })

        response = self.web_access.post("/api/user_survey_responses", data, cookies=cooks, headers=self.json_headers).json()
        self.test_case.assertIn("user_survey_responses", response)

        # Incoming question answer map can have extra stuff,
        # but anything that comes back should be in the question answer map
        for usr in response["user_survey_responses"]:
            self.test_case.assertIn(usr["question"]["key"], question_answer_map)
            self.test_case.assertEqual(question_answer_map[usr["question"]["key"]], usr["answer"]["key"])
