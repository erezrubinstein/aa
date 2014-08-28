import datetime
from mox import IsA
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
import mox
from core.service.svc_workflow.implementation.task.implementation.retailer_tasks.retailer_store_customers_gis_loader import RetailerStoreCustomersGisLoader
from retailer.common import ltm_helper
from retailer.common.business_logic import configuration_helper

class TestRetailerStoreCustomersGISLoader(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(TestRetailerStoreCustomersGISLoader, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mock dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_main_params_builder = Dependency("CoreAPIParamsBuilder").value
        self.mock_logger = Dependency("FlaskLogger").value



    def doCleanups(self):
        # call parent clean up
        super(TestRetailerStoreCustomersGISLoader, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_get_retailer_stores(self):
        # Test that the query for getting retailer stores is correct

        input_rec = self.get_common_input_rec()

        self.mock_main_access.mds.call_find_entities_raw(
            'retailer_store',
            {'entity_fields': ['_id', 'data.store_id', 'data.retailer_client_id']},
            {'source': 'unit_test', 'user_id': 'test_user'}
        )

        self.mox.ReplayAll()
        gis_loader = RetailerStoreCustomersGisLoader(input_rec)
        gis_loader._get_retailer_stores()


    def test_get_store_customers(self):
        # Test that the aggregate query for getting store customers is correct

        input_rec = self.get_common_input_rec()

        # Stub out some helper calls
        self.mox.StubOutWithMock(ltm_helper, 'get_default_ltm_end_date')
        ltm_helper.get_default_ltm_end_date(mox.IgnoreArg(), mox.IgnoreArg()).MultipleTimes().AndReturn(
            datetime.datetime(2013, 10, 12))

        self.mox.StubOutWithMock(configuration_helper, 'get_retailer_client_loader_file_configuration')
        configuration_helper.get_retailer_client_loader_file_configuration(
            mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg()).MultipleTimes().AndReturn({})

        # Now check that the aggregation is being called correctly
        expected_aggregate_result = [
            {
                "_id": { "customer_id": "15" },
                "customer_total": 10
            },
           {
                "_id": { "customer_id": "22" },
                "customer_total": 1120
            }
        ]

        self.mock_main_access.mds.call_aggregate_entities(
            'retailer_transaction',
            [
                {
                    '$match': {
                        'data.transaction_date':
                            {'$lte': datetime.datetime(2013, 10, 12, 0, 0),
                             '$gte': datetime.datetime(2012, 10, 13, 0, 0)},
                        'data.retailer_client_id': 7,
                        'data.store_id': '18'}
                },
                {
                    '$group': {
                        'customer_total': {'$sum': '$data.sales'},
                        '_id': {
                            'customer_id': '$data.customer_id',
                            'mds_id': '$data._id'}
                    }
                }
            ],
            {'source': 'unit_test', 'user_id': 'test_user'}, timeout=600).AndReturn(expected_aggregate_result)

        self.mox.ReplayAll()
        gis_loader = RetailerStoreCustomersGisLoader(input_rec)
        gis_loader._get_store_customers()

        # Validate store_customers dictionary
        expected_store_customers = {
            "22": {'sales': 1120},
            "15": {'sales': 10}
        }

        self.assertEqual(expected_store_customers,gis_loader.store_customers)

    def test_get_customers_coordinates(self):
        # Test that the  query for getting store customers coordinates is correct
        # And that assembling the results is also correct

        input_rec = self.get_common_input_rec()

        gis_loader = RetailerStoreCustomersGisLoader(input_rec)
        gis_loader.store_customers = {
            "22": {'sales': 1120},
            "15": {'sales': 101}
        }

        self.mock_main_access.mds.call_find_entities_raw(
            'retailer_customer',
            {
                'query': {
                    'data.retailer_client_id': 7,
                    'data.customer_id': {'$in': ['15', '22']},
                    'data.geo': {'$ne': None}
                },
                'options': {'as_list': True, 'has_metadata': False},
                'entity_fields': ['_id', 'data.geo', 'data.customer_id']},
            {'source': 'unit_test', 'user_id': 'test_user'},
            timeout=600
        ).AndReturn(
            [
                # _id, data.geo, data.customer_id
                [1, [80, 30], "22"],
                [2, [90, 40], "15"],
            ]
        )

        self.mox.ReplayAll()
        gis_loader._get_customers_coordinates()

        self.assertEqual(gis_loader.store_customers["15"]["longitude"], 90)
        self.assertEqual(gis_loader.store_customers["15"]["latitude"], 40)
        self.assertEqual(gis_loader.store_customers["22"]["longitude"], 80)
        self.assertEqual(gis_loader.store_customers["22"]["latitude"], 30)


    def test_remove_customers_without_coordinates(self):
        # Test that the logic for removing stores without coordinates are correct
        # And that a warning is logged

        input_rec = self.get_common_input_rec()

        gis_loader = RetailerStoreCustomersGisLoader(input_rec)
        gis_loader.store_customers = {
            "22": {'sales': 1120, "latitude": 30, "longitude": 60},
            "15": {'sales': 101}
        }

        gis_loader.logger.warn("Warning: The following customers for retailer_client 7 is detected in retailer_transaction but not in retailer_customers: ['15']")
        self.mox.ReplayAll()

        # Execute and validate
        gis_loader._remove_customers_without_coordinates()
        self.assertEqual(["22"], gis_loader.store_customers.keys())


    def get_common_input_rec(self):
        return {
            "task_id": "xxx",
            "retailer_store_id": "18",
            "retailer_client_id": 7,
            "context": {
                "source": "unit_test",
                "user_id": "test_user"
            }
        }