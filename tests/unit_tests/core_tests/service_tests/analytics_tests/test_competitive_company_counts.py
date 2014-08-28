from common.utilities.date_utilities import FastDateParser
from core.service.svc_analytics.implementation.calc.engines.competition.competitive_company_counts \
    import CompetitiveCompanyCounts
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
import unittest
import mox
import datetime
from core.service.svc_analytics.implementation.calc.engines.competition.trade_area_competitive_stores import CompStore
from tests.unit_tests.core_tests.data_stub_helpers import create_mock_taci


__author__ = 'vgold'


class CompetitiveCompanyCountsTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(CompetitiveCompanyCountsTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.maxDiff = None

    def doCleanups(self):

        super(CompetitiveCompanyCountsTests, self).doCleanups()
        dependencies.clear()

    def test_calculate_retail_segment(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        trade_area_id2 = generate_id()
        store_id02 = generate_id()

        company_id = generate_id()
        company_idx = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()
        competitor_id3 = generate_id()
        competitor_id4 = generate_id()

        cci_id0 = generate_id()
        cci_id1 = generate_id()
        cci_id2 = generate_id()
        cci_id3 = generate_id()
        cci_id4 = generate_id()

        store_id1 = generate_id()
        store_id2 = generate_id()
        store_id3 = generate_id()
        store_id4 = generate_id()
        store_idx = generate_id()

        # Make an instance without pesky __init__
        calc_engine = CompetitiveCompanyCounts.__new__(CompetitiveCompanyCounts)
        calc_engine.date_parser = FastDateParser()

        # Set instance variables
        calc_engine.parent_to_children_dict = None

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [[trade_area_id1], [trade_area_id2]]

        mock_tacis = [
            create_mock_taci(
                company_id,
                "",
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 0.8),
                    CompStore(company_id, store_id02, 1.0),
                    CompStore(company_idx, store_idx, 1.0)
                ]
            ),
            create_mock_taci(
                company_id,
                "",
                str(datetime.datetime(2013, 5, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5),
                    CompStore(competitor_id2, store_id2, 0.8)
                ]
            ),
            create_mock_taci(
                company_id,
                "",
                str(datetime.datetime(2013, 5, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5),
                    CompStore(competitor_id3, store_id3, 1.0)
                ]
            ),
            create_mock_taci(
                company_id,
                "",
                str(datetime.datetime(2013, 4, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5)
                ]
            ),
            create_mock_taci(
                company_id,
                "",
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 0.8),
                    CompStore(competitor_id4, store_id4, 0.35)
                ]
            )
        ]
        calc_engine.child_to_parent_dict = None

        calc_engine.company_pair_dict = {
            company_id: {
                company_id: cci_id0,
                competitor_id1: cci_id1,
                competitor_id2: cci_id2,
                competitor_id3: cci_id3,
                competitor_id4: cci_id4
            }
        }

        calc_engine.run_params = {
            "target_entity_ids": [company_id],
            "tacis": mock_tacis
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            company_id: {
                "total": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 3
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 3
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 1
                    }
                ],
                "primary": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 0
                    }
                ],
                "secondary": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 1
                    }
                ],
                "cluster": [
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 0
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 0
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)

    def test_calculate_retail_parent(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        trade_area_id3 = generate_id()
        store_id02 = generate_id()

        parent_id = generate_id()
        company_id1 = generate_id()
        company_id2 = generate_id()
        company_idx = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()
        competitor_id3 = generate_id()
        competitor_id4 = generate_id()

        cci_id101 = generate_id()
        cci_id102 = generate_id()
        cci_id11 = generate_id()
        cci_id12 = generate_id()
        cci_id13 = generate_id()
        cci_id14 = generate_id()

        cci_id201 = generate_id()
        cci_id202 = generate_id()
        cci_id21 = generate_id()
        cci_id22 = generate_id()
        cci_id23 = generate_id()
        cci_id24 = generate_id()

        store_id1 = generate_id()
        store_id2 = generate_id()
        store_id3 = generate_id()
        store_id4 = generate_id()
        store_idx1 = generate_id()
        store_cluster_id1 = generate_id()
        store_cluster_id2 = generate_id()


        # another family with 3 child banners
        parent_id2 = generate_id()
        company_id_fam2_1 = generate_id()
        company_id_fam2_2 = generate_id()
        company_id_fam2_3 = generate_id()

        cci_id_fam2_11 = generate_id()
        cci_id_fam2_22 = generate_id()
        cci_id_fam2_33 = generate_id()
        cci_id_fam2_12 = generate_id()
        cci_id_fam2_13 = generate_id()
        cci_id_fam2_21 = generate_id()
        cci_id_fam2_23 = generate_id()
        cci_id_fam2_31 = generate_id()
        cci_id_fam2_32 = generate_id()

        store_id_fam2_1 = generate_id()
        store_id_fam2_2 = generate_id()
        store_id_fam2_3 = generate_id()

        # Make an instance without pesky __init__
        calc_engine = CompetitiveCompanyCounts.__new__(CompetitiveCompanyCounts)
        calc_engine.date_parser = FastDateParser()

        # Set instance variables
        calc_engine.parent_to_children_dict = {
            parent_id: [company_id1, company_id2]
        }

        # A 1-day timedelta object
        one_day = datetime.timedelta(days=1)

        # Set fetched data
        calc_engine.fetched_data = [[trade_area_id1], [trade_area_id3], [trade_area_id1]]

        # tacis to match the fetched data
        mock_tacis = [
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 0.8),
                    CompStore(company_id1, store_id02, 1.0),
                    CompStore(company_idx, store_idx1, 1.0)
                ]
            ),
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 6, 1) - one_day),
                [
                    CompStore(competitor_id2, store_id2, 0.8),
                    CompStore(competitor_id4, store_id4, 0.35)
                ]
            ),
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 5, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5),
                    CompStore(competitor_id2, store_id2, 0.8)
                ]
            ),
            create_mock_taci(
                company_id2,
                "",
                str(datetime.datetime(2013, 5, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5),
                    CompStore(competitor_id3, store_id3, 1.0)
                ]
            ),
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 4, 1) - one_day),
                [
                    CompStore(competitor_id1, store_id1, 0.5)
                ]
            ),
            # typical clustering situation for families:
            # banner 1 and banner 2 both cluster, and banner 1 also competes with banner 2
            # --> we should get 2 total, 1 primary (assume banners are in the same industry), and 2 cluster
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 9, 1) - one_day),
                [
                    CompStore(company_id1, store_cluster_id1, 1.0)
                ]
            ),
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 9, 1) - one_day),
                [
                    CompStore(company_id2, store_cluster_id2, 1.0)
                ]
            ), create_mock_taci(
                company_id2,
                "",
                str(datetime.datetime(2013, 9, 1) - one_day),
                [
                    CompStore(company_id2, store_cluster_id2, 1.0)
                ]
            ),
            # typical primary competition situation for families:
            # banner 1 and banner 2 both cluster, and banner 1 also competes with banner 2, and banner 2 competes with banner 1
            # --> we should get 2 total, 2 primary (assume banners are in the same industry), and 2 cluster
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 10, 1) - one_day),
                [
                    CompStore(company_id1, store_cluster_id1, 1.0)
                ]
            ),
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 10, 1) - one_day),
                [
                    CompStore(company_id2, store_cluster_id2, 1.0)
                ]
            ), create_mock_taci(
                company_id2,
                "",
                str(datetime.datetime(2013, 10, 1) - one_day),
                [
                    CompStore(company_id2, store_cluster_id2, 1.0)
                ]
            ), create_mock_taci(
                company_id2,
                "",
                str(datetime.datetime(2013, 10, 1) - one_day),
                [
                    CompStore(company_id1, store_cluster_id1, 1.0)
                ]
            ),
            # another competition situation for families:
            # banner 1 and banner 2 both cluster, and banner 1 also competes with banner 2, and banner 2 competes with banner 1
            # but weight from 1 to 2 and 2 to 1 is < 0.7, so not primary
            # --> we should get 2 total, 2 secondary, and 2 cluster
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 11, 1) - one_day),
                [
                    CompStore(company_id1, store_cluster_id1, 1.0)
                ]
            ),
            create_mock_taci(
                company_id1,
                "",
                str(datetime.datetime(2013, 11, 1) - one_day),
                [
                    CompStore(company_id2, store_cluster_id2, 0.5)
                ]
            ), create_mock_taci(
                company_id2,
                "",
                str(datetime.datetime(2013, 11, 1) - one_day),
                [
                    CompStore(company_id2, store_cluster_id2, 1.0)
                ]
            ), create_mock_taci(
                company_id2,
                "",
                str(datetime.datetime(2013, 11, 1) - one_day),
                [
                    CompStore(company_id1, store_cluster_id1, 0.5)
                ]
            ),
            # another competition situation for families:
            # 3 banners, all compete with each other and themselves with 1.0 weight
            # --> we should get 3 total, 3 primary, and 3 cluster
            create_mock_taci(
                company_id_fam2_1,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_1, store_id_fam2_1, 1.0)
                ]
            ),
            create_mock_taci(
                company_id_fam2_2,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_2, store_id_fam2_2, 1.0)
                ]
            ),
            create_mock_taci(
                company_id_fam2_3,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_3, store_id_fam2_3, 1.0)
                ]
            ),
            create_mock_taci(
                company_id_fam2_1,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_2, store_id_fam2_2, 1.0)
                ]
            ),
            create_mock_taci(
                company_id_fam2_1,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_3, store_id_fam2_3, 1.0)
                ]
            ),
            create_mock_taci(
                company_id_fam2_2,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_1, store_id_fam2_1, 1.0)
                ]
            ),
            create_mock_taci(
                company_id_fam2_2,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_3, store_id_fam2_3, 1.0)
                ]
            ),
            create_mock_taci(
                company_id_fam2_3,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_1, store_id_fam2_1, 1.0)
                ]
            ),
            create_mock_taci(
                company_id_fam2_3,
                "",
                str(datetime.datetime(2013, 12, 1) - one_day),
                [
                    CompStore(company_id_fam2_2, store_id_fam2_2, 1.0)
                ]
            )
        ]

        calc_engine.run_params = {
            "target_entity_ids": [parent_id, parent_id2],
            "tacis": mock_tacis,
            "child_to_parent_dict": {
                company_id1: parent_id,
                company_id2: parent_id,
                company_id_fam2_1: parent_id2,
                company_id_fam2_2: parent_id2,
                company_id_fam2_3: parent_id2
            }
        }

        calc_engine.company_pair_dict = {
            company_id1: {
                company_id1: cci_id101,
                company_id2: cci_id102,
                competitor_id1: cci_id11,
                competitor_id2: cci_id12,
                competitor_id3: cci_id13,
                competitor_id4: cci_id14
            },
            company_id2: {
                company_id1: cci_id201,
                company_id2: cci_id202,
                competitor_id1: cci_id21,
                competitor_id2: cci_id22,
                competitor_id3: cci_id23,
                competitor_id4: cci_id24
            },
            company_id_fam2_1: {
                company_id_fam2_1: cci_id_fam2_11,
                company_id_fam2_2: cci_id_fam2_12,
                company_id_fam2_3: cci_id_fam2_13,
            },
            company_id_fam2_2: {
                company_id_fam2_1: cci_id_fam2_21,
                company_id_fam2_2: cci_id_fam2_22,
                company_id_fam2_3: cci_id_fam2_23,
            },
            company_id_fam2_3: {
                company_id_fam2_1: cci_id_fam2_31,
                company_id_fam2_2: cci_id_fam2_32,
                company_id_fam2_3: cci_id_fam2_33,
            }
        }

        # Do maths
        calc_engine._calculate()

        expected_result = {
            parent_id: {
                "total": [
                    {
                        'date': datetime.datetime(2013, 11, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 10, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 9, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 3
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 3
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 1
                    }
                ],
                "primary": [
                    {
                        'date': datetime.datetime(2013, 11, 1) - one_day,
                        'value': 0
                    },
                    {
                        'date': datetime.datetime(2013, 10, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 9, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 0
                    }
                ],
                "secondary": [
                    {
                        'date': datetime.datetime(2013, 11, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 10, 1) - one_day,
                        'value': 0
                    },
                    {
                        'date': datetime.datetime(2013, 9, 1) - one_day,
                        'value': 0
                    },
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 1
                    }
                ],
                "cluster": [
                    {
                        'date': datetime.datetime(2013, 11, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 10, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 9, 1) - one_day,
                        'value': 2
                    },
                    {
                        'date': datetime.datetime(2013, 6, 1) - one_day,
                        'value': 1
                    },
                    {
                        'date': datetime.datetime(2013, 5, 1) - one_day,
                        'value': 0
                    },
                    {
                        'date': datetime.datetime(2013, 4, 1) - one_day,
                        'value': 0
                    }
                ]
            },
            parent_id2: {
                "total": [
                    {
                        'date': datetime.datetime(2013, 12, 1) - one_day,
                        'value': 3
                    }
                ],
                "primary": [
                    {
                        'date': datetime.datetime(2013, 12, 1) - one_day,
                        'value': 3
                    }
                ],
                "secondary": [
                    {
                        'date': datetime.datetime(2013, 12, 1) - one_day,
                        'value': 0
                    }
                ],
                "cluster": [
                    {
                        'date': datetime.datetime(2013, 12, 1) - one_day,
                        'value': 3
                    }
                ]
            }
        }

        # Steam Punk
        self.assertDictEqual(calc_engine.results, expected_result)


if __name__ == '__main__':
    unittest.main()