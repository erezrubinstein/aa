from __future__ import division
import pprint
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_rir
from common.utilities.inversion_of_control import Dependency

__author__ = "irsalmashhor"


class EntityMatcherTestCollection(ServiceTestCollection):
    def initialize(self, data_params=None):
        pass

    def setUp(self):
        self.entity_matcher_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def entity_matcher_test_entity_vs_entity_exact_match(self):
        test_company_id = insert_test_company()
        test_rir_id = insert_test_rir(self.context, test_company_id, '1')
        exact_match_rir_id = insert_test_rir(self.context, test_company_id, '1')

        result = self.entity_matcher_access.call_match_entity_vs_entity('retail_input_record', test_rir_id, exact_match_rir_id)
        test_rir_results = result["details"][test_rir_id]

        self.test_case.assertEqual("exact", test_rir_results[exact_match_rir_id]["category"])
        self.test_case.assertEqual("match", test_rir_results[exact_match_rir_id]["matcher_prediction"])
        self.test_case.assertEqual(test_rir_results[exact_match_rir_id]["score"], 1)

    def entity_matcher_test_entity_vs_entity_auto_link(self):
        test_company_id = insert_test_company()
        test_rir_id = insert_test_rir(self.context, test_company_id)

        # as a result of preprocessing or diff-ing strategies, these should all get perfect scores and be auto_linked.
        longlat_diff_id = insert_test_rir(self.context, test_company_id, longitude=-80.104, latitude=40.004 )
        caps_diff_id = insert_test_rir(self.context, test_company_id, address='123 MAIN ST')
        whitespace_diff_id = insert_test_rir(self.context, test_company_id, address=' 123 MAIN ST ', city=' UNIT_TEST_VILLE ')
        phone_diff_id = insert_test_rir(self.context, test_company_id, phone='555.867.5309')
        zip_diff_id = insert_test_rir(self.context, test_company_id, zip_code='12345-2234')

        test_ids = [longlat_diff_id, caps_diff_id, whitespace_diff_id, phone_diff_id, zip_diff_id]

        for auto_link_id in test_ids:
            result = self.entity_matcher_access.call_match_entity_vs_entity('retail_input_record', test_rir_id,
                                                                            auto_link_id, {"explain": True})
            test_rir_results = result["details"][test_rir_id]

            self.test_case.assertEqual("auto_linkable", test_rir_results[auto_link_id]["category"])
            self.test_case.assertEqual("match", test_rir_results[auto_link_id]["matcher_prediction"])
            self.test_case.assertGreater(test_rir_results[auto_link_id]["score"], 0.99)


    def entity_matcher_test_entity_vs_entity_inexact_match(self):
        test_company_id = insert_test_company()
        address = '260 Park Ave.'
        zipcode = '11101'
        city = 'Manhattan'
        c = 'Microsoft'

        comparable_id = insert_test_rir(self.context, test_company_id, '1', None, c, address, city, 'NY', zipcode)

        # Create a few records which are different in small ways
        addr_id = insert_test_rir(self.context, test_company_id, '1', None, c, "270 Park Ave. S.", city, 'NY', zipcode)
        city_id = insert_test_rir(self.context, test_company_id, '1', None, c, address, 'New York', 'NY', zipcode)
        zip_id  = insert_test_rir(self.context, test_company_id, '1', None, c, address, city, 'NY', '11100')
        long_id = insert_test_rir(self.context, test_company_id, '1', None, c, address, city, 'NY', zipcode, longitude=-80.11)
        lat_id  = insert_test_rir(self.context, test_company_id, '1', None, c, address, city, 'NY', zipcode, latitude=40.01)
        mult_id = insert_test_rir(self.context, test_company_id, '1', None, c, address + " S.", 'New York', 'NY', '11100')

        different_ids = [addr_id, city_id, zip_id, long_id, lat_id, mult_id]

        # Assert for all the inexact records
        for rir_id in different_ids:
            result = self.entity_matcher_access.call_match_entity_vs_entity('retail_input_record', comparable_id, rir_id)
            test_rir_results = result["details"][comparable_id]

            self.test_case.assertEqual("inexact", test_rir_results[rir_id]["category"])
            self.test_case.assertEqual("match", test_rir_results[rir_id]["matcher_prediction"])
            self.test_case.assertGreater(test_rir_results[rir_id]["score"], 0.59)

    def entity_matcher_test_entity_vs_entity_mismatch(self):
        test_company_id = insert_test_company()
        test_rir_id = insert_test_rir(self.context, test_company_id, '1')
        mismatch_rir_id = insert_test_rir(self.context, test_company_id, '50', None, 'XYC', '99 Elm St',
                                          'Townsville', 'NY', '95123', 111.0, 32.1)

        result = self.entity_matcher_access.call_match_entity_vs_entity('retail_input_record', test_rir_id, mismatch_rir_id)

        self.test_case.assertEqual(set(result.keys()), {"details", "summary"})
        self.test_case.assertEqual(result, {"details": {},
                                            "summary": {"exact": {},
                                                        "auto_linkable": {},
                                                        "inexact": {},
                                                        "none": [test_rir_id]}})

    def entity_matcher_test_entity_vs_set(self):
        test_company_id = insert_test_company()
        test_rir_id = insert_test_rir(self.context, test_company_id, '1', address = "123 Main St", phone="(123) 456-7890")
        exact_match_rir_id = insert_test_rir(self.context, test_company_id, '1', address = "123 Main St", phone="(123) 456-7890")
        auto_linkable_rir_id = insert_test_rir(self.context, test_company_id, '1', address = "123 Main St", phone="123.456.7890")
        inexact_address_rir_id = insert_test_rir(self.context, test_company_id, '1', address = "555 Main St", phone="(123) 456-7890")
        absent_rir_id = insert_test_rir(self.context, test_company_id, '50', None, 'XYC', '99 Elm St',
                                         'Townsville', 'NY', '95123', "(123) 456-7890", 111.0, 32.1, )

        param_builder = Dependency("CoreAPIParamsBuilder").value
        query = {"_id": {"$in" : [exact_match_rir_id, auto_linkable_rir_id, inexact_address_rir_id, absent_rir_id] }}
        entity_fields = ["links", "data", "_id", "entity_type"]
        params = param_builder.mds.create_params(resource = "find_entities_raw", query = query, entity_fields = entity_fields, flatten = True)

        result = self.entity_matcher_access.call_match_entity_vs_set('retail_input_record', test_rir_id, params['params'])
        #pprint.pprint(result)

        test_rir_results = result["details"][test_rir_id]
        self.test_case.assertEqual("exact", test_rir_results[exact_match_rir_id]["category"])
        self.test_case.assertEqual("auto_linkable", test_rir_results[auto_linkable_rir_id]["category"])
        self.test_case.assertEqual("inexact", test_rir_results[inexact_address_rir_id]["category"])
        self.test_case.assertEqual("match", test_rir_results[inexact_address_rir_id]["matcher_prediction"])
        self.test_case.assertGreater(test_rir_results[inexact_address_rir_id]["score"], 0.9)
        self.test_case.assertNotIn(absent_rir_id, test_rir_results)

    def entity_matcher_test_set_vs_set(self):
        test_company_id = insert_test_company()
        test_rir_id = insert_test_rir(self.context, test_company_id, '1', address = "123 Main St", phone="(123) 456-7890")
        exact_match_rir_id = insert_test_rir(self.context, test_company_id, '1', address = "123 Main St", phone="(123) 456-7890")
        auto_linkable_rir_id = insert_test_rir(self.context, test_company_id, '1', address = "123 Main St", phone="123.456.7890")
        inexact_address_rir_id = insert_test_rir(self.context, test_company_id, '1', address = "555 Main St", phone="(123) 456-7890")
        absent_rir_id = insert_test_rir(self.context, test_company_id, '50', None, 'XYC', '99 Elm St',
                                         'Townsville', 'NY', '95123', "(123) 456-7890", 111.0, 32.1, )

        param_builder = Dependency("CoreAPIParamsBuilder").value
        query = {"_id": {"$in" : [test_rir_id, exact_match_rir_id, auto_linkable_rir_id, inexact_address_rir_id, absent_rir_id] }}
        entity_fields = ["links", "data", "_id", "entity_type"]
        params = param_builder.mds.create_params(resource = "find_entities_raw", query = query, entity_fields = entity_fields, flatten = True)

        # Reuse the same params
        result = self.entity_matcher_access.call_match_set_vs_set('retail_input_record', params['params'], params['params'])
        #pprint.pprint(result)

        # Verify results for initial test_rir
        test_rir_results = result["details"][test_rir_id]
        self.test_case.assertEqual("match", test_rir_results[test_rir_id]["matcher_prediction"])
        self.test_case.assertEqual("exact", test_rir_results[exact_match_rir_id]["category"])
        self.test_case.assertEqual("auto_linkable", test_rir_results[auto_linkable_rir_id]["category"])
        self.test_case.assertEqual("inexact", test_rir_results[inexact_address_rir_id]["category"])
        self.test_case.assertEqual("match", test_rir_results[inexact_address_rir_id]["matcher_prediction"])
        self.test_case.assertGreater(test_rir_results[inexact_address_rir_id]["score"], 0.9)
        self.test_case.assertNotIn(absent_rir_id, test_rir_results)

        # Verify results for the exact match rir
        test_rir_results = result["details"][exact_match_rir_id]
        self.test_case.assertEqual("match", test_rir_results[exact_match_rir_id]["matcher_prediction"])
        self.test_case.assertEqual("exact", test_rir_results[test_rir_id]["category"])
        self.test_case.assertEqual("auto_linkable", test_rir_results[auto_linkable_rir_id]["category"])
        self.test_case.assertEqual("inexact", test_rir_results[inexact_address_rir_id]["category"])
        self.test_case.assertEqual("match", test_rir_results[inexact_address_rir_id]["matcher_prediction"])
        self.test_case.assertGreater(test_rir_results[inexact_address_rir_id]["score"], 0.9)
        self.test_case.assertNotIn(absent_rir_id, test_rir_results)

        # Verify results for the inexact match rir
        test_rir_results = result["details"][inexact_address_rir_id]
        self.test_case.assertEqual("match", test_rir_results[inexact_address_rir_id]["matcher_prediction"])
        self.test_case.assertEqual("inexact", test_rir_results[test_rir_id]["category"])
        self.test_case.assertEqual("match", test_rir_results[test_rir_id]["matcher_prediction"])
        self.test_case.assertGreater(test_rir_results[test_rir_id]["score"], 0.9)
        self.test_case.assertEqual("inexact", test_rir_results[auto_linkable_rir_id]["category"])
        self.test_case.assertEqual("inexact", test_rir_results[exact_match_rir_id]["category"])
        self.test_case.assertEqual("match", test_rir_results[exact_match_rir_id]["matcher_prediction"])
        self.test_case.assertGreater(test_rir_results[exact_match_rir_id]["score"], 0.9)
        self.test_case.assertNotIn(absent_rir_id, test_rir_results)

        # Verify results for the mismatch rir
        test_rir_results = result["details"][absent_rir_id]
        self.test_case.assertEqual("match", test_rir_results[absent_rir_id]["matcher_prediction"])
        self.test_case.assertNotIn(test_rir_id, test_rir_results)
        self.test_case.assertNotIn(exact_match_rir_id, test_rir_results)
        self.test_case.assertNotIn(inexact_address_rir_id, test_rir_results)

    def entity_matcher_get_refdata(self):

        result = self.entity_matcher_access.call_get_reference_data()

        self.test_case.assertItemsEqual(result.keys(), ["retail_input_record"])
        rir_keys = ['matcher_params', 'record_format', 'pair_selector_params', 'diff_params', 'pair_matcher_params']
        self.test_case.assertItemsEqual(result["retail_input_record"].keys(), rir_keys)


    def entity_matcher_train_retail_input_records(self):

        result = self.entity_matcher_access.call_train_entity_matcher("retail_input_record")

        self.test_case.assertTrue("data" in result)
        main_keys = ["old_dists", "new_dists", "test_results", "distribution_charts", "meta", "old_params", "new_params"]

        for k in main_keys:
            self.test_case.assertTrue(k in result["data"])

        diff_params = {
                "string_smith_waterman": {
                    "method": "STRING_SMITH_WATERMAN",
                    "params": {
                        "score_matrix": {
                            "method": "STANDARD",
                            "params": {
                                "score_lowercase_match": 10,
                                "score_lowercase_mismatch": -4,
                                "score_uppercase_match": 10,
                                "score_uppercase_mismatch": -4,
                                "score_digit_match": 10,
                                "score_digit_mismatch": -4,
                                "score_punctuation_match": 5,
                                "score_punctuation_mismatch": -1,
                                "score_lowercase_uppercase_match": 9,
                                "score_lowercase_uppercase_mismatch": -5,
                                "score_lowercase_digit_mismatch": -5,
                                "score_lowercase_punctuation_mismatch": -5,
                                "score_uppercase_digit_mismatch": -5,
                                "score_uppercase_punctuation_mismatch": -5,
                                "score_digit_punctuation_mismatch": -2
                            }
                        },
                        "gap_score": -5, "min_score": 0, "max_score": 1000 }
                },
                "string_ngram": { "method": "STRING_NGRAM", "params": { "ngram_length": 2 } },
                "string_partial_ratio": { "method": "STRING_PARTIAL_RATIO", "params": { "num_bins": 11 } },
                "string_zipcode": { "method": "STRING_ZIPCODE", "params": { "num_bins": 11 } },
                "float_approximate": { "method": "FLOAT_APPROXIMATE", "params": { "tolerance": 0.005, "num_bins": 11 } },
                "exact": { "method": "EXACT", "params": {} }
            }
        self.test_case.assertDictEqual(result["data"]["old_params"]["record_params"]["retail_input_record"]["diff_params"], diff_params)
        self.test_case.assertDictEqual(result["data"]["new_params"]["record_params"]["retail_input_record"]["diff_params"], diff_params)
