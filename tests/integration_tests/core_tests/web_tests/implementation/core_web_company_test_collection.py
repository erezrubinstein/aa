from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from requests.cookies import RequestsCookieJar


__author__ = 'jsternberg'


###################################################################################################


class CoreWebCompanyTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "core_tests.web_tests.test_company_page_endpoints.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_test_user_get_cookies()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##

    def __login_test_user_get_cookies(self):

        params = {"email": "test@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    def __add_company(self, company_name):
        data = {"type": "retail_parent",
                "ticker": "",
                "status": "operating",
                "description": company_name,
                "exchange": "None",
                "closure_confirmation_threshold_days": 270}
        return self.mds_access.call_add_entity("company", company_name, data, self.context)

    def __add_industry(self, industry_name):
        data = {"industry_name": industry_name}
        return self.mds_access.call_add_entity("industry", industry_name, data, self.context)

    def __delete_entity(self, entity_type, entity_id):
        return self.mds_access.call_del_entity(entity_type, entity_id)

    ##------------------------------------ Typeahead Tests ---------------------------------------##

    def test_company_typeahead_empty(self):

        response = self.web_access.get("/api/companies", cookies=self.cooks)
        self.test_case.assert200(response)
        self.test_case.assertIsNotNone(response.json())
        companies = response.json()
        self.test_case.assertEqual(companies, [])


    def test_company_typeahead_one_company(self):

        company_id = self.__add_company("Vandelay Industries")

        expected_company_rec = {
            u'data': {
                u'status': u'operating',
                u'type': u'retail_parent'
            },
            u'_id': company_id,
            u'name': u'Vandelay Industries'
        }

        response = self.web_access.get("/api/companies", cookies=self.cooks)
        self.test_case.assert200(response)
        self.test_case.assertIsNotNone(response.json())
        companies = response.json()
        self.test_case.assertEqual(companies, [expected_company_rec])

        try:
            self.__delete_entity("company", company_id)
        except:
            pass


    def test_company_typeahead_multiple_companies(self):

        company_id1 = self.__add_company("Vandelay Industries 1")
        company_id2 = self.__add_company("Vandelay Industries 2")

        expected_company_list = [
            {
                u'data': {
                    u'status': u'operating',
                    u'type': u'retail_parent'
                },
                u'_id': company_id1,
                u'name': u'Vandelay Industries 1',

            },
            {
                u'data': {
                    u'status': u'operating',
                    u'type': u'retail_parent'
                },
                u'_id': company_id2,
                u'name': u'Vandelay Industries 2',
            }
        ]

        response = self.web_access.get("/api/companies", cookies=self.cooks)
        self.test_case.assert200(response)
        self.test_case.assertIsNotNone(response.json())
        companies = response.json()
        self.test_case.assertEqual(companies, expected_company_list)

        try:
            self.__delete_entity("company", company_id1)
            self.__delete_entity("company", company_id2)
        except:
            pass

    def test_company_typeahead_multiple_companies_with_delete(self):

        company_id1 = self.__add_company("Vandelay Industries 1")
        company_id2 = self.__add_company("Vandelay Industries 2")

        expected_company_list = [
            {
                u'data': {
                    u'status': u'operating',
                    u'type': u'retail_parent'
                },
                u'_id': company_id1,
                u'name': u'Vandelay Industries 1'
            },
            {
                u'data': {
                    u'status': u'operating',
                    u'type': u'retail_parent'
                },
                u'_id': company_id2,
                u'name': u'Vandelay Industries 2'
            }
        ]

        response = self.web_access.get("/api/companies", cookies=self.cooks)
        self.test_case.assert200(response)
        self.test_case.assertIsNotNone(response.json())
        companies = response.json()
        self.test_case.assertEqual(companies, expected_company_list)

        # delete 2nd company
        self.__delete_entity("company", company_id2)
        expected_company_list.pop(1)

        response = self.web_access.get("/api/companies", cookies=self.cooks)
        self.test_case.assert200(response)
        self.test_case.assertIsNotNone(response.json())
        companies = response.json()
        self.test_case.assertEqual(companies, expected_company_list)

        try:
            self.__delete_entity("company", company_id1)
        except:
            pass

    ##------------------------------------ HTML Tests ---------------------------------------------##

    def test_view_edit_company_page(self):

        company_id = self.__add_company("Vandelay Industries")

        # need to have at least 1 industry for the page to work
        industry_id = self.__add_industry("Architecture")

        response = self.web_access.get("/company/%s" % company_id, cookies=self.cooks)

        self.test_case.assert200(response)
        self.test_case.assertEqual(response.headers["content-type"], "text/html; charset=utf-8")
        self.test_case.assertGreater(len(response.content), 1000)

        # make sure company name text input is in there
        self.test_case.assertRegexpMatches(response.content, r"input id=\"txt_company_name\"[^>]*value=\"Vandelay Industries\"")

        # make sure company name text input is in there
        self.test_case.assertIn('<option value="retail_parent" selected="selected">', response.content)

        try:
            self.__delete_entity("company", company_id)
            self.__delete_entity("industry", industry_id)
        except:
            pass
