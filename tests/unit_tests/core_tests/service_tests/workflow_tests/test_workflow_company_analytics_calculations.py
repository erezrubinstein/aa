from bson.objectid import ObjectId
import mox

from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.company_analytics_calculations import CompanyAnalyticsCalculations
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies


class WorkflowCompanyAnalyticsCalculationsTests(mox.MoxTestBase):

    def setUp(self):
        super(WorkflowCompanyAnalyticsCalculationsTests, self).setUp()

        register_common_mox_dependencies(self.mox)

        self.mock = self.mox.CreateMock(CompanyAnalyticsCalculations)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.analytics = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()

        self.mock.main_params = self.mox.CreateMockAnything()
        self.mock.main_params.mds = self.mox.CreateMockAnything()

        self.mock.context = {}
        self.calc_run_params = {
            "target_entity_ids": ['trade_area_id'],
            "options": {
                "fetch": True,
                "save": True,
                "return": False
            }
        }

    def doCleanups(self):
        super(WorkflowCompanyAnalyticsCalculationsTests, self).doCleanups()
        dependencies.clear()

    def test_find_companies_ready_for_analytics(self):
        """
        Ensure that the procedure for finding companies ready for analytics follows this order:

        1. Get all companies that are published
        2. Get count of all trade areas that belong to the published companies
        3. Third get count of all trade areas that belong to the published companies that also meet the requirements for
           analytics calculations.  If this count matches the number of trade areas (meaning all of a published company's
           trade areas have the required geoprocessing completed) then the company is ready for analytics.

        There's no logic to test in this function.
        """
        self.mock.parent_to_banner_dict = {}
        self.mock.banner_ids_set = set()
        self.mock.not_geoprocessed_banners = []

        # Step 1
        query = {
            'data.workflow.current.status': 'published',
            'data.type': "retail_banner"
        }
        entity_fields = ['_id', 'links.company.retailer_branding']

        params = "params"
        self.mock.main_params.mds.create_params(resource='find_entities_raw', query=query,
                                                entity_fields=entity_fields, as_list=True).AndReturn({"params": params})

        published_companies = [["col1", [{"entity_id_to": "par1", "entity_role_to": "retail_parent"}]],
                               ["col2", [{"entity_id_to": "par2", "entity_role_to": "asdf"}]]]
        self.mock.main_access.mds.call_find_entities_raw('company', params).AndReturn(published_companies)
        published_companies = [co[0] for co in published_companies]

        # Step 2
        trade_areas_per_company1 = [{"_id": published_companies[0], "num_trade_areas": 10}]
        pipeline_trade_areas_per_company = [
            {"$match": {"data.company_id": published_companies[0]}},
            {"$group": {"_id": "$data.company_id", "num_trade_areas": {"$sum": 1}}}
        ]
        self.mock.main_access.mds.call_aggregate_entities("trade_area", pipeline_trade_areas_per_company,
                                                          self.mock.context).AndReturn(trade_areas_per_company1)

        trade_areas_per_company2 = [{"_id": published_companies[1], "num_trade_areas": 20}]
        pipeline_trade_areas_per_company = [
            {"$match": {"data.company_id": published_companies[1]}},
            {"$group": {"_id": "$data.company_id", "num_trade_areas": {"$sum": 1}}}
        ]
        self.mock.main_access.mds.call_aggregate_entities("trade_area", pipeline_trade_areas_per_company,
                                                          self.mock.context).AndReturn(trade_areas_per_company2)

        # Step 3
        trade_areas_per_company1 = [{"_id": published_companies[0], "num_trade_areas_ready": 10}]
        pipeline_companies_to_run = [
            {"$match": {"data.company_id": published_companies[0],
                        "data.demographics": {"$exists": True},
                        "data.competitive_stores": {"$exists": True},
                        "data.monopolies": {"$exists": True}
            }},
            {"$group": {"_id": "$data.company_id","num_trade_areas_ready": {"$sum": 1}}}
        ]
        self.mock.main_access.mds.call_aggregate_entities("trade_area", pipeline_companies_to_run,
                                                          self.mock.context).AndReturn(trade_areas_per_company1)

        trade_areas_per_company2 = [{"_id": published_companies[1], "num_trade_areas_ready": 19}]
        pipeline_companies_to_run = [
            {"$match": {"data.company_id": published_companies[1],
                        "data.demographics": {"$exists": True},
                        "data.competitive_stores": {"$exists": True},
                        "data.monopolies": {"$exists": True}
            }},
            {"$group": {"_id": "$data.company_id","num_trade_areas_ready": {"$sum": 1}}}
        ]
        self.mock.main_access.mds.call_aggregate_entities("trade_area", pipeline_companies_to_run,
                                                          self.mock.context).AndReturn(trade_areas_per_company2)

        self.mox.ReplayAll()

        CompanyAnalyticsCalculations._find_companies_ready_for_analytics(self.mock)

        self.assertDictEqual(self.mock.parent_to_banner_dict, {'par1': [published_companies[0]]})

    def test_get_parents_for_banners(self):

        self.mock.banner_ids = [ObjectId(), ObjectId()]
        self.mock.parent_to_banner_dict = {}
        self.mock.banner_ids_set = set()
        self.mock.not_geoprocessed_banners = []

        query = {
            '_id': {"$in": self.mock.banner_ids},
            'data.type': "retail_banner"
        }
        entity_fields = ['_id', 'links.company.retailer_branding']

        params = "params"
        self.mock.main_params.mds.create_params(resource='find_entities_raw', query=query,
                                                entity_fields=entity_fields, as_list=True).AndReturn({"params": params})

        published_companies = [["co1", [{"entity_id_to": "par1", "entity_role_to": "retail_parent"}]],
                               ["co2", [{"entity_id_to": "par2", "entity_role_to": "asdf"}]]]
        self.mock.main_access.mds.call_find_entities_raw('company', params, encode_and_decode_results=False).AndReturn(published_companies)

        self.mox.ReplayAll()

        CompanyAnalyticsCalculations._get_parents_for_banners(self.mock)

        self.assertDictEqual(self.mock.parent_to_banner_dict, {None: ["co2"], 'par1': ['co1']})

