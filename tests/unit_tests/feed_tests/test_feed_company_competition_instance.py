from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.analytics.feed_company_competition_instance import FeedCompanyCompetitionInstance
from StringIO import StringIO
from bson import ObjectId
import __builtin__
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedCompanyCompetitionInstanceTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedCompanyCompetitionInstanceTests, self).setUp()
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
        self.feed_cci = FeedCompanyCompetitionInstance(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_cci, "get_company_ids_from_company_file")
        self.mox.StubOutWithMock(self.feed_cci, "get_invalid_companies_for_dataset")
        self.mox.StubOutWithMock(self.feed_cci, "get_cci_id_splits_from_db")
        self.mox.StubOutWithMock(self.feed_cci, "write_chunk")
        self.mox.StubOutWithMock(self.feed_cci, "find_raw")
        self.mox.StubOutWithMock(self.feed_cci, "make_final_from_cursor")
        self.mox.StubOutWithMock(self.feed_cci, "write_header_to_final")
        self.mox.StubOutWithMock(self.feed_cci, "merge_and_purge_chunks")
        self.mox.StubOutWithMock(self.feed_cci, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_cci, "validate_final_row_count_within_tolerance")
        self.mox.StubOutWithMock(self.feed_cci.mp_manager, "add_process")
        self.mox.StubOutWithMock(self.feed_cci.mp_manager, "start_all")
        self.mox.StubOutWithMock(self.feed_cci.mp_manager, "join_all")
        self.mox.StubOutWithMock(self.feed_cci, "check_mp_errors")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_cci.export_result = mock_export_result
        self.feed_cci.company_ids_in_feed = {1,2,3,4,5,6}
        self.feed_cci.num_splits = 2
        self.feed_cci.mp_manager.results = [
            {
                "raw": 17,
                "counter": 8,
                "num_ccis_null_home_company_id": 0,
                "num_ccis_null_away_company_id": 0,
                "num_ccis_linked_to_invalid_home_company": 12,
                "num_ccis_linked_to_non_feed_home_company": 22,
                "num_ccis_linked_to_non_feed_away_company": 33
            },
            {
                "raw": 16,
                "counter": 10,
                "num_ccis_null_home_company_id": 0,
                "num_ccis_null_away_company_id": 0,
                "num_ccis_linked_to_invalid_home_company": 13,
                "num_ccis_linked_to_non_feed_home_company": 22,
                "num_ccis_linked_to_non_feed_away_company": 33
            }
        ]

        # record
        self.feed_cci.get_company_ids_from_company_file()
        self.feed_cci.get_invalid_companies_for_dataset("competition")
        self.feed_cci.get_cci_id_splits_from_db().AndReturn([(1,3),(4,6)])

        final_file = self.feed_cci.final_file + ".00"
        self.feed_cci.mp_manager.add_process(self.feed_cci.write_chunk, (1,3), self.feed_cci.find_raw, self.feed_cci.make_final_from_cursor, final_file)
        final_file = self.feed_cci.final_file + ".01"
        self.feed_cci.mp_manager.add_process(self.feed_cci.write_chunk, (4,6), self.feed_cci.find_raw, self.feed_cci.make_final_from_cursor, final_file)

        # start and join all sub processes
        self.feed_cci.mp_manager.start_all()
        self.feed_cci.mp_manager.join_all()

        self.feed_cci.check_mp_errors(self.feed_cci.__class__.__name__)

        # write the header row to the real final file
        self.feed_cci.write_header_to_final()

        # merge chunks with cat, then remove chunks, oh yeah!
        self.feed_cci.merge_and_purge_chunks()

        self.feed_cci.get_final_row_count()
        self.feed_cci.validate_final_row_count_within_tolerance()

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_cci.run()

        expected_result = {
            "final_file": self.feed_cci.final_file,
            "status": self.feed_cci.status,
            "row_count_raw": self.feed_cci.row_count_raw,
            "row_count_final": self.feed_cci.row_count_final,
            "num_ccis_null_home_company_id": self.feed_cci.num_ccis_null_home_company_id,
            "num_ccis_null_away_company_id": self.feed_cci.num_ccis_null_away_company_id,
            "num_ccis_linked_to_invalid_home_company": self.feed_cci.num_ccis_linked_to_invalid_home_company,
            "num_ccis_linked_to_non_feed_home_company": self.feed_cci.num_ccis_linked_to_non_feed_home_company,
            "num_ccis_linked_to_non_feed_away_company": self.feed_cci.num_ccis_linked_to_non_feed_away_company,
            "ccis_null_home_company_id_report": self.feed_cci.ccis_null_home_company_id_report,
            "ccis_null_away_company_id_report": self.feed_cci.ccis_null_away_company_id_report,
            "ccis_linked_to_invalid_home_company_report": self.feed_cci.ccis_linked_to_invalid_home_company_report,
            "ccis_linked_to_non_feed_home_company_report": self.feed_cci.ccis_linked_to_non_feed_home_company_report,
            "ccis_linked_to_non_feed_away_company_report": self.feed_cci.ccis_linked_to_non_feed_away_company_report,
            "duration": self.feed_cci.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_cci.company_ids_in_feed = {u"519b15df784d650a6f8ddf32", u"519b193b1d26be3eb461bdc0"}

        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "pair": {
                    "entity_id_from": u"519b15df784d650a6f8ddf32",
                    "entity_id_to": u"519b193b1d26be3eb461bdc0",
                    "data": {
                        "competition_strength": 42.123123
                    }
                }
            },
            "meta": {
                "created_at": created_date,
                "updated_at": modified_date
            }
        }
        expected_clean_rows = [[
            u"51b7b891784d6565bb3cd3d9",        # company_competition_instance_id
            u"519b15df784d650a6f8ddf32",        # home_company_id
            u"519b193b1d26be3eb461bdc0",        # away_company_id
            u"42.123",                          # weight
            date_YYYY_MM_DD(created_date),      # created_at
            date_YYYY_MM_DD(modified_date)      # modified_at
        ]]

        self.feed_cci._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)

    def test_write_clean_row__invalid_competition(self):
        """
        This tests that companies invalid for the competition dataset will not have the invalid CCI data in the feed.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_cci.company_ids_in_feed = {u"519b15df784d650a6f8ddf32", u"519b193b1d26be3eb461bdc0"}
        self.feed_cci.invalid_companies_competition = {u"519b15df784d650a6f8ddf32"}

        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "pair": {
                    "entity_id_from": u"519b15df784d650a6f8ddf32",
                    "entity_id_to": u"519b193b1d26be3eb461bdc0",
                    "data": {
                        "competition_strength": 42.123123
                    }
                }
            },
            "meta": {
                "created_at": created_date,
                "updated_at": modified_date
            }
        }

        # we'll get nothing, and like it!
        expected_clean_rows = []

        # stub out the call to write the invalid report
        self.mox.StubOutWithMock(__builtin__, 'open')

        mock_report = MockFile("invalid_companies")
        open(self.feed_cci.ccis_linked_to_invalid_home_company_report, "wb").AndReturn(mock_report)

        # replay
        self.mox.ReplayAll()

        self.feed_cci._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)
        self.assertEqual(mock_report.contents.getvalue(), "51b7b891784d6565bb3cd3d9,519b15df784d650a6f8ddf32\n")

    def __mock_write_row(self, values):
        self.row_values.append(values)


class MockFile(object):

    def __init__(self, name):
        self.name = name
        self.contents = StringIO("")

    def write(self, content):
        self.contents.write(content)

    def __enter__(self):
        return self

    def __exit__(self, *excinfo):
        pass

if __name__ == '__main__':
    unittest.main()
