from __future__ import division
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_cci
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import get_datetime_months_ago, LAST_ANALYTICS_DATE, ANALYTICS_TARGET_YEAR, LAST_ECONOMICS_DATE, get_months_difference
from core.common.utilities.helpers import ensure_id
from common.utilities.time_series import get_year_month_labels


__author__ = "vgold"


class SummaryMeasuresTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "analytics_competition_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # some pycharm/unittest param that blocks you from seeing a diff failure in an assert statement if it's too long
        self.maxDiff = None
        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.analytics_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def analytics_test_competition_measures(self):

        cids = [
            insert_test_company(type="retail_banner", analytics=self.__get_competition_measures_company_analytics_data(0)),
            insert_test_company(type="retail_banner", analytics=self.__get_competition_measures_company_analytics_data(1)),
            insert_test_company(type="retail_banner", analytics=self.__get_competition_measures_company_analytics_data(2))
        ]

        # TODO: Despite ensure_id, these company IDs are getting saved in CCI as strings, which is BAD

        insert_test_cci(ensure_id(cids[0]), ensure_id(cids[1]), analytics=self.__get_competition_measures_cci_analytics_data(1))
        insert_test_cci(ensure_id(cids[0]), ensure_id(cids[2]), analytics=self.__get_competition_measures_cci_analytics_data(2))

        resource = "/data/preset/competition_measures/%s" % cids[0]
        params = {
            "banner_ids": [cids[0]]
        }
        competition_measures = self.main_access.call_get_preset(resource, params=params, context=self.context)

    def analytics_test_economic_measures(self):
        self.test_case.maxDiff = None

        cids = [
            insert_test_company(type="retail_banner", analytics=self.__get_economic_measures_company_analytics_data())
        ]

        resource = "/data/preset/economic_measures/%s" % cids[0]
        params = {
            "last_store_date": LAST_ANALYTICS_DATE
        }
        economic_measures = self.main_access.call_get_preset(resource, params=params, context=self.context)

        start = LAST_ECONOMICS_DATE
        index = get_year_month_labels(start=start, end=get_datetime_months_ago(12*10, start=start))
        index.reverse()

        # dynamic date ranges we expect, mmm?
        if LAST_ECONOMICS_DATE < LAST_ANALYTICS_DATE:
            months_diff = get_months_difference(LAST_ECONOMICS_DATE, LAST_ANALYTICS_DATE)
        else:
            months_diff = get_months_difference(LAST_ANALYTICS_DATE, LAST_ECONOMICS_DATE)

        series = range(119, months_diff-1, -1)

        self.test_case.assertDictEqual(
            economic_measures,
            {
                u'graph': {
                    'stores_as_of_date': LAST_ANALYTICS_DATE.isoformat().split(".", 1)[0],
                    'as_of_date': start.isoformat().split(".", 1)[0],
                    u'data': {
                        u'company': {
                            u'unemployment': {
                                u'series': series
                            }
                        },
                        u'median': {
                            u'unemployment': {
                                u'attrs': {
                                    u'stroke-dasharray': u'5,5'
                                },
                                u'series': series
                            }
                        }
                    },
                    u'index': index,
                    u'metrics': [u'unemployment']
                },
                u'table': {
                    u'field_list': [u'&nbsp;', u'Unemployment Rate (%)<br/>Not Seasonally Adjusted'],
                    u'field_meta': {
                        u'Unemployment Rate (%)<br/>Not Seasonally Adjusted': {
                            u'decimals': 1,
                            u'type': u'percent'
                        }
                    }
                }
            }
        )

    def __get_competition_measures_company_analytics_data(self, i):

        date_string = LAST_ANALYTICS_DATE.isoformat().split(".", 1)[0]
        value = 10 * (i + 1)
        date_value_dict = {
            "date": date_string,
            "value": value
        }

        return {
            "competition": {
                "monthly": {
                    "DistanceMiles10": {
                        "aggregate_competitor_company_competition_ratio": {
                            "median": {
                                "weighted": {
                                    "total": [
                                        date_value_dict
                                    ],
                                    "primary": [
                                        date_value_dict
                                    ]
                                }
                            },
                            "min": {
                                "weighted": {
                                    "total": [
                                        date_value_dict
                                    ],
                                    "primary": [
                                        date_value_dict
                                    ]
                                }
                            }
                        },
                        "company_competition_ratio": {
                            "weighted": {
                                "total": [
                                    date_value_dict
                                ],
                                "primary": [
                                    date_value_dict
                                ]
                            }
                        },
                        "aggregate_competitor_trade_area_income": {
                            "median": {
                                "primary": [
                                    {
                                        "target_year": ANALYTICS_TARGET_YEAR,
                                        "series": [
                                            date_value_dict
                                        ]
                                    }
                                ]
                            },
                            "max": {
                                "primary": [
                                    {
                                        "target_year": ANALYTICS_TARGET_YEAR,
                                        "series": [
                                            date_value_dict
                                        ]
                                    }
                                ]
                            }
                        },
                        "aggregate_competitor_trade_area_population": {
                            "median": {
                                "primary": [
                                    {
                                        "target_year": ANALYTICS_TARGET_YEAR,
                                        "series": [
                                            date_value_dict
                                        ]
                                    }
                                ]
                            },
                            "max": {
                                "primary": [
                                    {
                                        "target_year": ANALYTICS_TARGET_YEAR,
                                        "series": [
                                            date_value_dict
                                        ]
                                    }
                                ]
                            }
                        },
                        "aggregate_competition_instances": {
                            "mean": {
                                "percents": {
                                    "weighted": {
                                        "total": [
                                            date_value_dict
                                        ],
                                        "primary": [
                                            date_value_dict
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "competition_adjusted_demographics": {
                "monthly": {
                    "DistanceMiles10": {
                        "aggregate_trade_area_income": {
                            "median": [
                                {
                                    "target_year": ANALYTICS_TARGET_YEAR,
                                    "series": [
                                        date_value_dict
                                    ]
                                }
                            ]
                        },
                        "aggregate_trade_area_population": {
                            "median": [
                                {
                                    "target_year": ANALYTICS_TARGET_YEAR,
                                    "series": [
                                        date_value_dict
                                    ]
                                }
                            ]
                        }
                    }
                }
            },
            "monopolies": {
                "monthly": {
                    "DistanceMiles10": {
                        "store_monopoly_percent": [
                            date_value_dict
                        ],
                        "aggregate_competitor_single_player_monopolies": {
                            "max": {
                                "primary": [
                                    date_value_dict
                                ]
                            },
                            "median": {
                                "primary": [
                                    date_value_dict
                                ]
                            }
                        }
                    }
                }
            },
            "stores": {
                "monthly": {
                    "store_counts": [
                        date_value_dict
                    ]
                }
            }
        }

    def __get_competition_measures_cci_analytics_data(self, i):

        date_string = LAST_ANALYTICS_DATE.isoformat().split(".", 1)[0]
        value = 10 * (i + 1)
        date_value_dict = {
            "date": date_string,
            "value": value
        }

        return {
            "competition": {
                "monthly": {
                    "DistanceMiles10": {
                        "distinct_away_store_counts": [
                            date_value_dict
                        ],
                        "competition_instances": {
                            "percents": {
                                "weighted": [
                                    date_value_dict
                                ]
                            },
                            "counts": {
                                "weighted": [
                                    date_value_dict
                                ]
                            }
                        }
                    }
                }
            }
        }

    def __get_economic_measures_company_analytics_data(self):

        return {
            "economics": {
                "monthly": {
                    "DistanceMiles10": {
                        "aggregate_trade_area_unemployment_rate": {
                            "mean": [
                                {
                                    "date": get_datetime_months_ago(i, start=LAST_ANALYTICS_DATE),
                                    "value": i
                                }
                                for i in range(120)
                            ]
                        },
                        "aggregate_competitor_trade_area_unemployment_rate": {
                            "median": {
                                "primary": [
                                    {
                                        "date": get_datetime_months_ago(i, start=LAST_ANALYTICS_DATE),
                                        "value": i
                                    }
                                    for i in range(120)
                                ]
                            }
                        }
                    }
                }
            }
        }
