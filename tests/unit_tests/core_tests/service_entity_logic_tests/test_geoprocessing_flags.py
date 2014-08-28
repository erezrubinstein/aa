from bson.objectid import ObjectId
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic import geoprocessing_helper
from core.common.business_logic.service_entity_logic.geoprocessing_rules.entity_rules.geoprocessing_flags import GeoprocessingFlags

__author__ = 'kingneptune'

class GeoprocessingFlagsTest(mox.MoxTestBase):

    def setUp(self):

        super(GeoprocessingFlagsTest, self).setUp()

        self.geoprocessing_flags = self.mox.CreateMock(GeoprocessingFlags)

    def doCleanups(self):

        super(GeoprocessingFlagsTest, self).doCleanups()

    def test_new_potential_trade_area_competition_flag__has_competitive_stores(self):

        trade_area_rec = {
            'data': {
                'competitive_stores': [
                    {
                        'away_store_id': 1
                    },
                    {
                        'away_store_id': 2
                    },
                    {
                        'away_store_id': 3
                    }
                ]
            }
        }

        gpf = GeoprocessingFlags()

        self.mox.StubOutWithMock(geoprocessing_helper, 'get_trade_areas_by_store_id')
        geoprocessing_helper.get_trade_areas_by_store_id(1).AndReturn([1])
        geoprocessing_helper.get_trade_areas_by_store_id(2).AndReturn([2])
        geoprocessing_helper.get_trade_areas_by_store_id(3).AndReturn([3])
        self.mox.StubOutWithMock(geoprocessing_helper, 'get_potential_competitor_trade_area_ids')
        geoprocessing_helper.get_potential_competitor_trade_area_ids(trade_area_rec).AndReturn([3, 4, 5])

        self.mox.ReplayAll()

        flag = gpf.new_potential_trade_area_competition_flag(trade_area_rec)
        expected_flag = {
            'affected_trade_area_ids': [1, 2, 3, 4, 5],
            'name': gpf.NewPotentialTradeAreaCompetition
        }
        self.assertEqual(expected_flag, flag)

    def test_new_potential_trade_area_competition_flag__has_no_competitive_stores(self):

        trade_area_rec = {
            'data': {}
        }

        gpf = GeoprocessingFlags()

        self.mox.StubOutWithMock(geoprocessing_helper, 'get_potential_competitor_trade_area_ids')
        geoprocessing_helper.get_potential_competitor_trade_area_ids(trade_area_rec).AndReturn([3, 4, 5])

        self.mox.ReplayAll()

        flag = gpf.new_potential_trade_area_competition_flag(trade_area_rec)
        expected_flag = {
            'affected_trade_area_ids': [3, 4, 5],
            'name': gpf.NewPotentialTradeAreaCompetition
        }
        self.assertEqual(expected_flag, flag)

    def test_store_closed(self):

        gpf = GeoprocessingFlags()
        flag = gpf.store_closed_flag()
        expected_flag = {
            'affected_trade_area_ids': '_all_child_trade_areas',
            'name': gpf.ParentStoreClosed
        }
        self.assertEqual(expected_flag, flag)

    def test_new_potential_address(self):

        gpf = GeoprocessingFlags()
        flag = gpf.new_potential_address_flag()
        expected_flag = {
            'affected_trade_area_ids': '_all_child_trade_areas',
            'name': gpf.NewPotentialAddress
        }
        self.assertEqual(expected_flag, flag)

    def test_parent_company_status_switched_to_published_flag(self):

        gpf = GeoprocessingFlags()
        flag = gpf.parent_company_status_switched_to_published_flag()
        expected_flag = {
            'affected_trade_area_ids': '_all_child_trade_areas',
            'name': gpf.ParentCompanyStatusSwitchedToPublished
        }
        self.assertEqual(expected_flag, flag)

    def test_construct_single_flag_to_emit(self):

        flag = GeoprocessingFlags._construct_single_flag_to_emit(self.geoprocessing_flags, [1, 2, 3, 4], 'flag')
        self.assertEqual({
            'affected_trade_area_ids': [1, 2, 3, 4],
            'name': 'flag'
        }, flag)