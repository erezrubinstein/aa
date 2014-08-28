from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.entity.feed_industry import FeedIndustry
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedIndustryTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedIndustryTests, self).setUp()
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
        self.feed_industry = FeedIndustry(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_industry, "export_raw")
        self.mox.StubOutWithMock(self.feed_industry, "get_export_row_count")
        self.mox.StubOutWithMock(self.feed_industry, "make_final")
        self.mox.StubOutWithMock(self.feed_industry, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_industry, "validate_final_row_count_exact")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_industry.export_result = mock_export_result
        self.feed_industry.status = "not as confused as Nigel"

        # record
        self.feed_industry.export_raw()
        self.feed_industry.get_export_row_count()
        self.feed_industry.make_final()
        self.feed_industry.get_final_row_count()
        self.feed_industry.validate_final_row_count_exact()

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_industry.run()

        expected_result = {
            "final_file": self.feed_industry.final_file,
            "status": self.feed_industry.status,
            "row_count_raw": self.feed_industry.row_count_raw,
            "row_count_final": self.feed_industry.row_count_final,
            "duration": self.feed_industry.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_industry.comp_published_industries = {u"52f83fc22345e32965167683"}

        created_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        modified_date = date_YYYY_MM_DD(datetime.datetime.utcnow())

        test_row = [
            u"ObjectID(123456789012)",  # industry_id
            u"baskin",                  # industry_name
            u"ice cream",               # source_vendor
            u"chocolate",               # industry_code
            u"1024",                    # industry_level
            u"12",                      # source_version
            created_date,               # created_at
            modified_date               # modified_at
        ]
        expected_clean_rows = [[
            u"123456789012",
            u"baskin",
            u"ice cream",
            u"chocolate",
            u"1024",
            u"12",
            created_date,
            modified_date
        ]]

        self.feed_industry._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
