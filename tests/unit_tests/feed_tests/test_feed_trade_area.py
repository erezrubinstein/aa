from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.analytics.feed_trade_area import FeedTradeArea
from bson import ObjectId
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedTradeAreaTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedTradeAreaTests, self).setUp()
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
        self.feed_trade_area = FeedTradeArea(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_trade_area, "get_company_ids_from_company_file")
        self.mox.StubOutWithMock(self.feed_trade_area, "get_store_ids_from_store_file")
        self.mox.StubOutWithMock(self.feed_trade_area, "get_address_ids_from_address_file")
        self.mox.StubOutWithMock(self.feed_trade_area, "find_raw")
        self.mox.StubOutWithMock(self.feed_trade_area, "make_final_from_cursor")
        self.mox.StubOutWithMock(self.feed_trade_area, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_trade_area, "validate_final_row_count_within_tolerance")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_trade_area.export_result = mock_export_result

        # record
        self.feed_trade_area.get_company_ids_from_company_file()
        self.feed_trade_area.get_store_ids_from_store_file()
        self.feed_trade_area.get_address_ids_from_address_file()
        self.feed_trade_area.find_raw()
        self.feed_trade_area.make_final_from_cursor(self.feed_trade_area.trade_areas)
        self.feed_trade_area.get_final_row_count()
        self.feed_trade_area.validate_final_row_count_within_tolerance()

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_trade_area.run()

        expected_result = {
            "final_file": self.feed_trade_area.final_file,
            "status": self.feed_trade_area.status,
            "row_count_raw": self.feed_trade_area.row_count_raw,
            "row_count_final": self.feed_trade_area.row_count_final,
            "num_trade_areas_null_company_id": self.feed_trade_area.num_trade_areas_null_company_id,
            "num_trade_areas_null_store_id": self.feed_trade_area.num_trade_areas_null_store_id,
            "num_trade_areas_null_address_id": self.feed_trade_area.num_trade_areas_null_address_id,
            "num_trade_areas_linked_to_non_feed_company": self.feed_trade_area.num_trade_areas_linked_to_non_feed_company,
            "num_trade_areas_linked_to_missing_store": self.feed_trade_area.num_trade_areas_linked_to_missing_store,
            "num_trade_areas_linked_to_missing_address": self.feed_trade_area.num_trade_areas_linked_to_missing_address,
            "trade_areas_null_company_id_report": self.feed_trade_area.trade_areas_null_company_id_report,
            "trade_areas_null_store_id_report": self.feed_trade_area.trade_areas_null_store_id_report,
            "trade_areas_null_address_id_report": self.feed_trade_area.trade_areas_null_address_id_report,
            "trade_areas_linked_to_non_feed_company_report": self.feed_trade_area.trade_areas_linked_to_non_feed_company_report,
            "trade_areas_linked_to_missing_store_report": self.feed_trade_area.trade_areas_linked_to_missing_store_report,
            "trade_areas_linked_to_missing_address_report": self.feed_trade_area.trade_areas_linked_to_missing_address_report,
            "duration": self.feed_trade_area.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_trade_area.company_ids_in_feed = {u"519b15df784d650a6f8ddf32"}
        self.feed_trade_area.store_ids_in_feed = {u"519b193b1d26be3eb461bdc0"}
        self.feed_trade_area.address_ids_in_feed = {u"519b193b1d26be3eb461bdbf"}

        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "company_id": u"519b15df784d650a6f8ddf32",
                "store_id": u"519b193b1d26be3eb461bdc0",
                "address_id": u"519b193b1d26be3eb461bdbf",
                "trade_area_threshold": u"pretty freakin' high, yo",
            },
            "meta": {
                "created_at": created_date,
                "updated_at": modified_date
            }
        }
        expected_clean_rows = [[
            u"51b7b891784d6565bb3cd3d9",    # trade_area_id
            u"519b15df784d650a6f8ddf32",    # company_id
            u"519b193b1d26be3eb461bdc0",    # store_id
            u"519b193b1d26be3eb461bdbf",    # address_id
            u"pretty freakin' high, yo",    # threshold
            date_YYYY_MM_DD(created_date),  # created_at
            date_YYYY_MM_DD(modified_date)  # modified_at
        ]]

        self.feed_trade_area._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
