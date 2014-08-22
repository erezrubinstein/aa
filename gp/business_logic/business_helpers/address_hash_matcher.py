from copy import deepcopy
from fuzzywuzzy import fuzz
from geoprocessing.business_logic.enums import HashMatcherFuzziness
from common.utilities.string_utilities import remove_punctuations, remove_whitespace, replace_words_in_string

__author__ = 'spacecowboy et al.'

# these global variables define the base 2 representation of each field in an address
STREETNUMBER = pow(2, 0)
STREET = pow(2, 1)
NORMALIZEDSTREET = pow(2, 2)
NORMALIZEDFIRSTWORDSTREET = pow(2, 3)
CITY = pow(2, 4)
STATE = pow(2, 5)
ZIP = pow(2, 6)
MISSINGZIP = pow(2, 7)
LONGITUDE = pow(2, 8)
LATITUDE = pow(2, 9)
LONGITUDE4 = pow(2, 10)
LATITUDE4 = pow(2, 11)
LONGITUDE3 = pow(2, 12)
LATITUDE3 = pow(2, 13)
LONGITUDE2 = pow(2, 14)
LATITUDE2 = pow(2, 15)
LONGITUDE1 = pow(2, 16)
LATITUDE1 = pow(2, 17)
NONEGATIVEONEGEOCOORDINATES = pow(2, 18)
NORMALIZEDCITY = pow(2, 19)
SUITE = pow(2,20)
NORMALIZEDSTREETNUMBER = pow(2,21)

