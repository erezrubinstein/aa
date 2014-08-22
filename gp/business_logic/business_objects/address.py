from datetime import datetime

__author__ = 'erezrubinstein'

from fractions import Fraction
from common.utilities.inversion_of_control import Dependency, HasMethods, dependencies
from common.utilities.signal_math import SignalDecimal

class Address(object):
    """
    This class represents an address and its various related object model properties
    """
    def __init__(self):
    # set up empty parameters
        self.address_id = None
        self.street_number = None
        self.street = None
        self.city = None
        self.state = None
        self.zip_code = None
        self.country_id = None
        self.latitude = None
        self.longitude = None
        self.suite_numbers = None
        self.complex = None
        self.note = None
        self.phone_number = None
        self.mismatched_parameters = []
        self.change_type = None

        # instantiate priate members for properties
        # always assume opened, source dates of 1/1/1900 unless otherwise set
        self._opened_on = datetime(1900, 1, 1)
        self._source_date = None

    ########################################################  Properties  #########################################################################
    @property
    def opened_on(self):
        return self._opened_on
    @opened_on.setter
    def opened_on(self, value):
        if value and isinstance(value, datetime):
            self._opened_on = value

    @property
    def source_date(self):
        return self._source_date
    @source_date.setter
    def source_date(self, value):
        if value and isinstance(value, datetime):
            self._source_date = value




    #####################################################  Factory Methods  #######################################################################

    @classmethod
    def standard_init(cls, address_id, street_number, street, city, state, zip_code, country_id,
                      latitude, longitude, suite_numbers, complex):
        address = Address()
        address.address_id = address_id
        if street_number is not None:
            address.street_number = street_number
        address.street = street
        address.city = city
        address.state = state
        address.zip_code = validate_zip(zip_code)
        address.country_id = country_id
        if latitude is not None:
            address.latitude = SignalDecimal(latitude)
        if longitude is not None:
            address.longitude = SignalDecimal(longitude)
        address.suite_numbers = suite_numbers
        address.complex = complex
        return address


    # the below factory method is specific to the data loader and contains fields that are not specifically address related.
    # this is a workaround and should eventually be refactored and deprecated.
    @classmethod
    def complex_init_for_loader(cls, address_id, street_number, street, city, state, zip_code, country_id, latitude, longitude, loader_opened_on = None,
                                source_date = None, note = None, suite_numbers = None, complex = None, phone_number = None, mismatched_parameters = [],
                                store_format = None, company_generated_store_number = None, loader_record_id = None):

        address = cls.standard_init(address_id, street_number, street, city, state, zip_code, country_id, latitude, longitude, suite_numbers, complex)

        # fill in complex non-address fields that are loader specific
        address.phone_number = phone_number
        address.mismatched_parameters = mismatched_parameters
        address.loader_opened_on = loader_opened_on
        if address.loader_opened_on:
            address._opened_on = address.loader_opened_on
        address.source_date = source_date
        address.note = note
        address.store_format = store_format
        address.company_generated_store_number = company_generated_store_number
        address.loader_record_id = loader_record_id
        return address


    @classmethod
    def select_by_id(cls, address_id):
    # query the address
        data_repository = Dependency("DataRepository", HasMethods("get_address_by_id")).value
        return data_repository.get_address_by_id(address_id)



    #####################################################  Private Methods  #######################################################################
    # validate and clean-up a zip code
    # note that this is a pretty basic implementation. We should scale this up eventually


    def __str__(self):
        attribute_list = []
        for key in self.__dict__:
            attribute_list.append(': '.join([key, str(self.__dict__[key])]))
        return ', '.join(attribute_list)




def validate_zip(zip):
    # None's allllright...

    if zip is None:
        return None

    zip = str(zip).encode('utf-8')
    # to account for 9 digit zip codes without the '-'
    if len(zip) > 5:
        if '-' in zip:
            pre_dash = zip.split('-')[0]
            post_dash = zip.split('-')[1]
            missing_zeros = 5-int(len(pre_dash))
            for add_zero in range(missing_zeros):
                pre_dash = ''.join(['0', pre_dash])
            zip = '-'.join([pre_dash, post_dash])
        else:
            missing_zeros = 9-int(len(zip))
            for digit in range(missing_zeros):
                zip = ''.join(['0', zip])
            zip = '-'.join([zip[:5], zip[5:]])
            pre_dash = zip.split('-')[0]
            post_dash = zip.split('-')[1]

    digit_sum = 0
    # determine if the zip code is like 0 or 0*
    for digit in str(zip):
        if digit.isdigit():
            digit_sum += int(digit)
        # fail the test if we get anything that's not 0 or -
        elif digit != '-':
            digit_sum += 1



    if digit_sum == 0:
        return None

    # parsers can cast to string, but let's double-check-good it here

    elif len(zip) == 3 and str.isdigit(zip):
        # yes this does exist -- Holtsville, NY is 00501 (also http://www.brainyzip.com/zips/zip_00.html)
        return '00' + zip
    elif len(zip) == 4 and str.isdigit(zip):
        # many zip codes have 1 leading zero
        return '0' + zip

    elif len(zip) == 5 and str(zip).isdigit():
        # normal 5 digit zip code
        return zip

    elif '-' in zip and len(pre_dash) == 5 and len(post_dash) == 4 and str(zip.replace('-', '')).isdigit():
        # zip + 4 format
        return zip

    elif '-' in zip and len(pre_dash) == 4 and len(post_dash) == 4 and str(zip.replace('-', '')).isdigit():
        # zip + 4 format
        return '0' + zip

    else:
        raise ValueError('Unrecognized zip code format: %s' % zip)

