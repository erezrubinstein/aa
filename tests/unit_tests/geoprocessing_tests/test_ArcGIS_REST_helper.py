"""
Created on Oct 22, 2012

@author: jsternberg
"""
import json
import logging
import unittest
from common.service_access.utilities.json_helpers import APIEncoder
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.business_logic.business_objects.store_competition_instance import StoreCompetitionInstance
from common.utilities.inversion_of_control import dependencies, Dependency
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.config import Config
from geoprocessing.helpers.ArcGIS_report_helper import ArcGISReportHelper
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockResponse


class TestArcGISRESTHelper(unittest.TestCase):
    def setUp(self):
        register_mock_dependencies()
        self._rest_provider = Dependency("RestProvider").value
        self._sql_provider = Dependency("DataRepository").value
        self._config = Dependency("Config").value
        dependencies.register_dependency("Config", Config().instance)
        
        # Joseph A Bank
        # dummy long and latitude since we don't need IoC here
        self.__store = Store.standard_init(120131, 14107, None, None, None, None, None, None, None, None, None)
        self.__store.address = Address.standard_init(1, None, None, None, None, None, None, 2, 1, None, None)

        # create away stores
        self.__away_stores = {44: StoreCompetitionInstance.basic_init_with_competition(000044, 14106, -73.54, 41.10, 1347901),
                             45: StoreCompetitionInstance.basic_init_with_competition(000045, 14107, -80.40, 37.21, 1347884)}


        # make config match the below expectations
        self._config.gp1_templates = ["Demographic and Income Profile", "Nexus Age by Sex Report", "Automotive Aftermarket Expenditures"]

    def tearDown(self):
        dependencies.clear()



    #####################################################################################################################
    ###########################################   Get Report Contents Tests #############################################
    #####################################################################################################################
    def test_get_report_contents(self):
        #set up mock response (see test_data/response.json)
        response_json = '{"results":[{"paramName":"OutputFeatureClass","dataType":"GPFeatureRecordSetLayer","value":{"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326},"features":[{"geometry":{"rings":[[[-73.477470832801,41.0569246589625],[-73.4775759237101,41.0567778407807],[-73.477635073139,41.0567222761656],[-73.47788553732,41.0564866808869],[-73.4780806368918,41.0561943039058],[-73.4779459275329,41.05550351477],[-73.4775379746541,41.055264505459],[-73.4772627964415,41.0551103174951],[-73.4768691830118,41.0549273271644],[-73.4767187239105,41.0548644857356],[-73.5927006473667,41.1045674635161],[-73.589618420755,41.1108495663361],[-73.5889758436313,41.1123431277376]]],"spatialReference":{"wkid":4326}},"attributes":{"FID":0,"AREA_ID":"120131_1","STORE_ID":"120131","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":41.039799,"STORE_LONG":-73.595016,"Latitude":41.039799,"Longitude":-73.595016,"NAME":"120131","DESCR":"120131","STORE_ADDR":"120131"}}]}},{"paramName":"Demographic and Income Report.s.xml","dataType":"GPDataFile","value":{"url":"/arcgisoutput/_ags_T2C53A2F9840668E6C31FAF768E361.s.xml"}},{"paramName":"Age by Sex Profile.s.xml","dataType":"GPDataFile","value":{"url":"/arcgisoutput/_ags_T38FE5941C40E8A1466DC034CB5D2E.s.xml"}}],"messages":[]}'
        test_response = MockResponse(response_json,'','')
        template = 'Age by Sex Profile'
         
        #expected data
        expected_url_regex = u'http://[a-zA-Z0-9.-]+/arcgis/arcgisoutput/_ags_T38FE5941C40E8A1466DC034CB5D2E.s.xml'

        #call the save function
        contents = ArcGISReportHelper().get_report_contents(test_response, 
                                                                template)
        
        # inspect the response
        self.assertRegexpMatches(self._rest_provider.url, expected_url_regex)
        self.assertGreater(len(contents), 0)





    #####################################################################################################################
    #############################################  Get GP1 Report Tests #################################################
    #####################################################################################################################
    def test_get_gp1_drive_time_report_url(self):
        #send request and verify its url
        self._rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp1_drive_time_report(self.__store, 10)
        #requests url is part of the expected mock response
        self.assertRegexpMatches(response.url, "http://[a-zA-Z0-9.-]+/arcgis/rest/services/DefaultMap/MapServer/exts/BAServer/DriveTime/execute")

    def test_get_gp1_drive_time_report_request(self):
        self._rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp1_drive_time_report(self.__store, 10)
        self.maxDiff = None
        expected_request = {'OutputType': 'GetReport;GetFeatureClass',
                            'CreateDetailedBorder': 'true',
                            'DetailedDriveTimes': 'true',
                            'ReportOptions': json.dumps([
                                {
                                    "ReportFormat":"s.xml",
                                    "TemplateName":"Demographic and Income Profile",
                                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                                },
                                {
                                    "ReportFormat":"s.xml",
                                    "TemplateName":"Nexus Age by Sex Report",
                                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                                },
                                {
                                    "ReportFormat":"s.xml",
                                    "TemplateName":"Automotive Aftermarket Expenditures",
                                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                                }
                            ]),
                            'Radii': '10',
                            'Stores': json.dumps({
                                "Points":[
                                    {
                                        "longitude":1.0,
                                        "description":"120131",
                                        "latitude":2.0,
                                        "name":"120131",
                                        "storeID":120131,
                                        "storeAddress":"120131"
                                    }
                                ],
                                "spatialReference": {"wkid": 4326}
                            }),
                            'OutputSpatialReference': '{"wkid": 4326}',
                            'f': 'JSON',
                            'ActiveDatasetID': 'USA_ESRI_2011',
                            'DistanceUnits': 'esriDriveTimeUnitsMinutes'}
        self.assertEqual(response.request, expected_request)

    def test_get_gp1_drive_time_report_response(self):
        #send request and verify its test response
        self._rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp1_drive_time_report(self.__store, 10)
        self.assertEqual(response.text, '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}')

    def test_get_good_address_from_response(self):
        response = '{"address": {"City": "woot city", "State": "woot land", "Zip": "42"}}'
        loads = json.loads(response)
        address = ArcGISReportHelper().get_address_from_response_ESRI(loads)
        self.assertEqual(address.city, 'woot city')
        self.assertEqual(address.state, 'woot land')
        self.assertEqual(address.zip_code, '42')

    def test_get_bad_address_from_response(self):
        response = '{"ERROR": {}}'
        loads = json.loads(response)
        address = ArcGISReportHelper().get_address_from_response_ESRI(loads)
        self.assertEqual(address.city, 'null')
        self.assertEqual(address.state, 'null')
        self.assertEqual(address.zip_code, 'null')

    def test_get_gp1_simple_rings_report_url(self):
        #send request and verify its url
        self._rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp1_simple_rings_report(self.__store, 10)
        #requests url is part of the expected mock response
        self.assertRegexpMatches(response.url, "http://[a-zA-Z0-9.-]+/arcgis/rest/services/DefaultMap/MapServer/exts/BAServer/SimpleRings/execute")

    def test_get_gp1_simple_rings_report_request(self):
        self.maxDiff = None
        self._rest_provider.post_response = '{"results":[{"paramName":"RecordSet","dataType":"GPFeatureRecordSetLayer","value":{"displayFieldName":"","fieldAliases":{"OBJECTID":"Object ID","AREA_ID":"AREA_ID","STORE_ID":"STORE_ID","RING":"RING","RING_DEFN":"Ring Definition","AREA_DESC":"AREA_DESC","AREA_DESC2":"AREA_DESC2","AREA_DESC3":"AREA_DESC3","STORE_LAT":"STORE_LAT","STORE_LONG":"STORE_LONG","NAME":"NAME","DESCR":"DESCR","STORE_ADDR":"STORE_ADDR"},"geometryType":"esriGeometryPolygon","spatialReference":{"wkid":4326,"latestWkid":4326},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"Object ID"},{"name":"AREA_ID","type":"esriFieldTypeString","alias":"AREA_ID","length":20},{"name":"STORE_ID","type":"esriFieldTypeString","alias":"STORE_ID","length":256},{"name":"RING","type":"esriFieldTypeInteger","alias":"RING"},{"name":"RING_DEFN","type":"esriFieldTypeString","alias":"Ring Definition","length":20},{"name":"AREA_DESC","type":"esriFieldTypeString","alias":"AREA_DESC","length":40},{"name":"AREA_DESC2","type":"esriFieldTypeString","alias":"AREA_DESC2","length":40},{"name":"AREA_DESC3","type":"esriFieldTypeString","alias":"AREA_DESC3","length":254},{"name":"STORE_LAT","type":"esriFieldTypeDouble","alias":"STORE_LAT"},{"name":"STORE_LONG","type":"esriFieldTypeDouble","alias":"STORE_LONG"},{"name":"NAME","type":"esriFieldTypeString","alias":"NAME","length":256},{"name":"DESCR","type":"esriFieldTypeString","alias":"DESCR","length":256},{"name":"STORE_ADDR","type":"esriFieldTypeString","alias":"STORE_ADDR","length":256}],"features":[{"attributes":{"OBJECTID":1,"AREA_ID":"25020_1","STORE_ID":"25020","RING":1,"RING_DEFN":"10 minutes","AREA_DESC":"0 - 10 minutes","AREA_DESC2":"Drive Time: 10 minutes","AREA_DESC3":"Drive Time: 10 minutes","STORE_LAT":36.031474000000003,"STORE_LONG":-114.96956299999999,"NAME":"25020","DESCR":"25020","STORE_ADDR":"25020"},"geometry":{"rings":[[[-114.9022352591395,36.098469321995694],[-114.9167488918695,36.070181024512607],[-114.92132721479651,36.067934086214905],[-114.92344219174559,36.055274132265595],[-114.9267490414732,36.051332360395605],[-114.9233427483568,36.043869488519604],[-114.91726416505099,36.038682000761298],[-114.9158093846941,36.014348846876402],[-114.90609025194711,36.004330756996595],[-114.90827402218019,35.993784811858106],[-114.9061490547542,35.986288367405905],[-114.89860489375479,35.980251792652098],[-114.8642153575647,35.968063882175997],[-114.8661719819235,35.965904901398403],[-114.8876607841971,35.960454384342],[-114.8970728415165,35.9546877534559],[-114.9047709245128,35.945001458071005],[-114.91668464462531,35.961014620669204],[-114.9313109149779,35.968925782396497],[-114.9399623250939,35.972790912986696],[-114.9578472884096,35.973559107776197],[-114.9801090118562,35.983274708690402],[-114.9933048463338,35.986318754447893],[-115.0066924150036,35.996087400783495],[-115.01452234954139,36.012323220983603],[-115.03991762336901,36.0157103271805],[-115.0552840289011,36.008730939585902],[-115.06797861816349,36.008707699731303],[-115.10040597330359,36.018240139575695],[-115.1143792483699,36.020177590609194],[-115.1186367881254,36.024211169694198],[-115.12445807825659,36.024874668562006],[-115.11894596401871,36.024553176811196],[-115.086151108419,36.0371693383223],[-115.0787718682419,36.041873110525103],[-115.0703777213229,36.043639905871004],[-115.05938161035149,36.057926752937803],[-115.0596535596362,36.075891290353496],[-115.0804794147802,36.093351109293195],[-115.079043951042,36.097132916816093],[-115.0564673338735,36.100642382301302],[-115.031479803295,36.089298731987995],[-115.01405341982129,36.088702836251898],[-114.9886847035886,36.076101723156498],[-114.981942124049,36.075755224531505],[-114.9701107338428,36.082380411221195],[-114.96385645073831,36.083369129514395],[-114.9383242367914,36.100193637961098],[-114.9016876998907,36.104282308043295],[-114.9022352591395,36.098469321995694]]]}}]}},{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_TA7D6D3F504382996F9361E3E0031F.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T55B21FDE245A193BE52BEFF22CD12.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp1_simple_rings_report(self.__store, 10)
        expected_request = {'OutputType': 'GetReport;GetFeatureClass',
                            'ReportOptions': json.dumps([
                                {
                                    "ReportFormat":"s.xml",
                                    "TemplateName":"Demographic and Income Profile",
                                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                                },
                                {
                                    "ReportFormat":"s.xml",
                                    "TemplateName":"Nexus Age by Sex Report",
                                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                                },
                                {
                                    "ReportFormat":"s.xml",
                                    "TemplateName":"Automotive Aftermarket Expenditures",
                                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                                }
                            ]),
                            'Radii': '10',
                            'Stores': json.dumps({
                                "Points":[
                                    {
                                        "longitude":1.0,
                                        "description":"120131",
                                        "latitude":2.0,
                                        "name":"120131",
                                        "storeID":120131,
                                        "storeAddress":"120131"
                                    }
                                ],
                                "spatialReference": {"wkid": 4326}
                            }),
                            'OutputSpatialReference': '{"wkid": 4326}',
                            'f': 'JSON',
                            'ActiveDatasetID': 'USA_ESRI_2011',
                            'DistanceUnits': 'esriMiles'}
        self.assertEqual(response.request, expected_request)

    def test_get_gp1_simple_rings_report_response(self):
        self._rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp1_simple_rings_report(self.__store, 10)
        self.assertEqual(response.text, '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}')





    #####################################################################################################################
    #############################################  Get GP2 Report Tests #################################################
    #####################################################################################################################

    def test_get_gp2_report_url(self):
        #send request and verify its url
        self._rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp2_report(self.__store, self.__away_stores, 10)
        #requests url is part of the expected mock response
        self.assertRegexpMatches(response.url, "http://[a-zA-Z0-9.-]+/arcgis/rest/services/DefaultMap/MapServer/exts/BAServer/LocatorReport/execute")

    def test_get_gp2_report_request(self):
        #create expected response
        home_point_json_format = json.dumps({
            "Points":[
                {
                    "longitude":self.__store.address.longitude,
                    "description":self.__store.store_id,
                    "latitude":self.__store.address.latitude,
                    "name":self.__store.store_id,
                    "storeID":self.__store.store_id
                }
            ],
            "spatialReference": {"wkid": 4326}
        }, cls = APIEncoder)
        away_stores_list = []
        for away_store in self.__away_stores.values():
            away_stores_list.append(away_store)
        away_points = []
        away_points.append({
            "storeID": away_stores_list[0].away_store_id,
            "name": away_stores_list[0].away_store_id,
            "description": away_stores_list[0].away_store_id,
            "latitude": away_stores_list[0].latitude,
            "longitude": away_stores_list[0].longitude,
            "storeAddress": away_stores_list[0].away_store_id
        })
        away_points.append({
            "storeID": away_stores_list[1].away_store_id,
            "name": away_stores_list[1].away_store_id,
            "description": away_stores_list[1].away_store_id,
            "latitude": away_stores_list[1].latitude,
            "longitude": away_stores_list[1].longitude,
            "storeAddress": away_stores_list[1].away_store_id
        })

        away_points_json_format = json.dumps({
                                                 "Points": away_points,
                                                 "spatialReference": {"wkid": 4326}
                                             }, cls = APIEncoder)
        gp2_standard_report_options = json.dumps({
            "ReportFormat":"s.xml",
            "ReportHeader":[
                {
                    "key":"subtitle",
                    "value":"Custom Report Title"
                }
            ]
        })
        expected_request_format = {
            'Stores': home_point_json_format,
            'BusinessPoints': away_points_json_format,
            'BusinessesSearchMethod': 'esriWithinRange',
            'CalculationMethod': 'esriDistanceCalcTypeDriveTime',
            'FieldNames': 'NAME;DESCR;latitude;longitude;STORE_ID',
            'FieldAliases': 'NAME;DESCR;latitude;longitude;STORE_ID',
            'ReturnGeometry': 'false',
            'ActiveDatasetID': 'USA_ESRI_2011',
            'StoreIDField': 'STORE_ID',
            'StoreNameField': 'NAME',
            'NearestDistance': str(10),
            'NearestDistanceUnits': 'esriMiles',
            'DistanceUnits': 'esriMiles',
            'StandardReportOptions': gp2_standard_report_options,
            'OutputType': 'GetReport',
            'f': 'JSON'
        }

        #send request
        self._rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp2_report(self.__store, self.__away_stores, 10)

        self.maxDiff = None

        # assert that the expected and returned dictionaries are the same
        self.assertDictEqual(response.request, expected_request_format)

    def test_get_gp2_report_response(self):
        #send request and verify its test response
        self._rest_provider.post_response = '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}'
        response = ArcGISReportHelper().get_gp2_report(self.__store, self.__away_stores, 10)
        self.assertEqual(response.text, '{"results":[{"paramName":"Demographic and Income Profile.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T97D4C677C4AA7BE75AC8F36136753.s.xml"}},{"paramName":"Nexus Age by Sex Report.s.xml","dataType":"GPDataFile","value":{"url":"/rest/directories/arcgisoutput/DefaultMap_MapServer/_ags_T84B45964C4249A0D42CBD478E5E01.s.xml"}}],"messages":[]}')




    #####################################################################################################################
    #############################################  get_drive_times Tests ################################################
    #####################################################################################################################
    def __test_GP2Report_parse_demographics_file_get_xml(self, mode):
        """
        Gets xml strings for demographic parsing unit tests.
        Positive xml is designed to pass parsing
        Else, return a fubar xml string
        """
        if mode == 'positive':
            return u'''<?xml version="1.0" encoding="utf-8"?>
                        <Report>
                          <ReportTitle>Custom Report Title</ReportTitle>
                          <ReportTitle2 />
                          <ReportName>Locator Report</ReportName>
                          <TemplateName>LocatorL</TemplateName>
                          <DataPath>locator</DataPath>
                          <ReportOrientation>Landscape</ReportOrientation>
                          <ReportType>Standard</ReportType>
                          <TextObjects />
                          <ReportVariables />
                          <Areas>
                            <Area>
                              <ReportItem name="ID" caption="" value="000043" />
                              <ReportItem name="NAME" caption="" value="000043" />
                              <ReportItem name="LOCATOR1" caption="" value="000044" />
                              <ReportItem name="LOCATOR2" caption="" value="000044" />
                              <ReportItem name="LOCATOR3" caption="" value="41.030972" />
                              <ReportItem name="LOCATOR4" caption="" value="-73.767174" />
                              <ReportItem name="LOCATOR5" caption="" value="000044" />
                              <ReportItem name="LOCATOR6" caption="" value="" />
                              <ReportItem name="DISTANCE" caption="" value="13.71" />
                              <ReportItem name="DIRECTION" caption="" value="SW" />
                            </Area>
                            <Area>
                              <ReportItem name="ID" caption="" value="000043" />
                              <ReportItem name="NAME" caption="" value="000043" />
                              <ReportItem name="LOCATOR1" caption="" value="000045" />
                              <ReportItem name="LOCATOR2" caption="" value="000045" />
                              <ReportItem name="LOCATOR3" caption="" value="41.031834" />
                              <ReportItem name="LOCATOR4" caption="" value="-73.626556" />
                              <ReportItem name="LOCATOR5" caption="" value="000045" />
                              <ReportItem name="LOCATOR6" caption="" value="" />
                              <ReportItem name="DISTANCE" caption="" value="2.46" />
                              <ReportItem name="DIRECTION" caption="" value="SW" />
                            </Area>
                          </Areas>
                        </Report>'''


        elif mode == 'negative':
            return u'''<?xml version="1.0" encoding="utf-8"?>
                  <Craptastic>
                    <Spam>Eggs</Spam>
                  </Craptastic>'''
        else:
            raise Exception('invalid xml mode, use positive or negative')

    def test_GP2Report_parse_demographics_file_basic_positive(self):
        """
        Test basic positive xml parsing in the format we expect from ArcGIS
        To avoid file dependencies, pass an xml string into the mock parser
        """
        test_full_path_as_string = self.__test_GP2Report_parse_demographics_file_get_xml('positive')
        # add drive times from the file above to the self. away stores
        away_stores = ArcGISReportHelper().get_drive_times(test_full_path_as_string, self.__away_stores)
        expected_drive_times = ['13.71', '2.46']

        for away_store in away_stores.values():
            self.assertIn(away_store.travel_time, expected_drive_times)

    def test_GP2Report_parse_demographics_file_basic_negative(self):
        """
        Test basic negative xml parsing using xml that is not formatted the way we expect from ArcGIS
        To avoid file dependencies, pass an xml string into the mock parser
        """
        test_full_path_as_string = self.__test_GP2Report_parse_demographics_file_get_xml('negative')
        away_stores = ArcGISReportHelper().get_drive_times(test_full_path_as_string, self.__away_stores)
        given_drive_times = ['13.71', '2.46']

        self.assertEqual(away_stores, {})



    #####################################################################################################################
    ############################################   Parse demographics Tests #############################################
    #####################################################################################################################
    def __test_GP1_parse_demographics_file_get_xml(self, mode):
        """
        Gets xml strings for demographic parsing unit tests.
        Positive xml is designed to pass parsing
        Else, return a fubar xml string
        """
        if mode == 'positive':
            return u'''<?xml version="1.0" encoding="utf-8"?>
              <Report>
                  <ReportTitle />
                  <ReportTitle2>Custom Title</ReportTitle2>
                  <ReportName>Nexus Age by Sex Report</ReportName>
                  <TemplateName>Nexus Age by Sex Report</TemplateName>
                  <Areas>
                    <Area>
                      <ReportItem name="RING" caption="" value="1" />
                      <ReportItem name="TOTPOP_CY" caption="2055 Total Population"
                          value="147031.00000000" />
                   </Area>
                  </Areas>
              </Report>'''
        elif mode == 'negative':
            return u'''<?xml version="1.0" encoding="utf-8"?>
                  <Craptastic>
                    <Spam>Eggs</Spam>
                  </Craptastic>'''
        else:
            raise Exception('invalid xml mode, use positive or negative')

    def test_GP1_parse_demographics_file_basic_positive(self):
        """Test basic positive xml parsing in the format we expect from ArcGIS
        To avoid file dependencies, pass an xml string into the mock parser"""
        test_xml = self.__test_GP1_parse_demographics_file_get_xml('positive')
        demographic_information = ArcGISReportHelper().parse_demographics_file(test_xml, self.__store.store_id)

        demographic_report_items = demographic_information[0]
        census_year = demographic_information[1]

        self.assertEqual(census_year, 2011)
        self.assertEqual(demographic_report_items[0].name, 'RING')
        self.assertEqual(demographic_report_items[0].value, 1.0)
        self.assertEqual(demographic_report_items[0].description, '')
        self.assertEqual(demographic_report_items[1].name, 'TOTPOP_CY')
        self.assertEqual(demographic_report_items[1].value, 147031.0)
        self.assertEqual(demographic_report_items[1].description, '2055 Total Population')

    def test_GP1_parse_demographics_file_basic_negative(self):
        """Test basic negative xml parsing using xml that is not formatted
        the way we expect from ArcGIS.
        To avoid file dependencies, pass an xml string into the mock parser."""
        test_xml = self.__test_GP1_parse_demographics_file_get_xml('negative')
        demographic_information = ArcGISReportHelper().parse_demographics_file(test_xml, self.__store.store_id)
        demographic_report_items = demographic_information[0]

        self.assertListEqual(demographic_report_items, [])

if __name__ == "__main__":
    unittest.main()