class HashMatcher(object):

    def __init__(self, address, fuzziness = HashMatcherFuzziness.Fuzzy):
        # reprocess the address for matching
        self.processed_address = self.reprocess_for_matching(address)

        # default to no match
        self.best_candidate_address = None

        # define our canon of matching functions - they all start with matched_
        self.matching_functions = [getattr(self, key) for key in dir(self) if key.startswith('matched_') and getattr(self, key) is not None]

        # the | describes a bitwise OR - so each matching classification has a unique binary key
        self.matching_classifications_fuzzy =   [(STREETNUMBER | STREET | CITY | STATE | ZIP | LONGITUDE | LATITUDE, 'full address + full long/lat (i.e. very precise)'),
                                                 (STREETNUMBER | STREET | CITY | STATE | LONGITUDE | LATITUDE, 'full address without zip + full long/lat (allows variations in zip)'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | ZIP | LONGITUDE | LATITUDE, 'normalized full address + full long/lat (i.e. very precise)'),
                                                 (STREET | CITY | STATE | ZIP | LONGITUDE | LATITUDE, 'street + city + state + zip + full long/lat (i.e. very precise)'),
                                                 (NORMALIZEDSTREET | CITY | STATE | ZIP | LONGITUDE | LATITUDE, 'normalized street + city + state + zip + full long/lat'),
                                                 (STREETNUMBER | STREET | STATE | ZIP | LONGITUDE | LATITUDE, 'street_number + street + state + zip + full long/lat (allows variations in city names)'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | STATE | ZIP | LONGITUDE | LATITUDE, 'street_number + normalized_street + state + zip + full long/lat (allows variations in city names)'),
                                                 (STREETNUMBER | CITY | STATE | ZIP | LONGITUDE | LATITUDE, 'street_number + city + state + zip + full long/lat (allows variations in street names)'),
                                                 (STREETNUMBER | STREET | CITY | STATE | LONGITUDE | LATITUDE, 'street_number + street + city + state + full long/lat (allows variations in zip)'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | LONGITUDE | LATITUDE, 'street_number + street_normalized + city + state + full long/lat (allows variations in zip)'),
                                                 (STREETNUMBER | STREET | STATE | LONGITUDE | LATITUDE, 'street_number + street + state + full long/lat (allows variations in city and zip)'),
                                                 (STREETNUMBER | STREET | CITY | STATE | ZIP | LONGITUDE4 | LATITUDE4, 'full address + 4 digit long/lat (i.e. precise to 11.1m at the equator)'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | ZIP | LONGITUDE4 | LATITUDE4, 'full normalized address + 4 digit long/lat (i.e. precise to 11.1m at the equator)'),
                                                 (STREETNUMBER | STREET | STATE | ZIP | LONGITUDE4 | LATITUDE4, 'street_number + street + state + zip + 4-digit long/lat (allows variations in city names)'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | STATE | ZIP | LONGITUDE4 | LATITUDE4, 'street_number + street_normalized + state + zip + 4-digit long/lat (allows variations in city names)'),
                                                 (STREETNUMBER | CITY | STATE | ZIP | LONGITUDE4 | LATITUDE4, 'street_number + city + state + zip + 4-digit long/lat (allows variations in street names)'),
                                                 (STREETNUMBER | STREET | CITY | STATE | ZIP | LONGITUDE3 | LATITUDE3, 'full address + 3 digit long/lat (i.e. accurate to 111m at the equator'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | ZIP | LONGITUDE3 | LATITUDE3, 'normalized address + 3 digit long/lat (i.e. accurate to 111m at the equator'),
                                                 (STREETNUMBER | STREET | CITY | STATE | ZIP | LONGITUDE2 | LATITUDE2, 'full address + 2 digit long/lat (i.e. accurate to 1.11km at the equator'),
                                                 (NORMALIZEDSTREET | CITY | STATE | ZIP | LONGITUDE2 | LATITUDE2 , 'full normalized address + 2 digit long/lat (i.e. accurate to 1.11km at the equator'),
                                                 (STREETNUMBER | STREET | CITY | STATE | ZIP | LONGITUDE1 | LATITUDE1 , 'full address + 1 digit long/lat (i.e. accurate to 11.1km at the equator'),
                                                 (NORMALIZEDSTREET | CITY | STATE | ZIP | LONGITUDE1 | LATITUDE1 , 'full normalized address + 1 digit long/lat (i.e. accurate to 11.1km at the equator'),
                                                 (STREETNUMBER | NORMALIZEDFIRSTWORDSTREET | CITY | STATE | ZIP | LONGITUDE3 | LATITUDE3 , 'street_number + street_normalized_first_word + city + state + zip + 3-digit long/lat (allows some variation in street names )'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | MISSINGZIP | LONGITUDE4 | LATITUDE4 , 'street_number + street_normalized + city + state + [blank zip on either side] + 4-digit long/lat'),
                                                 (STREETNUMBER | NORMALIZEDFIRSTWORDSTREET | STATE | ZIP | LONGITUDE3 | LATITUDE3 , 'street_number + street_normalized_first_word + state + zip + 3-digit long/lat (allows some variation in street names and city)'),
                                                 (STREETNUMBER | NORMALIZEDFIRSTWORDSTREET | STATE | ZIP | LONGITUDE2 | LATITUDE2 , 'street_number + street_normalized_first_word + state + zip + 2-digit long/lat (allows some variation in street names and city)'),
                                                 (ZIP | LONGITUDE | LATITUDE , 'zip + full long/lat (allows variations in addresses except zip)'),
                                                 (ZIP | LONGITUDE4 | LATITUDE4 , 'zip + 4-digit long/lat (allows variations in addresses except zip)'),
                                                 (STREETNUMBER | STREET | LONGITUDE4 | LATITUDE4 , 'phone + street_number + street + 4-digit long/lat'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | MISSINGZIP | LONGITUDE3 | LATITUDE3 , 'street_number + street_normalized + city + state + [blank zip on either side] + 3-digit long/lat'),
                                                 (STREETNUMBER | NORMALIZEDFIRSTWORDSTREET | CITY | STATE | LONGITUDE3 | LATITUDE3 , 'street_number + street_normalized_first_word + city + state + 3-digit long/lat (allows some variation in street names and zip)'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | MISSINGZIP | LONGITUDE2 | LATITUDE2 , 'street_number + street_normalized street + city + state + [blank zip on either side] + 2-digit long/lat'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | MISSINGZIP | LONGITUDE1 | LATITUDE1 , 'street_number + street_normalized street + city + state + [blank zip on either side] + 1-digit long/lat'),
                                                 (STREETNUMBER | STREET | CITY | STATE | ZIP | NONEGATIVEONEGEOCOORDINATES, 'full address (i.e. very precise)'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | CITY | STATE | ZIP | NONEGATIVEONEGEOCOORDINATES, 'normalized full address (i.e. very precise)'),
                                                 (STREETNUMBER | NORMALIZEDSTREET | NORMALIZEDCITY | STATE | ZIP | NONEGATIVEONEGEOCOORDINATES, 'normalized full')]

        self.matching_classifications_not_fuzzy = [(NORMALIZEDSTREETNUMBER | NORMALIZEDSTREET | NORMALIZEDCITY | STATE | ZIP | NONEGATIVEONEGEOCOORDINATES, 'normalized full postal, no long/lat match, long/lats must not be -1'),
                                                   (NORMALIZEDSTREETNUMBER | NORMALIZEDSTREET | NORMALIZEDCITY | STATE | LONGITUDE | LATITUDE | NONEGATIVEONEGEOCOORDINATES, 'normalized postal without zip + full long/lat (i.e. very precise)'),
                                                   (NORMALIZEDSTREETNUMBER | NORMALIZEDSTREET | ZIP | STATE | LONGITUDE | LATITUDE | NONEGATIVEONEGEOCOORDINATES, 'normalized postal without city + full long/lat (i.e. very precise)'),
                                                   ]

        if fuzziness == HashMatcherFuzziness.Fuzzy:
            self.matching_classifications = self.matching_classifications_fuzzy
        elif fuzziness == HashMatcherFuzziness.NotFuzzy:
            self.matching_classifications = self.matching_classifications_not_fuzzy

