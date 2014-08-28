from __future__ import division
from tests.integration_tests.core_tests.service_tests.implementation.wfs_company_analytics_calculations_data_test_collection import WFSCompanyAnalyticsCalculationsDataTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_industry_competition_pairs_updater_test_collection import WFSIndustryCompetitionInstanceUpdaterTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_company_competition_pairs_updater_test_collection import WFSCompanyCompetitionInstanceUpdaterTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_company_analytics_calculations_test_collection import WFSCompanyAnalyticsCalculationsTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_geoprocessing_rules_evaluator_test_collection import WFSGeoprocessingRulesEvaluatorTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_national_labor_calculator_test_collection import WFSNationalLaborCalculatorTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_cleanup_tasks_test_collection import WFSCleanupTasksTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_retailer_test_collection import WFSRetailerTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_white_space_analytics_test_collection import WFSWhiteSpaceAnalyticsTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_company_name_change_test_collection import WFSCompanyNameChangeTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_churn_validation_test_collection import WFSChurnValidationTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_analytics_plan_b_test_collection import WFSAnalyticsPlanBTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_stale_analytics_test_collection import WFSStaleAnalyticsTestCollection
from tests.integration_tests.core_tests.service_tests.implementation.wfs_test_collection import WFSTestCollection
from core.service.svc_entity_matcher.entity_matcher_api import app as entity_matcher_app
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_raw_data_storage.rds_api import app as rds_app
from core.service.svc_analytics.analytics_api import app as analytics_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from core.service.svc_main.main_api import app as main_app
import unittest


__author__ = "jsternberg"


