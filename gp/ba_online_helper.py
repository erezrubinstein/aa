import json
import pprint
import os
from common.utilities.inversion_of_control import Dependency, HasAttributes

__author__ = 'jsternberg'

"""
Test getting a Business Analyst Online authentication token and using it to request BA Online data.
http://help.arcgis.com/en/businessanalyst/apis/rest/reference/GetToken.html#exampleUsage
https://baoapi.esri.com/rest/authentication
"""

class BAOnlineAuthContext(object):
    """
    A context helper to wrap REST requests to Business Analyst Online.
    BA Online requires authenticating with a username/password, which returns a token.
    This token must be stored and managed on our (client) side, and sent in as a param in subsequent requests.
    """

    # static token so that it can be shared among instances
    token = ""

    def __init__(self):
        # get dependencies
        self.logger = Dependency("LogManager").value
        self.config = Dependency("Config", HasAttributes("ba_online_username", "ba_online_password")).value
        self.rest_provider = Dependency("RestProvider").value

        # get username and password
        self.user_name = self.config.ba_online_username
        self.password = self.config.ba_online_password

        # various internal vars
        self.num_auth_requests = 0


    def __enter__(self):
        self.__get_token()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


    def post(self, url, data):
        #inject token
        self.__log_request(url)
        data.update({ "Token": BAOnlineAuthContext.token })
        return self.rest_provider.post(url, data, 60)


    def get(self, url, params):
        #inject token
        self.__log_request(url)
        params.update({ "Token": BAOnlineAuthContext.token })
        return self.rest_provider.get(url, params, 60)


    def generate_report(self, request_format, url, try_again = True):
        """
        Adaptor method to make this fit into ArcGIS_report_helper.py
        """
        with self:
            response = self.get(url, request_format)

            if not response.ok:
                #inject potentially useful stuff in the response: the url and params
                response.reason += " | url: %s | GET data: %s" % (url, request_format)
                response.raise_for_status()
            else:
                response_rec = response.json()
                if "error" in response_rec:

                    # if try again, get a new token and try again
                    if try_again:
                        BAOnlineAuthContext.token = ""
                        self.__get_token()
                        return self.generate_report(request_format, url, False)

                    # otherwise raise an error
                    raise RuntimeError("BA Online Error - get_report_templates(): %s." % response_rec["error"])

            return response

    #this is being used in GP10, query params get too large with detailed trade areas so need to post
    def generate_report_with_post(self, request_format, url, try_again = True):
        """
        Adaptor method to make this fit into ArcGIS_report_helper.py
        """
        with self:
            response = self.post(url, request_format)

            if not response.ok:
                #inject potentially useful stuff in the response: the url and params
                response.reason += " | url: %s | GET data: %s" % (url, request_format)
                response.raise_for_status()
            else:
                response_rec = response.json()
                if "error" in response_rec:

                    # if try again, get a new token and try again
                    if try_again:
                        BAOnlineAuthContext.token = ""
                        self.__get_token()
                        return self.generate_report_with_post(request_format, url, False)

                    # otherwise raise an error
                    raise RuntimeError("BA Online Error - get_report_templates(): %s." % response_rec["error"])

            return response

    def download_file(self, url):
        """
        Adaptor method to make this fit into ArcGIS_report_helper.py
        """
        self.__log_request(url)
        return self.rest_provider.download_file(url)

    def __log_request(self, url):
        self.logger.info("BAOnline Request: %s" % url)



    def __get_token(self):
        """
        Authenticate with Business Analyst Online.
        docs: http://help.arcgis.com/en/businessanalyst/apis/rest/reference/GetToken.html
        Store the token in a local plain text file, and read it back from that file on subsequent calls.
        Note that we don't have to use a file for storing the token -- if we use a singleton we can keep it in memory.
        Or we could use something like Redis or MongoDB.
        """

        if not BAOnlineAuthContext.token:
            self.logger.debug("BA Online - Getting new token.")

            url = "https://baoapi.esri.com/rest/authentication"
            payload = {"request": "getToken",
                       "username": self.user_name,
                       "password": self.password,
                       "f": "JSON"}

            response = self.post(url, payload)
            self.num_auth_requests += 1

            if not response.ok:
                #inject potentially useful stuff in the response: the url and POST data payload
                response.reason += " | url: %s | POST data: %s" % (url, payload)
                response.raise_for_status()
            else:
                response_rec = response.json()

                if "error" in response_rec:
                    # check for bad password
                    # example: {u'error': u'Invalid user name / password pair.'}
                    if {"Invalid", "user", "password"} <= set(response_rec["error"].split(" ")):
                        # perhaps we could have different error handling if user/pwd is invalid?
                        raise AuthenticationError("BA Online - Authentication Failed! %s | user_name: %s | password: %s",
                                                  response_rec["error"], self.user_name, self.password)
                    else:
                        raise AuthenticationError("BA Online - Authentication Failed! %s." % response_rec["error"])
                else:
                    # example result:
                    # {u'results': {u'token': u'QCU89-M62iADv0TcQ5IP1Ck22sBuqcFxxiv5RSyWMdfPR2X6wFG3kIH8GnvUZQ3e'}}

                    token = response_rec["results"]["token"]
                    self.logger.debug("BA Online - Got new token: %s", token)

                    # save to instance and return
                    BAOnlineAuthContext.token = token


    def __get_datasets(self):
        """
        Returns the list of datasets that we are authorized for in Business Analyst Online.
        An example dataset is "USACensus2010".
        docs: http://help.arcgis.com/en/businessanalyst/apis/rest/reference/GetDatasets.html
        """
        url = "https://baoapi.esri.com/rest/report/GetDatasets"

        params = {"Token": BAOnlineAuthContext.token, "f": "JSON"}

        response = self.post(url, params)

        if not response.ok:
            #inject potentially useful stuff in the response: the url and params
            response.reason += " | url: %s | GET data: %s" % (url, params)
            response.raise_for_status()
        else:
            response_rec = response.json()
            if "error" in response_rec:
                # catch errors like: u'{"error":"(498) Token is invalid."}'
                if {"Token", "invalid."} <= set(response_rec["error"].split(" ")):
                    raise InvalidTokenError("BA Online Error - get_datasets(): %s." % response_rec["error"])
                else:
                    raise RuntimeError("BA Online Error - get_datasets(): %s." % response_rec["error"])
            else:
                datasets = response_rec["Result"]
                return datasets



