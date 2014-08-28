from __future__ import division
import json
from bson.objectid import ObjectId
import datetime
from common.service_access.utilities.json_helpers import APIEncoderForExportingMongoQuery
from retailer.common import ltm_helper
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_industry, insert_test_retailer_customer, insert_test_retailer_transaction, insert_test_retailer_store
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency


class AnalyticsRetailerTestCollection(ServiceTestCollection):
    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "main_retailerb_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }
        self.main_param = Dependency("CoreAPIParamsBuilder").value
        self.retailer_client_id = 0


    def setUp(self):
        self.mds_access.call_delete_reset_database()
        self.analytics_access.call_delete_reset_database()


    def tearDown(self):
        pass


    ##------------------------------------------------##


    def test_aggregate_transactions_per_customer(self):
        self._insert_default_entities()
        calc_params = {
            "retailer_client_id": self.retailer_client_id,
            "target_entity_type": "retailer_customer",
            "options": {
                "fetch": False,
                "save": True,
                "return": False,
                "overwrite": True,
                "sample": False,
                "summary": False
            }
        }
        response = self.analytics_access.call_post_run_calc_by_name("LTM Transactions Per Customer",
                                                                    calc_params, self.context)
        query = {"_id": ObjectId(self.rc_id)}
        fields = ["_id", "data.analytics.trx.all_stores.ltm"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        customer = self.main_access.mds.call_find_entities_raw("retailer_customer", params, self.context)

        analytics_query = json.dumps(self._build_query(), cls=APIEncoderForExportingMongoQuery)

        expected = {
            'meta': {
                # 'analytics_query': analytics_query,
                # 'analytics_calc_id': response["calc_id"],
                'wfs_task_id': None
            },
            'avg': 250000005.5,
            'count': 2,
            'max': 500000000.5,
            'min': 10.5,
            'sum': 500000011.0
        }
        self.test_case.assertDictEqual(customer[0][1], expected)


    def test_aggregate_transactions_per_customer__ltm(self):
        customer_id = "cid"

        self.rc_id = insert_test_retailer_customer(self.retailer_client_id, customer_id)

        self.trx_id1 = insert_test_retailer_transaction(self.retailer_client_id, customer_id, 10.5, datetime.datetime.now())
        # this guy really likes j.crew clothes
        self.trx_id2 = insert_test_retailer_transaction(self.retailer_client_id, customer_id, 500000000.5, datetime.datetime.now() - datetime.timedelta(days=366))

        calc_params = {
            "retailer_client_id": self.retailer_client_id,
            "target_entity_type": "retailer_customer",
            "options": {
                "fetch": False,
                "save": True,
                "return": False,
                "overwrite": True,
                "sample": False,
                "summary": False
            }
        }
        response = self.analytics_access.call_post_run_calc_by_name("LTM Transactions Per Customer",
                                                                    calc_params, self.context)
        query = {"_id": ObjectId(self.rc_id)}
        fields = ["_id", "data.analytics.trx.all_stores.ltm"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        customer = self.main_access.mds.call_find_entities_raw("retailer_customer", params, self.context)

        analytics_query = json.dumps(self._build_query(), cls=APIEncoderForExportingMongoQuery)

        expected = {
            'meta': {
                # 'analytics_query': analytics_query,
                # 'analytics_calc_id': response["calc_id"],
                'wfs_task_id': None
            },
            'avg': 10.5,
            'count': 1,
            'max': 10.5,
            'min': 10.5,
            'sum': 10.5
        }

        self.test_case.assertDictEqual(customer[0][1], expected)


    def test_aggregate_transactions_per_store(self):
        self._insert_default_entities()
        self._insert_extra_entities()
        self.test_case.maxDiff = None

        calc_params = {
            "retailer_client_id": self.retailer_client_id,
            "options": {
                "fetch": False,
                "save": True,
                "return": False,
                "overwrite": True,
                "sample": False,
                "summary": False
            }
        }
        response = self.analytics_access.call_post_run_calc_by_name("LTM Transactions Summary Per Store",
                                                                    calc_params, self.context)
        query = {"_id": ObjectId(self.store_id)}
        fields = ["_id", "data.analytics.trx.ltm"]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        store = self.main_access.mds.call_find_entities_raw("retailer_store", params, self.context)

        analytics_query = json.dumps(self._build_query(), cls=APIEncoderForExportingMongoQuery)


        # We're going to assert parts of the document to make it easier to debug
        # First, test the store values
        store_root_results = store[0][1].copy()
        del store_root_results['by_demographic']
        expected_store_root_results = {
            u'avg_sales_per_customer': 166670028.0,
            u'num_customers': 3,
            u'sum_sales': 500010084.0,
            u'meta': {'wfs_task_id': None},
            u'num_trx': 7,
        }

        self.test_case.assertDictEqual(expected_store_root_results, store_root_results)

        # Test each demographic seperately
        self._assert_demographic_values(store, 'Male <5')
        self._assert_demographic_values(store, 'Male 5-9')
        self._assert_demographic_values(store, 'Male 10-14')
        self._assert_demographic_values(store, 'Male 15-19')
        self._assert_demographic_values(store, 'Male 20-24')
        self._assert_demographic_values(store, 'Male 25-29')
        self._assert_demographic_values(store, 'Male 30-34')
        self._assert_demographic_values(store, 'Male 35-39')
        self._assert_demographic_values(store, 'Male 40-44')
        self._assert_demographic_values(store, 'Male 45-49')
        self._assert_demographic_values(store, 'Male 50-54')
        self._assert_demographic_values(store, 'Male 55-59')
        self._assert_demographic_values(store, 'Male 60-64')
        self._assert_demographic_values(store, 'Male 65-69')
        self._assert_demographic_values(store, 'Male 70-74')
        self._assert_demographic_values(store, 'Male 75-79')
        self._assert_demographic_values(store, 'Male 80-84')
        self._assert_demographic_values(store, 'Male >85', 1, 2, 10001.0, 10001.0)
        self._assert_demographic_values(store, 'Female <5')
        self._assert_demographic_values(store, 'Female 5-9')
        self._assert_demographic_values(store, 'Female 10-14')
        self._assert_demographic_values(store, 'Female 15-19', 2, 5,  500000083.0, 250000041.5 )
        self._assert_demographic_values(store, 'Female 20-24')
        self._assert_demographic_values(store, 'Female 25-29')
        self._assert_demographic_values(store, 'Female 30-34')
        self._assert_demographic_values(store, 'Female 35-39')
        self._assert_demographic_values(store, 'Female 40-44')
        self._assert_demographic_values(store, 'Female 45-49')
        self._assert_demographic_values(store, 'Female 50-54')
        self._assert_demographic_values(store, 'Female 55-59')
        self._assert_demographic_values(store, 'Female 60-64')
        self._assert_demographic_values(store, 'Female 65-69')
        self._assert_demographic_values(store, 'Female 70-74')
        self._assert_demographic_values(store, 'Female 75-79')
        self._assert_demographic_values(store, 'Female 80-84')
        self._assert_demographic_values(store, 'Female >85')
        
      
        # Test the second store
        query = {"_id": ObjectId(self.store_id2)}
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   as_list=True)["params"]
        store = self.main_access.mds.call_find_entities_raw("retailer_store", params, self.context)

        # We're going to assert parts of the document to make it easier to debug
        # First, test the store values
        store_root_results = store[0][1].copy()
        del store_root_results['by_demographic']
        expected_store_root_results = {
            u'avg_sales_per_customer': 150.0,
            u'num_customers': 1,
            u'sum_sales': 150.0,
            u'meta': {'wfs_task_id': None},
            u'num_trx': 2,
        }

        self.test_case.assertDictEqual(expected_store_root_results, store_root_results)

        # Test each demographic seperately
        self._assert_demographic_values(store, 'Male <5')
        self._assert_demographic_values(store, 'Male 5-9')
        self._assert_demographic_values(store, 'Male 10-14')
        self._assert_demographic_values(store, 'Male 15-19')
        self._assert_demographic_values(store, 'Male 20-24')
        self._assert_demographic_values(store, 'Male 25-29')
        self._assert_demographic_values(store, 'Male 30-34')
        self._assert_demographic_values(store, 'Male 35-39')
        self._assert_demographic_values(store, 'Male 40-44')
        self._assert_demographic_values(store, 'Male 45-49')
        self._assert_demographic_values(store, 'Male 50-54')
        self._assert_demographic_values(store, 'Male 55-59')
        self._assert_demographic_values(store, 'Male 60-64')
        self._assert_demographic_values(store, 'Male 65-69')
        self._assert_demographic_values(store, 'Male 70-74')
        self._assert_demographic_values(store, 'Male 75-79')
        self._assert_demographic_values(store, 'Male 80-84')
        self._assert_demographic_values(store, 'Male >85', 1, 2, 150.0, 150.0)
        self._assert_demographic_values(store, 'Female <5')
        self._assert_demographic_values(store, 'Female 5-9')
        self._assert_demographic_values(store, 'Female 10-14')
        self._assert_demographic_values(store, 'Female 20-24')
        self._assert_demographic_values(store, 'Female 25-29')
        self._assert_demographic_values(store, 'Female 30-34')
        self._assert_demographic_values(store, 'Female 35-39')
        self._assert_demographic_values(store, 'Female 40-44')
        self._assert_demographic_values(store, 'Female 45-49')
        self._assert_demographic_values(store, 'Female 50-54')
        self._assert_demographic_values(store, 'Female 55-59')
        self._assert_demographic_values(store, 'Female 60-64')
        self._assert_demographic_values(store, 'Female 65-69')
        self._assert_demographic_values(store, 'Female 70-74')
        self._assert_demographic_values(store, 'Female 75-79')
        self._assert_demographic_values(store, 'Female 80-84')
        self._assert_demographic_values(store, 'Female >85')

    def _insert_default_entities(self):
        customer_id = "cid"
        store_id = "sid"

        self.rc_id = insert_test_retailer_customer(self.retailer_client_id, customer_id, 19)

        self.trx_id1 = insert_test_retailer_transaction(self.retailer_client_id, customer_id, 10.5,
                                                        datetime.datetime.now(), store_id)
        # this guy really likes j.crew clothes
        self.trx_id2 = insert_test_retailer_transaction(self.retailer_client_id, customer_id, 500000000.5,
                                                        datetime.datetime.now(), store_id)

        self.store_id = insert_test_retailer_store(self.retailer_client_id, store_id)


    def _insert_extra_entities(self):
        customer_id2 = "cid2"
        store_id = "sid"
        store_id2 = "sid2"

        self.rc_id2 = insert_test_retailer_customer(self.retailer_client_id, customer_id2, 96, "M")

        self.trx_id3 = insert_test_retailer_transaction(self.retailer_client_id, customer_id2, 100,
                                                        datetime.datetime.now(), store_id2)
        self.trx_id4 = insert_test_retailer_transaction(self.retailer_client_id, customer_id2, 50,
                                                        datetime.datetime.now(), store_id2)
        self.trx_id5 = insert_test_retailer_transaction(self.retailer_client_id, customer_id2, 10000,
                                                        datetime.datetime.now(), store_id)
        self.trx_id6 = insert_test_retailer_transaction(self.retailer_client_id, customer_id2, 1,
                                                        datetime.datetime.now(), store_id)

        self.store_id2 = insert_test_retailer_store(self.retailer_client_id, store_id2)

        customer_id3 = "cid3"
        self.rc_id3 = insert_test_retailer_customer(self.retailer_client_id, customer_id3, 16)
        self.trx_id7 = insert_test_retailer_transaction(self.retailer_client_id, customer_id3, 7,
                                                        datetime.datetime.now(), store_id)
        self.trx_id8 = insert_test_retailer_transaction(self.retailer_client_id, customer_id3, 24,
                                                        datetime.datetime.now(), store_id)
        self.trx_id9 = insert_test_retailer_transaction(self.retailer_client_id, customer_id3, 41,
                                                        datetime.datetime.now(), store_id)

    def _build_query(self):
        query = {"data.retailer_client_id": self.retailer_client_id}
        end_date = ltm_helper.get_default_ltm_end_date(self.context, self.retailer_client_id)
        start_date = end_date - datetime.timedelta(days=364)
        query["data.transaction_date"] = {"$gte": start_date, "$lte": end_date}
        return query

    def _assert_demographic_values(self, store, demographic_key, num_customers=0, num_trx=0, sum_sales=0, avg_sales_per_customer=0):
        gender, age_range = demographic_key.split()
        expected = {
            u'age_range': unicode(age_range),
            u'gender': unicode(gender),
            u'num_customers': num_customers,
            u'num_trx': num_trx,
            u'sum_sales': sum_sales,
            u'avg_sales_per_customer': avg_sales_per_customer
        }

        self.test_case.assertDictEqual(expected, store[0][1]['by_demographic'][demographic_key])


