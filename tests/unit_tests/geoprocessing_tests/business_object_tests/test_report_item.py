#!/usr/bin/env python
#coding: utf8
# ER - encoding for unicode test below

import unittest
from geoprocessing.business_logic.business_objects.report_item import ReportItem

__author__ = 'erezrubinstein'

class ReportItemTests(unittest.TestCase):

    def test_parse_report_item_with_number(self):
        report_item = ReportItem("Name", "10", "Description")
        self.__common_report_item_asserts(report_item, "Name", "Description", 10, "number", "num", None, None, None, 2011)

    def test_parse_report_item_with_percent(self):
        report_item = ReportItem("Name", "10%", "Description")
        self.__common_report_item_asserts(report_item, "Name", "Description", 10, "number", "num", None, None, None, 2011)

    def test_parse_report_item_with_percent_2(self):
        report_item = ReportItem("Name", "0.20%", "Description")
        self.__common_report_item_asserts(report_item, "Name", "Description", 0.2, "number", "num", None, None, None, 2011)

    def test_parse_report_item_with_comma(self):
        report_item = ReportItem("Name", "17,000", "Description")
        self.__common_report_item_asserts(report_item, "Name", "Description", 17000, "number", "num", None, None, None, 2011)

    def test_parse_report_item_with_string(self):
        report_item = ReportItem("Name", "string value", "Description")
        self.__common_report_item_asserts(report_item, "Name", "Description", "string value", "string", "str", None, None, None, 2011)

    def test_parse_report_item_with_unicode_string(self):
        """
        This tests a bug fix for BA_Online unicode results
        """
        report_item = ReportItem("Street", u"Pso del Cañon E", "Unicode Street")
        self.__common_report_item_asserts(report_item, "Street", "Unicode Street", u"Pso del Cañon E", "string", "str", None, None, None, 2011)

    def test_parse_report_item_with_female(self):
        report_item = ReportItem("Name", "10", "FEM0C10")
        self.__common_report_item_asserts(report_item, "Name", "FEM0C10", 10, "number", "num", 'F', 0, 4, 2011)

    def test_parse_report_item_with_female__85_plus(self):
        # make sure that FEM85C10 hard-codes the max age to None (i.e. 85+)
        report_item = ReportItem("Name", "10", "FEM85C10")
        self.__common_report_item_asserts(report_item, "Name", "FEM85C10", 10, "number", "num", 'F',
            85, None, 2011)

    def test_parse_report_item_with_male(self):
        report_item = ReportItem("Name", "10", "MALE0C10")
        self.__common_report_item_asserts(report_item, "Name", "MALE0C10", 10, "number", "num", 'M',
            0, 4, 2011)

    def test_parse_report_item_with_male__85_plus(self):
        # make sure that MALE85C10 hard-codes the max age to None (i.e. 85+)
        report_item = ReportItem("Name", "10", "MALE85C10")
        self.__common_report_item_asserts(report_item, "Name", "MALE85C10", 10, "number", "num", 'M',
            85, None, 2011)

    def test_parse_report_item_with_fiscal_year(self):
        """
        This test verifies that a report item that ends with _FY gets a static year of 2016
        """
        report_item = ReportItem("Name_FY", "10", "MALE0C10")
        self.__common_report_item_asserts(report_item, "Name_FY", "MALE0C10", 10, "number", "num", 'M',
            0, 4, 2016)

    def test_parse_report_item_with_census_year(self):
        """
        This test verifies that a report item that ends with _CY gets a static year of 2011
        """
        report_item = ReportItem("Name_CY", "10", "MALE0C10")
        self.__common_report_item_asserts(report_item, "Name_CY", "MALE0C10", 10, "number", "num", 'M',
            0, 4, 2011)

    def test_parse_report_item_with_2010(self):
        """
        This test verifies that a report item that ends with 10 gets a static year of 2010
        """
        report_item = ReportItem("Name10", "10", "MALE0C10")
        self.__common_report_item_asserts(report_item, "Name10", "MALE0C10", 10, "number", "num", 'M',
            0, 4, 2010)

    def __common_report_item_asserts(self, report_item, name, description, value, value_type, type_short, gender, minimum_age,
                                     maximum_age, year):
        """ Common asserts for report item class """
        self.assertEqual(report_item.name, name)
        self.assertEqual(report_item.description, description)
        self.assertEqual(report_item.value, value)
        self.assertEqual(report_item.value_type, value_type)
        self.assertEqual(report_item.type_short, type_short)
        self.assertEqual(report_item.gender, gender)
        self.assertEqual(report_item.minimum_age, minimum_age)
        self.assertEqual(report_item.maximum_age, maximum_age)
        self.assertEqual(report_item.year, year)


if __name__ == '__main__':
    unittest.main()