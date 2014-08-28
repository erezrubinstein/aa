from common.utilities.misc_utilities import convert_entity_list_to_dictionary
from core.common.business_logic.service_entity_logic import company_helper, industry_helper
from core.common.business_logic.service_entity_logic.industry_helper_clean import select_industry_names_by_ids
from core.common.utilities.helpers import ensure_id
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_industry, insert_test_company, insert_test_industry_competition


__author__ = 'erezrubinstein'


class IndustryHelperTestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "main_export_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):
        # delete when starting
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    def test_get_industry_names_by_ids(self):

        # create three industries
        industry_id1 = ensure_id(insert_test_industry("test1"))
        industry_id2 = ensure_id(insert_test_industry("test2"))
        industry_id3 = ensure_id(insert_test_industry("test3"))

        # select two industries by their ids
        industries = select_industry_names_by_ids([industry_id1, industry_id2])

        # verify that they match
        industries = convert_entity_list_to_dictionary(industries)
        self.test_case.assertEqual(industries, {
            industry_id1: {
                "_id": industry_id1,
                "name": "test1"
            },
            industry_id2: {
                "_id": industry_id2,
                "name": "test2"
            }
        })

    def test_get_company_ids_by_primary_industry_id__no_companies(self):

        industry_id_1 = insert_test_industry(name='name')
        company_ids = industry_helper.get_company_ids_by_primary_industry_id(industry_id_1)
        self.test_case.assertEqual(0, len(company_ids))

    def test_get_company_ids_by_primary_industry_id(self):

        context = {
            'user_id': 42,
            'source': 'test_get_company_ids_by_primary_industry_id'
        }

        industry_id_1 = insert_test_industry(name='name')
        company_id_1 = insert_test_company(name='name')
        company_id_2 = insert_test_company(name='name')
        company_id_3 = insert_test_company(name='name')

        company_helper.insert_new_industry_links(company_id_1, [industry_id_1], True, context)
        company_helper.insert_new_industry_links(company_id_2, [industry_id_1], True, context)
        company_helper.insert_new_industry_links(company_id_3, [industry_id_1], True, context)

        company_ids = industry_helper.get_company_ids_by_primary_industry_id(industry_id_1)

        self.test_case.assertEqual(3, len(company_ids))
        self.test_case.assertEqual({company_id_1, company_id_2, company_id_3}, set(company_ids))

    def test_get_competing_industries(self):

        industry_id1 = ensure_id(insert_test_industry("test1"))
        industry_id2 = ensure_id(insert_test_industry("test2"))
        insert_test_industry_competition(industry_id1, industry_id2)

        competing_industries = industry_helper.get_competing_industries([industry_id1], self.context)

        self.test_case.assertEqual(competing_industries, [[industry_id2, {"chicken": "woot"}]])

    def test_structure_new_industry(self):

        # root industry
        datas = {
            "industry_code":"990001",
            "industry_level": 5,
            "source_vendor": "NAICS",
            "source_version": 2007
        }
        industry_id1 = insert_test_industry("Flying Saucers", data=datas)

        args = {
            "parent_entity_id": industry_id1,
            "parent_entity_source_id": "990001",
            "add_entity_new_name": "Flying Saucers, Broadline"
        }

        new_industry_rec = industry_helper.structure_new_industry(args, self.context)

        expected_rec = {
            "label": "9900010 - Flying Saucers, Broadline",
            "source_id": "9900010",
            "publish_competition_for_banners": False,
            "industry_level": 6
        }

        self.test_case.assertDictContainsSubset(expected_rec, new_industry_rec)