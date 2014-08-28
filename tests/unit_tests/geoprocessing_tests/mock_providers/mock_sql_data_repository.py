from common.helpers.mock_providers.mock_utilities import get_mock_dictionary_value
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from geoprocessing.business_logic.business_objects.trade_area import TradeArea
from geoprocessing.business_logic.business_objects.zip_code import ZipCode
from common.utilities.inversion_of_control import Dependency, HasAttributes
from common.utilities.signal_math import SignalDecimal

class MockSQLDataRepository(object):
    def __init__(self):

        self.is_sql = True

        self.latitude = 10
        self.longitude = 20
        self.__config = Dependency("Config", HasAttributes("gp1_templates")).value

        # init dictionaries/lists for mocking
        self.mock_trade_areas = {}
        self.competitive_stores = {}
        self.active_monopolies_stores = {}
        self.stores = {}
        self.addresses = {}
        self.competitive_companies = {}
        self.addresses_within_range = []
        self.addresses_within_range_companies = []
        self.problem_geographical_coordinate = None
        self.inserted_census_data = {}
        self.table_row_counts = {}
        self.data_check_entity_ids = {}
        self.logs_by_log_entry_type_id = {}
        self.data_check_types = {}
        self.away_stores_within_range = {}
        self.companies = {}
        self.zips = []
        self.zips_dict = {}
        self.zip_proximities = []
        self.store_count = {}
        self.store_match_phone_number = None
        self.mock_db_stores = []
        self.company_ids_per_name = {}
        self.sector_id_per_name = {}
        self.periods = {}
        self.source_files = {}
        self.source_file_records = {}
        self.period_ids_per_year = {}
        self.open_competitive_companies_per_company = {}
        self.sector_ids_per_company = {}
        self.store_ids_and_opened_dates_for_company = {}
        self.all_companies = []

        # init dictionaries/lists for verifying
        self.inserted_stores = []
        self.inserted_data_types = []
        self.logging_records = []
        self.closed_stores = []
        self.upserted_away_stores = []
        self.upserted_trade_area_ids = []
        self.upserted_monopolies = []
        self.upserted_monopolies_dates = []
        self.upserted_monopolies_trade_areas = []
        self.upserted_monopolies_types = []
        self.upserted_monopolies_batch_list = []
        self.closed_monopolies = []
        self.closed_monopolies_dates = []
        self.closed_monopolies_trade_areas = []
        self.closed_monopolies_batch_list = []
        self.inserted_demographics = []
        self.function_performance_logs = []
        self.saved_trade_areas = []
        self.trade_areas = []
        self.trade_area_shapes = {}
        self.competitive_trade_areas = []
        self.saved_trade_area_overlap_objects = []
        self.trade_area_shape = None
        self.broken_competitors = None
        self.non_sql_data_check_rowcounts = []
        self.changed_address = []
        self.deleted_loader_records = []
        self.phone_number_store_id = {}
        self.loader_records_parsed_addresses = []
        self.deleted_trade_areas = []
        self.deleted_trade_areas_analytics = []
        self.deleted_trade_areas_shapes = []
        self.updated_stores = []
        self.test_company_sectors = []



    ############################################# Demographics Queries ######################################################


    def insert_demographics(self, trade_area, period_id, demographic_report_items, template_name, dataset_id):
        self.inserted_demographics.append({
            "store_id" : trade_area.store_id,
            "demographic_report_items" : demographic_report_items,
            "period_id" : period_id,
            "template_name" : template_name
        })

    def get_seg_id(self, report_item):
        pass



    ############################################ Trade Area Queries ########################################################


    def select_away_trade_areas_within_lat_long_range(self, longitude_ranges, latitude_ranges, home_store):
        return self.competitive_trade_areas

    def save_trade_area_surface_area(self, trade_area):
        self.saved_trade_areas.append(trade_area)

    def save_trade_area_overlap(self, trade_area_overlap_object):
        self.saved_trade_area_overlap_objects.append(trade_area_overlap_object)

    def select_trade_area_by_store_id_and_threshold_id(self, store_id, threshold_id):
        return self.mock_trade_areas[(store_id, threshold_id)]


    def select_trade_area_force_insert(self, store_id, threshold):
        trade_area = TradeArea()
        trade_area.trade_area_id = store_id
        trade_area.store_id = store_id
        trade_area.threshold_id = threshold
        return trade_area

    def insert_trade_area_shape(self, trade_area, trade_area_shape_coordinates, period_id):
        self.trade_area_shape = trade_area_shape_coordinates

    def select_trade_areas_by_store_id_require_shape(self, store_id):
        return [trade_area for trade_area in self.trade_areas if trade_area.store_id == store_id]

    def select_away_trade_areas_within_lat_long_range(self, longitude_ranges, latitude_ranges, home_store):
        return self.competitive_trade_areas

    def select_trade_area_shape_by_id(self, trade_area_id):
        return self.trade_area_shapes[trade_area_id]

    def select_period_id_from_trade_area_shapes_by_id(self, trade_area_id):
        for trade_area in self.trade_areas:
            if trade_area.trade_area_id == trade_area_id:
                return trade_area.period_id

    def delete_trade_area(self, trade_area):
        self.deleted_trade_areas.append(trade_area)

    def delete_trade_area_analytics(self, trade_area):
        self.deleted_trade_areas_analytics.append(trade_area)

    def delete_trade_area_shape(self, trade_area):
        self.deleted_trade_areas_shapes.append(trade_area)

    def get_trade_area_by_id(self, trade_area_id):
        self.trade_area_id = trade_area_id



    ############################################### Address Queries ########################################################

    def get_problem_long_lat(self, store_id):
        return self.problem_geographical_coordinate

    def get_address_by_id(self, address_id):
        return get_mock_dictionary_value(self.addresses, address_id)

    def insert_new_address_get_id(self, address):
        address.address_id = int(address.street_number)
        return address

    def select_addresses_within_range(self, longitude_ranges, latitude_range, company_id = None):
        mocks = []

        # use different list for company specific addresses
        addresses = self.addresses_within_range
        if company_id is not None:
            addresses = self.addresses_within_range_companies

        for address in addresses:
            for longitude_range in longitude_ranges:
                if longitude_range.start <= address.longitude <= longitude_range.stop:
                    mocks.append(address)
        return mocks

    def update_address(self, address):
        self.db_address = address
        return self.db_address

    def is_already_mopped(self, store_id):
        pass

    def mark_as_mopped(self, problem_store_id):
        self.mopped = 1

    def delete_loader_records_for_current_file(self, source_file_id):
        self.deleted_loader_records.append(source_file_id)

    def save_loader_records_and_parsed_addresses(self, company_info):
        for i in range(len(company_info.records)):
            self.loader_records_parsed_addresses.append((company_info.records[i], company_info.parsed_records[i]))



    #################################################### Stores Methods ####################################################

    def get_matched_open_store_from_db(self, address_id, company_id, phone_number, store_format):

        for store in self.mock_db_stores:
            if store.address_id == address_id and store.company_id == company_id and store.phone_number == phone_number and store.store_format == store_format:
                return store

    def get_count_stores_by_company_id(self, company_id):
        return get_mock_dictionary_value(self.store_count, company_id, 0)

    def get_store_by_id(self, store_id):
        return get_mock_dictionary_value(self.stores, store_id)

    def get_store_ids(self, company_id):
        pass

    def get_all_store_ids_with_company_ids(self):
        pass

    def get_open_store_ids_and_open_dates_for_company(self, company_info):
        return get_mock_dictionary_value(self.store_ids_and_opened_dates_for_company, company_info.company_id, [])

    def get_all_store_ids_from_company_id(self, company_id):
        pass

    def save_stores_to_change_log(self, deleted_store_ids, changed_stores, file_created_date, file_size_in_bytes):
        self.deleted_stores = deleted_store_ids
        self.other_stores = changed_stores

    def save_address_to_change_log(self, changed_address, file_created_date, file_size_in_bytes):
        self.changed_address = changed_address

    def get_away_stores_within_lat_long_range(self, home_store, latitude_range, longitude_ranges):
        self.latitude_range = latitude_range
        self.longitude_range = longitude_ranges
        search_limits = GeographicalCoordinate(-1, -1, threshold=SignalDecimal(0.3)).get_search_limits()
        problem_latitude_range = search_limits['latitudes']
        if latitude_range.start == problem_latitude_range.start:
            return self.broken_competitors
        else:
            return self.away_stores_within_range

    def insert_store_return_with_new_store_id(self, store):
        store.store_id = store.address_id
        return store

    def update_store(self, store):
        self.updated_stores.append(store)

    def close_old_stores(self, store_ids, assumed_closed_date):
        id_close_date = {}
        for deleted_store in store_ids:
            id_close_date[deleted_store] = assumed_closed_date
        self.closed_store_and_date = id_close_date

    def get_zips_within_lat_long_range(self, latitude_range, longitude_ranges):
        # use the store's own zip code and lat/long
        # centroid = GeographicalCoordinate(home_store.address.longitude, home_store.address.latitude)
        # return [ZipCode.standard_init(home_store.address.zip_code, centroid)]
        return self.zips

    def get_zip_by_zip_code(self, zip_code):
        centroid = get_mock_dictionary_value(self.zips_dict, zip_code)
        return ZipCode.standard_init(zip_code, centroid)

    def save_zip_proximities(self, zip_proximities):
        self.zip_proximities = zip_proximities



    ################################################### Monopolies Methods ###################################################

    def select_active_monopoly_record(self, store_id, trade_area_id, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        return get_mock_dictionary_value(self.active_monopolies_stores, store_id)

    def close_monopoly_record(self, store_id, trade_area_id, end_date, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        self.closed_monopolies.append(store_id)
        self.closed_monopolies_dates.append(end_date)
        self.closed_monopolies_trade_areas.append(trade_area_id)
        self.closed_monopolies_batch_list.append(True)

    def delete_from_monopolies(self, store_id, trade_area_id):
        self.monopolies_deleted = True
        self.store_id = store_id
        self.trade_area_id = trade_area_id

    def insert_monopoly(self, store_id, monopoly_type_id, trade_area_id, start_date, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        self.upserted_monopolies.append(store_id)
        self.upserted_monopolies_dates.append(start_date)
        self.upserted_monopolies_trade_areas.append(trade_area_id)
        self.upserted_monopolies_types.append(monopoly_type_id)
        self.upserted_monopolies_batch_list.append(True)

        # for repository to understand logic.  this is for testing inserting and closing and insert monopolies again
        self.active_monopolies_stores[store_id] = True

    def batch_upsert_monopolies(self, trade_area_id, batch_monopolies_list):
        # this is purely for forwards compatibility, which only core uses.
        self.batch_upserted_monopolies_trade_area_id = trade_area_id
        self.batch_upserted_monopolies_list = batch_monopolies_list



    ############################################### Competitive Stores Methods ###############################################

    def get_competitive_stores(self, home_store_id, trade_area_id):
        self.home_store_id = home_store_id
        return get_mock_dictionary_value(self.competitive_stores, home_store_id, [])

    def batch_upsert_competitive_stores(self, trade_area_id, competitive_stores):
        self.batch_upserted_competitive_stores = competitive_stores
        self.batch_upserted_trade_area_id = trade_area_id

    def close_competitive_stores_by_id(self, home_store_id, away_store_id, trade_area_id, end_date):
        self.closed_stores.append(away_store_id)
        self.home_store_id = home_store_id
        self.trade_area_id = trade_area_id
        self.end_date = end_date

    def delete_from_competitive_stores(self, home_store_id, away_store_id):
        self.home_store_id = home_store_id
        self.away_store_id = away_store_id

    def get_competitive_store_by_id(self, competitive_store_id):
        pass


    ############################################### Data Check Queries #####################################################

    def get_sql_data_check_types(self):
        return self.data_check_types

    def save_data_check(self, data_check):
        self.entity_id = data_check.data_check_values[0].entity_id
        self.data_check_type_id = data_check.data_check_type_id
        self.mismatched_values = data_check.data_check_values
        self.bad_data_rows = data_check.bad_data_rows

    def execute_data_check_type_sql(self, data_check_type):
        return get_mock_dictionary_value(self.data_check_entity_ids, data_check_type)



    #################################################### Company Methods ###################################################

    def select_company_id_force_insert(self, company_name):
        if company_name in self.company_ids_per_name:
            return self.company_ids_per_name[company_name]

    def update_company_ticker(self, company_id, ticker):
        self.test_company_ticker = ticker

    def insert_source_file(self, file_path, file_created_date, file_size_in_bytes):
        pass

    def get_company_by_id(self, company_id):
        return self.companies[company_id]

    def select_sector_ids_for_company(self, company_id):
        return get_mock_dictionary_value(self.sector_ids_per_company, company_id, [])

    def close_old_companies_sectors(self, sector_ids, assumed_end_date):
        self.closed_sectors = sector_ids
        self.assumed_end_date = assumed_end_date

    def insert_company_sectors(self, sectors, company_id, assumed_start_date):
        self.test_company_sectors = sectors
        return self.test_company_sectors

    def select_all_companies(self):
        return self.all_companies


    ############################################### Competitive Companies Methods ###############################################

    def insert_company_competition(self, competitors):
        self.test_company_competitors = competitors
        self.assumed_start_date = competitors[0].start_date

    def select_all_open_competitive_companies_ids_for_company(self, company_id):
        return get_mock_dictionary_value(self.open_competitive_companies_per_company, company_id, [])

    def close_old_company_competitors(self, away_company_ids, home_company_id, assumed_end_date):
        self.closed_competitions = away_company_ids



    #################################################### Sectors Methods ###################################################

    def save_sector_name_get_id(self, sector_name):
        return get_mock_dictionary_value(self.sector_id_per_name, sector_name)



    ############################################# Logging Methods ######################################################

    def insert_logging_records(self, logging_records):
        self.logging_records = logging_records

    def select_logs_by_log_entry_type_ids(self, log_entry_type_ids):
        logs = []
        for log_entry_type_id in log_entry_type_ids:
            if log_entry_type_id in self.logs_by_log_entry_type_id:
                for log in self.logs_by_log_entry_type_id[log_entry_type_id]:
                    logs.append(log)
        return logs

    def select_function_performance(self):
        return self.function_performance_logs



    #################################################### Census Ingest Methods ###################################################

    def insert_census_data(self, census_ingest_provider, rows_per_batch, max_threads):
        self.inserted_census_data[hash(census_ingest_provider)] = census_ingest_provider.census_ingest_data

    def get_census_data_row_count(self, census_ingest_provider):
        return len(self.inserted_census_data[hash(census_ingest_provider)])

    def bulk_insert_census_data(self, census_ingest_provider, db_server, db_database, db_username, db_password):
        self.inserted_census_data[hash(census_ingest_provider)] = census_ingest_provider.census_ingest_data



    ########################################## Report Generator Queries ####################################################

    def select_row_counts_from_tables(self, tables):
        row_counts = []
        for table in tables:
            if table in self.table_row_counts:
                row_counts.append(self.table_row_counts[table])
        return row_counts

    def get_non_sql_data_check_rowcounts(self):
        return self.non_sql_data_check_rowcounts



    ########################################## MISC Queries ##############################################################

    def select_period_id_for_year_force_insert(self, year):
        return get_mock_dictionary_value(self.period_ids_per_year, year)

    def select_period_by_period_id(self, period_id):
        return self.periods[period_id]


    ############################################# Source File Methods ######################################################

    def select_source_file_by_source_file_id(self, source_file_id):
        return get_mock_dictionary_value(self.source_files, source_file_id)

    def select_source_file_record_by_source_file_record_id(self, source_file_record_id):
        return get_mock_dictionary_value(self.source_file_records, source_file_record_id)



########################################################################################################################
########################################### PostGIS Data Repository ####################################################
########################################################################################################################


class MockDataRepositorySpecializedForPostGIS(object):
    def __init__(self):
        self.upserted_away_stores_postgis = []
        self.competitive_stores_postgis = {}
        self.closed_stores_postgis = []
        self.active_monopolies_stores_postgis = {}
        self.upserted_monopolies_postgis = []
        self.upserted_monopolies_postgis_batch_list = []

    def batch_upsert_competitive_stores(self, trade_area_id, competitive_stores):
        self.batch_upserted_competitive_stores = competitive_stores
        self.batch_upserted_trade_area_id = trade_area_id

    def get_competitive_stores(self, home_store_id, trade_area_id):
        self.home_store_id = home_store_id
        return get_mock_dictionary_value(self.competitive_stores_postgis, home_store_id, [])

    def close_competitive_stores_by_id(self, home_store_id, away_store_id, trade_area_id, end_date):
        self.closed_stores_postgis.append(away_store_id)
        self.home_store_id = home_store_id
        self.trade_area_id = trade_area_id
        self.end_date = end_date

    def select_active_monopoly_record(self, store_id, trade_area_id, batch_monopolies_list):
        # batch_monopolies_list is for forward compatibility with the core data repository.  It's used for batch insert.
        return get_mock_dictionary_value(self.active_monopolies_stores_postgis, store_id)

    def insert_monopoly(self, store_id, monopoly_type_id, trade_area_id, start_date, batch_monopolies):
        self.upserted_monopolies_postgis.append(store_id)
        self.monopoly_type_id = monopoly_type_id
        self.trade_area_id = trade_area_id
        self.start_date = start_date
        self.upserted_monopolies_postgis_batch_list.append(True)

    def delete_from_monopolies(self, store_id, trade_area_id):
        self.store_id = store_id
        self.trade_area_id = trade_area_id

    def batch_upsert_monopolies(self, trade_area_id, batch_monopolies_list):
        # this is purely for forwards compatibility, which only core uses.
        self.batch_upserted_monopolies_trade_area_id = trade_area_id
        self.batch_upserted_monopolies_list = batch_monopolies_list




########################################################################################################################
############################################## Mock Row Objects ########################################################
########################################################################################################################

class MockRowCount(object):
    def __init__(self, table_name, row_count):
        self.table_name = table_name
        self.row_count = row_count

class MockLogFunctionPerformance(object):
    def __init__(self, function_name, avg_secs, count):
        self.function_name = function_name
        self.avg_secs = avg_secs
        self.count = count

class MockNonSqlDataRowCount(object):
    def __init__(self, data_check_name, count):
        self.data_check_name = data_check_name
        self.count = count




