from __future__ import division
from core.common.utilities.helpers import ensure_id
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from requests.cookies import RequestsCookieJar
import json
import os


__author__ = 'vgold'


class CoreWebFileTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "core_web_file_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}
        self.cooks = self.__login_test_user_get_cookies()

        self.main_params = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        self.mds_access.call_delete_reset_database()
        self.rds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------ Private Methods --------------------------------------##

    def __login_test_user_get_cookies(self):

        params = {"email": "test@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    ##------------------------------------ User Admin Tests ---------------------------------------##

    def core_web_test_upload_platform_research_report(self):

        cids = [
            insert_test_company(name="C1"),
            insert_test_company(name="C2")
        ]

        response = self.__upload_platform_research_pdf(cids)
        file_id = response["mds_file_ids"].values()[0]

        self.test_case.assertEqual(response["message"], "File upload successful.")
        self.test_case.assertEqual(response["status"], 201)
        self.test_case.assertIn("mds_file_ids", response)
        self.test_case.assertEqual(len(response["company_links"]), len(cids))

        linked_company_id_set = self.__get_linked_company_ids(file_id)
        self.test_case.assertSetEqual(linked_company_id_set, set(cids))

    def core_web_test_update_company_research_links(self):

        cids = [
            insert_test_company(name="C1"),
            insert_test_company(name="C2")
        ]

        response = self.__upload_platform_research_pdf(cids)
        file_id = response["mds_file_ids"].values()[0]

        cid3 = insert_test_company(name="C3")

        data = json.dumps({
            "company_links": [
                {
                    "id": cids[0],
                    "name": "C1"
                },
                {
                    "id": cid3,
                    "name": "C3"
                }
            ]
        })

        expected_company_result_set = {cids[0], cid3}

        response = self.web_access.put("/api/files/id/%s/company_research" % file_id, data, cookies=self.cooks,
                                       headers={"Content-Type": "application/json"}).json()

        self.test_case.assertIn("links_created", response)
        self.test_case.assertIn("links_deleted", response)
        self.test_case.assertSetEqual(set(response["linked_company_ids"]), expected_company_result_set)

        linked_company_id_set = self.__get_linked_company_ids(file_id)
        self.test_case.assertSetEqual(linked_company_id_set, expected_company_result_set)

    def core_web_test_update_company_research_links__moves_file(self):

        cids = [
            insert_test_company(name="C1"),
            insert_test_company(name="C2")
        ]

        # Upload file to MDS
        response = self.__upload_platform_research_pdf(cids)
        file_id = response["mds_file_ids"].values()[0]

        # Get MDS file
        query = {
            "_id": ensure_id(file_id)
        }
        entity_fields = ['_id', "data.rds_file_id"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query,
                                                    entity_fields=entity_fields, as_list=True)['params']
        mds_file = self.mds_access.call_find_entities_raw('file', params, self.context)[0]

        # Give RDS file bad path
        self.rds_access.call_update_file_path(mds_file[1], "platform_research_reports/C1/", self.context)

        # Give MDS file bad path/name
        field_data = {
            "data.path": "platform_research_reports/C1/",
            "name": "platform_research_reports/C1/stars.pdf"
        }
        self.mds_access.call_update_entity("file", file_id, self.context, field_data=field_data)

        rds_file = self.rds_access.call_get_file_by_name("platform_research_reports/C1/stars.pdf", self.context)

        data = json.dumps({
            "company_links": [
                {
                    "id": cids[0],
                    "name": "C1"
                },
                {
                    "id": cids[1],
                    "name": "C2"
                }
            ]
        })

        self.web_access.put("/api/files/id/%s/company_research" % file_id, data, cookies=self.cooks,
                            headers={"Content-Type": "application/json"}).json()

        query = {
            "_id": ensure_id(file_id)
        }
        entity_fields = ['_id', "name", "data.rds_file_id", "data.path"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query,
                                                    entity_fields=entity_fields, as_list=True)['params']
        mds_file = self.mds_access.call_find_entities_raw('file', params, self.context)[0]

        self.test_case.assertEqual(mds_file[1], "platform_research_reports/stars.pdf")
        self.test_case.assertEqual(mds_file[3], "platform_research_reports/")

        moved_rds_file = self.rds_access.call_get_file_by_name("platform_research_reports/stars.pdf", self.context)
        self.test_case.assertEqual(rds_file.content, moved_rds_file.content)

    #----------------------------------# Private Helpers #----------------------------------#

    def __upload_platform_research_pdf(self, cids):

        form_data = {
            "companyIds": json.dumps(cids),
            "fileName": "stars.pdf",
            "contentType": "application/pdf",
            "fileType": "platformResearchReport",
            "reportType": "full_report",
            "headline": "HEADLINE",
            "date": "2013-10-01",
            "src": "",
            "featured": "false",
            "public": "false"
        }

        path = os.path.dirname(os.path.abspath(__file__))
        filename = "stars.pdf"
        file_path = os.path.join(path, "data/", filename)

        with open(file_path, "r") as f:
            pdf_file = f

            files = {
                "file": pdf_file
            }

            response = self.web_access.post("/api/files", form_data, files=files, cookies=self.cooks).json()

        return response

    def __get_linked_company_ids(self, file_id):

        query = {
            "_id": ensure_id(file_id),
            "data.file_type": "platformResearchReport"
        }
        entity_fields = ['_id', "links.company.company_research"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query,
                                                    entity_fields=entity_fields, as_list=True)['params']
        files = self.main_access.mds.call_find_entities_raw('file', params, self.context)

        return {
            str(link["entity_id_to"])
            for link in files[0][1]
            if (link["entity_role_from"], link["entity_role_to"]) == ("research_pdf_file", "company")
        }
