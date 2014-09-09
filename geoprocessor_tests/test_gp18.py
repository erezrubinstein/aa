import unittest
import json

import mox

from common.service_access.utilities.json_helpers import APIEncoder
from common.utilities.inversion_of_control import dependencies
from geoprocessing.geoprocessors.shapes.gp18_customer_derived_shape import GP18CustomerDerivedShapeGetter
from geoprocessing.helpers.ArcGIS_connection_manager import ArcGISConnection
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockResponse


__author__ = 'imashhor'


class GP18Tests(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(GP18Tests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        self.gp = GP18CustomerDerivedShapeGetter()

        # Common test variables
        self.expected_url = '/rest/services/DefaultMap/MapServer/exts/BAServer/CustomerDerivedAreas/execute'
        self.expected_response_data = { "results": []}
        self.expected_response = MockResponse(json.dumps(self.expected_response_data), "url", "request")



    def doCleanups(self):
        # call GP16Tests clean up and clean dependencies
        super(GP18Tests, self).doCleanups()
        dependencies.clear()

    def test_gp_18_with_customer_list(self):
        input_data = {
            "_id": "asdf",
            "data": {
                "latitude": 40.753767,
                "longitude": -73.979067,
                "customers": [
                    {"latitude": 40.753760, "longitude": -73.979060},
                    {"latitude": 40.753755, "longitude": -73.979054},
                    {"latitude": 40.753770, "longitude": -73.979061}
                ],
                "percentages": [80.0],
                "cutoff": {"distance": 10.0, "units": "esriMiles"}
            }}

        # Create expected gis request
        mock_gis_conn = self.mox.CreateMock(ArcGISConnection)

        expected_request_params = self._get_request_params(
            input_data["data"]["latitude"],
            input_data["data"]["longitude"],
            input_data["data"]["percentages"],
            input_data["data"]["cutoff"]["distance"]
        )

        expected_request_customers = {"RecordSet": {
            "geometryType": "esriGeometryPoint",
            "features": [
                {"geometry": {"y": 40.75376, "x": -73.97906}, "attributes": {"STORE_ID": "1"}},
                {"geometry": {"y": 40.753755, "x": -73.979054}, "attributes": {"STORE_ID": "1"}},
                {"geometry": {"y": 40.75377, "x": -73.979061}, "attributes": {"STORE_ID": "1"}}],
            "spatialReference": {"wkid": 4326}}}

        expected_request_params["Customers"] =  json.dumps(expected_request_customers, cls=APIEncoder)
        expected_url = '/rest/services/DefaultMap/MapServer/exts/BAServer/CustomerDerivedAreas/execute'

        mock_gis_conn.generate_report(expected_request_params, expected_url).AndReturn(self.expected_response)
        self.gp._arcGIS_helper._gis_conn = mock_gis_conn

        self.mox.ReplayAll()

        # Run EET
        self.gp.process_object(input_data, save_to_db=False, return_data=True)


    def test_gp_18_with_customer_item_name(self):
        input_data = {
            "_id": "asdf",
            "data": {
                "latitude": 40.753767,
                "longitude": -73.979067,
                "item_name": "SomeItemName",
                "percentages": [80.0],
                "cutoff": {"distance": 10.0, "units": "esriMiles"}
            }}

        # Create expected gis request
        mock_gis_conn = self.mox.CreateMock(ArcGISConnection)

        expected_request_params = self._get_request_params(
            input_data["data"]["latitude"],
            input_data["data"]["longitude"],
            input_data["data"]["percentages"],
            input_data["data"]["cutoff"]["distance"]
        )

        expected_request_customers = {
            "Item": {
                "projectName": "Store Customers",
                "itemName": "SomeItemName",
                "folderType": "esriFolderTradeAreas",
                "workspaceName": "Retailer Dev"
            }
        }

        expected_request_params["Customers"] =  json.dumps(expected_request_customers, cls=APIEncoder)
        expected_url = '/rest/services/DefaultMap/MapServer/exts/BAServer/CustomerDerivedAreas/execute'

        mock_gis_conn.generate_report(expected_request_params, expected_url).AndReturn(self.expected_response)
        self.gp._arcGIS_helper._gis_conn = mock_gis_conn

        self.mox.ReplayAll()
        self.gp.process_object(input_data, save_to_db=False, return_data=True)


    def test_gp_18_with_customer_item_name_weighted(self):
        input_data = {
            "_id": "asdf",
            "data": {
                "latitude": 40.753767,
                "longitude": -73.979067,
                "item_name": "SomeItemName",
                "percentages": [80.0],
                "cutoff": {"distance": 10.0, "units": "esriMiles"},
                "weight_field": "sales"
            }}

        # Create expected gis request
        mock_gis_conn = self.mox.CreateMock(ArcGISConnection)

        expected_request_params = self._get_request_params(
            input_data["data"]["latitude"],
            input_data["data"]["longitude"],
            input_data["data"]["percentages"],
            input_data["data"]["cutoff"]["distance"]
        )

        expected_request_customers = {
            "Item": {
                "projectName": "Store Customers",
                "itemName": "SomeItemName",
                "folderType": "esriFolderTradeAreas",
                "workspaceName": "Retailer Dev"
            }
        }

        expected_request_params["Customers"] =  json.dumps(expected_request_customers, cls=APIEncoder)
        expected_request_params["CustomerWeightField"] = 'sales'
        expected_url = '/rest/services/DefaultMap/MapServer/exts/BAServer/CustomerDerivedAreas/execute'

        mock_gis_conn.generate_report(expected_request_params, expected_url).AndReturn(self.expected_response)
        self.gp._arcGIS_helper._gis_conn = mock_gis_conn

        self.mox.ReplayAll()
        self.gp.process_object(input_data, save_to_db=False, return_data=True)

    def _get_request_params(self, store_lat, store_lng, percentages, cutoff_distance):

        stores_params = {
            "Points": [
                {"latitude": store_lat, "storeID": "1", "longitude": store_lng}
            ],
            "spatialReference": {"wkid": 4326}}

        return {
            'OutputSpatialReference': '{"wkid": 4326}',
            'CutOffDistance': cutoff_distance,
            'CustomerLinkField': 'STORE_ID',
            'ActiveDatasetID': 'USA_ESRI_2011',
            'Stores':  json.dumps(stores_params, cls=APIEncoder),
            'f': 'JSON',
            'OutputType': 'GetFeatureClass',
            'CutOffUnits': 'esriMiles',
            'Percentages': percentages,
            'UseCustomersCentroid': False,
            'HullType': 'Detailed'
        }

if __name__ == '__main__':
    unittest.main()