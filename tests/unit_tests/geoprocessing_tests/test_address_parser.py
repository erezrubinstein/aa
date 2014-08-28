import unittest
from geoprocessing.business_logic.business_helpers.address_parser import AddressParser

__author__ = 'spacecowboy et al.'


class TestAddressHashMatcher(unittest.TestCase):

    """
       Note: You must access the backup parsed results via result.number, result.name, result.suite_numbers. The backup parser returns '123 Easy St' as the default label of the backup parsed address.
    """

    def test_backup_parser_fail(self):

        unparsed_address = 'Space 135 - Truck Court'
        parser = AddressParser()
        parsed_address_from_backup = parser.backup_parser(unparsed_address)
        self.assertEqual(parsed_address_from_backup.name, unparsed_address)

    def test_backup_parser_pass(self):

        unparsed_address = '135 Truck Court, Suite 145'
        parser = AddressParser()
        parsed_address_from_backup = parser.backup_parser(unparsed_address)
        self.assertEqual(parsed_address_from_backup.number, '135')
        self.assertEqual(parsed_address_from_backup.name, 'Truck Court')
        self.assertEqual(parsed_address_from_backup.suite_numbers[0], '145')


