import mox
import time
from common.utilities import lox
from common.utilities.inversion_of_control import dependencies
from common.utilities.lox import Lox, LoxException
from geoprocessing.helpers.dependency_helper import register_mox_gp_dependencies

__author__ = 'erezrubinstein'



class WhiteSpaceCalculatorTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(WhiteSpaceCalculatorTests, self).setUp()

        # register mock dependencies
        register_mox_gp_dependencies(self.mox)

        # helper class vars
        self.context = { "user_id": "azamat", "source": "bagatov" }

    def doCleanups(self):

        # call parent clean up and clean dependencies
        super(WhiteSpaceCalculatorTests, self).doCleanups()
        dependencies.clear()

    def test_one_lock_available(self):

        # mocks
        lock_type = "TestLock"
        lock_id = "TestLockID"

        # stub out methods/objects
        self.mox.StubOutClassWithMocks(lox, "MDSProvider")

        # start recording
        mock_provider = lox.MDSProvider(lock_type, lock_id, self.context)
        mock_provider.obtain_lock().AndReturn(True)
        mock_provider.release_lock()

        # replay all
        self.mox.ReplayAll()

        # create one lock (should be available)
        with Lox(lock_type, lock_id, (self.context,), keep_alive_timer = None):
            pass

    def test_one_lock_not_available(self):

        # mocks
        lock_type = "TestLock"
        lock_id = "TestLockID"

        # stub out methods/objects
        self.mox.StubOutClassWithMocks(lox, "MDSProvider")

        # start recording
        mock_provider = lox.MDSProvider(lock_type, lock_id, self.context)
        mock_provider.obtain_lock().AndReturn(False)

        # replay all
        self.mox.ReplayAll()

        # create one lock (should be available)
        try:
            with Lox(lock_type, lock_id, (self.context,), keep_alive_timer = None):
                pass
        except:
            pass
        else:
            raise Exception("Should have raised an exception.... :(")


    def test_multiple_ids_success(self):

        # mocks
        lock_type = "TestLock"
        lock_id_1 = "TestLockID_1"
        lock_id_2 = "TestLockID_2"

        # stub out methods/objects
        self.mox.StubOutClassWithMocks(lox, "MDSProvider")

        # start recording
        mock_provider_1 = lox.MDSProvider(lock_type, lock_id_1, self.context)
        mock_provider_2 = lox.MDSProvider(lock_type, lock_id_2, self.context)
        mock_provider_1.obtain_lock().AndReturn(True)
        mock_provider_2.obtain_lock().AndReturn(True)
        mock_provider_1.release_lock()
        mock_provider_2.release_lock()

        # replay all
        self.mox.ReplayAll()

        # lock
        with Lox(lock_type, [lock_id_1, lock_id_2], (self.context,), keep_alive_timer = None):
            pass


    def test_multiple_ids_fail(self):

        # mocks
        lock_type = "TestLock"
        lock_id_1 = "TestLockID_1"
        lock_id_2 = "TestLockID_2"
        lock_id_3 = "TestLockID_3"

        # stub out methods/objects
        self.mox.StubOutClassWithMocks(lox, "MDSProvider")

        # start recording
        mock_provider_1 = lox.MDSProvider(lock_type, lock_id_1, self.context)
        mock_provider_1.lock_id = lock_id_1
        mock_provider_1.lock_type = lock_type

        mock_provider_2 = lox.MDSProvider(lock_type, lock_id_2, self.context)
        mock_provider_2.lock_id = lock_id_2
        mock_provider_2.lock_type = lock_type

        mock_provider_3 = lox.MDSProvider(lock_type, lock_id_3, self.context)
        mock_provider_3.lock_id = lock_id_3
        mock_provider_3.lock_type = lock_type

        mock_provider_1.obtain_lock().AndReturn(True)
        mock_provider_2.obtain_lock().AndReturn(True)
        mock_provider_3.obtain_lock().AndReturn(False)

        # release the first 2 locks, which were successfully obtained
        mock_provider_1.release_lock()
        mock_provider_2.release_lock()

        # replay all
        self.mox.ReplayAll()

        # create lock, which should raise an exception
        try:
            with Lox(lock_type, [lock_id_1, lock_id_2, lock_id_3], (self.context,), keep_alive_timer = None):
                pass
        except LoxException:
            pass
        else:
            raise Exception("Should have raised an exception.... :(")



    def test_keep_alive(self):

        # mocks
        lock_type = "TestLock"
        lock_id = "TestLockID"

        # stub out methods/objects
        self.mox.StubOutClassWithMocks(lox, "MDSProvider")

        # start recording
        mock_provider = lox.MDSProvider(lock_type, lock_id, self.context)
        mock_provider.obtain_lock().AndReturn(True)
        mock_provider.keep_alive()
        mock_provider.keep_alive()
        mock_provider.keep_alive()
        mock_provider.release_lock()

        # replay all
        self.mox.ReplayAll()

        # create one lock (should be available)
        with Lox(lock_type, lock_id, (self.context,), keep_alive_timer = .15):
            time.sleep(.4)

        # sleep for another half a second to verify that the keep alive is no longer called
        time.sleep(.4)


    def test_try_again_success(self):

        # mocks
        lock_type = "TestLock"
        lock_id = "TestLockID"

        # stub out methods/objects
        self.mox.StubOutClassWithMocks(lox, "MDSProvider")

        # start recording
        mock_provider = lox.MDSProvider(lock_type, lock_id, self.context)
        mock_provider.obtain_lock().AndReturn(False)
        mock_provider.obtain_lock().AndReturn(False)
        mock_provider.obtain_lock().AndReturn(True)
        mock_provider.release_lock()

        # replay all
        self.mox.ReplayAll()

        # create one lock (should be available)
        with Lox(lock_type, lock_id, (self.context,), keep_alive_timer = None, try_again_timeout = .5, try_again_interval = .2):
            pass


    def test_try_again_failure(self):

        # mocks
        lock_type = "TestLock"
        lock_id = "TestLockID"

        # stub out methods/objects
        self.mox.StubOutClassWithMocks(lox, "MDSProvider")

        # start recording
        mock_provider = lox.MDSProvider(lock_type, lock_id, self.context)
        mock_provider.lock_id = lock_id
        mock_provider.lock_type = lock_type
        mock_provider.obtain_lock().AndReturn(False)
        mock_provider.obtain_lock().AndReturn(False)
        mock_provider.obtain_lock().AndReturn(False)

        # replay all
        self.mox.ReplayAll()
        # create lock, which should raise an exception
        try:
            with Lox(lock_type, lock_id, (self.context,), keep_alive_timer = None, try_again_timeout = .5, try_again_interval = .2):
                pass
        except LoxException:
            pass
        else:
            raise Exception("Should have raised an exception.... :(")
