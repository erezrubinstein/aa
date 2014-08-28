import datetime
import mox
import re
import redis
from requests.models import Response
from common.helpers import signal_quote_generator, sysadmin_helper
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency
from infrastructure.monitoring.retail_mds_monitor import RetailMDSMonitor

__author__ = 'erezrubinstein'

class TestRetailMDSMonitor(mox.MoxTestBase):

    def setUp(self):

        # call setUp on super class
        super(TestRetailMDSMonitor, self).setUp()

        # register mox dependencies
        register_common_mox_dependencies(self.mox)

        # get mock dependencies that we need to use for recording
        self.mock_rest_provider = Dependency("RestProvider").value
        self.mock_email_provider = Dependency("EmailProvider").value
        
        # helper vars
        self.stats_url = "http://localhost:5001/connection_stats"


    def tearDown(self):

        # call tearDown on super class
        super(TestRetailMDSMonitor, self).tearDown()


    def test_initialize(self):
        """
        Verify that initialize sets the correct variables
        """

        monitor = RetailMDSMonitor()
        self.assertEqual(monitor.server_regex, re.compile("^coredata-us-[a-zA-Z][0-9]:27017", re.IGNORECASE))
        self.assertEqual(monitor.connection_stats_url, "http://localhost:5001/connection_stats")
        self.assertEqual(monitor.loops, 10)


    def test_monitor__success(self):

        # create monitor and set loops to 2
        monitor = RetailMDSMonitor()
        monitor.loops = 2

        # create mocks
        mock_response = self.mox.CreateMock(Response)
        mock_response_json = self._get_mock_response_json("CoreData-US-B1:27017")
        mock_cells = [None] * 3296

        # stub out stuff
        self.mox.StubOutClassWithMocks(redis, "StrictRedis")

        # record
        mock_redis_connection = redis.StrictRedis("localhost", port = 6379, db = 0)
        mock_redis_connection.lrange("white_space_cells__SquareMiles50__TOTPOP_CY", 0, -1).AndReturn(mock_cells)
        self.mock_rest_provider.get(self.stats_url).AndReturn(mock_response)
        mock_response.ok = True
        mock_response.json().AndReturn(mock_response_json)
        self.mock_rest_provider.get(self.stats_url).AndReturn(mock_response)
        mock_response.ok = True
        mock_response.json().AndReturn(mock_response_json)

        # replay all
        self.mox.ReplayAll()

        # go!
        status = monitor.monitor()
        self.assertEqual(status, "success")


    def test_monitor__redis_not_loaded(self):

        # create monitor.  Leave loops as if, to make sure it "breaks" out of the loop
        monitor = RetailMDSMonitor()

        # stub out
        self.mox.StubOutWithMock(monitor, "send_redis_down_email")
        self.mox.StubOutClassWithMocks(redis, "StrictRedis")

        # record
        mock_redis_connection = redis.StrictRedis("localhost", port = 6379, db = 0)
        mock_redis_connection.lrange("white_space_cells__SquareMiles50__TOTPOP_CY", 0, -1).AndReturn([])
        monitor.send_redis_down_email()

        # replay all
        self.mox.ReplayAll()

        # go!
        status = monitor.monitor()
        self.assertEqual(status, "failed")


    def test_monitor__wrong_server(self):

        # create monitor.  Leave loops as if, to make sure it "breaks" out of the loop
        monitor = RetailMDSMonitor()

        # get mocks
        mock_response = self.mox.CreateMock(Response)
        mock_response_json = self._get_mock_response_json("CoreData-SG-B1:27017")
        mock_cells = [None] * 3296

        # stub out
        self.mox.StubOutWithMock(monitor, "send_incorrect_server_email")
        self.mox.StubOutClassWithMocks(redis, "StrictRedis")

        # record
        mock_redis_connection = redis.StrictRedis("localhost", port = 6379, db = 0)
        mock_redis_connection.lrange("white_space_cells__SquareMiles50__TOTPOP_CY", 0, -1).AndReturn(mock_cells)
        self.mock_rest_provider.get(self.stats_url).AndReturn(mock_response)
        mock_response.ok = True
        mock_response.json().AndReturn(mock_response_json)
        monitor.send_incorrect_server_email("CoreData-SG-B1:27017")

        # replay all
        self.mox.ReplayAll()

        # go!
        status = monitor.monitor()
        self.assertEqual(status, "failed")


    def test_monitor__response_not_ok(self):

        # create monitor.  Leave loops as if, to make sure it "breaks" out of the loop
        monitor = RetailMDSMonitor()

        # get mocks
        mock_response = self.mox.CreateMock(Response)
        mock_cells = [None] * 3296

        # stub out
        self.mox.StubOutClassWithMocks(redis, "StrictRedis")
        self.mox.StubOutWithMock(monitor, "send_error_email")

        # record
        mock_redis_connection = redis.StrictRedis("localhost", port = 6379, db = 0)
        mock_redis_connection.lrange("white_space_cells__SquareMiles50__TOTPOP_CY", 0, -1).AndReturn(mock_cells)
        self.mock_rest_provider.get(self.stats_url).AndReturn(mock_response)
        mock_response.ok = False
        mock_response.content = "michael_bolton"
        monitor.send_error_email("michael_bolton")

        # replay all
        self.mox.ReplayAll()

        # go!
        status = monitor.monitor()
        self.assertEqual(status, "failed")


    def test_monitor__exception(self):

        # create monitor.  Leave loops as if, to make sure it "breaks" out of the loop
        monitor = RetailMDSMonitor()

        # mock out exception method
        def exception_method(url):
            raise Exception("Woot!")

        # mocks
        mock_cells = [None] * 3296

        # stub out
        self.mox.StubOutClassWithMocks(redis, "StrictRedis")
        self.mox.StubOutWithMock(monitor, "send_error_email")

        # record
        mock_redis_connection = redis.StrictRedis("localhost", port = 6379, db = 0)
        mock_redis_connection.lrange("white_space_cells__SquareMiles50__TOTPOP_CY", 0, -1).AndReturn(mock_cells)
        self.mock_rest_provider.get(self.stats_url).WithSideEffects(exception_method)
        monitor.send_error_email("Woot!")

        # replay all
        self.mox.ReplayAll()

        # go!
        status = monitor.monitor()
        self.assertEqual(status, "failed")


    def test_send_error_email(self):

        # create monitor
        monitor = RetailMDSMonitor()

        # create various mocked/expected values
        mock_date = "1/1/2012"
        error_string = "chicken woot error."
        quote = "arnie quote"
        hostname = "my_computer"
        mock_body = '<br />'.join([
            "Error running Retail MDS Monitor",
            "",
            "Error Timestamp: %s" % mock_date,
            "",
            "Host: %s" % hostname,
            "",
            "Error: ",
            "",
            "",
            error_string,
            "",
            "",
            quote])

        # stub out various things that the email needs
        self.mox.StubOutWithMock(datetime, "datetime")
        self.mox.StubOutWithMock(sysadmin_helper, "get_host_name")
        self.mox.StubOutWithMock(signal_quote_generator, "get_email_quote")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_date)
        sysadmin_helper.get_host_name().AndReturn(hostname)
        signal_quote_generator.get_email_quote("<br />").AndReturn(quote)
        self.mock_email_provider.send_html_email("arnie@nexusri.com", ["engineering@signaldataco.com"], "Retail MDS Monitor Error", mock_body)

        # replay all
        self.mox.ReplayAll()

        # go
        monitor.send_error_email(error_string)


    def test_send_incorrect_server_email(self):

        # create monitor
        monitor = RetailMDSMonitor()

        # create various mocked/expected values
        mock_date = "1/1/2012"
        database = "blah"
        quote = "arnie quote"
        hostname = "my_computer"
        mock_body = '<br />'.join([
            "Retail MDS is pointing at an incorrect database.",
            "",
            "Timestamp: %s" % mock_date,
            "",
            "Host: %s" % hostname,
            "",
            "Database: '%s' did not match regex: '^coredata-us-[a-zA-Z][0-9]:27017'" % database,
            "",
            "",
            quote])

        # stub out various things that the email needs
        self.mox.StubOutWithMock(datetime, "datetime")
        self.mox.StubOutWithMock(sysadmin_helper, "get_host_name")
        self.mox.StubOutWithMock(signal_quote_generator, "get_email_quote")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_date)
        sysadmin_helper.get_host_name().AndReturn(hostname)
        signal_quote_generator.get_email_quote("<br />").AndReturn(quote)
        self.mock_email_provider.send_html_email("arnie@nexusri.com", ["engineering@signaldataco.com"], "Retail MDS Monitor Alert", mock_body)

        # replay all
        self.mox.ReplayAll()

        # go
        monitor.send_incorrect_server_email(database)




    # ------------------------------ Private Helpers ------------------------------ #


    def _get_mock_response_json(self, server_name):

        return {
            "status": {
                "server": server_name
            }
        }