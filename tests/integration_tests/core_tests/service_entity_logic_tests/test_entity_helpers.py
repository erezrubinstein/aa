from tests.integration_tests.core_tests.service_entity_logic_tests.implementation.address_helper_test_collection import AddressHelperTestCollection
from tests.integration_tests.core_tests.service_entity_logic_tests.implementation.company_helper_test_collection import CompanyHelperTestCollection
from tests.integration_tests.core_tests.service_entity_logic_tests.implementation.industry_helper_test_collection import IndustryHelperTestCollection
from tests.integration_tests.core_tests.service_entity_logic_tests.implementation.store_helper_test_collection import StoreHelperTestCollection
from tests.integration_tests.core_tests.service_entity_logic_tests.implementation.trade_area_upserter_test_collection import TradeAreaUpserterTestCollection
from tests.integration_tests.core_tests.service_entity_logic_tests.implementation.data_access_test_collection import CoreDataAccessTestCollection
from tests.integration_tests.core_tests.service_entity_logic_tests.implementation.white_space_helper_test_collection import WhiteSpaceHelperTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_raw_data_storage.rds_api import app as rds_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from core.service.svc_main.main_api import app as main_app
import unittest


__author__ = 'erezrubinstein'


class TestEntityHelpers(ServiceTestCase):
    """
    Test case for Main Service Export Data functions.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {"MAIN": main_app, "MDS": mds_app, "RDS": rds_app, "WFS": wfs_app}
        cls.svc_key = "MAIN"
        cls.test_colls = {
            "ADDRESS_HELPER": AddressHelperTestCollection,
            "COMPANY_HELPER": CompanyHelperTestCollection,
            "INDUSTRY_HELPER": IndustryHelperTestCollection,
            "STORE_HELPER": StoreHelperTestCollection,
            "TRADE_AREA_UPSERTER": TradeAreaUpserterTestCollection,
            "CORE_DATA_ACCESS": CoreDataAccessTestCollection,
            "WHITE_SPACE_HELPER": WhiteSpaceHelperTestCollection
        }
        cls.svc_main_exempt = {}

    #-----------------------------------# ADDRESS_HELPER #-----------------------------------#

    def test_get_addresses_per_store(self):
        self.tests["ADDRESS_HELPER"].test_get_addresses_per_store()

    def test_get_addresses_per_company_ids(self):
        self.tests["ADDRESS_HELPER"].test_get_addresses_per_company_ids()

    #-----------------------------------# COMPANY_HELPER #-----------------------------------#

    def test_select_companies_by_id(self):
        self.tests["COMPANY_HELPER"].test_select_companies_by_id()

    def test_comprehensive_file_finder_one_file_old_encoder(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_one_file_old_encoder()

    def test_comprehensive_file_finder_one_file(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_one_file()

    def test_comprehensive_file_finder_two_files_one_file_not_comprehensive_old_encoder(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_two_files_one_file_not_comprehensive_old_encoder()

    def test_comprehensive_file_finder_two_files_one_file_not_comprehensive(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_two_files_one_file_not_comprehensive()

    def test_comprehensive_file_finder_two_files_get_earliest_old_encoder(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_two_files_get_earliest_old_encoder()

    def test_comprehensive_file_finder_two_files_get_earliest(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_two_files_get_earliest()

    def test_comprehensive_file_finder_outside_interval_old_encoder(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_outside_interval_old_encoder()

    def test_comprehensive_file_finder_outside_interval(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_outside_interval()

    def test_comprehensive_file_finder_on_interval_lt_old_encoder(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_on_interval_lt_old_encoder()

    def test_comprehensive_file_finder_on_interval_lt(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_on_interval_lt()

    def test_comprehensive_file_finder_on_interval_strange_formats_lt(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_on_interval_strange_formats_lt()

    def test_comprehensive_file_finder_on_interval_gt_old_encoder(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_on_interval_gt_old_encoder()

    def test_comprehensive_file_finder_on_interval_gt(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_on_interval_gt()

    def test_comprehensive_file_finder_on_interval_strange_formats_gt(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_on_interval_strange_formats_gt()

    def test_comprehensive_file_finder_within_interval_strange_formats(self):
        self.tests["COMPANY_HELPER"].test_comprehensive_file_finder_within_interval_strange_formats()

    def test_select_companies_by_name_for_typeahead(self):
        self.tests["COMPANY_HELPER"].select_companies_by_name_for_typeahead()

    def test_select_company_ids_by_primary_industry_ids(self):
        self.tests["COMPANY_HELPER"].test_select_company_ids_by_primary_industry_ids()

    def test_select_competitive_companies(self):
        self.tests["COMPANY_HELPER"].test_select_competitive_companies()

    def test_select_competitive_companies__non_published_companies(self):
        self.tests["COMPANY_HELPER"].test_select_competitive_companies__non_published_companies()

    def test_select_competitive_companies__multiple_competition_records(self):
        self.tests["COMPANY_HELPER"].test_select_competitive_companies__multiple_competition_records()

    def test_delete_ccis(self):
        self.tests["COMPANY_HELPER"].test_delete_ccis()

    def test_get_published_banner_ids_of_parent(self):
        self.tests["COMPANY_HELPER"].test_get_published_banner_ids_of_parent()

    def test_get_company_family(self):
        self.tests["COMPANY_HELPER"].test_get_company_family()

    def test_get_published_company_family_ids_for_company_ids(self):
        self.tests["COMPANY_HELPER"].test_get_published_company_family_ids_for_company_ids()

    #-----------------------------------# INDUSTRY_HELPER #-----------------------------------#

    def test_get_industry_names_by_ids(self):
        self.tests["INDUSTRY_HELPER"].test_get_industry_names_by_ids()

    def test_get_company_ids_by_primary_industry_id(self):
        self.tests["INDUSTRY_HELPER"].test_get_company_ids_by_primary_industry_id()

    def test_get_company_ids_by_primary_industry_id__no_companies(self):
        self.tests["INDUSTRY_HELPER"].test_get_company_ids_by_primary_industry_id__no_companies()

    def test_get_competing_industries(self):
        self.tests["INDUSTRY_HELPER"].test_get_competing_industries()

    def test_structure_new_industry(self):
        self.tests["INDUSTRY_HELPER"].test_structure_new_industry()

    #-----------------------------------# STORE_HELPER #-----------------------------------#

    def test_store_helper_test_delete_store_and_all_children(self):
        self.tests["STORE_HELPER"].store_helper_test_delete_store_and_all_children()

    def test_select_potential_away_stores_for_geoprocessing__companies_filter(self):
        self.tests["STORE_HELPER"].test_select_potential_away_stores_for_geoprocessing__companies_filter()

    def test_select_potential_away_stores_for_geoprocessing__lat_long_filter(self):
        self.tests["STORE_HELPER"].test_select_potential_away_stores_for_geoprocessing__lat_long_filter()

    def test_select_potential_away_stores_for_geoprocessing__test_open_close_dates(self):
        self.tests["STORE_HELPER"].test_select_potential_away_stores_for_geoprocessing__test_open_close_dates()

    def test_select_potential_away_stores_for_geoprocessing__ignore_self(self):
        self.tests["STORE_HELPER"].test_select_potential_away_stores_for_geoprocessing__ignore_self()

    #-----------------------------------# TRADE_AREA_UPSERTER #-----------------------------------#

    def test_upsert_trade_area__new(self):
        self.tests["TRADE_AREA_UPSERTER"].test_upsert_trade_area__new()

    def test_upsert_trade_area__same_threshold(self):
        self.tests["TRADE_AREA_UPSERTER"].test_upsert_trade_area__same_threshold()

    def test_upsert_trade_area__different_threshold(self):
        self.tests["TRADE_AREA_UPSERTER"].test_upsert_trade_area__different_threshold()

    #-----------------------------------# CORE_DATA_ACCESS #-----------------------------------#

    def test_select_company_id_force_insert_basic(self):
        self.tests["CORE_DATA_ACCESS"].test_select_company_id_force_insert_basic()

    def test_select_company_id_force_insert_containing_names(self):
        self.tests["CORE_DATA_ACCESS"].test_select_company_id_force_insert_containing_names()

    def test_select_company_id_force_insert_escaped_chars(self):
        self.tests["CORE_DATA_ACCESS"].test_select_company_id_force_insert_escaped_chars()

    #-----------------------------------# WHITE_SPACE_HELPER #-----------------------------------#

    def test_white_space_helper_select_grid_cells_by_lat_long(self):
        self.tests["WHITE_SPACE_HELPER"].test_select_grid_cells_by_lat_long()


if __name__ == '__main__':
    unittest.main()
