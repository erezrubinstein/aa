from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.entity.feed_address import FeedAddress
import datetime
import unittest
import mox

__author__ = 'jsternberg'

class FeedAddressTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedAddressTests, self).setUp()
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
        self.feed_address = FeedAddress(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_address, "export_raw")
        self.mox.StubOutWithMock(self.feed_address, "get_export_row_count")
        self.mox.StubOutWithMock(self.feed_address, "make_final")
        self.mox.StubOutWithMock(self.feed_address, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_address, "validate_final_row_count_exact")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_address.export_result = mock_export_result

        # record
        self.feed_address.export_raw()
        self.feed_address.get_export_row_count()
        self.feed_address.make_final()
        self.feed_address.get_final_row_count()
        self.feed_address.validate_final_row_count_exact()

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_address.run()

        expected_result = {
            "final_file": self.feed_address.final_file,
            "status": self.feed_address.status,
            "row_count_raw": self.feed_address.row_count_raw,
            "row_count_final": self.feed_address.row_count_final,
            "duration": self.feed_address.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        created_date = date_YYYY_MM_DD(datetime.datetime.utcnow())
        modified_date = date_YYYY_MM_DD(datetime.datetime.utcnow())

        test_row = [
            u"ObjectID(52809c9c3f0cd20ede6741fb)",      # address_id
            u"123",                                     # street_number
            u"Fake St",                                 # street
            u"STE 123\nMall of Shameless Consumerism",  # suite
            u"Anytown",                                 # city
            u"NY",                                      # state
            u"11017",                                   # zip
            u"Grand Central Market",                    # shopping_center
            created_date,                               # created_at
            modified_date                               # modified_at
        ]
        expected_clean_rows = [[
            u"52809c9c3f0cd20ede6741fb",
            u"123",
            u"Fake St",
            u"""STE 123 Mall of Shameless Consumerism""",
            u"Anytown",
            u"NY",
            u"11017",
            u"Grand Central Market",
            created_date,
            modified_date
        ]]

        self.feed_address._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
