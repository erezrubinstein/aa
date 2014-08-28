from collections import OrderedDict
import datetime
import mox
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.company_rules.company_rules import IsPublished, HasNewIndustryClassification
from core.common.business_logic.service_entity_logic.geoprocessing_rules.geoprocessing_reference import GeoprocessingMethodsReference

__author__ = 'kingneptune'

class GeoprocessingCompanyRulesTests(mox.MoxTestBase):

    def setUp(self):
        super(GeoprocessingCompanyRulesTests, self).setUp()
        register_common_mock_dependencies(self.mox)
        
    def doCleanups(self):
        super(GeoprocessingCompanyRulesTests, self).doCleanups()
        dependencies.clear()


    def test_IsPublished_initialization(self):

        is_published = IsPublished({'entity': 'rec'})
        self.assertEqual(is_published._entity_rec, {'entity': 'rec'})
        self.assertEqual(is_published.name, 'is_published')

    def test_IsPublsihed_evaluate__is_published(self):

        is_published = self.mox.CreateMock(IsPublished)
        is_published._entity_rec = {
            'data': {
                'workflow': {
                    'current': {
                        'status': 'published'
                    }
                }
            }
        }

        is_published._get_latest_status_change_date().AndReturn(1)

        is_published._find_latest_validation_date().AndReturn(0)

        unordered_methods_decisions = {
            'random_method': None,
            GeoprocessingMethodsReference.GetDemographics: None,
            GeoprocessingMethodsReference.FindCompetition: None
        }

        is_published._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        published_false_reason = "This company's trade areas have not been flagged for geoprocessing after its status changed to 'published'"
        is_published._get_flags_to_emit().MultipleTimes().AndReturn(['published', 'flags'])
        is_published._construct_decision_dict(published_false_reason, flags_to_emit = ['published', 'flags']).MultipleTimes().AndReturn('published and flags will be set')

        expected_methods_decisions = {
            'random_method': 'published and flags will be set',
            GeoprocessingMethodsReference.GetDemographics: 'published and flags will be set',
            GeoprocessingMethodsReference.FindCompetition: 'published and flags will be set',
        }

        self.mox.ReplayAll()

        methods_decisions = IsPublished.evaluate(is_published)

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_IsPublsihed_evaluate__is_published__flags_already_set(self):

        is_published = self.mox.CreateMock(IsPublished)
        is_published._entity_rec = {
            'data': {
                'workflow': {
                    'current': {
                        'status': 'published'
                    }
                }
            }
        }

        is_published._get_latest_status_change_date().AndReturn(0)

        is_published._find_latest_validation_date().AndReturn(1)

        unordered_methods_decisions = {
            'random_method': None,
            GeoprocessingMethodsReference.GetDemographics: None,
            GeoprocessingMethodsReference.FindCompetition: None
        }

        is_published._methods_decisions = OrderedDict(sorted(unordered_methods_decisions.items()))

        published_false_reason = "The company's trade areas have already been flagged for geoprocessing after its status changed to 'published'"
        is_published._construct_decision_dict(published_false_reason).MultipleTimes().AndReturn('published and flags will not be set')

        expected_methods_decisions = {
            'random_method': 'published and flags will not be set',
            GeoprocessingMethodsReference.GetDemographics: 'published and flags will not be set',
            GeoprocessingMethodsReference.FindCompetition: 'published and flags will not be set',
        }

        self.mox.ReplayAll()

        methods_decisions = IsPublished.evaluate(is_published)

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_IsPublsihed_evaluate__is_not_published(self):

        is_published = self.mox.CreateMock(IsPublished)
        is_published._entity_rec = {
            'data': {
                'workflow': {
                    'current': {
                        'status': 'new'
                    }
                }
            }
        }

        is_published._methods_decisions = {
            GeoprocessingMethodsReference.GetDemographics: None,
            GeoprocessingMethodsReference.FindCompetition: None
        }

        not_published_reason = "The company's current workflow status is '%s', not 'published'" % 'new'
        is_published._construct_decision_dict(not_published_reason).MultipleTimes().AndReturn('I am not published')

        self.mox.ReplayAll()

        methods_decisions = IsPublished.evaluate(is_published)

        self.assertEqual({
            GeoprocessingMethodsReference.GetDemographics: 'I am not published',
            GeoprocessingMethodsReference.FindCompetition: 'I am not published'
        }, methods_decisions)

    def test_HasNewIndustryClassification__changed__never_validated(self):

        changed_rec = {
            'entity_type': 'company',
            'meta': {
                'history': {
                    'summary': [
                        {
                            'f': 'links.industry.industry_classification',
                            't': datetime.datetime(1989, 05, 18)
                        },
                        {
                            'f': 'links.industry.industry_classification',
                            't': datetime.datetime(1991, 05, 18)
                        }
                    ]
                }
            },
            'data': {}
        }

        hnic = HasNewIndustryClassification(changed_rec)

        meta_docs = [
            {
                'field': 'links.industry.industry_classification',
                'timestamp': datetime.datetime(1989, 05, 18)
            },
            {
                'field': 'links.industry.industry_classification',
                'timestamp': datetime.datetime(1991, 05, 18)
            }
        ]

        self.mox.StubOutWithMock(hnic, '_get_meta_docs')
        hnic._get_meta_docs().AndReturn(meta_docs)
        self.mox.ReplayAll()

        methods_decisions = hnic.evaluate()
        expected_methods_decisions = {
            'get_demographics': None,
            'find_competition': {
                'reason': "There has been a change to this company's industry classification",
                'flags': [{
                    'affected_trade_area_ids': '_all_child_trade_areas',
                    'name': 'parent_companys_industry_classification_changed'
                }]
            },
            'find_white_space_competition': None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_HasNewIndustryClassification__changed__validated(self):

        changed_rec = {
            'entity_type': 'industry',
            'meta': {
                'history': {
                    'summary': [
                        {
                            'f': 'links.industry.industry_classification',
                            't': datetime.datetime(1991, 05, 18)
                        }
                    ]
                }
            },
            'data': {
                'geoprocessing': {
                    'latest_validation_date': datetime.datetime(1991, 05, 19)
                }
            }
        }

        hnic = HasNewIndustryClassification(changed_rec)


        meta_docs = [
            {
                'field': 'links.industry.industry_classification',
                'timestamp': datetime.datetime(1991, 05, 18)
            }
        ]

        self.mox.StubOutWithMock(hnic, '_get_meta_docs')
        hnic._get_meta_docs().AndReturn(meta_docs)
        self.mox.ReplayAll()

        methods_decisions = hnic.evaluate()

        expected_methods_decisions = {
            'get_demographics': None,
            'find_competition': {
                'reason': "There has not been a change to this company's industry classification",
                'flags': []
            },
            'find_white_space_competition': None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_HasNewIndustryClassification__not_changed(self):

        changed_rec = {
            'entity_type': 'industry',
            'meta': {
                'history': {
                    'summary': []
                }
            },
            'data': {
                'geoprocessing': {
                    'latest_validation_date': datetime.datetime(1991, 05, 19)
                }
            }
        }

        hnic = HasNewIndustryClassification(changed_rec)

        meta_docs = [
        ]

        self.mox.StubOutWithMock(hnic, '_get_meta_docs')
        hnic._get_meta_docs().AndReturn(meta_docs)
        self.mox.ReplayAll()

        methods_decisions = hnic.evaluate()

        expected_methods_decisions = {
            'get_demographics': None,
            'find_competition': {
                'reason': "There has not been a change to this company's industry classification",
                'flags': []
            },
            'find_white_space_competition': None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_HasNewIndustryClassification__not_changed__not_validated(self):

        changed_rec = {
            'entity_type': 'industry',
            'meta': {
                'history': {
                    'summary': []
                }
            },
            'data': {
                'geoprocessing': {}
            }
        }

        hnic = HasNewIndustryClassification(changed_rec)

        meta_docs = [
        ]

        self.mox.StubOutWithMock(hnic, '_get_meta_docs')
        hnic._get_meta_docs().AndReturn(meta_docs)
        self.mox.ReplayAll()

        methods_decisions = hnic.evaluate()

        expected_methods_decisions = {
            'get_demographics': None,
            'find_competition': {
                'reason': "There has not been a change to this company's industry classification",
                'flags': []
            },
            'find_white_space_competition': None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)
