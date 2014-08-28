import os
from common.utilities.inversion_of_control import dependencies, Dependency
from infrastructure.cloudformation.cloudformation_helper import *
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
import unittest
import pprint as pp
import mox

__author__ = 'imashhor'


class CloudFormationHelperTests(mox.MoxTestBase):
    def setUp(self):
        super(CloudFormationHelperTests, self).setUp()

    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()
        self.mox.UnsetStubs()

    def test_create_template(self):
        test_name = "My Test Template"

        test_spot_resources = {
            "test1": {
                "auto_scaling_group": "ASGTest1",
                "launch_configuration": "LCTest1",
                "zones": ["some-zone-1"],
                "hostname": "testhost-1",
                "subdomain": "test.signaldataco.com",
                "puppet_node_name": "test_primary_sg_a1",
                "ec2_tag_name": "TEST-A1",
                "ami": "ami-1233435",
                "security_groups": ["TESTSG1"],
                "security_key_name": "TESTKEY1",
                "spot_price": "1.23",
                "instance_type": "m5.2xlarge",
                "ebs_optimized": True
            },
            "test2": {
                "auto_scaling_group": "ASGTest2",
                "launch_configuration": "LCTest2",
                "zones": ["some-zone-2"],
                "hostname": "testhost-2",
                "subdomain": "test.signaldataco.com",
                "puppet_node_name": "test_secondary_b2",
                "ec2_tag_name": "TEST-B1",
                "ami": "ami-435345",
                "security_groups": ["TESTSG2"],
                "security_key_name": "TESTKEY2",
                "spot_price": "2.34",
                "instance_type": "m1.xlarge",
                "ebs_optimized": False
            },
        }


        test_on_demand_resources = {
            "test3": {
                "zone": "some-zone-3",
                "hostname": "testhost-3",
                "subdomain": "test.signaldataco.com",
                "puppet_node_name": "test_primary_sg_a2",
                "ec2_tag_name": "TEST-A2",
                "ami": "ami-1233435",
                "security_groups": ["TESTSG1"],
                "security_key_name": "TESTKEY1",
                "instance_type": "m5.cxlarge",
                "ebs_optimized": True
            }
        }

        test_boot_commands = [
            "git pull command",
            "bootstrap command"
        ]

        result = create_template(test_name, test_spot_resources, test_on_demand_resources, test_boot_commands)

        expected = {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': 'My Test Template',
            'Parameters': {},
            'Resources': {
                'ASGTest1': {
                    'Properties': {
                        'AvailabilityZones': ['some-zone-1'],
                        'LaunchConfigurationName': {'Ref': 'LCTest1'},
                        'MaxSize': 1,
                        'MinSize': 1
                    },
                    'Type': 'AWS::AutoScaling::AutoScalingGroup'
                },
                'ASGTest2': {
                    'Properties': {
                        'AvailabilityZones': ['some-zone-2'],
                        'LaunchConfigurationName': {'Ref': 'LCTest2'},
                        'MaxSize': 1,
                        'MinSize': 1},
                    'Type': 'AWS::AutoScaling::AutoScalingGroup'},
                'LCTest1': {
                    'Properties': {
                        'ImageId': 'ami-1233435',
                        'InstanceType': 'm5.2xlarge',
                        'KeyName': 'TESTKEY1',
                        'SecurityGroups': ['TESTSG1'],
                        'SpotPrice': '1.23',
                        'UserData': {
                            'Fn::Base64': {
                                'Fn::Join': [
                                    '',
                                    ['#cloud-config',
                                     '\n',
                                     'runcmd:',
                                     '\n',
                                     ' - git pull command',
                                     '\n',
                                     ' - bootstrap command',
                                     '\n',
                                     "output: {all: '| tee -a /var/log/cloud-init-output.log'}",
                                     '\n',
                                     'custom:',
                                     '\n',
                                     '    subdomain: "test.signaldataco.com"',
                                     '\n',
                                     '    hostname: "testhost-1"',
                                     '\n',
                                     '    puppet_node_name: "test_primary_sg_a1"',
                                     '\n',
                                     '    ec2_tag_name: "TEST-A1"',
                                     '\n']]}},
                        "EbsOptimized": "true"
                    },
                    'Type': 'AWS::AutoScaling::LaunchConfiguration'
                },
                'LCTest2': {
                    'Properties': {
                        'ImageId': 'ami-435345',
                        'InstanceType': 'm1.xlarge',
                        'KeyName': 'TESTKEY2',
                        'SecurityGroups': ['TESTSG2'],
                        'SpotPrice': '2.34',
                        'UserData': {
                            'Fn::Base64': {
                                'Fn::Join': [
                                    '',
                                    ['#cloud-config',
                                     '\n',
                                     'runcmd:',
                                     '\n',
                                     ' - git pull command',
                                     '\n',
                                     ' - bootstrap command',
                                     '\n',
                                     "output: {all: '| tee -a /var/log/cloud-init-output.log'}",
                                     '\n',
                                     'custom:',
                                     '\n',
                                     '    subdomain: "test.signaldataco.com"',
                                     '\n',
                                     '    hostname: "testhost-2"',
                                     '\n',
                                     '    puppet_node_name: "test_secondary_b2"',
                                     '\n',
                                     '    ec2_tag_name: "TEST-B1"',
                                     '\n']]}},
                        "EbsOptimized": "false"
                    },
                    'Type': 'AWS::AutoScaling::LaunchConfiguration'
                },
                'test3': {
                    'Properties': {
                        "AvailabilityZone": "some-zone-3",
                        "UserData": {
                            "Fn::Base64": {
                                "Fn::Join": [
                                    "", ['#cloud-config',
                                     '\n',
                                     'runcmd:',
                                     '\n',
                                     ' - git pull command',
                                     '\n',
                                     ' - bootstrap command',
                                     '\n',
                                     "output: {all: '| tee -a /var/log/cloud-init-output.log'}",
                                     '\n',
                                     'custom:',
                                     '\n',
                                     '    subdomain: "test.signaldataco.com"',
                                     '\n',
                                     '    hostname: "testhost-3"',
                                     '\n',
                                     '    puppet_node_name: "test_primary_sg_a2"',
                                     '\n',
                                     '    ec2_tag_name: "TEST-A2"',
                                     '\n']
                                ]
                            }
                        },
                        "KeyName": "TESTKEY1",
                        "ImageId": "ami-1233435",
                        "SecurityGroups": ["TESTSG1"],
                        "InstanceType": "m5.cxlarge",
                        "EbsOptimized" : "true",
                        "Monitoring" : "true"
                    },
                    'Type': 'AWS::EC2::Instance'
                }
            }
        }

        self.maxDiff = None
        self.assertDictEqual(expected, result.template)


    def test_create_template_bad_resource_dict(self):
        test_name = "My Bad Test Template"

        test_resources = {
            "test1": {
                "auto_scaling_groupx": "ASGTest1",
                "launch_configuration": "LCTest1",
                "zones": ["some-zone-1"],
                "hostname": "testhost-1",
                "subdomain": "test.signaldataco.com",
                "puppet_node_name": "test_primary_sg_a1",
                "ec2_tag_name": "TEST-A1",
                "ami": "ami-1233435",
                "security_groups": ["TESTSG1"],
                "security_key_name": "TESTKEY1",
                "spot_price": "1.23",
                "instance_type": "m5.2xlarge"
            }
        }

        test_boot_commands = [
            "git pull command",
            "bootstrap command"
        ]

        self.assertRaises(KeyError, create_template, test_name, test_resources, [], test_boot_commands)
