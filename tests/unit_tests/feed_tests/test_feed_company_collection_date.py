from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.entity.feed_company_collection_date import FeedCompanyCollectionDate
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedCompanyCollectionDateTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedCompanyCollectionDateTests, self).setUp()
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
        self.feed_company_collection_date = FeedCompanyCollectionDate(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_company_collection_date, "export_raw")
        self.mox.StubOutWithMock(self.feed_company_collection_date, "get_export_row_count")
        self.mox.StubOutWithMock(self.feed_company_collection_date, "get_company_ids_from_company_file")
        self.mox.StubOutWithMock(self.feed_company_collection_date, "make_final")
        self.mox.StubOutWithMock(self.feed_company_collection_date, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_company_collection_date, "validate_final_row_count_many_to_one")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_company_collection_date.export_result = mock_export_result

        # record
        self.feed_company_collection_date.export_raw()
        self.feed_company_collection_date.get_export_row_count()
        self.feed_company_collection_date.get_company_ids_from_company_file()
        self.feed_company_collection_date.make_final()
        self.feed_company_collection_date.get_final_row_count()
        self.feed_company_collection_date.validate_final_row_count_many_to_one()

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_company_collection_date.run()

        expected_result = {
            "final_file": self.feed_company_collection_date.final_file,
            "status": self.feed_company_collection_date.status,
            "row_count_raw": self.feed_company_collection_date.row_count_raw,
            "row_count_final": self.feed_company_collection_date.row_count_final,
            "collection_dates_linked_to_missing_company": self.feed_company_collection_date.collection_dates_linked_to_missing_company,
            "duration": self.feed_company_collection_date.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_collection_date.company_ids_in_feed = {u"123456789012"}

        created_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        modified_date = date_YYYY_MM_DD(datetime.datetime.utcnow())

        test_row = [
            u"ObjectID(123456789012)",  # company_id
            u'''[ { "$date" : 1368144000000 }, { "$date" : 1359331200000 } ]''',
            created_date,               # created_at
            modified_date               # updated_at
        ]
        expected_clean_rows = [
            [
                u"123456789012",
                u"2013-05-10",
                created_date,
                modified_date
            ],
            [
                u"123456789012",
                u"2013-01-28",
                created_date,
                modified_date
            ],
        ]

        self.feed_company_collection_date._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
