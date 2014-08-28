import unittest
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.service_access.utilities.errors import RecInputError
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.workflow_validation_helpers.abstract_workflow_validation_undoer import AbstractWorkflowValidationUndoer
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.workflow_validation_helpers.add_rir_workflow_validation_undoer import AddRirWorkflowValidationUndoer


class WorkflowValidationUndoerTests(mox.MoxTestBase):
    def setUp(self):
        super(WorkflowValidationUndoerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Create caller context
        self.context = {"user_id": 1, "source": "test_workflow_validation_undoer.py"}


    def doCleanups(self):
        super(WorkflowValidationUndoerTests, self).doCleanups()
        dependencies.clear()


    def test_base__get_task_target_rir_id(self):
        target_rir_id = 'cheesesteak truck'
        task_to_undo_data = {
            'input': {
                'target_rir_id': target_rir_id
            }
        }
        undoer = AbstractWorkflowValidationUndoer(task_to_undo_data, self.context)
        undoer._AbstractWorkflowValidationUndoer__get_task_target_rir_id()

        self.assertEqual(undoer.target_rir_id, target_rir_id)


    def test_base__get_task_target_rir_id__exception(self):
        task_to_undo_data = {}
        undoer = AbstractWorkflowValidationUndoer(task_to_undo_data, self.context)

        with self.assertRaises(RecInputError) as cm:
            undoer._AbstractWorkflowValidationUndoer__get_task_target_rir_id()
        self.assertEqual(cm.exception.message, "Missing 'target_rir_id' in task['input']")


    def test_add_rir__check_if_task_target_is_or_was_most_correct__true_link(self):
        task_to_undo_data = {
            'output': {
                'decision': 'link',
                'dataToUse': 'target'
            }
        }
        undoer = AddRirWorkflowValidationUndoer(task_to_undo_data, self.context)
        undoer._AddRirWorkflowValidationUndoer__check_if_task_target_rir_is_or_was_most_correct()

        self.assertEqual(undoer.target_rir_is_or_was_most_correct, True)


    def test_add_rir__check_if_task_target_is_or_was_most_correct__false_link(self):
        task_to_undo_data = {
            'output': {
                'decision': 'link',
                'dataToUse': 'existing'
            }
        }
        undoer = AddRirWorkflowValidationUndoer(task_to_undo_data, self.context)
        undoer._AddRirWorkflowValidationUndoer__check_if_task_target_rir_is_or_was_most_correct()

        self.assertEqual(undoer.target_rir_is_or_was_most_correct, False)


    def test_add_rir__check_if_task_target_is_or_was_most_correct__true_nolink(self):
        task_to_undo_data = {
            'output': {
                'decision': 'no-link',
                'downstream': 'open'
            }
        }
        undoer = AddRirWorkflowValidationUndoer(task_to_undo_data, self.context)
        undoer._AddRirWorkflowValidationUndoer__check_if_task_target_rir_is_or_was_most_correct()

        self.assertEqual(undoer.target_rir_is_or_was_most_correct, True)


    def test_add_rir__check_if_task_target_is_or_was_most_correct__true_nolink(self):
        task_to_undo_data = {
            'output': {
            }
        }
        undoer = AddRirWorkflowValidationUndoer(task_to_undo_data, self.context)

        with self.assertRaises(RecInputError) as cm:
            undoer._AddRirWorkflowValidationUndoer__check_if_task_target_rir_is_or_was_most_correct()
        self.assertEqual(cm.exception.message, "Missing 'decision' in task['output']")

