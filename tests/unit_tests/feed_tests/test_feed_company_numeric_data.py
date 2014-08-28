import random
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from common.utilities.time_series import get_monthly_time_series
from feed.helpers.feed_helper import date_YYYY_MM_DD
from feed.tables.analytics.feed_company_numeric_data import FeedCompanyNumericData
from bson import ObjectId
import datetime
import mox
import unittest

__author__ = 'jsternberg'

class FeedCompanyNumericDataTests(mox.MoxTestBase):

    def setUp(self):
        super(FeedCompanyNumericDataTests, self).setUp()
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
        self.feed_company_numeric_data = FeedCompanyNumericData(mock_config, mock_logger)
        self.row_values = []


    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()


    def test_run(self):
        """
        Verify it calls the right funcs, yo
        """

        self.mox.StubOutWithMock(self.feed_company_numeric_data, "get_invalid_companies_for_dataset")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "get_company_ids_from_company_file")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "write_chunk")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "find_raw")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "make_final_from_cursor")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "write_header_to_final")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "merge_and_purge_chunks")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "get_final_row_count")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "validate_final_row_count_vs_counter")
        self.mox.StubOutWithMock(self.feed_company_numeric_data.mp_manager, "add_process")
        self.mox.StubOutWithMock(self.feed_company_numeric_data.mp_manager, "start_all")
        self.mox.StubOutWithMock(self.feed_company_numeric_data.mp_manager, "join_all")
        self.mox.StubOutWithMock(self.feed_company_numeric_data, "check_mp_errors")

        mock_export_result = self.mox.CreateMockAnything()
        mock_export_result.succeeded = True
        self.feed_company_numeric_data.export_result = mock_export_result
        self.feed_company_numeric_data.company_ids_in_feed = {1,2,3,4,5,6}
        self.feed_company_numeric_data.num_splits = 2
        self.feed_company_numeric_data.mp_manager.results = [
            {
                "raw": 17,
                "counter": 8
            },
            {
                "raw": 16,
                "counter": 10
            }
        ]

        # record
        self.feed_company_numeric_data.get_invalid_companies_for_dataset("stores")
        self.feed_company_numeric_data.get_invalid_companies_for_dataset("demographics")
        self.feed_company_numeric_data.get_invalid_companies_for_dataset("competition")
        self.feed_company_numeric_data.get_invalid_companies_for_dataset("economics")
        self.feed_company_numeric_data.get_company_ids_from_company_file()

        final_file = self.feed_company_numeric_data.final_file + ".00"
        self.feed_company_numeric_data.mp_manager.add_process(self.feed_company_numeric_data.write_chunk, (1,3), self.feed_company_numeric_data.find_raw, self.feed_company_numeric_data.make_final_from_cursor, final_file)
        final_file = self.feed_company_numeric_data.final_file + ".01"
        self.feed_company_numeric_data.mp_manager.add_process(self.feed_company_numeric_data.write_chunk, (4,6), self.feed_company_numeric_data.find_raw, self.feed_company_numeric_data.make_final_from_cursor, final_file)

        # start and join all sub processes
        self.feed_company_numeric_data.mp_manager.start_all()
        self.feed_company_numeric_data.mp_manager.join_all()

        self.feed_company_numeric_data.check_mp_errors(self.feed_company_numeric_data.__class__.__name__)

        # write the header row to the real final file
        self.feed_company_numeric_data.write_header_to_final()

        # merge chunks with cat, then remove chunks, oh yeah!
        self.feed_company_numeric_data.merge_and_purge_chunks()

        self.feed_company_numeric_data.get_final_row_count()
        self.feed_company_numeric_data.validate_final_row_count_vs_counter(19)

        # replay
        self.mox.ReplayAll()

        # test
        result = self.feed_company_numeric_data.run()

        expected_result = {
            "final_file": self.feed_company_numeric_data.final_file,
            "status": self.feed_company_numeric_data.status,
            "row_count_raw": self.feed_company_numeric_data.row_count_raw,
            "row_count_final": self.feed_company_numeric_data.row_count_final,
            "counter": self.feed_company_numeric_data.counter,
            "duration": self.feed_company_numeric_data.duration
        }

        self.assertEqual(result, expected_result)

    def test_write_clean_row__basic(self):
        """
        The most important function in the class. This tests the base case -- good / expected data.
        Note this does NOT test all data items.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_numeric_data.company_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()
        created_date_short = date_YYYY_MM_DD(created_date)
        modified_date_short = date_YYYY_MM_DD(modified_date)

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "analytics": {
                    "stores": {
                        "monthly": {
                            "store_counts": [
                                {"date": m, "value": random.random() * 1000}
                                for m in months
                            ]
                        }
                    },
                    "demographics": {
                        "monthly": {
                            "DistanceMiles10": {
                                "aggregate_trade_area_population": {
                                    "mean": [
                                            {
                                            "target_year": 2011,
                                            "series": [
                                                {"date": m, "value": random.random() * 1000}
                                                for m in months
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "primary": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "secondary": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "cluster": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ]
                                }
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
        expected_clean_rows = [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10026",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["stores"]["monthly"]["store_counts"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10031",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["mean"][0]["series"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10044",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["total"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10045",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["primary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10046",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["secondary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10047",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["cluster"]
        ]

        self.feed_company_numeric_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)

    def test_write_clean_row__invalid_companies_stores(self):
        """
        This tests that companies invalid for the stores dataset will not have the invalid data items in the feed.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_numeric_data.company_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}
        self.feed_company_numeric_data.invalid_companies_stores = {u"51b7b891784d6565bb3cd3d9"}


        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()
        created_date_short = date_YYYY_MM_DD(created_date)
        modified_date_short = date_YYYY_MM_DD(modified_date)

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "analytics": {
                    "stores": {
                        "monthly": {
                            "store_counts": [
                                {"date": m, "value": random.random() * 1000}
                                for m in months
                            ]
                        }
                    },
                    "demographics": {
                        "monthly": {
                            "DistanceMiles10": {
                                "aggregate_trade_area_population": {
                                    "mean": [
                                            {
                                            "target_year": 2011,
                                            "series": [
                                                {"date": m, "value": random.random() * 1000}
                                                for m in months
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "primary": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "secondary": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "cluster": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ]
                                }
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
        expected_clean_rows = [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10031",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["mean"][0]["series"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10044",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["total"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10045",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["primary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10046",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["secondary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10047",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["cluster"]
        ]

        self.feed_company_numeric_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)

    def test_write_clean_row__invalid_companies_demographics(self):
        """
        This tests that companies invalid for the demographics dataset will not have the invalid data items in the feed.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_numeric_data.company_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}
        self.feed_company_numeric_data.invalid_companies_demographics = {u"51b7b891784d6565bb3cd3d9"}


        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()
        created_date_short = date_YYYY_MM_DD(created_date)
        modified_date_short = date_YYYY_MM_DD(modified_date)

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "analytics": {
                    "stores": {
                        "monthly": {
                            "store_counts": [
                                {"date": m, "value": random.random() * 1000}
                                for m in months
                            ]
                        }
                    },
                    "demographics": {
                        "monthly": {
                            "DistanceMiles10": {
                                "aggregate_trade_area_population": {
                                    "mean": [
                                            {
                                            "target_year": 2011,
                                            "series": [
                                                {"date": m, "value": random.random() * 1000}
                                                for m in months
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "primary": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "secondary": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "cluster": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ]
                                }
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
        expected_clean_rows = [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10026",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["stores"]["monthly"]["store_counts"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10044",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["total"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10045",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["primary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10046",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["secondary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10047",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["competitive_company_counts"]["cluster"]
        ]

        self.feed_company_numeric_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def test_write_clean_row__invalid_companies_competition(self):
        """
        This tests that companies invalid for the competition dataset will not have the invalid data items in the feed.
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_numeric_data.company_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}
        self.feed_company_numeric_data.invalid_companies_competition = {u"51b7b891784d6565bb3cd3d9"}


        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()
        created_date_short = date_YYYY_MM_DD(created_date)
        modified_date_short = date_YYYY_MM_DD(modified_date)

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "analytics": {
                    "stores": {
                        "monthly": {
                            "store_counts": [
                                {"date": m, "value": random.random() * 1000}
                                for m in months
                            ]
                        }
                    },
                    "demographics": {
                        "monthly": {
                            "DistanceMiles10": {
                                "aggregate_trade_area_population": {
                                    "mean": [
                                            {
                                            "target_year": 2011,
                                            "series": [
                                                {"date": m, "value": random.random() * 1000}
                                                for m in months
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "competitive_company_counts": {
                                    "total": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "primary": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "secondary": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ],
                                    "cluster": [
                                        {"date": m, "value": random.random() * 1000}
                                        for m in months
                                    ]
                                }
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
        expected_clean_rows = [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10026",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["stores"]["monthly"]["store_counts"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10031",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["mean"][0]["series"]
        ]

        self.feed_company_numeric_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def test_write_clean_row__distinct_stores_affected(self):
        """
        This tests a few newer competition items added to the company numeric table
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_numeric_data.company_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}

        months = get_monthly_time_series()
        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()
        created_date_short = date_YYYY_MM_DD(created_date)
        modified_date_short = date_YYYY_MM_DD(modified_date)

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
                "analytics": {
                    "competition": {
                        "monthly": {
                            "DistanceMiles10": {
                                "aggregate_distinct_stores_affected": {
                                    "counts":
                                        {
                                        "total": [
                                            {"date": m, "value": int(random.random() * 1000)}
                                            for m in months
                                        ],
                                        "primary": [
                                            {"date": m, "value": int(random.random() * 1000)}
                                            for m in months
                                        ],
                                        "secondary": [
                                            {"date": m, "value": int(random.random() * 1000)}
                                            for m in months
                                        ],
                                        "cluster": [
                                            {"date": m, "value": int(random.random() * 1000)}
                                            for m in months
                                        ]
                                    },
                                    "percents":
                                        {
                                        "total": [
                                            {"date": m, "value": random.random() * 1000}
                                            for m in months
                                        ],
                                        "primary": [
                                            {"date": m, "value": random.random() * 1000}
                                            for m in months
                                        ],
                                        "secondary": [
                                            {"date": m, "value": random.random() * 1000}
                                            for m in months
                                        ],
                                        "cluster": [
                                            {"date": m, "value": random.random() * 1000}
                                            for m in months
                                        ]
                                    }
                                }
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
        expected_clean_rows = [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10084",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_distinct_stores_affected"]["counts"]["total"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10085",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_distinct_stores_affected"]["counts"]["primary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10086",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_distinct_stores_affected"]["counts"]["secondary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10087",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_distinct_stores_affected"]["counts"]["cluster"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10088",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_distinct_stores_affected"]["percents"]["total"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10089",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_distinct_stores_affected"]["percents"]["primary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10090",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_distinct_stores_affected"]["percents"]["secondary"]
        ] + [
            [
                u"51b7b891784d6565bb3cd3d9",        # company_id
                u"10091",                           # data_item_id
                u"M",                               # period_type
                row["date"].isoformat()[:10],       # date
                str(round(row["value"], 6)),        # value
                created_date_short,                 # created_at
                modified_date_short                 # modified_at
            ] for row in test_row["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["aggregate_distinct_stores_affected"]["percents"]["cluster"]
        ]

        self.feed_company_numeric_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)


    def test_write_clean_row__empty_analytics(self):
        """
        This tests the case where the company doesn't have analytics
        """

        mock_writer = self.mox.CreateMockAnything()
        mock_writer.writerow = self.__mock_write_row

        self.feed_company_numeric_data.company_ids_in_feed = {u"51b7b891784d6565bb3cd3d9"}

        created_date = datetime.datetime.utcnow()
        modified_date = datetime.datetime.utcnow()

        test_row = {
            "_id": ObjectId(u"51b7b891784d6565bb3cd3d9"),
            "data": {
            },
            "meta": {
                "created_at": created_date,
                "updated_at": modified_date
            }
        }
        expected_clean_rows = []

        self.feed_company_numeric_data._write_clean_row(mock_writer, test_row)

        self.assertEqual(self.row_values, expected_clean_rows)

    def __mock_write_row(self, values):
        self.row_values.append(values)


if __name__ == '__main__':
    unittest.main()
