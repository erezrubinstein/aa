from mox import MoxTestBase, Mox, IsA
import unittest
from common.helpers import sysadmin_helper
import socket
import requests
import os

__author__ = 'jsternberg'

class SysadminHelperTests(MoxTestBase):
    def setUp(self):
        # call super init
        super(SysadminHelperTests, self).setUp()

    def tearDown(self):
        super(SysadminHelperTests, self).tearDown()

    def test_module_features(self):
        """If a new function is added to this module, it should be covered by a unit test."""
        methods = sorted([x for x in dir(sysadmin_helper) if not x.startswith("__")])
        expected_methods = ['get_external_dns_name', 'get_external_ip', 'get_file_size', 'get_fqdn', 'get_host_name', 'get_local_ip', 'os', 'requests', 'socket']
        self.assertListEqual(methods, expected_methods)

    def test_get_host_name(self):
        # create stub
        self.mox.StubOutWithMock(socket, "gethostname")

        # start recording
        socket.gethostname().AndReturn("daddymack.local")
        self.mox.ReplayAll()

        # needful
        host_name = sysadmin_helper.get_host_name()
        self.assertEqual(host_name, "daddymack.local")

    def test_get_fqdn(self):
        # create stub
        self.mox.StubOutWithMock(socket, "getfqdn")

        # start recording
        socket.getfqdn().AndReturn("daddymack.andyouknowit.com")
        self.mox.ReplayAll()

        # needful
        host_name = sysadmin_helper.get_fqdn()
        self.assertEqual(host_name, "daddymack.andyouknowit.com")


    def test_get_local_ip(self):
        # create stub
        self.mox.StubOutWithMock(socket, "gethostname")
        self.mox.StubOutWithMock(socket, "gethostbyname")

        # start recording
        socket.gethostname().AndReturn("daddymack.local")
        socket.gethostbyname("daddymack.local").AndReturn("1.2.3.4")
        self.mox.ReplayAll()

        # needful
        local_ip = sysadmin_helper.get_local_ip()
        self.assertEqual(local_ip, "1.2.3.4")

    def test_get_external_ip(self):
        # create stub
        self.mox.StubOutWithMock(requests, "get")
        self.mox.StubOutWithMock(requests, "Response")

        # start recording
        requests.get('http://bot.whatismyipaddress.com', timeout=2).AndReturn(requests.Response)
        requests.Response.content = "999.999.999.999"
        self.mox.ReplayAll()

        # needful
        external_ip = sysadmin_helper.get_external_ip()
        self.assertEqual(external_ip, "999.999.999.999")

    def test_get_external_dns_name(self):
        # create stub
        self.mox.StubOutWithMock(socket, "gethostbyaddr")

        # start recording
        # socket.gethostbyaddr returns a list, from the doc:
        # gethostbyaddr(host) -> (name, aliaslist, addresslist)
        # we are only interested in the first element here
        socket.gethostbyaddr("888.888.888.888").AndReturn(["needful.com", "blah"])
        self.mox.ReplayAll()

        #needful
        external_dns_name = sysadmin_helper.get_external_dns_name("888.888.888.888")
        self.assertEqual(external_dns_name, "needful.com")

    def test_get_file_size(self):

        self.mox.StubOutWithMock(os, "stat")
        mock_stat = self.mox.CreateMockAnything()
        mock_stat.st_size = 1024.0

        # start recording
        os.stat("dummy_file").AndReturn(mock_stat)
        self.mox.ReplayAll()

        # needful
        dummy_size = sysadmin_helper.get_file_size("dummy_file")

        self.assertEqual(dummy_size, 1024.0)

if __name__ == '__main__':
    unittest.main()
