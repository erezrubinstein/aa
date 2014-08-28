from __future__ import division
import pprint
from common.service_access.utilities.json_helpers import APIEncoder_New
from core.service.svc_analytics.implementation.calc.engines.economics.aggregate_time_series_economics import AggregateTimeSeriesEconomics
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import FastDateParser
from bson.objectid import ObjectId
import datetime
import unittest
import mox


class AggregateTimeSeriesEconomicsTests(mox.MoxTestBase):

    def setUp(self):

        super(AggregateTimeSeriesEconomicsTests, self).setUp()
        register_common_mox_dependencies(self.mox)

        self.main_param = Dependency("CoreAPIParamsBuilder").value
        self.main_access = Dependency("CoreAPIProvider").value

    def test_calculate__mean(self):

        calc_engine = AggregateTimeSeriesEconomics.__new__(AggregateTimeSeriesEconomics)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "target_entity_type": "company",
            "aggregate": "mean"
        }

        company_id = ObjectId()

        calc_engine.run_params = {
            "target_entity_ids": [str(company_id)]
        }

        calc_engine.fetched_data = [
            [
                ObjectId(),
                str(company_id),
                [
                    {
                        "date": datetime.datetime(2013, 5, 1),
                        "value": 10000
                    },
                    {
                        "date": datetime.datetime(2013, 4, 1),
                        "value": 10000
                    },
                    {
                        "date": datetime.datetime(2013, 3, 1),
                        "value": 10000
                    }
                ]
            ],
            [
                ObjectId(),
                str(company_id),
                [
                    {
                        "date": datetime.datetime(2013, 5, 1),
                        "value": 20000
                    },
                    {
                        "date": datetime.datetime(2013, 4, 1),
                        "value": 20000
                    },
                    {
                        "date": datetime.datetime(2013, 3, 1),
                        "value": 20000
                    }
                ]
            ]
        ]

        calc_engine._calculate()

        expected_results = {
            str(company_id): [
                {
                    "date": datetime.datetime(2013, 5, 1),
                    "value": 15000
                },
                {
                    "date": datetime.datetime(2013, 4, 1),
                    "value": 15000
                },
                {
                    "date": datetime.datetime(2013, 3, 1),
                    "value": 15000
                }
            ]
        }

        self.assertDictEqual(expected_results, calc_engine.results)

    def test_calculate__can(self):

        calc_engine = AggregateTimeSeriesEconomics.__new__(AggregateTimeSeriesEconomics)
        calc_engine.date_parser = FastDateParser()
        calc_engine.child_to_parent_dict = None

        calc_engine.output = {
            "target_entity_type": "company_analytics"
        }

        company_id = ObjectId()

        calc_engine.run_params = {
            "target_entity_ids": [str(company_id)]
        }

        calc_engine.fetched_data = [
            [
                ObjectId(),
                str(company_id),
                [
                    {
                        "date": datetime.datetime(2013, 5, 1),
                        "value": 10000
                    },
                    {
                        "date": datetime.datetime(2013, 4, 1),
                        "value": 10000
                    },
                    {
                        "date": datetime.datetime(2013, 3, 1),
                        "value": 10000
                    }
                ]
            ],
            [
                ObjectId(),
                str(company_id),
                [
                    {
                        "date": datetime.datetime(2013, 5, 1),
                        "value": 20000
                    },
                    {
                        "date": datetime.datetime(2013, 4, 1),
                        "value": 20000
                    },
                    {
                        "date": datetime.datetime(2013, 3, 1),
                        "value": 20000
                    }
                ]
            ]
        ]

        calc_engine._calculate()

        expected_results = {
            str(company_id): {
                datetime.datetime(2013, 5, 1): [10000, 20000],
                datetime.datetime(2013, 4, 1): [10000, 20000],
                datetime.datetime(2013, 3, 1): [10000, 20000]
            }
        }

        self.assertDictEqual(expected_results, calc_engine.results)

    def test_save(self):

        calc_engine = AggregateTimeSeriesEconomics.__new__(AggregateTimeSeriesEconomics)

        engine = "economics"
        threshold = "DistanceMiles10"
        metric = "aggregate_trade_area_unemployment_rate"

        calc_engine.output = {
            "target_entity_type": "company_analytics",
            "key": "data.analytics.aggregate_trade_area_unemployment_rate"
        }

        calc_engine.main_param = self.main_param
        calc_engine.main_access = self.mox.CreateMockAnything()
        calc_engine.main_access.mds = self.mox.CreateMockAnything()
        calc_engine.context = "context"
        calc_engine.date_parser = FastDateParser()
        calc_engine.engine = engine

        target_id = ObjectId()

        calc_engine.results = {
            target_id: {
                datetime.datetime(2012, 1, 1): [1, 2, 3, 4, 5],
                datetime.datetime(2012, 2, 1): [11, 12, 13, 14, 15],
                datetime.datetime(2012, 4, 1): [31, 32, 33, 34, 35]
            }
        }

        cid1 = ObjectId()
        cid2 = ObjectId()
        cid3 = ObjectId()
        can_id1 = ObjectId()
        can_id2 = ObjectId()

        existing_cans = {
            cid1: {datetime.datetime(2012, 1, 1): {"can_id": can_id1, "values": [1, 2, 3, 4, 5]}},
            cid2: {datetime.datetime(2012, 2, 1): {"can_id": can_id2, "values": [11, 12, 13, 14, 15]}},
            cid3: {datetime.datetime(2012, 4, 1): None}
        }

        # find/update calls
        # simulate the first two being found and updated

        for cid in [cid3, cid2, cid1]:

            date = existing_cans[cid].keys()[0]

            query = {
                "data.company_id": str(target_id),
                "data.engine": calc_engine.engine,
                "data.threshold": threshold,
                "$or": [{"data.date": date}, {"data.date": date.isoformat()}]
            }
            fields = ["_id"]

            params = calc_engine.main_param.mds.create_params(resource="find_entities_raw", query=query,
                                                              entity_fields=fields, as_list=True)["params"]

            if existing_cans[cid][date] is None:
                # not there, simulate finding nothing
                calc_engine.main_access.mds.call_find_entities_raw(calc_engine.output["target_entity_type"],
                                                                   params, calc_engine.context,
                                                                   encode_and_decode_results=False).AndReturn(None)

                # insert 1 new can
                can_rec = {
                    "_id": mox.IgnoreArg(),
                    "name": "Analytics Data for Company ID %s" % target_id,
                    "data": {
                        "company_id": str(target_id),
                        "engine": engine,
                        "threshold": threshold,
                        "date": datetime.datetime(2012, 4, 1),
                        "analytics": {
                            "aggregate_trade_area_unemployment_rate": [31, 32, 33, 34, 35]
                        }
                    }
                }

                calc_engine.main_access.mds.call_add_entity(
                    calc_engine.output["target_entity_type"], can_rec["name"], can_rec["data"],
                    calc_engine.context, json_encoder=APIEncoder_New
                )

            else:
                # find and update
                can_id = existing_cans[cid][date]["can_id"]
                values = existing_cans[cid][date]["values"]

                calc_engine.main_access.mds.call_find_entities_raw(calc_engine.output["target_entity_type"],
                                                                   params, calc_engine.context,
                                                                   encode_and_decode_results=False).AndReturn([[can_id]])

                calc_engine.main_access.mds.call_update_entity(calc_engine.output["target_entity_type"],
                                                               can_id, calc_engine.context,
                                                               field_name=calc_engine.output["key"],
                                                               field_value=values,
                                                               use_new_json_encoder=True)

        # need to refactor things to handle CAN deletes!

        self.mox.ReplayAll()

        calc_engine._save()


if __name__ == '__main__':
    unittest.main()
