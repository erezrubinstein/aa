from common.utilities.date_utilities import LAST_ANALYTICS_DATE
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.competition_measures_attribution_data_builder import CompetitionMeasuresAttributionDataBuilder
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.utilities.helpers import generate_id
import unittest
import pprint
import mox


__author__ = 'vgold'


class CompetitionMeasuresAttributionDataBuilderTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(CompetitionMeasuresAttributionDataBuilderTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Create caller context
        self.context = {"user_id": 1, "source": "test_competition_measures_attribution_data_builder.py.py"}

    def doCleanups(self):

        super(CompetitionMeasuresAttributionDataBuilderTests, self).doCleanups()
        dependencies.clear()

    ############################################################
    # CompetitionMeasuresAttributionDataBuilderTests.build_competition_measures_data()

    def test_build_competition_measures_data(self):

        total_scr = 1.0
        primary_scr = 0.8
        median_ta_inc = 1000
        median_ta_pop = 2000
        monop_percent = 2.0

        total_median_comp_scr = 0.7
        primary_median_comp_scr = 0.85
        median_comp_median_ta_inc = 3000
        median_comp_median_ta_pop = 4000
        median_comp_monop_primary_percent = 3.5

        total_leader_comp_scr = 0.75
        primary_leader_comp_scr = 0.95
        leader_comp_median_ta_inc = 5000
        leader_comp_median_ta_pop = 6000
        leader_comp_monop_primary_percent = 2.15

        store_count = 1400
        mean_total_comp_inst_percent = 25.0
        mean_primary_comp_inst_percent = 23.0

        parent_id = generate_id()
        banner_id1 = generate_id()
        banner_id2 = generate_id()

        competitor_id1 = generate_id()
        competitor_id2 = generate_id()

        builder = CompetitionMeasuresAttributionDataBuilder.__new__(CompetitionMeasuresAttributionDataBuilder)

        builder.company = [
            parent_id,

            total_scr,
            primary_scr,
            median_ta_inc,
            median_ta_pop,
            monop_percent,

            total_median_comp_scr,
            primary_median_comp_scr,
            median_comp_median_ta_inc,
            median_comp_median_ta_pop,
            median_comp_monop_primary_percent,

            total_leader_comp_scr,
            primary_leader_comp_scr,
            leader_comp_median_ta_inc,
            leader_comp_median_ta_pop,
            leader_comp_monop_primary_percent,

            store_count,
            mean_total_comp_inst_percent,
            mean_primary_comp_inst_percent
        ]

        banner_1_comp_1_percent = 12.0
        banner_1_comp_1_count = 27
        banner_1_comp_1_away = 25
        banner_1_comp_1_weight = 0.9

        banner_1_comp_2_percent = 6.0
        banner_1_comp_2_count = 36
        banner_1_comp_2_away = 30
        banner_1_comp_2_weight = 0.5

        banner_2_comp_1_percent = 18.0
        banner_2_comp_1_count = 42
        banner_2_comp_1_away = 29
        banner_2_comp_1_weight = 0.9

        banner_2_comp_2_percent = 8.0
        banner_2_comp_2_count = 12
        banner_2_comp_2_away = 12
        banner_2_comp_2_weight = 0.6

        builder.total_ccis = [
            [
                generate_id(),
                competitor_id1,
                "Competitor 1",
                banner_1_comp_1_percent,
                banner_1_comp_1_count,
                banner_1_comp_1_away,
                banner_1_comp_1_weight,
                banner_id1
            ],
            [
                generate_id(),
                competitor_id2,
                "Competitor 2",
                banner_1_comp_2_percent,
                banner_1_comp_2_count,
                banner_1_comp_2_away,
                banner_1_comp_2_weight,
                banner_id1
            ],
            [
                generate_id(),
                competitor_id1,
                "Competitor 1",
                banner_2_comp_1_percent,
                banner_2_comp_1_count,
                banner_2_comp_1_away,
                banner_2_comp_1_weight,
                banner_id2
            ],
            [
                generate_id(),
                competitor_id2,
                "Competitor 2",
                banner_2_comp_2_percent,
                banner_2_comp_2_count,
                banner_2_comp_2_away,
                banner_2_comp_2_weight,
                banner_id2
            ]
        ]

        builder.primary_ccis = [
            [
                generate_id(),
                competitor_id1,
                "Competitor 1",
                banner_1_comp_1_percent,
                banner_1_comp_1_count,
                banner_1_comp_1_away,
                banner_1_comp_1_weight,
                banner_id1
            ],
            [
                generate_id(),
                competitor_id1,
                "Competitor 1",
                banner_2_comp_1_percent,
                banner_2_comp_1_count,
                banner_2_comp_1_away,
                banner_2_comp_1_weight,
                banner_id2
            ]
        ]

        builder.date = LAST_ANALYTICS_DATE

        builder._build_competition_measures_data()

        expected_results = {
            "table": {
                "field_list": [
                    "&nbsp;",
                    "H&rarr;T<br/>Competition<br/>Ratio",
                    "H&rarr;P<br/>Competition<br/>Ratio",
                    "Median Agg Income<br/>/ Competitive<br/>Store",
                    "Median Population<br/>/ Competitive<br/>Store",
                    "Primary<br/>Competitor<br/>Monopolies"
                ],
                "field_meta": {
                    "H&rarr;T<br/>Competition<br/>Ratio": {
                        "type": "number",
                        "decimals": 2
                    },
                    "H&rarr;P<br/>Competition<br/>Ratio": {
                        "type": "number",
                        "decimals": 2
                    },
                    "Median Agg Income<br/>/ Competitive<br/>Store": {
                        "type": "dollars",
                        "decimals": 1,
                        "order": 1000000,
                        "suffix": "M"
                    },
                    "Median Population<br/>/ Competitive<br/>Store": {
                        "type": "number",
                        "decimals": 0
                    },
                    "Primary<br/>Competitor<br/>Monopolies": {
                        "type": "percent",
                        "decimals": 2
                    }
                },
                "results": [
                    [
                        'This Company',
                        total_scr,
                        primary_scr,
                        median_ta_inc,
                        median_ta_pop,
                        monop_percent
                    ],
                    [
                        'Median of Primary Competitors',
                        total_median_comp_scr,
                        primary_median_comp_scr,
                        median_comp_median_ta_inc,
                        median_comp_median_ta_pop,
                        median_comp_monop_primary_percent
                    ],
                    [
                        'Leading Primary Competitor',
                        total_leader_comp_scr,
                        primary_leader_comp_scr,
                        leader_comp_median_ta_inc,
                        leader_comp_median_ta_pop,
                        leader_comp_monop_primary_percent
                    ]
                ]
            },
            "graph": {
                "date": LAST_ANALYTICS_DATE,
                "metrics": [
                    "home_total_competition_ratio",
                    "home_primary_competition_ratio"
                ],
                "data": {
                    "home_store_count": store_count,
                    "home_total_competition_ratio": {
                        "mean": 50.0,
                        "data": [
                            [
                                str(competitor_id1),
                                "Competitor 1",
                                round((banner_1_comp_1_count + banner_2_comp_1_count) / float(banner_1_comp_2_count + banner_2_comp_2_count + banner_1_comp_1_count + banner_2_comp_1_count) * 100.0, 2),
                                banner_1_comp_1_count + banner_2_comp_1_count,
                                banner_1_comp_1_away + banner_2_comp_1_away
                            ],
                            [
                                str(competitor_id2),
                                "Competitor 2",
                                round((banner_1_comp_2_count + banner_2_comp_2_count) / float(banner_1_comp_2_count + banner_2_comp_2_count + banner_1_comp_1_count + banner_2_comp_1_count) * 100.0, 2),
                                banner_1_comp_2_count + banner_2_comp_2_count,
                                banner_1_comp_2_away + banner_2_comp_2_away
                            ]
                        ]
                    },
                    "home_primary_competition_ratio": {
                        "mean": 100.0,
                        "data": [
                            [
                                str(competitor_id1),
                                "Competitor 1",
                                (banner_1_comp_1_count + banner_2_comp_1_count) / float(banner_1_comp_1_count + banner_2_comp_1_count) * 100.0,
                                banner_1_comp_1_count + banner_2_comp_1_count,
                                banner_1_comp_1_away + banner_2_comp_1_away
                            ]
                        ]
                    }
                }
            }
        }

        self.assertDictEqual(builder.competition_measures, expected_results)


if __name__ == '__main__':
    unittest.main()
