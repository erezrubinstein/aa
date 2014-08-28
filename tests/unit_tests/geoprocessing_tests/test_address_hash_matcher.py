import unittest
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_helpers.address_hash_matcher import HashMatcher
from geoprocessing.business_logic.enums import HashMatcherFuzziness

__author__ = 'spacecowboy et al.'

class TestAddressHashMatcher(unittest.TestCase):

    def test_full_address_full_long_lat_positive(self):
        """
        full address + full long/lat (i.e. very precise)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot    Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12 3451234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.001001'
        address_2.longitude = '1.001001'

        address_1.latitude = '1.001001'
        address_2.latitude = '1.001001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])

    def test_normalized_street_full_long_lat_blank_zip_positive_contained_within_street_blank_zip(self):
        """
        street_number + street_normalized + city + state + full long/lat (allows variations in zip)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '156'
        address_2.street_number = '156'

        address_1.street = 'Wilford Ash Pkwy'
        address_2.street = 'Wilford Ash Parkway'

        address_1.city = 'Cleveland'
        address_2.city = 'Cleveland'

        address_1.state = 'GA'
        address_2.state = 'GA'

        address_1.zip_code = '30528'
        address_2.zip_code = ''

        address_1.longitude = '-83.767283'
        address_2.longitude = '-83.767283'

        address_1.latitude = '34.598235'
        address_2.latitude = '34.598235'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized + city + state + full long/lat (allows variations in zip)', hash_matcher._match([address_2])[1])

    def test_full_address_full_long_lat_positive_diff_digit_length_zip(self):
        """
        full address + full long/lat (i.e. very precise)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot    Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12 3451234'
        address_2.zip_code = '12345'

        address_1.longitude = '1.001001'
        address_2.longitude = '1.001001'

        address_1.latitude = '1.001001'
        address_2.latitude = '1.001001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])

    def test_normalized_full_address_full_long_lat_positive(self):
        """
        normalized full address + full long/lat (i.e. very precise)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.001001'
        address_2.longitude = '1.001001'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('normalized full address + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])

        # test the other kind of normalizing
        address_1.street = 'Woot Dr E.'
        address_2.street = 'Woot Dr E'
        hash_matcher = HashMatcher(address_1)

        self.assertEqual('normalized full address + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])

    def test_normalized_full_address_full_long_lat_positive_contained_street(self):
        """
        normalized full address + full long/lat (i.e. very precise)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Loop SW'
        address_2.street = 'Woot Loop South West'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.001001'
        address_2.longitude = '1.001001'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('normalized full address + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])

        # test the other kind of normalizing
        address_1.street = 'Woot Dr E.'
        address_2.street = 'Woot Dr E'
        hash_matcher = HashMatcher(address_1)

        self.assertEqual('normalized full address + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])

    def test_street_city_state_zip_full_long_lat_positive(self):
        """
        street + city + state + zip + full long/lat (i.e. very precise)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234z'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00100'
        address_2.longitude = '1.00100'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street + city + state + zip + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])

    def test_street_number_street_state_zip_full_long_lat_positive(self):
        """
        street_number + street + state + zip + full long/lat (allows variations in city names)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00100'
        address_2.longitude = '1.00100'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street + state + zip + full long/lat (allows variations in city names)', hash_matcher._match([address_2])[1])

    def test_street_number_normalized_street_state_zip_full_long_lat_positive(self):
        """
        street_number + normalized_street + state + zip + full long/lat (allows variations in city names)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00100'
        address_2.longitude = '1.00100'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + normalized_street + state + zip + full long/lat (allows variations in city names)', hash_matcher._match([address_2])[1])

        address_1.street = 'Woot Dr E.'
        address_2.street = 'Woot Dr E'
        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + normalized_street + state + zip + full long/lat (allows variations in city names)', hash_matcher._match([address_2])[1])

    def test_street_number_city_state_zip_full_long_lat_positive(self):
        """
        street_number + city + state + zip + full long/lat (allows variations in street names)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Wot Drz'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00100'
        address_2.longitude = '1.00100'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + city + state + zip + full long/lat (allows variations in street names)', hash_matcher._match([address_2])[1])

    def test_street_number_street_city_state_full_long_lat_positive(self):
        """
        street_number + street + city + state + full long/lat (allows variations in zip)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '11345-1234'

        address_1.longitude = '1.00100'
        address_2.longitude = '1.00100'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address without zip + full long/lat (allows variations in zip)', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_city_state_full_long_lat_positive(self):
        """
        street_number + street_normalized + city + state + full long/lat (allows variations in zip)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '11345-1234'

        address_1.longitude = '1.00100'
        address_2.longitude = '1.00100'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized + city + state + full long/lat (allows variations in zip)', hash_matcher._match([address_2])[1])

        address_1.street = 'Woot Dr E.'
        address_2.street = 'Woot Dr E'
        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized + city + state + full long/lat (allows variations in zip)', hash_matcher._match([address_2])[1])

    def test_street_number_street_state_full_long_lat_positive(self):
        """
        street_number + street + state + full long/lat (allows variations in city and zip)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '11345-1234'

        address_1.longitude = '1.00100'
        address_2.longitude = '1.00100'

        address_1.latitude = '1.00100'
        address_2.latitude = '1.00100'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street + state + full long/lat (allows variations in city and zip)', hash_matcher._match([address_2])[1])

    def test_full_address_4_digit_long_lat_positive(self):
        """
        full address + 4 digit long/lat (i.e. precise to 11.1m at the equator)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00006'
        address_2.longitude = '1.00007'

        address_1.latitude = '1.00002'
        address_2.latitude = '1.00001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address + 4 digit long/lat (i.e. precise to 11.1m at the equator)', hash_matcher._match([address_2])[1])

    def test_full_normalized_address_4_digit_long_lat_positive(self):
        """
        full normalized address + 4 digit long/lat (i.e. precise to 11.1m at the equator)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00006'
        address_2.longitude = '1.00007'

        address_1.latitude = '1.00002'
        address_2.latitude = '1.00001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full normalized address + 4 digit long/lat (i.e. precise to 11.1m at the equator)', hash_matcher._match([address_2])[1])

    def test_street_number_street_state_zip_4_digit_long_lat_positive(self):
        """
        street_number + street + state + zip + 4-digit long/lat (allows variations in city names)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00006'
        address_2.longitude = '1.00007'

        address_1.latitude = '1.00002'
        address_2.latitude = '1.00001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street + state + zip + 4-digit long/lat (allows variations in city names)', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_state_zip_4_digit_long_lat_positive(self):
        """
        street_number + street_normalized + state + zip + 4-digit long/lat (allows variations in city names)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr E.'
        address_2.street = 'Woot Dr East'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00006'
        address_2.longitude = '1.00007'

        address_1.latitude = '1.00002'
        address_2.latitude = '1.00001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized + state + zip + 4-digit long/lat (allows variations in city names)', hash_matcher._match([address_2])[1])

    def test_street_number_city_state_zip_4_digit_long_lat_positive(self):
        """
        street_number + city + state + zip + 4-digit long/lat (allows variations in street names)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Wot Drz'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.00006'
        address_2.longitude = '1.00007'

        address_1.latitude = '1.00002'
        address_2.latitude = '1.00001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + city + state + zip + 4-digit long/lat (allows variations in street names)', hash_matcher._match([address_2])[1])

    def test_full_address_3_digit_long_lat_positive(self):
        """
        full address + 3 digit long/lat (i.e. accurate to 111m at the equator
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.0006'
        address_2.longitude = '1.0007'

        address_1.latitude = '1.0002'
        address_2.latitude = '1.0001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address + 3 digit long/lat (i.e. accurate to 111m at the equator', hash_matcher._match([address_2])[1])

    def test_normalized_address_3_digit_long_lat_positive(self):
        """
        normalized address + 3 digit long/lat (i.e. accurate to 111m at the equator
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.0006'
        address_2.longitude = '1.0007'

        address_1.latitude = '1.0002'
        address_2.latitude = '1.0001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('normalized address + 3 digit long/lat (i.e. accurate to 111m at the equator', hash_matcher._match([address_2])[1])

    def test_full_address_2_digit_long_lat_positive(self):
        """
        full address + 2 digit long/lat (i.e. accurate to 1.11km at the equator
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.006'
        address_2.longitude = '1.007'

        address_1.latitude = '1.002'
        address_2.latitude = '1.001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address + 2 digit long/lat (i.e. accurate to 1.11km at the equator', hash_matcher._match([address_2])[1])

    def test_full_address_1_digit_long_lat_positive(self):
        """
        full address + 1 digit long/lat (i.e. accurate to 11.1km at the equator
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.06'
        address_2.longitude = '1.07'

        address_1.latitude = '1.02'
        address_2.latitude = '1.01'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address + 1 digit long/lat (i.e. accurate to 11.1km at the equator', hash_matcher._match([address_2])[1])

    def test_full_normalized_address_1_digit_long_lat_positive(self):
        """
        full normalized address + 1 digit long/lat (i.e. accurate to 11.1km at the equator
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.06'
        address_2.longitude = '1.07'

        address_1.latitude = '1.02'
        address_2.latitude = '1.01'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full normalized address + 1 digit long/lat (i.e. accurate to 11.1km at the equator', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_first_word_city_state_zip_3_digit_long_lat_positive(self):
        """
        street_number + street_normalized_first_word + city + state + zip + 3-digit long/lat (allows some variation in street names )
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Drz East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.0006'
        address_2.longitude = '1.0007'

        address_1.latitude = '1.0002'
        address_2.latitude = '1.0001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized_first_word + city + state + zip + 3-digit long/lat (allows some variation in street names )', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_city_state_blank_zip_full_long_lat_positive_specific(self):
        """
        street_number + street_normalized + city + state + full long/lat (allows variations in zip)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '3050'
        address_2.street_number = '3050'

        address_1.street = 'Simpson, Hwy 13'
        address_2.street = 'Simpson Highway 13'

        address_1.city = 'Mendenhall'
        address_2.city = 'Mendenhall'

        address_1.state = 'MS'
        address_2.state = 'MS'

        address_1.zip_code = '39114'
        address_2.zip_code = ''

        address_1.longitude = '-89.877649'
        address_2.longitude = '-89.877649'

        address_1.latitude = '31.974292'
        address_2.latitude = '31.974292'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized + city + state + full long/lat (allows variations in zip)', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_city_state_blank_zip_3_digit_long_lat_positive(self):
        """
        street_number + street_normalized street + city + state + [blank zip on either side] + 3-digit long/lat
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = ''
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.1238'
        address_2.longitude = '1.1239'

        address_1.latitude = '1.1232'
        address_2.latitude = '1.1231'

        address_1.phone_number = '(516)776-0972'
        address_2.phone_number = '(516)776-0972'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized + city + state + [blank zip on either side] + 3-digit long/lat', hash_matcher._match([address_2])[1])


    def test_street_number_street_normalized_state_zip_3_digit_long_lat_positive(self):
        """
        street_number + street_normalized_first_word + state + zip + 3-digit long/lat (allows some variation in street names and city)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Drz East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.0006'
        address_2.longitude = '1.0007'

        address_1.latitude = '1.0002'
        address_2.latitude = '1.0001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized_first_word + state + zip + 3-digit long/lat (allows some variation in street names and city)', hash_matcher._match([address_2])[1])

    def test_zip_full_long_lat_positive(self):
        """
        zip + full long/lat (allows variations in addresses except zip)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234z'
        address_2.street_number = '1234'

        address_1.street = 'Woot Drz'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WTz'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.1234567'
        address_2.longitude = '1.1234567'

        address_1.latitude = '1.1234567'
        address_2.latitude = '1.1234567'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('zip + full long/lat (allows variations in addresses except zip)', hash_matcher._match([address_2])[1])

    def test_zip_4_digit_long_lat_positive(self):
        """
        zip + 4-digit long/lat (allows variations in addresses except zip)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234z'
        address_2.street_number = '1234'

        address_1.street = 'Woot Drz'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WTz'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.1234667'
        address_2.longitude = '1.1234567'

        address_1.latitude = '1.1234467'
        address_2.latitude = '1.1234367'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('zip + 4-digit long/lat (allows variations in addresses except zip)', hash_matcher._match([address_2])[1])

    def test_stripped_phone_full_long_lat_positive(self):
        """
        stripped phone + full long/lat
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234z'
        address_2.street_number = '1234'

        address_1.street = 'Woot Drz'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WTz'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '11345-1234'

        address_1.longitude = '1.1234567'
        address_2.longitude = '1.1234567'

        address_1.latitude = '1.1234567'
        address_2.latitude = '1.1234567'

        address_1.phone_number = '(516)776-0972'
        address_2.phone_number = '5167760972'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('stripped phone + full long/lat', hash_matcher._match([address_2])[1])

    def test_stripped_phone_full_long_lat_positive(self):
        """
        stripped phone + full long/lat
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot Cityz'
        address_2.city = 'Woot City'

        address_1.state = 'WTz'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '11345-1234'

        address_1.longitude = '1.12345'
        address_2.longitude = '1.12349'

        address_1.latitude = '1.12346'
        address_2.latitude = '1.12345'

        address_1.phone_number = '(516)776-0972'
        address_2.phone_number = '(516)776-0972'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('phone + street_number + street + 4-digit long/lat', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_city_state_blank_zip_4_digit_long_lat_positive(self):
        """
        street_number + street_normalized + city + state + [blank zip on either side] + 4-digit long/lat
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = ''
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.12345'
        address_2.longitude = '1.12349'

        address_1.latitude = '1.12346'
        address_2.latitude = '1.12345'

        address_1.phone_number = '(516)776-0972'
        address_2.phone_number = '(516)776-0972'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized + city + state + [blank zip on either side] + 4-digit long/lat', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_city_state_blank_zip_3_digit_long_lat_positive(self):
        """
        street_number + street_normalized + city + state + [blank zip on either side] + 3-digit long/lat
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = ''
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.1238'
        address_2.longitude = '1.1239'

        address_1.latitude = '1.1232'
        address_2.latitude = '1.1231'

        address_1.phone_number = '(516)776-0972'
        address_2.phone_number = '(516)776-0972'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized + city + state + [blank zip on either side] + 3-digit long/lat', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_city_state_3_digit_long_lat_positive(self):
        """
        street_number + street_normalized_first_word + city + state + 3-digit long/lat (allows some variation in street names and zip)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Drz East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12345-1234'
        address_2.zip_code = '11345-1234'

        address_1.longitude = '1.0006'
        address_2.longitude = '1.0007'

        address_1.latitude = '1.0002'
        address_2.latitude = '1.0001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized_first_word + city + state + 3-digit long/lat (allows some variation in street names and zip)', hash_matcher._match([address_2])[1])

        address_1.zip_code = ''
        address_2.zip_code = None

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized_first_word + city + state + 3-digit long/lat (allows some variation in street names and zip)', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_city_state_blank_zip_2_digit_long_lat_positive(self):
        """
        street_number + street_normalized street + city + state + [blank zip on either side] + 2-digit long/lat
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = ''
        address_2.zip_code = '11345-1234'

        address_1.longitude = '1.006'
        address_2.longitude = '1.007'

        address_1.latitude = '1.002'
        address_2.latitude = '1.001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized street + city + state + [blank zip on either side] + 2-digit long/lat', hash_matcher._match([address_2])[1])

    def test_street_number_street_normalized_city_state_blank_zip_1_digit_long_lat_positive(self):
        """
        street_number + street_normalized street + city + state + [blank zip on either side] + 1-digit long/lat
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Woot Dr E.'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = ''
        address_2.zip_code = '11345-1234'

        address_1.longitude = '1.06'
        address_2.longitude = '1.07'

        address_1.latitude = '1.09'
        address_2.latitude = '1.06'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('street_number + street_normalized street + city + state + [blank zip on either side] + 1-digit long/lat', hash_matcher._match([address_2])[1])

    def test_negative_match(self):

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1235'

        address_1.street = 'Woot Dr East'
        address_2.street = 'Circle Road'

        address_1.city = 'Woot City'
        address_2.city = 'Muttontown'

        address_1.state = 'WT'
        address_2.state = 'NY'

        address_1.zip_code = '12345-67891'
        address_2.zip_code = '11791'

        address_1.longitude = '1.06'
        address_2.longitude = '42'

        address_1.latitude = '1.09'
        address_2.latitude = '-73.50'

        hash_matcher = HashMatcher(address_1)
        self.assertIsNone(hash_matcher._match([address_2]))

    def test_full_address_mixed_long_lat_positive(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot    Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12 3451234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '1.191234'
        address_2.longitude = '1.174321'

        address_1.latitude = '1.001001'
        address_2.latitude = '1.001001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address + 1 digit long/lat (i.e. accurate to 11.1km at the equator', hash_matcher._match([address_2])[1])


    def test_full_address(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot    Dr'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12 3451234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '2.191234'
        address_2.longitude = '1.174321'

        address_1.latitude = '1.001001'
        address_2.latitude = '1.001001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('full address (i.e. very precise)', hash_matcher._match([address_2])[1])

    def test_full_address_normalized(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot    Dr Chicken'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12 3451234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '-2.191234'
        address_2.longitude = '1.174321'

        address_1.latitude = '1.001001'
        address_2.latitude = '1.001001'

        hash_matcher = HashMatcher(address_1)
        self.assertEqual('normalized full address (i.e. very precise)', hash_matcher._match([address_2])[1])

    def test_full_address_normalized(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '1234'
        address_2.street_number = '1234'

        address_1.street = 'Woot    Dr Chicken'
        address_2.street = 'Woot Dr'

        address_1.city = 'Woot City'
        address_2.city = 'Woot City'

        address_1.state = 'WT'
        address_2.state = 'WT'

        address_1.zip_code = '12 3451234'
        address_2.zip_code = '12345-1234'

        address_1.longitude = '-1'
        address_2.longitude = '1.174321'

        address_1.latitude = '-1'
        address_2.latitude = '1.001001'

        hash_matcher = HashMatcher(address_1)
        self.assertIsNone(hash_matcher._match([address_2]))

    def test_full_address_normalized_city_normalized_street(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '15575'
        address_2.street_number = '15575'

        address_1.street = 'Starfish Street'
        address_2.street = 'Starfish St'

        address_1.city = 'Panama City Heights'
        address_2.city = 'Panama City Hghts'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '32413'
        address_2.zip_code = '32413'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'

        hash_matcher = HashMatcher(address_1)
        self.assertIsNotNone(hash_matcher._match([address_2]))


    def test_full_address_normalized_city_normalized_street_enclosed(self):

        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '15575'
        address_2.street_number = '15575'

        address_1.street = 'Starfish Street'
        address_2.street = 'Starfish St'

        address_1.city = 'Panama City Heights'
        address_2.city = 'Panama City Hghts'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '32413'
        address_2.zip_code = '32413'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'
        
        address_1.suite_numbers = ['Suite 3']
        address_2.suite_numbers = ['Ste 3']

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))

    def test_full_address_normalized_city_normalized_street_suite_check_empty_two(self):

        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '5001'
        address_2.street_number = '5001'

        address_1.street = 'South France Avenue'
        address_2.street = 'S France Avenue'

        address_1.city = 'Minneapolis'
        address_2.city = 'Minneapolis'

        address_1.state = 'MN'
        address_2.state = 'MN'

        address_1.zip_code = '55410'
        address_2.zip_code = '55424'

        address_1.longitude = '44.912477'
        address_2.longitude = '44.916291'

        address_1.latitude = '-93.329038'
        address_2.latitude = '-93.329048'

        hash_matcher = HashMatcher(address_1)
        self.assertIsNotNone(hash_matcher._match([address_2]))

    def test_full_address_normalized_city_normalized_street_suite_check_empty_four(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '15575'
        address_2.street_number = '15575'

        address_1.street = 'Starfish Street'
        address_2.street = 'Starfish St'

        address_1.city = 'Panama City Heights'
        address_2.city = 'Panama City Hghts'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '32413'
        address_2.zip_code = '32413'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'

        address_1.suite_numbers = ['Suite 3']
        address_2.suite_numbers = ['#3']

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))

    def test_full_address_normalized_city_normalized_street_suite_check_empty_four(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '15575'
        address_2.street_number = '15575'

        address_1.street = 'Starfish Street'
        address_2.street = 'Starfish St'

        address_1.city = 'Panama City Heights'
        address_2.city = 'Panama City Hghts'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '32413'
        address_2.zip_code = '32413'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'

        address_1.suite_numbers = ['Suite#3']
        address_2.suite_numbers = ['#3']

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))

    def test_full_address_normalized_city_normalized_street_suite_check_empty_four(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '15575'
        address_2.street_number = '15575'

        address_1.street = 'Starfish Street'
        address_2.street = 'Starfish St'

        address_1.city = 'Panama City Heights'
        address_2.city = 'Panama City Hghts'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '32413'
        address_2.zip_code = '32413'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'

        address_1.suite_numbers = ['Suite#3', '4']
        address_2.suite_numbers = ['3', 'suite #4']

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))

    def test_full_address_normalized_city_normalized_street_suite_check_empty_four(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '15575'
        address_2.street_number = '15575'

        address_1.street = 'Starfish Street'
        address_2.street = 'Starfish St'

        address_1.city = 'Panama City Heights'
        address_2.city = 'Panama City Hghts'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '32413'
        address_2.zip_code = '32413'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'


        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))

    def test_full_address_normalized_city_normalized_street_suite_test_case_1(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '15575'
        address_2.street_number = '15575'

        address_1.street = 'Starfish St'
        address_2.street = 'Starfish St'

        address_1.city = 'Ross'
        address_2.city = 'Pittsburg'

        address_1.state = 'PA'
        address_2.state = 'PA'

        address_1.zip_code = '32413'
        address_2.zip_code = '32413'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNone(hash_matcher._match([address_2]))


    def test_full_address_normalized_city_normalized_street_suite_test_case_2(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '3101'
        address_2.street_number = '3101'

        address_1.street = 'Pga Boulevard'
        address_2.street = 'Pga Blvd'

        address_1.city = 'Palm Beach Gardens'
        address_2.city = 'Palm Gardens'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '33410'
        address_2.zip_code = '33410'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'


        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))

    def test_full_address_normalized_city_normalized_street_suite_test_case_2(self):
        """
        full address + mixed long/lat (i.e. lat has full, long has fewer digits)
        """

        address_1 = Address()
        address_2 = Address()

        address_1.street_number = '3101'
        address_2.street_number = '3101'

        address_1.street = 'Saint Louis Street'
        address_2.street = 'Saint Louis St'

        address_1.city = 'Saint Louis'
        address_2.city = 'St. Louis'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '33410'
        address_2.zip_code = '33410'

        address_1.longitude = '-235'
        address_2.longitude = '-80.006498'

        address_1.latitude = '115'
        address_2.latitude = '40.541267'


        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))

    def test_not_fuzzy__exact_match__normalized(self):
        """
        make sure that an exact match(normalizedstreet, normalizzed street number, normalized city, state, zip, none negative geos, matches)
        """
        address_1 = Address()
        address_2 = Address()

        address_1.street_number = 'One'
        address_2.street_number = '1'

        address_1.street = 'Saint Louis Street'
        address_2.street = 'Saint Louis St'

        address_1.city = 'Saint Louis'
        address_2.city = 'St. Louis'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '33410'
        address_2.zip_code = '33410'

        address_1.longitude = '-235'
        address_2.longitude = '-235'

        address_1.latitude = '115'
        address_2.latitude = '115'


        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertEqual('normalized full postal, no long/lat match, long/lats must not be -1', hash_matcher._match([address_2])[1])


    def test_not_fuzzy__geos_dont_match__normalized(self):
        """
        make sure that an exact match minus geos (normalizedstreet, normalizzed street number, normalized city, state, zip, none negative geos) matches.
        Geos do not need to match (they are taken care of in the candidate query before)
        """
        address_1 = Address()
        address_2 = Address()

        address_1.street_number = 'One'
        address_2.street_number = '1'

        address_1.street = 'Saint Louis Street'
        address_2.street = 'Saint Louis St'

        address_1.city = 'Saint Louis'
        address_2.city = 'St. Louis'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '33410'
        address_2.zip_code = '33410'

        address_1.longitude = '-235'
        address_2.longitude = '-44'

        address_1.latitude = '115'
        address_2.latitude = '124'


        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertEqual('normalized full postal, no long/lat match, long/lats must not be -1', hash_matcher._match([address_2])[1])


    def test_not_fuzzy__zips_dont_match__normalized(self):
        """
        make sure that an exact match minus zip (normalizedstreet, normalizzed street number, normalized city, state, geos, none negative geos) matches
        """
        address_1 = Address()
        address_2 = Address()

        address_1.street_number = 'One'
        address_2.street_number = '1'

        address_1.street = 'Saint Louis Street'
        address_2.street = 'Saint Louis St'

        address_1.city = 'Saint Louis'
        address_2.city = 'St. Louis'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '33410'
        address_2.zip_code = '324234'

        address_1.longitude = '-235'
        address_2.longitude = '-235'

        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertEqual('normalized postal without zip + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])


    def test_not_fuzzy__cities_dont_match__normalized(self):
        """
        make sure that an exact match minus cities (normalizedstreet, normalizzed street number, zip, state, geos, none negative geos) matches
        """
        address_1 = Address()
        address_2 = Address()

        address_1.street_number = 'One'
        address_2.street_number = '1'

        address_1.street = 'Saint Louis Street'
        address_2.street = 'Saint Louis St'

        address_1.city = 'asdgasdg Louis'
        address_2.city = 'gfyy5635trefg'

        address_1.state = 'FL'
        address_2.state = 'FL'

        address_1.zip_code = '33410'
        address_2.zip_code = '33410'

        address_1.longitude = '-235'
        address_2.longitude = '-235'

        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertEqual('normalized postal without city + full long/lat (i.e. very precise)', hash_matcher._match([address_2])[1])


    def test__normalization__parkway_pkwy(self):
        """
        make sure that an exact match, with a normalization of parkway matches
        """
        address_1 = Address()
        address_2 = Address()
        address_1.street_number = '1'
        address_2.street_number = '1'
        address_1.street = 'Saint Louis PKWY'
        address_2.street = 'Saint Louis Parkway'
        address_1.city = 'Saint Louis'
        address_2.city = 'Saint Louis'
        address_1.state = 'FL'
        address_2.state = 'FL'
        address_1.zip_code = '33410'
        address_2.zip_code = '33410'
        address_1.longitude = '-235'
        address_2.longitude = '-235'
        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))


    def test__normalization__parkway_pky(self):
        """
        make sure that an exact match, with a normalization works
        """
        address_1 = Address()
        address_2 = Address()
        address_1.street_number = '1'
        address_2.street_number = '1'
        address_1.street = 'Saint Louis PKY'
        address_2.street = 'Saint Louis Parkway'
        address_1.city = 'Saint Louis'
        address_2.city = 'Saint Louis'
        address_1.state = 'FL'
        address_2.state = 'FL'
        address_1.zip_code = '33410'
        address_2.zip_code = '33410'
        address_1.longitude = '-235'
        address_2.longitude = '-235'
        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))


    def test__normalization__township_twnshp(self):
        """
        make sure that an exact match, with a normalization works
        """
        address_1 = Address()
        address_2 = Address()
        address_1.street_number = '1'
        address_2.street_number = '1'
        address_1.street = 'Saint Louis Parkway'
        address_2.street = 'Saint Louis Parkway'
        address_1.city = 'Saint Louis TWNSHP'
        address_2.city = 'Saint Louis township'
        address_1.state = 'FL'
        address_2.state = 'FL'
        address_1.zip_code = '33410'
        address_2.zip_code = '33410'
        address_1.longitude = '-235'
        address_2.longitude = '-235'
        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))


    def test__normalization__township_twp(self):
        """
        make sure that an exact match, with a normalization works
        """
        address_1 = Address()
        address_2 = Address()
        address_1.street_number = '1'
        address_2.street_number = '1'
        address_1.street = 'Saint Louis Parkway'
        address_2.street = 'Saint Louis Parkway'
        address_1.city = 'Saint Louis TWP'
        address_2.city = 'Saint Louis township'
        address_1.state = 'FL'
        address_2.state = 'FL'
        address_1.zip_code = '33410'
        address_2.zip_code = '33410'
        address_1.longitude = '-235'
        address_2.longitude = '-235'
        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))


    def test__normalization__turnpike_tpke(self):
        """
        make sure that an exact match, with a normalization works
        """
        address_1 = Address()
        address_2 = Address()
        address_1.street_number = '1'
        address_2.street_number = '1'
        address_1.street = 'Saint Louis TPKE'
        address_2.street = 'Saint Louis turnpike'
        address_1.city = 'Saint Louis township'
        address_2.city = 'Saint Louis township'
        address_1.state = 'FL'
        address_2.state = 'FL'
        address_1.zip_code = '33410'
        address_2.zip_code = '33410'
        address_1.longitude = '-235'
        address_2.longitude = '-235'
        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))


    def test__normalization__freeway_fwy(self):
        """
        make sure that an exact match, with a normalization works
        """
        address_1 = Address()
        address_2 = Address()
        address_1.street_number = '1'
        address_2.street_number = '1'
        address_1.street = 'Saint Louis FWY'
        address_2.street = 'Saint Louis freeway'
        address_1.city = 'Saint Louis township'
        address_2.city = 'Saint Louis township'
        address_1.state = 'FL'
        address_2.state = 'FL'
        address_1.zip_code = '33410'
        address_2.zip_code = '33410'
        address_1.longitude = '-235'
        address_2.longitude = '-235'
        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))


    def test__normalization__twn_cntr__town_center(self):
        """
        make sure that an exact match, with a normalization works
        """
        address_1 = Address()
        address_2 = Address()
        address_1.street_number = '1'
        address_2.street_number = '1'
        address_1.street = 'Saint Louis turnpike'
        address_2.street = 'Saint Louis turnpike'
        address_1.city = 'Saint Louis TWN CNTR'
        address_2.city = 'Saint Louis town center'
        address_1.state = 'FL'
        address_2.state = 'FL'
        address_1.zip_code = '33410'
        address_2.zip_code = '33410'
        address_1.longitude = '-235'
        address_2.longitude = '-235'
        address_1.latitude = '115'
        address_2.latitude = '115'

        hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
        self.assertIsNotNone(hash_matcher._match([address_2]))


    def test__normalization__street_number__letters_to_digit(self):
        """
        make sure that an exact match, with a normalization of street number works
        """
        norm_dictionary = {'one':'1',
                              'two': '2',
                              'three': '3',
                              'four': '4',
                              'five': '5',
                              'six': '6',
                              'seven': '7',
                              'eight': '8',
                              'nine': '9',
                              'ten': '10'}

        # cycle through dictionary and make sure all normalization combinations match
        for number in norm_dictionary:
            address_1 = Address()
            address_2 = Address()
            address_1.street_number = number
            address_2.street_number = norm_dictionary[number]
            address_1.street = 'Saint Louis turnpike'
            address_2.street = 'Saint Louis turnpike'
            address_1.city = 'Saint Louis town center'
            address_2.city = 'Saint Louis town center'
            address_1.state = 'FL'
            address_2.state = 'FL'
            address_1.zip_code = '33410'
            address_2.zip_code = '33410'
            address_1.longitude = '-235'
            address_2.longitude = '-235'
            address_1.latitude = '115'
            address_2.latitude = '115'

            hash_matcher = HashMatcher(address_1, HashMatcherFuzziness.NotFuzzy)
            self.assertIsNotNone(hash_matcher._match([address_2]))

