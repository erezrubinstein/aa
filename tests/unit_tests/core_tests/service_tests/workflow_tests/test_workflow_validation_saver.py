import mox

from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import BadRequestError
from core.common.utilities.helpers import generate_id
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.workflow_validation_helpers.workflow_validation_saver import WorkflowValidationSaver


__author__ = 'vgold'


class WorkflowValidationSaverTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(WorkflowValidationSaverTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get several dependencies that we'll need in the class
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(WorkflowValidationSaver)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.QCTaskCreator = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_workflow_validation_saver.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

        self.mock.context = self.context

    def doCleanups(self):

        super(WorkflowValidationSaverTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # WorkflowValidationSaver._get_and_validate_task()

    def test_get_and_validate_task(self):
    
        workflow_validation_saver = WorkflowValidationSaver.__new__(WorkflowValidationSaver)

        correct_request_data = {"taskID": "taskID"}
        correct_context = {"user_id": 1}

        # Invalid request_data
        workflow_validation_saver.request_data = None
        workflow_validation_saver.context = correct_context
        workflow_validation_saver.logger = self.mock.logger
        self.assertRaises(BadRequestError, workflow_validation_saver._get_and_validate_task)

        # Invalid request_data
        workflow_validation_saver.request_data = {}
        workflow_validation_saver.context = correct_context
        self.assertRaises(BadRequestError, workflow_validation_saver._get_and_validate_task)

        # TODO: Complete this test

        # Correct
        # workflow_validation_saver.request_data = correct_request_data
        # workflow_validation_saver.context = correct_context
        # result = workflow_validation_saver._get_and_validate_task()
        # self.assertEqual(result, workflow_validation_saver)

    ##########################################################################
    # WorkflowValidationSaver._create_and_checkout_qc_task_if_necessary()

    # def test_create_and_checkout_qc_task_if_necessary__qc_decision(self):
    #
    #     request_data = {"decision": "qc"}
    #     rir_id = generate_id()
    #     rir = {"_id": rir_id}
    #
    #     qc_task_data = {
    #         "rirID": rir["_id"],
    #         "stage": "new_store_validation_qc"
    #     }
    #
    #     qc_task_creator = self.mox.CreateMockAnything()
    #     self.mock.QCTaskCreator(qc_task_data, self.context).AndReturn(qc_task_creator)
    #
    #     qc_task = "qc_task"
    #     qc_task_creator.run().AndReturn(qc_task)
    #
    #     self.mox.ReplayAll()
    #
    #     self.mock.request_data = request_data
    #     self.mock.rir = rir
    #     result = WorkflowValidationSaver._create_and_checkout_qc_task_if_necessary(self.mock)
    #     self.assertEqual(result, self.mock)
    #     self.assertEqual(qc_task, self.mock.qc_task)
    #
    # def test_create_and_checkout_qc_task_if_necessary__link_decision(self):
    #
    #     request_data = {"decision": "link"}
    #
    #     self.mox.ReplayAll()
    #
    #     self.mock.request_data = request_data
    #     self.mock.qc_task = None
    #
    #     result = WorkflowValidationSaver._create_and_checkout_qc_task_if_necessary(self.mock)
    #
    #     self.assertEqual(result, self.mock)
    #     self.assertEqual(None, self.mock.qc_task)

    ##########################################################################
    # WorkflowValidationSaver.()

    # def test(self):
    #     pass

