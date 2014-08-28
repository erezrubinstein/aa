from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import parse_date, FastDateParser, LAST_ANALYTICS_DATE
from common.utilities.inversion_of_control import dependencies
from common.utilities.time_series import get_monthly_time_series
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competition.trade_area_competitive_stores \
    import TradeAreaCompetitiveStores
import unittest
import mox
import datetime


__author__ = 'vgold'


class TradeAreaCompetitiveStoresTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TradeAreaCompetitiveStoresTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.maxDiff = None

    def doCleanups(self):

        super(TradeAreaCompetitiveStoresTests, self).doCleanups()
        dependencies.clear()

    def test_calculate__full_series(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        company_id = generate_id()

        # Make an instance without pesky __init__
        calc_engine = TradeAreaCompetitiveStores.__new__(TradeAreaCompetitiveStores)
        calc_engine.start_of_month_timeseries = get_monthly_time_series(end=LAST_ANALYTICS_DATE)
        calc_engine.date_parser = FastDateParser()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }

        # Set fetched data
        calc_engine.fetched_data = [
            [
                trade_area_id1,
                company_id,
                [
                    {
                        "start_date": datetime.datetime(2013, 2, 1),
                        "end_date": datetime.datetime(2013, 6, 1),
                        "away_company_id": company_id, "weight": 0.1, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    },
                    {
                        "start_date": datetime.datetime(2013, 3, 1),
                        "end_date": datetime.datetime(2013, 6, 1),
                        "away_company_id": company_id, "weight": 0.2, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    },
                    {
                        "start_date": datetime.datetime(2013, 4, 1),
                        "end_date": datetime.datetime(2013, 6, 1),
                        "away_company_id": company_id, "weight": 0.3, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    },
                    {
                        "start_date": datetime.datetime(2013, 5, 1),
                        "end_date": datetime.datetime(2013, 6, 1),
                        "away_company_id": company_id, "weight": 0.4, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    },
                    {
                        "start_date": datetime.datetime(2013, 2, 1),
                        "end_date": datetime.datetime(2013, 3, 1),
                        "away_company_id": company_id, "weight": 0.5, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    },
                    {
                        "start_date": datetime.datetime(2013, 2, 1),
                        "end_date": datetime.datetime(2013, 4, 1),
                        "away_company_id": company_id, "weight": 0.6, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    }
                ],
                [datetime.datetime(1990, 05, 18), datetime.datetime(3000, 05, 18)]
            ]
        ]

        # Do maths
        calc_engine._calculate()

        for entity in calc_engine.tacis:
            expected_store_count = self.__get_num_stores_for_date(calc_engine.fetched_data[0][2], entity.date)
            len_taci_cis = len(list(entity.competition_instances))
            self.assertEqual(len_taci_cis, expected_store_count)


    def test_calculate__partial_series(self):

        # Make some object ids to be real
        trade_area_id1 = generate_id()
        company_id = generate_id()

        # Make an instance without pesky __init__
        calc_engine = TradeAreaCompetitiveStores.__new__(TradeAreaCompetitiveStores)
        calc_engine.start_of_month_timeseries = get_monthly_time_series(end=LAST_ANALYTICS_DATE)
        calc_engine.date_parser = FastDateParser()

        # Set instance variables
        calc_engine.run_params = {
            "target_entity_ids": [company_id]
        }

        # Set fetched data
        calc_engine.fetched_data = [
            [
                trade_area_id1,
                company_id,
                [
                    {
                        "start_date": datetime.datetime(2011, 4, 1),
                        "end_date": datetime.datetime(2012, 6, 1),
                        "away_company_id": company_id, "weight": 0.1, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    },
                    {
                        "start_date": datetime.datetime(2011, 5, 23),
                        "end_date": datetime.datetime(2011, 6, 1),
                        "away_company_id": company_id, "weight": 0.2, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    },
                    {
                        "start_date": datetime.datetime(2012, 5, 1),
                        "end_date": datetime.datetime(2012, 6, 1),
                        "away_company_id": company_id, "weight": 0.3, "away_store_id": "store1",
                        "away_company_name": "away_company_name",
                        "away_street_number": "away_street_number",
                        "away_street": "away_street",
                        "away_city": "away_city",
                        "away_state": "away_state",
                        "away_zip": "away_zip",
                        "away_geo": ["away_geo_lng", "away_geo_lat"],
                        "away_lng": "away_geo_lng",
                        "away_lat": "away_geo_lat"
                    }
                ],
                [datetime.datetime(2011, 04, 01), datetime.datetime(2012, 06, 01)]
            ]
        ]

        # Do maths
        calc_engine._calculate()

        # check that the length of the overall entities is 14, and that the last date is 2012, 06, 01
        # iterate through the generator and save results to a local list, so we can do asserts
        tacis_list = []
        for taci in calc_engine.tacis:
            # ci's is also a generator
            competition_instances = []
            for ci in taci.competition_instances:
                competition_instances.append(ci)
            taci.competition_instances = competition_instances
            tacis_list.append(taci)

        self.assertEqual(14, len(tacis_list))
        self.assertEqual(datetime.datetime(2012, 5, 1), self._extract_latest_date(tacis_list))

        # check that for april 2011, competition length is 1
        self.assertEqual(1, self._number_of_competitors_for_month(tacis_list, datetime.datetime(2011, 4, 1)))

        # check that for may 2011, competition length is 2
        self.assertEqual(2, self._number_of_competitors_for_month(tacis_list, datetime.datetime(2011, 5, 1)))

        # check that for may 2012, competition length is 2
        self.assertEqual(2, self._number_of_competitors_for_month(tacis_list, datetime.datetime(2012, 5, 1)))

        # check that for the rest, competition length is 1
        for item in tacis_list:
            if item.date not in [
                datetime.datetime(2011, 5, 1),
                datetime.datetime(2011, 6, 1),
                datetime.datetime(2012, 5, 1),
                datetime.datetime(2012, 6, 1)

            ]:
                self.assertEqual(1, len(item.competition_instances))

    def _number_of_competitors_for_month(self, tacis, m_date):

        count = 0
        for taci in tacis:
            c_date = taci.date
            if c_date == m_date:
                count = len(taci.competition_instances)
                break

        return count

    def _extract_latest_date(self, tacis):

        latest_date = datetime.datetime(1990, 05, 18)
        for taci in tacis:
            if parse_date(taci.date) > latest_date:
                latest_date = taci.date

        return latest_date

    def __get_num_stores_for_date(self, stores, date):

        return len([
            store
            for store in stores
            if parse_date(store["start_date"]) <= date < parse_date(store["end_date"])
        ])

    def __get_sample_tacis(self):

        company_id1 = generate_id()
        trade_area_id1 = generate_id()

        company_id2 = generate_id()
        store_id2 = generate_id()

        one_moment = datetime.timedelta(microseconds=1000)

        return [
            [
                str(generate_id()),
                str(company_id1),
                str(trade_area_id1),
                str(datetime.datetime(2011, 1, 1) - one_moment),
                [
                    {
                        "company_id": str(company_id2),
                        "store_id": str(store_id2),
                        "weight": 0.8
                    }
                ]
            ],
            [
                str(generate_id()),
                str(company_id1),
                str(trade_area_id1),
                str(datetime.datetime(2011, 2, 1) - one_moment),
                [
                    {
                        "company_id": str(company_id2),
                        "store_id": str(store_id2),
                        "weight": 0.8
                    }
                ]
            ],
            [
                str(generate_id()),
                str(company_id1),
                str(trade_area_id1),
                str(datetime.datetime(2011, 3, 1) - one_moment),
                [
                    {
                        "company_id": str(company_id2),
                        "store_id": str(store_id2),
                        "weight": 0.8
                    }
                ]
            ]
        ]

    def __get_sample_taci_results(self, tacis):

        new_taci_id1 = generate_id()
        new_taci_id2 = generate_id()
        new_taci_id3 = generate_id()
        new_taci_id4 = generate_id()

        company_id1 = tacis[0][1]
        store_id2 = tacis[0][4][0]["store_id"]
        trade_area_id1 = tacis[0][2]
        company_id2 = tacis[0][4][0]["company_id"]
        store_id1 = generate_id()
        trade_area_id2 = generate_id()

        taci_results = {
            str(new_taci_id1): {
                "_id": new_taci_id1,
                "name": "asdf",
                "data": {
                    "date": parse_date(tacis[1][3]),
                    "company_id": str(company_id1),
                    "store_id": str(store_id1),
                    "trade_area_id": str(trade_area_id1),
                    "analytics": {
                        "competition_instances": [
                            {
                                "company_id": str(company_id2),
                                "store_id": str(store_id2),
                                "weight": 0.8
                            }
                        ]
                    }
                }
            },
            str(new_taci_id2): {
                "_id": new_taci_id2,
                "name": "asdf",
                "data": {
                    "date": parse_date(tacis[2][3]),
                    "company_id": str(company_id1),
                    "store_id": str(store_id1),
                    "trade_area_id": str(trade_area_id1),
                    "analytics": {
                        "competition_instances": [
                            {
                                "company_id": str(company_id2),
                                "store_id": str(store_id2),
                                "weight": 0.5
                            }
                        ]
                    }
                }
            },
            str(new_taci_id3): {
                "_id": new_taci_id3,
                "name": "asdf",
                "data": {
                    "date": parse_date(tacis[1][3]),
                    "company_id": str(company_id2),
                    "store_id": str(store_id2),
                    "trade_area_id": str(trade_area_id2),
                    "analytics": {
                        "competition_instances": [
                            {
                                "company_id": str(company_id1),
                                "store_id": str(store_id1),
                                "weight": 0.5
                            }
                        ]
                    }
                }
            },
            str(new_taci_id4): {
                "_id": new_taci_id4,
                "name": "asdf",
                "data": {
                    "date": parse_date(tacis[2][3]),
                    "company_id": str(company_id2),
                    "store_id": str(store_id2),
                    "trade_area_id": str(trade_area_id2),
                    "analytics": {
                        "competition_instances": [
                            {
                                "company_id": str(company_id1),
                                "store_id": str(store_id1),
                                "weight": 0.5
                            }
                        ]
                    }
                }
            }
        }

        taci_ids = [new_taci_id1, new_taci_id2, new_taci_id3, new_taci_id4]

        return taci_results, taci_ids


if __name__ == '__main__':
    unittest.main()
