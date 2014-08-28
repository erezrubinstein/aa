from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import trade_area_helper
from bson.objectid import ObjectId
import mox


__author__ = 'jsternberg'


class TestTradeAreaHelper(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestTradeAreaHelper, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # various needed data
        self.context = { "user": "chicken_woot" }

    def doCleanups(self):
        # call parent clean up
        super(TestTradeAreaHelper, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_get_all_trade_area_ids_for_banner(self):

        # set up mock data
        mock_banner_id = ObjectId()
        mock_trade_area_ids = {ObjectId(), ObjectId(), ObjectId()}

        query = {
            "data.company_id": str(mock_banner_id)
        }

        # start recording
        self.mock_main_access.mds.call_distinct_field_values("trade_area", "_id", query=query, context=self.context).AndReturn(mock_trade_area_ids)

        # replay All
        self.mox.ReplayAll()

        # go!
        trade_area_ids = trade_area_helper.get_all_trade_area_ids_for_banner(mock_banner_id, self.context)

        self.assertEqual(trade_area_ids, mock_trade_area_ids)
