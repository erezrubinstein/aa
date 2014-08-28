import datetime
from mox import IsA
from werkzeug.datastructures import FileStorage
from common.service_access.utilities.json_helpers import APIEncoder_New
from core.service.svc_main.implementation.service_endpoints.endpoint_helpers.retailer_helpers.csv_file_uploader import CsvFileUploader
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.utilities.errors import BadRequestError, ForbiddenError, ServiceError
from core.common.utilities.helpers import generate_id
import mox
import unittest


__author__ = 'imashhor'


class RetailerCsvFileUploaderTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RetailerCsvFileUploaderTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get several dependencies that we'll need in the class
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(CsvFileUploader)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.wfs = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.as_of_date = "today"
        self.mock.retailer_client_id = "client id"

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_retailer_customer_file_uploader.py",
                        "user": {"user_id": 1 }}

        self.mock.context = self.context

    def doCleanups(self):

        super(RetailerCsvFileUploaderTests, self).doCleanups()
        dependencies.clear()


    def test_validate_request_file__invalid_files_dict(self):

        uploader = CsvFileUploader.__new__(CsvFileUploader)
        uploader.logger = self.mock.logger
        uploader.request_files = None
        self.assertRaises(BadRequestError, uploader._validate_file_object)

        uploader.request_files = {}
        self.assertRaises(BadRequestError, uploader._validate_file_object)

        uploader.request_files = {"asdf": "asdf"}
        self.assertRaises(BadRequestError, uploader._validate_file_object)


    def test_validate_file_object(self):

        filename = "some_file.xls"
        file_obj = self.mox.CreateMockAnything()
        files = {filename: file_obj}

        self.mox.ReplayAll()
        self.mock.request_files = files

        result = CsvFileUploader._validate_file_object(self.mock)


    def test_validate_file_format__bad_csv(self):
        # Mock the file object
        mock_customer_file = self.mox.CreateMockAnything()

        def to_str():
            return str("bad to teh bone -- yes the teh is intentional.csv")

        mock_customer_file.__str__ = to_str

        # Its "space delimited"
        bad_contents = """dfsdsdgasd, asd, asd
xxx, xxx, xxx
"""

        mock_customer_file.read(100000).AndReturn(bad_contents)
        mock_customer_file.seek(0)

        self.mock.logger.error("File %s is not a valid tab-delimited file.\nFirst Row: %s\nError: %s" % (mock_customer_file, bad_contents, IsA(basestring)))

        self.mox.ReplayAll()
        self.mock.uploaded_file = mock_customer_file

        self.assertRaises(BadRequestError, CsvFileUploader._validate_csv_file_format, *(self.mock,))


    def test_validate_file_format__good_csv(self):
        # Mock the file object
        mock_customer_file = self.mox.CreateMockAnything()
        good_contents = """cat\tdog\tchicken
1\t2\t3
x\ta\tz
"""

        mock_customer_file.read(100000).AndReturn(good_contents)
        mock_customer_file.seek(0)

        self.mox.ReplayAll()
        self.mock.uploaded_file = mock_customer_file

        result = CsvFileUploader._validate_csv_file_format(self.mock)


    def test_upload_retail_input_file__bad_request_error(self):

        # Setup test file
        test_filename = u"customer_list_Oct_2013.xls"
        customer_file = self.mox.CreateMockAnything()

        def to_str():
            return str(test_filename)

        customer_file.__str__ = to_str
        customer_file.filename = test_filename

        # Setup mock main access call
        add_file_args = {
            test_filename: customer_file
        }

        self.mock.upload_entity_type = "customer"

        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn("utc")

        additional_data = {
            "retailer_entity_type": self.mock.upload_entity_type,
            "retailer_client_id": self.mock.retailer_client_id,
            "as_of_date": self.mock.as_of_date,
            "file_format": "zip",
            "upload_result": {
                "status": "queued",
                "status_date": "utc"
            }
        }

        self.mock.main_access.call_add_files("retailer/csv_files/{0}/customer/".format(self.mock.retailer_client_id), self.context, add_file_args,
                                             file_entity_type='retailer_file',
                                             additional_data=additional_data,
                                             json_encoder=APIEncoder_New,
                                             resource="file/new_new").AndReturn({})
        self.mock.uploaded_file = customer_file
        self.mock.logger.error("Service failed to save file %s. Additional Data: %s" % (self.mock.uploaded_file, additional_data))
        self.mock.uploaded_file_format = "zip"

        self.mox.ReplayAll()

        # Run and validate
        self.assertRaises(BadRequestError, CsvFileUploader._upload_file, *(self.mock,))

    def test_upload_retail_input_file(self):

        # Setup test file
        test_filename = u"customer_list_Oct_2013.xls"
        customer_file = self.mox.CreateMockAnything()
        customer_file.filename = test_filename

        # Setup mock main access call
        add_file_args = {
            test_filename: customer_file
        }

        test_mds_file_id = generate_id()
        add_file_result = {
            u"retailer/csv_files/{0}/customer/{1}".format(self.mock.retailer_client_id, test_filename): test_mds_file_id
        }
        self.mock.upload_entity_type = "customer"

        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn("utc")

        additional_data = {
            "retailer_entity_type": self.mock.upload_entity_type,
            "retailer_client_id": self.mock.retailer_client_id,
            "as_of_date": self.mock.as_of_date,
            "file_format": "zip",
            "upload_result": {
                "status": "queued",
                "status_date": "utc"
            }
        }

        self.mock.main_access.call_add_files("retailer/csv_files/{0}/customer/".format(self.mock.retailer_client_id), self.context, add_file_args,
                                             file_entity_type='retailer_file',
                                             additional_data=additional_data,
                                             json_encoder=APIEncoder_New,
                                             resource="file/new_new").AndReturn(add_file_result)

        self.mock.uploaded_file = customer_file
        self.mock.uploaded_file_format = "zip"

        self.mox.ReplayAll()

        # Run function
        result = CsvFileUploader._upload_file(self.mock)

        self.assertEqual(test_mds_file_id, self.mock.mds_file_id)


if __name__ == '__main__':
    unittest.main()