from bson.objectid import ObjectId
import mox
from mox import IsA
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import company_helper, geoprocessing_helper
from core.common.business_logic.service_entity_logic.company_helper import mark_as_needs_plan_b
from core.service.svc_master_data_storage.implementation import pair_entity_helper
import unittest
import datetime

__author__ = 'erezrubinstein'


class TestCompanyHelper(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestCompanyHelper, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # various needed data
        self.context = { "user": "chicken_woot" }

    def doCleanups(self):
        # call parent clean up
        super(TestCompanyHelper, self).doCleanups()

        # clear dependencies
        dependencies.clear()

    def test_update_company_fields__name_does_not_change(self):

        # set up mock data
        mock_company_id = ObjectId()
        mock_primary_industry_id = ObjectId()
        mock_secondary_industries = ["chicken", "woot"]
        mock_company = { "name": "name" }
        extra_fields = ["data.workflow.current.status", "links.company.retailer_branding.entity_role_to"]

        # stub out various methods
        self.mox.StubOutWithMock(company_helper, "select_companies_by_id")
        self.mox.StubOutWithMock(company_helper, "upsert_company_primary_industry")
        self.mox.StubOutWithMock(company_helper, "upsert_company_secondary_industries")
        #self.mox.StubOutWithMock(geoprocessing_helper, 'evaluate_need_for_geoprocessing')
        self.mox.StubOutWithMock(pair_entity_helper, 'create_pair_entity_sync_task')

        # start recording
        company_helper.select_companies_by_id([mock_company_id], self.context, additional_fields=extra_fields).AndReturn([mock_company])
        self.mock_main_access.mds.call_update_entity("company", mock_company_id, self.context, field_data = IsA(dict))
        company_helper.upsert_company_primary_industry(mock_company_id, mock_primary_industry_id, self.context, "wfs_status")
        company_helper.upsert_company_secondary_industries(mock_company_id, mock_secondary_industries, self.context)
        #geoprocessing_helper.evaluate_need_for_geoprocessing('company', mock_company_id, self.context)
        pair_entity_helper.create_pair_entity_sync_task('company', mock_company_id, self.context)

        # replay All
        self.mox.ReplayAll()

        # go!
        company_helper.update_company_fields(mock_company_id, "name", "type", "status", "ticker", "exchange", "wfs_status", 10, None, None,
                                             "description", [], mock_primary_industry_id, mock_secondary_industries, "false", self.context)

    def test_update_company_fields__name_does_change(self):

        # set up mock data
        mock_company_id = ObjectId()
        mock_primary_industry_id = ObjectId()
        mock_secondary_industries = ["chicken", "woot"]
        mock_company = { "name": "name" }
        extra_fields = ["data.workflow.current.status", "links.company.retailer_branding.entity_role_to"]

        # stub out various methods
        self.mox.StubOutWithMock(company_helper, "select_companies_by_id")
        self.mox.StubOutWithMock(company_helper, "upsert_company_primary_industry")
        self.mox.StubOutWithMock(company_helper, "upsert_company_secondary_industries")
        self.mox.StubOutWithMock(company_helper, "start_company_name_change_async_task")
        #self.mox.StubOutWithMock(geoprocessing_helper, 'evaluate_need_for_geoprocessing')
        self.mox.StubOutWithMock(pair_entity_helper, 'create_pair_entity_sync_task')

        # start recording
        company_helper.select_companies_by_id([mock_company_id], self.context, additional_fields=extra_fields).AndReturn([mock_company])
        self.mock_main_access.mds.call_update_entity("company", mock_company_id, self.context, field_data = IsA(dict))
        company_helper.upsert_company_primary_industry(mock_company_id, mock_primary_industry_id, self.context, "wfs_status")
        company_helper.upsert_company_secondary_industries(mock_company_id, mock_secondary_industries, self.context)
        company_helper.start_company_name_change_async_task(mock_company_id, self.context)
        #geoprocessing_helper.evaluate_need_for_geoprocessing('company', mock_company_id, self.context)
        pair_entity_helper.create_pair_entity_sync_task('company', mock_company_id, self.context)

        # replay All
        self.mox.ReplayAll()

        # go (with new name)!
        company_helper.update_company_fields(mock_company_id, "chicken_woot", "type", "status", "ticker", "exchange", "wfs_status", 10, None, None,
                                             "description", [], mock_primary_industry_id, mock_secondary_industries, "false", self.context)

    def test_start_company_name_change_async_task(self):
        # set up expected data
        mock_company_id = ObjectId()
        workflow_input_record = {
            'input': {
                "context": self.context,
                "company_id": mock_company_id
            },
            'meta': {
                'async': True
            },
            'task_status': {
                'status': "in-progress"
            }
        }

        # start recording
        self.mock_main_access.wfs.call_task_new('entity_updated', 'company', 'company_name_change', workflow_input_record, self.context)

        # replay all
        self.mox.ReplayAll()

        # go!
        company_helper.start_company_name_change_async_task(mock_company_id, self.context)


    def test_upsert_company_primary_industry__needs_update(self):
        company_id = "taco express"
        industry_id = "mexican cuisine"
        current_primary_id = "asdf"
        current_primary_name = ";lkj"
        context = {}

        self.mox.StubOutWithMock(company_helper, "select_primary_industry_id")
        self.mox.StubOutWithMock(company_helper, "update_company_competition_pairs")
        self.mox.StubOutWithMock(company_helper, "delete_industry_links")
        self.mox.StubOutWithMock(company_helper, "insert_new_industry_links")

        # start recording
        company_helper.select_primary_industry_id(company_id).AndReturn((current_primary_id, current_primary_name))
        company_helper.delete_industry_links(company_id, [current_primary_id], True, context)
        company_helper.insert_new_industry_links(company_id, [industry_id], True, context)
        company_helper.update_company_competition_pairs(company_id, context)

        # replay all
        self.mox.ReplayAll()

        company_helper.upsert_company_primary_industry(company_id, industry_id, context, "published")


    def test_upsert_company_primary_industry__needs_update_not_published(self):
        company_id = "taco express"
        industry_id = "mexican cuisine"
        current_primary_id = "asdf"
        current_primary_name = ";lkj"
        context = {}

        self.mox.StubOutWithMock(company_helper, "select_primary_industry_id")
        self.mox.StubOutWithMock(company_helper, "update_company_competition_pairs")
        self.mox.StubOutWithMock(company_helper, "delete_industry_links")
        self.mox.StubOutWithMock(company_helper, "insert_new_industry_links")

        # start recording
        company_helper.select_primary_industry_id(company_id).AndReturn((current_primary_id, current_primary_name))
        company_helper.delete_industry_links(company_id, [current_primary_id], True, context)
        company_helper.insert_new_industry_links(company_id, [industry_id], True, context)
        # does NOT call CCI update...

        # replay all
        self.mox.ReplayAll()

        company_helper.upsert_company_primary_industry(company_id, industry_id, context, "new")


    def test_publish_company_marks_needs_plan_b(self):

        # set up mock data
        mock_company_id = ObjectId()
        mock_primary_industry_id = ObjectId()
        mock_secondary_industries = ["chicken", "woot"]
        mock_company = { "name": "name", "type": "retail_banner","data": {"current": {"workflow": {"status": "give me a taco"}}} }
        extra_fields = ["data.workflow.current.status", "links.company.retailer_branding.entity_role_to"]

        # stub out various methods
        self.mox.StubOutWithMock(company_helper, "select_companies_by_id")
        self.mox.StubOutWithMock(company_helper, "upsert_company_primary_industry")
        self.mox.StubOutWithMock(company_helper, "upsert_company_secondary_industries")
        #self.mox.StubOutWithMock(geoprocessing_helper, 'evaluate_need_for_geoprocessing')
        self.mox.StubOutWithMock(pair_entity_helper, 'create_pair_entity_sync_task')
        self.mox.StubOutWithMock(company_helper, "mark_as_needs_plan_b")

        # start recording
        company_helper.select_companies_by_id([mock_company_id], self.context, additional_fields=extra_fields).AndReturn([mock_company])
        self.mock_main_access.mds.call_update_entity("company", mock_company_id, self.context, field_data = IsA(dict))
        company_helper.upsert_company_primary_industry(mock_company_id, mock_primary_industry_id, self.context, "published")
        company_helper.upsert_company_secondary_industries(mock_company_id, mock_secondary_industries, self.context)
        #geoprocessing_helper.evaluate_need_for_geoprocessing('company', mock_company_id, self.context)
        pair_entity_helper.create_pair_entity_sync_task('company', mock_company_id, self.context)

        # we expect this to run because we're publishing the company
        company_helper.mark_as_needs_plan_b([mock_company_id], self.context)

        # replay All
        self.mox.ReplayAll()

        # go!
        company_helper.update_company_fields(mock_company_id, "name", "retail_banner", "status", "ticker", "exchange", "published", 10, None, None,
                                             "description", [], mock_primary_industry_id, mock_secondary_industries, "false", self.context)


    def test_mark_as_needs_plan_b(self):

        # set up fake data
        company_ids = [ObjectId() for _ in range(3)]
        query = {
            "_id": {
                "$in": company_ids
            }
        }
        operations = {
            "$set": {
                "data.workflow.analytics.status": "needs_plan_b",
                "data.workflow.analytics.needs_plan_b_date": mox.IgnoreArg(),
                "data.workflow.analytics.run_id": None,
                "data.workflow.analytics.creation_time": None,
                "data.workflow.analytics.start_time": None,
                "data.workflow.analytics.end_time": None,
                "data.workflow.analytics.exception": None,
                "data.workflow.analytics.duration": None
            }
        }

        # start recording
        self.mock_main_access.mds.call_batch_update_entities("company", query, operations, self.context)

         # replay All
        self.mox.ReplayAll()

        # rocket, please go now!
        mark_as_needs_plan_b(company_ids, self.context)


    def test_change_workflow_status_sets_date(self):

        # set up mock data
        mock_company_id = ObjectId()
        mock_primary_industry_id = ObjectId()
        mock_secondary_industries = ["chicken", "woot"]
        mock_company = { "name": "name", "data": {"current": {"workflow": {"status": "give me a taco", "date": "yesterday"}}} }
        extra_fields = ["data.workflow.current.status", "links.company.retailer_branding.entity_role_to"]

        # this is the data rec that will be passed to call_update_entity
        new_company_data = {
            "name": "name",
            "data.type": "type",
            "data.status": "status",
            "data.ticker": "ticker",
            "data.exchange": "exchange",
            "data.workflow.current.status": "in_qc",
            "data.workflow.current.date": mox.IgnoreArg(),
            "data.closure_confirmation_threshold_days": 10,
            "data.opened_to": "Tuesday",
            "data.description": "description",
            "data.urls": [],
            "data.is_initialized_with_stores": False,
            "interval": ["Nineteen Dickety Two", "Tuesday"]
        }

        # stub out various methods
        self.mox.StubOutWithMock(company_helper, "select_companies_by_id")
        self.mox.StubOutWithMock(company_helper, "upsert_company_primary_industry")
        self.mox.StubOutWithMock(company_helper, "upsert_company_secondary_industries")
        #self.mox.StubOutWithMock(geoprocessing_helper, 'evaluate_need_for_geoprocessing')
        self.mox.StubOutWithMock(pair_entity_helper, 'create_pair_entity_sync_task')
        self.mox.StubOutWithMock(company_helper, "mark_as_needs_plan_b")
        self.mox.StubOutWithMock(company_helper, "normalize_start_date")
        self.mox.StubOutWithMock(company_helper, "normalize_end_date")

        # start recording
        company_helper.normalize_start_date(None).AndReturn("Nineteen Dickety Two")
        company_helper.normalize_end_date(None).AndReturn("Tuesday")
        company_helper.select_companies_by_id([mock_company_id], self.context, additional_fields=extra_fields).AndReturn([mock_company])
        self.mock_main_access.mds.call_update_entity("company", mock_company_id, self.context, field_data = new_company_data)
        company_helper.upsert_company_primary_industry(mock_company_id, mock_primary_industry_id, self.context, "in_qc")
        company_helper.upsert_company_secondary_industries(mock_company_id, mock_secondary_industries, self.context)
        #geoprocessing_helper.evaluate_need_for_geoprocessing('company', mock_company_id, self.context)
        pair_entity_helper.create_pair_entity_sync_task('company', mock_company_id, self.context)

        # replay All
        self.mox.ReplayAll()

        # go!
        company_helper.update_company_fields(mock_company_id, "name", "type", "status", "ticker", "exchange", "in_qc", 10, None, None,
                                             "description", [], mock_primary_industry_id, mock_secondary_industries, "false", self.context)


    def test_update_store_collection_dates(self):

        # set up mock data & inputs
        mock_company_id1 = ObjectId() # with strings, opens 1 store on the same date as files
        mock_company_id2 = ObjectId() # with dates, closes 2 stores after file dates
        mock_company_id3 = ObjectId() # no file dates, only store open/close dates
        mock_company_id4 = ObjectId() # no file dates, no store dates
        mock_company_ids = [mock_company_id1, mock_company_id2, mock_company_id3, mock_company_id4]

        file_pipeline = [
            {
                "$match": {
                    "data.company_id": {"$in": map(str, mock_company_ids)},
                    "data.type": "retail_input_file"
                }
            },
            {
                "$group": {
                    "_id": {"banner_id": "$data.company_id", "file_as_of_date": "$data.as_of_date"},
                    "num_records": {"$sum": "$data.num_records"}
                }
            },
            {
                "$sort": {
                    "_id.banner_id": 1,
                    "_id.file_as_of_date": -1
                }
            }
        ]
        file_results = [
            {
                "_id": {
                    "banner_id": str(mock_company_id1),
                    "file_as_of_date": "2013-03-13T00:00:00"
                },
                "num_records": 133
            },
            {
                "_id": {
                    "banner_id": str(mock_company_id1),
                    "file_as_of_date": "2012-02-12T00:00:00"
                },
                "num_records": 132
            },
            {
                "_id": {
                    "banner_id": str(mock_company_id2),
                    "file_as_of_date": datetime.datetime(2013, 11, 2)
                },
                "num_records": 5
            },
            {
                "_id": {
                    "banner_id": str(mock_company_id2),
                    "file_as_of_date": datetime.datetime(2012, 10, 24)
                },
                "num_records": 7
            }
        ]

        store_pipeline = [
            {
            "$match": {
                "links.company.store_ownership.entity_id_to": {"$in": mock_company_ids}
            }
            },
            {
                "$unwind": "$links.company.store_ownership"
            },
            {
                "$match": {"links.company.store_ownership.entity_role_to": "retail_parent"}
            },
            {
                "$unwind": "$interval"
            },
            {
                "$group": {
                    "_id": {"banner_id": "$links.company.store_ownership.entity_id_to", "date": "$interval"},
                    "num_stores": {"$sum": 1}
                }
            },
            {
                "$match": {"_id.date": {"$ne": None}}
            },
            {
                "$sort": {
                    "_id.banner_id": 1,
                    "_id.date": -1
                }
            }
        ]
        store_results = [
            {
                "_id": {
                    "banner_id": mock_company_id1,
                    "date": "2013-03-13T00:00:00" # 1 store opened on this date
                },
                "num_stores": 1
            },
            {
                "_id": {
                    "banner_id": mock_company_id2,
                    "date": datetime.datetime(2013, 11, 17) # 2 stores closed on this date
                },
                "num_stores": 2
            },
            {
                "_id": {
                    "banner_id": mock_company_id3,
                    "date": datetime.datetime(2014, 4, 9) # 8 stores opened or closed on this date
                },
                "num_stores": 8
            },
            {
                "_id": {
                    "banner_id": mock_company_id3,
                    "date": datetime.datetime(2013, 8, 1) # 12 stores opened or closed on this date
                },
                "num_stores": 12
            }
        ]

        company1_update = {
            "data.collection.dates.stores": [datetime.datetime(2013, 3, 13), datetime.datetime(2012, 2, 12)]
        }
        company2_update = {
            "data.collection.dates.stores": [datetime.datetime(2013, 11, 17), datetime.datetime(2013, 11, 2), datetime.datetime(2012, 10, 24)]
        }
        company3_update = {
            "data.collection.dates.stores": [datetime.datetime(2014, 4, 9), datetime.datetime(2013, 8, 1)]
        }
        company4_update = {
            "data.collection.dates.stores": []
        }

        # start recording
        self.mock_main_access.mds.call_aggregate_entities("file", file_pipeline, context=self.context).AndReturn(file_results)
        self.mock_main_access.mds.call_aggregate_entities("store", store_pipeline, context=self.context).AndReturn(store_results)
        self.mock_main_access.mds.call_update_entity("company", mock_company_id1, self.context, field_data=company1_update, use_new_json_encoder=True)
        self.mock_main_access.mds.call_update_entity("company", mock_company_id2, self.context, field_data=company2_update, use_new_json_encoder=True)
        self.mock_main_access.mds.call_update_entity("company", mock_company_id3, self.context, field_data=company3_update, use_new_json_encoder=True)
        self.mock_main_access.mds.call_update_entity("company", mock_company_id4, self.context, field_data=company4_update, use_new_json_encoder=True)

        # replay All
        self.mox.ReplayAll()

        # go!
        company_helper.update_store_collection_dates(mock_company_ids, None, self.context)

    def test_get_company_family__include_unpublished_banners(self):

        # set up mock data
        mock_company_id = ObjectId()
        mock_hierarchy = {
            "entities": {
                "parent_id": ["parent_id", "retail_parent", "published"],
                "banner_id_1": ["banner_id_1", "retail_banner", "published"],
                "banner_id_2": ["banner_id_2", "retail_banner", "published"],
                "banner_id_3": ["banner_id_3", "retail_banner", "new"]
            }
        }

        # use real params builder to make params
        fields = ["_id", "data.type", "data.workflow.current.status"]
        root_query = {
            "_id": mock_company_id
        }
        link_filters = [
            ["retail_parent", "retail_segment", "retailer_branding"]
        ]
        main_param = Dependency("CoreAPIParamsBuilder").value
        params = main_param.mds.create_params(resource="find_entity_hierarchy", entity_fields=fields,
                                              link_filters=link_filters, root_query=root_query)["params"]

        # start recording
        self.mock_main_access.mds.call_find_entity_hierarchy("company", params, self.context).AndReturn(mock_hierarchy)

        # replay All
        self.mox.ReplayAll()

        # go!
        banner_ids, parent_id = company_helper.get_company_family(mock_company_id, self.context, published_banners_only=False)

        self.assertEqual(parent_id, "parent_id")
        self.assertEqual(sorted(banner_ids), ["banner_id_1", "banner_id_2", "banner_id_3"])

    def test_get_company_family__only_published_banners(self):

        # set up mock data
        mock_company_id = ObjectId()
        mock_hierarchy = {
            "entities": {
                "parent_id": ["parent_id", "retail_parent", "published"],
                "banner_id_1": ["banner_id_1", "retail_banner", "published"],
                "banner_id_2": ["banner_id_2", "retail_banner", "published"],
                "banner_id_3": ["banner_id_3", "retail_banner", "new"]
            }
        }

        # use real params builder to make params
        fields = ["_id", "data.type", "data.workflow.current.status"]
        root_query = {
            "_id": mock_company_id
        }
        link_filters = [
            ["retail_parent", "retail_segment", "retailer_branding"]
        ]
        main_param = Dependency("CoreAPIParamsBuilder").value
        params = main_param.mds.create_params(resource="find_entity_hierarchy", entity_fields=fields,
                                              link_filters=link_filters, root_query=root_query)["params"]

        # start recording
        self.mock_main_access.mds.call_find_entity_hierarchy("company", params, self.context).AndReturn(mock_hierarchy)

        # replay All
        self.mox.ReplayAll()

        # go!
        banner_ids, parent_id = company_helper.get_company_family(mock_company_id, self.context, published_banners_only=True)

        self.assertEqual(parent_id, "parent_id")
        self.assertEqual(sorted(banner_ids), ["banner_id_1", "banner_id_2"])

    def test_get_company_family__no_parent(self):

        # set up mock data
        mock_company_id = ObjectId()
        mock_hierarchy = {
            "entities": {
                "banner_id_1": ["banner_id_1", "retail_banner", "published"]
            }
        }

        # use real params builder to make params
        fields = ["_id", "data.type", "data.workflow.current.status"]
        root_query = {
            "_id": mock_company_id
        }
        link_filters = [
            ["retail_parent", "retail_segment", "retailer_branding"]
        ]
        main_param = Dependency("CoreAPIParamsBuilder").value
        params = main_param.mds.create_params(resource="find_entity_hierarchy", entity_fields=fields,
                                              link_filters=link_filters, root_query=root_query)["params"]

        # start recording
        self.mock_main_access.mds.call_find_entity_hierarchy("company", params, self.context).AndReturn(mock_hierarchy)

        # replay All
        self.mox.ReplayAll()

        # go!
        banner_ids, parent_id = company_helper.get_company_family(mock_company_id, self.context, published_banners_only=True)

        self.assertIsNone(parent_id)
        self.assertEqual(sorted(banner_ids), ["banner_id_1"])

    def test_get_published_banner_ids__not_operating_only(self):

        # set up mock data
        mock_banners = {"banner_id_1", "banner_id_2", "banner_id_3"}

        query = {
            "data.type": "retail_banner",
            "data.workflow.current.status": "published"
        }

        # start recording
        self.mock_main_access.mds.call_distinct_field_values("company", "_id", query=query, context=self.context, timeout=120).AndReturn(mock_banners)

        # replay All
        self.mox.ReplayAll()

        # go!
        banner_ids = company_helper.get_published_banner_ids(self.context, operating_only=False)

        self.assertEqual(banner_ids, mock_banners)

    def test_get_published_banner_ids__operating_only(self):

        # set up mock data
        mock_banners = {"banner_id_1", "banner_id_2", "banner_id_3"}

        query = {
            "data.type": "retail_banner",
            "data.workflow.current.status": "published",
            "data.status": "operating"
        }

        # start recording
        self.mock_main_access.mds.call_distinct_field_values("company", "_id", query=query, context=self.context, timeout=120).AndReturn(mock_banners)

        # replay All
        self.mox.ReplayAll()

        # go!
        banner_ids = company_helper.get_published_banner_ids(self.context, operating_only=True)

        self.assertEqual(banner_ids, mock_banners)

    def test_get_published_banner_ids__specific_banners(self):

        # set up mock data
        mock_banners = {ObjectId(), ObjectId(), ObjectId()}

        query = {
            "data.type": "retail_banner",
            "data.workflow.current.status": "published",
            "data.status": "operating",
            "_id": {"$in": list(mock_banners)}
        }

        # start recording
        self.mock_main_access.mds.call_distinct_field_values("company", "_id", query=query, context=self.context, timeout=120).AndReturn(mock_banners)

        # replay All
        self.mox.ReplayAll()

        # go!
        banner_ids = company_helper.get_published_banner_ids(self.context, operating_only=True, banner_ids=mock_banners)

        self.assertEqual(sorted(banner_ids), sorted(mock_banners))

    def test_get_families_and_orphans__published_operating(self):

        # set up mock data... 1st 2 banners are children of the parent, 3rd is an orphan
        mock_banners = [ObjectId(), ObjectId(), ObjectId()]
        mock_parent = ObjectId()

        # stub out various methods
        self.mox.StubOutWithMock(company_helper, "get_published_banner_ids")
        self.mox.StubOutWithMock(company_helper, "get_company_family")

        # use real params builder to make params
        query = {
            "data.type": "retail_banner",
            "data.workflow.current.status": "published",
            "data.status": "operating",
            "_id": {"$in": mock_banners}
        }

        # start recording
        company_helper.get_published_banner_ids(self.context, operating_only=True, banner_ids=None).AndReturn(mock_banners)
        company_helper.get_company_family(mock_banners[0], self.context, published_banners_only=True).AndReturn((mock_banners[:2], mock_parent))
        company_helper.get_company_family(mock_banners[1], self.context, published_banners_only=True).AndReturn((mock_banners[:2], mock_parent))
        company_helper.get_company_family(mock_banners[2], self.context, published_banners_only=True).AndReturn(([mock_banners[2]], None))

        # replay All
        self.mox.ReplayAll()

        # go!
        families, orphans = company_helper.get_families_and_orphans(self.context, published_banners_only=True, operating_only=True, banner_ids=None)

        self.assertEqual(families, {mock_parent: mock_banners[:2]})
        self.assertEqual(orphans, {mock_banners[2]})

if __name__ == '__main__':
    unittest.main()
