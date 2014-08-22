import logging
import yaml
import os
from multiprocessing.synchronize import Lock
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.business_logic.enums import FailThreshold

class Config(object):

    #static instance variable
    instance = None
    singletonLock = Lock()
    
    def __init__(self, config_name = "config.yml"):

        # thread safety check
        with Config.singletonLock:
            # singleton check
            if Config.instance is None:
                # instantiate configuration object
                file_settings = self.__read_config_file(config_name)

                #################################### Loader Directory Settings #########################################
                self.loader_directory = file_settings["loader_settings"]["loader_directory"]
                self.loader_master_competition_file = file_settings["loader_settings"]["master_competition_file"]


                ####################################### Address Match Settings #########################################
                self.geocoordinate_precision_fuzzy = file_settings["address_match_settings"]["geocoordinate_precision_fuzzy"]
                self.geocoordinate_precision_not_fuzzy = file_settings["address_match_settings"]["geocoordinate_precision_not_fuzzy"]


                ############################################ Cloud Settings ############################################
                self.amazon_access_key = file_settings["cloud_settings"]["amazon_access_key"]
                self.amazon_secret_key = file_settings["cloud_settings"]["amazon_secret_key"]
                self.amazon_access_key_new = file_settings["new_cloud_settings"]["amazon_access_key"]
                self.amazon_secret_key_new = file_settings["new_cloud_settings"]["amazon_secret_key"]


                ####################################### Verify Geocode Settings ########################################
                self.run_verify_geocode = bool(file_settings["run_settings"]["run_verify_geocode"])
                self.verify_geocode_service_Google = file_settings["GIS_settings"]["Google_service"]["name"]
                self.verify_geocode_service_ESRI = file_settings["GIS_settings"]["ESRI_service"]["name"]
                self.geoprocessors = file_settings["run_settings"]["geoprocessors"]
                self.controller_inputs = file_settings["run_settings"]["controller_inputs"]
                self.verify_geocode_urls = {
                    self.verify_geocode_service_ESRI: file_settings["GIS_settings"]["ESRI_service"]["reverse_geocode_url"],
                    self.verify_geocode_service_Google: file_settings["GIS_settings"]["Google_service"]["reverse_geocode_url"]
                }
                self.geocoordinate_qualifiers = {
                    self.verify_geocode_service_ESRI: {"positive":"+", "negative":""},
                    self.verify_geocode_service_Google: {"positive":"", "negative":""}
                }
                self.fail_thresholds = {
                    self.verify_geocode_service_ESRI: FailThreshold.ReverseGeoCodeESRI,
                    self.verify_geocode_service_Google: FailThreshold.ReverseGeoCodeGoogle
                }

                ############################################ Mop Settings ##############################################
                self.trade_area_thresholds_for_reprocess = [TradeAreaThreshold.DistanceMiles10, TradeAreaThreshold.DriveTimeMinutes10]
                self.wkid = file_settings["GIS_settings"]["wkid"]
                self.geodetic_network_datum = file_settings["GIS_settings"]["geodetic_network_datum"]


                ########################################## ArcGIS Settings #############################################
                self.dataset_id = file_settings["GIS_settings"]["demographics_dataset"]
                self.dataset_year = file_settings["GIS_settings"]["dataset_year"]
                self.ArcGIS_server_ips = file_settings["GIS_settings"]["ArcGIS_servers"]
                self.ArcGIS_timeout = file_settings["GIS_settings"]["timeout_seconds"]
                self.ArcGIS_max_errors = file_settings["GIS_settings"]["max_errors"]
                self.ArcGIS_max_timeouts = file_settings["GIS_settings"]["max_timeouts"]
                self.ArcGIS_remove_server_after_max_timeouts = file_settings["GIS_settings"].get("remove_server_after_max_timeouts", False)

                # GP1
                self.gp1_templates = file_settings["GIS_settings"]["gp1_templates"]
                self.gp1_drive_time_url = file_settings["GIS_settings"]["trade_area_drive_time"]
                self.gp1_simple_rings_url = file_settings["GIS_settings"]["trade_area_simple_rings"]
                self.gp1_drive_time_radius = 10
                self.gp1_drive_time_distance_units = "esriDriveTimeUnitsMinutes"
                self.gp1_simple_rings_radius = 10
                self.gp1_simple_rings_distance_units = "esriMiles"

                #GP2
                self.gp2_template = "LocatorP"
                self.gp2_url = file_settings["GIS_settings"]["locator_report"]
                self.gp2_radius = 10

                #GP5
                self.network_analyst_route_solver_url = file_settings["GIS_settings"]["network_analyst_route_solver"]

                #GP11
                self.grid_url = file_settings["GIS_settings"]["grid"]
                self.grid_threshold = file_settings["run_settings"]["white_space_grid_threshold"]
                self.grid_size = file_settings["run_settings"]["white_space_grid_size"]

                #GP12
                self.give_shape_get_demographics_url = file_settings["GIS_settings"]["give_shape_get_demographics"]

                #GP18
                self.customer_derived_url = file_settings["GIS_settings"]["customer_derived"]

                #GP19
                self.upload_feature_set_url = file_settings["GIS_settings"]["upload_feature_set"]

                # Repository settings
                self.retailer_workspace = file_settings["GIS_settings"]["retailer_workspace"]
                self.store_customer_project = file_settings["GIS_settings"]["store_customer_project"]

                ######################################## BA Online Settings ############################################
                self.ba_online_templates = file_settings["ba_online_settings"]["gp6_templates"]
                self.ba_online_username = file_settings["ba_online_settings"]["username"]
                self.ba_online_password = file_settings["ba_online_settings"]["password"]
                self.ba_online_simple_rings_url = file_settings["ba_online_settings"]["simple_rings_url"]
                self.ba_online_drive_time_url = file_settings["ba_online_settings"]["drive_time_url"]
                self.ba_online_summary_reports_url = file_settings["ba_online_settings"]["summary_reports_url"]


                ######################################### postgis Settings #############################################
                self.postgis_server = file_settings["postgis_settings"]["server"]
                self.postgis_database = file_settings["postgis_settings"]["database"]
                self.postgis_username = file_settings["postgis_settings"]["username"]
                self.postgis_password = file_settings["postgis_settings"]["password"]


                ######################################### Database Settings ############################################
                self.odbc_driver = file_settings["db_settings"]["odbc_driver"]
                self.odbc_backup_driver = file_settings["db_settings"]["odbc_backup_driver"]
                self.connection_timeout = file_settings["db_settings"]["connection_timeout"]
                # default db
                self.db_server = file_settings["db_settings"]["default_db"]["server"]
                self.db_database = file_settings["db_settings"]["default_db"]["database"]
                self.db_username = file_settings["db_settings"]["default_db"]["username"]
                self.db_password = file_settings["db_settings"]["default_db"]["password"]
                # default db
                self.logging_db_server = file_settings["db_settings"]["logging_db"]["server"]
                self.logging_db_database = file_settings["db_settings"]["logging_db"]["database"]
                self.logging_db_username = file_settings["db_settings"]["logging_db"]["username"]
                self.logging_db_password = file_settings["db_settings"]["logging_db"]["password"]
                # build_db
                self.build_without_confirmation = file_settings["db_settings"]["build_db"]["build_without_confirmation"]
                self.build_db_server = file_settings["db_settings"]["build_db"]["server"]
                self.build_db_database = file_settings["db_settings"]["build_db"]["database"]
                self.build_db_username = file_settings["db_settings"]["build_db"]["username"]
                self.build_db_password = file_settings["db_settings"]["build_db"]["password"]
                self.build_db_target_database = file_settings["db_settings"]["build_db"]["target_database"]
                self.build_db_target_database_logging = file_settings["db_settings"]["build_db"]["target_database_logging"]
                self.build_db_target_database_username = file_settings["db_settings"]["build_db"]["target_database_username"]
                self.build_db_target_database_password = file_settings["db_settings"]["build_db"]["target_database_password"]
                self.build_db_bulk_operations_username = file_settings["db_settings"]["build_db"]["bulk_operations_username"]
                self.build_db_bulk_operations_password = file_settings["db_settings"]["build_db"]["bulk_operations_password"]
                self.build_db_data_checks_username = file_settings["db_settings"]["build_db"]["data_checks_username"]
                self.build_db_data_checks_password = file_settings["db_settings"]["build_db"]["data_checks_password"]
                self.build_db_target_database_directory = file_settings["db_settings"]["build_db"]["target_database_directory"]
                self.build_db_old_dbs_to_keep = file_settings["db_settings"]["build_db"]["old_dbs_to_keep"]
                # bad_data_integration_test_db
                self.bad_data_integration_test_db_server = file_settings["db_settings"]["bad_data_integration_test_db"]["server"]
                self.bad_data_integration_test_db_database = file_settings["db_settings"]["bad_data_integration_test_db"]["database"]
                self.bad_data_integration_test_db_username = file_settings["db_settings"]["bad_data_integration_test_db"]["username"]
                self.bad_data_integration_test_db_password = file_settings["db_settings"]["bad_data_integration_test_db"]["password"]


                ########################################### App Settings ############################################
                self.app_version = file_settings["app_settings"]["version"]
                self.environment = file_settings["app_settings"]["environment"]
                self.partition_size = file_settings["run_settings"]["partition_size"]
                self.max_processes = file_settings["run_settings"]["max_processes"]
                self.trade_area_thresholds = file_settings["run_settings"]["trade_area_thresholds"]


                ########################################## Logging Settings #########################################
                # global settings
                self.logging_level = getattr(logging, file_settings["logging_settings"]["logging_level"])
                # Console handler settings
                self.console_logging_level = getattr(logging, file_settings["logging_settings"]["console_handler_settings"]["logging_level"])
                # file handler settings
                self.file_logging_level = getattr(logging, file_settings["logging_settings"]["file_handler_settings"]["logging_level"])
                # SQL handler settings
                self.sql_logging_level = getattr(logging, file_settings["logging_settings"]["sql_handler_settings"]["logging_level"])
                self.sql_logging_insert_timer = int(file_settings["logging_settings"]["sql_handler_settings"]["sql_logging_insert_timer"])

                if "mongodb_handler_settings" in file_settings["logging_settings"]:
                    self.mongodb_logging_level =  getattr(logging, file_settings["logging_settings"]["mongodb_handler_settings"]["logging_level"])
                    self.mongodb_logging_host =  file_settings["logging_settings"]["mongodb_handler_settings"]["host"]
                    self.mongodb_logging_port =  file_settings["logging_settings"]["mongodb_handler_settings"]["port"]
                    self.mongodb_logging_db =  file_settings["logging_settings"]["mongodb_handler_settings"]["db"]
                    self.mongodb_logging_collection =  file_settings["logging_settings"]["mongodb_handler_settings"]["collection"]

                ####################################### Report Generator Settings ######################################
                self.report_generator_table_names = file_settings["report_generator"]["table_names"]
                self.report_generator_num_bad_data_rows_to_display = file_settings["report_generator"]["num_bad_data_rows_to_display"]
                self.report_generator_daily_build_report_directory = file_settings["report_generator"]["daily_build_report_directory"]
                self.report_generator_email_recipients_developers = file_settings["report_generator"]["email_recipients_developers"]
                self.report_generator_email_recipients_others = file_settings["report_generator"]["email_recipients_others"]
                self.report_generator_s3_report_directory = file_settings["report_generator"]["s3_report_directory"]
                self.report_generator_s3_http_report_directory = file_settings["report_generator"]["s3_http_report_directory"]


                ############################################ Email Settings ############################################
                self.email_settings_smtp_server = file_settings["email_settings"]["smtp_server"]
                self.email_settings_username = file_settings["email_settings"]["username"]
                self.email_settings_password = file_settings["email_settings"]["password"]
                self.email_settings_from_email = file_settings["email_settings"]["from_email"]
                self.census_ingest_year = file_settings["census_ingest"]["census_year"]
                self.census_ingest_files_list = file_settings["census_ingest"]["census_ingest_files"]


                ############################################ Deploy Settings ###########################################
                self.deploy_settings_local_signal_directory = file_settings["deploy_settings"]["local_signal_directory"]
                self.deploy_settings_local_deploy_directory = file_settings["deploy_settings"]["local_deploy_directory"]
                self.deploy_settings_local_code_directory = file_settings["deploy_settings"]["local_code_directory"]
                self.deploy_settings_local_loader_files_directory = file_settings["deploy_settings"]["local_loader_files_directory"]
                self.deploy_settings_local_census_data_directory = file_settings["deploy_settings"]["local_census_data_directory"]
                self.deploy_settings_local_dot_git_directory = file_settings["deploy_settings"]["local_dot_git_directory"]
                self.deploy_settings_local_python_directory = file_settings["deploy_settings"]["local_python_directory"]
                self.deploy_settings_local_geoprocessing_directory = file_settings["deploy_settings"]["local_geoprocessing_directory"]
                self.deploy_settings_local_unit_tests_directory = file_settings["deploy_settings"]["local_unit_tests_directory"]
                self.deploy_settings_local_integration_tests_directory = file_settings["deploy_settings"]["local_integration_tests_directory"]
                self.deploy_settings_local_loader_file_next_run_directory = file_settings["deploy_settings"]["local_loader_file_next_run_directory"]
                self.deploy_ssh_key_path = file_settings["deploy_settings"].get("ssh_key_path", None)
                self.deploy_amazon_region = file_settings["deploy_settings"].get("amazon_region", None)
                self.deploy_settings_local_root_directory = file_settings["deploy_settings"]["local_root_directory"]


                ############################################ Custom Analytics Settings ###########################################
                self.custom_analytics_run_id = file_settings["run_settings"].get("ca_run_id", "Internal")
                self.custom_analytics_report_name = file_settings["run_settings"].get("report_name", "Internal")
                self.custom_analytics_client_name = file_settings["run_settings"].get("client_name", "Internal")
                self.custom_analytics_client_email = file_settings["run_settings"].get("client_email", "engineering@signaldataco.com")
                self.custom_analytics_company_settings = file_settings["run_settings"].get("company_settings", None)
                self.custom_analytics_time_periods = file_settings["run_settings"].get("time_periods", [])
                self.custom_analytics_core_url = file_settings["run_settings"].get("core_url", [])
                self.custom_analytics_core_login = file_settings["run_settings"].get("core_login", [])
                self.custom_analytics_core_password = file_settings["run_settings"].get("core_password", [])
                self.custom_analytics_retail_url = file_settings["run_settings"].get("retail_url", [])
                self.custom_analytics_retail_login = file_settings["run_settings"].get("retail_login", [])
                self.custom_analytics_retail_password = file_settings["run_settings"].get("retail_password", [])
                self.retail_mongo_db = file_settings["db_settings"].get("retail_mongo_db", {})
                self.custom_analytics_run_comp_stores_report = file_settings["run_settings"].get("run_comp_stores_report", False)
                self.custom_analytics_comp_stores_periods = file_settings["run_settings"].get("comp_stores_periods", [])

                # instantiate singleton
                Config.instance = self
    
    def __read_config_file(self, config_name):
        config_path = os.path.dirname(__file__) + "/../" + config_name
        with open(config_path) as file:
            return yaml.load(file)

    def reload_from_different_file(self, config_name):

        # reset singleton
        Config.instance = None

        # call again to create singleton with new config
        return Config(config_name).instance


    def update_config_file_with_new_GIS_servers(self, new_server_ips):
        # read data
        config_path = os.path.dirname(__file__) + "/../config.yml"
        with open(config_path) as file:
            # read file
            data = yaml.load(file)

        # save file back with updated ips
        with open(config_path, "w+") as file:
            data["GIS_settings"]["ArcGIS_servers"] = new_server_ips
            yaml.dump(data, file, default_flow_style = False)


    def update_config_with_custom_analytics_settings(self, ca_run_id, demographic_template, trade_areas, target_db, target_db_logging, report_name,
                                                     client_name, client_email, company_settings, time_periods, run_comp_stores_report, comp_stores_periods):

        # get the file path
        config_path = os.path.dirname(__file__) + "/../config.yml"

        # read the file into a dictionary
        with open(config_path) as file:
            data = yaml.load(file)

        # update the data
        data["GIS_settings"]["gp1_templates"] = [demographic_template]
        data["run_settings"]["trade_area_thresholds"] = trade_areas
        data["run_settings"]["ca_run_id"] = ca_run_id
        data["run_settings"]["report_name"] = report_name
        data["run_settings"]["client_name"] = client_name
        data["run_settings"]["client_email"] = client_email
        data["run_settings"]["company_settings"] = company_settings
        data["run_settings"]["time_periods"] = time_periods
        data["run_settings"]["run_comp_stores_report"] = run_comp_stores_report
        data["run_settings"]["comp_stores_periods"] = comp_stores_periods
        data["db_settings"]["default_db"]["database"] = target_db
        data["db_settings"]["logging_db"]["database"] = target_db_logging
        data["db_settings"]["build_db"]["target_database"] = target_db
        data["db_settings"]["build_db"]["target_database_logging"] = target_db_logging
        data["db_settings"]["bad_data_integration_test_db"]["database"] = target_db

        # save file back with updated ips
        with open(config_path, "w+") as file:
            yaml.dump(data, file, default_flow_style = False)

        # reset the config
        Config.instance = None
        config = Config().instance

        # reset the dependency
        dependencies.register_dependency("Config", config)

        # return the config
        return config