########################################################################################################################
################################################# Entrance Point #######################################################
########################################################################################################################

    def get_best_address_from_candidates(self, candidate_addresses):
        self._match(candidate_addresses)
        return self.best_candidate_address

########################################################################################################################
########################################### Private Match Functions ####################################################
########################################################################################################################

    def _match(self, candidate_addresses):


        match_results = {}
        processed_addresses = {}
        tier = None
        description = None
        # first loop through the matching classifications, first tier first, second tier second, etc.
        for matching_classification_tuple in self.matching_classifications:
            classification_hash = matching_classification_tuple[0]
            tier = self.matching_classifications.index(matching_classification_tuple)
            description = matching_classification_tuple[1]
            # see if any of the candidate addresses match the current tier
            for unprocessed_candidate_address in candidate_addresses:

                # if we haven't processed this address already (we're in tier one)
                if unprocessed_candidate_address not in processed_addresses:
                    # reprocess and save to a dictionary for further reference
                    processed_addresses[unprocessed_candidate_address] = self.reprocess_for_matching(unprocessed_candidate_address)
                processed_candidate_address = processed_addresses[unprocessed_candidate_address]

                # if we don't have a result yet for this processed candidate against the input address
                if processed_candidate_address not in match_results:
                    # get a result and store it for iterations after the first tier
                    match_results[processed_candidate_address] = self._get_result(processed_candidate_address)

                result_from_match = match_results[processed_candidate_address]

                # this is a bitwise AND - it performs 'and' between each corresponding base 2 place between the key of accepted matches (classification_hash), and the result of the match
                if (classification_hash & result_from_match) == classification_hash:
                    self.best_candidate_address = unprocessed_candidate_address
                    # for testing
                    return ((tier + 1), description)


    def _get_result(self, processed_candidate_address):

        result = 0
        # to get a base 2 representation of the match, loop through each matching function below, which corresponds to a global base 2 variable defined above
        for matching_function in self.matching_functions:

            # if we're looking at longitude latitude precisions
            if matching_function.__name__.endswith('_with_precision'):

                # the word 'precision' here defines to places after the decimal to which we consider equality, starting with the most precise
                for precision in range(4, 0, -1):
                    matched_precision = matching_function(processed_candidate_address, precision)

                    # if we received a match
                    if matched_precision > 0:
                        # add to result
                        result += matched_precision
            # if we're not looking at longitude latitude precisions
            else:

                result += matching_function(processed_candidate_address)

        return result

