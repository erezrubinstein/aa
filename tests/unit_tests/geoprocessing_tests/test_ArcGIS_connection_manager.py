import unittest

from geoprocessing.helpers.ArcGIS_connection_manager import ArcGISConnectionManager, RoundRobinRoutingAlgorithm
from geoprocessing.business_logic.config import Config
from common.utilities.inversion_of_control import dependencies
from common.utilities.Logging.log_manager import LogManager
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockRestProvider


__author__ = 'erezrubinstein'


class MyTestCase(unittest.TestCase):
    def setUp(self):
        # register dependencies
        self._config = Config().instance
        dependencies.register_dependency("Config", self._config)
        self.__rest_provider = MockRestProvider()
        dependencies.register_dependency("RestProvider", self.__rest_provider)
        # adding a super high level so that it doesn't output errors from unit tests
        logger = LogManager(10000)
        dependencies.register_dependency("LogManager", logger)

        # create new manager
        self.manager = ArcGISConnectionManager.instance = None
        self.manager = ArcGISConnectionManager().instance

        # set up timeouts and error limits
        self.manager.max_timeouts = 5
        # max error should be bigger than timeouts to make sure the ip is not removed
        self._config.ArcGIS_max_errors = 10

    def doCleanups(self):
        # erase singleton instance
        ArcGISConnectionManager.instance = None
        # clean up dependencies
        dependencies.clear()




##################################################################################################################
############################################ Routing Algorithm Tests #############################################
##################################################################################################################

    def test_round_robin_algorithm(self):
        # create several test ip addresses
        self.manager.routing_algorithm = RoundRobinRoutingAlgorithm(
                ['1.1.1.1', '2.2.2.2', '3.3.3.3']
            )
        # reset index to zero, so that we know where it starts
        self.manager.routing_algorithm._current_index = 0

        # make sure manager iterates through ips correctly
        conn = self.manager.get_connection()
        self.assertEqual(conn._server_ip_address, '1.1.1.1')
        conn = self.manager.get_connection()
        self.assertEqual(conn._server_ip_address, '2.2.2.2')
        conn = self.manager.get_connection()
        self.assertEqual(conn._server_ip_address, '3.3.3.3')

        # make sure the round robin knows how to "turn around"
        conn = self.manager.get_connection()
        self.assertEqual(conn._server_ip_address, '1.1.1.1')


    def test_round_robin_algorithm_random_current_index(self):
        """
        This tests that the current index is selected randomly.
        It's important so that it works properly when run in different processes
        """
        index = 0
        uses_different_indexes = False

        # create several test ip addresses
        for i in range(0,1000):
            routing_algorithm = RoundRobinRoutingAlgorithm(
                ['1.1.1.1', '2.2.2.2', '3.3.3.3']
            )

            if index != routing_algorithm._current_index:
                uses_different_indexes = True

        self.assertTrue(uses_different_indexes)





##################################################################################################################
############################################## Download File Tests ###############################################
##################################################################################################################
    def test_connection_download_file_relative_path(self):
        """
        this test makes sure that the connection object is able to construct the download URL correctly
        """
        # download fake file
        conn = self.manager.get_connection()
        conn.download_file("/testurl/test.xml")

        # make sure url was constructed correctly
        self.assertRegexpMatches(self.__rest_provider.url, "http://[a-zA-Z0-9.-]+/arcgis/testurl/test.xml")

    def test_connection_download_file_absolute_path(self):
        """
        this test makes sure that if an absolute url is passed in, it's not replaced
        """
        # download fake file
        conn = self.manager.get_connection()
        url = 'http://1.1.1.1/testurl/test.xml'
        conn.download_file(url)

        # make sure url was constructed correctly
        self.assertEqual(self.__rest_provider.url, url)





