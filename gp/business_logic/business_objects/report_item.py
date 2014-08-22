"""
Created on Oct 17, 2012

"""
import re

__author__ = 'spacecowboy'

class ReportItem(object):
    """
    This object is in charge of parsing out ArcGIS ReportItems
    """
    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

        #parse out value into other members
        if value is not None:
            self.__parse_value()
        if description is not None:
            self.__parse_description()

        # set sql-determined default values
        self.data_item_id = None
        self.segment_id = None

    def __parse_value(self):
        # remove certain characters if removing them makes it a digit.  replace period when checking, but do not remove
        if self.value.replace('%', '').replace(',', '').replace('.', '').isdigit():
            self.value = self.value.replace('%', '')
            self.value = self.value.replace(',', '')

        try:
            self.value = float(self.value)
            self.value_type = 'number'
            self.type_short = 'num'
        except:
            self.value = self.value
            self.value_type = 'string'
            self.type_short = 'str'

    def __parse_description(self):
        self.__get_gender_age_ranges()
        self.__get_year()

    def __get_gender_age_ranges(self):
        f_match = re.search('.*FEM(\d+)C(\d*)', self.description)
        m_match = re.search('.*MALE(\d+)C(\d*)', self.description)

        if f_match is not None:
            self.gender = 'F'
            self.__parse_min_max_age(f_match)
        elif m_match is not None:
            self.gender = 'M'
            self.__parse_min_max_age(m_match)
        else:
            self.gender = None
            self.minimum_age = None
            self.maximum_age = None

    def __parse_min_max_age(self, regex):
        self.minimum_age = int(regex.group(1))

        # this is a very specific case to ESRI and how it considers "MALE85C10"	to be "2010 Male Population 85+"
        # unfortunately, there is no way to distinguish by name, so we have to hard-code 85
        if self.minimum_age == 85:
            self.maximum_age = None
        else:
            self.maximum_age = self.minimum_age + 4

    def __get_year(self):
        if self.name[-3:] == '_FY':
            self.year = 2016
        elif self.name[-3:] == '_CY':
            self.year = 2011
        elif self.name[-2:] == '10':
            self.year = 2010
        else:
            # default to census year
            self.year = 2011