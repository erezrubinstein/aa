from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.analytics.feed_trade_area_competition_instance import FeedTradeAreaCompetitionInstance
from bson import ObjectId
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedTradeAreaCompetitionInstanceTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedTradeAreaCompetitionInstanceTests, self).setUp()
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
        self.feed_taci = FeedTradeAreaCompetitionInstance(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_taci, "get_company_ids_from_company_file")
        self.mox.StubOutWithMock(self.feed_taci, "get_store_ids_from_store_file")
        self.mox.StubOutWithMock(self.feed_taci, "write_chunk")
        self.mox.StubOutWithMock(self.feed_taci, "get_trade_area_ids_from_trade_area_file")
        self.mox.StubOutWithMock(self.feed_taci, "find_raw")
        self.mox.StubOutWithMock(self.feed_taci, "make_final_from_cursor")
        self.mox.StubOutWithMock(self.feed_taci, "write_header_to_final")
        self.mox.StubOutWithMock(self.feed_taci, "merge_and_purge_chunks")
        self.mox.StubOutWithMock(self.feed_taci, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_taci, "validate_final_row_count_vs_counter")
        self.mox.StubOutWithMock(self.feed_taci.mp_manager, "add_process")
        self.mox.StubOutWithMock(self.feed_taci.mp_manager, "start_all")
        self.mox.StubOutWithMock(self.feed_taci.mp_manager, "join_all")
        self.mox.StubOutWithMock(self.feed_taci, "check_mp_errors")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_taci.export_result = mock_export_result
        self.feed_taci.trade_area_ids_in_feed = {1,2,3,4,5,6}
        self.feed_taci.num_splits = 2
        self.feed_taci.mp_manager.results = [{
                "raw": 17,
                "counter": 8,
                "num_tacis_null_company_id": 0,
                "num_tacis_null_store_id": 0,
                "num_tacis_linked_to_non_feed_company": 22,
                "num_tacis_linked_to_missing_store": 33,
                "num_tacis_linked_to_missing_trade_area": 44
            },
            {
                "raw": 16,
                "counter": 10,
                "num_tacis_null_company_id": 0,
                "num_tacis_null_store_id": 0,
                "num_tacis_linked_to_non_feed_company": 22,
                "num_tacis_linked_to_missing_store": 33,
                "num_tacis_linked_to_missing_trade_area": 44
            }]

        # record
        self.feed_taci.get_company_ids_from_company_file()
        self.feed_taci.get_store_ids_from_store_file()
        self.feed_taci.get_trade_area_ids_from_trade_area_file()

        final_file = self.feed_taci.final_file + ".00"
        self.feed_taci.mp_manager.add_process(self.feed_taci.write_chunk, (1,3), self.feed_taci.find_raw, self.feed_taci.make_final_from_cursor, final_file)
        final_file = self.feed_taci.final_file + ".01"
        self.feed_taci.mp_manager.add_process(self.feed_taci.write_chunk, (4,6), self.feed_taci.find_raw, self.feed_taci.make_final_from_cursor, final_file)

        # start and join all sub processes
        self.feed_taci.mp_manager.start_all()
        self.feed_taci.mp_manager.join_all()

        self.feed_taci.check_mp_errors(self.feed_taci.__class__.__name__)

        # write the header row to the real final file
        self.feed_taci.write_header_to_final()

        # merge chunks with cat, then remove chunks, oh yeah!
        self.feed_taci.merge_and_purge_chunks()

        # validate that the final file has the same number of rows that we wrote, plus one for the header row
        self.feed_taci.get_final_row_count()
        self.feed_taci.validate_final_row_count_vs_counter(19)

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_taci.run()

        expected_result = {
            "final_file": self.feed_taci.final_file,
            "status": self.feed_taci.status,
            "row_count_raw": self.feed_taci.row_count_raw,
            "row_count_final": self.feed_taci.row_count_final,
            "counter": self.feed_taci.counter,
            "num_tacis_null_company_id": self.feed_taci.num_tacis_null_company_id,
            "num_tacis_null_store_id": self.feed_taci.num_tacis_null_store_id,
            "num_tacis_linked_to_non_feed_company": self.feed_taci.num_tacis_linked_to_non_feed_company,
            "num_tacis_linked_to_missing_store": self.feed_taci.num_tacis_linked_to_missing_store,
            "num_tacis_linked_to_missing_trade_area": self.feed_taci.num_tacis_linked_to_missing_trade_area,
            "tacis_null_company_id_report": self.feed_taci.tacis_null_company_id_report,
            "tacis_null_store_id_report": self.feed_taci.tacis_null_store_id_report,
            "tacis_linked_to_non_feed_company_report": self.feed_taci.tacis_linked_to_non_feed_company_report,
            "tacis_linked_to_missing_store_report": self.feed_taci.tacis_linked_to_missing_store_report,
            "tacis_linked_to_missing_trade_area_report": self.feed_taci.tacis_linked_to_missing_trade_area_report,
            "duration": self.feed_taci.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_taci.company_ids_in_feed = {u"519b15df784d650a6f8ddf32", u"51c66de05892d07c2eaf7e86"}
        self.feed_taci.store_ids_in_feed = {u"519b193b1d26be3eb461bdc0", u"51b767b1784d656be5d3364a"}
        self.feed_taci.trade_area_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}

        start_date = datetime.datetime.utcnow()
        end_date = datetime.datetime.utcnow()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "competitive_stores": [
                    {
                        "away_company_id": u"519b15df784d650a6f8ddf32",
                        "away_store_id": u"519b193b1d26be3eb461bdc0",
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    {
                        "away_company_id": u"51c66de05892d07c2eaf7e86",
                        "away_store_id": u"51b767b1784d656be5d3364a",
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
                u"519b15df784d650a6f8ddf32",    # company_id
                u"519b193b1d26be3eb461bdc0",    # store_id
                date_YYYY_MM_DD(start_date),    # start_date
                date_YYYY_MM_DD(end_date),      # end_date
                date_YYYY_MM_DD(created_date),  # created_at
                date_YYYY_MM_DD(modified_date)  # modified_at
            ],
            [
                u"51b7b891784d6565bb3cd3d9",   # trade_area_id
                u"51c66de05892d07c2eaf7e86",   # company_id
                u"51b767b1784d656be5d3364a",   # store_id
                date_YYYY_MM_DD(start_date),    # start_date
                date_YYYY_MM_DD(end_date),      # end_date
                date_YYYY_MM_DD(created_date),  # created_at
                date_YYYY_MM_DD(modified_date)  # modified_at
            ]
        ]

        self.feed_taci._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
