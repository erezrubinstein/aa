__author__ = 'erezrubinstein'

# TODO Can't move this to common.helpers.mock_providers in its current form, too GP-specific

class MockRestProvider(object):
    def __init__(self):
        self.post_response = None
        self.get_ASP_response = u'''<?xml version="1.0" encoding="utf-8"?>
            <Report>
              <ReportTitle />
              <ReportTitle2>Custom Title</ReportTitle2>
              <ReportName>Nexus Age by Sex Report</ReportName>
              <TemplateName>Nexus Age by Sex Report</TemplateName>
              <Areas>
                <Area>
                  <ReportItem name="RING" caption="" value="1" />
                  <ReportItem name="TOTPOP_CY" caption="2055 Total Population" value="2.2" />
                  <ReportItem name="PCI_CY" caption="PCI" value="2" />
                  <ReportItem name="ROB" caption="MALE 18-25" value="1010101010" />
               </Area>
              </Areas>
            </Report>'''
        self.get_DIR_response = u'''<?xml version="1.0" encoding="utf-8"?>
            <Report>
              <ReportTitle />
              <ReportTitle2>Custom Title</ReportTitle2>
              <ReportName>Demographic and Income Profile</ReportName>
              <TemplateName>Demographic and Income Profile</TemplateName>
              <Areas>
                <Area>
                  <ReportItem name="RING" caption="" value="1" />
                  <ReportItem name="TOTPOP_CY" caption="2055 Total Population" value="2.2" />
                  <ReportItem name="PCI_CY" caption="PCI" value="2" />
                  <ReportItem name="ROB" caption="MALE 18-25" value="1010101010" />
                </Area>
              </Areas>
            </Report>'''
        self.download_drive_times_response = u'''<?xml version="1.0" encoding="utf-8"?>
            <Report>
              <ReportInfo>
                <ReportTitle>Locator Report</ReportTitle>
                <ReportName>Locator Report</ReportName>
                <TemplateName>LocatorP</TemplateName>
                <ReportType>PointAndMarketBased</ReportType>
                <ReportTitle2 />
              </ReportInfo>
              <Areas>
                <Area>
                  <ReportItem name="ID" caption="ID" value="43" />
                  <ReportItem name="NAME" caption="NAME" value="43" />
                  <ReportItem name="LOCATOR1" caption="LOCATOR1" value="44" />
                  <ReportItem name="LOCATOR2" caption="LOCATOR2" value="44" />
                  <ReportItem name="LOCATOR3" caption="LOCATOR3" value="41.10" />
                  <ReportItem name="LOCATOR4" caption="LOCATOR4" value="-73.54" />
                  <ReportItem name="LOCATOR5" caption="LOCATOR5" value="1347901" />
                  <ReportItem name="LOCATOR6" caption="LOCATOR6" value=" " />
                  <ReportItem name="DISTANCE" caption="DISTANCE" value="6.05" />
                  <ReportItem name="DIRECTION" caption="DIRECTION" value="NE" />
                </Area>
                <Area>
                  <ReportItem name="ID" caption="ID" value="43" />
                  <ReportItem name="NAME" caption="NAME" value="43" />
                  <ReportItem name="LOCATOR1" caption="LOCATOR1" value="45" />
                  <ReportItem name="LOCATOR2" caption="LOCATOR2" value="45" />
                  <ReportItem name="LOCATOR3" caption="LOCATOR3" value="37.21" />
                  <ReportItem name="LOCATOR4" caption="LOCATOR4" value="-80.40" />
                  <ReportItem name="LOCATOR5" caption="LOCATOR5" value="1347884" />
                  <ReportItem name="LOCATOR6" caption="LOCATOR6" value=" " />
                  <ReportItem name="DISTANCE" caption="DISTANCE" value="5.06" />
                  <ReportItem name="DIRECTION" caption="DIRECTION" value="NE" />
                </Area>
                <Area>
                  <ReportItem name="ID" caption="ID" value="43" />
                  <ReportItem name="NAME" caption="NAME" value="43" />
                  <ReportItem name="LOCATOR1" caption="LOCATOR1" value="N/A" />
                  <ReportItem name="LOCATOR2" caption="LOCATOR2" value="N/A" />
                  <ReportItem name="LOCATOR3" caption="LOCATOR3" value="37.21" />
                  <ReportItem name="LOCATOR4" caption="LOCATOR4" value="-80.40" />
                  <ReportItem name="LOCATOR5" caption="LOCATOR5" value="N/A" />
                  <ReportItem name="LOCATOR6" caption="LOCATOR6" value=" " />
                  <ReportItem name="DISTANCE" caption="DISTANCE" value="-1" />
                  <ReportItem name="DIRECTION" caption="DIRECTION" value="NE" />
                </Area>
              </Areas>
            </Report>
        '''


    def make_post_request(self, url, request, time_out=10.0):
        return MockResponse(self.post_response, url, request, time_out)

    def make_get_request(self, url, request):
        if 'ASP' in url:
            return MockResponse(self.get_ASP_response, url, request)
        elif 'DIR' in url:
            return MockResponse(self.get_DIR_response, url, request)
        else:
            return MockResponse(self.get_DIR_response, url, request)

    def download_file(self, url):
        self.url = url
        if 'reverseGeocode' in url:
            return ''' {
                         "address": {
                          "Address": "Koopa Castle",
                          "City": "Woot Land",
                          "State": "Rob's Desk",
                          "Zip": "07029",
                          "Loc_name": "Address_Points"
                         },
                         "location": {
                          "x": -73.59507144859532,
                          "y": 41.040104683909931,
                          "spatialReference": {
                           "wkid": 4326,
                           "latestWkid": 4326
                          }
                         }
                        } '''
        if 'google' in url and 'geocode' in url:
            return '''{
                           "results" : [
                              {
                                 "address_components" : [
                                    {
                                       "long_name" : "600",
                                       "short_name" : "600",
                                       "types" : [ "street_number" ]
                                    },
                                    {
                                       "long_name" : "Koopa Castle",
                                       "short_name" : "Koopa Castle",
                                       "types" : [ "route" ]
                                    },
                                    {
                                       "long_name" : "Woot Land",
                                       "short_name" : "Woot Land",
                                       "types" : [ "locality", "political" ]
                                    },
                                    {
                                       "long_name" : "Hudson",
                                       "short_name" : "Hudson",
                                       "types" : [ "administrative_area_level_2", "political" ]
                                    },
                                    {
                                       "long_name" : "Rob's Desk",
                                       "short_name" : "Rob's Desk",
                                       "types" : [ "administrative_area_level_1", "political" ]
                                    },
                                    {
                                       "long_name" : "United States",
                                       "short_name" : "US",
                                       "types" : [ "country", "political" ]
                                    },
                                    {
                                       "long_name" : "07029",
                                       "short_name" : "07029",
                                       "types" : [ "postal_code" ]
                                    }
                                 ]
                                 }
                                 ]
                                 }'''


        if 'ASP' in url:
            return self.get_ASP_response
        elif 'DIR' in url:
            return self.get_DIR_response
        elif 'LocatorReport' in url:
            return self.download_drive_times_response
        else:
            return self.get_DIR_response

class MockResponse(object):
    def __init__(self, text, url, request, time_out=10.0):
        self.text = text
        self.url = url
        self.request = request
        self.time_out = time_out