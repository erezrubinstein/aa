import unittest

import mox

from common.helpers.common_dependency_helper import register_common_mox_dependencies
from retail.v010.data_access.retail_data_helper import RetailDataHelper
from common.utilities.inversion_of_control import Dependency, dependencies


__author__ = 'vgold'


class RetailDataHelperTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RetailDataHelperTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_store_helper.py"}

        # Set up useful mocks
        self.mock = self.mox.CreateMock(RetailDataHelper)
        self.mock.user_controller = self.mox.CreateMockAnything()
        self.mock.User = self.mox.CreateMockAnything()
        self.mock.Role = self.mox.CreateMockAnything()
        self.mock.Client = self.mox.CreateMockAnything()
        self.mock.ResetPasswordRequest = self.mox.CreateMockAnything()
        self.mock.Notification = self.mox.CreateMockAnything()
        self.mock.Setting = self.mox.CreateMockAnything()
        self.mock.Survey = self.mox.CreateMockAnything()
        self.mock.SurveyQuestion = self.mox.CreateMockAnything()
        self.mock.SurveyAnswer = self.mox.CreateMockAnything()

    def doCleanups(self):

        super(RetailDataHelperTests, self).doCleanups()
        dependencies.clear()

    ###########################################
    # RetailDataHelper._create_roles()

    def test_create_roles__none_exist(self):

        self.mock.default_roles = [
            ("user", "Standard User"),
            ("client_support", "Client Support"),
            ("admin", "Administrator")
        ]

        self.mock.Role.get('user').AndReturn(None)
        self.mock.Role.create(name="user", description="Standard User")

        self.mock.Role.get('client_support').AndReturn(None)
        self.mock.Role.create(name="client_support", description="Client Support")

        self.mock.Role.get('admin').AndReturn(None)
        self.mock.Role.create(name="admin", description="Administrator")

        self.mox.ReplayAll()
        RetailDataHelper._create_roles(self.mock)

    def test_create_roles_and_default_user__all_exist(self):

        self.mock.default_roles = [
            ("user", "Standard User"),
            ("client_support", "Client Support"),
            ("admin", "Administrator")
        ]

        self.mock.Role.get('user').AndReturn(True)
        self.mock.Role.get('client_support').AndReturn(True)
        self.mock.Role.get('admin').AndReturn(True)

        self.mox.ReplayAll()
        RetailDataHelper._create_roles(self.mock)

    ###########################################
    # RetailDataHelper._create_default_clients()

    def test_create_default_clients__none_exist(self):

        self.mock.default_clients = [
            {
                "name": "Signal Data",
                "description": "Signal Data Internal Client.",
                "contact_name": "Thomas Aquinas",
                "contact_email": "engineering@nexusri.com",
                "contact_phone": "555-123-4567",
                "is_internal_client": True,
                "retailer_access": True,
                "retail_access": True
            }
        ]

        client_name = 'Signal Data'
        client = self.mox.CreateMockAnything()
        client.name = client_name

        self.mock.Client.get(client_name, include_deleted=True).AndReturn(None)
        self.mock.Client.create(name=client_name,
                                description="Signal Data Internal Client.",
                                contact_name="Thomas Aquinas",
                                contact_email="engineering@nexusri.com",
                                contact_phone="555-123-4567",
                                is_internal_client=True,
                                retailer_access=True,
                                retail_access=True,
                                serialize=False).AndReturn(client)

        self.mox.ReplayAll()
        RetailDataHelper._create_default_clients(self.mock)

    def test_create_default_clients__all_exist(self):

        client_name = 'Signal Data'
        client = self.mox.CreateMockAnything()
        client.name = client_name

        self.mock.Client.get(client_name, include_deleted=True).AndReturn(True)

        self.mox.ReplayAll()
        RetailDataHelper._create_default_clients(self.mock)

    ###########################################
    # RetailDataHelper._create_default_users()

    def test_create_default_users__none_exist(self):

        self.mock.default_users = [
            (None, {
                "name": "test",
                "email": "test@nexusri.com",
                "client": "Signal Data",
                "roles": ["admin"],
                "retailer_access": True,
                "retail_access": True,
                "expiration_date": "3000-01-01",
                "subscription_level": "Subscriber"
            }),
            ("test@nexusri.com", {
                "name": "user",
                "email": "user@nexusri.com",
                "client": "Signal Data",
                "roles": ["user"],
                "retailer_access": True,
                "retail_access": True,
                "expiration_date": "3000-01-01",
                "subscription_level": "Subscriber"
            })
        ]

        self.mock.config = {
            "TEST_USER_PASSWORD": "test"
        }

        self.mock.User.get("test@nexusri.com", include_deleted=True).AndReturn(None)

        user = self.mox.CreateMockAnything()
        user.id = 1
        self.mock.user_controller._create_user_direct(None, {
            "name": "test",
            "email": "test@nexusri.com",
            "client": "Signal Data",
            "retail_access": True,
            "retailer_access": True,
            "roles": ["admin"],
            "expiration_date": "3000-01-01",
            "subscription_level": "Subscriber"
        }).AndReturn(user)
        user.update(password=self.mock.config["TEST_USER_PASSWORD"], active=True)

        self.mock.User.get("user@nexusri.com", include_deleted=True).AndReturn(None)

        user = self.mox.CreateMockAnything()
        user.id = 2
        self.mock.user_controller._create_user_direct("test@nexusri.com", {
            "name": "user",
            "email": "user@nexusri.com",
            "client": "Signal Data",
            "retail_access": True,
            "retailer_access": True,
            "roles": ["user"],
            "expiration_date": "3000-01-01",
            "subscription_level": "Subscriber"
        }).AndReturn(user)
        user.update(password=self.mock.config["TEST_USER_PASSWORD"], active=True)

        self.mox.ReplayAll()

        RetailDataHelper._create_default_users(self.mock)

    def test_create_default_users__all_exist(self):

        self.mock.default_users = [
            (None, {
                "name": "test",
                "email": "test@nexusri.com",
                "client": "Signal Data",
                "roles": ["admin"],
                "retailer_access": True,
                "retail_access": True,
                "expiration_date": "3000-01-01",
                "subscription_level": "Subscriber"
            }),
            ("test@nexusri.com", {
                "name": "user",
                "email": "user@nexusri.com",
                "client": "Signal Data",
                "roles": ["user"],
                "retailer_access": True,
                "retail_access": True,
                "expiration_date": "3000-01-01",
                "subscription_level": "Subscriber"
            })
        ]

        self.mock.User.get("test@nexusri.com", include_deleted=True).AndReturn(True)
        self.mock.User.get("user@nexusri.com", include_deleted=True).AndReturn(True)

        self.mox.ReplayAll()
        RetailDataHelper._create_default_users(self.mock)

    ###########################################
    # RetailDataHelper._create_notifications()

    def test_create_notifications(self):

        self.mock.default_notifications = [
            ('new_product_features', 'New product features'),
            ('new_product_releases', 'New product releases')
        ]

        self.mock.Notification.get("new_product_features").AndReturn(True)
        self.mock.Notification.get("new_product_releases").AndReturn(None)
        self.mock.Notification.create(name="new_product_releases", description="New product releases")

        self.mox.ReplayAll()
        RetailDataHelper._create_notifications(self.mock)

    ###########################################
    # RetailDataHelper._create_settings()

    def test_create_settings(self):

        self.mock.default_settings = [
            {
                "name": "setting1",
                "description": "Setting 1",
                "type": "bool",
                "value": False
            },
            {
                "name": "setting2",
                "description": "Setting 2",
                "type": "bool",
                "value": True
            }
        ]

        self.mock.Setting.get("setting1").AndReturn(True)
        self.mock.Setting.get("setting2").AndReturn(None)
        self.mock.Setting.create(**self.mock.default_settings[1])

        self.mox.ReplayAll()
        RetailDataHelper._create_settings(self.mock)

    ###########################################
    # RetailDataHelper._manage_surveys()

    def test_manage_surveys(self):

        surveys = [
            ("survey1", {
                "title": "survey1",
                "description": "survey1",
                "completion_type": "single",
                "questions": {}
            }),
            ("survey2", {
                "title": "survey2",
                "description": "survey2",
                "completion_type": "single",
                "questions": {}
            }),
            ("survey3", {
                "title": "survey3",
                "description": "survey3",
                "completion_type": "single",
                "questions": {}
            })
        ]

        mock_survey_ref = self.mox.CreateMockAnything()
        survey_ref = {
            "surveys": mock_survey_ref
        }

        self.mock._get_survey_reference_data(survey_key=None).AndReturn(survey_ref)

        survey2 = self.mox.CreateMockAnything()
        survey2.key = "survey2"
        survey2.title = "survey2"
        survey2.description = "survey2"
        survey2.completion_type = "single"

        survey3 = self.mox.CreateMockAnything()
        survey3.key = "survey3"
        survey3.title = "asdf"
        survey3.description = "asdf"
        survey3.completion_type = "asdf"

        survey4 = self.mox.CreateMockAnything()
        survey4.key = "survey4"
        survey4.title = "survey4"
        survey4.description = "survey4"
        survey4.completion_type = "single"

        self.mock.Survey.find_all().AndReturn([survey2, survey3, survey4])

        mock_survey_ref.iteritems().AndReturn(surveys)

        self.mock.Survey.create(key="survey1", title="survey1", description="survey1", completion_type="single").AndReturn("survey")
        self.mock._manage_survey_questions("survey", {})

        self.mock._manage_survey_questions(survey2, {})

        survey3.update(title="survey3", description="survey3", completion_type="single")
        self.mock.Survey.get("survey3").AndReturn(survey3)
        self.mock._manage_survey_questions(survey3, {})

        survey4.delete()

        self.mox.ReplayAll()
        RetailDataHelper._manage_surveys(self.mock)

    ###########################################
    # RetailDataHelper._manage_survey_questions()

    def test_manage_survey_questions(self):

        questions = [
            ("question1", {
                "index": 0,
                "type": "question1",
                "text": "question1",
                "branch": "question1",
                "min_answer_length": None,
                "answers": {}
            }),
            ("question2", {
                "index": 1,
                "type": "question2",
                "text": "question2",
                "branch": "question2",
                "min_answer_length": None,
                "answers": {}
            }),
            ("question3", {
                "index": 2,
                "type": "question3",
                "text": "question3",
                "branch": "question3",
                "min_answer_length": 42,
                "answers": {}
            })
        ]

        mock_survey = self.mox.CreateMockAnything()
        mock_question_ref = self.mox.CreateMockAnything()

        question2 = self.mox.CreateMockAnything()
        question2.key = "question2"
        question2.type = "question2"
        question2.index = 1
        question2.text = "question2"
        question2.branch = "question2"
        question2.min_answer_length = None

        question3 = self.mox.CreateMockAnything()
        question3.key = "question3"
        question3.index = 2
        question3.type = "asdf"
        question3.text = "asdf"
        question3.branch = "asdf"
        question2.min_answer_length = None

        question4 = self.mox.CreateMockAnything()
        question4.key = "question4"
        question4.index = 3
        question4.type = "question4"
        question4.text = "question4"
        question4.branch = "question4"
        question2.min_answer_length = None

        self.mock.SurveyQuestion.find_all(survey=mock_survey).AndReturn([question2, question3, question4])

        mock_question_ref.iteritems().AndReturn(questions)

        self.mock.SurveyQuestion.create(survey=mock_survey, key="question1", text="question1", type="question1", index=0, branch="question1").AndReturn("question1")
        self.mock._manage_survey_answers(mock_survey, "question1", {})

        # we expect no changes for question 2
        self.mock._manage_survey_answers(mock_survey, question2, {})

        question3.update(type="question3", index=2, text="question3", branch="question3", min_answer_length=42)
        self.mock.SurveyQuestion.get("question3").AndReturn(question3)
        self.mock._manage_survey_answers(mock_survey, question3, {})

        mock_survey.update(questions=["question1", question2, question3])

        question4.delete()

        self.mox.ReplayAll()
        RetailDataHelper._manage_survey_questions(self.mock, mock_survey, mock_question_ref)

    ###########################################
    # RetailDataHelper._manage_survey_answers()

    def test_manage_survey_answers(self):

        answers = [
            ("answer1", {
                "index": 0,
                "branch": "answer1",
                "text": "answer1"
            }),
            ("answer2", {
                "index": 1,
                "branch": "answer2",
                "text": "answer2"
            }),
            ("answer3", {
                "index": 2,
                "branch": "answer3",
                "text": "answer3"
            })
        ]

        mock_survey = self.mox.CreateMockAnything()
        mock_question = self.mox.CreateMockAnything()
        mock_answer_ref = self.mox.CreateMockAnything()

        answer2 = self.mox.CreateMockAnything()
        answer2.key = "answer2"
        answer2.index = 1
        answer2.text = "answer2"
        answer2.branch = "answer2"

        answer3 = self.mox.CreateMockAnything()
        answer3.key = "answer3"
        answer3.index = 1
        answer3.text = "asdf"
        answer3.branch = "asdf"

        answer4 = self.mox.CreateMockAnything()
        answer4.key = "answer4"
        answer4.index = 3
        answer4.text = "answer4"
        answer4.branch = "answer4"

        self.mock.SurveyAnswer.find_all(survey=mock_survey, question=mock_question).AndReturn([answer2, answer3, answer4])

        mock_answer_ref.iteritems().AndReturn(answers)

        self.mock.SurveyAnswer.create(survey=mock_survey, question=mock_question, key="answer1", text="answer1", branch="answer1", index=0).AndReturn("answer1")

        answer3.update(text="answer3", index=2, branch="answer3")
        self.mock.SurveyAnswer.get("answer3").AndReturn(answer3)

        mock_question.update(answers=["answer1", answer2, answer3])

        answer4.delete()

        self.mox.ReplayAll()
        RetailDataHelper._manage_survey_answers(self.mock, mock_survey, mock_question, mock_answer_ref)


if __name__ == '__main__':
    unittest.main()
