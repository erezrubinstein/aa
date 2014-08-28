import datetime
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic import rir_helper
from core.service.svc_workflow.implementation.task.implementation.retail_input_tasks.store_helper_async_helper import StoreHelperAsyncHelper

__author__ = 'erezrubinstein'


class TestStoreHelperAsyncHelper(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestStoreHelperAsyncHelper, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.start_time = datetime.datetime(2013, 1, 1)
        self.end_time = datetime.datetime(2013, 3, 3)


    def doCleanups(self):
        # call parent clean up
        super(TestStoreHelperAsyncHelper, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_update_rirs_with_store_interval_command(self):

        # set up data
        input_rec = { "context": self.context, "command": "update_rirs_with_store_interval", "store_id": "woot" }

        # get store helper async helper
        helper = self._init_helper_and_mock_start_date(input_rec)

        # stub out the method
        self.mox.StubOutWithMock(rir_helper, "update_rirs_with_store_interval")

        # record
        rir_helper.update_rirs_with_store_interval("woot", self.context, rir_id_list = None)
        datetime.datetime.utcnow().AndReturn(self.end_time)

        # replay
        self.mox.ReplayAll()

        # go!
        response = helper.run()

        # make sure results are good
        self.assertEqual(response, {
            "status": "success",
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "command": "update_rirs_with_store_interval"
        })


    def test_update_rirs_with_store_interval_command__with_rir_id_list(self):

        # set up data
        input_rec = { "context": self.context, "command": "update_rirs_with_store_interval", "store_id": "woot", "rir_id_list": "YESSIR!" }

        # get store helper async helper
        helper = self._init_helper_and_mock_start_date(input_rec)

        # stub out the method
        self.mox.StubOutWithMock(rir_helper, "update_rirs_with_store_interval")

        # record
        rir_helper.update_rirs_with_store_interval("woot", self.context, rir_id_list = "YESSIR!")
        datetime.datetime.utcnow().AndReturn(self.end_time)

        # replay
        self.mox.ReplayAll()

        # go!
        response = helper.run()

        # make sure results are good
        self.assertEqual(response, {
            "status": "success",
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "command": "update_rirs_with_store_interval"
        })


    def test_unset_rir_store_interval_command(self):

        # set up data
        input_rec = { "context": self.context, "command": "unset_rir_store_interval", "rir_id": "roundhouse_kick" }

        # get store helper async helper
        helper = self._init_helper_and_mock_start_date(input_rec)

        # stub out the method
        self.mox.StubOutWithMock(rir_helper, "unset_rir_store_interval")

        # record
        rir_helper.unset_rir_store_interval("roundhouse_kick", self.context)
        datetime.datetime.utcnow().AndReturn(self.end_time)

        # replay
        self.mox.ReplayAll()

        # go!
        response = helper.run()

        # make sure results are good
        self.assertEqual(response, {
            "status": "success",
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "command": "unset_rir_store_interval"
        })


    def test_exception_handling(self):

        # set up data
        input_rec = { "context": self.context, "command": "damn_kids" }

        # get store helper async helper
        helper = self._init_helper_and_mock_start_date(input_rec)

        # record
        datetime.datetime.utcnow().AndReturn(self.end_time)

        # replay
        self.mox.ReplayAll()

        # go!
        response = helper.run()

        # make sure results are good
        self.assertEqual(response, {
            "status": "failure",
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "exception": "Unknown Command",
            "command": "damn_kids"
        })





    # ----------------------------------- Helper Methods ----------------------------------- #

    def _init_helper_and_mock_start_date(self, input_rec):

        # create object, but stub out the start date before
        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn(self.start_time)
        self.mox.ReplayAll()
        helper = StoreHelperAsyncHelper(input_rec)

        # reset so we can record again
        self.mox.ResetAll()

        return helper