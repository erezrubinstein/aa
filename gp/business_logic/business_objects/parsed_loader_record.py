from datetime import datetime
from common.utilities.signal_math import SignalDecimal
from geoprocessing.business_logic.business_objects.address import validate_zip

__author__ = 'spacecowboy et al.'

class ParsedLoaderRecord(object):
    """
    The beginning skeleton of a loader record object. My question to the reader:
    Q: Should include here the cleaning up logic currently implemented in the excel helper for the address row?
    A:
    """
    def __init__(self, address_id = None,
                       street_number = None,
                       street = None,
                       city = None,
                       state = None,
                       zip_code = None,
                       country_id = None,
                       longitude = None,
                       latitude = None,
                       suite_numbers = None,
                       complex = None,
                       loader_opened_on = None,
                       source_date = None,
                       note = None,
                       store_format = None,
                       company_generated_store_number = None,
                       loader_record_id = None,
                       phone_number = None,
                       row_number = None,
                       source_file = None,
                       source_file_id = None,
                       company_name = None,
                       company_id = None,
                       core_store_id = None):

        self.address_id = address_id
        self._opened_on = datetime(1900, 1, 1)
        self._source_date = None
        self.street_number = street_number

        self.street = street
        self.city = city
        self.state = state
        self.zip_code = validate_zip(zip_code)

        self.country_id = country_id
        if country_id is None:
            self.country_id = 840


        self.phone_number = phone_number
        if latitude is not None:
            self.latitude = SignalDecimal(latitude)
        if longitude is not None:
            self.longitude = SignalDecimal(longitude)
        self.suite_numbers = suite_numbers
        self.complex = complex


        self.note = note
        self.store_format = store_format
        self.company_generated_store_number = company_generated_store_number
        self.loader_record_id = loader_record_id

        self.loader_opened_on = loader_opened_on
        if self.loader_opened_on:
            self._opened_on = self.loader_opened_on
        self.source_date = source_date
        self.row_number = row_number
        self.source_file = source_file
        self.source_file_id = source_file_id
        self.company_name = company_name
        self.company_id = company_id
        self.core_store_id = core_store_id

        # adding in keys that match the address keys we're using as of 3/20/13
        # todo: clean this up when impact is determined
        self.suite = suite_numbers
        self.zip = zip_code
        self.geo = [longitude, latitude]
        self.shopping_center = complex
        self.country = country_id



#``````````````````````````````````Properties````````````````````````````````````````#

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