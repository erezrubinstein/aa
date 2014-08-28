import unittest
import json

import mox

from common.utilities.inversion_of_control import dependencies
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies
from geoprocessing.geoprocessors.shapes.gp17_drive_time_shape import GP17DriveTimeShapeGetter
from geoprocessing.helpers.ArcGIS_report_helper import ArcGISReportHelper
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockResponse


__author__ = 'jsternberg'

class GP17Tests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(GP17Tests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        # create the mock retailer_trade_area
        self.trade_area_id = "asdf"
        self.latitude = 40.753767
        self.longitude = -73.979067
        self.minutes = 1
        self.minutes_threshold = None
        self.trade_area = {
            "_id" : self.trade_area_id,
            "data" : {
                "latitude" : self.latitude,
                "longitude" : self.longitude,
                "minutes": self.minutes
            }
        }

        # create the test gp
        self.gp = GP17DriveTimeShapeGetter()
        self.gp._entity = self.trade_area

    def doCleanups(self):

        # call GP16Tests clean up and clean dependencies
        super(GP17Tests, self).doCleanups()
        dependencies.clear()

    def test_gp_17_initialize_defaults(self):

        # run initialize
        self.gp._initialize()

        # make sure we're using the right vars
        self.assertEqual(self.gp.latitude, self.latitude)
        self.assertEqual(self.gp.longitude, self.longitude)
        self.assertEqual(self.gp.minutes, self.minutes)

    def test_gp_17_complete_run(self):

        mock_response, mock_shape = self.__set_up_stubs()

        # start recording
        self.gp._arcGIS_helper.get_drive_time_shape(self.latitude, self.longitude, self.minutes, self.minutes_threshold).AndReturn(mock_response)
        self.gp._arcGIS_helper.get_trade_area_shape_array_representation(mock_response).AndReturn(mock_shape)

        # replay all
        self.mox.ReplayAll()

        # test!
        self.gp.process_object(self.trade_area, save_to_db=False)
        self.assertEqual(self.gp._entity["data"]["shape"], mock_shape)

    def test_gp_17_raises_error_if_save(self):

        mock_response, mock_shape = self.__set_up_stubs()

        # start recording
        self.gp._arcGIS_helper.get_drive_time_shape(self.latitude, self.longitude, self.minutes, self.minutes_threshold).AndReturn(mock_response)
        self.gp._arcGIS_helper.get_trade_area_shape_array_representation(mock_response).AndReturn(mock_shape)

        # no need to record for this test
        self.mox.ReplayAll()

        with self.assertRaises(ValueError):
            self.gp.process_object(self.trade_area, save_to_db=True)

    def __set_up_stubs(self):

        # create mock drive time shape
        mock_shape = [[[1,2],[3,4],[5,6],[1,2]], [[10,11],[12,13],[14,15],[10,11]]]

        ArcGIS_response = {
            "results": [
                {
                    "paramName": "RecordSet",
                    "value": {
                        "features": [
                            {
                                "geometry": {
                                    "rings": mock_shape
                                }
                            }
                        ]
                    }
                }
            ]
        }

        mock_response = MockResponse(json.dumps(ArcGIS_response), "url", "request")

        # stub out the ArcGIS helper
        self.gp._arcGIS_helper = self.mox.CreateMock(ArcGISReportHelper)

        return mock_response, mock_shape


if __name__ == '__main__':
    unittest.main()