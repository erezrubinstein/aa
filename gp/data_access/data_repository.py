from geoprocessing.data_access.address_handler import get_address_by_id, get_problem_long_lat, is_already_mopped, mark_as_mopped, insert_new_address_get_id, select_addresses_within_range, update_address
from geoprocessing.data_access.company_competition_handler import insert_company_competition, select_all_open_competitive_companies_ids_for_company, close_old_company_competitors
from geoprocessing.data_access.company_handler import select_company_id_force_insert, update_company_ticker, select_sector_ids_for_company, close_old_companies_sectors, insert_company_sectors, get_company_by_id, select_all_companies
from geoprocessing.data_access.data_check_handler import save_data_check, get_sql_data_check_types, execute_data_check_type_sql, get_non_sql_data_check_rowcounts
from geoprocessing.data_access.demographics_handler import get_seg_id, select_data_item_by_name, insert_demographics
from geoprocessing.data_access.logging_handler import insert_logging_records, select_logs_by_log_entry_type_ids, select_function_performance
from geoprocessing.data_access.monopoly_handler import delete_from_monopolies, select_active_monopoly_record, close_monopoly_record, insert_monopoly, insert_monopoly_postgis, select_active_monopoly_record_postgis, close_monopoly_record_postgis, delete_from_monopolies_postgis
from geoprocessing.data_access.period_handler import PeriodQueryHelper, select_period_by_period_id
from geoprocessing.data_access.postgis_handler import compute_overlap_area, get_distance_between_points, shape_contains_point, get_centroid_point_string_from_shape, get_surface_area, determine_srid_from_UTM_and_datum, get_geoco_city_state_zip, determine_union_shape, determine_intersecting_shape, shape_contains_points, multi_shape_contain_points
from geoprocessing.data_access.report_generator_handler import select_row_counts_from_tables
from geoprocessing.data_access.sector_handler import save_sector_name_get_id
from geoprocessing.data_access.change_log_handler import save_stores_to_change_log, save_address_to_change_log
from geoprocessing.data_access.source_file_handler import delete_loader_records_for_current_file, save_loader_records_and_parsed_addresses, insert_source_file, select_source_file_by_source_file_id, select_source_file_record_by_source_file_record_id
from geoprocessing.data_access.store_competition_handler import delete_from_competitive_stores, get_competitive_stores, close_competitive_stores_by_id, get_competitive_stores_postgis, close_competitive_stores_by_id_postgis, delete_from_competitive_stores_postgis, get_competitive_store_by_id, batch_upsert_competitive_stores
from geoprocessing.data_access.store_handler import get_away_stores_within_lat_long_range, get_store_by_id, get_open_store_ids_and_open_dates_for_company, insert_store_return_with_new_store_id, close_old_stores, get_all_store_ids_from_company_id, get_all_store_ids_with_company_ids, get_zips_within_lat_long_range, get_zip_by_zip_code, get_count_stores_by_company_id, get_matched_open_store_from_db, save_zip_proximities, update_store, select_address_id_by_core_store_id, get_matched_open_store_from_db_by_core_store_id
from geoprocessing.data_access.trade_area_handler import select_trade_area_force_insert, insert_trade_area_shape, save_trade_area_surface_area, save_trade_area_overlap, select_trade_areas_by_store_id_require_shape, select_trade_area_shape_by_id, select_period_id_from_trade_area_shapes_by_id, delete_trade_area_analytics, delete_trade_area_shape, delete_trade_area, select_away_trade_areas_within_lat_long_range, select_trade_area_by_store_id_and_threshold_id, select_trade_areas_for_core_export
from geoprocessing.data_access.census_ingest_handler import insert_census_data, bulk_insert_census_data, get_census_data_row_count


__author__ = 'erezrubinstein'


class DataRepository(object):
    """
    This class serves as the Dependency Injection (IoC) instance.
    """

    def __init__(self):

        self.is_sql = True

############################################# Demographics Queries ######################################################

    def insert_demographics(self, trade_area, period_id, demographic_report_items, template_name, dataset_id):
        return insert_demographics(trade_area, period_id, demographic_report_items, template_name, dataset_id)

    def get_seg_id(self, report_item):
        return get_seg_id(report_item)

