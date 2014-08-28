import pprint
import time
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.exception_retry_handler import ExceptionRetryHandler
from common.utilities.inversion_of_control import Dependency, dependencies
import mox


__author__ = 'erezrubinstein'


class ExceptionRetryHandlerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(ExceptionRetryHandlerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # reset the class counter to 0, for exception counting
        self.exception_counter = 0

    def doCleanups(self):

        # call parent clean up and clean dependencies
        super(ExceptionRetryHandlerTests, self).doCleanups()
        dependencies.clear()


    def test_exception_type_matches(self):

        # define method that is wrapped and raises an exception
        @ExceptionRetryHandler(exception_type = NotImplementedError)
        def exception():
            if self.exception_counter == 0:
                self.exception_counter += 1
                raise NotImplementedError()

            self.exception_counter += 1

        # call the exception
        exception()

        # make sure the counter is 2, meaning exception was raised and the function was retried
        self.assertEqual(self.exception_counter, 2)


    def test_exception_type_does_not_match(self):

        # define method that is wrapped and raises an exception
        @ExceptionRetryHandler(exception_type = NotImplementedError)
        def exception():
            if self.exception_counter == 0:
                self.exception_counter += 1
                raise Exception()

            self.exception_counter += 1

        # verify that we get an exception, since the text does not match...
        self.assertRaises(Exception, exception)

        # verify that the counter is 1, meaning that the exception was raised, but the function was not retried
        self.assertEqual(self.exception_counter, 1)


    def test_exception_text_matches(self):

        # define method that is wrapped and raises an exception
        @ExceptionRetryHandler(exception_text = "o ma")
        def exception():
            if self.exception_counter == 0:
                self.exception_counter += 1
                raise Exception("Yo mama")

            self.exception_counter += 1

        # call the exception
        exception()

        # make sure the counter is 2, meaning exception was raised and the function was retried
        self.assertEqual(self.exception_counter, 2)


    def test_exception_text_does_not_match(self):

        # define method that is wrapped and raises an exception
        @ExceptionRetryHandler(exception_text = "papako")
        def exception():
            if self.exception_counter == 0:
                self.exception_counter += 1
                raise Exception("Yo mama")

            self.exception_counter += 1

        # verify that we get an exception, since the text does not match...
        self.assertRaises(Exception, exception)

        # verify that the counter is 1, meaning that the exception was raised, but the function was not retried
        self.assertEqual(self.exception_counter, 1)


    def test_exception_type_and_text_matches(self):

        # define method that is wrapped and raises an exception
        @ExceptionRetryHandler(exception_type = NotImplementedError, exception_text = "ma")
        def exception():
            if self.exception_counter == 0:
                self.exception_counter += 1
                raise NotImplementedError("yo mama")

            self.exception_counter += 1

        # call the exception
        exception()

        # make sure the counter is 2, meaning exception was raised and the function was retried
        self.assertEqual(self.exception_counter, 2)


    def test_exception_type_and_text_does_not_match(self):

        # define method that is wrapped and raises an exception
        @ExceptionRetryHandler(exception_type = NotImplementedError, exception_text = "papako")
        def exception():
            if self.exception_counter == 0:
                self.exception_counter += 1
                raise NotImplementedError("yo mama")

            self.exception_counter += 1

        # verify that we get an exception, since the text does not match...
        self.assertRaises(Exception, exception)

        # verify that the counter is 1, meaning that the exception was raised, but the function was not retried
        self.assertEqual(self.exception_counter, 1)


    def test_exception_max_retries__pass(self):

        # define method that is wrapped and raises an exception
        # make sure max retries is 3, meaning this should pass on its last retry
        @ExceptionRetryHandler(max_retries = 3)
        def exception():

            # raise exceptions 3 times
            if self.exception_counter < 3:
                self.exception_counter += 1
                raise Exception("Yo mama")

            self.exception_counter += 1

        # call the exception
        exception()

        # make sure the counter is 4, meaning exception was raised and the function was retried
        self.assertEqual(self.exception_counter, 4)


    def test_exception_max_retries__fail(self):

        # define method that is wrapped and raises an exception
        # make sure max retries is 2, meaning this should fail on its last retry
        @ExceptionRetryHandler(max_retries = 2)
        def exception():

            # raise exceptions 3 times
            if self.exception_counter < 3:
                self.exception_counter += 1
                raise Exception("Yo mama")

            self.exception_counter += 1

        # call the exception
        self.assertRaises(Exception, exception)

        # make sure the counter is 3, meaning exception was retried the right amount
        self.assertEqual(self.exception_counter, 3)


    def test_exception_retry_logging(self):

        # create a mock logger
        mock_logger = self.mox.CreateMockAnything()

        # re-register the mock logger as FlaskLogger
        dependencies.register_dependency("FlaskLogger", mock_logger, force_singleton = True)

        # define method that is wrapped and raises an exception
        # retry twice and pass
        @ExceptionRetryHandler(max_retries = 2)
        def exception():

            # raise exceptions twice and then pass
            if self.exception_counter < 2:
                self.exception_counter += 1
                raise Exception("Yo mama")

            self.exception_counter += 1

        # record two warning logs to the mock logger
        mock_logger.warning("ExceptionRetryHandler exception. Attempt: 1, Exception: Yo mama")
        mock_logger.warning("ExceptionRetryHandler exception. Attempt: 2, Exception: Yo mama")

        # replay all
        self.mox.ReplayAll()

        # call the exception
        exception()

        # make sure the counter is 3, meaning exception was retried the right amount
        self.assertEqual(self.exception_counter, 3)


    def test_exception_retry_time_to_sleep(self):

        # define method that is wrapped and raises an exception
        # retry twice and pass
        @ExceptionRetryHandler(max_retries = 2, retry_seconds_wait = 2)
        def exception():

            # raise exceptions twice and then pass
            if self.exception_counter < 2:
                self.exception_counter += 1
                raise Exception("Yo mama")

            self.exception_counter += 1

        # stub time.sleep
        self.mox.StubOutWithMock(time, "sleep")

        # record two time sleeps
        time.sleep(2)
        time.sleep(2)

        # replay all
        self.mox.ReplayAll()

        # call the exception
        exception()

        # make sure the counter is 3, meaning exception was retried the right amount
        self.assertEqual(self.exception_counter, 3)