# ------------------------------------- Custom Errors ------------------------------------- #

class AuthenticationError(Exception):
    pass

class InvalidTokenError(Exception):
    pass




# ------------------------------------ Testing Methods ------------------------------------ #

def test_baonline_auth_context():
    # get logging dependency
    logger = Dependency("LogManager").value

    # this is how it would look in geoprocessing (without the debugs of course
    with BAOnlineAuthContext() as bao:
        logger.info("get, token: %s, num_auth_requests: %s", bao.token, bao.num_auth_requests)
        response = get_report_templates(bao)
        logger.info("templates: %s", pprint.pformat(response))


def get_report_templates(bao):
    """
    Returns the list of report templates that we are authorized for in Business Analyst Online.
    An example report template is "ACS Housing Summary".
    http://help.arcgis.com/en/businessanalyst/apis/rest/reference/GetReportTemplates.html
    """

    url = "https://baoapi.esri.com/rest/report/GetReportTemplates"
    params = {"f": "JSON"}
    response = bao.get(url=url, params = params)

    # this part could be added to auth context as well... might be too much though

    if not response.ok:
        #inject potentially useful stuff in the response: the url and params
        response.reason += " | url: %s | GET data: %s" % (url, params)
        response.raise_for_status()
    else:
        response_rec = response.json()
        if "error" in response_rec:
            raise RuntimeError("BA Online Error - get_report_templates(): %s." % response_rec["error"])
        else:
            templates = response_rec["results"]
            return templates




def get_simple_rings(bao):
    url = "http://baoapi.esri.com/rest/report/SimpleRings"

    stores = {
        "Points": [
            {
                "longitude": -117.183838,
                "latitude": 34.042737,
                "name": 12345,
                "description": 12345,
                "storeID": "12345"
            }
        ],
        "spatialReference": {"wkid":4326}
    }

    params = {
        'Radii': 10,
        'Stores': json.dumps(stores),
        'f': 'JSON',
        'OutputType': 'GetFeatureClass',
        'DistanceUnits': 'esriMiles'
    }

    response = bao.get(url=url, params=params)
    return response.json()

if __name__ == '__main__':
    # do the import here so that we don't have a circular dependency (because this is a dependency)
    from geoprocessing.helpers.dependency_helper import register_concrete_dependencies

    # register dependencies
    register_concrete_dependencies()

    # go!
    test_baonline_auth_context()




