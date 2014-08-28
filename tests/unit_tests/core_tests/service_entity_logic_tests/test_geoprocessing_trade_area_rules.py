from collections import OrderedDict
import json
import datetime
import mox
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.trade_area_rules.trade_area_rules import FailedLatestGeoprocessingEvent, PickUpParentCompanyStatusSwitchedToPublishedFlag, PickUpNewPotentialAddressFlag, PickUpParentStoreClosedFlag, PickUpNewPotentialTradeAreaCompetitionFlag, PickUpGeoprocessingFlags, PickUpParentCompanysIndustryClassificationChangedFlag, PickUpParentIndustryCompetitionChangedFlag, FlaggedForGeoprocessingButHasNotBeenGeoprocessed
from core.common.business_logic.service_entity_logic.geoprocessing_rules.geoprocessing_reference import GeoprocessingMethodsReference as GMR
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.geoprocessing_flags import GeoprocessingFlags as GF

__author__ = 'kingneptune'

class GeoprocessingCommonRulesTests(mox.MoxTestBase):

    def setUp(self):
        super(GeoprocessingCommonRulesTests, self).setUp()
        register_common_mock_dependencies(self.mox)

    def doCleanups(self):
        super(GeoprocessingCommonRulesTests, self).doCleanups()
        dependencies.clear()
    
    def test_FailedLatestGeoprocessingEvent_init(self):
        
        failed_latest_geoprocessing = FailedLatestGeoprocessingEvent({'entity': 'rec'})
        self.assertEqual(failed_latest_geoprocessing._entity_rec, {'entity': 'rec'})
        self.assertEqual(failed_latest_geoprocessing.name, 'failed_latest_geoprocessing_event')

    def test_FailedLatestGeoprocessingEvent_evaluate__both_pass(self):

        failed_latest_geoprocessing = self.mox.CreateMock(FailedLatestGeoprocessingEvent)
        unordered_methods_decisions = {
            'demo': None,
            'comp': None
        }

        failed_latest_geoprocessing._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        failed_latest_geoprocessing._entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_attempt': {
                        'demo': {'result': 'success'},
                        'comp': {'result': 'success'}
                    }
                }
            }
        }

        comp_reason = "The latest '%s' geoprocessing event was successful" % 'comp'
        failed_latest_geoprocessing._construct_decision_dict(comp_reason, needs_gp = False).AndReturn('comp doesnt need geoprocessing')

        demo_reason = "The latest '%s' geoprocessing event was successful" % 'demo'
        failed_latest_geoprocessing._construct_decision_dict(demo_reason, needs_gp = False).AndReturn('demo doesnt need geoprocessing')

        self.mox.ReplayAll()

        expected_methods_decisions = {
            'comp': 'comp doesnt need geoprocessing',
            'demo': 'demo doesnt need geoprocessing'
        }

        methods_decisions = FailedLatestGeoprocessingEvent.evaluate(failed_latest_geoprocessing)
        self.assertEqual(expected_methods_decisions, methods_decisions)


    def test_FailedLatestGeoprocessingEvent_evaluate__one_pass_one_fail(self):

        failed_latest_geoprocessing = self.mox.CreateMock(FailedLatestGeoprocessingEvent)
        unordered_methods_decisions = {
            'demo': None,
            'comp': None
        }

        failed_latest_geoprocessing._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        failed_latest_geoprocessing._entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_attempt': {
                        'demo': {'result': 'success'},
                        'comp': {'result': 'failed'}
                    }
                }
            }
        }

        comp_reason = "The latest '%s' geoprocessing event failed" % 'comp'
        failed_latest_geoprocessing._construct_decision_dict(comp_reason, needs_gp = True).AndReturn('comp failed and needs geoprocessing')

        demo_reason = "The latest '%s' geoprocessing event was successful" % 'demo'
        failed_latest_geoprocessing._construct_decision_dict(demo_reason, needs_gp = False).AndReturn('demo doesnt need geoprocessing')

        self.mox.ReplayAll()

        expected_methods_decisions = {
            'comp': 'comp failed and needs geoprocessing',
            'demo': 'demo doesnt need geoprocessing'
        }

        methods_decisions = FailedLatestGeoprocessingEvent.evaluate(failed_latest_geoprocessing)
        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_FailedLatestGeoprocessingEvent_evaluate__both_fail(self):

        failed_latest_geoprocessing = self.mox.CreateMock(FailedLatestGeoprocessingEvent)
        unordered_methods_decisions = {
            'demo': None,
            'comp': None
        }

        failed_latest_geoprocessing._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        failed_latest_geoprocessing._entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_attempt': {
                        'demo': {'result': 'failed'},
                        'comp': {'result': 'failed'}
                    }
                }
            }
        }

        comp_reason = "The latest '%s' geoprocessing event failed" % 'comp'
        failed_latest_geoprocessing._construct_decision_dict(comp_reason,
                                                             needs_gp = True).AndReturn('comp failed and needs geoprocessing')

        demo_reason = "The latest '%s' geoprocessing event failed" % 'demo'
        failed_latest_geoprocessing._construct_decision_dict(demo_reason,
                                                             needs_gp = True).AndReturn('demo failed and needs geoprocessing')

        self.mox.ReplayAll()

        expected_methods_decisions = {
            'comp': 'comp failed and needs geoprocessing',
            'demo': 'demo failed and needs geoprocessing'
        }

        methods_decisions = FailedLatestGeoprocessingEvent.evaluate(failed_latest_geoprocessing)
        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_FailedLatestGeoprocessingEvent_evaluate__missing_one_latest_attempt(self):

        failed_latest_geoprocessing = self.mox.CreateMock(FailedLatestGeoprocessingEvent)
        unordered_methods_decisions = {
            'demo': None,
            'comp': None
        }

        failed_latest_geoprocessing._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        failed_latest_geoprocessing._entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_attempt': {
                        'demo': {'result': 'failed'}
                    }
                }
            }
        }

        comp_reason = "This trade area has never been geoprocessed for method '%s'" % 'comp'
        failed_latest_geoprocessing._construct_decision_dict(comp_reason, needs_gp = True).AndReturn('comp was never geoprocessed')

        demo_reason = "The latest '%s' geoprocessing event failed" % 'demo'
        failed_latest_geoprocessing._construct_decision_dict(demo_reason, needs_gp = True).AndReturn('demo failed and needs geoprocessing')

        self.mox.ReplayAll()

        expected_methods_decisions = {
            'comp': 'comp was never geoprocessed',
            'demo': 'demo failed and needs geoprocessing'
        }

        methods_decisions = FailedLatestGeoprocessingEvent.evaluate(failed_latest_geoprocessing)
        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_FailedLatestGeoprocessingEvent_evaluate__missing_both_latest_attempts(self):

        failed_latest_geoprocessing = self.mox.CreateMock(FailedLatestGeoprocessingEvent)
        unordered_methods_decisions = {
            'demo': None,
            'comp': None
        }

        failed_latest_geoprocessing._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        failed_latest_geoprocessing._entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_attempt': {
                    }
                }
            }
        }

        comp_reason = "This trade area has never been geoprocessed for method '%s'" % 'comp'
        failed_latest_geoprocessing._construct_decision_dict(comp_reason, needs_gp = True).AndReturn('comp was never geoprocessed')

        demo_reason = "This trade area has never been geoprocessed for method '%s'" % 'demo'
        failed_latest_geoprocessing._construct_decision_dict(demo_reason, needs_gp = True).AndReturn('demo was never geoprocessed')

        self.mox.ReplayAll()

        expected_methods_decisions = {
            'comp': 'comp was never geoprocessed',
            'demo': 'demo was never geoprocessed'
        }

        methods_decisions = FailedLatestGeoprocessingEvent.evaluate(failed_latest_geoprocessing)
        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_FailedLatestGeoprocessingEvent_evaluate__missing_latest_attempt(self):

        failed_latest_geoprocessing = self.mox.CreateMock(FailedLatestGeoprocessingEvent)
        unordered_methods_decisions = {
            'demo': None,
            'comp': None
        }

        failed_latest_geoprocessing._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        failed_latest_geoprocessing._entity_rec = {
            'data': {
                'geoprocessing': {}
            }
        }

        comp_reason = "This trade area has never been geoprocessed for method '%s'" % 'comp'
        failed_latest_geoprocessing._construct_decision_dict(comp_reason, needs_gp = True).AndReturn('comp was never geoprocessed')

        demo_reason = "This trade area has never been geoprocessed for method '%s'" % 'demo'
        failed_latest_geoprocessing._construct_decision_dict(demo_reason, needs_gp = True).AndReturn('demo was never geoprocessed')

        self.mox.ReplayAll()

        expected_methods_decisions = {
            'comp': 'comp was never geoprocessed',
            'demo': 'demo was never geoprocessed'
        }

        methods_decisions = FailedLatestGeoprocessingEvent.evaluate(failed_latest_geoprocessing)
        self.assertEqual(expected_methods_decisions, methods_decisions)


    def test_FailedLatestGeoprocessingEvent_evaluate__missing_geoprocessing(self):

        failed_latest_geoprocessing = self.mox.CreateMock(FailedLatestGeoprocessingEvent)
        unordered_methods_decisions = {
            'demo': None,
            'comp': None
        }

        failed_latest_geoprocessing._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        failed_latest_geoprocessing._entity_rec = {
            'data': {
            }
        }

        comp_reason = "This trade area has never been geoprocessed for method '%s'" % 'comp'
        failed_latest_geoprocessing._construct_decision_dict(comp_reason, needs_gp = True).AndReturn('comp was never geoprocessed')

        demo_reason = "This trade area has never been geoprocessed for method '%s'" % 'demo'
        failed_latest_geoprocessing._construct_decision_dict(demo_reason, needs_gp = True).AndReturn('demo was never geoprocessed')

        self.mox.ReplayAll()

        expected_methods_decisions = {
            'comp': 'comp was never geoprocessed',
            'demo': 'demo was never geoprocessed'
        }

        methods_decisions = FailedLatestGeoprocessingEvent.evaluate(failed_latest_geoprocessing)
        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_FlaggedForGeoprocessingButHasNotBeenGeoprocessed__missing_geoprocessing_and_latest_rules(self):

        entity_rec = {
            'data': {
                'random': 'data'
            },
            'entity_type': 'trade_area'
        }

        rule = FlaggedForGeoprocessingButHasNotBeenGeoprocessed(entity_rec)


        methods_decisions = rule.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': "This trade area has not been flagged for geoprocessing for this method.",
                'needs_gp': False,
                'flags': []
            },
            GMR.FindWhiteSpaceCompetition: {
                'reason': "This trade area has not been flagged for geoprocessing for this method.",
                'needs_gp': False,
                'flags': []
            },
            GMR.GetDemographics: {
                'reason': "This trade area has not been flagged for geoprocessing for this method.",
                'needs_gp': False,
                'flags': []
            }
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_FlaggedForGeoprocessingButHasNotBeenGeoprocessed__missing_geoprocessing_not_latest_rules(self):

        entity_rec = {
            'data': {
                'random': 'data',
                'geoprocessing': {
                    'latest_validation_date': datetime.datetime(2013, 05, 18).isoformat(),
                    'needs_gp': {
                        GMR.GetDemographics: True,
                        GMR.FindCompetition: True
                    }
                }
            },
            'entity_type': 'trade_area'
        }

        rule = FlaggedForGeoprocessingButHasNotBeenGeoprocessed(entity_rec)


        methods_decisions = rule.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': 'This trade area has been marked for geoprocessing and has not yet been geoprocessed for this method since that marking.',
                'needs_gp': True,
                'flags': []
            },
            GMR.FindWhiteSpaceCompetition: {
                'reason': "This trade area has not been flagged for geoprocessing for this method.",
                'needs_gp': False,
                'flags': []
            },
            GMR.GetDemographics: {
                'reason': 'This trade area has been marked for geoprocessing and has not yet been geoprocessed for this method since that marking.',
                'needs_gp': True,
                'flags': []
            }
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_FlaggedForGeoprocessingButHasNotBeenGeoprocessed__missing_latest_rules_not_geoprocessing(self):

        entity_rec = {
            'data': {
                'random': 'data',
                'geoprocessing': {
                    'latest_validation_date': datetime.datetime(2013, 05, 18).isoformat(),
                    'needs_gp': {}
                }
            },
            'entity_type': 'trade_area'
        }

        rule = FlaggedForGeoprocessingButHasNotBeenGeoprocessed(entity_rec)


        methods_decisions = rule.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': "This trade area has not been flagged for geoprocessing for this method.",
                'needs_gp': False,
                'flags': []
            },
            GMR.FindWhiteSpaceCompetition: {
                'reason': "This trade area has not been flagged for geoprocessing for this method.",
                'needs_gp': False,
                'flags': []
            },
            GMR.GetDemographics: {
                'reason': "This trade area has not been flagged for geoprocessing for this method.",
                'needs_gp': False,
                'flags': []
            }
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_FlaggedForGeoprocessingButHasNotBeenGeoprocessed__has_both(self):

        entity_rec = {
            'data': {
                'random': 'data',
                'geoprocessing': {
                    'latest_validation_date': datetime.datetime(2013, 05, 18).isoformat(),
                    'needs_gp': {
                        GMR.GetDemographics: True,
                        GMR.FindCompetition: True,
                        GMR.FindWhiteSpaceCompetition: True
                    },
                    'latest_attempt': {
                        GMR.GetDemographics: {'end_timestamp': datetime.datetime(2013, 05, 19).isoformat()},
                        GMR.FindCompetition: {'end_timestamp': datetime.datetime(2013, 05, 19).isoformat()},
                        GMR.FindWhiteSpaceCompetition: {'end_timestamp': datetime.datetime(2013, 05, 17).isoformat()}
                    }
                }
            },
            'entity_type': 'trade_area'
        }

        rule = FlaggedForGeoprocessingButHasNotBeenGeoprocessed(entity_rec)


        methods_decisions = rule.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': 'This trade area has been marked for geoprocessing and has not yet been geoprocessed for this method since that marking.',
                'needs_gp': True,
                'flags': []
            },
            GMR.GetDemographics: {
                'reason': 'This trade area has been marked for geoprocessing and has not yet been geoprocessed for this method since that marking.',
                'needs_gp': True,
                'flags': []
            },
            GMR.FindWhiteSpaceCompetition: {
                'reason': 'This trade area has been marked for geoprocessing and has been geoprocessed for this method since that marking.',
                'needs_gp': False,
                'flags': []
            }
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

