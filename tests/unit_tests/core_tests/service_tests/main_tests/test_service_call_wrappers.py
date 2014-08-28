from common.helpers.statsd_provider import StatsdProvider
from common.service_access.utilities.errors import RecValidationError, RecInputError, RecError, ServiceParamsError, ServiceCallError, ServiceAccessError
from common.utilities.inversion_of_control import dependencies
from core.service.svc_main import main_api
from core.common.utilities.errors       import *
from pymongo.errors                     import ConnectionFailure,\
                                               OperationFailure, \
                                               TimeoutError, \
                                               DuplicateKeyError, \
                                               PyMongoError
from bson.errors                        import BSONError, \
                                               InvalidBSON, \
                                               InvalidStringData, \
                                               InvalidDocument, \
                                               InvalidId
from gridfs.errors                      import UnsupportedAPI, \
                                               FileExists, \
                                               NoFile, \
                                               CorruptGridFile, \
                                               GridFSError

from core.service.svc_main.implementation import cache_helper

import unittest
import mox
import json


__author__ = 'imashhor'


# This test class tests the various call wrapper mechanisms that are performed for most of the API calls
# such as checking for service initialization and registering the call context based on the requests
# I put it in unit tests because its directly testing the service call wrapping functionalities.

class ServiceCallWrapperTests(mox.MoxTestBase):

    @classmethod
    def setUpClass(cls):
        # call parent set up
        super(ServiceCallWrapperTests, cls).setUpClass()

        dependencies.register_dependency("EntityMatcherProvider", None)

        class A(object):
            def incr(*args, **kwargs):
                pass

            class timer(object):
                def __init__(self, *args, **kwargs):
                    pass

                def __enter__(self, *args, **kwargs):
                    pass

                def __exit__(self, *args, **kwargs):
                    pass

                def __call__(self, *args, **kwargs):
                    pass

        mock = A()
        dependencies.register_dependency("StatsdProvider", mock)

        cls.app = main_api.app

        #CacheHelper uses a mongo db connection, which we don't want in a unit test, so stub it out
        mocker = mox.Mox()
        mocker.StubOutClassWithMocks(cache_helper, "CacheHelper")

        cls.app.init_api(environment="UNIT TESTING")


    def setUp(self):
        # call parent set up
        self.client = self.app.test_client()
        super(ServiceCallWrapperTests, self).setUp()

        #We might mess with the service for testing conditions, make sure we reset them during teardown
        self.__actual_service = self.app.svc
        self.app.svc.set_initialized_flag(True)

        # Create some test context
        self.context = {"user_id": 1, "source": "test_mds_service.py",
                        "user": {"user_id": 1, "is_generalist": False},
                        "team_industries": ["asdf"]}

    def doCleanups(self):
        super(ServiceCallWrapperTests, self).doCleanups()
        # Restore any changes to the service
        self.app.svc = self.__actual_service


    def test_register_caller_context_for_get(self):
        # Stub out the MDS call
        self.mox.StubOutWithMock(self.app, 'call_mds')
        self.app.call_mds("call_get_entity_type_summary", entity_type="company").AndReturn("hello")

        # Set up expectation that the caller context will be registered
        self.mox.StubOutWithMock(self.app.svc.svc_access, 'register_caller_context')
        self.app.svc.svc_access.register_caller_context("some_context")
        self.mox.ReplayAll()

        # Execute and let mox validate
        response = self.client.get('/summary/entity/company', content_type='application/json',
                        data=json.dumps(
                            {'context': 'some_context'}
                        ))
        self.assertEqual('{"summary": "hello"}', response.data)

    def test_reset_caller_context(self):
         # Stub out the MDS call
        self.mox.StubOutWithMock(self.app, 'call_mds')
        self.app.call_mds("call_get_entity_type_summary", entity_type="company").AndReturn("hello")

        # Set up expectation that the caller context will be reset
        self.mox.StubOutWithMock(self.app.svc.svc_access, 'reset_caller_context')
        self.app.svc.svc_access.reset_caller_context()
        self.mox.ReplayAll()

        # Execute and let mox validate
        response = self.client.get('/summary/entity/company', content_type='application/json',
                        data=json.dumps(
                            {'nocontext': 'none!'}
                        ))
        self.assertEqual('{"summary": "hello"}', response.data)

    def test_successful_response(self):
        self.mox.StubOutWithMock(self.app, 'call_mds')
        self.app.call_mds("call_get_entity_type_summary", entity_type="company").AndReturn("hello")
        self.mox.ReplayAll()

        response = self.client.get('/summary/entity/company')
        self.assertEqual('200 OK', response.status)

    # Note : Not testing None response as this is an artifact of the way we are doing call_response

    def test_exception_wrapping(self):
        test_cases = [
            # Tuple in the form of (<Exception raised>, <Expected status code>, <Expected message>)

            # GridFS Errors
            (UnsupportedAPI, 500, 'GridFS Error: Unsupported API call'),
            (FileExists, 403, 'GridFS Error: File already exists'),
            (NoFile, 404, 'GridFS Error: File does not exist'),
            (CorruptGridFile, 500, 'GridFS Error: File is corrupt'),
            (GridFSError, 500, 'GridFS Error'),

            # MongoDB Errors
            (ConnectionFailure, 503, 'DB Error: connection failure'),
            (TimeoutError(None), 503, 'DB Error: operation timeout'),
            (DuplicateKeyError(None), 403, 'DB Error: duplicate key'),
            (OperationFailure(None), 500, 'DB Error: operation failure'),
            (PyMongoError(None), 500, 'DB Error'),

            # BSON Encode/Decode Errors
            (InvalidBSON, 500, 'BSON Error: object creation'),
            (InvalidStringData, 500, 'BSON Error: string encoding'),
            (InvalidDocument, 500, 'BSON Error: document creation'),
            (InvalidId, 500, 'BSON Error: id creation'),
            (BSONError, 500, 'BSON Error:'),

            # Record Errors
            (RecValidationError, 500, 'Record Error: Validation Failed'),
            (RecInputError, 500, 'Record Error: Invalid Input'),
            (RecError, 500, 'Record Error'),

            # Service Access Errors
            (ServiceParamsError, 500, 'Service Access Error: Invalid Parameters'),
            (ServiceCallError, 500, 'Service Access Error: Failed Service Call'),
            (ServiceAccessError, 500, 'Service Access Error'),

            # Core Service Errors
            (BadRequestError, 400, 'Core Service Error: Bad Request'),
            (UnauthorizedError, 401, 'Core Service Error: Unauthorized Access'),
            (ForbiddenError, 403, 'Core Service Error: Forbidden'),
            (NotFoundError, 404, 'Core Service Error: Not Found'),
            (MethodNotAllowedError, 405, 'Core Service Error: Method Not Allowed'),
            (ConflictError, 409, 'Core Service Error: Conflict'),
            (ServiceError, 500, 'Core Service Error'),

            # Core Errors
            (InternalError, 500, 'Core Error: Internal'),
            (MatcherError, 500, 'Core Error: Entity Matcher'),
            (DataError, 500, 'Core Error: Data / DB'),
            (InputError, 500, 'Core Error: Input'),
            (WorkflowError, 500, 'Core Error: Workflow'),
            (CoreError, 500, 'Core Error'),

            # Python Errors
            (MemoryError, 500, 'Memory error'),
            (ArithmeticError, 500, 'Calculation error'),
            (RuntimeError, 500, 'Runtime error'),
            (Exception, 500, 'Error'),
        ]

        for test_case in test_cases:
            exception, expected_status_code, expected_message = test_case
            self.mox.StubOutWithMock(self.app, 'call_mds')
            self.app.call_mds("call_get_entity_type_summary", entity_type="company").AndRaise(exception)
            self.mox.ReplayAll()

            response = self.client.get('/summary/entity/company')
            self.assertEqual(expected_status_code, response.status_code)
            self.assertIn(expected_message, json.loads(response.data)['message'])
            self.mox.UnsetStubs()


if __name__ == '__main__':
    unittest.main()