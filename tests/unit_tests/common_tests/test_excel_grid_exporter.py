from common.web_helpers.export_helpers.excel_grid_exporter import ExcelGridExporter
from common.helpers.mock_providers.mock_logger import MockLogger

import unittest
import datetime
import mox

__author__ = 'jsternberg'

class ExcelGridExporterTests(mox.MoxTestBase):

    def setUp(self):

         # call parent set up
        super(ExcelGridExporterTests, self).setUp()

        self.grid_data = {
            "field_list": ["Good", "Bad"],
            "results": [
                [datetime.datetime(2014,1,1), None]
            ]
        }

        self.test_worksheet_name = "test_worksheet"

        self.exporter = ExcelGridExporter(self.grid_data, self.test_worksheet_name, MockLogger())


    def test_write_date_month_year_valid_date(self):

        # create a mock row
        mock_row = self.mox.CreateMockAnything()

        # stub out the cell date method
        self.mox.StubOutWithMock(mock_row, "set_cell_date")

        # gather test data
        row_data = self.grid_data["results"][0]
        test_date = row_data[0]

        # we expect this call, only
        mock_row.set_cell_date(0, test_date, self.exporter.date_format_month_year).AndReturn(None)

        # replay all
        self.mox.ReplayAll()

        # make it happen
        self.exporter._write_date_month_year(mock_row, 0, test_date)


    def test_write_date_month_year_invalid_date(self):

        # create a mock row
        mock_row = self.mox.CreateMockAnything()

        # stub out the exporter cell width method
        self.mox.StubOutWithMock(self.exporter, "_track_max_character")

        # gather test data
        row_data = self.grid_data["results"][0]
        test_date = row_data[1]

        # we expect this call, only
        self.exporter._track_max_character(0, "     ").AndReturn(None)

        # replay all
        self.mox.ReplayAll()

        # make it happen
        self.exporter._write_date_month_year(mock_row, 0, test_date)





if __name__ == '__main__':
    unittest.main()