########################################################################################################################

                                        # BASE PICK UP FLAG CLASS TESTS #

########################################################################################################################

    def test_find_flag_create_decision__no_previous_flags(self):
        entity_rec = {
            'data': {
                'flags': {
                    GMR.FindCompetition: ['foo']
                }
            },
            'entity_type': 'trade_area'
        }
        
        def foo(x):
            return {
                'affected_trade_area_ids': [x],
                'name': 'nearby_foo'
            }
        
        pickup = PickUpGeoprocessingFlags()
        pickup._entity_rec = entity_rec
        pickup._flag = 'foo'
        pickup.name = pickup._construct_pick_up_rule_name()

        self.assertEqual('pick_up_foo_flag', pickup.name)

        decision_dict = pickup._find_flag_create_decision(GMR.FindCompetition, [(foo, (1,))])
        expected_decision_dict = {
            'needs_gp': True,
            'reason': "Found flag 'foo'",
            'flags': [
                {
                    'affected_trade_area_ids': [1],
                    'name': 'nearby_foo'
                }
            ]
        }

        self.assertEqual(expected_decision_dict, decision_dict)

    def test_find_flag_create_decision__identical_flag(self):
        entity_rec = {
            'data': {
                'flags': {
                    GMR.FindCompetition: ['foo']
                },
                'geoprocessing': {
                    'gp_rules': {
                        GMR.FindCompetition: {
                            'pick_up_foo_flag': {
                                'needs_gp': True,
                                'reason': "Found flag 'foo'",
                                'flags': [
                                    {
                                        'affected_trade_area_ids': [1],
                                        'name': 'nearby_foo'
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            'entity_type': 'trade_area'
        }

        def foo(x):
            return {
                'affected_trade_area_ids': [x],
                'name': 'nearby_foo'
            }

        pickup = PickUpGeoprocessingFlags()
        pickup._entity_rec = entity_rec
        pickup.name = 'pick_up_foo_flag'
        pickup._flag = 'foo'

        decision_dict = pickup._find_flag_create_decision(GMR.FindCompetition, [(foo, (1,))])
        expected_decision_dict = {
            'needs_gp': True,
            'reason': "Found flag 'foo'",
            'flags': []
        }

        self.assertEqual(expected_decision_dict, decision_dict)

    def test_find_flag_create_decision__non_identical_flag(self):
        entity_rec = {
            'data': {
                'flags': {
                    GMR.FindCompetition: ['foo']
                },
                'geoprocessing': {
                    'gp_rules': {
                        'pick_up_foo_flag': {
                            'needs_gp': True,
                            'reason': "Found flag 'foo'",
                            'flags': [
                                {
                                    'affected_trade_area_ids': [3],
                                    'name': 'nearby_foo'
                                }
                            ]
                        }
                    }
                }
            },
            'entity_type': 'trade_area'
        }

        def foo(x):
            return {
                'affected_trade_area_ids': [x],
                'name': 'nearby_foo'
            }

        pickup = PickUpGeoprocessingFlags()
        pickup._entity_rec = entity_rec
        pickup.name = 'pick_up_foo_flag'
        pickup._flag = 'foo'

        decision_dict = pickup._find_flag_create_decision(GMR.FindCompetition, [(foo, (1,))])

        expected_decision_dict = {
            'needs_gp': True,
            'reason': "Found flag 'foo'",
            'flags': [
                {
                    'affected_trade_area_ids': [1],
                    'name': 'nearby_foo'
                }
            ]
        }

        self.assertEqual(expected_decision_dict, decision_dict)


    def test_PickUpParentIndustryCompetitionChangedFlag__has_flag(self):

        entity_rec = {
            'data': {'flags': {
                GMR.FindCompetition: [GF.ParentIndustryCompetitionChanged]
            }},
            'entity_type': 'trade_area'
        }



        pickup_flags = PickUpParentIndustryCompetitionChangedFlag(entity_rec)

        def foo(x, y, z):
            return {
                'name': 'foo_flag',
                'affected_trade_area_ids': [x, y, z]
            }

        self.mox.StubOutWithMock(pickup_flags, '_get_flag_functions_arguments')
        pickup_flags._get_flag_functions_arguments().AndReturn([
            (foo, (1, 2, 3))
        ])

        self.mox.ReplayAll()


        methods_decisions = pickup_flags.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': "Found flag '%s'" % GF.ParentIndustryCompetitionChanged,
                'needs_gp': True,
                'flags': [
                    {
                        'name': 'foo_flag',
                        'affected_trade_area_ids': [1, 2, 3]
                    }
                ]
            },
            GMR.FindWhiteSpaceCompetition: None,
            GMR.GetDemographics: None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)


########################################################################################################################

                                        # PICK UP COMPANY FLAG TESTS #

########################################################################################################################

    def test_PickUpParentCompanyStatusSwitchedToPublishedFlag__has_flag(self):

        entity_rec = {
            'data': {'flags': {
                GMR.FindCompetition: [GF.ParentCompanyStatusSwitchedToPublished],
                GMR.GetDemographics: [GF.ParentCompanyStatusSwitchedToPublished],
                GMR.FindWhiteSpaceCompetition: [GF.ParentCompanyStatusSwitchedToPublished],
            }},
            'entity_type': 'trade_area'
        }

        pickup_flags = PickUpParentCompanyStatusSwitchedToPublishedFlag(entity_rec)

        methods_decisions = pickup_flags.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': "Found flag '%s'" % GF.ParentCompanyStatusSwitchedToPublished,
                'needs_gp': True,
                'flags': []
            },
            GMR.GetDemographics: {
                'reason': "Found flag '%s'" % GF.ParentCompanyStatusSwitchedToPublished,
                'needs_gp': True,
                'flags': []
            },
            GMR.FindWhiteSpaceCompetition: {
                'reason': "Found flag '%s'" % GF.ParentCompanyStatusSwitchedToPublished,
                'needs_gp': True,
                'flags': []
            }
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_PickUpParentCompanysIndustryClassificationChangedFlag__has_flag(self):

        entity_rec = {
            'data': {'flags': {
                GMR.FindCompetition: [GF.ParentCompanysIndustryClassificationChanged]
            }},
            'entity_type': 'trade_area'
        }



        pickup_flags = PickUpParentCompanysIndustryClassificationChangedFlag(entity_rec)

        def foo(x, y, z):
            return {
                'name': 'foo_flag',
                'affected_trade_area_ids': [x, y, z]
            }

        self.mox.StubOutWithMock(pickup_flags, '_get_flag_functions_arguments')
        pickup_flags._get_flag_functions_arguments().AndReturn([
            (foo, (1, 2, 3))
        ])

        self.mox.ReplayAll()


        methods_decisions = pickup_flags.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': "Found flag '%s'" % GF.ParentCompanysIndustryClassificationChanged,
                'needs_gp': True,
                'flags': [
                    {
                        'name': 'foo_flag',
                        'affected_trade_area_ids': [1, 2, 3]
                    }
                ]
            },
            GMR.FindWhiteSpaceCompetition: None,
            GMR.GetDemographics: None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

########################################################################################################################

                                        # PICK UP STORE FLAG TESTS #

########################################################################################################################

    def test_PickUpNewPotentialAddressFlag__has_flag(self):

        entity_rec = {
            'data': {
                'flags': {
                    GMR.FindCompetition: [GF.NewPotentialAddress],
                    GMR.GetDemographics: [GF.NewPotentialAddress],
                    GMR.FindWhiteSpaceCompetition: [GF.NewPotentialAddress]
                }
            },
            'entity_type': 'trade_area'
        }

        pickup_flags = PickUpNewPotentialAddressFlag(entity_rec)

        def foo(x, y, z):
            return {
                'name': 'foo_flag',
                'affected_trade_area_ids': [x, y, z]
            }

        self.mox.StubOutWithMock(pickup_flags, '_get_flag_functions_arguments')
        pickup_flags._get_flag_functions_arguments().AndReturn([
            (foo, (1, 2, 3))
        ])

        self.mox.ReplayAll()

        methods_decisions = pickup_flags.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': "Found flag '%s'" % GF.NewPotentialAddress,
                'needs_gp': True,
                'flags': [
                    {
                        'name': 'foo_flag',
                        'affected_trade_area_ids': [1, 2, 3]
                    }
                ]
            },
            GMR.GetDemographics: {
                'reason': "Found flag '%s'" % GF.NewPotentialAddress,
                'needs_gp': True,
                'flags': []
            },
            GMR.FindWhiteSpaceCompetition: {
                'reason': "Found flag '%s'" % GF.NewPotentialAddress,
                'needs_gp': True,
                'flags': []
            }
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)


    def test_PickUpParentStoreClosedFlag__has_flag(self):

        entity_rec = {
            'data': {
                'flags': {
                    GMR.FindCompetition: [GF.ParentStoreClosed],
                    GMR.FindWhiteSpaceCompetition: [GF.ParentStoreClosed]
                }
            },
            'entity_type': 'trade_area'
        }

        pickup_flags = PickUpParentStoreClosedFlag(entity_rec)

        def foo(x, y, z):
            return {
                'name': 'foo_flag',
                'affected_trade_area_ids': [x, y, z]
            }

        self.mox.StubOutWithMock(pickup_flags, '_get_flag_functions_arguments')
        pickup_flags._get_flag_functions_arguments().AndReturn([
            (foo, (1, 2, 3))
        ])

        self.mox.ReplayAll()

        methods_decisions = pickup_flags.evaluate()

        expected_methods_decisions = {
            GMR.FindCompetition: {
                'reason': "Found flag '%s'" % GF.ParentStoreClosed,
                'needs_gp': True,
                'flags': [
                    {
                        'name': 'foo_flag',
                        'affected_trade_area_ids': [1, 2, 3]
                    }
                ]
            },
            GMR.FindWhiteSpaceCompetition: {
                'reason': "Found flag '%s'" % GF.ParentStoreClosed,
                'needs_gp': True,
                'flags': []
            },
            GMR.GetDemographics: None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

########################################################################################################################

                                        # PICK UP TRADE AREA FLAG TESTS #

########################################################################################################################

    def test_PickUpNewPotentialTradeAreaCompetitionFlag__has_flag(self):

        entity_rec = {
            'data': {'flags': {GMR.FindCompetition: [GF.NewPotentialTradeAreaCompetition]}},
            'entity_type': 'trade_area'
        }

        pickup_flags = PickUpNewPotentialTradeAreaCompetitionFlag(entity_rec)

        methods_decisions = pickup_flags.evaluate()

        expected_methods_decisions = {

            GMR.FindCompetition: {
                'reason': "Found flag '%s'" % GF.NewPotentialTradeAreaCompetition,
                'needs_gp': True,
                'flags': []
            },
            GMR.FindWhiteSpaceCompetition: None,
            GMR.GetDemographics: None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)