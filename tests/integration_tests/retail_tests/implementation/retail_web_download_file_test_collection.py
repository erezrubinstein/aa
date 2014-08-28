from __future__ import division
import json
import pprint
import datetime
from common.utilities.date_utilities import LAST_ANALYTICS_DATE
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from requests.cookies import RequestsCookieJar
import cStringIO
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_store, insert_test_company_competition_instance


__author__ = 'vgold'


class RetailWebDownloadFileTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "retail_web_companies_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_test_user_get_cookies()

    def setUp(self):

        self.rds_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##

    def __login_test_user_get_cookies(self):

        params = {"email": "test@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    ##------------------------------------ Retail Web Download File Tests ---------------------------------------##

    def retail_test_download_file__exists(self):

        test_file_path = "platform_research_reports"
        test_filename = "respect.txt"
        test_file_content = "Respect My Athorta!"
        test_file = cStringIO.StringIO(test_file_content)

        result = self.rds_access.call_post_file(test_file_path, {test_filename: test_file}, self.context)

        rds_file_id = result.values()[0]

        response = self.web_access.get('/api/files/download/%s' % rds_file_id, cookies=self.cooks, stream=True)
        self.test_case.assertEqual(test_file_content, response.content)

    def retail_test_download_file__unauthorized(self):

        test_file_path = "platform_research_reports"
        test_filename = "respect.txt"
        test_file_content = "Respect My Athorta!"
        test_file = cStringIO.StringIO(test_file_content)

        result = self.rds_access.call_post_file(test_file_path, {test_filename: test_file}, self.context)

        rds_file_id = result.values()[0]

        response = self.web_access.get('/api/files/download/%s' % rds_file_id, stream=True)
        self.test_case.assertIn(self.config["SECURITY_LOGIN_URL"], response.url)

    def retail_test_download_stores_export_file(self):

        cid = insert_test_company(name="COMPANY")
        insert_test_store(cid, [None, None])
        insert_test_store(cid, [None, None])
        insert_test_store(cid, [None, None])

        query_string = json.dumps({
            "company_ids": [cid],
            "grid_id": "stores",
            "show_competition": True,
            "company_name": "COMPANY",
            "date_filter": "2013-01-01",
            "stat_type": "avg"
        })

        response = self.web_access.get('/api/stores/export?params=%s' % query_string, cookies=self.cooks, stream=True)

        self.test_case.assertEqual(response.headers["content-type"], 'application/vnd.ms-excel')
        self.test_case.assertEqual(response.headers["content-disposition"],
                                   'attachment; filename="COMPANY - All Stores - As of JANUARY 2013.xls"')

        query_string = json.dumps({
            "company_ids": [cid],
            "grid_id": "stores",
            "show_competition": True,
            "company_name": "COMPANY",
            "stat_type": "avg"
        })

        response = self.web_access.get('/api/stores/export?params=%s' % query_string, cookies=self.cooks, stream=True)

        self.test_case.assertEqual(response.headers["content-type"], 'application/vnd.ms-excel')
        self.test_case.assertEqual(response.headers["content-disposition"],
                                   'attachment; filename="COMPANY - All Stores - As of ANY DATE.xls"')

        query_string = json.dumps({
            "company_ids": [cid],
            "grid_id": "opening_stores",
            "show_competition": True,
            "company_name": "COMPANY",
            "date_filter": ["2013-01-01", "2014-01-01"],
            "stat_type": "avg"
        })

        response = self.web_access.get('/api/stores/export?params=%s' % query_string, cookies=self.cooks, stream=True)

        self.test_case.assertEqual(response.headers["content-type"], 'application/vnd.ms-excel')
        self.test_case.assertEqual(response.headers["content-disposition"],
                                   'attachment; filename="COMPANY - Store Openings - Between JANUARY 2013 and JANUARY 2014.xls"')

        query_string = json.dumps({
            "company_ids": [cid],
            "grid_id": "closing_stores",
            "show_competition": True,
            "company_name": "COMPANY",
            "date_filter": ["2013-01-01", "2014-01-01"],
            "stat_type": "avg"
        })

        response = self.web_access.get('/api/stores/export?params=%s' % query_string, cookies=self.cooks, stream=True)

        self.test_case.assertEqual(response.headers["content-type"], 'application/vnd.ms-excel')
        self.test_case.assertEqual(response.headers["content-disposition"],
                                   'attachment; filename="COMPANY - Store Closings - Between JANUARY 2013 and JANUARY 2014.xls"')

    def retail_test_download_competitors_export_file(self):

        cid1 = insert_test_company(name="COMPANY 1")
        cid2 = insert_test_company(name="COMPANY 2")
        insert_test_company_competition_instance(cid1, cid2)

        query_string = json.dumps({
            "company_ids": [cid1],
            "company_name": "COMPANY 1",
            "as_of_date": LAST_ANALYTICS_DATE.isoformat()[:10],
            "last_store_date": LAST_ANALYTICS_DATE.isoformat()[:10],
            "company_status": "operating",
            "last_analytics_competition_date": LAST_ANALYTICS_DATE.isoformat()[:10]
        })

        response = self.web_access.get('/api/companies/competition/competitors/export?params=%s' % query_string, cookies=self.cooks, stream=True)

        now = datetime.datetime.utcnow()
        self.test_case.assertEqual(response.headers["content-type"], 'application/vnd.ms-excel')
        self.test_case.assertIn('attachment; filename="Competitors of COMPANY 1 - As of', response.headers["content-disposition"])





