__author__ = 'imashhor'

import unittest
from infrastructure.cloudformation.template_generator import Template


class TemplateGeneratorTests(unittest.TestCase):
    """
    NOTE: We might not use the security group stuff, so no tests for those for now
    """

    def setUp(self):
        pass

    def doCleanups(self):
        pass

    def test_initialize_template(self):
        template = Template("Test Template")

        expected = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "Test Template",
            "Parameters": {},
            "Resources": {}
        }

        self.assertEqual(expected, template.template)

    def test_add_parameter(self):
        template = Template("Test Template")

        expected = {
            "Type": "String",
            "Default": "Some Value"
        }

        template.add_string_parameter("Some Param", "Some Value")

        self.assertEqual(expected, template.template["Parameters"]["Some Param"])

    def test_add_autoscaling_group(self):
        template = Template("Test Template")

        expected = {
            "Type": "AWS::AutoScaling::AutoScalingGroup",
            "Properties": {
                "AvailabilityZones": ["us-east-1a"],
                "LaunchConfigurationName": {
                    "Ref": "LC1"
                },
                "MinSize": 2,
                "MaxSize": 3
            }
        }

        template.add_autoscaling_group("ASG1", ["us-east-1a"], "LC1", 2, 3)

        self.assertEqual(expected, template.template["Resources"]["ASG1"])

    def test_add_launch_configuration(self):
        template = Template("Test Template")

        expected = {
            "Type": "AWS::AutoScaling::LaunchConfiguration",
            "Properties": {
                "UserData": {
                    "Fn::Base64": {
                        "Fn::Join": [
                            "", ["Some", "Data"]
                        ]
                    }
                },
                "KeyName": "MyKey",
                "ImageId": "ami-1234",
                "SecurityGroups": ["RegusSSH"],
                "InstanceType": "t1.micro",
                "SpotPrice": "1.99",
                "EbsOptimized": "false"
            }
        }

        template.add_launch_configurations("LC1", "MyKey", "ami-1234", ["RegusSSH"], "t1.micro", "1.99",
                                           ["Some", "Data"])

        self.assertEqual(expected, template.template["Resources"]["LC1"])


    def test_add_instance(self):
        template = Template("Test Template")

        expected = {
            "Type": "AWS::EC2::Instance",
            "Properties": {
            "AvailabilityZone": "some-zone-3",
                "UserData": {
                    "Fn::Base64": {
                        "Fn::Join": [
                            "", ["Some", "Data"]
                        ]
                    }
                },
                "KeyName": "MyKey",
                "ImageId": "ami-1234",
                "SecurityGroups": ["TESTSG1"],
                "InstanceType": "t1.micro",
                "EbsOptimized" : "false",
                "Monitoring" : "true"
            }
        }

        template.add_instance("Test1", "MyKey", "ami-1234", ["TESTSG1"], "t1.micro",  "some-zone-3", ["Some", "Data"])

        self.maxDiff = None
        self.assertDictEqual(expected, template.template["Resources"]["Test1"])


    def test_build_user_data(self):
        template = Template("Test Template")
        expected = ["#cloud-config", "\n",
                    "runcmd:", "\n",
                    " - exec command 1", "\n",
                    " - exec command 2", "\n",
                    "output: {all: '| tee -a /var/log/cloud-init-output.log'}", "\n",
                    "custom:", "\n",
                    "    subdomain: \"{0}\"".format("sandbox.nexusri.com"), "\n",
                    "    hostname: \"{0}\"".format("test-machine"), "\n",
                    "    puppet_node_name: \"{0}\"".format("test-node"), "\n",
                     "    ec2_tag_name: \"{0}\"".format("test-name"), "\n"]


        self.assertEqual(expected, template.build_user_data(["exec command 1", "exec command 2"], "sandbox.nexusri.com",
                                                            "test-machine", "test-node", "test-name"))


if __name__ == '__main__':
    unittest.main()
