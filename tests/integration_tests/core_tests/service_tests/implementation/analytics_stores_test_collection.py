from __future__ import division
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_store, insert_test_trade_area
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
import datetime
import random


class AnalyticsStoresTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "analytics_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.analytics_access.call_delete_reset_database()
        self.analytics_access.call_default_calcs_reload()

    def tearDown(self):
        pass


    #--------------------------------------------------------------------------
    # Tests Monthly Store Count and growth (fractional)
    #--------------------------------------------------------------------------
    def analytics_test_monthly_store_growth(self):

        # this is (month number, # of test stores to create with starting date in the month)
        month_stores = [(1, 1), (2, 1), (3, 1), (5, 2)]
        company = insert_test_company(ticker='ANC', name='AnalyticsCompany')
        now = datetime.datetime.utcnow()
        test_year = 2013

        expected_store_growth = []
        expected_store_count = []
        total_store_count = 0

        for item in month_stores:
            date = datetime.datetime(test_year, item[0],
                                     random.randint(1, 10))

            for i in range(item[1]):
                store_id = insert_test_store(company, interval=[date, None])
                #also insert trade areas
                insert_test_trade_area(store_id=store_id, company_id=company, company_name="ANC", opened_date=date,
                                       closed_date=None)

            result_date = datetime.datetime(test_year, item[0], 1)
            total_store_count += item[1]
            expected_store_count.append(
                {
                    'date': result_date,
                    'value': total_store_count
                }
            )

            fractional_increase = 0
            if total_store_count - item[1] > 0:
                fractional_increase = item[1] / (total_store_count - item[1])

            expected_store_growth.append(
                {
                    'date': result_date,
                    'value': fractional_increase
                }
            )

        ########### store count test ###########################################################
        calc1 = self._create_calc('Store Count By month', 'count # stores', 'store_count', 'monthly.store_count')

        run_params1 = self._create_run_params([company])
        run_params1['options']['save'] = True
        run_params1['options']['fetch'] = True
        run_params1['start_date'] = "{}-01-01".format(test_year)
        run_params1['end_date'] = "{}-06-01".format(test_year)

        calc_id1 = self.analytics_access.call_post_new_calc(calc1, self.context)
        result_doc1 = self.analytics_access.call_post_run_calc(calc_id1, run_params1, self.context)

        #check we have results
        self.test_case.assertEqual('results' in result_doc1, True)

        #check results for test company id are returned
        self.test_case.assertEqual(company in result_doc1['results'], True)

        #check store counts are ok for all dates
        results_list1 = result_doc1['results'][company]

        for expected in expected_store_count:
            result = next(item for item in results_list1 if item['date'] == expected['date'])
            self.test_case.assertEqual(result['value'], expected['value'])

        ########### store growth test ###########################################################
        calc = self._create_calc('Store Count By month growth', 'count # stores', 'store_growth', 'monthly.store_growth')
        calc['input']['entity_type'] = 'company'
        calc['input']['target_entity_field'] = '_id'
        calc['input']['fields'] = ["_id", 'data.analytics.monthly.store_count']

        run_params = self._create_run_params([company])
        run_params['options']['fetch'] = True

        calc_id = self.analytics_access.call_post_new_calc(calc, self.context)
        result_doc = self.analytics_access.call_post_run_calc(calc_id, run_params, self.context)

        #check we have results
        self.test_case.assertEqual('results' in result_doc, True)

        #check results for test company id are returned
        self.test_case.assertEqual(company in result_doc['results'], True)

        #check store counts are ok for all dates
        results_list = result_doc['results'][company]
        for expected in expected_store_growth:
            result = next(item for item in results_list if item['date'] == expected['date'])
            self.test_case.assertEqual(result['value'], expected['value'])

    #--------------------------------------------------------------------------
    # Privates
    #--------------------------------------------------------------------------

    def _create_calc(self, name, description, module, key, entity_type='store'):
        calc = {
            'name': name,
            'description': description,
            'engine': 'stores',
            'engine_module': module,
            'input': {
                'entity_type': 'trade_area',
                'target_entity_field': 'data.company_id',
                'entity_query': '{}',
                'fields': []
            },
            'output': {
                "key": "data.analytics.{}".format(key),
                'target_entity_type': 'company'
            }
        }
        return calc

    def _create_run_params(self, target_ids, fetch=False):
        run_params = {
            'target_entity_ids': target_ids,
            'target_entity_type': 'company',
            'options': {
                'save': False,
                'fetch': fetch,
                'return': True,
            }
        }
        return run_params
