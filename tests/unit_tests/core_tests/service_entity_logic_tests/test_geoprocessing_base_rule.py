import datetime
import mox
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.base_rule import GeoprocessingBaseRule
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.geoprocessing_flags import GeoprocessingFlags
from core.common.business_logic.service_entity_logic.geoprocessing_rules.geoprocessing_reference import GeoprocessingMethodsReference as GMR

__author__ = 'kingneptune'


class GeoprocessingBaseRuleTests(mox.MoxTestBase):

    def setUp(self):

        super(GeoprocessingBaseRuleTests, self).setUp()
        register_common_mock_dependencies(self.mox)

        self.base_rule = self.mox.CreateMock(GeoprocessingBaseRule)

        self.base_rule._geoprocessing_methods = [GMR.GetDemographics, GMR.FindCompetition]

        self.base_rule._main_access = self.mox.CreateMockAnything()
        self.base_rule._main_access.mds = self.mox.CreateMockAnything()

        self.base_rule._main_params = self.mox.CreateMockAnything()
        self.base_rule._main_params.mds = self.mox.CreateMockAnything()
        self.base_rule._default_old_date = datetime.datetime(1990, 05, 18)


    def doCleanups(self):
        super(GeoprocessingBaseRuleTests, self).doCleanups()
        dependencies.clear()

    def test_init(self):

        flag_constructor_type = type(GeoprocessingFlags())

        expected_methods_decisions = {
            GMR.FindCompetition: None,
            GMR.GetDemographics: None,
            GMR.FindWhiteSpaceCompetition: None
        }

        base_rule = GeoprocessingBaseRule()

        self.assertEqual(type(base_rule._flags_constructor), flag_constructor_type)
        self.assertEqual(base_rule._methods_decisions, expected_methods_decisions)


    def test_find_latest_gp_run_dates__latest_validation_date(self):

        latest_find_competition_timestamp = datetime.datetime(1991, 5, 6, 7, 8, 9, microsecond = 10).isoformat()
        self.base_rule._entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_validation_date': latest_find_competition_timestamp
                }
            }
        }

        latest_validation_date = GeoprocessingBaseRule._find_latest_validation_date(self.base_rule)

        self.assertEqual(latest_validation_date, datetime.datetime(1991, 5, 6, 7, 8, 9, microsecond = 10))

    def test_find_latest_gp_run_dates__empty_latest_validation_date_key(self):

        self.base_rule._entity_rec = {
            'data': {
                'geoprocessing': {
                    'latest_validation_date': None
                }
            }
        }

        latest_validation_date = GeoprocessingBaseRule._find_latest_validation_date(self.base_rule)

        self.assertEqual(latest_validation_date, datetime.datetime(1990, 05, 18))

    def test_find_latest_gp_run_dates__no_latest_validation_date_key(self):

        self.base_rule._entity_rec = {
            'data': {
                'geoprocessing': {
                }
            }
        }

        latest_validation_date = GeoprocessingBaseRule._find_latest_validation_date(self.base_rule)
        self.assertEqual(latest_validation_date, datetime.datetime(1990, 05, 18))


    def test_find_latest_gp_run_dates__no_geoprocessing_key(self):

        self.base_rule._entity_rec = {
            'data': {
            }
        }

        latest_validation_date = GeoprocessingBaseRule._find_latest_validation_date(self.base_rule)
        self.assertEqual(latest_validation_date, datetime.datetime(1990, 05, 18))


    def test_construct_decision_dict__trade_area(self):

        base_rule = GeoprocessingBaseRule()
        base_rule._entity_rec = {'entity_type': 'trade_area'}
        decision_dict = base_rule._construct_decision_dict('reason', [], needs_gp = True)
        self.assertEqual({
            'needs_gp': True,
            'reason': 'reason',
            'flags': []
        }, decision_dict)

    def test_construct_decision_dict__trade_area__no_needs_gp(self):

        base_rule = GeoprocessingBaseRule()
        base_rule._entity_rec = {'entity_type': 'trade_area'}

        self.assertRaises(ValueError, base_rule._construct_decision_dict, ('reason', []))

    def test_construct_decision_dict__store(self):

        base_rule = GeoprocessingBaseRule()
        base_rule._entity_rec = {'entity_type': 'store'}
        decision_dict = base_rule._construct_decision_dict('reason', ['flags'])
        self.assertEqual({
            'reason': 'reason',
            'flags': ['flags']
        }, decision_dict)

    def test_construct_methods_decisions(self):

        method_decisions = GeoprocessingBaseRule._construct_methods_decisions(self.base_rule)

        self.assertEqual({
            GMR.GetDemographics: None,
            GMR.FindCompetition: None
        }, method_decisions)

    def test_extract_most_correct_ids__has_most_correct_ids(self):

        self.base_rule._entity_rec = {
            'links': {
                'retail_input_record': {
                    'retail_input': [
                        {
                        'entity_role_to': 'most_correct_record',
                        'entity_id_to': 'most_correct_id',
                        '_id': 'correct_link_id'
                        },{
                        'entity_role_to': 'just_a_normal_rir',
                        'entity_id_to': 'normal_rir_id',
                        '_id': 'normal_link_id'
                        }
                    ]
                }
            }
        }

        link_id = GeoprocessingBaseRule._extract_most_correct_rir_link_id(self.base_rule)

        self.assertEqual('correct_link_id', link_id)

    def test_extract_most_correct_ids__has_rir_ids__none_are_most_correct(self):

        self.base_rule._entity_rec = {
            'links': {
                'retail_input_record': {
                    'retail_input': [
                        {
                        'entity_role_to': 'just_a_normal_rir',
                        'entity_id_to': 'most_correct_id',
                        '_id': 'correct_link_id'
                        },{
                        'entity_role_to': 'just_a_normal_rir',
                        'entity_id_to': 'normal_rir_id',
                        '_id': 'normal_link_id'
                        }
                    ]
                }
            }
        }

        link_id = GeoprocessingBaseRule._extract_most_correct_rir_link_id(self.base_rule)

        self.assertEqual(None, link_id)

    def test_extract_most_correct_ids__has_no_rir_ids(self):

        self.base_rule._entity_rec = {
            'links': {
                'retail_input_record': {
                    'retail_input': []
                }
            }
        }

        link_id = GeoprocessingBaseRule._extract_most_correct_rir_link_id(self.base_rule)

        self.assertEqual(None, link_id)

    def test_extract_most_correct_ids__has_no_retail_input_field(self):

        self.base_rule._entity_rec = {
            'links': {
                'retail_input_record': {}
            }
        }

        link_id = GeoprocessingBaseRule._extract_most_correct_rir_link_id(self.base_rule)

        self.assertEqual(None, link_id)

    def test_extract_most_correct_ids__has_no_retail_input_record_field(self):

        self.base_rule._entity_rec = {
            'links': {}
        }

        link_id = GeoprocessingBaseRule._extract_most_correct_rir_link_id(self.base_rule)

        self.assertEqual(None, link_id)

    def test_extract_most_correct_ids__has_no_links_field(self):

        self.base_rule._entity_rec = {}

        link_id = GeoprocessingBaseRule._extract_most_correct_rir_link_id(self.base_rule)

        self.assertEqual(None, link_id)

