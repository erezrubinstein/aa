from mox import IsA
import xlwt
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency
from retail.v010.helpers.export_helpers.retail_store_exporter import ExcelStoreExporter

__author__ = 'erezrubinstein'

import unittest
import mox


class RetailStoreExporterTests(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(RetailStoreExporterTests, self).setUp()

        # init mox dependencies
        register_common_mox_dependencies(self.mox)

        # get dependencies
        self.mock_logger = Dependency("FlaskLogger").value


    def test_init_cleans_headers(self):

        # create mock_stores structure with headers that have html in them (i.e. the real clean header fields)
        mock_stores = {
            "field_list": ["Company Name", "State", "City", "Trade Area", "Population\n(000)", "Per Capita Income\n($)", "Aggregate Income\n($M)", "Households\n(000)",
                           "&lt;&nbsp;$15K\n(000)", "$15-25K\n(000)", "$25-35K\n(000)", "$35-50K\n(000)", "$50-75K\n(000)", "$75-100K\n(000)", "$100-150K\n(000)",
                           "$150-200K\n(000)", "$200K+\n(000)", "Store ID", "Street Number", "Street", "Suite", "Zip Code", "Phone Number", "Store Opened", "Store Closed",
                           "Company ID", "Trade Area ID"],
            "results": []
        }

        # create the object
        exporter = ExcelStoreExporter(mock_stores, "test", self.mock_logger)

        # verify that the headers have the html stripped out
        self.assertEqual(exporter.headers,
                         ["Company Name", "State", "City", "Trade Area", "Population (000)", "Per Capita Income ($)", "Aggregate Income ($M)", "Households (000)",
                          "< $15K (000)", "$15-25K (000)", "$25-35K (000)", "$35-50K (000)", "$50-75K (000)", "$75-100K (000)", "$100-150K (000)",
                          "$150-200K (000)", "$200K+ (000)", "Store ID", "Street Number", "Street", "Suite", "Zip Code", "Phone Number", "Store Opened", "Store Closed",
                          "Company ID", "Trade Area ID"])


    def test_export__worksheet_name_limit(self):
        # worksheet_name with 32 characters
        worksheet_name = "12345678901234567890123456789012"

        # mock stores
        mock_stores = {
            "field_list": [],
            "results": []
        }

        # create exporter
        exporter = ExcelStoreExporter(mock_stores, worksheet_name, self.mock_logger)

        # verify that the worksheet name was truncated to 31 characters
        self.assertEqual(exporter.worksheet_name, "1234567890123456789012345678901")

        # make sure it was 32 before, and now 31
        self.assertEqual(len(worksheet_name), 32)
        self.assertEqual(len(exporter.worksheet_name), 31)


    def test_export(self):
        """
        Verify that an export is working correctly
        """

        # create fake data
        worksheet_name = "chicken_woot"
        mock_stores = {
            "field_list": [
                 "Company Name", "State", "City", "Trade Area", "Population (000)", "Per Capita Income ($)", "Aggregate Income ($M)", "Households (000)",
                 "< $15K (000)", "$15-25K (000)", "$25-35K (000)", "$35-50K (000)", "$50-75K (000)", "$75-100K (000)", "$100-150K (000)", "$150-200K (000)", "$200K+ (000)",
                 "Store ID", "Street Number", "Street", "Suite", "Zip Code", "Phone Number", "Store Opened", "Store Closed", "Company ID", "Trade Area ID"
             ],
             "results": [
                 ["test company 1", "state", "city", "10 Mile Circle", 142695, 25644, 999999999, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 2, "street_number", "street", "suite", "zip", "phone", "2012-01-01", None, 1, 1],
                 ["test company 1", "state", "city", "10 Mile Circle", 142695, 25644, 999999999, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 3, "street_number", "street", "suite", "zip", "phone", "2012-01-15", "2013-01-01", 1, 2]
             ]
        }

        # create various mock objects
        mock_workbook = self.mox.CreateMockAnything()
        mock_sheet = self.mox.CreateMockAnything()
        mock_row = self.mox.CreateMockAnything()

        # create exporter
        exporter = ExcelStoreExporter(mock_stores, worksheet_name, self.mock_logger)

        # stub various methods/classes
        self.mox.StubOutWithMock(xlwt, "Workbook")
        self.mox.StubOutWithMock(exporter, "_track_max_character")
        self.mox.StubOutWithMock(exporter, "_set_auto_widths")

        # ------------- Begin Recording (long) -------------

        # create worksheet and workbook
        xlwt.Workbook().AndReturn(mock_workbook)
        mock_workbook.add_sheet(worksheet_name).AndReturn(mock_sheet)

        # add all headers (skip those that should be skipped)
        mock_sheet.write(0, 0, "Company Name", IsA(xlwt.XFStyle))
        exporter._track_max_character(0, "Company Name")
        mock_sheet.write(0, 1, "State", IsA(xlwt.XFStyle))
        exporter._track_max_character(1, "State")
        mock_sheet.write(0, 2, "City", IsA(xlwt.XFStyle))
        exporter._track_max_character(2, "City")
        mock_sheet.write(0, 3, "Trade Area", IsA(xlwt.XFStyle))
        exporter._track_max_character(3, "Trade Area")
        mock_sheet.write(0, 4, "Population (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(4, "Population (000)")
        mock_sheet.write(0, 5, "Per Capita Income ($)", IsA(xlwt.XFStyle))
        exporter._track_max_character(5, "Per Capita Income ($)")
        mock_sheet.write(0, 6, "Aggregate Income ($M)", IsA(xlwt.XFStyle))
        exporter._track_max_character(6, "Aggregate Income ($M)")
        mock_sheet.write(0, 7, "Households (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(7, "Households (000)")
        mock_sheet.write(0, 8, "< $15K (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(8, "< $15K (000)")
        mock_sheet.write(0, 9, "$15-25K (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(9, "$15-25K (000)")
        mock_sheet.write(0, 10, "$25-35K (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(10, "$25-35K (000)")
        mock_sheet.write(0, 11, "$35-50K (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(11, "$35-50K (000)")
        mock_sheet.write(0, 12, "$50-75K (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(12, "$50-75K (000)")
        mock_sheet.write(0, 13, "$75-100K (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(13, "$75-100K (000)")
        mock_sheet.write(0, 14, "$100-150K (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(14, "$100-150K (000)")
        mock_sheet.write(0, 15, "$150-200K (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(15, "$150-200K (000)")
        mock_sheet.write(0, 16, "$200K+ (000)", IsA(xlwt.XFStyle))
        exporter._track_max_character(16, "$200K+ (000)")
        mock_sheet.write(0, 17, "Street Number", IsA(xlwt.XFStyle))
        exporter._track_max_character(17, "Street Number")
        mock_sheet.write(0, 18, "Street", IsA(xlwt.XFStyle))
        exporter._track_max_character(18, "Street")
        mock_sheet.write(0, 19, "Suite", IsA(xlwt.XFStyle))
        exporter._track_max_character(19, "Suite")
        mock_sheet.write(0, 20, "Zip Code", IsA(xlwt.XFStyle))
        exporter._track_max_character(20, "Zip Code")
        mock_sheet.write(0, 21, "Phone Number", IsA(xlwt.XFStyle))
        exporter._track_max_character(21, "Phone Number")
        mock_sheet.write(0, 22, "Store Opened", IsA(xlwt.XFStyle))
        exporter._track_max_character(22, "Store Opened")
        mock_sheet.write(0, 23, "Store Closed", IsA(xlwt.XFStyle))
        exporter._track_max_character(23, "Store Closed")

        # write down all the fields from each row (skip those fields that should be skipped)
        mock_sheet.row(1).AndReturn(mock_row)
        mock_row.set_cell_text(0, "test company 1")
        exporter._track_max_character(0, "test company 1")
        mock_row.set_cell_text(1, "state")
        exporter._track_max_character(1, "state")
        mock_row.set_cell_text(2, "city")
        exporter._track_max_character(2, "city")
        mock_row.set_cell_text(3, "10 Mile Circle")
        exporter._track_max_character(3, "10 Mile Circle")
        mock_row.set_cell_number(4, 142.695, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(4, 142695)
        mock_row.set_cell_number(5, 25644, exporter.dollar_style)
        exporter._track_max_character(5, 25644)
        mock_row.set_cell_number(6, 999.999999, exporter.dollar_style)
        exporter._track_max_character(6, 999999999)
        mock_row.set_cell_number(7, 5.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(7, 5000)
        mock_row.set_cell_number(8, 6.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(8, 6000)
        mock_row.set_cell_number(9, 7.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(9, 7000)
        mock_row.set_cell_number(10, 8.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(10, 8000)
        mock_row.set_cell_number(11, 9.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(11, 9000)
        mock_row.set_cell_number(12, 10.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(12, 10000)
        mock_row.set_cell_number(13, 11.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(13, 11000)
        mock_row.set_cell_number(14, 12.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(14, 12000)
        mock_row.set_cell_number(15, 13.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(15, 13000)
        mock_row.set_cell_number(16, 14.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(16, 14000)
        mock_row.set_cell_text(17, "street_number")
        exporter._track_max_character(17, "street_number")
        mock_row.set_cell_text(18, "street")
        exporter._track_max_character(18, "street")
        mock_row.set_cell_text(19, "suite")
        exporter._track_max_character(19, "suite")
        mock_row.set_cell_text(20, "zip")
        exporter._track_max_character(20, "zip")
        mock_row.set_cell_text(21, "phone")
        exporter._track_max_character(21, "phone")
        mock_row.set_cell_text(22, "2012-01-01")
        exporter._track_max_character(22, "2012-01-01")
        exporter._track_max_character(23, "     ")

        # second row
        mock_sheet.row(2).AndReturn(mock_row)
        mock_row.set_cell_text(0, "test company 1")
        exporter._track_max_character(0, "test company 1")
        mock_row.set_cell_text(1, "state")
        exporter._track_max_character(1, "state")
        mock_row.set_cell_text(2, "city")
        exporter._track_max_character(2, "city")
        mock_row.set_cell_text(3, "10 Mile Circle")
        exporter._track_max_character(3, "10 Mile Circle")
        mock_row.set_cell_number(4, 142.695, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(4, 142695)
        mock_row.set_cell_number(5, 25644, exporter.dollar_style)
        exporter._track_max_character(5, 25644)
        mock_row.set_cell_number(6, 999.999999, exporter.dollar_style)
        exporter._track_max_character(6, 999999999)
        mock_row.set_cell_number(7, 5.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(7, 5000)
        mock_row.set_cell_number(8, 6.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(8, 6000)
        mock_row.set_cell_number(9, 7.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(9, 7000)
        mock_row.set_cell_number(10, 8.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(10, 8000)
        mock_row.set_cell_number(11, 9.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(11, 9000)
        mock_row.set_cell_number(12, 10.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(12, 10000)
        mock_row.set_cell_number(13, 11.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(13, 11000)
        mock_row.set_cell_number(14, 12.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(14, 12000)
        mock_row.set_cell_number(15, 13.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(15, 13000)
        mock_row.set_cell_number(16, 14.000, exporter.thousands_1_decimal_place_style)
        exporter._track_max_character(16, 14000)
        mock_row.set_cell_text(17, "street_number")
        exporter._track_max_character(17, "street_number")
        mock_row.set_cell_text(18, "street")
        exporter._track_max_character(18, "street")
        mock_row.set_cell_text(19, "suite")
        exporter._track_max_character(19, "suite")
        mock_row.set_cell_text(20, "zip")
        exporter._track_max_character(20, "zip")
        mock_row.set_cell_text(21, "phone")
        exporter._track_max_character(21, "phone")
        mock_row.set_cell_text(22, "2012-01-15")
        exporter._track_max_character(22, "2012-01-15")
        mock_row.set_cell_text(23, "2013-01-01")
        exporter._track_max_character(23, "2013-01-01")

        # set auto widths
        exporter._set_auto_widths(mock_sheet)

        # ------------- End Recording (long) -------------


        # replay all
        self.mox.ReplayAll()

        # go!
        workbook = exporter.get_excel_workbook()

        # make sure workbook is the excel workbook
        self.assertEqual(workbook, mock_workbook)


if __name__ == '__main__':
    unittest.main()
