import json
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import dependencies, Dependency
from core.common.business_logic.service_entity_logic import trade_area_helper
from core.common.utilities.helpers import generate_id
from core.service.svc_analytics.implementation.calc.engines.competition.distinct_away_store_counts_per_competitor \
    import DistinctAwayStoreCountsPerCompetitor
import unittest
import mox
import datetime
from core.service.svc_analytics.implementation.calc.engines.retailer_transactions.aggregate_transactions_per_customer import AggregateTransactionsPerCustomer
from retailer.common.ltm_helper import get_default_ltm_end_date
from tests.unit_tests.core_tests.data_stub_helpers import create_mock_taci


class AggregateTransactionsTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AggregateTransactionsTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)
        self.mock = self.mox.CreateMock(AggregateTransactionsPerCustomer)
        self.mock.main_param = Dependency("CoreAPIParamsBuilder").value
        self.mock.main_access = Dependency("CoreAPIProvider").value
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.context = {
            "the": "context"
        }

        self.maxDiff = None


    def doCleanups(self):
        super(AggregateTransactionsTests, self).doCleanups()
        dependencies.clear()


    def test_get_default_ltm_end_date(self):
        self.mock.retailer_client_id = 10

        trx_dt = datetime.datetime.now()
        mock_transactions = [["id", trx_dt]]
        params = {'sort': [['data.transaction_date', -1]], 'query': {'data.retailer_client_id': 10}, 'limit': 1, 'options': {'as_list': True}, 'entity_fields': ['_id', 'data.transaction_date']}
        self.mock.main_access.mds.call_find_entities_raw("retailer_transaction",
                                                         params,
                                                         self.mock.context).AndReturn(mock_transactions)
        # replay all
        self.mox.ReplayAll()

        date = get_default_ltm_end_date(self.mock.context, self.mock.retailer_client_id)

        self.assertEqual(date, trx_dt)



if __name__ == '__main__':
    unittest.main()