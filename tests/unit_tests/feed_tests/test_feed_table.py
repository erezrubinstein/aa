from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from common.utilities.time_series import get_monthly_time_series
from feed.helpers.feed_helper import date_YYYY_MM_DD, replace_none
from feed.tables.feed_table import FeedTable
import random
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedTableTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedTableTests, self).setUp()
        # set up mocks
        register_common_mock_dependencies()

        mock_config = {
            "MONGODB_HOST_MDS": "nope",
            "MONGODB_PORT_MDS": "no_way",
            "DB_PREFIX": "you_wish",
            "FEED_OUTPUT_DIR": "most_certainly_not",
            "FEED_REPORTS_BATCH_DIR": "nadda"
        }
        mock_logger = Dependency("SimpleConsole").value
        self.feed_table = FeedTable(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()

    def test_write_time_series_rows_basic(self):

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        # try null values
        test_series = [{"date": m, "value": random.random() * 1000} for m in months]
        expected_rows = [[
            u"an_entity_id",
            u"1024",
            u"M",
            date_YYYY_MM_DD(t["date"]),
            replace_none(str(round(t["value"], 6))),
            created_date,
            modified_date
        ] for t in test_series]

        # should just not write anything
        self.feed_table._write_time_series_rows(mock_writer, u"an_entity_id", 1024, u"M", test_series, created_date, modified_date)

        self.assertEqual(self.row_values, expected_rows)

    def test_write_time_series_rows_null_values(self):

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        # try null values
        test_series = [{"date": m, "value": None} for m in months]

        # should just not write anything
        self.feed_table._write_time_series_rows(mock_writer, u"an_entity_id", 1024, "M", test_series, created_date, modified_date)

        self.assertEqual(self.row_values, [])

    def test_write_time_series_rows_null_dates(self):

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        # try null values
        test_series = [{"date": None, "value": random.random() * 1000} for m in months]

        # should just not write anything
        self.feed_table._write_time_series_rows(mock_writer, u"an_entity_id", 1024, "M", test_series, created_date, modified_date)

        self.assertEqual(self.row_values, [])


    def test_write_time_series_rows_zero_values(self):
        """
        Zero's *should* be written to files!
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        # try null values
        test_series = [{"date": m, "value": 0.0} for m in months]
        expected_rows = [[
            u"an_entity_id",
            u"1024",
            u"M",
            date_YYYY_MM_DD(t["date"]),
            u"0.0",
            created_date,
            modified_date
        ] for t in test_series]

        # should just not write anything
        self.feed_table._write_time_series_rows(mock_writer, u"an_entity_id", 1024, "M", test_series, created_date, modified_date)

        self.assertEqual(self.row_values, expected_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
