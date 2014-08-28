from collections import OrderedDict
import mox
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities import date_utilities
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.store_rules.store_rules import StoreClosed, NewMostCorrectRIR
from core.common.business_logic.service_entity_logic.geoprocessing_rules.geoprocessing_reference import GeoprocessingMethodsReference

__author__ = 'kingneptune'

class GeoprocessingStoreRulesTests(mox.MoxTestBase):

    def setUp(self):
        super(GeoprocessingStoreRulesTests, self).setUp()
        register_common_mock_dependencies(self.mox)

    def doCleanups(self):
        super(GeoprocessingStoreRulesTests, self).doCleanups()
        dependencies.clear()


    # -------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------- Store Closed Tests --------------------------------------------- #
    # -------------------------------------------------------------------------------------------------------------- #

    def test_StoreClosed_initialization(self):

        store_closed = StoreClosed({'entity': 'rec'})
        self.assertEqual(store_closed._entity_rec, {'entity': 'rec'})
        self.assertEqual('store_closed', store_closed.name)

    
    def test_StoreClosed_evaluate__store_closed(self):
        
        store_closed = self.mox.CreateMock(StoreClosed)

        store_closed._entity_rec = {
            'interval': [None, 'now']
        }

        store_closed.name = 'store_closed'
        store_closed._methods_decisions = {}
        store_closed._get_latest_interval_change_date().AndReturn(100)
        store_closed._find_latest_validation_date().AndReturn(99)
        store_closed._get_flags_to_emit().AndReturn(['flag'])
        store_closed._construct_decision_dict('This store has closed.',
                                              ['flag']).AndReturn({'decision': 'dictionary'})
        store_closed._construct_decision_dict('This store has closed.',
                                              ['flag']).AndReturn({'white space decision': 'dictionary'})

        self.mox.ReplayAll()

        methods_decisions = StoreClosed.evaluate(store_closed)
        expected_methods_decisions = {
            GeoprocessingMethodsReference.FindCompetition: {
                'decision': 'dictionary'
            },
            GeoprocessingMethodsReference.FindWhiteSpaceCompetition: {
                'white space decision': 'dictionary'
            }
        }
        self.assertEqual(expected_methods_decisions, methods_decisions)


    def test_StoreClosed_evaluate__store_still_opened(self):

        store_closed = self.mox.CreateMock(StoreClosed)

        store_closed._entity_rec = {
            'interval': [None, None]
        }

        store_closed._methods_decisions = {}
        store_closed._get_latest_interval_change_date().AndReturn(100)
        store_closed._find_latest_validation_date().AndReturn({GeoprocessingMethodsReference.FindCompetition: 99})

        self.mox.ReplayAll()

        methods_decisions = StoreClosed.evaluate(store_closed)
        self.assertEqual({}, methods_decisions)


    def test_StoreClosed_get_flags_to_emit(self):

        store_closed = self.mox.CreateMock(StoreClosed)
        store_closed._entity_rec = {
            '_id': '42',
            'data': {
                'company_id': '43'
            }
        }

        store_closed._flags_constructor = self.mox.CreateMockAnything()
        store_closed._flags_constructor.store_closed_flag().AndReturn('flag')

        self.mox.ReplayAll()

        flags = StoreClosed._get_flags_to_emit(store_closed)
        self.assertEqual(['flag'], flags)


    # -------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------- New Most Correct RIR Tests ------------------------------------------- #
    # -------------------------------------------------------------------------------------------------------------- #

    def test_NewMostCorrectRIR_initialization(self):
        
        new_most_correct_rir = NewMostCorrectRIR({'entity': 'rec'})
        self.assertEqual(new_most_correct_rir._entity_rec, {'entity': 'rec'})
        self.assertEqual(new_most_correct_rir.name, 'new_most_correct_rir')

    def test_NewMostCorrectRIR_evaluate__new_most_correct_rir(self):

        new_most_correct_rir = self.mox.CreateMock(NewMostCorrectRIR)
        new_most_correct_rir._extract_most_correct_rir_link_id().AndReturn(42)

        self.mox.StubOutWithMock(date_utilities, 'get_utc_date_from_bson_object_id')
        date_utilities.get_utc_date_from_bson_object_id(42).AndReturn(1)

        new_most_correct_rir._find_latest_validation_date().AndReturn(0)

        unordered_methods_decisions = {
            GeoprocessingMethodsReference.FindCompetition: None,
            GeoprocessingMethodsReference.GetDemographics: None
        }

        new_most_correct_rir._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        new_most_correct_rir._get_flags_to_emit().AndReturn(['competition flag'])
        new_most_correct_rir._construct_decision_dict("There is a newly linked 'most correct' retail input record",
                                                      ['competition flag']).AndReturn('competition decision')

        new_most_correct_rir._get_flags_to_emit().AndReturn(['demographics flag'])
        new_most_correct_rir._construct_decision_dict("There is a newly linked 'most correct' retail input record",
                                                      ['demographics flag']).AndReturn('demographics decision')

        self.mox.ReplayAll()

        methods_decisions = NewMostCorrectRIR.evaluate(new_most_correct_rir)
        expected_methods_decisions = {
            GeoprocessingMethodsReference.FindCompetition: 'competition decision',
            GeoprocessingMethodsReference.GetDemographics: 'demographics decision'
        }
        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_NewMostCorrectRIR_initialization(self):

        new_most_correct_rir = NewMostCorrectRIR({'entity': 'rec'})
        self.assertEqual(new_most_correct_rir._entity_rec, {'entity': 'rec'})
        self.assertEqual(new_most_correct_rir.name, 'new_most_correct_rir')

    def test_NewMostCorrectRIR_evaluate__no_new_most_correct_rir(self):

        new_most_correct_rir = self.mox.CreateMock(NewMostCorrectRIR)
        new_most_correct_rir._extract_most_correct_rir_link_id().AndReturn(42)

        self.mox.StubOutWithMock(date_utilities, 'get_utc_date_from_bson_object_id')
        date_utilities.get_utc_date_from_bson_object_id(42).AndReturn(0)

        new_most_correct_rir._find_latest_validation_date().AndReturn(1)

        unordered_methods_decisions = {
            GeoprocessingMethodsReference.FindCompetition: None,
            GeoprocessingMethodsReference.GetDemographics: None
        }

        new_most_correct_rir._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        new_most_correct_rir._construct_decision_dict("This store's trade areas were already flagged for geoprocessing "
                                                      "under the current most-correct retail input record link",
                                                      []).AndReturn('competition decision')

        new_most_correct_rir._construct_decision_dict("This store's trade areas were already flagged for geoprocessing "
                                                      "under the current most-correct retail input record link",
                                                      []).AndReturn('demographics decision')

        self.mox.ReplayAll()

        methods_decisions = NewMostCorrectRIR.evaluate(new_most_correct_rir)
        expected_methods_decisions = {
            GeoprocessingMethodsReference.FindCompetition: 'competition decision',
            GeoprocessingMethodsReference.GetDemographics: 'demographics decision'
        }
        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_NewMostCorrectRIR_evaluate__no_most_correct_rir(self):

        new_most_correct_rir = self.mox.CreateMock(NewMostCorrectRIR)
        new_most_correct_rir._extract_most_correct_rir_link_id().AndReturn(None)

        new_most_correct_rir._methods_decisions = {
            GeoprocessingMethodsReference.GetDemographics: None,
            GeoprocessingMethodsReference.FindCompetition: None
        }

        expected_reason = 'This store does not have a most correct retail input record link as of this date'
        new_most_correct_rir._construct_decision_dict(expected_reason).MultipleTimes().AndReturn('same decision')

        self.mox.ReplayAll()

        methods_decisions = NewMostCorrectRIR.evaluate(new_most_correct_rir)

        expected_methods_decisions = {
            GeoprocessingMethodsReference.FindCompetition: 'same decision',
            GeoprocessingMethodsReference.GetDemographics: 'same decision'
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)


    def test_NewMostCorrectRIR_evaluate__get_flags_to_emit__competition(self):

        new_most_correct_rir = self.mox.CreateMock(NewMostCorrectRIR)
        new_most_correct_rir._entity_rec = {
            '_id': '42',
            'data': {
                'company_id': '43'
            }
        }
        new_most_correct_rir._flags_constructor = self.mox.CreateMockAnything()
        new_most_correct_rir._flags_constructor.new_potential_address_flag().AndReturn('flag')

        self.mox.ReplayAll()

        flags = NewMostCorrectRIR._get_flags_to_emit(new_most_correct_rir)
        self.assertEqual(['flag'], flags)

    def test_NewMostCorrectRIR_evaluate__get_flags_to_emit__demographics(self):

        new_most_correct_rir = self.mox.CreateMock(NewMostCorrectRIR)
        new_most_correct_rir._entity_rec = {
            '_id': '42',
            'data': {
                'company_id': '43'
            }
        }

        new_most_correct_rir._flags_constructor = self.mox.CreateMockAnything()
        new_most_correct_rir._flags_constructor.new_potential_address_flag().AndReturn('flag')

        self.mox.ReplayAll()

        flags = NewMostCorrectRIR._get_flags_to_emit(new_most_correct_rir)
        self.assertEqual(['flag'], flags)