##################################################################################################################
############################################# Generate Report Tests ##############################################
##################################################################################################################

    def test_generate_report(self):
        self.__rest_provider.post_response = "test arcgisoutput"
        conn = self.manager.get_connection()

        # make request and assert response
        response = conn.generate_report("test request", "/testreport")

        self.assertEqual(response.text, "test arcgisoutput")
        self.assertRegexpMatches(response.url, "http://[a-zA-Z0-9.-]+/arcgis/testreport")
        self.assertEqual(response.request, "test request")



    def test_generate_report_no_infinite_loop(self):
        conn = self.manager.get_connection()
        self.__rest_provider.post_response = "error"

        # get length of ip addresses before to make sure they're not removed in the loop
        len_ip_addresses = len(self.manager.ip_addresses)

        #send request
        error_happened = False
        try:
            conn.generate_report("test", "test")
        except:
            error_happened = True

        self.assertTrue(error_happened)
        # make sure ip address was not removed with regular error
        self.assertEqual(len(self.manager.ip_addresses), len_ip_addresses)


    def test_generate_report_timeout_limit_removes_ip_address(self):

        # create new connection
        conn = self.manager.get_connection()

        # mock up timeout error
        self.__rest_provider.post_response = "Request timed out"

        # get length of ip addresses before to make sure they're removed in the loop
        len_ip_addresses = len(self.manager.ip_addresses)

        #send request
        error_happened = False
        try:
            conn.generate_report("test", "test")
        except Exception as e:
            error_happened = True
            error_message = str(e)

        # make sure ip address was removed
        self.assertTrue(error_happened)
        self.assertEqual(len(self.manager.ip_addresses), len_ip_addresses - 1)
        self.assertIn("Timeout limit exceeded.  Removing ip address", error_message)



    def test_generate_report_timeout_limit__without_removing_ip_address(self):

        # make sure config is set to not allow removing ips
        ArcGISConnectionManager().instance.remove_server_after_max_timeouts = False

        # create new connection
        conn = self.manager.get_connection()

        # mock up timeout error
        self.__rest_provider.post_response = "Request timed out"

        # get length of ip addresses before to make sure they're removed in the loop
        len_ip_addresses = len(self.manager.ip_addresses)

        #send request
        error_happened = False
        try:
            conn.generate_report("test", "test")
        except Exception as e:
            error_happened = True
            error_message = str(e)

        # make sure ip address was NOT removed
        self.assertTrue(error_happened)
        self.assertEqual(len(self.manager.ip_addresses), len_ip_addresses)
        self.assertEqual("Timeout limit exceeded.", error_message)


    def test_generate_report_with_no_ips_left(self):
        # mock up ip addresses to make sure it works if config changes to multiple servers
        self.manager.ip_addresses = ['1.1.1.1']
        self.manager.routing_algorithm = RoundRobinRoutingAlgorithm(
            ['1.1.1.1']
        )
        self.manager._timeout_count['1.1.1.1'] = 0


        conn = self.manager.get_connection()
        # mock up timeout error
        self.__rest_provider.post_response = "Request timed out"

        # get length of ip addresses before to make sure they're removed in the loop
        len_ip_addresses = len(self.manager.ip_addresses)

        # loop until enough timeouts remove the conection
        error_happened = False
        try:
            conn.generate_report("test", "test")
        except Exception as e:
            pass

        # go again and verify that you get a "no ip addresses left" exception
        try:
            self.manager.get_connection()
        except Exception as e:
            error_happened = True
            error_message = str(e)

        self.assertTrue(error_happened)
        self.assertIn("No more ip addressees left!!!", error_message)


    def test_generate_report_successful_response_resets_timeout_counter(self):
        # mock up timeout error
        self.__rest_provider.post_response = "Request timed out"

        # set the max errors to be less that the timeouts, so that the ip is not removed
        self._config.ArcGIS_max_errors = 3

        # generate a report, which should fail with a 'too many requests' error
        conn = self.manager.get_connection()
        try:
            conn.generate_report("test", "test")
        except Exception as e:
            error_message = str(e)

        # verify that there was a 'too many requests' error
        self.assertIn("too many requests", error_message)
        self.assertEqual(self.manager._timeout_count[conn._server_ip_address], 4)



        # reset the mock to be a successful request
        self.__rest_provider.post_response = "test arcgisoutput"

        # generate a report, which should fail with a 'too many requests' error
        conn = self.manager.get_connection()
        conn.generate_report("test", "test")

        # verify that there was a 'too many requests' error
        self.assertEqual(self.manager._timeout_count[conn._server_ip_address], 0)

        # run another test, and make sure the timeout count is reset to 0


if __name__ == '__main__':
    unittest.main()
