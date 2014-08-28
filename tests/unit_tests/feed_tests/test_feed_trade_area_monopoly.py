from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.analytics.feed_trade_area_monopoly import FeedTradeAreaMonopoly
from bson import ObjectId
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedTradeAreaMonopolyTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedTradeAreaMonopolyTests, self).setUp()
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
        self.feed_trade_area_monopoly = FeedTradeAreaMonopoly(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_trade_area_monopoly, "get_trade_area_ids_from_trade_area_file")
        self.mox.StubOutWithMock(self.feed_trade_area_monopoly, "find_raw")
        self.mox.StubOutWithMock(self.feed_trade_area_monopoly, "make_final_from_cursor")
        self.mox.StubOutWithMock(self.feed_trade_area_monopoly, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_trade_area_monopoly, "validate_final_row_count_vs_counter")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_trade_area_monopoly.export_result = mock_export_result
        self.feed_trade_area_monopoly.trade_area_ids_in_feed = {1,2,3,4,5,6}

        # record
        self.feed_trade_area_monopoly.get_trade_area_ids_from_trade_area_file()
        self.feed_trade_area_monopoly.find_raw()
        self.feed_trade_area_monopoly.make_final_from_cursor(self.feed_trade_area_monopoly.trade_areas)

        # validate that the final file has the same number of rows that we wrote, plus one for the header row
        self.feed_trade_area_monopoly.get_final_row_count()
        self.feed_trade_area_monopoly.validate_final_row_count_vs_counter(1)

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_trade_area_monopoly.run()

        expected_result = {
            "final_file": self.feed_trade_area_monopoly.final_file,
            "status": self.feed_trade_area_monopoly.status,
            "row_count_raw": self.feed_trade_area_monopoly.row_count_raw,
            "row_count_final": self.feed_trade_area_monopoly.row_count_final,
            "counter": self.feed_trade_area_monopoly.counter,
            "num_monopolies_linked_to_missing_trade_area": self.feed_trade_area_monopoly.num_monopolies_linked_to_missing_trade_area,
            "monopolies_linked_to_missing_trade_area_report": self.feed_trade_area_monopoly.monopolies_linked_to_missing_trade_area_report,
            "duration": self.feed_trade_area_monopoly.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_trade_area_monopoly.trade_area_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}

        start_date = datetime.datetime.utcnow()
        end_date = datetime.datetime.utcnow()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "monopolies": [
                    {
                        "monopoly_type": u"AbsoluteMonopoly",
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    {
                        "monopoly_type": u"SinglePlayerMonopoly",
                        "start_date": start_date,
                        "end_date": end_date
                    }
                ]
            },
            "meta": {
                "created_at": created_date,
                "updated_at": modified_date
            }
        }
        expected_clean_rows = [
            [
                u"51b7b891784d6565bb3cd3d9",    # trade_area_id
                u"A",                           # monopoly_type
                date_YYYY_MM_DD(start_date),    # start_date
                date_YYYY_MM_DD(end_date),      # end_date
                date_YYYY_MM_DD(created_date),  # created_at
                date_YYYY_MM_DD(modified_date)  # modified_at
            ],
            [
                u"51b7b891784d6565bb3cd3d9",   # trade_area_id
                u"S",                           # monopoly_type
                date_YYYY_MM_DD(start_date),    # start_date
                date_YYYY_MM_DD(end_date),      # end_date
                date_YYYY_MM_DD(created_date),  # created_at
                date_YYYY_MM_DD(modified_date)  # modified_at
            ]
        ]

        self.feed_trade_area_monopoly._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
