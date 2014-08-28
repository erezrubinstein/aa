from bson.objectid import ObjectId
from geoprocessing.geoprocessors.demographics.gp7_core_trade_area_geo_processor import GP7CoreTradeAreaDemographics
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection

__author__ = 'kingneptune'


class GP7TestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 42
        self.source = "gp7_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):
        pass

    def tearDown(self):

        # delete when ending
        self.mds_access.call_delete_reset_database()

    def test_gp7_does_not_override_analytics(self):

        data = {
            "analytics": {
                "shape": "old_shape",
                "not_shape": "random_analytics_data"
            },
            "longitude": -75.0,
            "latitude": 42.0,
            "trade_area_threshold": "DistanceMiles10",
            "store_id": 42,
            "company_id": 42
        }

        trade_area = self.main_access.mds.call_add_entity("trade_area", "name", data, self.context)
        params = {
            "entity_fields": ["_id", "data"],
            "query": {"_id": ObjectId(trade_area)}
        }
        trade_area_doc = self.main_access.mds.call_find_entities_raw("trade_area", params)[0]

        # process
        gp7 = GP7CoreTradeAreaDemographics()
        gp7.process_object(trade_area_doc)

        # requery
        trade_area_doc = self.main_access.mds.call_find_entities_raw("trade_area", params)[0]
        new_analytics = trade_area_doc["data"]["analytics"]["shape"]
        trade_area_dems = trade_area_doc["data"]["demographics"]

        expected_analytics = {
            "shape": new_analytics,
            "not_shape": "random_analytics_data",
            "AGG_INCOME_CY": {
                "value": float(trade_area_dems["PCI_CY"]["value"]) * float(trade_area_dems["TOTPOP_CY"]["value"]),
                "target_year": 2011,
                "description": "Aggregate Income"
            }
        }

        self.test_case.assertEqual(expected_analytics, trade_area_doc["data"]["analytics"])