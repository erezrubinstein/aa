from common.service_access.utilities.json_helpers import APIEncoder
from geoprocessing.business_logic.business_objects.address import Address
from geoprocessing.helpers.ArcGIS_connection_manager import ArcGISConnectionManager
import xml.etree.ElementTree as ET
from geoprocessing.business_logic.business_objects.report_item import ReportItem
import json
from common.utilities.inversion_of_control import Dependency, HasAttributes

class ArcGISReportHelper(object):
    def __init__(self, gis_conn = None):
        self._config = Dependency("Config", HasAttributes("gp1_drive_time_radius", "gp1_drive_time_distance_units",
            "dataset_id", "gp1_simple_rings_radius", "gp1_simple_rings_distance_units", "gp2_radius",
            "gp1_templates", "gp1_drive_time_url", "gp1_simple_rings_url", "gp2_url")).value

        # get a local ArcGIS connection from the load balancer and keep it so that we have a "sticky session"
        if gis_conn is None:
            self._gis_conn = ArcGISConnectionManager().instance.get_connection()
            self._simple_rings_url = self._config.gp1_simple_rings_url
            self._drive_time_url = self._config.gp1_drive_time_url
            self._customer_derived_url = self._config.customer_derived_url
            self._gp1_templates = self._config.gp1_templates
            self._upload_feature_set_url = self._config.upload_feature_set_url
            self._retailer_workspace = self._config.retailer_workspace
            self._store_customer_project = self._config.store_customer_project

        # get a ba_online connection
        else:
            self._gis_conn = gis_conn
            self._simple_rings_url = self._config.ba_online_simple_rings_url
            self._drive_time_url = self._config.ba_online_drive_time_url
            self._customer_derived_url = None
            self._upload_feature_set_url = None
            self._gp1_templates = self._config.ba_online_templates
            self._ba_online_summary_reports_url = self._config.ba_online_summary_reports_url
            self._retailer_workspace = self._config.retailer_workspace
            self._store_customer_project = self._config.store_customer_project

    def __store_point(self, store_id, longitude, latitude):
        name = str(store_id)
        description = str(store_id)
        store_address = str(store_id)
        return {
            "longitude": longitude,
            "description": description,
            "latitude": latitude,
            "name": name,
            "storeID": store_id,
            "storeAddress":store_address
        }


    def __home_point_form(self, home_store):
        name = home_store.store_id
        description = home_store.store_id
        return {
            "longitude": home_store.address.longitude,
            "description": description,
            "latitude": home_store.address.latitude,
            "name": name,
            "storeID": home_store.store_id
        }


    def __away_point_form(self, away_store):
        name = away_store.away_store_id
        description = away_store.away_store_id
        store_address = away_store.away_store_id
        return {
            "storeID": away_store.away_store_id,
            "name": name,
            "description": description,
            "latitude": away_store.latitude,
            "longitude": away_store.longitude,
            "storeAddress":store_address
        }


    def __wrap_point(self, points):
        # be able to pass in one point
        if isinstance(points, dict):
            points = [points]

        return {
            "Points": points ,
            "spatialReference":  { "wkid": self._config.wkid }
        }


    def __generate_gp1_report_request_format(self, store, complexity, radius):
        point = self.__store_point(store.store_id, store.address.longitude, store.address.latitude)
        wrapped_point = self.__wrap_point(point)

        if complexity == 'drive_time':
            return {
                'Stores': json.dumps(wrapped_point, cls = APIEncoder),
                'CreateDetailedBorder': 'true',
                'Radii': str(self._config.gp1_drive_time_radius),
                'DistanceUnits': self._config.gp1_drive_time_distance_units,
                'ActiveDatasetID': self._config.dataset_id,
                'OutputSpatialReference': '{"wkid": %s}' % self._config.wkid,
                'ReportOptions': json.dumps(self.__generate_gp1_report_options(), cls = APIEncoder),
                'DetailedDriveTimes': 'true',
                'OutputType': 'GetReport;GetFeatureClass',
                'f': 'JSON'
            }

        elif complexity =='simple_rings':
            return {
                'Stores': json.dumps(wrapped_point, cls = APIEncoder),
                'Radii': str(radius),
                'DistanceUnits': self._config.gp1_simple_rings_distance_units,
                'ActiveDatasetID': self._config.dataset_id,
                'OutputSpatialReference': '{"wkid": %s}' % self._config.wkid,
                'ReportOptions': json.dumps(self.__generate_gp1_report_options(), cls = APIEncoder),
                'OutputType': 'GetReport;GetFeatureClass',
                'f': 'JSON'
            }

        else:
            raise Exception('Unexpected complexity, pass in either drive_time or simple_rings')


    def __generate_gp1_report_options(self, override_template=None):
        if override_template:
            return [{
                "ReportFormat": "s.xml",
                "TemplateName": override_template,
                "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
            }]
        else:
            report_options = []
            for template in self._gp1_templates:
                report_options.append({
                    "ReportFormat": "s.xml",
                    "TemplateName": template,
                    "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
                })
            return report_options


    def __generate_gp2_report_form(self, home_store, away_stores, radius):
        home_point = self.__home_point_form(home_store)
        wrapped_home_point = self.__wrap_point(home_point)

        # make the large list of away store points
        away_store_list = []
        for away_store in away_stores.values():
            # !! change this to append(self.__away_point_form(away_store))
            away_store_list.append(self.__away_point_form(away_store))

        # wrap away points
        wrapped_away_points = self.__wrap_point(away_store_list)

        return {
            'Stores': json.dumps(wrapped_home_point, cls = APIEncoder),
            'BusinessPoints': json.dumps(wrapped_away_points, cls = APIEncoder),
            'BusinessesSearchMethod': 'esriWithinRange',
            'CalculationMethod': 'esriDistanceCalcTypeDriveTime',
            'FieldNames': 'NAME;DESCR;latitude;longitude;STORE_ID',
            'FieldAliases': 'NAME;DESCR;latitude;longitude;STORE_ID',
            'ActiveDatasetID': self._config.dataset_id,
            'StoreIDField': 'STORE_ID',
            'StoreNameField': 'NAME',
            'NearestDistance': str(radius),
            'NearestDistanceUnits': 'esriMiles',
            'DistanceUnits': 'esriMiles', #try removing this one -- it's ignored for DriveTime
            'StandardReportOptions': json.dumps(self.__generate_gp2_report_options(), cls = APIEncoder),
            'OutputType': 'GetReport',
            'ReturnGeometry': 'false', #to speed things up
            'f': 'JSON'
        }


    def __generate_gp2_report_options(self):
        return {
            "ReportFormat":"s.xml",
            "ReportHeader":[
                {
                    "key":"subtitle",
                    "value":"Custom Report Title"
                }
            ]

        }


    def __parse_template_url_from_response(self, response, template_name):
        url_download = None
        loads = json.loads(response.text)
        for x in loads['results']:
            if x['paramName'].find(template_name) != -1:
                url_download = x['value']['url']

        if url_download is None:
            raise Exception('Oh no! URL not pulled')
        return url_download


    def __parse_template_url_from_ba_online_response(self, response, template_name):

        loads = json.loads(response.text)

        for report in loads['Reports']:
            if report['TemplateName'] == template_name:
                return report["ReportURL"]


    def get_gp1_drive_time_report(self, store, radius):
        return self._gis_conn.generate_report(
                            self.__generate_gp1_report_request_format(store, 'drive_time', radius),
                            self._drive_time_url)


    def get_gp1_simple_rings_report(self, store, radius):
        return self._gis_conn.generate_report(
                            self.__generate_gp1_report_request_format(store, 'simple_rings', radius),
                            self._simple_rings_url)


    def get_gp2_report(self, home_store, away_stores, radius):
        return self._gis_conn.generate_report(self.__generate_gp2_report_form(home_store, away_stores, radius), self._config.gp2_url)

    def get_trade_area_shape_array_representation(self, response):

        loads = json.loads(response.text)

        shape_arrays = None
        for x in loads['results']:
            if x['paramName'] == 'RecordSet':
                shape_arrays = x['value']['features'][0]['geometry']['rings']

        return shape_arrays

    def get_trade_area_shape(self, response):

        loads = json.loads(response.text)

        # build a list of tuples

        wkt_representation_linestrings = []
        shapes = []
        for x in loads['results']:
            if x['paramName'] == 'RecordSet':
                shape_arrays = x['value']['features'][0]['geometry']['rings']

                for shape_array in shape_arrays:

                    temp_shape = shape_array
                    shape = None
                    for geocoordinate in temp_shape:
                        shape_point = ' '.join([''.join([str(geocoordinate[0])]), ''.join([str(geocoordinate[1])])])
                        if not shape:
                            shape = shape_point
                        else:
                            shape = ', '.join([shape, shape_point])
                    shapes.append(shape)
        wkt_representation_linestrings = [''.join(['LINESTRING', '(', shape, ')']) for shape in shapes]

        wkt_representation_linestring = max(wkt_representation_linestrings, key = len)

        if wkt_representation_linestring:
            return wkt_representation_linestring
        else:
            raise Exception('Could not pull geoshape from response')

    def get_report_contents(self, response, template, is_ba_online_response = False):
        # parse URL from GIS response
        if is_ba_online_response:
            url = self.__parse_template_url_from_ba_online_response(response, template)
        else:
            url = self.__parse_template_url_from_response(response, template)

        #download the file and return the filename
        return self._gis_conn.download_file(url)

    def __generate_stop_form(self, home_store, away_store):

        return '''
                    {
                        "features": [
                                        {
                                          "geometry" : {"x" : %s, "y" : %s},
                                          "attributes" : {"Name" : "Store_ID_%d", "RouteName" : "Route A"}
                                        },
                                        {
                                          "geometry" : {"x" : %s, "y" : %s},
                                          "attributes" : {"Name" : "Store_ID_%d", "RouteName" : "Route A"}
                                        }
                                      ]
                    }
                  ''' % (home_store.address.longitude, home_store.address.latitude, home_store.store_id,
                         away_store.longitude, away_store.latitude, away_store.away_store_id)

    def generate_NA_form(self, home_store, away_store):

        stops = self.__generate_stop_form(home_store, away_store)

        return {

            'stops': stops,
            'barriers': '{}',
            'polylineBarriers': '{}',
            'polygonBarriers': '{}',
            'outSR': '{"wkid": %s}' % self._config.wkid,
            'ignoreInvalidLocations': 'false',
            'accumulateAttributeNames': 'null',
            'impedanceAttributeName': 'Time',
            'restrictionAttributeNames': 'Driving an Automobile, Avoid Private Roads, OneWay',
            'attributeParameterValues': '{}',
            'restrictUTurns': 'esriNFSBAllowBacktrack',
            'useHierarchy': 'true',
            'returnDirections': 'false',
            'returnRoutes': 'false',
            'returnStops': 'true',
            'returnBarriers': 'false',
            'returnPolylineBarriers': 'false',
            'returnPolygonBarriers': 'false',
            'directionsLanguage': 'en-US',
            'directionsStyleName': 'null',
            'outputLines': 'esriNAOutputLineNone',
            'findBestSequence': 'false',
            'preserveFirstStop': 'true',
            'preserveLastStop': 'false',
            'useTimeWindows': 'false',
            'startTime': 'null',
            'outputGeometryPrecision': '0.0',
            'outputGeometryPrecisionUnits': 'esriMiles',
            'directionsOutputType': 'esriDOTStandard',
            'directionsTimeAttributeName': 'Time',
            'directionsLengthUnits': 'esriNAUMiles',
            'returnZ': 'false',
            'f': 'JSON'
        }

    def solve_route(self, home_store, away_store):

        return self._gis_conn.generate_report(self.generate_NA_form(home_store, away_store), self._config.network_analyst_route_solver_url)

    def get_drive_times_from_route(self, away_stores, responses):
        for away_store in away_stores.values():
            response = responses[away_store.away_store_id]
            response_dict = json.loads(response.text)
            away_store.travel_time = response_dict['stops']['features'][1]['attributes']['Cumul_Time']
        return away_stores


    def parse_demographics_file(self, xml_contents, store_id):
        # parses downloaded file into a ReportItemCollection
        root = ET.fromstring(xml_contents)

        # sneaky
        census_year = 2011
        demographic_report_items = []
        for child in root.iter('ReportItem'):
            name = child.get('name')

            value = child.get('value')
            caption = child.get('caption')
            report_item = ReportItem(name, value, caption)
            demographic_report_items.append(report_item)

        return demographic_report_items, census_year

    def get_address_from_response_Google(self, response):

        address = Address()

        if 'results' in response.keys() and response['results'] and 'address_components' in response['results'][0].keys():
            for sub_dictionary in response['results'][0]['address_components']:
                for key in sub_dictionary:
                    if sub_dictionary[key][0] == 'route':
                        try:
                            address.street = sub_dictionary['long_name'].encode('utf-8')
                        except:
                            address.street = None
                    if sub_dictionary[key][0] == 'locality':
                        try:
                            address.city = sub_dictionary['long_name'].encode('utf-8')
                        except:
                            address.city = None

                    if sub_dictionary[key][0] == 'administrative_area_level_1':
                        address.state = sub_dictionary['short_name'].encode('utf-8')


                    if sub_dictionary[key][0] == 'postal_code':
                        address.zip_code = sub_dictionary['long_name'].encode('utf-8')
        else:
            address.city = 'null'
            address.state = 'null'
            address.zip_code = 'null'

        return address


    def get_address_from_response_ESRI(self, response):
        address = Address()
        if 'address' in response.keys():
            try:
                address.city = response['address']['City'].encode('utf-8')
            except:
                address.city = None

            address.state = response['address']['State'].encode('utf-8')
            address.zip_code = response['address']['Zip'].encode('utf-8')

        else:
            address.city = 'null'
            address.state = 'null'
            address.zip_code = 'null'

        return address

    def get_drive_times(self, xml_contents, away_stores):

        root = ET.fromstring(xml_contents)
        away_stores_filtered = {}
        # maybe this is inefficient (!?)
        for parent in root.iter('Area'):
            home_id = None
            away_id = None
            travel_time = None
            for child in parent:
                if child.get('name') == 'NAME':
                    home_id = child.get('value')
                if child.get('name') == 'LOCATOR1' and child.get('value') != 'N/A':
                    away_id = child.get('value')
                if child.get('name') == 'DISTANCE':
                    travel_time = child.get('value')
            if home_id is not None and away_id is not None and travel_time is not None:
                away_stores_filtered[int(away_id)] = away_stores[int(away_id)]
                away_stores_filtered[int(away_id)].travel_time = travel_time

        return away_stores_filtered

    ######################################## GP10 methods ###################################
    def get_gp10_report(self, trade_area_json):
        return self._gis_conn.generate_report_with_post(self.__gp10_get_report_params(trade_area_json), self._ba_online_summary_reports_url)

    def __gp10_get_report_params(self, trade_area_json):
        #get report options
        #this is a copy of __generate_gp1_report_options()
        #because we will use self._gp1_templates to hold ba_online templates also
        report_options = []
        for template in self._gp1_templates:
            report_options.append({
                "ReportFormat": "s.xml",
                "TemplateName": template,
                "ReportHeader":[{"key":"subtitle", "value":"Custom Title"}]
            })

        gp10_report_form = {
            "Boundaries": trade_area_json,
            "ReportOptions": json.dumps(report_options, cls=APIEncoder),
            "TaskOutputType": "GetReport",
            "f": "json",
            "areaidfield": "area_id"
        }

        return gp10_report_form

    def get_shape_array(self, start_x, start_y, end_x, end_y, wkid, cell_size):

        extent = {
            "xmin": start_x,
            "ymin": end_y,
            "xmax": end_x,
            "ymax": start_y,
            "spacialReference": {"wkid": wkid}
        }


        options = [{
            "ReportFormat" : "s.xml",
            # not used
            "TemplateName" : "Demographic and Income Profile"
        }]

        post_params = {
            "AnalysisExtent": json.dumps({"Extent": extent}),
            "DistanceUnits": "esriMiles",
            "GridCellSize": cell_size,
            "OutputType": "GetFeatureClass",
            "f": "JSON",
            "ReportOptions": json.dumps(options)
        }


        response = self._gis_conn.generate_report(post_params, self._config.grid_url)
        return self._extract_shape_array_from_grid_response(response)

    def _extract_shape_array_from_grid_response(self, response):
        report = json.loads(response.text)
        shape_array = []
        for shape in report["results"][0]["value"]["features"]:
            for geoco in shape["geometry"]["rings"][0]:
                shape_array.append([float(geoco[0]), float(geoco[1])])
        return shape_array

    def give_shape_array_get_demographics_report(self, shape_array, override_template=None):

        boundaries = {
            "Recordset" : {
                "geometryType" : "esriGeometryPolygon",
                "spatialReference" : { "wkid" : self._config.wkid },
                "features" : [
                    {
                        "geometry" : {
                            "rings" : shape_array,
                            "spatialReference" : { "wkid" : self._config.wkid }
                        },
                        "attributes" : {
                            "OID" : 1,
                            "AREA_ID" : "42",
                            "STORE_ID" : "42",
                            "RING" : 1,
                            "RING_DEFN" : "Shape ID 42",
                            "AREA_DESC" : "Trade Area for Shape 42"
                        }
                    }
                ]
            }
        }

        report_options = json.dumps(self.__generate_gp1_report_options(override_template), cls=APIEncoder)

        ESRI_request = {
            "boundaries": json.dumps(boundaries).replace(" ", ""),
            "outputtype": "GetReport;",
            "reportoptions": report_options,
            "f": "JSON"
        }

        return self._gis_conn.generate_report(ESRI_request, self._config.give_shape_get_demographics_url)

    ######################################## GP17 methods ###################################

    def __generate_drive_time_shape_request_format(self, latitude, longitude, minutes, minutes_threshold):
        point = {
            "longitude": longitude,
            "latitude": latitude,
            "storeID": 123
        }
        wrapped_point = self.__wrap_point(point)

        result =  {
            'Stores': json.dumps(wrapped_point, cls=APIEncoder),
            'CreateDetailedBorder': 'true',
            'Radii': str(minutes),
            'DistanceUnits': 'esriDriveTimeUnitsMinutes',
            'ActiveDatasetID': self._config.dataset_id,
            'OutputSpatialReference': '{"wkid": %s}' % self._config.wkid,
            # This parameter must be set to true and must exist
            'DetailedDriveTimes': 'true',
            'OutputType': 'GetFeatureClass',
            'f': 'JSON'
        }

        if minutes_threshold and float(minutes) > minutes_threshold:
            result['CreateDetailedBorder'] = 'false'

        return result

    def get_drive_time_shape(self, latitude, longitude, minutes, minutes_threshold):
        return self._gis_conn.generate_report(
                            self.__generate_drive_time_shape_request_format(latitude, longitude, minutes, minutes_threshold),
                            self._drive_time_url)


    ######################################## GP18 methods ###################################
    def get_store_customer_folder_item(self, item_name):
        return {
            "workspaceName": self._config.retailer_workspace,
            "projectName": self._config.store_customer_project,
            "folderType": "esriFolderTradeAreas",
            "itemName": item_name
        }

    def __convert_customers_to_recordset_format(self, customers):

        if not customers:
            customer_geometry_features = []

        elif isinstance(customers[0], dict):
            customer_geometry_features = [
                self.__convert_customer_point_to_geometry_feature(c["latitude"], c["longitude"], c.get("sales"))
                for c in customers
            ]

        # customer is an array
        else:
            if len(customers[0]) == 3:
                customer_geometry_features = [
                    self.__convert_customer_point_to_geometry_feature(c[1], c[0], c[2])
                    for c in customers
                ]
            else:
                customer_geometry_features = [
                    self.__convert_customer_point_to_geometry_feature(c[1], c[0])
                    for c in customers
                ]

        return {
            "RecordSet" : {
                "geometryType" : "esriGeometryPoint",
                "spatialReference" : { "wkid" : 4326 },
                "features" : customer_geometry_features
            }
        }


    def __convert_customer_point_to_geometry_feature(self, latitude, longitude, sales=None, store_id = "1"):
        geometry_feature = {
            "geometry": {
                "x": longitude,
                "y": latitude
            },
            "attributes": {
                "STORE_ID": store_id,
            }
        }

        if sales is not None:
            geometry_feature["attributes"]["SALES"] = sales

        return geometry_feature


    def __generate_customer_derived_shape_request_format(self, latitude, longitude, customers, item_name, percentages, cutoff, weight_field):
        store = {
            "longitude": longitude,
            "latitude": latitude,
            "storeID": "1"
        }
        wrapped_store_point = self.__wrap_point(store)

        if customers:
            customers_parameter = self.__convert_customers_to_recordset_format(customers)
        elif item_name:
            customers_parameter = {
            "Item": self.get_store_customer_folder_item(item_name)
        }
        else:
            raise Exception('Either customers or item_name must be provided to run GP18')

        request_format = {
            'Stores': json.dumps(wrapped_store_point, cls=APIEncoder),
            'CustomerLinkField': "STORE_ID", # I tried storeID first, it didn't work... whatevs
            'Customers': json.dumps(customers_parameter, cls=APIEncoder),
            'Percentages': percentages,
            'CutOffDistance': cutoff["distance"],
            'CutOffUnits': cutoff["units"],
            'UseCustomersCentroid': False,
            'HullType': "Detailed", # Note, changing this to Simple seems to cause MongoDB to raise invalid polygon errors
            'ActiveDatasetID': self._config.dataset_id,
            'OutputSpatialReference': '{"wkid": %s}' % self._config.wkid,
            'OutputType': 'GetFeatureClass',
            'f': 'JSON'
        }

        if weight_field:
            request_format["CustomerWeightField"] = weight_field

        return request_format


    def get_customer_derived_shape(self, latitude, longitude, customers, item_name, percentages, cutoff, weight_field):
        return self._gis_conn.generate_report(
                            self.__generate_customer_derived_shape_request_format(latitude, longitude, customers,
                                                                                  item_name, percentages, cutoff, weight_field),
                            self._customer_derived_url)


    ######################################## GP19 methods ###################################

    def generate_customers_feature_set(self, item_name, customers):
        # Create a point layer
        customers_recordset = self.__convert_customers_to_recordset_format(customers)

        # create the esriFolderItem for the Feature Set
        folder_item = self.get_store_customer_folder_item(item_name)

        return  {
            "FeatureSet": json.dumps(customers_recordset, cls=APIEncoder),
            "OutputAnalysisItem": json.dumps(folder_item, cls=APIEncoder),
            'f': 'JSON'
        }

    def upload_feature_set(self, item_name, customers):

        # Not really generating a report...
        return self._gis_conn.generate_report(
                            self.generate_customers_feature_set(item_name, customers),
                            self._upload_feature_set_url)

