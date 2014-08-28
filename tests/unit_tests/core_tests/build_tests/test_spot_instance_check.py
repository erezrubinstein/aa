import itertools
from common.utilities.inversion_of_control import dependencies, Dependency
from infrastructure.monitoring.spot_instance_check import SpotInstanceChecker
from geoprocessing.helpers.dependency_helper import register_mock_dependencies

__author__ = 'clairseager'

import unittest

class SpotInstanceCheckTests(unittest.TestCase):
    def setUp(self):
        # set up mocks
        register_mock_dependencies()
        self.cloud_provider = Dependency("CloudProvider").value
        self.file_provider = Dependency("FileProvider").value
        self.email_provider = Dependency("EmailProvider").value

        # logger
        logger = Dependency("SimpleConsole").value

        # set up mongo deployer
        self.spot_checker = SpotInstanceChecker(logger)
        self.spot_checker.request_headers = [('id', 'idy'), ('chicken', 'SuperChicken'), ('danger', 'WhoKilledKenny')]
        self.spot_checker.launch_spec_headers = [('rocket', 'RocketMan')]
        self.spot_checker.status_headers = [('code', "StatusCode")]
        self.spot_checker.headers = list(itertools.chain(*[['*', 'Instance Tag'],
                                                           [h[1] for h in self.spot_checker.request_headers],
                                                           [h[1] for h in self.spot_checker.launch_spec_headers],
                                                           [h[1] for h in self.spot_checker.status_headers]]))


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_check_spot_instances(self):
        # expected perfect match
        retrieved_spot_instances = [PretendSpotInstanceObject("id1"), PretendSpotInstanceObject("id2")]
        self.cloud_provider.current_spot_instances = retrieved_spot_instances

        # expected (from file record)
        self.file_provider.file_lines = {'id1': {'chicken': 'woot', 'id': 'id1', 'danger': 'zone', 'launch_specification':{'rocket':'go'}, 'status':{'code':'bar'}},
                                         'id2': {'chicken': 'woot', 'id': 'id2', 'danger': 'zone', 'launch_specification':{'rocket':'go'}, 'status':{'code':'bar'}}}

        # go
        self.spot_checker.do_comparison()

        self.assertEqual(self.spot_checker.current, self.spot_checker.recorded)
        self.assertFalse(hasattr(self.spot_checker.current["id1"]["status"], "update_time"))
        self.assertFalse(hasattr(self.spot_checker.current["id2"]["status"], "update_time"))
        self.assertFalse(hasattr(self.spot_checker, 'diff'))

        # File provider assertions
        self.assertIn(self.spot_checker.current_file_path, self.file_provider.files.keys())
        self.assertEqual([self.spot_checker.current_file_path], self.file_provider.deleted_files)

        # Email provider assertions - EVERYTHING should be None
        for attr in self.email_provider.__dict__.keys():
            self.assertIsNone(self.email_provider.__getattribute__(attr))


    def test_check_spot_one_missing(self):
        expected_diff = {'*': '-', 'RocketMan': 'fuel', 'SuperChicken': 'parrot', 'WhoKilledKenny': 'manger', 'idy': 'id2', 'StatusCode': 'bar'}
        retrieved_spot_instances = [PretendSpotInstanceObject("id1")]
        self.cloud_provider.current_spot_instances = retrieved_spot_instances

        # expected (from file record)
        self.file_provider.file_lines = {'id1': {'chicken': 'woot', 'id': 'id1', 'danger': 'zone', 'launch_specification':{'rocket':'go'}, 'status':{'code':'bar'}},
                                         'id2': {'chicken': 'parrot', 'id': 'id2', 'danger': 'manger', 'launch_specification':{'rocket':'fuel'}, 'status':{'code':'bar'}}}

        # go
        self.spot_checker.do_comparison()

        self.assertEqual(self.spot_checker.current["id1"], self.spot_checker.recorded["id1"])
        self.assertFalse(hasattr(self.spot_checker.current, "id2"))
        self.assertEqual(self.spot_checker.changes, {'removed': ['id2'], 'modified': [], 'added': []})
        self.assertDictEqual(self.spot_checker.diff[0], expected_diff)

        # File provider assertions
        self.assertEqual([self.spot_checker.recorded_file_path], self.file_provider.deleted_files)
        self.assertEqual([(self.spot_checker.current_file_path, self.spot_checker.recorded_file_path)], self.file_provider.moved_files)

        # Email provider assertions
        self.assertEqual(self.email_provider.html_from_email, 'arnie@nexusri.com')
        self.assertEqual(self.email_provider.html_subject, 'Spot Instance Monitor')
        email_terms = ['SuperChicken', 'WhoKilledKenny', 'RocketMan', 'parrot', 'manger', 'fuel']
        for value in email_terms:
            self.assertIn(value, self.email_provider.html_message)



    def test_check_spot_one_extra(self):
        expected_diff = {'*': '+', 'RocketMan': 'go', 'SuperChicken': 'woot', 'WhoKilledKenny': 'zone', 'idy': 'id2', 'StatusCode': 'bar'}
        retrieved_spot_instances = [PretendSpotInstanceObject("id1"), PretendSpotInstanceObject("id2")]
        self.cloud_provider.current_spot_instances = retrieved_spot_instances

        # expected (from file record)
        self.file_provider.file_lines = {'id1': {'chicken': 'woot', 'id': 'id1', 'danger': 'zone', 'launch_specification':{'rocket':'go'}, 'status':{'code':'bar'}}}

        # go
        self.spot_checker.do_comparison()

        self.assertEqual(self.spot_checker.current["id1"], self.spot_checker.recorded["id1"])
        self.assertFalse(hasattr(self.spot_checker.recorded, "id2"))
        self.assertEqual(self.spot_checker.changes, {'removed': [], 'modified': [], 'added': ['id2']})
        self.assertDictEqual(self.spot_checker.diff[0], expected_diff)

        # File provider assertions
        self.assertEqual([self.spot_checker.recorded_file_path], self.file_provider.deleted_files)
        self.assertEqual([(self.spot_checker.current_file_path, self.spot_checker.recorded_file_path)], self.file_provider.moved_files)

        # Email provider assertions
        self.assertEqual(self.email_provider.html_from_email, 'arnie@nexusri.com')
        self.assertEqual(self.email_provider.html_subject, 'Spot Instance Monitor')
        email_terms = ['SuperChicken', 'WhoKilledKenny', 'RocketMan', 'woot', 'zone', 'go', 'bar']
        for value in email_terms:
            self.assertIn(value, self.email_provider.html_message)


    def test_check_spot_values_different(self):
        expected_diff = [{'*': '*', 'RocketMan': 'go', 'SuperChicken': 'woot', 'WhoKilledKenny': 'zone', 'idy': 'id2', 'StatusCode': 'bar'},
                         {'*': '--', 'SuperChicken': 'parrot', 'WhoKilledKenny': 'manger', 'RocketMan': 'fuel'},
                         {'*': '*', 'RocketMan': 'go', 'SuperChicken': 'woot', 'WhoKilledKenny': 'zone', 'idy': 'id1', 'StatusCode': 'bar'},
                         {'*': '--', 'WhoKilledKenny': 'orange', 'StatusCode': 'Barbarella'}]

        retrieved_spot_instances = [PretendSpotInstanceObject("id1"), PretendSpotInstanceObject("id2")]
        self.cloud_provider.current_spot_instances = retrieved_spot_instances

        # expected (from file record)
        self.file_provider.file_lines = {'id1': {'chicken': 'woot', 'id': 'id1', 'danger': 'orange', 'launch_specification':{'rocket':'go'}, 'status':{'code':'Barbarella'}},
                                         'id2': {'chicken': 'parrot', 'id': 'id2', 'danger': 'manger', 'launch_specification':{'rocket':'fuel'}, 'status':{'code':'bar'}}}

        # go
        self.spot_checker.do_comparison()

        self.assertEqual(self.spot_checker.changes['removed'], [])
        self.assertItemsEqual(self.spot_checker.changes['modified'], ['id1','id2'])
        self.assertEqual(self.spot_checker.changes['added'], [])
        for i, v in enumerate(expected_diff):
            self.assertDictEqual(self.spot_checker.diff[i], v)

        # File provider assertions
        self.assertEqual([self.spot_checker.recorded_file_path], self.file_provider.deleted_files)
        self.assertEqual([(self.spot_checker.current_file_path, self.spot_checker.recorded_file_path)], self.file_provider.moved_files)

        # Email provider assertions
        self.assertEqual(self.email_provider.html_from_email, 'arnie@nexusri.com')
        self.assertEqual(self.email_provider.html_subject, 'Spot Instance Monitor')
        email_terms = ['SuperChicken', 'WhoKilledKenny', 'RocketMan', 'parrot', 'fuel', 'orange', 'manger', 'zone']
        for value in email_terms:
            self.assertIn(value, self.email_provider.html_message)


    def test_check_spot_status_code_ignored(self):
        retrieved_spot_instances = [PretendSpotInstanceObject("id1")]
        retrieved_spot_instances[0].status.code = "instance-terminated-by-user"
        self.cloud_provider.current_spot_instances = retrieved_spot_instances

        # expected (from file record)
        self.file_provider.file_lines = {'id1': {'chicken': 'woot', 'id': 'id1', 'danger': 'orange', 'launch_specification':{'rocket':'go'}, 'status':{'code':'Barbarella'}}}

        # go
        self.spot_checker.do_comparison()

        self.assertEqual(self.spot_checker.changes, {"removed":[], "modified":[], "added":[]})
        self.assertFalse(hasattr(self.spot_checker, "diff"))

        # File provider assertions
        self.assertEqual([self.spot_checker.recorded_file_path], self.file_provider.deleted_files)
        self.assertEqual([(self.spot_checker.current_file_path, self.spot_checker.recorded_file_path)], self.file_provider.moved_files)

        # Email provider assertions - EVERYTHING should be None
        for attr in self.email_provider.__dict__.keys():
            self.assertIsNone(self.email_provider.__getattribute__(attr))


#  helper classes
class PretendSpotInstanceObject(object):
    def __init__(self, id):
        self.id = id
        self.chicken = "woot"
        self.danger = "zone"
        self.status = Foo()
        self.status.update_time = "I should not be included"
        self.status.code = "bar"
        self.launch_specification = Foo()
        self.launch_specification.rocket = "go"

class Foo(object):
    pass


if __name__ == '__main__':
    unittest.main()