########################################################################################################################
########################################### Public Match Functions #####################################################
########################################################################################################################
    """
    Each of these functions either returns 0, or the base 2 classification of the address entity. i.e., 0 and 5 = 0, 1 and 5 = 5
    """

    def matched_street_number(self, processed_candidate_address):
        return bool(self.processed_address.street_number == processed_candidate_address.street_number) and STREETNUMBER

    def matched_normalized_street_number(self, processed_candidate_address):
        return bool(self.__get_normalized_street_number(self.processed_address.street_number) == self.__get_normalized_street_number(processed_candidate_address.street_number)) and NORMALIZEDSTREETNUMBER

    def matched_street(self, processed_candidate_address):
        return bool(remove_whitespace(self.processed_address.street) == remove_whitespace(processed_candidate_address.street)) and STREET

    def matched_suite(self, processed_candidate_address):
        return (bool(remove_whitespace(self.__get_normalized_suite(self.processed_address.suite_numbers)) == remove_whitespace(self.__get_normalized_suite(processed_candidate_address.suite_numbers)))) and SUITE

    def matched_normalized_street(self, processed_candidate_address):

        # split string into list around white space to prepare for replacing
        normalized_street = self.__get_normalized_entity(self.processed_address.street)

        normalized_candidate_street = self.__get_normalized_entity(processed_candidate_address.street)

        return bool(remove_whitespace(remove_punctuations(normalized_street)) == remove_whitespace(remove_punctuations(normalized_candidate_street))) and NORMALIZEDSTREET

    def matched_normalized_first_word_street(self, processed_candidate_address):
        first_word_address = self.__get_normalized_entity(self.processed_address.street).split(' ')[0]
        first_word_candidate_address = self.__get_normalized_entity(processed_candidate_address.street).split(' ')[0]

        return bool(first_word_address == first_word_candidate_address) and NORMALIZEDFIRSTWORDSTREET

    def matched_city(self, processed_candidate_address):
        return bool(self.processed_address.city == processed_candidate_address.city) and CITY

    def matched_city_normalized(self, processed_candidate_address):
        # split string into list around white space to prepare for replacing
        normalized_city = self.__get_normalized_entity(self.processed_address.city)

        normalized_candidate_city = self.__get_normalized_entity(processed_candidate_address.city)

        partial_ratio = fuzz.token_set_ratio(normalized_city, normalized_candidate_city)

        return bool(remove_whitespace(remove_punctuations(normalized_city)) == remove_whitespace(remove_punctuations(normalized_candidate_city)) or partial_ratio == 100) and NORMALIZEDCITY


    def matched_state(self, processed_candidate_address):
        return bool(self.processed_address.state == processed_candidate_address.state) and STATE

    def matched_zip(self, processed_candidate_address):
        if (bool(self.processed_address.zip_code) ==  bool(processed_candidate_address.zip_code)):
            return bool(remove_whitespace(remove_punctuations(self.processed_address.zip_code)) == remove_whitespace(remove_punctuations(processed_candidate_address.zip_code))) and ZIP
        else:
            return False and ZIP

    def matched_blank_zip(self, processed_candidate_address):
        return bool(self.processed_address.zip_code or processed_candidate_address.zip_code) and MISSINGZIP

    def matched_longitude(self, processed_candidate_address):
        return bool(str(self.processed_address.longitude).strip() == str(processed_candidate_address.longitude).strip()) and LONGITUDE

    def matched_latitude(self, processed_candidate_address):
        return bool(str(self.processed_address.latitude).strip() == str(processed_candidate_address.latitude).strip()) and LATITUDE

    def matched_longitude_with_precision(self, processed_candidate_address, decimal_point_precision = 10):

        round_string = '{0:.%df}' % decimal_point_precision
        value_delta = float(round_string.format(float(self.processed_address.longitude))) - float(round_string.format(float(processed_candidate_address.longitude)))

        # this is a quick way to pull the geocoordinate precision global variables given an input precision. i.e., decimal_point_precision = 1 will yield hash_index = LONGITUDE1 = pow(2, 16)
        hash_index = globals()[''.join(['LONGITUDE' + str(decimal_point_precision)])]

        return bool(value_delta == 0) and hash_index

    def matched_no_neg_1_geo_coordinates(self, processed_candidate_address):

        return bool(str(processed_candidate_address.longitude) != str(-1) and \
                    str(processed_candidate_address.latitude) != str(-1) and \
                    str(self.processed_address.longitude) != str(-1) and \
                    str(self.processed_address.latitude) != str(-1)) and \
               NONEGATIVEONEGEOCOORDINATES

    def matched_latitude_with_precision(self, processed_candidate_address, decimal_point_precision = 10):

        round_string = '{0:.%df}' % decimal_point_precision
        value_delta = float(round_string.format(float(self.processed_address.latitude))) - float(round_string.format(float(processed_candidate_address.latitude)))

        # see the longitude description above
        hash_index = globals()[''.join(['LATITUDE' + str(decimal_point_precision)])]

        return bool(value_delta == 0) and hash_index

