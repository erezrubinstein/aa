import unittest
import json

import mox

from common.service_access.utilities.json_helpers import APIEncoder
from common.utilities.inversion_of_control import dependencies
from geoprocessing.geoprocessors.input.gp19_upload_feature_set import GP19UploadFeatureSet
from geoprocessing.helpers.ArcGIS_connection_manager import ArcGISConnection
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockResponse


__author__ = 'imashhor'


class GP19Tests(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(GP19Tests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        self.gp = GP19UploadFeatureSet()

        # Common test variables
        self.expected_url = '/rest/services/DefaultMap/MapServer/exts/BAServer/UploadFeatureSet/execute'
        self.expected_response_data = {"results": []}
        self.expected_response = MockResponse(json.dumps(self.expected_response_data), "url", "request")


    def doCleanups(self):
        # call GP16Tests clean up and clean dependencies
        super(GP19Tests, self).doCleanups()
        dependencies.clear()

    def test_gp_19(self):
        input_data = {
            "_id": "asdf",
            "data": {
                "customers": [
                    {"latitude": 40.753760, "longitude": -73.979060, "sales": 10},
                    {"latitude": 40.753755, "longitude": -73.979054, "sales": 11},
                    {"latitude": 40.753770, "longitude": -73.979061, "sales": 21}
                ],
                "item_name": "MyTestItem"
            }}

        # Create expected gis request
        mock_gis_conn = self.mox.CreateMock(ArcGISConnection)

        expected_request_feature_set = {
            "RecordSet":
                {"geometryType": "esriGeometryPoint",
                 "features": [
                     {"geometry": {"y": 40.75376, "x": -73.97906}, "attributes": {"STORE_ID": "1", "SALES": 10}},
                     {"geometry": {"y": 40.753755, "x": -73.979054}, "attributes": {"STORE_ID": "1", "SALES": 11}},
                     {"geometry": {"y": 40.75377, "x": -73.979061}, "attributes": {"STORE_ID": "1", "SALES": 21}}],
                 "spatialReference": {"wkid": 4326}}}

        expected_item = {
            "projectName": "Store Customers",
            "itemName": "MyTestItem",
            "folderType": "esriFolderTradeAreas",
            "workspaceName": "Retailer Dev"
        }

        expected_request_format = {
            'FeatureSet': json.dumps(expected_request_feature_set, cls=APIEncoder),
            'OutputAnalysisItem':  json.dumps(expected_item, cls=APIEncoder),
            'f': 'JSON'
        }

        mock_gis_conn.generate_report(expected_request_format, self.expected_url).AndReturn(self.expected_response)
        self.gp._arcGIS_helper._gis_conn = mock_gis_conn

        self.mox.ReplayAll()

        # Run EET
        self.gp.process_object(input_data, save_to_db=False, return_data=True)


if __name__ == '__main__':
    unittest.main()