from bson.objectid import ObjectId
import datetime
import json
import mox
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic.geoprocessing_rules.evaluate_need_for_geoprocessing import EvaluateNeedForGeoprocessing

__author__ = 'kingneptune'

class EvaluateNeedForGeoprocessingTests(mox.MoxTestBase):

    def setUp(self):

        super(EvaluateNeedForGeoprocessingTests, self).setUp()

        self.evaluator = self.mox.CreateMock(EvaluateNeedForGeoprocessing)
        self.evaluator.entity_id = str(ObjectId())
        self.evaluator.entity_type = 'red_panda'
        self.evaluator.rule_containers = {
            'red_panda': RedPandaRuleContainer,
            'trade_area': MockTradeAreaRuleContainer
        }

        self.evaluator._main_access = self.mox.CreateMockAnything()
        self.evaluator._main_access.mds = self.mox.CreateMockAnything()
        self.evaluator._main_params = self.mox.CreateMockAnything()
        self.evaluator._main_params.mds = self.mox.CreateMockAnything()

        self.evaluator._geoprocessing_methods = ['eat', 'sleep']
        self.evaluator.gp_rules = {}
        self.evaluator.flags = {}

    def doCleanups(self):
        super(EvaluateNeedForGeoprocessingTests, self).doCleanups()


    def test_evaluate_need_for_geoprocessing(self):

        self.evaluator._initialize_gp_rules()
        self.evaluator._get_entity_rec()
        self.evaluator._evaluate_rules_and_construct_outcome()
        self.evaluator._create_master_decision_and_gp_data().AndReturn({'This is': 'mocked GP data'})
        self.evaluator._construct_update_query().AndReturn('This is an update query')
        self.evaluator._construct_update_command({'This is': 'mocked GP data'}).AndReturn('This is an update command')
        self.evaluator.flags = 'flags'

        self.mox.ReplayAll()

        outcome = EvaluateNeedForGeoprocessing.evaluate_need_for_geoprocessing(self.evaluator)

        self.assertEqual({
            'update_query': 'This is an update query',
            'update_operations': 'This is an update command',
            'flags': 'flags'
        }, outcome)


    def test_initialize_gp_rules(self):

        EvaluateNeedForGeoprocessing._initialize_gp_rules(self.evaluator)
        self.assertEqual({
            'eat': {},
            'sleep': {}
        }, self.evaluator.gp_rules)


    def test_evaluate_rules_and_construct_outcome__not_trade_area(self):

        self.evaluator.entity_type = 'red_panda'
        self.evaluator._entity_rec = {'_id': 42}

        EvaluateNeedForGeoprocessing._initialize_gp_rules(self.evaluator)
        EvaluateNeedForGeoprocessing._evaluate_rules_and_construct_outcome(self.evaluator)

        self.assertEqual({
            'eat': {
                'bill': {
                    'reason': 'I am hungry',
                    'flags': [
                        {
                            'name': 'food flag',
                            'affected_store_ids': 'all_pandas'
                        }
                    ]
                },
                'ted': {
                    'reason': 'I am very hungry',
                    'flags': [
                        {
                            'name': 'very food flag',
                            'affected_store_ids': 'all_pandas'
                        }
                    ]
                }
            },
            'sleep': {
                'bill': {
                    'reason': 'I am tired',
                    'flags': [
                        {
                            'name': 'sleep flag',
                            'affected_store_ids': 'all_pandas'
                        }
                    ]
                },
                'ted': {
                    'reason': 'I am very tired',
                    'flags': [
                        {
                            'name': 'very sleep flag',
                            'affected_store_ids': 'all_pandas'
                        }
                    ]
                }
            }
        }, self.evaluator.gp_rules)

    def test_evaluate_rules_and_construct_outcome__trade_area(self):

        self.evaluator.entity_type = 'trade_area'
        self.evaluator._entity_rec = {'_id': 42}

        EvaluateNeedForGeoprocessing._initialize_gp_rules(self.evaluator)
        EvaluateNeedForGeoprocessing._evaluate_rules_and_construct_outcome(self.evaluator)

        self.assertEqual({
            'eat': {
                'bill': {
                    'needs_gp': True,
                    'reason': 'I am hungry',
                    'flags': []
                },
                'ted': {
                    'needs_gp': True,
                    'reason': 'I am very hungry',
                    'flags': []
                }
            },
            'sleep': {
                'bill': {
                    'needs_gp': True,
                    'reason': 'I am tired',
                    'flags': []
                },
                'ted': {
                    'needs_gp': True,
                    'reason': 'I am very tired',
                    'flags': []
                }
            }
        }, self.evaluator.gp_rules)


    def test_construct_update_query(self):

        update_query = EvaluateNeedForGeoprocessing._construct_update_query(self.evaluator)
        self.assertEqual({'_id': ObjectId(self.evaluator.entity_id)}, update_query)

    def test_create_master_decision_and_gp_data__store(self):
        self.maxDiff = None
        self.evaluator.entity_type = 'red_panda'
        self.evaluator._entity_rec = {'_id': 42}

        EvaluateNeedForGeoprocessing._initialize_gp_rules(self.evaluator)
        EvaluateNeedForGeoprocessing._evaluate_rules_and_construct_outcome(self.evaluator)

        self.evaluator._construct_initial_gp_data().AndReturn({
            'latest_validation_date': 'now',
            'gp_rules': self.evaluator.gp_rules
        })

        self.mox.ReplayAll()

        gp_data = EvaluateNeedForGeoprocessing._create_master_decision_and_gp_data(self.evaluator)

        self.assertEqual({
            'sleep': [
                {
                    'name': 'sleep flag',
                    'affected_store_ids': 'all_pandas'
                },
                {
                    'name': 'very sleep flag',
                    'affected_store_ids': 'all_pandas'
                }
            ],
            'eat': [
                {
                    'name': 'food flag',
                    'affected_store_ids': 'all_pandas'
                },
                {
                    'name': 'very food flag',
                    'affected_store_ids': 'all_pandas'
                }
            ]
        }, self.evaluator.flags)

        self.assertEqual({
            'latest_validation_date': 'now',
            'gp_rules': {
                'eat': {
                    'bill': {
                        'reason': 'I am hungry',
                        'flags': [
                            {
                                'name': 'food flag',
                                'affected_store_ids': 'all_pandas'
                            }
                        ]
                    },
                    'ted': {
                        'reason': 'I am very hungry',
                        'flags': [
                            {
                                'name': 'very food flag',
                                'affected_store_ids': 'all_pandas'
                            }
                        ]
                    }
                },
                'sleep': {
                    'bill': {
                        'reason': 'I am tired',
                        'flags': [
                            {
                                'name': 'sleep flag',
                                'affected_store_ids': 'all_pandas'
                            }
                        ]
                    },
                    'ted': {
                        'reason': 'I am very tired',
                        'flags': [
                            {
                                'name': 'very sleep flag',
                                'affected_store_ids': 'all_pandas'
                            }
                        ]
                    }
                }
            }
        }, gp_data)

    def test_create_master_decision_and_gp_data__trade_area(self):

        self.evaluator.entity_type = 'trade_area'
        self.evaluator._entity_rec = {'_id': 42}

        EvaluateNeedForGeoprocessing._initialize_gp_rules(self.evaluator)
        EvaluateNeedForGeoprocessing._evaluate_rules_and_construct_outcome(self.evaluator)

        self.evaluator._construct_initial_gp_data().AndReturn({
            'needs_gp': {
                'eat': False,
                'sleep': False
            },
            'latest_validation_date': 'now',
            'gp_rules': self.evaluator.gp_rules
        })

        self.mox.ReplayAll()

        gp_data = EvaluateNeedForGeoprocessing._create_master_decision_and_gp_data(self.evaluator)

        self.assertEqual({'eat': [], 'sleep': []}, self.evaluator.flags)

        self.assertEqual({
            'needs_gp': {
                'eat': True,
                'sleep': True
            },
            'latest_validation_date': 'now',
            'gp_rules': {
                'eat': {
                    'bill': {
                        'needs_gp': True,
                        'reason': 'I am hungry',
                        'flags': []
                    },
                    'ted': {
                        'needs_gp': True,
                        'reason': 'I am very hungry',
                        'flags': []
                    }
                },
                'sleep': {
                    'bill': {
                        'needs_gp': True,
                        'reason': 'I am tired',
                        'flags': []
                    },
                    'ted': {
                        'needs_gp': True,
                        'reason': 'I am very tired',
                        'flags': []
                    }
                }
            }
        }, gp_data)


    def test_get_entity_rec(self):

        expected_query = {'_id': ObjectId(self.evaluator.entity_id)}
        expected_entity_fields = ['data', 'meta', 'interval', 'links', 'entity_type']

        self.evaluator._main_params.mds.create_params(resource = 'find_entities_raw', query = expected_query,
                                                      entity_fields = expected_entity_fields).AndReturn({'params': 'params'})
        self.evaluator._main_access.mds.call_find_entities_raw(self.evaluator.entity_type, 'params').AndReturn(['panda rec'])

        self.mox.ReplayAll()

        EvaluateNeedForGeoprocessing._get_entity_rec(self.evaluator)
        self.assertEqual('panda rec', self.evaluator._entity_rec)


    def test_construct_update_command__no_geoprocessing_data__trade_area(self):
        self.evaluator.entity_type = 'trade_area'
        self.evaluator._entity_rec = {
            'data': {
                'there isnt': 'any geoprocessing here'
            }
        }

        gp_data = {
            'needs_gp': 'yeah',
            'latest_validation_date': 'now',
            'gp_rules': 'what rules?'
        }

        update_command = EvaluateNeedForGeoprocessing._construct_update_command(self.evaluator, gp_data)

        self.assertEqual({
            '$set': {
                'data.geoprocessing': {
                    'needs_gp': 'yeah',
                    'latest_validation_date': 'now',
                    'gp_rules': 'what rules?',
                    'latest_attempt': None
                }
            }

        }, update_command)

    def test_construct_update_command__no_geoprocessing_data__store(self):
        self.evaluator.entity_type = 'store'
        self.evaluator._entity_rec = {
            'data': {
                'there isnt': 'any geoprocessing here'
            }
        }

        gp_data = {
            'latest_validation_date': 'now',
            'gp_rules': 'what rules?'
        }

        update_command = EvaluateNeedForGeoprocessing._construct_update_command(self.evaluator, gp_data)

        self.assertEqual({
            '$set': {
                'data.geoprocessing': {
                    'latest_validation_date': 'now',
                    'gp_rules': 'what rules?',
                }
            }

        }, update_command)

    def test_construct_update_command__geoprocessing_data__store(self):

        self.evaluator.entity_type = 'store'
        self.evaluator._entity_rec = {
            'data': {
                'geoprocessing': {}
            }
        }

        gp_data = {
            'latest_validation_date': 'now',
            'gp_rules': 'what rules?'
        }

        update_command = EvaluateNeedForGeoprocessing._construct_update_command(self.evaluator, gp_data)
        self.assertEqual({
            '$set': {
                'data.geoprocessing.latest_validation_date': 'now',
                'data.geoprocessing.gp_rules': 'what rules?',
            }
        }, update_command)



    def test_construct_update_command__geoprocessing_data__trade_area(self):

        self.evaluator.entity_type = 'trade_area'
        self.evaluator._entity_rec = {
            'data': {
                'geoprocessing': {}
            }
        }

        gp_data = {
            'needs_gp': 'yeah',
            'latest_validation_date': 'now',
            'gp_rules': 'what rules?'
        }

        update_command = EvaluateNeedForGeoprocessing._construct_update_command(self.evaluator, gp_data)
        self.assertEqual({
            '$set': {
                'data.geoprocessing.needs_gp': 'yeah',
                'data.geoprocessing.latest_validation_date': 'now',
                'data.geoprocessing.gp_rules': 'what rules?',
            }
        }, update_command)


    def test_construct_initial_gp_data__not_trade_area(self):

        self.evaluator.entity_type = 'store'
        self.evaluator.gp_rules = {
            'these are some': 'gp rules'
        }

        random_time = datetime.datetime.utcnow()

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(random_time)

        self.mox.ReplayAll()

        initial_gp_data = EvaluateNeedForGeoprocessing._construct_initial_gp_data(self.evaluator)
        self.assertEqual({
            'latest_validation_date': random_time.isoformat(),
            'gp_rules': {
                'these are some': 'gp rules'
            }
        }, initial_gp_data)

    def test_construct_initial_gp_data__trade_area(self):

        self.evaluator.entity_type = 'trade_area'
        self.evaluator.gp_rules = {
            'these are some': 'gp rules'
        }

        random_time = datetime.datetime.utcnow()

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(random_time)

        self.mox.ReplayAll()

        initial_gp_data = EvaluateNeedForGeoprocessing._construct_initial_gp_data(self.evaluator)
        self.assertEqual({
            'needs_gp': {
                'eat': False,
                'sleep': False
            },
            'latest_validation_date': random_time.isoformat(),
            'gp_rules': {
                'these are some': 'gp rules'
            }
        }, initial_gp_data)

