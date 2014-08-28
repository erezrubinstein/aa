import json
import logging
import unittest
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from common.utilities.rest import RestProvider
from geoprocessing.helpers.ArcGIS_report_helper import ArcGISReportHelper
from geoprocessing.business_logic.config import Config
from geoprocessing.helpers.reverse_geocode_helper import put_geocoordinates_into_url

__author__ = 'spacecowboy'

class TestReverseGeocodeServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.__config = Config().instance
        dependencies.register_dependency("Config", cls.__config)
        dependencies.register_dependency("RestProvider", RestProvider())
        dependencies.register_dependency("LogManager", LogManager(logging.ERROR))



        # create sample store (home_store) and competitor stores
        cls.__long_lat_new_york = (-74.0064, 40.7142)


    @classmethod
    def tearDownClass(cls):
        dependencies.clear()


    def test_ESRI_reverse_geocode_url(self):

        self.__source_ESRI = 'ESRI'
        self.__reverse_geocode_url_ESRI = self.__config.verify_geocode_urls[self.__source_ESRI]
        self.__geocoordinate_qualifiers_ESRI = self.__config.geocoordinate_qualifiers[self.__source_ESRI]

        reverse_coded_url = put_geocoordinates_into_url(self.__long_lat_new_york[0], self.__long_lat_new_york[1],
            self.__reverse_geocode_url_ESRI, self.__geocoordinate_qualifiers_ESRI)

        reverse_geocode_response = json.loads(ArcGISReportHelper()._gis_conn.download_file(reverse_coded_url))

        self.assertEqual(reverse_geocode_response['address']['City'].lower(), 'new york')





