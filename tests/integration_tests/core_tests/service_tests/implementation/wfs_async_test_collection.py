from __future__ import division
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, create_store_with_rir, insert_test_industry, insert_test_white_space_grid, insert_test_white_space_grid_cell
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from common.helpers.sysadmin_helper import get_host_name
from common.service_access.utilities.errors import ServiceCallError
from common.utilities.date_utilities import parse_date
from core.common.utilities.helpers import ensure_id
import datetime
import pprint
import time
import os


__author__ = "erezrubinstein"


class WFSAsyncTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = '1'
        self.source = "wfs_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source,
            "team_industries": [],
            "user": {"is_generalist": False}
        }

        # get dependencies
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # create helper vars for this class
        self.store_helper = StoreHelper()

    def setUp(self):

        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()
        self.rds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##----------------------## Test Methods ##--------------------------##

    def wfs_test_async_task(self):

        flow = "_test"
        process = "_test"
        stage = "_test"

        task_rec = {
            "input": {"entity_type": "company"},
            "meta": {"async": True}
        }
        result = self.main_access.wfs.call_task_new(flow, process, stage, task_rec, self.context)

        task_id = ensure_id(result["_id"])

        self.test_case.assertIn("task_status", result)
        self.test_case.assertDictEqual(result["task_status"], {"status": "in_progress", "result": None})

        tries = 20
        while result["task_status"]["status"] == "in_progress" and tries > 0:
            tries -= 1
            time.sleep(3)
            result = self.main_access.wfs.call_get_task_id(task_id)

            self.test_case.assertIn("task_status", result)

        self.test_case.assertEqual(result["task_status"]["status"], "success")

    def wfs_test_async_task__insert_wfs_task_false(self):

        # insert a test company
        company_id = insert_test_company()

        # set up task params
        flow = "_test"
        process = "_test"
        stage = "_test_no_wfs_task"
        task_rec = {
            "input": {"entity_type": "company", "entity_id": str(company_id)},
            "meta": {"async": True, "insert_wfs_task": False}
        }

        # insert the task (do not care about results)
        self.main_access.wfs.call_task_new(flow, process, stage, task_rec, self.context)

        # create find raw params
        query = {"_id": company_id}
        entity_fields = ["_id", "data.updated"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query,
                                                    entity_fields=entity_fields)["params"]

        company = None

        tries = 5
        while tries > 0:
            tries -= 1
            time.sleep(2)

            # query company
            company = self.main_access.mds.call_find_entities_raw("company", params)[0]

            # if company is there break
            if "updated" in company["data"] and company["data"]["updated"]:
                break

        # verify company exists, and updated is true
        self.test_case.assertTrue(company["data"]["updated"])

    def wfs_company_analytics_plan_b(self):

        self.test_case.maxDiff = None

        file_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

        zipped_filename = file_base_path + "/../../../../economics_tests/implementation/data/US_labor_data_2013_09_06.tar.gz"
        filename = "US_labor_data_2013_09_06"
        rds_path = "/economics/unemployment"
        self.__upload_file_to_rds(zipped_filename, filename, rds_path)

        industry_id1 = insert_test_industry("Industry 1")

        link_data = {
            "home_to_away": {
                "weight": 1.0
            },
            "away_to_home": {
                "weight": 1.0
            }
        }
        self.main_access.mds.call_add_link("industry", industry_id1, "competitor", "industry", industry_id1,
                                           "competitor", "industry_competition", self.context, link_data=link_data)

        workflow = {
            "analytics": {
                "status": "pending",
                "plan_b_has_run": True
            }
        }

        # create three companies, one parent, two children
        company_id_parent = insert_test_company(type="retail_parent", workflow_status="published", workflow=workflow)
        company_id_child_1 = insert_test_company(type="retail_banner", workflow_status="published", workflow=workflow)
        company_id_child_2 = insert_test_company(type="retail_banner", workflow_status="published", workflow=workflow)

        # make both banners children of the parent
        self.main_access.mds.call_add_link("company", company_id_child_1, "retail_segment", "company",
                                           company_id_parent, "retail_parent", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", company_id_child_2, "retail_segment", "company",
                                           company_id_parent, "retail_parent", "retailer_branding", self.context)

        self.main_access.mds.call_add_link("company", company_id_child_1, "primary_industry_classification", "industry",
                                           industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id_child_2, "primary_industry_classification", "industry",
                                           industry_id1, "primary_industry", "industry_classification", self.context)

        # create a white_space grid and one cell to encompass the 4 stores
        grid_name = "test_grid"
        grid_threshold = "SquareMiles10"
        grid_id = insert_test_white_space_grid(grid_threshold, grid_name)
        cell_id = insert_test_white_space_grid_cell(grid_id, [[[2, 2], [-2, 2], [-2, -2], [2, -2], [2, 2]]], grid_threshold, grid_name, 0, 0)

        # insert two stores per company
        store_id_1 = create_store_with_rir(company_id_child_1)
        store_id_2 = create_store_with_rir(company_id_child_1)
        store_id_3 = create_store_with_rir(company_id_child_2)
        store_id_4 = create_store_with_rir(company_id_child_2)

        # create task_rec for Plan B.  Run on company 1, which should run on all companies.
        # shall be run synchronously, but it spawns other asynchronous tasks via celery.canvas
        params = {
            "company_id": company_id_child_1,
            "timeout": 100000,
            "async": False
        }

        task_id = self.main_access.call_run_plan_b(params, self.context, timeout=100000)["_id"]

        # verify both child companies have the correct trade areas
        self._verify_company_trade_areas(company_id_child_1, [store_id_1, store_id_2])
        self._verify_company_trade_areas(company_id_child_2, [store_id_3, store_id_4], [])

        # verify gp14
        self._verify_gp_14([store_id_1, store_id_2, store_id_3, store_id_4], [], cell_id, grid_id, grid_threshold, grid_name)

        # verify white_space analytics
        self._verify_white_space_analytics(company_id_child_1, cell_id, 2)
        self._verify_white_space_analytics(company_id_child_2, cell_id, 2)

        # verify CCIs are correct
        self._verify_company_ccis(company_id_child_1, company_id_child_1)
        self._verify_company_ccis(company_id_child_1, company_id_child_2)
        self._verify_company_ccis(company_id_child_2, company_id_child_2)

        # make sure that all three companies have analytics and that the store_counts are correct
        self._verify_company_analytics(company_id_child_1, 2)
        self._verify_company_analytics(company_id_child_2, 2)
        self._verify_company_analytics(company_id_parent, 4)

        # query the task and make sure the status is correct
        task = self.main_access.wfs.call_get_task_id(task_id)

        host = get_host_name()

        # compare the results
        self.test_case.assertDictEqual(task["task_status"]["result"], {
            "status": "success",
            "duration_seconds": task["task_status"]["result"]["duration_seconds"],
            "start_time": task["task_status"]["result"]["start_time"],
            "end_time": task["task_status"]["result"]["end_time"],
            "company_id": company_id_child_1,
            "gp7_results": task["task_status"]["result"]["gp7_results"],
            "gp9_results": task["task_status"]["result"]["gp9_results"],
            "gp14_results": task["task_status"]["result"]["gp14_results"],
            "gp16_results": task["task_status"]["result"]["gp16_results"],
            "cci_results": task["task_status"]["result"]["cci_results"],
            "company_analytics_results": task["task_status"]["result"]["company_analytics_results"],
            "data_check_results": task["task_status"]["result"]["data_check_results"],
            "white_space_results": {
                company_id_child_1: {
                    'created_matches': [
                        {
                            'data': {
                                'cell_id': task["task_status"]["result"]["white_space_results"][company_id_child_1]["created_matches"][0]["data"]["cell_id"],
                                'company_id': company_id_child_1,
                                'grid_id': task["task_status"]["result"]["white_space_results"][company_id_child_1]["created_matches"][0]["data"]["grid_id"],
                                'grid_name': 'test_grid',
                                'has_openings': False,
                                'store_count': 2,
                                'threshold': 'SquareMiles10'
                            },
                            'name': 'cell_match'
                        }
                    ],
                    'deleted_matches': None,
                    'duration_seconds': task["task_status"]["result"]["white_space_results"][company_id_child_1]["duration_seconds"],
                    'num_created': 1,
                    'num_deleted': 0,
                    'status': 'success'
                },
                company_id_child_2: {
                    'created_matches': [
                        {
                            'data': {
                                'cell_id': task["task_status"]["result"]["white_space_results"][company_id_child_2]["created_matches"][0]["data"]["cell_id"],
                                'company_id': company_id_child_2,
                                'grid_id': task["task_status"]["result"]["white_space_results"][company_id_child_2]["created_matches"][0]["data"]["grid_id"],
                                'grid_name': 'test_grid',
                                'has_openings': False,
                                'store_count': 2,
                                'threshold': 'SquareMiles10'
                            },
                            'name': 'cell_match'
                        }
                    ],
                    'deleted_matches': None,
                    'duration_seconds': task["task_status"]["result"]["white_space_results"][company_id_child_2]["duration_seconds"],
                    'num_created': 1,
                    'num_deleted': 0,
                    'status': 'success'
                }
            },
            "exception": None,
            "host": host
        })

        # more specific tests to make sure the counts are right above
        self.test_case.assertEqual(len(task["task_status"]["result"]["gp7_results"]["succeeded"]), 4)
        self.test_case.assertEqual(len(task["task_status"]["result"]["gp7_results"]["failed"]), 0)
        self.test_case.assertEqual(len(task["task_status"]["result"]["gp9_results"]["succeeded"]), 4)
        self.test_case.assertEqual(len(task["task_status"]["result"]["gp9_results"]["failed"]), 0)
        self.test_case.assertEqual(len(task["task_status"]["result"]["gp14_results"]["succeeded"]), 4)
        self.test_case.assertEqual(len(task["task_status"]["result"]["gp14_results"]["failed"]), 0)
        self.test_case.assertEqual(len(task["task_status"]["result"]["gp16_results"]["succeeded"]), 4)
        #self.test_case.assertEqual(len(task["task_status"]["result"]["gp16_results"]["succeeded"]), 0) # commented out for now
        self.test_case.assertEqual(len(task["task_status"]["result"]["gp16_results"]["failed"]), 0)
        self.test_case.assertEqual(len(task["task_status"]["result"]["cci_results"]["succeeded"]), 2)
        self.test_case.assertEqual(len(task["task_status"]["result"]["cci_results"]["failed"]), 0)
        self.test_case.assertEqual(task["task_status"]["result"]["data_check_results"]["status"], "success")
        self.test_case.assertItemsEqual(task["task_status"]["result"]["company_analytics_results"]["banner_ids"], [
            company_id_child_1,
            company_id_child_2
        ])
        self.test_case.assertItemsEqual(task["task_status"]["result"]["company_analytics_results"]["engines"], [
            "demographics",
            "competition",
            "stores",
            "economics",
            "monopolies"
        ])

        query = {
            "_id": {
                "$in": [ensure_id(company_id_child_1), ensure_id(company_id_child_2), ensure_id(company_id_parent)]
            }
        }
        fields = ["_id", "data.workflow.analytics"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                    as_list=True)["params"]
        companies = self.main_access.mds.call_find_entities_raw("company", params, self.context)

        five_min_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

        for co in companies:

            duration_seconds = (parse_date(co[1]["end_time"]) - parse_date(co[1]["start_time"])).total_seconds()
            duration_minutes = round(duration_seconds / 60.0, 2)

            self.test_case.assertDictEqual(co[1], {
                'exception': None,
                'status': 'success',
                'creation_time': co[1]["creation_time"],
                'needs_plan_b_date': co[1]["needs_plan_b_date"],
                'plan_b_has_run': True,
                'run_id': co[1]["run_id"],
                'start_time': co[1]["start_time"],
                'end_time': co[1]["end_time"],
                'duration': duration_minutes,
                "host": host
            })

            self.test_case.assertTrue(co[1]["start_time"] < co[1]["end_time"])
            self.test_case.assertTrue(co[1]["end_time"] > five_min_ago)

        # create a fifth store for company2, which has a bad lat/long.  This should return an esri error on GP7
        store_id_5 = create_store_with_rir(company_id_child_2, latitude=-500, longitude=-500)

        # create task_rec for Plan B.  Run on company 1, which should run on all companies.
        # shall be run synchronously, but it spawns other asynchronous tasks via celery.canvas
        params = {
            "company_id": company_id_child_1,
            "timeout": 100000,
            "async": False
        }

        # Run again to make sure it fails
        with self.test_case.assertRaises(ServiceCallError):
            self.main_access.call_run_plan_b(params, self.context)

    def wfs_task_custom_on_failure(self):

        # set up task params
        flow = "_test"
        process = "_test"
        stage = "_test_custom_on_failure"
        task_rec = {
            "meta": {"async": True, "insert_wfs_task": True}
        }

        # insert the task -- should report in_progress
        task = self.main_access.wfs.call_task_new(flow, process, stage, task_rec, self.context)

        self.test_case.assertEqual(task["task_status"]["status"], "in_progress")

        print task

        tries = 5
        while tries > 0:
            tries -= 1
            time.sleep(2)

            running_task = self.main_access.wfs.call_get_task_id(ensure_id(task["_id"]), self.context)

            print running_task

            # if task has been marked failed, break
            if running_task["task_status"]["status"] == "failure":
                break

        self.test_case.assertIn("You know what I blame this on the breakdown of? Society.",
                                running_task["task_status"]["message"])

    # -------------------------- Private Helpers -------------------------- #

    def _verify_company_ccis(self, cid1, cid2):

        query = {
            "$or": [
                {
                    "data.pair.entity_id_from": ensure_id(cid1),
                    "data.pair.entity_id_to": ensure_id(cid2)
                },
                {
                    "data.pair.entity_id_from": ensure_id(cid2),
                    "data.pair.entity_id_to": ensure_id(cid1)
                }
            ]
        }
        fields = ["_id"]
        params = self.main_params.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                    as_list=True)["params"]
        ccis = self.main_access.mds.call_find_entities_raw("company_competition_instance", params, self.context)

        if cid1 == cid2:
            self.test_case.assertEqual(len(ccis), 1)
        else:
            self.test_case.assertEqual(len(ccis), 2)

    def _verify_company_analytics(self, company_id, store_count, should_pprint=False):

        # find company
        params = {
            "query": {"_id": company_id},
            "entity_fields": ["_id", "data"]
        }
        company = self.main_access.mds.call_find_entities_raw("company", params)[0]

        if should_pprint:
            self._pprint_json(company)

        # make sure store count is correct
        self.test_case.assertEqual(company["data"]["analytics"]["stores"]["monthly"]["store_counts"][0]["value"],
                                   store_count)

    def _verify_company_trade_areas(self, company_id, store_ids, bad_store_ids=None):

        if not bad_store_ids:
            bad_store_ids = []

        # find all trade areas for this company
        params = {
            "query": {"data.company_id": company_id},
            "entity_fields": ["_id", "data"]
        }
        trade_areas = self.main_access.mds.call_find_entities_raw("trade_area", params)

        # make sure there are the correct amount of trade areas
        self.test_case.assertEqual(len(trade_areas), len(store_ids))

        # for each trade area, make sure it's been geoprocessed
        for trade_area in trade_areas:
            self._verify_trade_area_has_been_geoprocessed(trade_area, store_ids, bad_store_ids)

    def _verify_gp_14(self, matching_store_ids, non_matching_store_ids, cell_id, grid_id, threshold, grid_name):

        # select all matching stores stores
        if matching_store_ids:
            params = {
                "query": { "_id": { "$in": matching_store_ids }},
                "entity_fields": ["_id", "data.white_space_cell_matches"]
            }
            matching_stores = self.main_access.mds.call_find_entities_raw("store", params)

            # verify each store
            for store in matching_stores:
                self.test_case.assertEqual(store["data"]["white_space_cell_matches"], {
                    threshold: {
                        "cell_id": cell_id,
                        "grid_name": grid_name,
                        "grid_id": grid_id
                    }
                })

        # select all non-matching stores stores
        if non_matching_store_ids:
            params = {
                "query": { "_id": { "$in": non_matching_store_ids }},
                "entity_fields": ["_id", "data.white_space_cell_matches"]
            }
            non_matching_stores = self.main_access.mds.call_find_entities_raw("store", params)

            # verify each store
            for store in non_matching_stores:
                self.test_case.assertNotIn("white_space_cell_matches", store["data"])

    def _verify_white_space_analytics(self, company_id, cell_id, store_count):

        # find all cell matches
        params = {
            "query": { "data.company_id": company_id },
            "entity_fields": ["_id", "data.cell_id", "data.store_count"]
        }
        matches = self.main_access.mds.call_find_entities_raw("white_space_grid_cell_match", params)

        # verify, son.
        self.test_case.assertEqual(matches, [{
            "_id": matches[0]["_id"],
            "data": {
                "cell_id": cell_id,
                "store_count": store_count
            }
        }])

    def _verify_trade_area_has_been_geoprocessed(self, trade_area, store_ids, bad_store_ids=None):

        if not bad_store_ids:
            bad_store_ids = []

        store_id = trade_area["data"]["store_id"]

        if store_id in bad_store_ids:
            self.test_case.assertIn(store_id, bad_store_ids)
            self.test_case.assertNotIn("demographics", trade_area["data"])
            self.test_case.assertNotIn("competitive_stores", trade_area["data"])
            self.test_case.assertNotIn("monopolies", trade_area["data"])
        else:
            self.test_case.assertIn(store_id, store_ids)
            self.test_case.assertIn("demographics", trade_area["data"])
            self.test_case.assertIn("competitive_stores", trade_area["data"])
            self.test_case.assertIn("monopolies", trade_area["data"])

    def _pprint_json(self, obj):

        print pprint.pformat(obj).replace("u'", "'").replace("'", "\"") \
            .replace("None", "null").replace("False", "false").replace("True", "true")

    #-----------------------------------# Private Helpers #-------------------------------------#

    def __upload_file_to_rds(self, zipped_filename, filename, rds_path):

        with open(zipped_filename, 'rb') as f:
            post_file = {
                "file": (filename + ".tar.gz", f)
            }
            self.main_access.rds.call_post_file(rds_path, post_file, context=self.context)

###################################################################################################
