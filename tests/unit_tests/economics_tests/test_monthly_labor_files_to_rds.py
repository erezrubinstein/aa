from economics.raw_data.monthly_us_labor_files_to_rds import LaborBLStoRDS
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from datetime import datetime
import __builtin__
import StringIO
import unittest
import mox
import os
import requests

__author__ = 'clairseager'


class LaborFTPtoRDSTest(mox.MoxTestBase):

    def setUp(self):
        super(LaborFTPtoRDSTest, self).setUp()

        # set up mocks
        register_common_mock_dependencies()
        self.mox.StubOutWithMock(__builtin__, "open")

        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.deployment_provider = Dependency("DeploymentProvider").value
        self.requests = self.mox.CreateMock(requests)
        self.email_provider = Dependency("EmailProvider").value

        # logger
        self.logger = Dependency("SimpleConsole").value

        self.email_recipients = ["taco"]
        self.url = "fake_url.com/fake/directory/"

        self.downloader = LaborBLStoRDS(self.logger, self.email_recipients, rds_directory="/whatevs/data")
        self.downloader.url = self.url
        self.downloader.local_dir = "monty/python/"
        self.downloader.file_name = "TacoDonut"
        self.downloader.zipped_filename = self.downloader.file_name + ".tar.gz"
        self.downloader.rds_path = "holy/grail"
        self.downloader.skip_files_containing = ["Alaska", "footnote"]
        self.downloader.requests = self.requests

    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()

    def test_download_files(self):

        urls, dates = self.downloader.parse_directory_html(mock_html_listing)

        for f in urls:
            if "Alaska" not in f and "footnote" not in f:
                self.requests.get(f).AndReturn(MockRequest())
                fn = self.downloader.local_dir + f.split("/")[-1]
                opf = open(fn, 'w').AndReturn(MockFile())
                opf.write("asdf")

        self.mox.ReplayAll()
        self.downloader.download_files(urls)

        self.assertItemsEqual(self.downloader.saved_files, mock_file_list)
        self.assertNotIn("la.data.Alaska", self.downloader.saved_files)

    def test_upload_to_rds(self):
        # set up a fake file for the mocked open method to return
        f = open(self.downloader.zipped_filename, 'rb').AndReturn(MockFile())
        self.mox.ReplayAll()

        self.downloader.upload_to_rds(datetime.utcnow())

        self.assertDictEqual(self.downloader.response, {"holy/grail/TacoDonut.tar.gz":"fake_object_id"})
        self.assertItemsEqual(self.mock_main_access.rds.files, [(self.downloader.rds_path, self.downloader.file_name + ".tar.gz")])

    def test_send_email_no_exception(self):
        self.downloader.send_email()

        self.assertItemsEqual(self.email_provider.to_email, self.email_recipients)
        self.assertEqual(self.email_provider.from_email, "zoolander@signaldataco.com")
        self.assertEqual(self.email_provider.subject, "Monthly Labor Downloader Succeeded")
        self.assertIn("Monthly Labor Downloader Success!", self.email_provider.message)

    def test_send_email_with_exception(self):
        self.downloader.send_email(exception_message="DANCE IS LIFE")

        self.assertItemsEqual(self.email_provider.to_email, self.email_recipients)
        self.assertEqual(self.email_provider.from_email, "zoolander@signaldataco.com")
        self.assertEqual(self.email_provider.subject, "Monthly Labor Downloader Error!")
        self.assertIn("Monthly Labor Downloader Error!", self.email_provider.message)
        self.assertIn("DANCE IS LIFE", self.email_provider.message)
        self.assertNotIn("DANCE IS LIFF", self.email_provider.message)

    def test_send_email_with_info(self):
        info = {"extra_info": "goes here"}
        self.downloader.response = info
        self.downloader.send_email()

        self.assertItemsEqual(self.email_provider.to_email, self.email_recipients)
        self.assertEqual(self.email_provider.from_email, "zoolander@signaldataco.com")
        self.assertEqual(self.email_provider.subject, "Monthly Labor Downloader Succeeded")
        self.assertIn("Monthly Labor Downloader Success!", self.email_provider.message)
        self.assertIn(str(info), self.email_provider.message)

    def test_run(self):

        r = self.requests.get(self.url).AndReturn(MockRequest())
        r.text = mock_html_listing

        urls, dates = self.downloader.parse_directory_html(mock_html_listing)

        # stub out the call to check for the latest bls file date, and make the file in RDS seem old
        self.mox.StubOutWithMock(self.downloader.main_access.rds, "call_get_latest_in_path")
        mock_response = self.mox.CreateMockAnything()
        def mock_json():
            return {"metadata": {"max_bls_file_date": datetime(1900,1,1)}}
        mock_response.json = mock_json
        self.downloader.main_access.rds.call_get_latest_in_path("/whatevs/data").AndReturn(mock_response)

        self.downloader.get_filenames = lambda x: ("TacoDonut", "monty/python/", "TacoDonut.tar.gz")
        self.downloader.get_filenames(mock_html_listing)

        for f in urls:
            if "Alaska" not in f and "footnote" not in f:
                self.requests.get(f).AndReturn(MockRequest())
                fn = self.downloader.local_dir + f.split("/")[-1]
                opf = open(fn, 'w').AndReturn(MockFile())
                opf.write("asdf")

        f = open(self.downloader.zipped_filename, 'rb').AndReturn(MockFile())

        self.mox.ReplayAll()

        self.downloader.run()

        self.assertItemsEqual(self.email_provider.to_email, self.email_recipients)
        self.assertEqual(self.email_provider.from_email, "zoolander@signaldataco.com")
        self.assertIn(str(self.downloader.response), self.email_provider.message)

        self.assertItemsEqual(self.deployment_provider.deleted_files, ["".join([os.path.expanduser("~/"), i]) for i in ["monty/python", "monty/python.tar.gz"]])
        self.assertEqual(self.deployment_provider.tar_filename, self.downloader.file_name)
        self.assertEqual(self.deployment_provider.tar_zipped_file_name, self.downloader.zipped_filename)

        self.assertItemsEqual(self.downloader.saved_files, mock_file_list)
        self.assertNotIn("la.data.Alaska", self.downloader.saved_files)
        self.assertDictEqual(self.downloader.response, {"holy/grail/TacoDonut.tar.gz":"fake_object_id"})

        self.assertItemsEqual(self.mock_main_access.rds.files, [(self.downloader.rds_path, self.downloader.file_name + ".tar.gz")])


