from core.service.svc_workflow.helpers.atomic_workflow_validation_task_retriever import AtomicWorkflowValidationTaskRetriever
from core.service.svc_workflow.implementation.workflow_service import WorkflowService
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import *
import unittest
import mox


__author__ = 'vgold'


class AtomicWorkflowValidationTaskRetrieverTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AtomicWorkflowValidationTaskRetrieverTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock_svc = self.mox.CreateMock(WorkflowService)
        self.mock_svc.mongo_access = self.mox.CreateMockAnything()
        self.mock_svc.AtomicWorkflowValidationTaskRetriever = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock_svc.cfg = Dependency("MoxConfig").value
        self.mock_svc.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {
            "user_id": 1,
            "source": "test_workflow_service.py",
            "user": {"user_id": 1, "is_generalist": False},
            "team_industries": ["asdf"]
        }

    def doCleanups(self):
        super(AtomicWorkflowValidationTaskRetrieverTests, self).doCleanups()
        dependencies.clear()

    ############################################################
    # AtomicWorkflowValidationTaskRetriever._validate_context()

    def test_validate_context(self):

        no_user_context = {k: v for k, v in self.context.iteritems() if k != "user"}
        awv = AtomicWorkflowValidationTaskRetriever(None, None, None, None, no_user_context)
        with self.assertRaises(BadRequestError):
            awv._validate_context()

        empty_user_context = dict(self.context, user=None)
        awv = AtomicWorkflowValidationTaskRetriever(None, None, None, None, empty_user_context)
        with self.assertRaises(BadRequestError):
            awv._validate_context()

        invalid_user_context = dict(self.context, user={"user_id": 1})
        awv = AtomicWorkflowValidationTaskRetriever(None, None, None, None, invalid_user_context)
        with self.assertRaises(BadRequestError):
            awv._validate_context()

        no_team_industries_context = {k: v for k, v in self.context.iteritems() if k != "team_industries"}
        awv = AtomicWorkflowValidationTaskRetriever(None, None, None, None, no_team_industries_context)
        with self.assertRaises(BadRequestError):
            awv._validate_context()

        empty_team_industries_context = dict(self.context, team_industries=[])
        awv = AtomicWorkflowValidationTaskRetriever(None, None, None, None, empty_team_industries_context)
        with self.assertRaises(BadRequestError):
            awv._validate_context()

        generalist_no_team_industries_context = dict(self.context, user={"user_id": 1, "is_generalist": True})
        awv = AtomicWorkflowValidationTaskRetriever(None, None, None, None, generalist_no_team_industries_context)
        # No errors raised
        awv._validate_context()


if __name__ == '__main__':
    unittest.main()