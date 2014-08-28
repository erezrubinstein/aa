import random

from bson.objectid import ObjectId

from geoprocessing.geoprocessors.competition.gp9_core_trade_area_competition_geo_json import GP9CoreTradeAreaCompetition
from core.service.svc_workflow.helpers.company_analytics_report_assesser import CompanyAnalyticsReportAssesser
from core.common.business_logic.service_entity_logic.company_helper import update_company_competition_pairs
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_industry, create_store_with_rir, insert_test_geoprocessed_trade_area, select_trade_area, insert_test_company, insert_test_store, insert_test_trade_area
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from core.common.business_logic.service_entity_logic import company_helper, industry_helper
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import LAST_ANALYTICS_DATE, ANALYTICS_TARGET_YEAR
from common.utilities.time_series import get_monthly_time_series, TIME_SERIES_START


__author__ = 'vgold'


class WFSCompanyAnalyticsCalculationsTestCollection(ServiceTestCollection):

    def initialize(self):

        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            'user_id': ObjectId(),
            'source': 'wfs_company_analytics_calculations_test_collection.py'
        }

    def setUp(self):

        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def wfs_test_company_analytics_task_and_store_quality_data(self):

        cids = [
            insert_test_company(name="Company %s" % i, type="retail_banner", workflow_status="published")
            for i in range(3)
        ]

        store_dict = {
            cid: [
                insert_test_store(cid, [None, None])
                for _ in range(3)
            ]
            for cid in cids
        }

        competitive_store = {
            "end_date": "3000-01-01T00:00:00",
            "start_date": "1900-01-01T00:00:00",
            "weight": 1,
            "away_company_name": "away_company_name",
            "away_street_number": "away_street_number",
            "away_street": "away_street",
            "away_city": "away_city",
            "away_state": "away_state",
            "away_zip": "away_zip",
            "away_geo": [
                "away_geo_lng", "away_geo_lat"
            ],
            "away_lng": "away_geo_lng",
            "away_lat": "away_geo_lat"
        }

        demographics = {
            "TOTHH_CY": {
                "value": 301120,
                "description": "TOTHH_CY",
                "target_year": ANALYTICS_TARGET_YEAR
            },
            "TOTPOP_CY": {
                "value": 711395,
                "description": "TOTPOP_CY",
                "target_year": ANALYTICS_TARGET_YEAR
            }
        }

        monopolies = [
            {
                "start_date": "1900-01-01T00:00:00",
                "end_date": "3000-01-01T00:00:00",
                "monopoly_type": "SinglePlayerMonopoly"
            }
        ]

        tids = []
        for cid, sids in store_dict.iteritems():
            for sid in sids:

                away_store_id = random.choice(sids)
                while away_store_id == sid:
                    away_store_id = random.choice(sids)

                away_company_id = random.choice(cids)
                while away_company_id == sid:
                    away_company_id = random.choice(cids)

                comp_stores = [
                    dict(competitive_store, away_store_id=away_store_id, away_company_id=away_company_id)
                    for _ in range(3)
                ]

                tids.append(insert_test_trade_area(store_id=sid, company_id=cid, competitive_stores=comp_stores,
                                                   demographics=demographics, monopolies=monopolies))

        engines = ["demographics", "competition", "monopolies", "stores"]

        task_rec = {
            'input': {
                'engines': engines,
                'banner_ids': cids[:-1],
                'spawn_async_tasks': False,
                'wait_for_tasks': True,
                'sleep_interval': 1,
                'run_report': False
            },
            'meta': {
                'async': False
            }
        }

        options = {
            "start_tasks": False
        }
        task_response = self.wfs_access.call_task_new('retail_analytics', 'analytics',
                                                      'company_analytics_calculations',
                                                      task_rec, self.context, options=options)
        parent_task_id = task_response["_id"]

        # Put a task that mimicks being lost in there
        lost_task_rec = {
            'input': {
                'parent_task_id': parent_task_id,
                'engines': engines,
                'banner_ids': [cids[-1]],
                'spawn_async_reporter': False,
                'spawn_async_pair_sync_tasks': False,
                'run_report': False
            }
        }

        lost_task_response = self.wfs_access.call_task_new('retail_analytics', 'analytics',
                                                           'company_family_analytics_calculator',
                                                           lost_task_rec, self.context, options=options)

        self.wfs_access.call_start_tasks([parent_task_id], self.context)

        # Make the parent task this it has more child tasks
        params = {
            "task_status.result.num_child_tasks": 3,
            "task_status.result.num_retail_banners": 3,
            "task_status.result.reported": False,
            "_actions": {
                "task_status.result.child_task_ids": {
                    "$push": {
                        "task_status.result.child_task_ids": lost_task_response["_id"]
                    }
                }
            }
        }
        self.wfs_access.call_update_task_id(parent_task_id, self.context, params)

        # Run assesser with retries lost tasks
        CompanyAnalyticsReportAssesser(parent_task_id, self.context, spawn_async_reporter=False).assess()

        # Now get task rec
        task = self.wfs_access.call_get_task_id(parent_task_id, self.context, {})

        self.test_case.assertEqual(task["task_status"]["status"], "success")
        self.test_case.assertEqual(task["task_status"]["result"]["num_child_tasks"], 3)
        self.test_case.assertEqual(task["task_status"]["result"]["num_child_tasks_completed"], 2)
        self.test_case.assertEqual(task["task_status"]["result"]["num_child_tasks_started"], 2)
        self.test_case.assertEqual(task["task_status"]["result"]["num_child_tasks_succeeded"], 2)
        self.test_case.assertEqual(task["task_status"]["result"]["num_child_tasks_failed"], 0)

        self.test_case.assertTrue(len(task["task_status"]["children"]) > 0)
        for child_task_id, child_task_result in task["task_status"]["children"].iteritems():
            self.test_case.assertEqual(child_task_result["status"], "success")

        #
        # Test out report
        #
        report = self.wfs_access.call_get_task_analytics_report(task["_id"], self.context)

        self.test_case.assertEqual(report["stats"]["task_id"], "Web Request")
        self.test_case.assertEqual(report["stats"]["parent_task_id"], task["_id"])
        self.test_case.assertEqual(report["stats"]["engines"], ', '.join(engines))

        self.test_case.assertIn("start_time", report["stats"])
        self.test_case.assertIn("end_time", report["stats"])
        self.test_case.assertIn("task_run_time", report["stats"])

        self.test_case.assertDictContainsSubset(
            {
                "num_tasks": 4,
                "num_unstarted_tasks": 1,
                "num_tasks_started": 2,
                "num_tasks_completed": 2,
                "num_tasks_succeeded": 2,
                "num_tasks_failed": 0,
                "percent_success": "50%",
                "percent_failure": "0%",
                "percent_unstarted": "25%",
                "lost_task_ids": lost_task_response["_id"],
                "num_retail_parents": 0,
                "num_retail_banners": 3,
                "num_not_geoprocessed_banners": 0,
                "not_geoprocessed_banners": "--",
                "num_succeeded_parents": 0,
                "num_succeeded_banners": 2,
                "num_failed_parents": 0,
                "num_failed_banners": 0,
                "num_unstarted_parents": 0,
                "num_unstarted_banners": 1,
                "num_in_progress_parents": 0,
                "num_in_progress_banners": 0,
            },
            report["stats"]
        )

        self.test_case.assertEqual(len(report["successful_tasks"]), 2)
        self.test_case.assertEqual(len(report["failed_tasks"]), 0)
        self.test_case.assertEqual(report["results_are_valid"], True)

    def test_analytics_run__0_weights(self):
        """
        Industry A competes with Industry B
        A->B : weight 1.0
        B->A : weight 0.0
        """
        # industries
        industry_A = insert_test_industry()
        industry_B = insert_test_industry()

        # companies
        company_parent = insert_test_company(name ="company_parent", workflow_status="published", type="retail_parent")
        company_A = insert_test_company(name="company_A", workflow_status="published", type="retail_banner")
        company_B = insert_test_company(name="company_B", workflow_status="published", type="retail_banner")

        # make these companies children of the parent
        relationships = [
            {
                "company_id_from": company_parent,
                "role_from": "retail_parent",
                "company_id_to": company_A,
                "role_to": "retail_segment",
                "relation_type": "retailer_branding"
            },
            {
                "company_id_from": company_parent,
                "role_from": "retail_parent",
                "company_id_to": company_B,
                "role_to": "retail_segment",
                "relation_type": "retailer_branding"
            }
        ]

        company_helper.create_company_relationships(relationships, self.context, async=False)

        # two stores per company
        A_store_1 = create_store_with_rir(company_A, longitude=0.0, latitude=0.0)
        A_store_2 = create_store_with_rir(company_A, longitude=10.0, latitude=10.0)
        B_store_1 = create_store_with_rir(company_B, longitude=0.0, latitude=0.0)
        B_store_2 = create_store_with_rir(company_B, longitude=10.0, latitude=10.0)

        # shape arrays
        shape_array_1 = [[[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0], [1.0, 0.0]]]
        shape_array_2 = [[[11.0, 10.0], [10.0, 11.0], [9.0, 10.0], [10.0, 9.0], [11.0, 10.0]]]

        # one trade area per store
        A_trade_area_1 = insert_test_geoprocessed_trade_area(A_store_1, B_store_1, company_id=company_A, longitude=0.0,
                                                             latitude=0.0, shape_array=shape_array_1,
                                                             dem_total_population=5000)
        A_trade_area_2 = insert_test_geoprocessed_trade_area(A_store_2, B_store_2, company_id=company_A, longitude=10.0,
                                                             latitude=10.0, shape_array=shape_array_2,
                                                             dem_total_population=5000)
        B_trade_area_1 = insert_test_geoprocessed_trade_area(B_store_1, A_store_1, company_id=company_B, longitude=0.0,
                                                             latitude=0.0, shape_array=shape_array_1,
                                                             dem_total_population=5000)
        B_trade_area_2 = insert_test_geoprocessed_trade_area(B_store_2, A_store_2, company_id=company_B, longitude=10.0,
                                                             latitude=10.0, shape_array=shape_array_2,
                                                             dem_total_population=5000)

        # set companies to industries
        company_helper.insert_new_industry_links(company_A, [industry_A], True, self.context)
        company_helper.insert_new_industry_links(company_B, [industry_B], True, self.context)

        # competition data
        comp_data = {
            "home_industry": industry_A,
            "away_industry": industry_B,
            "home_weight": 1.0,
            "away_weight": 0.0
        }

        # create industry competition
        industry_helper.create_industry_competition_link(comp_data, self.context, async=False)

        # cci
        update_company_competition_pairs(company_A, self.context, async=False)
        update_company_competition_pairs(company_B, self.context, async=False)

        geoprocessor = GP9CoreTradeAreaCompetition()

        # geoprocess those steeds
        geoprocessor.process_object(select_trade_area(A_trade_area_1))
        geoprocessor.process_object(select_trade_area(A_trade_area_2))
        geoprocessor.process_object(select_trade_area(B_trade_area_1))
        geoprocessor.process_object(select_trade_area(B_trade_area_2))

        # now do analytics!1
        # run analytics
        task_rec = {
            'input': {
                'banner_ids': [company_A, company_B],
                'engines': ["demographics", "competition", "monopolies", "stores"],
                'spawn_async_tasks': False,
                'wait_for_tasks': True,
                'sleep_interval': 1,
                'run_report': False
            },
            'meta': {
                'async': False
            }
        }

        self.wfs_access.call_task_new('retail_analytics',
                                      'analytics',
                                      'company_analytics_calculations',
                                      task_rec,
                                      self.context,
                                      timeout=999999)

        A_trade_area_1_doc = select_trade_area(A_trade_area_1)
        B_trade_area_1_doc = select_trade_area(B_trade_area_1)
        A_trade_area_2_doc = select_trade_area(A_trade_area_2)
        B_trade_area_2_doc = select_trade_area(B_trade_area_2)

        company_A_doc, company_B_doc = company_helper.select_companies_by_id([company_A, company_B], self.context,
                                                                             additional_fields=["data"])

        # All trade areas should have the same raw away store counts
        monthly_time_series = get_monthly_time_series(start=TIME_SERIES_START, end=LAST_ANALYTICS_DATE)

        for i in range(len(monthly_time_series)):

            # raw
            self.test_case.assertEqual(1, A_trade_area_1_doc["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["raw"][i]["value"])
            self.test_case.assertEqual(1, B_trade_area_1_doc["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["raw"][i]["value"])
            self.test_case.assertEqual(1, A_trade_area_2_doc["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["raw"][i]["value"])
            self.test_case.assertEqual(1, B_trade_area_2_doc["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["raw"][i]["value"])

            # weighted
            self.test_case.assertEqual(1.0, A_trade_area_1_doc["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["weighted"][i]["value"])
            self.test_case.assertEqual(0.0, B_trade_area_1_doc["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["weighted"][i]["value"])
            self.test_case.assertEqual(1.0, A_trade_area_2_doc["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["weighted"][i]["value"])
            self.test_case.assertEqual(0.0, B_trade_area_2_doc["data"]["analytics"]["competition"]["monthly"]["away_store_counts"]["weighted"][i]["value"])

            # competition weighted demographics
            self.test_case.assertEqual(2500, A_trade_area_1_doc["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["TOTPOP_CY"][0]["series"][i]["value"])
            self.test_case.assertEqual(5000, B_trade_area_1_doc["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["TOTPOP_CY"][0]["series"][i]["value"])
            self.test_case.assertEqual(2500, A_trade_area_2_doc["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["TOTPOP_CY"][0]["series"][i]["value"])
            self.test_case.assertEqual(5000, B_trade_area_2_doc["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["TOTPOP_CY"][0]["series"][i]["value"])

            # company competition ratios
            self.test_case.assertEqual(1.0, company_A_doc["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["company_competition_ratio"]["weighted"]["total"][i]["value"])
            self.test_case.assertEqual(0.0, company_B_doc["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["company_competition_ratio"]["weighted"]["total"][i]["value"])

            # average company competition weights
            self.test_case.assertEqual(1.0, company_A_doc["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["total"][i]["value"])
            self.test_case.assertEqual(0.0, company_B_doc["data"]["analytics"]["competition"]["monthly"]["DistanceMiles10"]["average_competition_weight"]["total"][i]["value"])

            # median demographics
            self.test_case.assertEqual(2500, company_A_doc["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["median"][0]["series"][i]["value"])
            self.test_case.assertEqual(5000, company_B_doc["data"]["analytics"]["competition_adjusted_demographics"]["monthly"]["DistanceMiles10"]["aggregate_trade_area_population"]["median"][0]["series"][i]["value"])

