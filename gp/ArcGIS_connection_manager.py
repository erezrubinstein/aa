from random import randint
from threading import Lock
import traceback
from common.utilities.inversion_of_control import Dependency, HasMethods, HasAttributes

__author__ = 'erezrubinstein'

class ArcGISConnectionManager(object):
    """
    This is a singleton ArcGIS Connection Manager.
    It is in-charge of doing load balancing between a set of servers.
    """

    # static members
    instance = None
    __singleton_lock = Lock()

    def __init__(self):
        # singleton check and set up
        with self.__singleton_lock:
            if ArcGISConnectionManager.instance is None:
                # set local config values
                self._log = Dependency("LogManager").value
                config = Dependency("Config", HasAttributes("ArcGIS_server_ips", "ArcGIS_max_timeouts")).value
                self.ip_addresses = config.ArcGIS_server_ips[:]
                self.max_timeouts = config.ArcGIS_max_timeouts
                self.remove_server_after_max_timeouts = config.ArcGIS_remove_server_after_max_timeouts

                # keep the algorithm in a class, which makes it easier to exchange
                self.routing_algorithm = RoundRobinRoutingAlgorithm(self.ip_addresses)

                # variables for registering errors and timeouts per ip
                self._timeout_count = {}
                for ip_address in config.ArcGIS_server_ips:
                    self._timeout_count[ip_address] = 0

                # singleton instantiation
                ArcGISConnectionManager.instance = self


    def register_timeout(self, ip_address):
        """
        This registers and increments a time out count per ip.  It removes IPs from the list that have "too many" timeouts
        """
        self._timeout_count[ip_address] += 1

        # if there are more time outs, than allowed, remove the ip and re-create the round robin
        if self._timeout_count[ip_address] > self.max_timeouts:

            # if we allow removing ips, after certain timeouts, remove the ips and reset the routing algorithm
            if self.remove_server_after_max_timeouts:

                self.ip_addresses.remove(ip_address)
                self.routing_algorithm = RoundRobinRoutingAlgorithm(self.ip_addresses)
                message = "Timeout limit exceeded.  Removing ip address (%s)." % ip_address
                self._log.critical(message)

            else:

                message = "Timeout limit exceeded."

            # raise exception to exit from after removing the ip
            raise Exception(message)


    def reset_timeout_count_on_successful_connection(self, ip_address):
        """
        This method should be called on a successful call, which would then reset the timeout counter.
        It's used to signal that everything seems to be OK now
        """
        self._timeout_count[ip_address] = 0


    def get_connection(self):
        ip_address = self.routing_algorithm.get_next_ip_address()
        return ArcGISConnection(ip_address)


class ArcGISConnection(object):
    """
    This class is in charge of keeping track of an ArcGIS server and making calls to it
    """

    def __init__(self, server_ip_address):
        self._rest_provider = Dependency("RestProvider", HasMethods("download_file")).value
        self._config = Dependency("Config", HasAttributes("ArcGIS_timeout", "ArcGIS_max_errors")).value
        self._logger = Dependency("LogManager", HasMethods("error")).value
        self._server_ip_address = server_ip_address
        self._timeout = self._config.ArcGIS_timeout
        self._max_error_count = self._config.ArcGIS_max_errors

    def download_file(self, url):

        try:

            # append the server ip to the url
            url = self._append_ip_address_to_url(url)

            # download the file
            return self._rest_provider.download_file(url)

        except Exception as ex:

            # this has been timing out a lot, so I'm adding some logging...
            self._logger.critical("Exception on ESRI Server: " % str(self._server_ip_address))
            self._logger.critical(str(ex))
            self._logger.critical(traceback.format_exc())
            raise

    def generate_report(self, request_format, url):
        # append the server ip to the url
        url = self._append_ip_address_to_url(url)

        # the ArcGIS server has weird errors. This ensures that we loop several times until a good response is returned
        successful_response = False
        request_counter = 0
        response = None

        while not successful_response:

            # try to get the request and handle errors properly (so that we can retry)
            try:
                response = self._rest_provider.make_post_request(url, request_format, time_out = self._timeout)

            except Exception as e:
                # if there's an error, log it and try again
                response = None
                error_text = str(e)
                self._logger.critical("error send ArcGIS report (exception): %s" + str(error_text))

                # if it's a timeout, register the server ip address, so that it keeps count
                # treat token required as a time out, so that those servers are taken out of the pool
                if "Request timed out" in error_text or "timeout" in error_text or "Token Required" in error_text:
                    ArcGISConnectionManager.instance.register_timeout(self._server_ip_address)

            # once we get a response back, check it's type
            if response is not None:

                # this signals a successful response
                gp19_success_response_text = '{"paramName":"OutputStatus","dataType":"GPBoolean","value":true}'
                if response.text.find('arcgisoutput') != -1 or response.text.find('stops') != -1 \
                    or response.text.find("rings") != -1 or response.text.find(gp19_success_response_text) != -1:

                    # mark for exit and reset the timeout count
                    successful_response = True
                    ArcGISConnectionManager.instance.reset_timeout_count_on_successful_connection(self._server_ip_address)

                # if it's a timeout, register the server ip address
                # treat token required as a time out, so that those servers are taken out of the pool
                elif "Request timed out" in response.text or "timeout" in response.text or "Token Required" in response.text:
                    ArcGISConnectionManager.instance.register_timeout(self._server_ip_address)
                elif 'No solution found.' in response.text and 'useHierarchy' in request_format and request_format['useHierarchy'] == 'true':
                    request_format['useHierarchy'] = 'false'
                else:
                    self._logger.critical("error send ArcGIS report (no arcgisoutput): %s" + response.text)

            else:
                self._logger.critical("error send ArcGIS report (response is None)")

            if request_counter >= self._max_error_count:
                raise Exception('too many requests - %s' % url)

            # increment the request counter
            request_counter += 1

        return response

    def _append_ip_address_to_url(self, url):
        if url is not None and url[:4] != 'http':
            url = ''.join(['http://', self._server_ip_address, '/arcgis', url])
        return url



##################################################################################################################
################################################# Routing Algorithms #############################################
##################################################################################################################

class RoundRobinRoutingAlgorithm(object):
    """
    This is a class to represent the RoundRobin routing algorithm.
    It uses the strategy pattern in case we ever need to develop a smarter algorithm
    """
    def __init__(self, ip_addresses):
        self.__ip_addresses = ip_addresses
        self.__get_next_ip_address_lock = Lock()
        # the current index needs to be generated randomly.
        # this will assure that this works ok when different processes use it concurrently
        if len(ip_addresses) > 0:
            self._current_index = randint(0, len(ip_addresses) - 1)


    def get_next_ip_address(self):
        if not self.__ip_addresses or len(self.__ip_addresses) <=0:
            raise Exception("No more ip addressees left!!!")

        # lock for thread safety
        with self.__get_next_ip_address_lock:
            # get ip address
            ip_address = self.__ip_addresses[self._current_index]

            # move index
            if self._current_index == len(self.__ip_addresses) - 1:
                self._current_index = 0
            else:
                self._current_index += 1

            return ip_address



