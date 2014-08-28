from copy import deepcopy
from time import sleep
from bson.objectid import ObjectId
import datetime
import json
from common.utilities.date_utilities import parse_date
from core.common.business_logic.service_entity_logic import industry_helper, company_helper
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.geoprocessing_flags import GeoprocessingFlags
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.industry_rules.industry_rules import IndustryCompetitionChanged
from core.common.business_logic.service_entity_logic.trade_area_upserter import TradeAreaUpserter
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection

__author__ = 'kingneptune'


class WFSGeoprocessingRulesEvaluatorTestCollection(ServiceTestCollection):

    def initialize(self):

        self.context = {"user_id": ObjectId(), "source": 'geoprocessing_rules_test_collection'}

    def setUp(self):
        # delete when starting
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.test_case.maxDiff = None

    def tearDown(self):
        pass

    # _____________________________________________ store rules ______________________________________________________ #

    def test_EVALUATE_failed_last_geoprocessing_event(self):

        current_timestamp = datetime.datetime.utcnow()
        yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat()
        gp_data = {
            'latest_attempt': {
                'get_demographics': {
                    'result': 'failed',
                    'start_timestamp': yesterday,
                    'end_timestamp': yesterday
                },
                'find_competition': {
                    'result': 'success',
                    'start_timestamp': yesterday,
                    'end_timestamp': yesterday
                },
                'find_white_space_competition': {
                    'result': 'success',
                    'start_timestamp': yesterday,
                    'end_timestamp': yesterday
                },
            }
        }

        trade_area_data = {'woot': 'chicken', 'geoprocessing': gp_data}
        trade_area_id = self.main_access.mds.call_add_entity('trade_area', 'name', trade_area_data, self.context)

        task_rec = {
            'input': {
                'entity_type': 'trade_area',
                'entity_id': trade_area_id,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }

        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)
        # whitespace_20_mile_07_12_2013


        expected_data = {
            'needs_gp': {
                'find_competition': False,
                'get_demographics': True,
                'find_white_space_competition': False
            },
            "gp_rules": {
                "find_competition": {
                    "failed_latest_geoprocessing_event": {
                        "reason": "The latest 'find_competition' geoprocessing event was successful",
                        "needs_gp": False,
                        "flags": []
                    },
                    "flagged_for_gp_but_has_not_been_gpd": {
                        "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                        'needs_gp': False,
                        'flags': []
                    }
                },
                "find_white_space_competition": {
                    "failed_latest_geoprocessing_event": {
                        "reason": "The latest 'find_white_space_competition' geoprocessing event was successful",
                        "needs_gp": False,
                        "flags": []
                    },
                    "flagged_for_gp_but_has_not_been_gpd": {
                        "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                        'needs_gp': False,
                        'flags': []
                    }
                },
                "get_demographics": {
                    "failed_latest_geoprocessing_event": {
                        "reason": "The latest 'get_demographics' geoprocessing event failed",
                        "needs_gp": True,
                        "flags": []
                    },
                    "flagged_for_gp_but_has_not_been_gpd": {
                        "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                        'needs_gp': False,
                        'flags': []
                    }
                }
            }
        }

        # get the store
        query = {'_id': {'$in': [ObjectId(trade_area_id)]}}
        entity_fields = ['_id', 'data']
        params = {'query': query, 'entity_fields': entity_fields}
        entity_rec = self.main_access.mds.call_find_entities_raw('trade_area', params)[0]

        self.test_case.assertEqual(expected_data['needs_gp'], entity_rec['data']['geoprocessing']['needs_gp'])
        self.test_case.assertEqual(expected_data['gp_rules'], entity_rec['data']['geoprocessing']['gp_rules'])
        self.test_case.assertGreater(parse_date(entity_rec['data']['geoprocessing']['latest_validation_date']), current_timestamp)


    def test_EVALUATE_has_most_correct_link__never_geoprocessed__check_flags(self):
        """
        This test is massive so I'm giving it a doc string. Basically we need to make sure that when a store has
        a new most correct RIR and goes through the rules engine, that not only it gets flagged for competition,
        but that its potential competitors get the proper flag that say they need geoprocessing
        """

        current_timestamp = datetime.datetime.utcnow()
        primary_industry_id = self.main_access.mds.call_add_entity('industry', 'name', {}, self.context)

        # insert company information
        home_company_id = self.main_access.mds.call_add_entity('company', 'name', {'workflow': {'current': {'status': 'published'}}}, self.context)
        competitor_company_id_1 = self.main_access.mds.call_add_entity('company', 'name', {'workflow': {'current': {'status': 'published'}}}, self.context)

        # link both companies to the industry
        self.main_access.mds.call_add_link('company',
                                           home_company_id,
                                           'primary_industry_classification',
                                           'industry',
                                           primary_industry_id,
                                           'primary_industry',
                                           'industry_classification',
                                           self.context)

        self.main_access.mds.call_add_link('company',
                                           competitor_company_id_1,
                                           'primary_industry_classification',
                                           'industry',
                                           primary_industry_id,
                                           'primary_industry',
                                           'industry_classification',
                                           self.context)

        # industry competition
        self.main_access.mds.call_add_link('industry',
                                           primary_industry_id,
                                           'competitor',
                                           'industry',
                                           primary_industry_id,
                                           'competitor',
                                           'industry_competition',
                                           self.context)


        self.main_access.mds.call_add_link('company', home_company_id, 'competitor', 'company', competitor_company_id_1, 'competitor', 'company_competition', self.context)

        # insert home store and its address and its rir
        home_store_id = self.main_access.mds.call_add_entity('store', 'name', {'company_id': str(home_company_id)}, self.context)

        home_ta_data = {
            'longitude': 10.1,
            'latitude': 10.1,
            'geo': [10.1, 10.1],
            'store_id': str(home_store_id),
            'trade_area_threshold': 'DistanceMiles10',
            'analytics': {
                'shape': {
                    'shape_array': [[[12, 0], [0, 12], [-12, 0], [0, -12], [12, 0]]]
                }
            },
            'company_id': str(home_company_id)
        }
        home_rir_data = {
            'auto_parsed_address': {
                'longitude': 10.1,
                'latitude': 10.1,
            },
            'store_id': str(home_store_id),
            'trade_area_threshold': 'DistanceMiles10'
        }

        home_rir_id = self.main_access.mds.call_add_entity('retail_input_record', 'name', home_rir_data, self.context)
        home_trade_area_id = self.main_access.mds.call_add_entity('trade_area', 'name', home_ta_data, self.context)
        self.main_access.mds.call_add_link('store', home_store_id, 'store', 'retail_input_record', home_rir_id, 'most_correct_record', 'retail_input', self.context)


        # two competitor stores per company
        comp_store_1_1_id = self.main_access.mds.call_add_entity('store', 'name', {'company_id': str(competitor_company_id_1)}, self.context)
        comp_store_1_1_ta_data = {
            'longitude': 1.0,
            'latitude': -1.0,
            'geo': [1.0, -1.0],
            'company_ids': [str(competitor_company_id_1)],
            'store_id': str(comp_store_1_1_id),
            'trade_area_threshold': 'DistanceMiles10',
            'analytics': {
                'shape': {
                    'shape_array': [[[12, 0], [0, 12], [-12, 0], [0, -12], [12, 0]]]
                }
            },
            'company_id': competitor_company_id_1,
        }

        comp_store_1_1_trade_area_id = self.main_access.mds.call_add_entity('trade_area', 'name', comp_store_1_1_ta_data, self.context)

        # two competitor stores per company
        comp_store_1_2_id = self.main_access.mds.call_add_entity('store', 'name', {'company_id': str(competitor_company_id_1)}, self.context)
        comp_store_1_2_ta_data = {
            'longitude': 0.0,
            'latitude': 0.0,
            'geo': [0.0, 0.0],
            'company_ids': [str(competitor_company_id_1)],
            'store_id': str(comp_store_1_2_id),
            'trade_area_threshold': 'DistanceMiles10',
            'analytics': {
                'shape': {
                    'shape_array': [[[12, 0], [0, 12], [-12, 0], [0, -12], [12, 0]]]
                }
            },
            'company_id': competitor_company_id_1,
        }

        comp_store_1_2_trade_area_id = self.main_access.mds.call_add_entity('trade_area', 'name', comp_store_1_2_ta_data, self.context)

        # for now the timestamp of the new RIR is found through the link ID (seconds precision).
        # we sleep to ensure at least 1 second separation.
        sleep(1)

        task_rec = {
            'input': {
                'entity_type': 'store',
                'entity_id': home_store_id,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }

        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)

        expected_data = {
            "gp_rules": {
                "find_competition": {
                    "new_most_correct_rir": {
                        "reason": "There is a newly linked 'most correct' retail input record",
                        "flags": [
                            {
                                "affected_trade_area_ids": '_all_child_trade_areas',
                                "name": "new_potential_address"
                            }
                        ]
                    }
                },
                "find_white_space_competition": {
                    "new_most_correct_rir": {
                        "reason": "There is a newly linked 'most correct' retail input record",
                        "flags": [
                            {
                                "affected_trade_area_ids": '_all_child_trade_areas',
                                "name": "new_potential_address"
                            }
                        ]
                    }
                },
                "get_demographics": {
                    "new_most_correct_rir": {
                        "reason": "There is a newly linked 'most correct' retail input record",
                        "flags": [
                            {
                                "affected_trade_area_ids": '_all_child_trade_areas',
                                "name": "new_potential_address"
                            }
                        ]
                    }
                }
            }
        }

        # get the store
        query = {'_id': {'$in': [ObjectId(home_store_id)]}}
        entity_fields = ['_id', 'data']
        params = {'query': query, 'entity_fields': entity_fields}
        entity_rec = self.main_access.mds.call_find_entities_raw('store', params)[0]

        # make sure that the store has the right geoprocessing rules rec after it gets evaluated
        self.test_case.assertEqual(expected_data['gp_rules'], entity_rec['data']['geoprocessing']['gp_rules'])
        self.test_case.assertGreater(parse_date(entity_rec['data']['geoprocessing']['latest_validation_date']), current_timestamp)


        expected_home_data = {
            'flags': {},
            'geoprocessing': {
                'needs_gp': {
                    'find_competition': True,
                    'get_demographics': True,
                    'find_white_space_competition': True,
                },
                "gp_rules": {
                    "find_competition": {
                        "pick_up_new_potential_address_flag": {
                            "reason": "Found flag '%s'" % GeoprocessingFlags.NewPotentialAddress,
                            "needs_gp": True,
                            "flags": [{
                                'affected_trade_area_ids': [comp_store_1_1_trade_area_id, comp_store_1_2_trade_area_id],
                                'name': 'new_potential_trade_area_competition'
                            }]
                        },
                        "failed_latest_geoprocessing_event": {
                            "reason": "This trade area has never been geoprocessed for method '%s'" % 'find_competition',
                            "needs_gp": True,
                            "flags": []
                        },
                        "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                        }
                    },
                    "get_demographics": {
                        "pick_up_new_potential_address_flag": {
                            "reason": "Found flag '%s'" % GeoprocessingFlags.NewPotentialAddress,
                            "needs_gp": True,
                            "flags": []
                        },
                        "failed_latest_geoprocessing_event": {
                            "reason": "This trade area has never been geoprocessed for method '%s'" % 'get_demographics',
                            "needs_gp": True,
                            "flags": []
                        },
                        "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                        }
                    },
                    "find_white_space_competition": {
                        "pick_up_new_potential_address_flag": {
                            "reason": "Found flag '%s'" % GeoprocessingFlags.NewPotentialAddress,
                            "needs_gp": True,
                            "flags": []
                        },
                        "failed_latest_geoprocessing_event": {
                            "reason": "This trade area has never been geoprocessed for method '%s'" % 'find_white_space_competition',
                            "needs_gp": True,
                            "flags": []
                        },
                        "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                        }
                    },
                }
            }
        }

        expected_competition_data = {
            'flags': {},
            'geoprocessing': {
                'needs_gp': {
                    'find_competition': True,
                    'get_demographics': True,
                    'find_white_space_competition': True
                },
                "gp_rules": {
                    "find_competition": {
                        "pick_up_new_potential_trade_area_competition_flag": {
                            "reason": "Found flag '%s'" % GeoprocessingFlags.NewPotentialTradeAreaCompetition,
                            "needs_gp": True,
                            "flags": []
                        },
                        "failed_latest_geoprocessing_event": {
                            "reason": "This trade area has never been geoprocessed for method '%s'" % 'find_competition',
                            "needs_gp": True,
                            "flags": []
                        },
                        "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                        }
                    },
                    "get_demographics": {
                        "failed_latest_geoprocessing_event": {
                            "reason": "This trade area has never been geoprocessed for method '%s'" % 'get_demographics',
                            "needs_gp": True,
                            "flags": []
                        },
                        "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                        }
                    },
                    "find_white_space_competition": {
                        "failed_latest_geoprocessing_event": {
                            "reason": "This trade area has never been geoprocessed for method '%s'" % 'find_white_space_competition',
                            "needs_gp": True,
                            "flags": []
                        },
                        "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                        }
                    },
                }
            }
        }

        # now we have to look up the competitive stores and make sure they have flags.
        query = {'_id': {'$in': [ObjectId(home_trade_area_id), ObjectId(comp_store_1_1_trade_area_id), ObjectId(comp_store_1_2_trade_area_id)]}}
        entity_fields = ['_id', 'data']
        params = {'query': query, 'entity_fields': entity_fields}
        entity_recs = self.main_access.mds.call_find_entities_raw('trade_area', params)

        home_trade_area = entity_recs[0]
        competitive_trade_area_1 = entity_recs[1]
        competitive_trade_area_2 = entity_recs[2]


        self.test_case.assertEqual(expected_home_data['flags'], home_trade_area['data']['flags'])

        self.test_case.assertEqual(expected_home_data['geoprocessing']['needs_gp'], home_trade_area['data']['geoprocessing']['needs_gp'])

        expected_gp_rules = expected_home_data['geoprocessing']['gp_rules']
        actual_gp_rules = home_trade_area['data']['geoprocessing']['gp_rules']

        self.test_case.assertEqual(expected_gp_rules['get_demographics'], actual_gp_rules['get_demographics'])

        self.test_case.assertEqual(expected_gp_rules['find_competition']['failed_latest_geoprocessing_event'],
                                   actual_gp_rules['find_competition']['failed_latest_geoprocessing_event'])

        self.test_case.assertEqual(expected_gp_rules['find_competition']['pick_up_new_potential_address_flag']['reason'],
                                   actual_gp_rules['find_competition']['pick_up_new_potential_address_flag']['reason'])

        self.test_case.assertEqual(expected_gp_rules['find_competition']['pick_up_new_potential_address_flag']['needs_gp'],
                                   actual_gp_rules['find_competition']['pick_up_new_potential_address_flag']['needs_gp'])

        self.test_case.assertEqual(len(expected_gp_rules['find_competition']['pick_up_new_potential_address_flag']['flags']),
                                   len(actual_gp_rules['find_competition']['pick_up_new_potential_address_flag']['flags']))

        expected_flag = expected_gp_rules['find_competition']['pick_up_new_potential_address_flag']['flags'][0]
        actual_flag = actual_gp_rules['find_competition']['pick_up_new_potential_address_flag']['flags'][0]

        self.test_case.assertEqual(expected_flag['name'], actual_flag['name'])
        self.test_case.assertEqual(len(expected_flag['affected_trade_area_ids']), len(actual_flag['affected_trade_area_ids']))
        self.test_case.assertEqual(set(expected_flag['affected_trade_area_ids']), set(actual_flag['affected_trade_area_ids']))

        # test that the flags were raised
        self.test_case.assertEqual(expected_competition_data['flags'], competitive_trade_area_1['data']['flags'])
        self.test_case.assertEqual(expected_competition_data['flags'], competitive_trade_area_2['data']['flags'])

        self.test_case.assertEqual(expected_competition_data['geoprocessing']['needs_gp'], competitive_trade_area_1['data']['geoprocessing']['needs_gp'])
        self.test_case.assertEqual(expected_competition_data['geoprocessing']['gp_rules'], competitive_trade_area_1['data']['geoprocessing']['gp_rules'])


        self.test_case.assertEqual(expected_competition_data['geoprocessing']['needs_gp'], competitive_trade_area_2['data']['geoprocessing']['needs_gp'])
        self.test_case.assertEqual(expected_competition_data['geoprocessing']['gp_rules'], competitive_trade_area_2['data']['geoprocessing']['gp_rules'])



    def test_EVALUATE_is_published__check_flags(self):

        # insert company information
        home_company_id = self.main_access.mds.call_add_entity('company', 'name', {'workflow': {'current': {'status': 'published'}}}, self.context)

        # insert home trade area
        home_ta_data = {
            'longitude': 10.1,
            'latitude': 10.1,
            'company_id': home_company_id
        }

        self.main_access.mds.call_add_entity('trade_area', 'name', home_ta_data, self.context)

        task_rec = {
            'input': {
                'entity_type': 'company',
                'entity_id': home_company_id,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }
        before_rules_time = datetime.datetime.utcnow()
        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)

        # get the company rec
        query = {'_id': ObjectId(home_company_id)}
        entity_fields = ['_id', 'data']
        params = {'query': query, 'entity_fields': entity_fields}
        entity_rec = self.main_access.mds.call_find_entities_raw('company', params)[0]

        expected_geo_data = {
            'gp_rules': {
                'find_competition': {
                    'is_published': {
                        'reason': "This company's trade areas have not been flagged for geoprocessing after its status changed to 'published'",
                        'flags': [{
                            'affected_trade_area_ids': '_all_child_trade_areas',
                            'name': 'parent_company_status_switched_to_published'
                        }]
                    },
                    'has_new_industry_classification': {
                        'reason': "There has not been a change to this company's industry classification",
                        'flags': []
                    }
                },
                'get_demographics': {
                    'is_published': {
                        'reason': "This company's trade areas have not been flagged for geoprocessing after its status changed to 'published'",
                        'flags': [{
                            'affected_trade_area_ids': '_all_child_trade_areas',
                            'name': 'parent_company_status_switched_to_published'
                        }]
                    }
                },
                'find_white_space_competition': {
                    'is_published': {
                        'reason': "This company's trade areas have not been flagged for geoprocessing after its status changed to 'published'",
                        'flags': [{
                            'affected_trade_area_ids': '_all_child_trade_areas',
                            'name': 'parent_company_status_switched_to_published'
                        }]
                    }
                }
            }
        }

        self.test_case.assertEqual(expected_geo_data['gp_rules'], entity_rec['data']['geoprocessing']['gp_rules'])
        self.test_case.assertGreater(parse_date(entity_rec['data']['geoprocessing']['latest_validation_date']), before_rules_time)


        # get the trade area of the store
        query = {'data.company_id': home_company_id}
        entity_fields = ['_id', 'data']
        params = {'query': query, 'entity_fields': entity_fields}
        entity_rec = self.main_access.mds.call_find_entities_raw('trade_area', params)[0]

        expected_ta_geo_data = {
            'needs_gp': {
                'find_competition': True,
                'get_demographics': True,
                'find_white_space_competition': True
            },
            'gp_rules': {
                'find_competition': {
                    'pick_up_parent_company_status_switched_to_published_flag': {
                        'needs_gp': True,
                        'reason': "Found flag 'parent_company_status_switched_to_published'",
                        'flags': []
                    },
                    'failed_latest_geoprocessing_event': {
                        'needs_gp': True,
                        'reason': "This trade area has never been geoprocessed for method 'find_competition'",
                        'flags': []
                    },
                    "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                    }
                },
                'get_demographics': {
                    'pick_up_parent_company_status_switched_to_published_flag': {
                        'needs_gp': True,
                        'reason': "Found flag 'parent_company_status_switched_to_published'",
                        'flags': []
                    },
                    'failed_latest_geoprocessing_event': {
                        'needs_gp': True,
                        'reason': "This trade area has never been geoprocessed for method 'get_demographics'",
                        'flags': []
                    },
                    "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                    }
                },
                'find_white_space_competition': {
                    'pick_up_parent_company_status_switched_to_published_flag': {
                        'needs_gp': True,
                        'reason': "Found flag 'parent_company_status_switched_to_published'",
                        'flags': []
                    },
                    'failed_latest_geoprocessing_event': {
                        'needs_gp': True,
                        'reason': "This trade area has never been geoprocessed for method 'find_white_space_competition'",
                        'flags': []
                    },
                    "flagged_for_gp_but_has_not_been_gpd": {
                            "reason": 'This trade area has not been flagged for geoprocessing for this method.',
                            'needs_gp': False,
                            'flags': []
                    }
                }
            }
        }

        self.test_case.assertEqual(expected_ta_geo_data['needs_gp'], entity_rec['data']['geoprocessing']['needs_gp'])
        self.test_case.assertEqual(expected_ta_geo_data['gp_rules'], entity_rec['data']['geoprocessing']['gp_rules'])
        self.test_case.assertGreater(parse_date(entity_rec['data']['geoprocessing']['latest_validation_date']), before_rules_time)

    # ____________________________________________ industry rules ____________________________________________ #

    def test_EVALUATE_industry_competition_changed__created(self):

        context = {
            'user_id': 42,
            'source': 'test_EVALUATE_industry_competition_changed__created'
        }

        # create industries
        industry_id_1 = self.main_access.mds.call_add_entity('industry', 'name', {'random': 'data'}, self.context)
        industry_id_2 = self.main_access.mds.call_add_entity('industry', 'name', {'random': 'data'}, self.context)

        # competition data
        c_data = {
            'from_industry': industry_id_1,
            'to_industry': industry_id_2,
            'competition_strength': 1.0
        }

        # create competition
        link_data = {
            "competition_strength": float(c_data["competition_strength"])
        }

        # create competition
        self.main_access.mds.call_add_link("industry", c_data["from_industry"], "competitor",
                                           "industry", c_data["to_industry"], "competitor",
                                           "industry_competition", context, link_data = link_data)

        # get the industry recs
        entity_fields = ['_id', 'meta', 'data', 'entity_type']
        industry_1_rec = self.main_access.mds.call_find_entities_raw('industry', {'query': {'_id': ObjectId(industry_id_1)}, 'entity_fields': entity_fields})[0]
        industry_2_rec = self.main_access.mds.call_find_entities_raw('industry', {'query': {'_id': ObjectId(industry_id_2)}, 'entity_fields': entity_fields})[0]

        # evaluate
        methods_decisions_1 = IndustryCompetitionChanged(industry_1_rec).evaluate()
        methods_decisions_2 = IndustryCompetitionChanged(industry_2_rec).evaluate()


        expected_methods_decisions = {
            'find_competition': {
                'reason': "There has been a change to this industry's competition",
                'flags': [
                    {
                        'affected_trade_area_ids': '_all_child_trade_areas',
                        'name': 'parent_industry_competition_changed'
                    }
                ]
            },
            'find_white_space_competition': None,
            'get_demographics': None
        }

        self.test_case.assertEqual(expected_methods_decisions, methods_decisions_1)
        self.test_case.assertEqual(expected_methods_decisions, methods_decisions_2)

    def test_EVALUATE_industry_competition_changed__deleted(self):

        context = {
            'user_id': 42,
            'source': 'test_EVALUATE_industry_competition_changed__created'
        }

        # create industries
        industry_id_1 = self.main_access.mds.call_add_entity('industry', 'name', {'random': 'data'}, self.context)
        industry_id_2 = self.main_access.mds.call_add_entity('industry', 'name', {'random': 'data'}, self.context)

        # competition data
        c_data = {
            'from_industry': industry_id_1,
            'to_industry': industry_id_2,
            'competition_strength': 1.0
        }

        link_data = {
            "competition_strength": float(c_data["competition_strength"])
        }

        # create competition
        link_id = self.main_access.mds.call_add_link("industry", c_data["from_industry"], "competitor",
                                                     "industry", c_data["to_industry"], "competitor",
                                                     "industry_competition", context, link_data = link_data)[0]["_id"]

        task_rec = {
            'input': {
                'entity_type': 'industry',
                'entity_id': industry_id_1,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }

        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)

        task_rec = {
            'input': {
                'entity_type': 'industry',
                'entity_id': industry_id_2,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }

        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)

        expected_methods_decisions = {
            'reason': "There has been a change to this industry's competition",
            'flags': [
                {
                    'affected_trade_area_ids': '_all_child_trade_areas',
                    'name': 'parent_industry_competition_changed'
                }
            ]
        }

        entity_fields = ['_id', 'meta', 'data', 'entity_type']
        industry_1_rec = self.main_access.mds.call_find_entities_raw('industry', {'query': {'_id': ObjectId(industry_id_1)}, 'entity_fields': entity_fields})[0]
        industry_2_rec = self.main_access.mds.call_find_entities_raw('industry', {'query': {'_id': ObjectId(industry_id_2)}, 'entity_fields': entity_fields})[0]

        self.test_case.assertEqual(expected_methods_decisions, industry_1_rec['data']['geoprocessing']['gp_rules']['find_competition']['industry_competition_changed'])
        self.test_case.assertEqual(expected_methods_decisions, industry_2_rec['data']['geoprocessing']['gp_rules']['find_competition']['industry_competition_changed'])

        # now, re-evaluate, make sure there hasn't been a change
        task_rec = {
            'input': {
                'entity_type': 'industry',
                'entity_id': industry_id_1,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }

        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)

        task_rec = {
            'input': {
                'entity_type': 'industry',
                'entity_id': industry_id_2,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }

        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)

        expected_methods_decisions = {
            'reason': "There has not been a change to this industry's competition",
            'flags': []
        }

        entity_fields = ['_id', 'meta', 'data', 'entity_type']
        industry_1_rec = self.main_access.mds.call_find_entities_raw('industry', {'query': {'_id': ObjectId(industry_id_1)}, 'entity_fields': entity_fields})[0]
        industry_2_rec = self.main_access.mds.call_find_entities_raw('industry', {'query': {'_id': ObjectId(industry_id_2)}, 'entity_fields': entity_fields})[0]

        self.test_case.assertEqual(expected_methods_decisions, industry_1_rec['data']['geoprocessing']['gp_rules']['find_competition']['industry_competition_changed'])
        self.test_case.assertEqual(expected_methods_decisions, industry_2_rec['data']['geoprocessing']['gp_rules']['find_competition']['industry_competition_changed'])

        # now delete the competition link
        self.main_access.mds.call_del_link("industry", industry_id_1, "industry", industry_id_2, link_id)

        task_rec = {
            'input': {
                'entity_type': 'industry',
                'entity_id': industry_id_1,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }

        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)

        task_rec = {
            'input': {
                'entity_type': 'industry',
                'entity_id': industry_id_2,
                'evaluate_trade_area_rules_asynchronously': False
            },
            'meta': {
                'async': False
            }
        }

        self.main_access.wfs.call_task_new('retail_analytics', 'geoprocessing',
                                           'evaluate_geoprocessing_rules', task_rec, self.context)

        expected_methods_decisions = {
            'reason': "There has been a change to this industry's competition",
            'flags': [
                {
                    'affected_trade_area_ids': '_all_child_trade_areas',
                    'name': 'parent_industry_competition_changed'
                }
            ]
        }

        entity_fields = ['_id', 'meta', 'data', 'entity_type']
        industry_1_rec = self.main_access.mds.call_find_entities_raw('industry', {'query': {'_id': ObjectId(industry_id_1)}, 'entity_fields': entity_fields})[0]
        industry_2_rec = self.main_access.mds.call_find_entities_raw('industry', {'query': {'_id': ObjectId(industry_id_2)}, 'entity_fields': entity_fields})[0]

        self.test_case.assertEqual(expected_methods_decisions, industry_1_rec['data']['geoprocessing']['gp_rules']['find_competition']['industry_competition_changed'])
        self.test_case.assertEqual(expected_methods_decisions, industry_2_rec['data']['geoprocessing']['gp_rules']['find_competition']['industry_competition_changed'])
