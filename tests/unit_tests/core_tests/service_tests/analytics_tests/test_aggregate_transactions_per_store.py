from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
import unittest
import mox
from core.service.svc_analytics.implementation.calc.engines.retailer_transactions.aggregate_transactions_per_store import AggregateTransactionsPerStore



class AggregateTransactionsPerStoreTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AggregateTransactionsPerStoreTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get and set various mock dependencies
        dependencies.register_dependency("MDSMongoAccess", None)
        self.mock = self.mox.CreateMock(AggregateTransactionsPerStore)
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.mds_mongo_access = self.mox.CreateMockAnything()
        self.mock.context = {
            "the": "context"
        }
        self.mock.map = """function() {
                            var value = {
                                "num_trx": 1,
                                "customers": {},
                                "sum_sales": this.data.sales
                            };

                            value.customers[this.data.customer_id] = {
                                num_trx: 1,
                                sum_sales: this.data.sales
                            };

                            emit(this.data.store_id, value);
                        };"""

        self.mock.reduce = """function(key, values) {

                                var result = {
                                        "num_trx": 0,
                                        "customers": {},
                                        "sum_sales": 0
                                };

                                values.forEach(function(v){
                                    result.num_trx += v.num_trx;
                                    result.sum_sales += v.sum_sales;
                                    for (var i in v.customers) {
                                        if (!result.customers.hasOwnProperty(i)) {
                                            result.customers[i] = {
                                                num_trx: 0,
                                                sum_sales: 0
                                            };
                                        }
                                        result.customers[i].num_trx += v.customers[i].num_trx;
                                        result.customers[i].sum_sales += v.customers[i].sum_sales;
                                    }
                                });

                                return result;
                            };"""

        self.mock.finalize = """function(store_id, store) {

                                    for (var i in store.customers) {
                                        var customer = store.customers[i];
                                        customer.avg_trx = customer.sum_sales / customer.num_trx;
                                        customer.num_trx = NumberInt(customer.num_trx);
                                    }

                                    store.num_customers = NumberInt(Object.keys(store.customers).length);
                                    store.num_trx = NumberInt(store.num_trx);

                                    if (store.num_customers > 0) {
                                        store.avg_sales_per_customer = store.sum_sales / store.num_customers;
                                    }

                                    return store;
                                };"""
        self.maxDiff = None


    def doCleanups(self):
        super(AggregateTransactionsPerStoreTests, self).doCleanups()
        dependencies.clear()


    def test_get_default_bucket_results_dict(self):
        age_range = "1-100"
        actual = AggregateTransactionsPerStore._get_default_demographics_bucket(self.mock, "Female", age_range)
        expected = {
            "gender": "Female",
            "age_range": age_range,
            "num_trx": 0,
            "num_customers": 0,
            "sum_sales": 0,
            "avg_sales_per_customer": 0
        }

        self.assertEqual(actual, expected)


    def test_get_age_bucket_min_from_age__zero(self):
        # get 0 for 5 and under
        for age in range(3):
            min_age = AggregateTransactionsPerStore._get_age_bucket_min_from_age(self.mock, age)
            self.assertEqual(min_age, 0)


    def test_get_age_bucket_min_from_age__mid(self):
        # get 30 for 30 (mid bracket)
        age = 30
        min_age = AggregateTransactionsPerStore._get_age_bucket_min_from_age(self.mock, age)
        self.assertEqual(min_age, 30)


    def test_get_age_bucket_min_from_age__old(self):
        age = 92
        min_age = AggregateTransactionsPerStore._get_age_bucket_min_from_age(self.mock, age)
        self.assertEqual(min_age, 85)


    def test_get_customer_demographic__in_cache_already(self):
        self.mock.customer_id_demographic_lookup = {
            "id1": ("F", 32)
        }
        gender, age = AggregateTransactionsPerStore._get_customer_demographic(self.mock, "id1")

        self.assertEqual(gender, "F")
        self.assertEqual(age, 32)


    def test_get_customer_demographic__not_in_cache_return_success(self):
        self.mock.customer_id_demographic_lookup = {}
        self.mock.projection = {}
        self.mock.retailer_client_id = 42
        customer_id = "cid"
        # begin recording
        query = {
            "data.retailer_client_id": self.mock.retailer_client_id,
            "data.customer_id": customer_id
        }
        self.mock.mds_mongo_access.find_one("retailer_customer", query, self.mock.projection).AndReturn(
            {"data": {"gender": "M", "age": 50}})

        # replay all
        self.mox.ReplayAll()

        gender, age = AggregateTransactionsPerStore._get_customer_demographic(self.mock, customer_id)
        self.assertEqual(gender, "M")
        self.assertEqual(age, 50)
        self.assertEqual(self.mock.customer_id_demographic_lookup, {customer_id: ("M", 50)})


    def test_get_customer_demographic__not_in_cache_return_none(self):
        self.mock.customer_id_demographic_lookup = {}
        self.mock.projection = {}
        self.mock.retailer_client_id = 42
        customer_id = "cid"
        # begin recording
        query = {
            "data.retailer_client_id": self.mock.retailer_client_id,
            "data.customer_id": customer_id
        }
        self.mock.mds_mongo_access.find_one("retailer_customer", query, self.mock.projection).AndReturn(None)
        # replay all
        self.mox.ReplayAll()

        gender, age = AggregateTransactionsPerStore._get_customer_demographic(self.mock, customer_id)
        self.assertEqual(gender, None)
        self.assertEqual(age, None)
        self.assertEqual(self.mock.customer_id_demographic_lookup, {customer_id: (None, None)})


    def test_get_customer_demographic__not_in_cache_return_non_int(self):
        self.mock.customer_id_demographic_lookup = {}
        self.mock.projection = {}
        self.mock.retailer_client_id = 42
        customer_id = "cid"
        # begin recording
        customer_data = {"data": {
            "gender": "F",
            "age": "hi I'm not an integer, sucka"
        }}
        query = {
            "data.retailer_client_id": self.mock.retailer_client_id,
            "data.customer_id": customer_id
        }
        self.mock.mds_mongo_access.find_one("retailer_customer", query, self.mock.projection).AndReturn(customer_data)
        # replay all
        self.mox.ReplayAll()

        gender, age = AggregateTransactionsPerStore._get_customer_demographic(self.mock, customer_id)
        self.assertEqual(gender, 'F')
        self.assertEqual(age, None)
        self.assertEqual(self.mock.customer_id_demographic_lookup, {customer_id:  ('F', None)})


    def test_init_full_age_bucket_results_dict(self):

        test_calc = AggregateTransactionsPerStore(None, None, None, None, None, None, None, None, None, None)

        expected_female_below_5 = {
                 'gender': 'Female',
                 'avg_sales_per_customer': 0,
                 'age_range': '<5',
                 'num_customers': 0,
                 'num_trx': 0,
                 'sum_sales': 0
        }
        #self.mox.ReplayAll()

        result = test_calc._init_full_demographics_bucket_dicts()

        self.assertEqual(result["Female <5"], expected_female_below_5)


    def test_calculate(self):
        """
        This only tests one store with one customer, due to mocking.
        A more comprehensive calculation results test is in the integration test.
        """
        self.mock.input = {
            "entity_type": "et"
        }
        self.mock.output = {}

        # begin recording
        self.mock.out = [("replace", "ltmTrxPerStore"), ("db", "map_reduce")]
        self.mock.query = "query"
        results = [
            {
                "_id": "1",
                "value": {
                    "customers": {
                        "100": {
                            "num_trx": 5,
                            "sum_sales": 100,
                            "avg_trx": 20
                        }
                    }
                }
            }
        ]
        self.mock._build_query()
        self.mock.main_access.mds.call_map_reduce("et", self.mock.map, self.mock.reduce, self.mock.out,
                                                  finalize=self.mock.finalize,
                                                  query=self.mock.query).AndReturn(results)
        bucket = {
            "Female 15-20":
            {
                "gender": "Female",
                "age_range": "15-19",
                "num_trx": 0,
                "num_customers": 0,
                "sum_sales": 0,
                "avg_sales_per_customer": 0,
            }
        }
        self.mock._init_full_demographics_bucket_dicts().AndReturn(bucket)
        self.mock._get_customer_demographic("100").AndReturn(("F", 16))
        self.mock._get_demographic_key("F", 16).AndReturn(("Female 15-20"))

        # replay all
        self.mox.ReplayAll()

        AggregateTransactionsPerStore._calculate(self.mock)

        expected = [{
                        '_id': '1',
                        'value': {
                            'by_demographic': {
                                 "Female 15-20": {
                                    "gender": "Female",
                                    'age_range': '15-19',
                                    'num_trx': 5,
                                    'avg_sales_per_customer':100,
                                    'sum_sales': 100,
                                    'num_customers': 1,
                                }
                            }
                        }
                    }]

        self.assertEqual(self.mock.results, expected)

if __name__ == '__main__':
    unittest.main()