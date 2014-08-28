from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from common.utilities.time_series import get_monthly_time_series
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.analytics.feed_trade_area_numeric_data import FeedTradeAreaNumericData
from bson import ObjectId
import datetime
import random
import mox
import unittest

__author__ = 'jsternberg'

class FeedTradeAreaNumericDataTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedTradeAreaNumericDataTests, self).setUp()
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
        self.feed_ta_data = FeedTradeAreaNumericData(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_ta_data, "get_invalid_companies_for_dataset")
        self.mox.StubOutWithMock(self.feed_ta_data, "get_trade_area_ids_from_trade_area_file")
        self.mox.StubOutWithMock(self.feed_ta_data, "write_chunk")
        self.mox.StubOutWithMock(self.feed_ta_data, "find_raw")
        self.mox.StubOutWithMock(self.feed_ta_data, "make_final_from_cursor")
        self.mox.StubOutWithMock(self.feed_ta_data, "write_header_to_final")
        self.mox.StubOutWithMock(self.feed_ta_data, "merge_and_purge_chunks")
        self.mox.StubOutWithMock(self.feed_ta_data, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_ta_data, "validate_final_row_count_vs_counter")
        self.mox.StubOutWithMock(self.feed_ta_data.mp_manager, "add_process")
        self.mox.StubOutWithMock(self.feed_ta_data.mp_manager, "start_all")
        self.mox.StubOutWithMock(self.feed_ta_data.mp_manager, "join_all")
        self.mox.StubOutWithMock(self.feed_ta_data, "check_mp_errors")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_ta_data.export_result = mock_export_result
        self.feed_ta_data.trade_area_ids_in_feed = {1,2,3,4,5,6}
        self.feed_ta_data.num_splits = 2
        self.feed_ta_data.mp_manager.results = [
            {
                "raw": 17,
                "counter": 8,
                "num_trade_areas_not_in_feed": 22
            },
            {
                "raw": 16,
                "counter": 10,
                "num_trade_areas_not_in_feed": 33
            }
        ]

        # record
        self.feed_ta_data.get_invalid_companies_for_dataset("demographics")
        self.feed_ta_data.get_invalid_companies_for_dataset("competition")
        self.feed_ta_data.get_invalid_companies_for_dataset("economics")
        self.feed_ta_data.get_trade_area_ids_from_trade_area_file()
        final_file = self.feed_ta_data.final_file + ".00"
        self.feed_ta_data.mp_manager.add_process(self.feed_ta_data.write_chunk, (1,3), self.feed_ta_data.find_raw, self.feed_ta_data.make_final_from_cursor, final_file)
        final_file = self.feed_ta_data.final_file + ".01"
        self.feed_ta_data.mp_manager.add_process(self.feed_ta_data.write_chunk, (4,6), self.feed_ta_data.find_raw, self.feed_ta_data.make_final_from_cursor, final_file)

        # start and join all sub processes
        self.feed_ta_data.mp_manager.start_all()
        self.feed_ta_data.mp_manager.join_all()

        self.feed_ta_data.check_mp_errors(self.feed_ta_data.__class__.__name__)

        # write the header row to the real final file
        self.feed_ta_data.write_header_to_final()

        # merge chunks with cat, then remove chunks, oh yeah!
        self.feed_ta_data.merge_and_purge_chunks()

        # validate that the final file has the same number of rows that we wrote, plus one for the header row
        self.feed_ta_data.get_final_row_count()
        self.feed_ta_data.validate_final_row_count_vs_counter(19)

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_ta_data.run()

        expected_result = {
            "final_file": self.feed_ta_data.final_file,
            "status": self.feed_ta_data.status,
            "row_count_raw": self.feed_ta_data.row_count_raw,
            "row_count_final": self.feed_ta_data.row_count_final,
            "counter": self.feed_ta_data.counter,
            "num_trade_areas_not_in_feed": self.feed_ta_data.num_trade_areas_not_in_feed,
            "trade_area_ids_not_in_feed_report": self.feed_ta_data.trade_area_ids_not_in_feed_report,
            "duration": self.feed_ta_data.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        Note this does NOT test all data items.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_ta_data.trade_area_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()
        created_date_short = date_YYYY_MM_DD(created_date)
        modified_date_short = date_YYYY_MM_DD(modified_date)

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "company_id": u"519b15df784d650a6f8ddf32",
                "demographics": {
                    "TOTPOP_CY": {
                        "target_year": 2011,
                        "value": random.random() * 10000
                    },
                    "PCI_CY": {
                        "target_year": 2011,
                        "value": random.random() * 1000
                    }
                },
                "analytics": {
                    "competition": {
                        "monthly": {
                            "away_store_counts": {
                                "raw": [
                                    {"date": m, "value": random.random() * 1000}
                                    for m in months
                                ],
                                "weighted": [
                                    {"date": m, "value": random.random() * 1000}
                                    for m in months
                                ]
                            }
                        }
                    }
                }
            },
            "meta": {
                "created_at": created_date,
                "updated_at": modified_date
            }
        }

        # note, the order of these is deterministic!
        expected_clean_rows = [[
                u"51b7b891784d6565bb3cd3d9",                                                # trade_area_id
                u"10002",                                                                   # data_item_id
                u"T",                                                                       # period_type
                u"2011-01-01",                                                              # date
                str(round(test_row["data"]["demographics"]["PCI_CY"]["value"], 6)),         # value
                created_date_short,                                                         # created_at
                modified_date_short                                                         # modified_at
        ], [
                u"51b7b891784d6565bb3cd3d9",                                                # trade_area_id
                u"10001",                                                                   # data_item_id
                u"T",                                                                       # period_type
                u"2011-01-01",                                                              # date
                str(round(test_row["data"]["demographics"]["TOTPOP_CY"]["value"], 6)),      # value
                created_date_short,                                                         # created_at
                modified_date_short                                                         # modified_at
        ]] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # trade_area_id
                u"10014",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["raw"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # trade_area_id
                u"10015",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["weighted"]
        ]

        self.feed_ta_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)

    def test_write_clean_row__invalid_demographics(self):
        """
        This tests that companies invalid for the demographics dataset will not have invalid trade area numeric data
        in the feed.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_ta_data.trade_area_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}
        self.feed_ta_data.invalid_companies_demographics = {u"519b15df784d650a6f8ddf32"}

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()
        created_date_short = date_YYYY_MM_DD(created_date)
        modified_date_short = date_YYYY_MM_DD(modified_date)

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "company_id": u"519b15df784d650a6f8ddf32",
                "demographics": {
                    "TOTPOP_CY": {
                        "target_year": 2011,
                        "value": random.random() * 10000
                    },
                    "PCI_CY": {
                        "target_year": 2011,
                        "value": random.random() * 1000
                    }
                },
                "analytics": {
                    "competition": {
                        "monthly": {
                            "away_store_counts": {
                                "raw": [
                                    {"date": m, "value": random.random() * 1000}
                                    for m in months
                                ],
                                "weighted": [
                                    {"date": m, "value": random.random() * 1000}
                                    for m in months
                                ]
                            }
                        }
                    }
                }
            },
            "meta": {
                "created_at": created_date,
                "updated_at": modified_date
            }
        }

        # note, the order of these is deterministic!
        expected_clean_rows = [
            [
                u"51b7b891784d6565bb3cd3d9",        # trade_area_id
                u"10014",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["raw"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # trade_area_id
                u"10015",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["weighted"]
        ]

        self.feed_ta_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)

    def test_write_clean_row__invalid_competition(self):
        """
        This tests that companies invalid for the competition dataset will not have invalid trade area numeric data
        in the feed.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_ta_data.trade_area_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}
        self.feed_ta_data.invalid_companies_competition = {u"519b15df784d650a6f8ddf32"}

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()
        created_date_short = date_YYYY_MM_DD(created_date)
        modified_date_short = date_YYYY_MM_DD(modified_date)

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "company_id": u"519b15df784d650a6f8ddf32",
                "demographics": {
                    "TOTPOP_CY": {
                        "target_year": 2011,
                        "value": random.random() * 10000
                    },
                    "PCI_CY": {
                        "target_year": 2011,
                        "value": random.random() * 1000
                    }
                },
                "analytics": {
                    "competition": {
                        "monthly": {
                            "away_store_counts": {
                                "raw": [
                                    {"date": m, "value": random.random() * 1000}
                                    for m in months
                                ],
                                "weighted": [
                                    {"date": m, "value": random.random() * 1000}
                                    for m in months
                                ]
                            }
                        }
                    }
                }
            },
            "meta": {
                "created_at": created_date,
                "updated_at": modified_date
            }
        }

        # note, the order of these is deterministic!
        expected_clean_rows = [[
                u"51b7b891784d6565bb3cd3d9",                                                # trade_area_id
                u"10002",                                                                   # data_item_id
                u"T",                                                                       # period_type
                u"2011-01-01",                                                              # date
                str(round(test_row["data"]["demographics"]["PCI_CY"]["value"], 6)),         # value
                created_date_short,                                                         # created_at
                modified_date_short                                                         # modified_at
        ], [
                u"51b7b891784d6565bb3cd3d9",                                                # trade_area_id
                u"10001",                                                                   # data_item_id
                u"T",                                                                       # period_type
                u"2011-01-01",                                                              # date
                str(round(test_row["data"]["demographics"]["TOTPOP_CY"]["value"], 6)),      # value
                created_date_short,                                                         # created_at
                modified_date_short                                                         # modified_at
        ]]

        self.feed_ta_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)



    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
