from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
import mox
import unittest
from core.service.svc_entity_matcher.implementation.matcher.entity_field_preprocessor import EntityFieldPreprocessor


__author__ = 'clairseager'


class EntityFieldPreprocessorTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(EntityFieldPreprocessorTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)


    def doCleanups(self):

        super(EntityFieldPreprocessorTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################

    def test_run(self):
        rec = {
            'id': '123456789abcd',
            'address': {
                'street_address': u'\xac2428 Main   St. ',
                'city': u'Auburn\xac',
                'state': 'NY',
                'zip': '68305-0004'
            },
            'street_number': '2428',
            'street': u'Main   St. \xac',
            'city': 'Unit     Testville ',
            'state': 'NY ',
            'zip': '68305-0004',
            'phone': '(402) 274-3221',
            'country': 'None',
            'longitude': -95.83782239,
            'latitude': 40.3786696807
        }

        preprocessor = EntityFieldPreprocessor()

        newrec = preprocessor.run(rec)

        expected = {
            'id': '123456789abcd',
            'address': '2428 MAIN ST AUBURN NY 68305',
            'street_number': '2428',
            'street': 'MAIN ST',
            'city': 'UNIT TESTVILLE',
            'state': 'NY',
            'zip': '683050004',
            'phone': '4022743221',
            'country': 'None',
            'longitude': -95.83782239,
            'latitude': 40.3786696807
        }

        self.assertDictEqual(expected, newrec)


    ##########################################################################

    def test_address(self):

        address = {
            'street_address': ' 2428 Main   St. ',
            'city': 'auburn',
            'state': 'ny ',
            'zip': '6 8 3 0  5 -0.sdk004'
        }

        preprocessor = EntityFieldPreprocessor()

        newaddress = preprocessor._address(address)

        expected = '2428 MAIN ST AUBURN NY 68305'

        self.assertEqual(newaddress, expected)

    ##########################################################################

    def test_string(self):

        value_in = u' 2428 M\xbcain Street \xac'

        preprocessor = EntityFieldPreprocessor()

        value_out = preprocessor._string(value_in)

        expected = '2428 MAIN STREET'

        self.assertEqual(value_out, expected)

    def test_string_numeric(self):

        value_in = u' 1.2.34 - 5'

        preprocessor = EntityFieldPreprocessor()

        value_out = preprocessor._string_numeric(value_in)

        expected = '12345'

        self.assertEqual(value_out, expected)

    def test_zip4(self):

        value_in = u'12345-1234\xac'

        preprocessor = EntityFieldPreprocessor()

        value_out = preprocessor._zip4(value_in)

        expected = '12345'

        self.assertEqual(value_out, expected)


    def test_string_normalize(self):

        preprocessor = EntityFieldPreprocessor()

        # [input, expected_output]
        normalize_tests = [

            [' 2428 Main   St. ', "2428 MAIN ST"],
            [u' 2428 M\xbcain Street \xac','2428 MAIN ST'],

            ['123 Fake Street S.W.','123 FAKE ST SW'],
            ['123 Fake Street N.W.','123 FAKE ST NW'],
            ['123 Fake Street N.E.','123 FAKE ST NE'],
            ['123 Fake Street S.W.','123 FAKE ST SW'],

            ['123 Fake Street, Suite 777','123 FAKE ST STE 777'],
            ['123 Fake Street S.W., Suite 76A','123 FAKE ST SW STE 76A'],

            ["132nd St S E Mill Creek", "132ND ST SE ML CRK"],
            ["132ND STREET S.E. Mill Creek", "132ND ST SE ML CRK"],

            ["4701 S U S Hwy", "4701 S US HWY"],
            ["4701 SOUTH U.S. HIGHWAY", "4701 S US HWY"],

            ["1100 N.W. LOWES AVENUE", "1100 NW LOWES AVE"],
            ["1100 N W Lowes Ave", "1100 NW LOWES AVE"],

            ["271 Greece Rdg Ctr Dr", "271 GREECE RDG CTR DR"],
            ["271 Greece Ridge Center Drive", "271 GREECE RDG CTR DR"]

            # pile on everybody!
        ]

        for test_pair in normalize_tests:
            result = preprocessor._string_normalize(test_pair[0])
            self.assertEqual(test_pair[1], result)

if __name__ == "__main__":
    unittest.main()