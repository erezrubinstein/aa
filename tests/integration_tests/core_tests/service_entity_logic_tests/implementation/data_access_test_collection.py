from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection

from core.data_access.company_handler import select_company_id_force_insert

__author__ = 'jsternberg'


class CoreDataAccessTestCollection(ServiceTestCollection):

    def initialize(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##

    def __add_company(self, company_name):
        data = {"type": "retail_parent",
                "ticker": "",
                "status": "operating",
                "description": company_name,
                "exchange": "None",
                "closure_confirmation_threshold_days": 730}
        return self.mds_access.call_add_entity("company", company_name, data, self.context)

    def __delete_entity(self, entity_type, entity_id):
        return self.mds_access.call_del_entity(entity_type, entity_id)


    ##------------------------------------ Data Access Tests ---------------------------------------##

    def test_select_company_id_force_insert_basic(self):

        try:
            company_id = self.__add_company("ABC")
            found_company_id = select_company_id_force_insert("ABC")
            self.test_case.assertEqual(found_company_id, company_id)

            # check for case-insensitive search
            found_company_id = select_company_id_force_insert("abc")
            self.test_case.assertEqual(found_company_id, company_id)

        finally:
            if company_id:
                self.__delete_entity("company", company_id)

    def test_select_company_id_force_insert_containing_names(self):

        """
        See RET-997.
        This tests a situation where the name of one company is contained within another company's name.
        """

        try:
            company_id1 = self.__add_company("CASHSAVER COST PLUS FOOD OUTLET")
            company_id2 = self.__add_company("Cost Plus FOOD OUTLET")

            found_company_id1 = select_company_id_force_insert("CASHSAVER COST PLUS FOOD OUTLET")
            found_company_id2 = select_company_id_force_insert("Cost Plus FOOD OUTLET")

            self.test_case.assertEqual(found_company_id1, company_id1)
            self.test_case.assertEqual(found_company_id2, company_id2)
            self.test_case.assertNotEqual(found_company_id1, found_company_id2)

        finally:
            if company_id1:
                self.__delete_entity("company", company_id1)
            if company_id2:
                self.__delete_entity("company", company_id2)

    def test_select_company_id_force_insert_escaped_chars(self):

        """
        Test for company names with characters that need to be escaped for regex
        regex_chars_to_encode = ["(", ")", "[", "]", "+", "*", "?", "$", "^", "-"]
        Note that select_company_id_force_insert does not actually find the correct company in this case,
         because it replaces invalid regex characters with "." because of json encoding/decoding limitations.
        But it shouldn't give us an exception.
        """

        regex_chars_to_encode = ["(", ")", "[", "]", "+", "*", "?", "$", "^", "-"]
        companies = []

        try:
            for char in regex_chars_to_encode:
                company_id = self.__add_company("ABC%sDEF" % char)
                companies.append(company_id)
                found_company_id = select_company_id_force_insert("ABC%sDEF" % char)
                self.test_case.assertIn(found_company_id, companies)

        finally:
            for company_id in companies:
                if company_id:
                    self.__delete_entity("company", company_id)