class Test_WFS_API(ServiceTestCase):
    """
    Test case for Workflow Service.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {
            "MAIN": main_app,
            "MDS": mds_app,
            "RDS": rds_app,
            "WFS": wfs_app,
            "ENTITY_MATCHER": entity_matcher_app,
            "ANALYTICS": analytics_app
        }
        cls.svc_key = "WFS"
        cls.test_colls = {
            "WFS": WFSTestCollection,
            "WFS_CHURN_VALIDATION": WFSChurnValidationTestCollection,
            "WFSGeoprocessingRulesEvaluatorTestCollection": WFSGeoprocessingRulesEvaluatorTestCollection,
            "WFS_COMPANY_NAME_CHANGE": WFSCompanyNameChangeTestCollection,
            "WFS_COMPANY_COMPETITION_INSTANCE_UPDATER": WFSCompanyCompetitionInstanceUpdaterTestCollection,
            "WFS_INDUSTRY_COMPETITION_INSTANCE_UPDATER": WFSIndustryCompetitionInstanceUpdaterTestCollection,
            "WFS_COMPANY_ANALYTICS_CALCULATIONS": WFSCompanyAnalyticsCalculationsTestCollection,
            "WFS_COMPANY_ANALYTICS_DATA_CALCULATIONS": WFSCompanyAnalyticsCalculationsDataTestCollection,
            "WFS_WHITE_SPACE_ANALYTICS": WFSWhiteSpaceAnalyticsTestCollection,
            "WFS_CLEANUPS": WFSCleanupTasksTestCollection,
            "WFS_NATIONAL_LABOR_CALC": WFSNationalLaborCalculatorTestCollection,
            "WFS_ANALYTICS_PLAN_B": WFSAnalyticsPlanBTestCollection,
            "WFS_STALE_ANALYTICS": WFSStaleAnalyticsTestCollection,
            "WFS_RETAILER": WFSRetailerTestCollection
        }

##############################################################################################################
##
## Test methods must adhere to a strict naming convention:
##   1)  Name of test method must have "test_" prepended to the actual name of the test method
##       from the test collection.
##
##   2)  The actual test that should run must be called from within the test method (obviously).
##
##   3)  The actual test's name must start with its lowercase service key and an underscore ("mds_",
##       "main_", "rds_", "wfs_", etc.).
##
##   **  NOTE: The values of these test methods are dynamically overwritten to execute the setUp and
##       tearDown methods from the test's collection before and after the actual test specified. This
##       was a design decision, because the test collection should know how to set up and tear down
##       each test it houses.
##
##############################################################################################################

    def test_wfs_test_reference_data_workflow_statuses(self):
        self.tests["WFS"].wfs_test_reference_data_workflow_statuses()

    def test_wfs_test_retail_input_record_summary_collections(self):
        self.tests["WFS"].wfs_test_retail_input_record_summary_collections()

    def test_wfs_test_find_manual_tasks(self):
        self.tests["WFS"].wfs_test_find_manual_tasks()

    def test_wfs_test_task_group_deletion(self):
        self.tests["WFS"].wfs_test_task_group_deletion()

    def test_wfs_test_task_deletion(self):
        self.tests["WFS"].async_mode = False
        self.tests["WFS"].wfs_test_task_deletion()

    def test_wfs_test_add_empty_task_raises_error(self):
        self.tests["WFS"].wfs_test_add_empty_task_raises_error()

    def test_wfs_test_retail_input_file_deletion_task(self):
        self.tests['WFS'].wfs_test_retail_input_file_deletion_task()

    def test_wfs_test_retail_input_file_deletion_task__deletes_qc_tasks(self):
        self.tests['WFS'].wfs_test_retail_input_file_deletion_task__deletes_qc_tasks()

    #
    # RET-1579 - Commented out until that bug is fixed
    #
    # def test_wfs_test_file_deletion_does_not_delete_stores_before_last_rirs(self):
    #     self.tests['WFS'].wfs_test_file_deletion_does_not_delete_stores_before_last_rirs()

    def test_wfs_test_company_deletion(self):
        self.tests['WFS'].test_wfs_test_company_deletion()

    def test_wfs_test_update_task_group(self):
        self.tests['WFS'].test_wfs_test_update_task_group()

    def test_wfs_test_retail_input_file_loader(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_file_loader()

    def test_wfs_test_retail_input_file_loader__auto_create_stores_first_time_only(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_file_loader__auto_create_stores_first_time_only()

    def test_wfs_test_retail_input_record_churn_matching_jcrew_full_line(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_matching_jcrew_full_line()

    def test_wfs_test_retail_input_record_churn_matching__exact_match_closed_store_no_auto_link(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_matching__exact_match_closed_store_no_auto_link()

    def test_wfs_test_retail_input_record_churn_validation_link_target(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_link_target()

    def test_wfs_test_retail_input_record_churn_validation_link_target_store_update(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_link_target_store_update()

    def test_wfs_test_retail_input_record_churn_validation_link_existing(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_link_existing()

    def test_wfs_test_retail_input_record_churn_validation_link_relocation(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_link_relocation()

    def test_wfs_test_retail_input_record_churn_validation_no_link_open(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_no_link_open()

    def test_wfs_test_retail_input_record_churn_validation_complete_before_getting_next(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_complete_before_getting_next()

    def test_wfs_test_retail_input_record_churn_validation_user_tries_to_get_validated_task(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_user_tries_to_get_validated_task()

    def test_wfs_test_retail_input_record_churn_validation_dupe_avoided_jit_entity_matching(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_dupe_avoided_jit_entity_matching()

    def test_wfs_test_retail_input_record_churn_validation_dupe_race_condition(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_churn_validation_dupe_race_condition()

    def test_wfs_test_retail_input_record_closed_store_validation__close_store(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_closed_store_validation__close_store()

    def test_wfs_test_retail_input_record_closed_store_validation__keep_store_open(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_record_closed_store_validation__keep_store_open()

    def test_wfs_test_retail_input_create_qc_task(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_retail_input_create_qc_task()

    def test_wfs_test_churn_validation_task_deletion(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_churn_validation_task_deletion()

    def test_wfs_test_churn_completion_fixer(self):
        self.tests["WFS_CHURN_VALIDATION"].wfs_test_churn_completion_fixer()

    def test_EVALUATE_failed_last_geoprocessing_event(self):
        self.tests['WFSGeoprocessingRulesEvaluatorTestCollection'].test_EVALUATE_failed_last_geoprocessing_event()

    def test_EVALUATE_has_most_correct_link__never_geoprocessed__check_flags(self):
        self.tests['WFSGeoprocessingRulesEvaluatorTestCollection'].test_EVALUATE_has_most_correct_link__never_geoprocessed__check_flags()

    def test_EVALUATE_is_published__check_flags(self):
        self.tests['WFSGeoprocessingRulesEvaluatorTestCollection'].test_EVALUATE_is_published__check_flags()

    def test_EVALUATE_industry_competition_changed__deleted(self):
        self.tests['WFSGeoprocessingRulesEvaluatorTestCollection'].test_EVALUATE_industry_competition_changed__deleted()

    def test_EVALUATE_industry_competition_changed__created(self):
        self.tests['WFSGeoprocessingRulesEvaluatorTestCollection'].test_EVALUATE_industry_competition_changed__created()

    def test_complete_company_name_change(self):
        self.tests['WFS_COMPANY_NAME_CHANGE'].test_complete_company_name_change()

    def test_test_company_competition_instance_updater__create(self):
        self.tests['WFS_COMPANY_COMPETITION_INSTANCE_UPDATER'].test_company_competition_pairs_updater__create()

    def test_test_company_competition_instance_updater__create_twice_no_dupes(self):
        self.tests['WFS_COMPANY_COMPETITION_INSTANCE_UPDATER'].test_company_competition_pairs_updater__create_twice_no_dupes()

    def test_test_company_competition_instance_updater__delete(self):
        self.tests['WFS_COMPANY_COMPETITION_INSTANCE_UPDATER'].test_company_competition_pairs_updater__delete()

    def test_test_company_competition_instance_updater__change_industry(self):
        self.tests['WFS_COMPANY_COMPETITION_INSTANCE_UPDATER'].test_company_competition_pairs_updater__change_industry()

    def test_test_company_competition_instance_updater__change_industry_competition_weights(self):
        self.tests['WFS_COMPANY_COMPETITION_INSTANCE_UPDATER'].test_company_competition_pairs_updater__change_industry_competition_weights()

    def test_test_industry_competition_pairs_updater__run_industry_search_industries(self):
        self.tests['WFS_INDUSTRY_COMPETITION_INSTANCE_UPDATER'].test_industry_competition_pairs_updater__run_industry_search_industries()

    def test_test_industry_competition_pairs_updater__run_industry_specified_industry(self):
        self.tests['WFS_INDUSTRY_COMPETITION_INSTANCE_UPDATER'].test_industry_competition_pairs_updater__run_industry_specified_industry()

    def test_test_industry_competition_pairs_updater__add_competition(self):
        self.tests['WFS_INDUSTRY_COMPETITION_INSTANCE_UPDATER'].test_industry_competition_pairs_updater__add_competition()

    def test_test_industry_competition_pairs_updater__delete_competition(self):
        self.tests['WFS_INDUSTRY_COMPETITION_INSTANCE_UPDATER'].test_industry_competition_pairs_updater__delete_competition()

    def test_wfs_test_company_analytics_task_and_store_quality_data(self):
        self.tests['WFS_COMPANY_ANALYTICS_CALCULATIONS'].wfs_test_company_analytics_task_and_store_quality_data()

    def test_wfs_test_company_analytics_task__trade_area_store_level_default_calcs(self):
        self.tests['WFS_COMPANY_ANALYTICS_DATA_CALCULATIONS'].wfs_test_company_analytics_task__trade_area_store_level_default_calcs()

    def test_analytics_run__0_weights(self):
        self.tests["WFS_COMPANY_ANALYTICS_CALCULATIONS"].test_analytics_run__0_weights()

    def test_test_wfs_archive_task(self):
        self.tests["WFS"].test_wfs_archive_task()

    def test_white_space_grid_analytics(self):
        self.tests["WFS_WHITE_SPACE_ANALYTICS"].test_white_space_grid_analytics()

    def test_orphan_task_fixer(self):
        self.tests["WFS_CLEANUPS"].test_orphan_task_fixer()

    def test_most_correct_rir_fixer(self):
        self.tests["WFS_CLEANUPS"].test_most_correct_rir_fixer()

    def test_orphan_cci_fixer(self):
        self.tests["WFS_CLEANUPS"].test_orphan_cci_fixer()

    def test_national_labor_calculator(self):
        self.tests["WFS_NATIONAL_LABOR_CALC"].wfs_test_national_labor_calculator()

    def test_company_analytics_plan_b_runner(self):
        self.tests["WFS_ANALYTICS_PLAN_B"].wfs_test_company_analytics_plan_b_runner()

    def test_stale_company_analytics_runner(self):
        self.tests["WFS_STALE_ANALYTICS"].wfs_test_stale_company_analytics_runner()

    def test_retailer_entity_dupe_checker(self):
        self.tests["WFS_RETAILER"].test_retailer_entity_dupe_checker()


if __name__ == '__main__':
    unittest.main()
