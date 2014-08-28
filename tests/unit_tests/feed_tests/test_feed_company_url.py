from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.entity.feed_company_url import FeedCompanyURL
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedCompanyURLTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedCompanyURLTests, self).setUp()
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
        self.feed_company_url = FeedCompanyURL(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_company_url, "export_raw")
        self.mox.StubOutWithMock(self.feed_company_url, "get_export_row_count")
        self.mox.StubOutWithMock(self.feed_company_url, "get_company_ids_from_company_file")
        self.mox.StubOutWithMock(self.feed_company_url, "make_final")
        self.mox.StubOutWithMock(self.feed_company_url, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_company_url, "validate_final_row_count_many_to_one")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_company_url.export_result = mock_export_result

        self.feed_company_url.final_file = "/out/there.csv"

        # record
        self.feed_company_url.export_raw()
        self.feed_company_url.get_export_row_count()
        self.feed_company_url.get_company_ids_from_company_file()
        self.feed_company_url.make_final()
        self.feed_company_url.get_final_row_count()
        self.feed_company_url.validate_final_row_count_many_to_one()

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_company_url.run()

        expected_result = {
            "final_file": self.feed_company_url.final_file,
            "status": self.feed_company_url.status,
            "row_count_raw": self.feed_company_url.row_count_raw,
            "row_count_final": self.feed_company_url.row_count_final,
            "urls_linked_to_missing_company": self.feed_company_url.urls_linked_to_missing_company,
            "duration": self.feed_company_url.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_url.company_ids_in_feed = {u"123456789012"}

        created_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        modified_date = date_YYYY_MM_DD(datetime.datetime.utcnow())

        test_row = [
            u"ObjectID(123456789012)",  # company_id
            u'''[{
                    "url" : "http://www.vanheusen.com",
                    "url_type" : "Main Site"
                },
                {
                    "url" : "http://www.aseriesoftubes.com",
                    "url_type" : "Fake Site"
                }]''',
            created_date,               # created_at
            modified_date               # updated_at
        ]
        expected_clean_rows = [
            [
                u"123456789012",
                u"Main Site",
                u"http://www.vanheusen.com",
                created_date,
                modified_date
            ],
            [
                u"123456789012",
                u"Fake Site",
                u"http://www.aseriesoftubes.com",
                created_date,
                modified_date
            ],
        ]

        self.feed_company_url._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