############################################ Trade Area Queries ########################################################
    def select_trade_areas_for_core_export(self, store_ids):
        return select_trade_areas_for_core_export(store_ids)

    def save_trade_area_surface_area(self, trade_area):
        return save_trade_area_surface_area(trade_area)

    def save_trade_area_overlap(self, trade_area_overlap):
        return save_trade_area_overlap(trade_area_overlap)
    
    def select_trade_area_by_store_id_and_threshold_id(self, store_id, threshold_id):
        return select_trade_area_by_store_id_and_threshold_id(store_id, threshold_id)

    def select_trade_area_force_insert(self, store_id, threshold):
        return select_trade_area_force_insert(store_id, threshold)

    def insert_trade_area_shape(self, trade_area_id, trade_area_shape_coordinates, period_id):
        return insert_trade_area_shape(trade_area_id, trade_area_shape_coordinates, period_id)

    def select_trade_areas_by_store_id_require_shape(self, store_id):
        return select_trade_areas_by_store_id_require_shape(store_id)

    def select_away_trade_areas_within_lat_long_range(self, home_store, longitude_ranges, latitude_range):
        return select_away_trade_areas_within_lat_long_range(home_store, longitude_ranges, latitude_range)

    def select_trade_area_shape_by_id(self, trade_area_id):
        return select_trade_area_shape_by_id(trade_area_id)

    def select_period_id_from_trade_area_shapes_by_id(self, trade_area_id):
        return select_period_id_from_trade_area_shapes_by_id(trade_area_id)

    def delete_trade_area(self, trade_area):
        return delete_trade_area(trade_area)

    def delete_trade_area_analytics(self, trade_area):
        return delete_trade_area_analytics(trade_area)

    def delete_trade_area_shape(self, trade_area):
        return delete_trade_area_shape(trade_area)

############################################### Address Queries ########################################################


    def get_problem_long_lat(self, store):
        return get_problem_long_lat(store)

    def get_address_by_id(self, store_id):
        return get_address_by_id(store_id)

    def insert_new_address_get_id(self, address):
        return insert_new_address_get_id(address)

    def select_addresses_within_range(self, search_limits_long, search_limits_lat, company_id = None):
        return select_addresses_within_range(search_limits_long, search_limits_lat, company_id)

    def update_address(self, address):
        return update_address(address)

    def is_already_mopped(self, store_id):
        return is_already_mopped(store_id)

    def mark_as_mopped(self, problem_store_id):
        mark_as_mopped(problem_store_id)

    def delete_loader_records_for_current_file(self, company_info):
        delete_loader_records_for_current_file(company_info)

    def save_loader_records_and_parsed_addresses(self, company_info):
        save_loader_records_and_parsed_addresses(company_info)



################################################ Store Queries #########################################################

    def select_address_id_by_core_store_id(self, core_store_id):
        return select_address_id_by_core_store_id(core_store_id)

    def get_matched_open_store_from_db_by_core_store_id(self, core_store_id):
        return get_matched_open_store_from_db_by_core_store_id(core_store_id)

    def get_matched_open_store_from_db(self, address_id, company_id, phone, store_format):
        return get_matched_open_store_from_db(address_id, company_id, phone, store_format)

    def get_count_stores_by_company_id(self, company_id):
        return get_count_stores_by_company_id(company_id)

    def get_store_by_id(self, store_id):
        return get_store_by_id(store_id)

    def get_store_ids(self, company_id):
        return get_all_store_ids_from_company_id(company_id)

    def get_all_store_ids_with_company_ids(self):
        return get_all_store_ids_with_company_ids()

    def get_open_store_ids_and_open_dates_for_company(self, company_info):
        return get_open_store_ids_and_open_dates_for_company(company_info)

    def get_all_store_ids_from_company_id(self, company_id):
        return get_all_store_ids_from_company_id(company_id)

    def save_stores_to_change_log(self, deleted_store_ids, changed_stores, file_created_date, source_file_id):
        return save_stores_to_change_log(deleted_store_ids, changed_stores, file_created_date, source_file_id)

    def save_address_to_change_log(self, changed_address, file_created_date, source_file_id):
        return save_address_to_change_log(changed_address, file_created_date, source_file_id)

    def get_away_stores_within_lat_long_range(self, home_store, latitude_range, longitude_ranges):
        return get_away_stores_within_lat_long_range(home_store, latitude_range, longitude_ranges)

    def insert_store_return_with_new_store_id(self, store):
        return insert_store_return_with_new_store_id(store)

    def update_store(self, store):
        update_store(store)

    def close_old_stores(self, store_ids, assumed_closed_date):
        close_old_stores(store_ids, assumed_closed_date)

    def get_zips_within_lat_long_range(self, latitude_range, longitude_ranges):
        return get_zips_within_lat_long_range(latitude_range, longitude_ranges)

    def get_zip_by_zip_code(self, zip_code):
        return get_zip_by_zip_code(zip_code)

    def save_zip_proximities(self, store_zip_proximities):
        return save_zip_proximities(store_zip_proximities)

