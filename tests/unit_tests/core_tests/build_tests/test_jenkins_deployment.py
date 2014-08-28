import unittest
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency

import xml.etree.ElementTree as ET

__author__ = 'jsternberg'

class CoreJenkinsDeploymentTest(unittest.TestCase):
    def setUp(self):
        register_common_mock_dependencies()
        self.deployment_provider = Dependency("DeploymentProvider").value

    def doCleanups(self):
        dependencies.clear()

    def test_notify_new_relic(self):
        response = self.deployment_provider.notify_new_relic("Mack Daddy App", "The daddy of the mack daddy", "Daddy Mack")

        self.assertEqual(self.deployment_provider.new_relic_application_name, "Mack Daddy App")
        self.assertEqual(self.deployment_provider.new_relic_deployment_description, "The daddy of the mack daddy")
        self.assertEqual(self.deployment_provider.new_relic_api_key, "Daddy Mack")

        # make sure we get an xml string back, with a <deployment> root node that has <id> and <timestamp> elements
        tree = ET.fromstring(response)
        self.assertEqual(tree.tag, "deployment")
        self.assertEqual(tree.find("id").text, "1489838")
        self.assertEqual(tree.find("timestamp").text, "2013-05-05T11:35:24-07:00")

if __name__ == '__main__':
    unittest.main()
