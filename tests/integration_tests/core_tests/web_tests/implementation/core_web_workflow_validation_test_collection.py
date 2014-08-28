from __future__ import division
import json
import pprint
import datetime
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_rir, insert_test_company, insert_test_industry
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from requests.cookies import RequestsCookieJar
from bson.objectid import ObjectId


__author__ = 'vgold'


class CoreWebWorkflowValidationTestCollection(ServiceTestCollection):

    def initialize(self):
        self.main_param = Dependency("CoreAPIParamsBuilder").value
        self.user_id = 'test@nexusri.com'
        self.source = "core_web_workflow_validation_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }
        self.cooks = self.__login_test_user_get_cookies()
        self.json_headers = {"access": "application/json", "content-type": "application/json"}

    def setUp(self):
        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def __login_test_user_get_cookies(self):
        params = {"email": "test@nexusri.com", "password": self.config["TEST_USER_PASSWORD"]}
        response = self.web_access.post(self.config["SECURITY_LOGIN_URL"], params)
        assert response.ok
        assert isinstance(response.cookies, RequestsCookieJar)
        return response.cookies

    ##------------------------------------ User Admin Tests ---------------------------------------##

    def web_test_get_tasks_by_status(self):
        self.test_case.maxDiff = None

        statuses = [
            "open",
            "in_progress",
            "locked",
            "completed"
        ]

        for i, status in enumerate(statuses):
            ind_name = "IND%s" % i
            iid = insert_test_industry(name=ind_name)
            co_name = "CO%s" % i
            cid = insert_test_company(name=co_name)
            rid = insert_test_rir(self.context, cid, company_name=co_name)
            email = "email%s" % i
            t = self.__form_task_rec(iid, cid, rid, status, email)

            params = {
                "query": t,
                "update": {"$set": t},
                "upsert": True
            }
            self.wfs_access.call_find_and_modify_task(params, self.context)

            task_results = self.web_access.get("/api/retail_input/matching_workflow/%s" % status, "",
                                               headers=self.json_headers, cookies=self.cooks).json()
            tasks_recs = task_results["results"]
            self.test_case.assertEqual(len(tasks_recs), task_results["meta"]["num_rows"], 1)
            self.test_case.assertListEqual(tasks_recs[0], [
                email,
                tasks_recs[0][1],
                'Churn Validation',
                tasks_recs[0][3],
                ind_name,
                co_name,
                tasks_recs[0][6],
                '123 Main St',
                'UNIT_TEST_VILLE',
                'UT',
                '12345',
                '555-867-5309',
                'UNIT_TEST_MALL',
                '',
                'UNIT_TEST_STORE_FORMAT',
                'IM A UNIT TEST'
            ])

    def web_test_unlock_task(self):
        self.test_case.maxDiff = None

        i = 0
        status = "locked"

        ind_name = "IND%s" % i
        iid = insert_test_industry(name=ind_name)
        co_name = "CO%s" % i
        cid = insert_test_company(name=co_name)
        rid = insert_test_rir(self.context, cid, company_name=co_name)
        email = "email%s" % i
        t = self.__form_task_rec(iid, cid, rid, status, email)

        params = {
            "query": t,
            "update": {"$set": t},
            "upsert": True
        }
        self.wfs_access.call_find_and_modify_task(params, self.context)

        task_id = self.web_access.get("/api/retail_input/matching_workflow/%s" % status, "",
                                      headers=self.json_headers, cookies=self.cooks).json()["results"][0][1]

        task = self.web_access.put("/api/retail_input/task/%s/unlock" % task_id, json.dumps({}),
                                   headers=self.json_headers, cookies=self.cooks).json()

        self.test_case.assertDictEqual(task, {
            "task": {
                "_id": task_id,
                "task_status": {
                    "status": "open"
                }
            }
        })

    def __form_task_rec(self, iid, cid, rid, status, email):
        return  {
            "type": "task",
            "flow": "retail_curation",
            "process": "input_sourcing",
            "stage": "churn_validation",
            "input": {
                "company_id": cid,
                "industry_id": iid,
                "target_rir_id": rid
            },
            "task_status": {
                "status": status
            },
            "context_data": {
                "user": {
                    "email": email
                }
            },
            "meta": {
                "updated_at": datetime.datetime.utcnow()
            }
        }