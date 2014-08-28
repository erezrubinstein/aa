import unittest
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from geoprocessing.helpers.ArcGIS_report_helper import ArcGISReportHelper
from common.utilities.inversion_of_control import dependencies, Dependency
import xml.etree.ElementTree as ET
import json
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies


class TestArcGISRestHelper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # register dependencies and get local copies
        register_concrete_dependencies(False)
        cls._config = Dependency("Config").value
        cls._ba_online_conn = Dependency("BAOnlineConnection").value

        # create sample store (home_store) and competitor stores
        cls._store = Store.simple_init_with_address(000042, 14107, -72.3950, 40.8850)
        cls._home_store = cls._store
        cls._away_stores = {
            000043: StoreCompetitionInstance.basic_init(000043, 14106, -73.9735, 40.7697),
            000044: StoreCompetitionInstance.basic_init(000044, 14106, -73.4261, 40.8681)
        }

        # make config match the below expectations
        cls._config.gp1_templates = ["Demographic and Income Profile", "Nexus Age by Sex Report", "Automotive Aftermarket Expenditures"]
        cls._config.ba_online_templates = ["acs_housing", "traffic"]

    @classmethod
    def tearDownClass(cls):
        dependencies.clear()

    def test_get_gp1_drive_time_report(self):
        gp1_response = ArcGISReportHelper().get_gp1_drive_time_report(self._store, 10)
        # we expect the following tree structure

        loads = json.loads(gp1_response.text)

        for x in loads['results']:
            # look for the url
            for template in self._config.gp1_templates:
                if x['paramName'].find(template) != -1:
                    url_download = x['value']['url']
                    self.assertTrue(len(url_download) > 10)


    def test_get_gp1_simple_rings_report(self):
        gp1_response = ArcGISReportHelper().get_gp1_simple_rings_report(self._store, 10)
        # we expect the following tree structure

        loads = json.loads(gp1_response.text)

        for x in loads['results']:
            # look for the url
            for template in self._config.gp1_templates:
                if x['paramName'].find(template) != -1:
                    url_download = x['value']['url']
                    self.assertGreater(len(url_download), 10)

    def test_get_gp2_url_in_response(self):
        gp2_response = ArcGISReportHelper().get_gp2_report(self._store, self._away_stores, 10)
        loads = json.loads(gp2_response.text)

        for x in loads['results']:
            # look for the url
            if x['paramName'].find(self._config.gp2_template) != -1:
                url_download = x['value']['url']
                self.assertGreater(len(url_download), 10)


    # def test_get_gp6_simple_rings_report(self):
    #     # make request to ba online
    #     response = ArcGISReportHelper(self._ba_online_conn).get_gp1_simple_rings_report(self._store, 10)
    #
    #     # parse json and verify structure
    #     loads = json.loads(response.text)
    #
    #     # make sure we have 2 urls
    #     self.assertEqual(len(loads["Reports"]), 2)
    #     self.assertGreater(len(loads["Reports"][0]["ReportURL"]), 10)
    #     self.assertGreater(len(loads["Reports"][1]["ReportURL"]), 10)


    def test_get_report_contents(self):
        """
        This test makes sure that we can successfully download the report files from the server
        """
        # send an ArcGIS generate report request
        helper = ArcGISReportHelper()
        gp1_response = helper.get_gp1_drive_time_report(self._store, 10)

        # parse URL and download the actual report
        report_contents = helper.get_report_contents(gp1_response, "Nexus Age by Sex Report.s.xml")

        # make sure report contents are there
        self.assertGreater(len(report_contents), 10)

        # make sure it's proper xml
        root = ET.fromstring(report_contents)
        self.assertGreater(len(root._children), 0)


    # def test_get_report_contents__ba_online(self):
    #     """
    #     This test makes sure that we can successfully download the report files from the server
    #     """
    #     # send an ArcGIS generate report request
    #     helper = ArcGISReportHelper(self._ba_online_conn)
    #     gp1_response = helper.get_gp1_simple_rings_report(self._store, 10)
    #
    #     # parse URL and download the actual report
    #     report_contents = helper.get_report_contents(gp1_response, "traffic", True)
    #
    #     # make sure report contents are there
    #     self.assertGreater(len(report_contents), 10)
    #
    #     # make sure it's proper xml
    #     root = ET.fromstring(report_contents)
    #     self.assertGreater(len(root._children), 0)

    # Commenting this out to prevent unecessary baonline requests.
    # def test_get_gp10_report(self):
    #
    #     arcgis_helper = ArcGISReportHelper(self._ba_online_conn)
    #     test_trade_area_json = '''{
    #                               "RecordSet": {
    #                                 "geometryType": "esriGeometryPolygon",
    #                                 "spatialReference": {"wkid":4326},
    #                                 "features": [
    #                                   {
    #                                     "geometry": {
    #                                       "rings": [
    #                                         [
    #                                           [-117.185412,34.063170],
    #                                           [-117.200570,34.057196],
    #                                           [-117.189395,34.052240],
    #                                           [-117.185412,34.063170]
    #                                         ]
    #                                       ],
    #                                       "spatialReference": {"wkid":4326}
    #                                     },
    #                                     "attributes": {
    #                                       "store_id": "1",
    #                                       "area_id": "10"
    #                                     }
    #                                   }
    #                                 ]
    #                               }
    #                             }'''
    #
    #     gp10_response = arcgis_helper.get_gp10_report(test_trade_area_json)
    #     self.assertEqual(gp10_response.status_code, 200)
    #     loads = json.loads(gp10_response.content)
    #     self.assertGreater(len(loads["Reports"]), 0)
    #     for report in loads["Reports"]:
    #         self.assertGreater(len(report['ReportURL']), 0)
    #
    #

#####################################################################################################################
#####################################################   Main  #######################################################
#####################################################################################################################
if __name__ == "__main__":
    unittest.main()