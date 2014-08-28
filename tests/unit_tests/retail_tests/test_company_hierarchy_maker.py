import datetime
from core.common.business_logic.service_entity_logic.company_hierarchy_maker import CompanyHierarchyMaker
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from bson.objectid import ObjectId
import mox


__author__ = 'vgold'


class CompanyHierarchyMakerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(CompanyHierarchyMakerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get several dependencies that we'll need in the class
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # Set mock attributes on WorkflowService instance for calls to record
        self.mock = self.mox.CreateMock(CompanyHierarchyMaker)
        self.mock.main_access = self.mox.CreateMockAnything()
        self.mock.main_access.mds = self.mox.CreateMockAnything()
        self.mock.main_param = self.mox.CreateMockAnything()
        self.mock.main_param.mds = self.mox.CreateMockAnything()

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.mock.cfg = Dependency("MoxConfig").value
        self.mock.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_company_hierarchy_maker.py"}

        self.mock.context = self.context

    def doCleanups(self):

        super(CompanyHierarchyMakerTests, self).doCleanups()
        dependencies.clear()

    ##########################################################################
    # CompanyHierarchyMaker._get_company_family_id_list()

    def test_get_company_family_id_list__banner(self):

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)

        company_hierarchy_maker.company_id = self.__get_banner_company_id()
        company_hierarchy_maker.family_companies = self.__make_family_companies_dict()
        company_hierarchy_maker.parent_to_children_dict = self.__make_parent_to_children_dict()
        company_hierarchy_maker.child_to_parents_dict = self.__make_child_to_parent_dict()

        result = company_hierarchy_maker._get_company_family_id_list()

        self.assertEqual(result, company_hierarchy_maker)

        self.assertSetEqual(set(company_hierarchy_maker.family_list), set(self.__make_family_list()))

        self.assertDictEqual(company_hierarchy_maker.parents_dict,
                             self.__make_parents_dict())

        self.assertListEqual(sorted(company_hierarchy_maker.parents),
                             sorted(self.__make_parents_dict().values()))

        self.assertDictEqual(company_hierarchy_maker.secondary_parents_dict,
                             self.__make_secondary_parents_dict())

        self.assertListEqual(sorted(company_hierarchy_maker.secondary_parents),
                             sorted(self.__make_secondary_parents_dict().values()))

        self.assertDictEqual(company_hierarchy_maker.banners_dict,
                             self.__make_banners_dict())

        self.assertListEqual(sorted(company_hierarchy_maker.banners),
                             sorted(self.__make_banners_dict().values()))

        self.assertDictEqual(company_hierarchy_maker.secondary_banners_dict,
                             self.__make_secondary_banners_dict())

        self.assertListEqual(sorted(company_hierarchy_maker.secondary_banners),
                             sorted(self.__make_secondary_banners_dict().values()))

        self.assertDictEqual(company_hierarchy_maker.cooperatives_dict,
                             self.__make_cooperatives_dict())

        self.assertListEqual(sorted(company_hierarchy_maker.cooperatives),
                             sorted(self.__make_cooperatives_dict().values()))

        self.assertDictEqual(company_hierarchy_maker.owners_dict,
                             self.__make_owners_dict())

        self.assertListEqual(sorted(company_hierarchy_maker.owners),
                             sorted(self.__make_owners_dict().values()))

    ##########################################################################
    # CompanyHierarchyMaker._create_descendant_list()

    def test_create_descendant_list__banner(self):

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)

        company_hierarchy_maker.company_id = self.__get_banner_company_id()
        company_hierarchy_maker.parent_to_children_dict = self.__make_parent_to_children_dict()

        result = company_hierarchy_maker._create_descendant_list()

        self.assertEqual(result, company_hierarchy_maker)
        self.assertListEqual(sorted(company_hierarchy_maker.descendants), sorted(self.__make_banner_descendants()))

    def test_create_descendant_list__parent(self):

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)

        company_hierarchy_maker.company_id = self.__get_parent_company_id()
        company_hierarchy_maker.parent_to_children_dict = self.__make_parent_to_children_dict()

        result = company_hierarchy_maker._create_descendant_list()

        self.assertEqual(result, company_hierarchy_maker)
        self.assertListEqual(sorted(company_hierarchy_maker.descendants), sorted(self.__make_parent_descendants()))

    def test_create_descendant_list__owner(self):

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)

        company_hierarchy_maker.company_id = self.__get_owner_company_id()
        company_hierarchy_maker.parent_to_children_dict = self.__make_parent_to_children_dict()

        result = company_hierarchy_maker._create_descendant_list()

        self.assertEqual(result, company_hierarchy_maker)
        self.assertListEqual(sorted(company_hierarchy_maker.descendants), sorted(self.__make_owner_descendants()))

    ##########################################################################
    # CompanyHierarchyMaker._get_industries_for_company_family()

    def test_get_industries_for_company_family(self):

        params = "params"
        self.mock.main_param.mds.create_params(resource = "find_entities_raw", origin = "_get_industries_for_company_family",
                                               entity_fields = mox.IgnoreArg(), query = mox.IgnoreArg(), as_list = True).AndReturn({"params": params})

        industry_rows = [["1", "2", "3", "4", "5"]]
        self.mock.main_access.mds.call_find_entities_raw("industry", params = params, context = self.context).AndReturn(industry_rows)

        self.mox.ReplayAll()

        self.mock.family_oid_list = "family_oid_list"
        result = CompanyHierarchyMaker._get_industries_for_company_family(self.mock)

        self.assertEqual(result, self.mock)
        self.assertEqual(industry_rows, self.mock.industry_rows)

    ##########################################################################
    # CompanyHierarchyMaker._fill_industries_into_companies()

    def test_fill_industries_into_companies(self):

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)

        company_hierarchy_maker.company_id = self.__get_banner_company_id()
        company_hierarchy_maker.target_company = {}
        company_hierarchy_maker.parents_dict = self.__make_parents_dict()
        company_hierarchy_maker.secondary_parents_dict = self.__make_secondary_parents_dict()
        company_hierarchy_maker.banners_dict = self.__make_banners_dict()
        company_hierarchy_maker.secondary_banners_dict = self.__make_secondary_banners_dict()
        company_hierarchy_maker.cooperatives_dict = self.__make_cooperatives_dict()
        company_hierarchy_maker.owners_dict = self.__make_owners_dict()
        company_hierarchy_maker.industry_rows = self.__make_industry_rows()

        result = company_hierarchy_maker._fill_industries_into_companies()

        self.assertEqual(result, company_hierarchy_maker)

        self.assertDictEqual(company_hierarchy_maker.target_company["primary_industry"],
                             self.__make_target_company_primary_industry_dict())

        self.assertDictEqual(company_hierarchy_maker.parents_dict,
                             self.__make_parents_dict_with_industries())

        self.assertDictEqual(company_hierarchy_maker.banners_dict,
                             self.__make_banners_dict_with_industries())

        self.assertDictEqual(company_hierarchy_maker.cooperatives_dict,
                             self.__make_cooperatives_dict_with_industries())

        self.assertDictEqual(company_hierarchy_maker.owners_dict,
                             self.__make_owners_dict_with_industries())

    ##########################################################################
    # CompanyHierarchyMaker._check_if_competing_industries_are_published()

    def test_check_if_competing_industries_are_published__all_true(self):

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)
        company_hierarchy_maker.context = self.context
        industry_id = ObjectId()
        company_hierarchy_maker.target_company = {
            "primary_industry": {
                "id": industry_id
            }
        }
        company_hierarchy_maker.industry_helper = self.mox.CreateMockAnything()
        competing_industries = [["1", {"publish_competition_for_banners": True}],
                                ["2", {"publish_competition_for_banners": True}]]
        company_hierarchy_maker.industry_helper.get_competing_industries([industry_id],
                                                                         self.context).AndReturn(competing_industries)

        self.mox.ReplayAll()

        company_hierarchy_maker._check_if_competing_industries_are_published()
        self.assertTrue(company_hierarchy_maker.all_competing_industries_published)
        self.assertTrue(company_hierarchy_maker.any_competing_industries_published)

    def test_check_if_competing_industries_are_published__true_false(self):

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)
        company_hierarchy_maker.context = self.context
        industry_id = ObjectId()
        company_hierarchy_maker.target_company = {
            "primary_industry": {
                "id": industry_id
            }
        }
        company_hierarchy_maker.industry_helper = self.mox.CreateMockAnything()
        competing_industries = [["1", {"publish_competition_for_banners": True}],
                                ["2", {"publish_competition_for_banners": False}]]
        company_hierarchy_maker.industry_helper.get_competing_industries([industry_id],
                                                                         self.context).AndReturn(competing_industries)

        self.mox.ReplayAll()

        company_hierarchy_maker._check_if_competing_industries_are_published()
        self.assertFalse(company_hierarchy_maker.all_competing_industries_published)
        self.assertTrue(company_hierarchy_maker.any_competing_industries_published)

    def test_check_if_competing_industries_are_published__all_false(self):

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)
        company_hierarchy_maker.context = self.context
        industry_id = ObjectId()
        company_hierarchy_maker.target_company = {
            "primary_industry": {
                "id": industry_id
            }
        }
        company_hierarchy_maker.industry_helper = self.mox.CreateMockAnything()
        competing_industries = [["1", {"publish_competition_for_banners": False}],
                                ["2", {"publish_competition_for_banners": False}]]
        company_hierarchy_maker.industry_helper.get_competing_industries([industry_id],
                                                                         self.context).AndReturn(competing_industries)

        self.mox.ReplayAll()

        company_hierarchy_maker._check_if_competing_industries_are_published()
        self.assertFalse(company_hierarchy_maker.all_competing_industries_published)
        self.assertFalse(company_hierarchy_maker.any_competing_industries_published)

    ##########################################################################
    # CompanyHierarchyMaker._add_company_data_to_hierarchy()

    def test_add_company_data_to_hierarchy(self):
        self.maxDiff = None

        company_hierarchy_maker = CompanyHierarchyMaker.__new__(CompanyHierarchyMaker)

        company_hierarchy_maker.company_id = self.__get_banner_company_id()
        company_hierarchy_maker.target_company = {}

        company_hierarchy_maker.parents_dict = self.__make_parents_dict()
        company_hierarchy_maker.secondary_parents_dict = {}
        company_hierarchy_maker.banners_dict = self.__make_banners_dict()
        company_hierarchy_maker.secondary_banners_dict = {}
        company_hierarchy_maker.cooperatives_dict = self.__make_cooperatives_dict()
        company_hierarchy_maker.owners_dict = self.__make_owners_dict()

        company_hierarchy_maker.family_companies = self.__make_family_companies_dict()

        result = company_hierarchy_maker._add_company_data_to_hierarchy()

        self.assertEqual(result, company_hierarchy_maker)

        self.assertDictEqual(company_hierarchy_maker.parents_dict,
                             self.__make_parents_dict_with_company_data())

        self.assertDictEqual(company_hierarchy_maker.target_company,
                             self.__make_target_company_with_company_data())

        self.assertDictEqual(company_hierarchy_maker.banners_dict,
                             self.__make_banners_dict_with_company_data())

        self.assertDictEqual(company_hierarchy_maker.cooperatives_dict,
                             self.__make_cooperatives_dict_with_company_data())

        self.assertDictEqual(company_hierarchy_maker.owners_dict,
                             self.__make_owners_dict_with_company_data())

    #---------------------------# Private Helper Methods #---------------------------#

    @staticmethod
    def __make_family_companies_dict():
        return {
            1: [1, "a", "a", "a", "a", "a", "retail_parent", None, "published", {"analytics": True}, {"start": datetime.datetime(2011,1,1), "end": datetime.datetime(2013,12,31)}, [datetime.datetime(2013,7,8), datetime.datetime(2013,9,19)]],
            2: [2, "b", "b", "b", "b", "b", "retailer_cooperative", None, "published", {"analytics": True}, None],
            3: [3, "c", "c", "c", "c", "c", "retail_parent", None, "published", {"analytics": True}, {"start": datetime.datetime(2011,1,1), "end": datetime.datetime(2013,12,31)}, [datetime.datetime(2013,7,8), datetime.datetime(2013,9,19)]],
            4: [4, "c", "c", "c", "c", "c", "retail_parent", None, "published", {"analytics": True}, {"start": datetime.datetime(2011,1,1), "end": datetime.datetime(2013,12,31)}, [datetime.datetime(2013,7,8), datetime.datetime(2013,9,19)]],
            7: [7, "g", "g", "g", "g", "g", "retailer_cooperative", None, "published", {"analytics": True}, None, None],
            8: [8, "h", "h", "h", "h", "h", "retail_owner", None, "published", {"analytics": True}, None, None],
            9: [9, "i", "i", "i", "i", "i", "retail_parent", None, "published", {"analytics": True}, {"start": datetime.datetime(2011,1,1), "end": datetime.datetime(2013,12,31)}, [datetime.datetime(2013,7,8), datetime.datetime(2013,9,19)]],
            11: [11, "aa", "aa", "aa", "aa", "aa", "retail_banner", None, "published", {"analytics": True}, {"start": datetime.datetime(2011,1,1), "end": datetime.datetime(2013,12,31)}, [datetime.datetime(2013,7,8), datetime.datetime(2013,9,19)]],
            12: [12, "ab", "ab", "ab", "ab", "ab", "retail_banner", None, "published", {"analytics": True}, {"start": datetime.datetime(2011,1,1), "end": datetime.datetime(2013,12,31)}, [datetime.datetime(2013,7,8), datetime.datetime(2013,9,19)]],
            23: [23, "bc", "bc", "bc", "bc", "bc", "retail_banner", [{"url": "url", "url_type": "Main Site"}], "published", {"analytics": True}, {"start": datetime.datetime(2011,1,1), "end": datetime.datetime(2013,12,31)}, [datetime.datetime(2013,7,8), datetime.datetime(2013,9,19)]],
            34: [34, "cd", "cd", "cd", "cd", "cd", "retail_banner", None, "published", {"analytics": True}, {"start": datetime.datetime(2011,1,1), "end": datetime.datetime(2013,12,31)}, [datetime.datetime(2013,7,8), datetime.datetime(2013,9,19)]]
        }

    @staticmethod
    def __make_parent_to_children_dict():
        return {
            1: {
                11: {"_id": 11, "entity_role_from": "retail_parent", "entity_role_to": "retail_segment"},
                12: {"_id": 12, "entity_role_from": "retail_parent", "entity_role_to": "retail_segment"}
            },
            2: {
                12: {"_id": 12, "entity_role_from": "retail_parent", "entity_role_to": "retail_segment"},
                23: {"_id": 23, "entity_role_from": "retail_parent", "entity_role_to": "retail_segment"}
            },
            3: {
                23: {"_id": 23, "entity_role_from": "retail_parent", "entity_role_to": "retail_segment"},
                34: {"_id": 34, "entity_role_from": "retail_parent", "entity_role_to": "retail_segment"}
            },
            4: {
                23: {"_id": 23, "entity_role_from": "secondary_parent", "entity_role_to": "secondary_banner"}
            },
            7: {
                34: {"_id": 34, "entity_role_from": "cooperative_parent_non_owner", "entity_role_to": "cooperative_member_non_owner"}
            },
            8: {
                2: {"_id": 2, "entity_role_from": "investment_firm", "entity_role_to": "portfolio_company"}
            },
            9: {
                3: {"_id": 3, "entity_role_from": "investor", "entity_role_to": "investment"}
            }
        }

    @staticmethod
    def __make_child_to_parent_dict():
        return {
            11: {1: {"_id": 1, "entity_role_from": "retail_segment", "entity_role_to": "retail_parent"}},
            12: {1: {"_id": 1, "entity_role_from": "retail_segment", "entity_role_to": "retail_parent"},
                 2: {"_id": 2, "entity_role_from": "retail_segment", "entity_role_to": "retail_parent"}},
            23: {2: {"_id": 2, "entity_role_from": "retail_segment", "entity_role_to": "retail_parent"},
                 3: {"_id": 3, "entity_role_from": "retail_segment", "entity_role_to": "retail_parent"},
                 4: {"_id": 4, "entity_role_from": "secondary_banner", "entity_role_to": "secondary_parent"},
                 7: {"_id": 7, "entity_role_from": "cooperative_member_non_owner", "entity_role_to": "cooperative_parent_non_owner"}},
            34: {3: {"_id": 3, "entity_role_from": "retail_segment", "entity_role_to": "retail_parent"}},
            2: {8: {"_id": 8, "entity_role_from": "portfolio_company", "entity_role_to": "investment_firm"}},
            3: {9: {"_id": 9, "entity_role_from": "investment", "entity_role_to": "investor"}}
        }

    @staticmethod
    def __get_banner_company_id():
        return 23

    @staticmethod
    def __get_parent_company_id():
        return 1

    @staticmethod
    def __get_owner_company_id():
        return 8

    @staticmethod
    def __make_banner_descendants():
        return [23]

    @staticmethod
    def __make_parent_descendants():
        return [1, 11, 12]

    @staticmethod
    def __make_owner_descendants():
        return [8, 2, 12, 23]

    @staticmethod
    def __make_family_list():
        return [2, 3, 4, 7, 8, 12, 23, 34]

    @staticmethod
    def __make_parents_dict():
        return {
            2: {"id": 2, "primary_industry": None},
            3: {"id": 3, "primary_industry": None}
        }

    @staticmethod
    def __make_secondary_parents_dict():
        return {
            4: {"id": 4, "primary_industry": None}
        }

    @staticmethod
    def __make_owners_dict():
        return {
            8: {"id": 8, "primary_industry": None}
        }

    @staticmethod
    def __make_banners_dict():
        return {
            12: {"id": 12, "primary_industry": None},
            23: {"id": 23, "primary_industry": None},
            34: {"id": 34, "primary_industry": None}
        }

    @staticmethod
    def __make_secondary_banners_dict():
        return {}

    @staticmethod
    def __make_cooperatives_dict():
        return {
            7: {"id": 7, "primary_industry": None}
        }

    @classmethod
    def __make_parents_dict_with_industries(cls):
        d = cls.__make_parents_dict()
        for ind in cls.__make_industry_rows():
            if ind[4] in d:
                d[ind[4]]["primary_industry"] = cls.__make_industry_dict_from_industry_row(ind)
        return d

    @classmethod
    def __make_parents_dict_with_company_data(cls):
        d = cls.__make_parents_dict()
        for cid, co in cls.__make_family_companies_dict().iteritems():
            if co[0] in d:
                d[co[0]] = cls.__make_company_dict_from_company_row(co)
        return d

    @classmethod
    def __make_banners_dict_with_industries(cls):
        d = cls.__make_banners_dict()
        for ind in cls.__make_industry_rows():
            if ind[4] in d:
                d[ind[4]]["primary_industry"] = cls.__make_industry_dict_from_industry_row(ind)
        return d

    @classmethod
    def __make_banners_dict_with_company_data(cls):
        d = cls.__make_banners_dict()
        for cid, co in cls.__make_family_companies_dict().iteritems():
            if co[0] in d:
                d[co[0]] = cls.__make_banner_dict_from_company_row(co)
        return d

    @classmethod
    def __make_cooperatives_dict_with_industries(cls):
        d = cls.__make_cooperatives_dict()
        for ind in cls.__make_industry_rows():
            if ind[4] in d:
                d[ind[4]]["primary_industry"] = cls.__make_industry_dict_from_industry_row(ind)
        return d

    @classmethod
    def __make_cooperatives_dict_with_company_data(cls):
        d = cls.__make_cooperatives_dict()
        for cid, co in cls.__make_family_companies_dict().iteritems():
            if co[0] in d:
                d[co[0]] = cls.__make_company_dict_from_company_row(co)
        return d

    @classmethod
    def __make_owners_dict_with_industries(cls):
        d = cls.__make_owners_dict()
        for ind in cls.__make_industry_rows():
            if ind[4] in d:
                d[ind[4]]["primary_industry"] = cls.__make_industry_dict_from_industry_row(ind)
        return d

    @classmethod
    def __make_owners_dict_with_company_data(cls):
        d = cls.__make_owners_dict()
        for cid, co in cls.__make_family_companies_dict().iteritems():
            if co[0] in d:
                d[co[0]] = cls.__make_company_dict_from_company_row(co)
        return d

    @staticmethod
    def __make_industry_dict_from_industry_row(ind):
        return {
            "id": ind[0],
            "name": ind[3],
            "label": "%s %s" % (ind[1], ind[2]),
            "publish_competition_for_banners": ind[5]
        }

    @staticmethod
    def __make_company_dict_from_company_row(co):
        return {
            "id": co[0],
            "name": co[1],
            "ticker": co[2],
            "exchange": co[3],
            "primary_industry": None,
            "published": co[8] == "published"
        }

    @staticmethod
    def __make_banner_dict_from_company_row(co):
        return {
            "id": co[0],
            "name": co[1],
            "ticker": co[2],
            "exchange": co[3],
            "primary_industry": None,
            "published": co[8] == "published",
            "store_collection_dates": co[11]
        }

    @staticmethod
    def __make_industry_rows():
        return [
            ["a", "a", "a", "a", True, [{"entity_id_to": 1, "entity_role_to": "primary_industry_classification"}]],
            ["ba", "ba", "ba", "ba", False, [{"entity_id_to": 11, "entity_role_to": "primary_industry_classification"}]],
            ["bb", "bb", "bb", "bb", True, [{"entity_id_to": 12, "entity_role_to": "primary_industry_classification"}]],
            ["bc", "bc", "bc", "bc", False, [{"entity_id_to": 23, "entity_role_to": "primary_industry_classification"}]],
            ["b", "b", "b", "b", True, [{"entity_id_to": 2, "entity_role_to": "primary_industry_classification"}]],
            ["h", "h", "h", "h", False, [{"entity_id_to": 8, "entity_role_to": "primary_industry_classification"}]],
            ["i", "i", "i", "i", True, [{"entity_id_to": 9, "entity_role_to": "primary_industry_classification"}]]
        ]

    @staticmethod
    def __make_target_company_primary_industry_dict():
        return {
            "id": "bc",
            "name": "bc",
            "label": "bc bc",
            "publish_competition_for_banners": False
        }

    @classmethod
    def __make_target_company_with_company_data(cls):
        return {
            "name": "bc",
            "ticker": "bc",
            "exchange": "bc",
            "status": "bc",
            "description": "bc",
            "type": "retail_banner",
            "main_site_url": "url",
            "published": True,
            "valid": {
                "analytics": True,
                "v1_2": {
                    "analytics": {
                        "stores": False,
                        "competition": False,
                        "demographics": False,
                        "monopolies": False,
                        "economics": False,
                        "white_space": False,
                        "competitor_summary": False
                    }
                }
            },
            "analytics_dates": {
                "start": datetime.datetime(2011,1,1),
                "end": datetime.datetime(2013,12,31)
            },
            "store_collection_dates": [datetime.datetime(2013, 7, 8, 0, 0),
                                       datetime.datetime(2013, 9, 19, 0, 0)]
        }
