from __future__ import division
from tests.integration_tests.core_tests.web_tests.implementation.core_web_industry_competition_links_test_collection import CoreWebIndustryCompetitionLinksTestCollection
from tests.integration_tests.core_tests.web_tests.implementation.core_web_workflow_validation_test_collection import CoreWebWorkflowValidationTestCollection
from tests.integration_tests.core_tests.web_tests.implementation.core_web_user_admin_test_collection import CoreWebUserAdminTestCollection
from tests.integration_tests.core_tests.web_tests.implementation.core_web_company_test_collection import CoreWebCompanyTestCollection
from tests.integration_tests.core_tests.web_tests.implementation.core_web_stores_test_collection import CoreWebStoresTestCollection
from tests.integration_tests.core_tests.web_tests.implementation.core_web_export_test_collection import CoreWebExportTestCollection
from tests.integration_tests.core_tests.web_tests.implementation.core_web_file_test_collection import CoreWebFileTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_raw_data_storage.rds_api import app as rds_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from core.service.svc_main.main_api import app as main_app
from core.web.run_core_web import app as web_app
import unittest


__author__ = 'vgold'


class CoreWebExportTests(ServiceTestCase):
    """
    Test case for Core Web Company Page endpoints.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {"CORE_WEB": web_app, "MAIN": main_app, "RDS": rds_app, "MDS": mds_app, "WFS": wfs_app}
        cls.svc_key = "CORE_WEB"
        cls.test_colls = {
            "CORE_WEB_EXPORT": CoreWebExportTestCollection,
            "CORE_WEB_STORES": CoreWebStoresTestCollection,
            "CORE_WEB_USER_ADMIN": CoreWebUserAdminTestCollection,
            "CORE_WEB_COMPANY": CoreWebCompanyTestCollection,
            "CORE_WEB_INDUSTRY_COMPETITION": CoreWebIndustryCompetitionLinksTestCollection,
            "CORE_WEB_FILE": CoreWebFileTestCollection,
            "CORE_WEB_WORKFLOW_VALIDATION": CoreWebWorkflowValidationTestCollection
        }
        cls.svc_main_exempt = {}

    ##------------------------------------ Tests ------------------------------------------------##

    def test_web_test_get_export_companies_content(self):
        self.tests["CORE_WEB_EXPORT"].web_test_get_export_companies_content()

    def test_web_test_get_export_companies_csv(self):
        self.tests["CORE_WEB_EXPORT"].web_test_get_export_companies_csv()

    def test_web_test_delete_orphaned_store(self):
        self.tests["CORE_WEB_STORES"].web_test_delete_orphaned_store()

    def test_get_default_users(self):
        self.tests["CORE_WEB_USER_ADMIN"].test_get_default_users()

    def test_create_user_and_login(self):
        self.tests["CORE_WEB_USER_ADMIN"].test_create_user_and_login()

    def test_company_typeahead_empty(self):
        self.tests["CORE_WEB_COMPANY"].test_company_typeahead_empty()

    def test_company_typeahead_one_company(self):
        self.tests["CORE_WEB_COMPANY"].test_company_typeahead_one_company()

    def test_company_typeahead_multiple_companies(self):
        self.tests["CORE_WEB_COMPANY"].test_company_typeahead_multiple_companies()

    def test_company_typeahead_multiple_companies_with_delete(self):
        self.tests["CORE_WEB_COMPANY"].test_company_typeahead_multiple_companies_with_delete()

    def test_view_edit_company_page(self):
        self.tests["CORE_WEB_COMPANY"].test_view_edit_company_page()

    def test_web_test_create_delete_industry_competition_links(self):
        self.tests["CORE_WEB_INDUSTRY_COMPETITION"].web_test_create_delete_industry_competition_links()

    def test_core_web_test_upload_platform_research_report(self):
        self.tests["CORE_WEB_FILE"].core_web_test_upload_platform_research_report()

    def test_core_web_test_update_company_research_links(self):
        self.tests["CORE_WEB_FILE"].core_web_test_update_company_research_links()

    def test_core_web_test_update_company_research_links__moves_file(self):
        self.tests["CORE_WEB_FILE"].core_web_test_update_company_research_links__moves_file()

    def test_web_test_get_tasks_by_status(self):
        self.tests["CORE_WEB_WORKFLOW_VALIDATION"].web_test_get_tasks_by_status()

    def test_web_test_unlock_task(self):
        self.tests["CORE_WEB_WORKFLOW_VALIDATION"].web_test_unlock_task()


if __name__ == '__main__':
    unittest.main()
