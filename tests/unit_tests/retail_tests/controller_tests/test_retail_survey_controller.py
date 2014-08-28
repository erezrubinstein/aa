from retail.v010.data_access.controllers.survey_controller import SurveyController
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.errors import BadRequestError
from collections import defaultdict
import unittest
import mox


__author__ = 'vgold'


class RetailSurveyControllerTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(RetailSurveyControllerTests, self).setUp()
        # register mock dependencies
        register_common_mox_dependencies(self.mox)
        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value
        # Create caller context
        self.context = {"user_id": 1, "source": "test_retail_survey_controller.py"}
        # Set up useful mocks
        self.mock = self.mox.CreateMock(SurveyController)
        self.mock.User = self.mox.CreateMockAnything()
        self.mock.Survey = self.mox.CreateMockAnything()
        self.mock.SurveyQuestion = self.mox.CreateMockAnything()
        self.mock.SurveyAnswer = self.mox.CreateMockAnything()
        self.mock.UserSurveyResponse = self.mox.CreateMockAnything()

    def doCleanups(self):
        super(RetailSurveyControllerTests, self).doCleanups()
        dependencies.clear()

    ####################################################
    # SurveyController.user_has_completed_survey()
    
    def test_user_has_completed_survey(self):

        survey_ctrl = SurveyController()
        user = self.mox.CreateMockAnything()

        user.survey_completion = {}
        result = survey_ctrl.user_has_completed_survey(user, "test_survey")
        self.assertFalse(result)

        user.survey_completion = {
            "test_survey": 0
        }
        result = survey_ctrl.user_has_completed_survey(user, "test_survey")
        self.assertFalse(result)

        user.survey_completion = {
            "test_survey": 1
        }
        result = survey_ctrl.user_has_completed_survey(user, "test_survey")
        self.assertTrue(result)

    ####################################################
    # SurveyController.create_user_survey_response()

    def test_create_user_survey_response__bad_request_error(self):

        survey_ctrl = SurveyController()
        user = "user"

        params = {}
        with self.assertRaises(BadRequestError):
            survey_ctrl.create_user_survey_response(user, params)

        params = {"survey_key": None, "question_answer_map": None}
        with self.assertRaises(BadRequestError):
            survey_ctrl.create_user_survey_response(user, params)
        params = {"survey_key": "", "question_answer_map": {}}
        with self.assertRaises(BadRequestError):
            survey_ctrl.create_user_survey_response(user, params)
        params = {"survey_key": "test_survey1", "question_answer_map": {}}
        with self.assertRaises(BadRequestError):
            survey_ctrl.create_user_survey_response(user, params)
        params = {"survey_key": "", "question_answer_map": {"test_q1": "test_a1"}}
        with self.assertRaises(BadRequestError):
            survey_ctrl.create_user_survey_response(user, params)

        params = {
            "survey_key": "test_survey1",
            "question_answer_map": {
                "test_q1": "test_a1"
            }
        }
        survey_ctrl.Survey = {}
        with self.assertRaises(BadRequestError):
            survey_ctrl.create_user_survey_response(user, params)

        params = {
            "survey_key": "test_survey1",
            "question_answer_map": {
                "test_q1": "test_a1"
            }
        }
        survey_ctrl.Survey = {
            "survey_key": None
        }
        with self.assertRaises(BadRequestError):
            survey_ctrl.create_user_survey_response(user, params)

    def test_create_user_survey_response__survey_completed(self):

        user = "user"
        survey_key = "test_survey1"
        params = {
            "survey_key": survey_key,
            "question_answer_map": {
                "test_q1": "test_a1"
            }
        }

        survey = self.mox.CreateMockAnything()
        survey.completion_type = "single"
        self.mock.Survey.get(survey_key).AndReturn(survey)

        self.mock.user_has_completed_survey(user, survey_key).AndReturn(True)

        self.mox.ReplayAll()

        result = SurveyController.create_user_survey_response(self.mock, user, params)
        self.assertEqual(result, {})

    def test_create_user_survey_response(self):

        user = "user"
        survey_key = "test_survey1"
        question_answer_map = {
            "test_q1": "test_a1"
        }
        params = {
            "survey_key": survey_key,
            "question_answer_map": question_answer_map
        }
        survey = self.mox.CreateMockAnything()
        survey.completion_type = "multiple"
        question_dict = "question_dict"
        answer_dict = "answer_dict"
        valid_question_answer_dict = "valid_question_answer_dict"
        survey_validation_dict = "survey_validation_dict"
        user_survey_responses = "user_survey_responses"

        self.mock.Survey.get(survey_key).AndReturn(survey)
        self.mock._create_survey_dictionaries(survey).AndReturn((question_dict, answer_dict, valid_question_answer_dict))
        self.mock._create_clean_question_answer_map(question_dict, answer_dict, valid_question_answer_dict,
                                                    question_answer_map).AndReturn(question_answer_map)
        self.mock._create_survey_validation_dict(question_dict, answer_dict).AndReturn(survey_validation_dict)
        self.mock._validate_user_question_answer_map(question_dict, question_answer_map, survey_validation_dict)
        self.mock._create_user_survey_responses_and_update_user(user, survey, question_dict, answer_dict,
                                                                question_answer_map).AndReturn(user_survey_responses)

        self.mox.ReplayAll()

        result = SurveyController.create_user_survey_response(self.mock, user, params)
        self.assertEqual(result, user_survey_responses)

    #####################################################
    ## SurveyController._create_survey_dictionaries()
    #
    def test_create_survey_dictionaries(self):

        survey = "survey"
        answers = [
            self.__create_mock_answer_with_question("a1", "q1"),
            self.__create_mock_answer_with_question("a2", "q2"),
            self.__create_mock_answer_with_question("a3", "q3")
        ]
        question_dict, answer_dict, valid_question_answer_dict = self.__create_question_answer_valid_dicts(answers)

        self.mock.SurveyAnswer.find_all(survey=survey).AndReturn(answers)

        self.mox.ReplayAll()

        result = SurveyController._create_survey_dictionaries(self.mock, survey)
        self.assertEqual(result, (question_dict, answer_dict, valid_question_answer_dict))

    ####################################################
    # SurveyController._create_clean_question_answer_map()

    def test_create_clean_question_answer_map(self):

        answers = [
            self.__create_mock_answer_with_question("a1", "q1"),
            self.__create_mock_answer_with_question("a2", "q2"),
            self.__create_mock_answer_with_question("a3", "q3")
        ]
        question_dict, answer_dict, valid_question_answer_dict = self.__create_question_answer_valid_dicts(answers)

        question_answer_map = {
            "q1": "a1",
            "asdf": "asdf",
            "q2": "asdf",
            "qwer": "a3"
        }
        clean_question_answer_map = {
            "q1": "a1"
        }

        result = SurveyController._create_clean_question_answer_map(self.mock, question_dict, answer_dict,
                                                                    valid_question_answer_dict, question_answer_map)
        self.assertEqual(result, clean_question_answer_map)

    ####################################################
    # SurveyController._create_survey_validation_dict()

    def test_create_survey_validation_dict(self):

        question_dict = "question_dict"
        answer_dict = "answer_dict"

        def add_to_dict(q, a, v, bv, branch, root=False):
            v["asdf"] = "asdf"

        self.mock._create_survey_validation_dict_recursive(question_dict, answer_dict, {}, {}, None, root=True).WithSideEffects(add_to_dict)

        self.mox.ReplayAll()

        result = SurveyController._create_survey_validation_dict(self.mock, question_dict, answer_dict)
        self.assertEqual(result, {"asdf": "asdf"})

    ####################################################
    # SurveyController._validate_user_question_answer_map()

    def test_validate_user_question_answer_map__no_invalid_questions(self):

        mock_question = self.mox.CreateMockAnything()
        mock_question.branch = None
        question_dict = {"q1": mock_question}
        question_answer_map = {"q1": "ohyeah"}
        survey_validation_dict = {"root": "survey_validation_dict"}

        self.mock._validate_user_question_answer_map_recursive(question_dict, question_answer_map, survey_validation_dict["root"]).AndReturn([])

        self.mox.ReplayAll()

        result = SurveyController._validate_user_question_answer_map(self.mock, question_dict, question_answer_map, survey_validation_dict)
        self.assertEqual(result, defaultdict(list))

    def test_validate_user_question_answer_map__invalid_questions(self):

        mock_question = self.mox.CreateMockAnything()
        mock_question.key = "q1"
        mock_question.branch = None
        question_dict = {"q1": mock_question}
        question_answer_map = {"q1": "ohyeah"}
        survey_validation_dict = {"root": "survey_validation_dict"}

        self.mock._validate_user_question_answer_map_recursive(question_dict, question_answer_map, survey_validation_dict["root"]).AndReturn([mock_question])

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            SurveyController._validate_user_question_answer_map(self.mock, question_dict, question_answer_map, survey_validation_dict)

    ####################################################
    # SurveyController._create_user_survey_responses_and_update_user()

    def test_create_user_survey_responses_and_update_user(self):

        user = self.mox.CreateMockAnything()
        user.email = "email"
        user.survey_completion = {}
        survey = self.mox.CreateMockAnything()
        survey.key = "key"
        mock_question_answer_map = self.mox.CreateMockAnything()
        question_answer_map_list = [
            ("q1", "a1"),
            ("q2", {"a2": "HIYA!"}),
            ("q3", ["a3", "a4"])
        ]
        mock_question1 = self.mox.CreateMockAnything()
        mock_question1.type = "single_choice"
        mock_question1.key = "q1"
        mock_question2 = self.mox.CreateMockAnything()
        mock_question2.type = "single_choice"
        mock_question2.key = "q2"
        mock_question3 = self.mox.CreateMockAnything()
        mock_question3.type = "single_choice"
        mock_question3.key = "q3"
        question_dict = {
            "q1": mock_question1,
            "q2": mock_question2,
            "q3": mock_question3
        }
        answer_dict = {
            "a1": "a1",
            "a2": "a2",
            "a3": "a3",
            "a4": "a4"
        }

        self.mock.User.get(user.email).AndReturn(user)
        mock_question_answer_map.iteritems().AndReturn(question_answer_map_list)
        self.mock.UserSurveyResponse.create(serialize=True, user=user, survey=survey, question=mock_question1, answer="a1").AndReturn("usr1")
        self.mock.UserSurveyResponse.create(serialize=True, user=user, survey=survey, question=mock_question2, answer="a2", response="HIYA!").AndReturn("usr2")
        self.mock.UserSurveyResponse.create(serialize=True, user=user, survey=survey, question=mock_question3, answer="a3").AndReturn("usr3")
        self.mock.UserSurveyResponse.create(serialize=True, user=user, survey=survey, question=mock_question3, answer="a4").AndReturn("usr4")
        user.save()

        self.mox.ReplayAll()

        result = SurveyController._create_user_survey_responses_and_update_user(self.mock, user, survey, question_dict,
                                                                                answer_dict, mock_question_answer_map)
        self.assertEqual(result, ["usr1", "usr2", "usr3", "usr4"])
        self.assertEqual(user.survey_completion, {"key": 1})

    ####################################################
    # SurveyController._create_survey_validation_dict_recursive()

    def test_create_survey_validation_dict_recursive(self):

        survey_ctrl = SurveyController()
        question_dict, answer_dict, expected_result = self.__create_full_sample_question_answer_valid_dicts()

        survey_validation_dict = {}

        survey_ctrl._create_survey_validation_dict_recursive(question_dict, answer_dict, survey_validation_dict, {}, None,
                                                             root=True)
        self.assertEqual(survey_validation_dict, expected_result)

    ####################################################
    # SurveyController._validate_user_question_answer_map_recursive()

    def test_validate_user_question_answer_map_recursive(self):

        survey_ctrl = SurveyController()
        question_dict, _, survey_validation_dict = self.__create_full_sample_question_answer_valid_dicts()

        question_answer_map = {
            "q1": "a11",
            "q2": "a21"
        }
        invalid_questions = survey_ctrl._validate_user_question_answer_map_recursive(question_dict, question_answer_map,
                                                                                     survey_validation_dict["branch1"])
        self.assertEqual(invalid_questions, [])

        question_answer_map = {
            "q1": "a12",
            "q3": "a32"
        }
        invalid_questions = survey_ctrl._validate_user_question_answer_map_recursive(question_dict, question_answer_map,
                                                                                     survey_validation_dict["branch2"])
        self.assertEqual(invalid_questions, [])

        question_answer_map = {
            "q1": "a12",
            "q3": "a31",
            "q4": "a43"
        }
        invalid_questions = survey_ctrl._validate_user_question_answer_map_recursive(question_dict, question_answer_map,
                                                                                     survey_validation_dict["branch3"])
        self.assertEqual(invalid_questions, [])

        # missing 1 answer
        question_answer_map = {
            "q1": "a11"
        }
        invalid_questions = survey_ctrl._validate_user_question_answer_map_recursive(question_dict, question_answer_map,
                                                                                     survey_validation_dict["branch1"])
        self.assertEqual(len(invalid_questions), 1)

        # missing all answers
        question_answer_map = {}
        invalid_questions = survey_ctrl._validate_user_question_answer_map_recursive(question_dict, question_answer_map,
                                                                                     survey_validation_dict["branch1"])
        self.assertEqual(len(invalid_questions), 2)

    ##---------------------------------------# Private Helpers #---------------------------------------#

    def __create_mock_answer_with_question(self, akey, qkey):
        q = self.mox.CreateMockAnything()
        q.key = qkey
        a = self.mox.CreateMockAnything()
        a.key = akey
        a.question = q
        return a

    def __create_question_answer_valid_dicts(self, answers):
        question_dict = {
            a.question.key: a.question
            for a in answers
        }
        answer_dict = {
            a.key: a
            for a in answers
        }
        valid_question_answer_dict = {
            a.question.key: {a.key}
            for a in answers
        }

        return question_dict, answer_dict, valid_question_answer_dict

    def __create_full_sample_question_answer_valid_dicts(self):

        q1 = self.mox.CreateMockAnything()
        q1.branch = None
        q1.type = "single_choice"

        a11 = self.mox.CreateMockAnything()
        a11.branch = "branch1"
        a11.key = "a11"
        a12 = self.mox.CreateMockAnything()
        a12.branch = "branch2"
        a12.key = "a12"
        a13 = self.mox.CreateMockAnything()
        a13.branch = None
        a13.key = "a13"

        q1.answers = [a11, a12, a13]

        q2 = self.mox.CreateMockAnything()
        q2.branch = "branch1"
        q2.type = "single_choice"

        a21 = self.mox.CreateMockAnything()
        a21.branch = None
        a21.key = "a21"
        a22 = self.mox.CreateMockAnything()
        a22.branch = None
        a22.key = "a22"
        a23 = self.mox.CreateMockAnything()
        a23.branch = None
        a23.key = "a23"

        q2.answers = [a21, a22, a23]

        q3 = self.mox.CreateMockAnything()
        q3.branch = "branch2"
        q3.type = "single_choice"

        a31 = self.mox.CreateMockAnything()
        a31.branch = "branch3"
        a31.key = "a31"
        a32 = self.mox.CreateMockAnything()
        a32.branch = None
        a32.key = "a32"
        a33 = self.mox.CreateMockAnything()
        a33.branch = None
        a33.key = "a33"

        q3.answers = [a31, a32, a33]

        q4 = self.mox.CreateMockAnything()
        q4.branch = "branch3"
        q4.type = "single_choice"

        a41 = self.mox.CreateMockAnything()
        a41.branch = None
        a41.key = "a41"
        a42 = self.mox.CreateMockAnything()
        a42.branch = None
        a42.key = "a42"
        a43 = self.mox.CreateMockAnything()
        a43.branch = None
        a43.key = "a43"

        q4.answers = [a41, a42, a43]

        question_dict = {
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4
        }

        answer_dict = {
            "a11": a11,
            "a12": a12,
            "a13": a13,
            "a21": a21,
            "a22": a22,
            "a23": a23,
            "a31": a31,
            "a32": a32,
            "a33": a33,
            "a41": a41,
            "a42": a42,
            "a43": a43
        }

        survey_validation_dict = {
            "root": {
                "q1": {
                    "a11": {},
                    "a12": {},
                    "a13": {},
                }
            },
            "branch1": {
                "q1": {
                    "a11": {},
                    "a12": {},
                    "a13": {}
                },
                "q2": {
                    "a21": {},
                    "a22": {},
                    "a23": {}
                }
            },
            "branch2": {
                "q1": {
                    "a11": {},
                    "a12": {},
                    "a13": {}
                },
                "q3": {
                    "a31": {},
                    "a32": {},
                    "a33": {}
                }
            },
            "branch3": {
                "q1": {
                    "a11": {},
                    "a12": {},
                    "a13": {}
                },
                "q4": {
                    "a41": {},
                    "a42": {},
                    "a43": {}
                }
            },
        }

        return question_dict, answer_dict, survey_validation_dict


if __name__ == '__main__':
    unittest.main()
