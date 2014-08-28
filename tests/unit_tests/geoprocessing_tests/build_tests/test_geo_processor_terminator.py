from common.helpers.mock_providers.mock_cloud_provider import MockStack
from geoprocessing.build.amazon_cloud_formation.geo_processing_terminator import GeoProcessingTerminator
from common.utilities.inversion_of_control import dependencies, Dependency
from common.helpers.amazon_cloud_provider import EC2Status
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
#from geoprocessing.tests.unit_tests.mock_providers.mock_cloud_provider import MockStack

__author__ = 'erezrubinstein'

import unittest

class GeoProcessorTerminatorTests(unittest.TestCase):
    def setUp(self):
        # set up dependencies
        register_mock_dependencies()
        self.cloud_provider = Dependency("CloudProviderNewEnvironment").value
        self.email_provider = Dependency("EmailProvider").value
        self.config = Dependency("Config").value

        # set up terminator
        self._terminator = GeoProcessingTerminator()

    def doCleanups(self):
        dependencies.clear()

    def test_non_supported_stack(self):
        """
        Verify that a stack that is not a geo processor worker is ignored
        """
        # set up mock with a fake status
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "unknown status", "DifferentStack"))

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the stack was ignored
        self.assertEqual(len(self._terminator._ignored_workers), 1)
        self.assertTrue(self._terminator._ignored_workers.has_key("stack-1"))
        self.assertEqual(self._terminator._ignored_workers["stack-1"], "Ignored stack with name:DifferentStack")


    def test_unknown_stack_status(self):
        """
        Verify that a stack with an unknown status is ignored
        """
        # set up mock with a fake status
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "unknown status"))

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the stack was ignored
        self.assertEqual(len(self._terminator._failed_actions), 1)
        self.assertTrue(self._terminator._failed_actions.has_key("stack-1"))
        self.assertEqual(self._terminator._failed_actions["stack-1"], "Unrecognized status: unknown status")


    def test_create_failed_status(self):
        """
        Verify that a stack with a CREATE_FAILED status is deleted
        """
        # set up mock with a CREATE_FAILED status
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "CREATE_FAILED"))

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the stack was deleted
        self.assertEqual(len(self.cloud_provider.deleted_stacks), 1)
        self.assertIn("stack-1", self.cloud_provider.deleted_stacks)
        self.assertEqual(len(self._terminator._successful_actions), 1)
        self.assertTrue(self._terminator._successful_actions.has_key("stack-1"))
        self.assertEqual(self._terminator._successful_actions["stack-1"], "Deleted STACK_ID:stack-1 | STATUS:CREATE_FAILED")


    def test_rollback_failed_status(self):
        """
        Verify that a stack with a ROLLBACK_FAILED status is deleted
        """
        # set up mock with a ROLLBACK_FAILED status
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "ROLLBACK_FAILED"))

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the stack was deleted
        self.assertEqual(len(self.cloud_provider.deleted_stacks), 1)
        self.assertIn("stack-1", self.cloud_provider.deleted_stacks)
        self.assertEqual(len(self._terminator._successful_actions), 1)
        self.assertTrue(self._terminator._successful_actions.has_key("stack-1"))
        self.assertEqual(self._terminator._successful_actions["stack-1"], "Deleted STACK_ID:stack-1 | STATUS:ROLLBACK_FAILED")


    def test_rollback_complete_status(self):
        """
        Verify that a stack with a ROLLBACK_COMPLETE status is deleted
        """
        # set up mock with a ROLLBACK_COMPLETE status
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "ROLLBACK_COMPLETE"))

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the stack was deleted
        self.assertEqual(len(self.cloud_provider.deleted_stacks), 1)
        self.assertIn("stack-1", self.cloud_provider.deleted_stacks)
        self.assertEqual(len(self._terminator._successful_actions), 1)
        self.assertTrue(self._terminator._successful_actions.has_key("stack-1"))
        self.assertEqual(self._terminator._successful_actions["stack-1"], "Deleted STACK_ID:stack-1 | STATUS:ROLLBACK_COMPLETE")


    def test_delete_failed_status(self):
        """
        Verify that a stack with a DELETE_FAILED status is deleted
        """
        # set up mock with a DELETE_FAILED status
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "DELETE_FAILED"))

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that server is being deleted
        self.assertEqual(len(self.cloud_provider.deleted_stacks), 1)
        self.assertIn("stack-1", self.cloud_provider.deleted_stacks)
        self.assertEqual(len(self._terminator._successful_actions), 1)
        self.assertTrue(self._terminator._successful_actions.has_key("stack-1"))
        self.assertEqual(self._terminator._successful_actions["stack-1"], "Deleted STACK_ID:stack-1 | STATUS:DELETE_FAILED")


    def test_created_worker_has_less_than_1_hour(self):
        # set up mocks
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "CREATE_COMPLETE"))
        self.cloud_provider.ec2_instance_ids["stack-1"] = "instance-1"
        self.cloud_provider.ec2_instance_statuses["instance-1"] = EC2Status.Running
        self.cloud_provider.average_cpu_stats["stack-1"] = None

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the server was properly ignored
        self.assertEqual(len(self._terminator._ignored_workers), 1)
        self.assertTrue(self._terminator._ignored_workers.has_key("stack-1"))
        self.assertEqual(self._terminator._ignored_workers["stack-1"], "Server is up for less than 4 hours. STACK_ID:stack-1")


    def test_running_worker_has_high_cpu_do_not_stop(self):
        # set up mocks
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "CREATE_COMPLETE"))
        self.cloud_provider.ec2_instance_ids["stack-1"] = "instance-1"
        self.cloud_provider.ec2_instance_statuses["instance-1"] = EC2Status.Running
        # set the CPU average to just above the current threshold (2%)
        self.cloud_provider.average_cpu_stats["instance-1"] = 2.1

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the server was properly ignored
        self.assertEqual(len(self._terminator._ignored_workers), 1)
        self.assertTrue(self._terminator._ignored_workers.has_key("stack-1"))
        self.assertEqual(self._terminator._ignored_workers["stack-1"], "Still working.  STACK_ID:stack-1  AVERAGE_CUP:2.100000")


    def test_running_worker_is_ready_to_stop(self):
        # set up mocks
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "CREATE_COMPLETE"))
        self.cloud_provider.ec2_instance_ids["stack-1"] = "instance-1"
        self.cloud_provider.ec2_instance_statuses["instance-1"] = EC2Status.Running
        # set the CPU average to just under the current threshold (1%)
        self.cloud_provider.average_cpu_stats["instance-1"] = 0.9

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the server was properly stopped
        self.assertEqual(len(self.cloud_provider.stopped_instances), 1)
        self.assertIn("instance-1", self.cloud_provider.stopped_instances)
        self.assertEqual(len(self._terminator._successful_actions), 1)
        self.assertTrue(self._terminator._successful_actions.has_key("stack-1"))
        self.assertEqual(self._terminator._successful_actions["stack-1"], "EC2 instance stopped.  STACK_ID:stack-1  AVERAGE_CUP:0.900000")


    def test_running_worker_is_ready_to_stop__honkin_GIS(self):
        # set up mocks
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "CREATE_COMPLETE", "HonkinGISWorker-1"))
        self.cloud_provider.ec2_instance_ids["stack-1"] = "instance-1"
        self.cloud_provider.ec2_instance_statuses["instance-1"] = EC2Status.Running
        # set the CPU average to just under the current threshold (2%)
        self.cloud_provider.average_cpu_stats["instance-1"] = 0.9

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the server was properly stopped
        self.assertEqual(len(self.cloud_provider.stopped_instances), 1)
        self.assertIn("instance-1", self.cloud_provider.stopped_instances)
        self.assertEqual(len(self._terminator._successful_actions), 1)
        self.assertTrue(self._terminator._successful_actions.has_key("stack-1"))
        self.assertEqual(self._terminator._successful_actions["stack-1"], "EC2 instance stopped.  STACK_ID:stack-1  AVERAGE_CUP:0.900000")



    def test_stopped_worker_is_ignored(self):
        # set up mocks
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "CREATE_COMPLETE"))
        self.cloud_provider.ec2_instance_ids["stack-1"] = "instance-1"
        self.cloud_provider.ec2_instance_statuses["instance-1"] = EC2Status.Stopped
        # set the CPU average to just under the current threshold (2%)
        self.cloud_provider.average_cpu_stats["instance-1"] = 5

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the server was properly stopped
        self.assertEqual(len(self._terminator._ignored_workers), 1)
        self.assertTrue(self._terminator._ignored_workers.has_key("stack-1"))
        self.assertEqual(self._terminator._ignored_workers["stack-1"], "Server is stopped - no action needed. STACK_ID:stack-1")


    def test_server_has_been_terminated_ignore_rule(self):
        # set up mocks
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "CREATE_COMPLETE"))
        self.cloud_provider.ec2_instance_ids["stack-1"] = "instance-1"
        self.cloud_provider.ec2_instance_statuses["instance-1"] = EC2Status.Terminated
        self.cloud_provider.average_cpu_stats["instance-1"] = None

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the server was properly ignored
        self.assertEqual(len(self._terminator._ignored_workers), 1)
        self.assertTrue(self._terminator._ignored_workers.has_key("stack-1"))
        self.assertEqual(self._terminator._ignored_workers["stack-1"], "Server has been terminated. STACK_ID:stack-1")

    def test_email_sent_successful_only(self):
        # set up mocks for successful actions
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-1", "CREATE_COMPLETE"))
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-2", "CREATE_COMPLETE"))
        self.cloud_provider.ec2_instance_ids["stack-1"] = "instance-1"
        self.cloud_provider.ec2_instance_ids["stack-2"] = "instance-2"
        self.cloud_provider.ec2_instance_statuses["instance-1"] = EC2Status.Running
        self.cloud_provider.ec2_instance_statuses["instance-2"] = EC2Status.Running
        # set the CPU average to just under the current threshold (1%)
        self.cloud_provider.average_cpu_stats["instance-1"] = 0.9
        self.cloud_provider.average_cpu_stats["instance-2"] = 0.9

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the email was set up right
        self.assertEqual(self.email_provider.to_email, self.config.report_generator_email_recipients_developers)
        self.assertEqual(self.email_provider.from_email, self.config.email_settings_from_email)
        self.assertEqual(self.email_provider.subject, "Success running GeoProcessingTerminator.  I'll be back.")

        # verify parts of the email
        self.assertRegexpMatches(self.email_provider.message, "Finished running the terminator script!.*\n")
        self.assertRegexpMatches(self.email_provider.message, "Successful Actions:.*\n")
        self.assertRegexpMatches(self.email_provider.message, "EC2 instance stopped.*\n")

        # verify no failed or error messages
        self.assertNotIn("Failed Actions:", self.email_provider.message)
        self.assertNotIn("Encountered Error during run:", self.email_provider.message)


    def test_email_sent__failed_list(self):
        # set up mocks for failed actions
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-3", "unknown status"))
        self.cloud_provider.cloud_formation_stacks.append(MockStack("stack-4", "unknown status"))

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the email was set up right
        self.assertEqual(self.email_provider.to_email, self.config.report_generator_email_recipients_developers)
        self.assertEqual(self.email_provider.from_email, self.config.email_settings_from_email)
        self.assertEqual(self.email_provider.subject, "Encountered errors running GeoProcessingTerminator.  I'll be back.")

        # verify parts of the email
        self.assertRegexpMatches(self.email_provider.message, "Finished running the terminator script!.*\n")
        self.assertRegexpMatches(self.email_provider.message, "Failed Actions:.*\n")
        self.assertRegexpMatches(self.email_provider.message, "Unrecognized status.*\n")

        # verify no successful or error messages
        self.assertNotIn("Successful Actions:", self.email_provider.message)
        self.assertNotIn("Encountered Error during run:", self.email_provider.message)


    def test_email_sent__error(self):
        # mock up error
        self._terminator._cloud_provider = None

        # run the cloud provider terminate class
        self._terminator.start()

        # verify that the email was set up right
        self.assertEqual(self.email_provider.to_email, self.config.report_generator_email_recipients_developers)
        self.assertEqual(self.email_provider.from_email, self.config.email_settings_from_email)
        self.assertEqual(self.email_provider.subject, "Encountered errors running GeoProcessingTerminator.  I'll be back.")

        # verify parts of the email
        self.assertRegexpMatches(self.email_provider.message, "Finished running the terminator script!.*\n")
        self.assertRegexpMatches(self.email_provider.message, "Encountered Error during run:.*\n")
        self.assertRegexpMatches(self.email_provider.message, "'NoneType' object has no attribute.*\n")

        # verify no successful or failed messages
        self.assertNotIn("Successful Actions:", self.email_provider.message)
        self.assertNotIn("Failed Actions:", self.email_provider.message)

    def test_email_not_sent_if_no_actions(self):
        # run the cloud provider terminate class
        self._terminator.start()

        # make sure there was no email
        self.assertIsNone(self.email_provider.to_email)
        self.assertIsNone(self.email_provider.from_email)
        self.assertIsNone(self.email_provider.subject)
        self.assertIsNone(self.email_provider.message)



if __name__ == '__main__':
    unittest.main()