########################################################################################################################
######################################### Public Utility Functions #####################################################
########################################################################################################################

    def reprocess_for_matching(self, address):

        copy_address = deepcopy(address)

        # set None -> '' for the sake of the parser
        if not copy_address.street_number:
            copy_address.street_number = ''
        if not copy_address.street:
            copy_address.street = ''
        if not copy_address.city:
            copy_address.city = ''
        if not copy_address.suite_numbers:
            copy_address.suite_numbers = ''

        # reparse the incoming address
        # this step is an unneeded double-check on the address, so it's terminated
        # we can assume that all addresses coming from the database were inserted
        # by the loader with proper formatting, so there's no need to reparse it

        # reassign values. convert to lower for the sake of comparison

        copy_address.street_number = copy_address.street_number.strip().lower()
        copy_address.street = copy_address.street.strip().lower()
        copy_address.city = copy_address.city.lower()
        copy_address.state = copy_address.state.lower()
        # take the first 5 digit zip
        copy_address.zip_code = remove_whitespace(str(address.zip_code))[:5]

        #flatten suites if list
        if type(copy_address.suite_numbers) == list:
            copy_address.suite_numbers = ' '.join([item for item in address.suite_numbers]).lower()
        elif type(copy_address.suite_numbers) == str:
            copy_address.suite_numbers = copy_address.suite_numbers.lower()

        return copy_address

########################################################################################################################
######################################### Internal Match Functions #####################################################
########################################################################################################################


    def __get_normalized_entity(self, entity):
        # punctuations are evil
        entity = remove_punctuations(entity)

        # this is arbitrary - trying to set a standard for the sake of comparison
        replace_dictionary = {'north': 'n',
                              'south': 's',
                              'east': 'e',
                              'west': 'w',
                              'street': 'st',
                              'road': 'rd',
                              'lane': 'ln',
                              'plz': 'plaza',
                              'route': 'rt',
                              'highway': 'hwy',
                              'avenue': 'ave',
                              'drive': 'dr',
                              'pkwy': 'parkway',
                              'pky': 'parkway',
                              'square': 'sq',
                              'loop': 'lp',
                              'terrace': 'ter',
                              'circle': 'cir',
                              'boulevard': 'blvd',
                              'saint': 'st',
                              'fort': 'ft',
                              'heights': 'hghts',
                              'twnshp': 'township',
                              'twp': 'township',
                              'turnpike': 'tpke',
                              'town': 'twn',
                              'center': 'ctr',
                              'freeway': 'fwy'
                              }

        return replace_words_in_string(entity, replace_dictionary)

    def __get_normalized_suite(self, suite):
        # punctuations are evil
        suite = remove_punctuations(suite)

        # this is arbitrary - trying to set a standard for the sake of comparison
        replace_dictionary = {'ste':'',
                              'suite': '',
                              'suites': '',
                              'space': '',
                              'block': '',
                              'unit': ''}
        return replace_words_in_string(suite, replace_dictionary)

    def __get_normalized_street_number(self, street_number):
        # punctuations are evil
        street_number = remove_punctuations(street_number)

        # this is arbitrary - trying to set a standard for the sake of comparison
        replace_dictionary = {'one':'1',
                              'two': '2',
                              'three': '3',
                              'four': '4',
                              'five': '5',
                              'six': '6',
                              'seven': '7',
                              'eight': '8',
                              'nine': '9',
                              'ten': '10'}
        return replace_words_in_string(street_number, replace_dictionary)

def main():
    pass
    # :(

if __name__ == '__main__':
    main()