############################################## Monopoly Queries ########################################################

    def select_active_monopoly_record(self, store_id, trade_area_id, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        return select_active_monopoly_record(store_id, trade_area_id)

    def close_monopoly_record(self, store_id, trade_area_id, end_date, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        return close_monopoly_record(store_id, trade_area_id, end_date)

    def delete_from_monopolies(self, store_id, trade_area_id):
        delete_from_monopolies(store_id, trade_area_id)

    def insert_monopoly(self, store_id, monopoly_type_id, trade_area_id, start_date, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        return insert_monopoly(store_id, monopoly_type_id, trade_area_id, start_date)

    def batch_upsert_monopolies(self, trade_area_id, batch_monopolies_list):
        # this is purely for forwards compatibility, which only core uses.
        pass


########################################## Competitive Stores Queries ##################################################

    def get_competitive_stores(self, home_store_id, trade_area_id):
        return get_competitive_stores(home_store_id, trade_area_id)

    def batch_upsert_competitive_stores(self, trade_area_id, competitive_stores):
        return batch_upsert_competitive_stores(trade_area_id, competitive_stores)

    def close_competitive_stores_by_id(self, home_store_id, away_store_id, trade_area_id, end_date):
        return close_competitive_stores_by_id(home_store_id, away_store_id, trade_area_id, end_date)

    def delete_from_competitive_stores(self, home_store_id, away_store_id):
        delete_from_competitive_stores(home_store_id, away_store_id)

    def get_competitive_store_by_id(self, competitive_store_id):
        return get_competitive_store_by_id(competitive_store_id)

############################################### Data Check Queries #####################################################

    def get_sql_data_check_types(self):
        return get_sql_data_check_types()

    def save_data_check(self, data_check):
        return save_data_check(data_check)

    def execute_data_check_type_sql(self, data_check_type):
        return execute_data_check_type_sql(data_check_type)

################################################ Company Queries #######################################################

    def select_company_id_force_insert(self, company_name):
        return select_company_id_force_insert(company_name)

    def update_company_ticker(self, company_id, ticker):
        update_company_ticker(company_id, ticker)

    def insert_source_file(self, file_path, file_created_date, file_size_in_bytes):
        return insert_source_file(file_path, file_created_date, file_size_in_bytes)

    def get_company_by_id(self, company_id):
        return get_company_by_id(company_id)

    ## company_sectors queries
    def select_sector_ids_for_company(self, company_id):
        return select_sector_ids_for_company(company_id)

    def close_old_companies_sectors(self, sector_ids, assumed_end_date):
        close_old_companies_sectors(sector_ids, assumed_end_date)

    def insert_company_sectors(self, sectors, company_id, assumed_start_date):
        insert_company_sectors(sectors, company_id, assumed_start_date)

    def select_all_companies(self):
        return select_all_companies()


########################################## Competitive Companies Queries ###############################################

    def insert_company_competition(self, competitors):
        insert_company_competition(competitors)

    def select_all_open_competitive_companies_ids_for_company(self, company_id):
        return select_all_open_competitive_companies_ids_for_company(company_id)

    def close_old_company_competitors(self, away_company_ids, home_company_id, assumed_end_date):
        close_old_company_competitors(away_company_ids, home_company_id, assumed_end_date)



########################################## Sector Queries ##############################################################

    def save_sector_name_get_id(self, sector_name):
        return save_sector_name_get_id(sector_name)



######################################### Logging Queries ##############################################################

    def insert_logging_records(self, logging_records):
        return insert_logging_records(logging_records)

    def select_logs_by_log_entry_type_ids(self, log_entry_type_ids):
        return select_logs_by_log_entry_type_ids(log_entry_type_ids)

    def select_function_performance(self):
        return select_function_performance()

#################################################### Census Ingest Methods #############################################

    def insert_census_data(self, census_ingest_provider, rows_per_batch, max_threads):
        return insert_census_data(census_ingest_provider, rows_per_batch, max_threads)

    def get_census_data_row_count(self, census_ingest_provider):
        return get_census_data_row_count(census_ingest_provider)

    def bulk_insert_census_data(self, census_ingest_provider, db_server, db_database, db_username, db_password):
        return bulk_insert_census_data(census_ingest_provider, db_server, db_database, db_username, db_password)



########################################## Report Generator Queries ####################################################

    def select_row_counts_from_tables(self, tables):
        return select_row_counts_from_tables(tables)

    def get_non_sql_data_check_rowcounts(self):
        return get_non_sql_data_check_rowcounts()


########################################## MISC Queries ################################################################

    def select_period_id_for_year_force_insert(self, year):
        return PeriodQueryHelper().select_period_id_for_year(year)

    def select_period_by_period_id(self, period_id):
        return select_period_by_period_id(period_id)

    def select_source_file_by_source_file_id(self, source_file_id):
        return select_source_file_by_source_file_id(source_file_id)

    def select_source_file_record_by_source_file_record_id(self, source_file_record_id):
        return select_source_file_record_by_source_file_record_id(source_file_record_id)



########################################################################################################################
########################################### PostGIS Data Repository ####################################################
########################################################################################################################

class DataRepositorySpecializedForPostGIS(DataRepository):
    """
    A Data Repository for storing the results of PostGIS geoprocessing routines.
    This is helpful for migrating from ArcGIS-based geoprocessing to PostGIS-based processing.
    To use, reference this class -- instead of the normal DataRepository -- in dependency injection.
    """
    def __init__(self):
        pass

    def get_competitive_stores(self, home_store_id, trade_area_id):
        return get_competitive_stores_postgis(home_store_id, trade_area_id)

    def close_competitive_stores_by_id(self, home_store_id, away_store_id, trade_area_id, end_date):
        return close_competitive_stores_by_id_postgis(home_store_id, away_store_id, trade_area_id, end_date)

    def delete_from_competitive_stores(self, home_store_id, away_store_id):
        return delete_from_competitive_stores_postgis(home_store_id, away_store_id)

    def insert_monopoly(self, store_id, monopoly_type_id, trade_area_id, start_date, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        return insert_monopoly_postgis(store_id, monopoly_type_id, trade_area_id, start_date)

    def select_active_monopoly_record(self, store_id, trade_area_id, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        return select_active_monopoly_record_postgis(store_id, trade_area_id)

    def close_monopoly_record(self, store_id, trade_area_id, end_date, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        return close_monopoly_record_postgis(store_id, trade_area_id, end_date)
    
    def delete_from_monopolies(self, store_id, trade_area_id):
        return delete_from_monopolies_postgis(store_id, trade_area_id)


class PostgresDataRepository(object):
    """
    A Data Repository for interacting with Postgres SQL, such as for PostGIS geo_spatial functionality.
    """
    def __init__(self):
        pass

    def get_geoco_city_state_zip(self, geoco):
        return get_geoco_city_state_zip(geoco)

    def get_surface_area(self, shape, srid, wkid):
        return get_surface_area(shape, srid, wkid)

    def get_centroid_point_string_from_shape(self, shape, wkid):
        return get_centroid_point_string_from_shape(shape, wkid)

    def determine_srid_from_UTM_and_datum(self, utm_zone, geodetic_network_datum):
        return determine_srid_from_UTM_and_datum(utm_zone, geodetic_network_datum)

    def shape_contains_point(self, shape, point, wkid):
        return shape_contains_point(shape, point, wkid)

    def shape_contains_points(self, shape, points, wkid):
        return shape_contains_points(shape, points, wkid)

    def multi_shape_contain_points(self, shapes, points, wkid):
        return multi_shape_contain_points(shapes, points, wkid)

    def compute_overlap_area(self, shape_1, shape_2, wkid, midpoint_srid):
        return compute_overlap_area(shape_1, shape_2, wkid, midpoint_srid)

    def determine_intersecting_shape(self, shape_1, shape_2, wkid):
        return determine_intersecting_shape(shape_1, shape_2, wkid)

    def determine_union_shape(self, shape_1, shape_2, wkid):
        return determine_union_shape(shape_1, shape_2, wkid)

    def get_distance_between_points(self, wkt_point_1, wkt_point_2):
        return get_distance_between_points(wkt_point_1, wkt_point_2)
