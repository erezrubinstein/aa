import datetime
import mox
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.industry_rules.industry_rules import IndustryCompetitionChanged

__author__ = 'kingneptune'

class GeoprocessingIndustryRulesTests(mox.MoxTestBase):

    def setUp(self):
        super(GeoprocessingIndustryRulesTests, self).setUp()
        register_common_mock_dependencies(self.mox)

    def doCleanups(self):
        super(GeoprocessingIndustryRulesTests, self).doCleanups()
        dependencies.clear()
    
    def test_IndustryCompetitionChanged__changed__never_validated(self):

        changed_rec = {
            'entity_type': 'industry',
            'meta': {
                'history': {
                    'summary': [
                        {
                            'f': 'links.industry.industry_competition',
                            't': datetime.datetime(1989, 05, 18)
                        },
                        {
                            'f': 'links.industry.industry_competition',
                            't': datetime.datetime(1991, 05, 18)
                        }
                    ]
                }
            },
            'data': {}
        }

        icc = IndustryCompetitionChanged(changed_rec)

        meta_docs = [
            {
                'field': 'links.industry.industry_competition',
                'timestamp': datetime.datetime(1989, 05, 18)
            },
            {
                'field': 'links.industry.industry_competition',
                'timestamp': datetime.datetime(1991, 05, 18)
            }
        ]

        self.mox.StubOutWithMock(icc, '_get_meta_docs')
        icc._get_meta_docs().AndReturn(meta_docs)
        self.mox.ReplayAll()

        methods_decisions = icc.evaluate()
        expected_methods_decisions = {
            'get_demographics': None,
            'find_competition': {
                'reason': "There has been a change to this industry's competition",
                'flags': [{
                    'affected_trade_area_ids': '_all_child_trade_areas',
                    'name': 'parent_industry_competition_changed'
                }]
            },
            'find_white_space_competition': None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)

    def test_IndustryCompetitionChanged__changed__validated(self):

        changed_rec = {
            'entity_type': 'industry',
            'meta': {
                'history': {
                    'summary': [
                        {
                            'f': 'links.industry.industry_competition',
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

        icc = IndustryCompetitionChanged(changed_rec)


        meta_docs = [
            {
                'field': 'links.industry.industry_competition',
                'timestamp': datetime.datetime(1991, 05, 18)
            }
        ]

        self.mox.StubOutWithMock(icc, '_get_meta_docs')
        icc._get_meta_docs().AndReturn(meta_docs)
        self.mox.ReplayAll()

        methods_decisions = icc.evaluate()

        expected_methods_decisions = {
            'get_demographics': None,
            'find_competition': {
                'reason': "There has not been a change to this industry's competition",
                'flags': []
            },
            'find_white_space_competition': None
        }

        self.assertEqual(expected_methods_decisions, methods_decisions)