class MockFile():

    def __enter__(self):
        return StringIO.StringIO("Fake File")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def write(self, text):
        pass

class MockRequest():

    text = "asdf"


mock_html_listing = """
<html><head><title>download.bls.gov - /pub/time.series/la/</title></head><body><H1>download.bls.gov - /pub/time.series/la/</H1><hr>

<pre><A HREF="/pub/time.series/">[To Parent Directory]</A><br>
<br>
 3/22/2013  9:27 AM       380154 <A HREF="/pub/time.series/la/la.area">la.area</A><br>
 3/20/2006  4:19 PM          468 <A HREF="/pub/time.series/la/la.area_type">la.area_type</A><br>
 4/15/2005  9:58 AM          316 <A HREF="/pub/time.series/la/la.contacts">la.contacts</A><br>
12/20/2013 10:20 AM     87349704 <A HREF="/pub/time.series/la/la.data.0.CurrentU00-04">la.data.0.CurrentU00-04</A><br>
12/20/2013 10:22 AM     30786564 <A HREF="/pub/time.series/la/la.data.62.Micro">la.data.62.Micro</A><br>
12/20/2013 10:22 AM      6993064 <A HREF="/pub/time.series/la/la.data.63.Combined">la.data.63.Combined</A><br>
12/20/2013 10:23 AM      7130376 <A HREF="/pub/time.series/la/la.data.7.Alabama">la.data.7.Alabama</A><br>
12/20/2013 10:23 AM      2052188 <A HREF="/pub/time.series/la/la.data.8.Alaska">la.data.8.Alaska</A><br>
12/20/2013 10:23 AM      2911688 <A HREF="/pub/time.series/la/la.data.9.Arizona">la.data.9.Arizona</A><br>
  3/1/2013 10:29 AM          973 <A HREF="/pub/time.series/la/la.footnote">la.footnote</A><br>
  3/1/1994  5:41 PM           97 <A HREF="/pub/time.series/la/la.measure">la.measure</A><br>
  11/15/2013  3:12 PM          206 <A HREF="/pub/time.series/la/la.notice">la.notice</A><br>
  3/1/1994  5:41 PM          252 <A HREF="/pub/time.series/la/la.period">la.period</A><br>
  12/20/2013 10:23 AM      1854926 <A HREF="/pub/time.series/la/la.series">la.series</A><br>
 3/10/2005  9:10 AM          818 <A HREF="/pub/time.series/la/la.state_region_division">la.state_region_division</A><br>
 10/17/2007  8:45 AM        16838 <A HREF="/pub/time.series/la/la.txt">la.txt</A><br>
 7/23/2008  4:57 PM        &lt;dir&gt; <A HREF="/pub/time.series/la/maps/">maps</A><br>
</pre><hr></body></html>"""

mock_file_list = [
    'la.area',
    'la.area_type',
    'la.contacts',
    'la.data.0.CurrentU00-04',
    'la.data.62.Micro',
    'la.data.63.Combined',
    'la.data.7.Alabama',
    'la.data.9.Arizona',
    'la.measure',
    'la.period',
    'la.series',
    'la.state_region_division',
    'la.txt',
    'la.notice',
    'maps'
]


if __name__ == '__main__':
    unittest.main()