class MockTradeAreaRuleContainer(object):
    def __init__(self):
        self.rules = [MockTradeAreaRuleOne, MockTradeAreaRuleTwo]


class MockTradeAreaRuleOne(object):

    def __init__(self, entity_rec):
        self._entity_rec = entity_rec
        self.name = 'bill'

    def evaluate(self):
        return {
            'eat': {
                'needs_gp': True,
                'reason': 'I am hungry',
                'flags': []
            },
            'sleep': {
                'needs_gp': True,
                'reason': 'I am tired',
                'flags': []
            }
        }


class MockTradeAreaRuleTwo(object):

    def __init__(self, entity_rec):
        self._entity_rec = entity_rec
        self.name = 'ted'

    def evaluate(self):
        return {
            'eat': {
                'needs_gp': True,
                'reason': 'I am very hungry',
                'flags': []
            },
            'sleep': {
                'needs_gp': True,
                'reason': 'I am very tired',
                'flags': []
            }
        }


class RedPandaRuleContainer(object):
    def __init__(self):
        self.rules = [RedPandaRuleOne, RedPandaRuleTwo]


class RedPandaRuleOne(object):

    def __init__(self, entity_rec):
        self._entity_rec = entity_rec
        self.name = 'bill'

    def evaluate(self):
        return {
            'eat': {
                'reason': 'I am hungry',
                'flags': [{
                    'name': 'food flag',
                    'affected_store_ids': 'all_pandas'
                }]
            },
            'sleep': {
                'reason': 'I am tired',
                'flags': [{
                    'name': 'sleep flag',
                    'affected_store_ids': 'all_pandas'
                }]
            }
        }


class RedPandaRuleTwo(object):

    def __init__(self, entity_rec):
        self._entity_rec = entity_rec
        self.name = 'ted'

    def evaluate(self):
        return {
            'eat': {
                'reason': 'I am very hungry',
                'flags': [{
                    'name': 'very food flag',
                    'affected_store_ids': 'all_pandas'
                }]
            },
            'sleep': {
                'reason': 'I am very tired',
                'flags': [{
                    'name': 'very sleep flag',
                    'affected_store_ids': 'all_pandas'
                }]
            }
        }





