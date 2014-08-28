from common.utilities.misc_utilities import convert_entity_list_to_dictionary__array_format, convert_entity_list_to_dictionary
from core.common.business_logic.service_entity_logic.company_helper import *
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_file, insert_test_industry, insert_test_company_competition_instance
import datetime


__author__ = 'erezrubinstein'


class CompanyHelperTestCollection(ServiceTestCollection):

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

    # -------------------------------------- Begin Testing!! -------------------

    def test_select_companies_by_id(self):

        # create three companies
        company_id_1 = ensure_id(insert_test_company(name = "test1"))
        company_id_2 = ensure_id(insert_test_company(name = "test2"))
        company_id_3 = ensure_id(insert_test_company(name = "test3"))

        # select the first two companies
        companies = select_companies_by_id([company_id_1, company_id_2], self.context)
        companies = convert_entity_list_to_dictionary(companies)

        # verify that the first two are selected and not the third
        self.test_case.assertEqual(len(companies), 2)
        self.test_case.assertIn(company_id_1, companies)
        self.test_case.assertIn(company_id_2, companies)

        # verify that id and name are included (just in one company assume the others too)
        self.test_case.assertIn("_id", companies[company_id_1])
        self.test_case.assertIn("name", companies[company_id_1])

    def test_comprehensive_file_finder_one_file_old_encoder(self):

        # this inserts the test company and file using the old JSON encoder

        company_id = insert_test_company(name = 'woot')
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': company_id,
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02)
        }

        mds_file_id = ensure_id(insert_test_file(name = 'woot', data = data))

        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])

        self.test_case.assertEqual(sorted_file_list[0]['_id'], mds_file_id)
        self.test_case.assertEqual(sorted_file_list[0]['data']['is_comprehensive'], True)
        self.test_case.assertEqual(sorted_file_list[0]['data']['company_id'], str(company_id))
        self.test_case.assertEqual(sorted_file_list[0]['data']['type'], 'retail_input_file')
        self.test_case.assertEqual(sorted_file_list[0]['data']['as_of_date'], '2013-05-02T00:00:00')

    def test_comprehensive_file_finder_one_file(self):

        # this inserts the test company and file using the new JSON encoder

        company_id = insert_test_company(name = 'woot', use_new_json_encoder=True)
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': company_id,
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data, use_new_json_encoder=True))

        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])

        self.test_case.assertEqual(sorted_file_list[0]['_id'], mds_file_id)
        self.test_case.assertEqual(sorted_file_list[0]['data']['is_comprehensive'], True)
        self.test_case.assertEqual(sorted_file_list[0]['data']['company_id'], str(company_id))
        self.test_case.assertEqual(sorted_file_list[0]['data']['type'], 'retail_input_file')
        self.test_case.assertEqual(sorted_file_list[0]['data']['as_of_date'], datetime.datetime(2013, 05, 02))

    def test_comprehensive_file_finder_two_files_one_file_not_comprehensive_old_encoder(self):

        company_id = insert_test_company(name='woot')
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': False,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02)
        }

        non_comp_mds_file_id = ensure_id(insert_test_file(name='woot', data=data))

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02, 12, 30)
        }

        comp_mds_file_id = ensure_id(insert_test_file(name='woot', data=data))

        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])

        self.test_case.assertEqual(sorted_file_list[0]['_id'], comp_mds_file_id)
        self.test_case.assertEqual(sorted_file_list[0]['data']['is_comprehensive'], True)
        self.test_case.assertEqual(sorted_file_list[0]['data']['company_id'], str(company_id))
        self.test_case.assertEqual(sorted_file_list[0]['data']['type'], 'retail_input_file')
        self.test_case.assertEqual(sorted_file_list[0]['data']['as_of_date'], '2013-05-02T12:30:00')

    def test_comprehensive_file_finder_two_files_one_file_not_comprehensive(self):

        company_id = insert_test_company(name='woot', use_new_json_encoder=True)
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': False,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02)
        }

        non_comp_mds_file_id = ensure_id(insert_test_file(name='woot', data=data, use_new_json_encoder=True))

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02, 12, 30)
        }

        comp_mds_file_id = ensure_id(insert_test_file(name='woot', data=data, use_new_json_encoder=True))

        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])

        self.test_case.assertEqual(sorted_file_list[0]['_id'], comp_mds_file_id)
        self.test_case.assertEqual(sorted_file_list[0]['data']['is_comprehensive'], True)
        self.test_case.assertEqual(sorted_file_list[0]['data']['company_id'], str(company_id))
        self.test_case.assertEqual(sorted_file_list[0]['data']['type'], 'retail_input_file')
        self.test_case.assertEqual(sorted_file_list[0]['data']['as_of_date'], datetime.datetime(2013, 05, 02, 12, 30))

    def test_comprehensive_file_finder_two_files_get_earliest_old_encoder(self):

        company_id = insert_test_company(name='woot')
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': company_id,
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02, 14, 30)
        }

        second_comp_mds_file_id = ensure_id(insert_test_file(name='woot', data=data))

        data = {
            'is_comprehensive': True,
            'company_id': company_id,
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02, 12, 30)
        }

        first_mds_file_id = ensure_id(insert_test_file(name='woot', data=data))

        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])

        self.test_case.assertEqual(sorted_file_list[0]['_id'], first_mds_file_id)
        self.test_case.assertEqual(sorted_file_list[0]['data']['is_comprehensive'], True)
        self.test_case.assertEqual(sorted_file_list[0]['data']['company_id'], company_id)
        self.test_case.assertEqual(sorted_file_list[0]['data']['type'], 'retail_input_file')
        self.test_case.assertEqual(sorted_file_list[0]['data']['as_of_date'], '2013-05-02T12:30:00')

        self.test_case.assertEqual(sorted_file_list[1]['_id'], second_comp_mds_file_id)
        self.test_case.assertEqual(sorted_file_list[1]['data']['is_comprehensive'], True)
        self.test_case.assertEqual(sorted_file_list[1]['data']['company_id'], company_id)
        self.test_case.assertEqual(sorted_file_list[1]['data']['type'], 'retail_input_file')
        self.test_case.assertEqual(sorted_file_list[1]['data']['as_of_date'], '2013-05-02T14:30:00')

    def test_comprehensive_file_finder_two_files_get_earliest(self):

        company_id = insert_test_company(name='woot', use_new_json_encoder=True)
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02, 14, 30)
        }

        second_comp_mds_file_id = ensure_id(insert_test_file(name='woot', data=data, use_new_json_encoder=True))

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 02, 12, 30)
        }

        first_mds_file_id = ensure_id(insert_test_file(name='woot', data=data, use_new_json_encoder=True))

        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])

        self.test_case.assertEqual(sorted_file_list[0]['_id'], first_mds_file_id)
        self.test_case.assertEqual(sorted_file_list[0]['data']['is_comprehensive'], True)
        self.test_case.assertEqual(sorted_file_list[0]['data']['company_id'], company_id)
        self.test_case.assertEqual(sorted_file_list[0]['data']['type'], 'retail_input_file')
        self.test_case.assertEqual(sorted_file_list[0]['data']['as_of_date'], datetime.datetime(2013, 05, 02, 12, 30))

        self.test_case.assertEqual(sorted_file_list[1]['_id'], second_comp_mds_file_id)
        self.test_case.assertEqual(sorted_file_list[1]['data']['is_comprehensive'], True)
        self.test_case.assertEqual(sorted_file_list[1]['data']['company_id'], company_id)
        self.test_case.assertEqual(sorted_file_list[1]['data']['type'], 'retail_input_file')
        self.test_case.assertEqual(sorted_file_list[1]['data']['as_of_date'], datetime.datetime(2013, 05, 02, 14, 30))

    def test_comprehensive_file_finder_on_interval_gt_old_encoder(self):

        company_id = insert_test_company(name='woot')
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 01)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(len(sorted_file_list), 0)

    def test_comprehensive_file_finder_on_interval_gt(self):

        company_id = insert_test_company(name='woot', use_new_json_encoder=True)
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 01)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data, use_new_json_encoder=True))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(len(sorted_file_list), 0)

    def test_comprehensive_file_finder_on_interval_lt_old_encoder(self):

        company_id = insert_test_company(name='woot')
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 03)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(len(sorted_file_list), 0)

    def test_comprehensive_file_finder_on_interval_lt(self):

        company_id = insert_test_company(name='woot')
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 03)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data, use_new_json_encoder=True))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(len(sorted_file_list), 0)

    def test_comprehensive_file_finder_outside_interval_old_encoder(self):

        company_id = insert_test_company(name='woot')
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 04)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(sorted_file_list, [])

    def test_comprehensive_file_finder_outside_interval(self):

        company_id = insert_test_company(name='woot', use_new_json_encoder=True)
        start = datetime.datetime(2013, 05, 01)
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 04)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data, use_new_json_encoder=True))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(sorted_file_list, [])

    def test_comprehensive_file_finder_within_interval_strange_formats(self):

        company_id = insert_test_company(name = 'woot')
        start = "2013-05-01T12:00:00"
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 01, 12, 30, 00)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(sorted_file_list[0]["_id"], mds_file_id)

    def test_comprehensive_file_finder_on_interval_strange_formats_lt(self):

        company_id = insert_test_company(name='woot')
        start = "2013-05-01T00:00:00"
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 03)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(len(sorted_file_list), 0)

    def test_comprehensive_file_finder_on_interval_strange_formats_gt(self):

        company_id = insert_test_company(name='woot')
        start = "2013-05-01T00:00:00"
        end = datetime.datetime(2013, 05, 03)

        data = {
            'is_comprehensive': True,
            'company_id': str(company_id),
            'type': 'retail_input_file',
            'as_of_date': datetime.datetime(2013, 05, 01)
        }

        mds_file_id = ensure_id(insert_test_file(name='woot', data=data))
        sorted_file_list = find_comprehensive_retail_input_files_for_company_on_interval(company_id, [start, end])
        self.test_case.assertEqual(len(sorted_file_list), 0)

    def select_companies_by_name_for_typeahead(self):

        # create three companies.  One complete match, one partial match, and one no match.
        company_id_1 = ensure_id(insert_test_company(ticker = "w", name = "Woot", workflow_status = "published"))
        company_id_2 = ensure_id(insert_test_company(ticker = "cw", name = "Chickenwoot", workflow_status = "published"))
        company_id_3 = ensure_id(insert_test_company(ticker = "c", name = "chicken", workflow_status = "published"))
        company_id_4 = ensure_id(insert_test_company(ticker = "cwoo", name = "chicken", workflow_status = "other"))
        company_id_5 = ensure_id(insert_test_company(ticker = "woo", name = "WootWoot"))

        # search for companies that match woo
        matches = select_companies_by_name_for_typeahead("woo", hide_unpublished = True)

        # make sure structure is correct
        self.test_case.assertEquals(matches["header"], ["id", "name", "ticker", "score"])
        self.test_case.assertEquals(matches["meta"], {
            "num_rows": 2,
            "page_index": 0,
            "sort_direction": -1,
            "page_size": 2,
            "sort_index": 3
        })

        # make sure results are correct
        matches = convert_entity_list_to_dictionary__array_format(matches["rows"])
        self.test_case.assertEquals(matches, {
            company_id_1: [company_id_1, "Woot", "w", 2],
            company_id_2: [company_id_2, "Chickenwoot", "cw", 1]
        })

    def test_select_company_ids_by_primary_industry_ids(self):

        # create three companies
        company_id1 = insert_test_company()
        company_id2 = insert_test_company()
        company_id3 = insert_test_company()

        # create three industries
        industry_id1 = insert_test_industry()
        industry_id2 = insert_test_industry()
        industry_id3 = insert_test_industry()

        # assign an industry per company
        insert_new_industry_links(company_id1, [industry_id1], True, self.context)
        insert_new_industry_links(company_id2, [industry_id2], True, self.context)
        insert_new_industry_links(company_id3, [industry_id3], True, self.context)

        # query the company ids for the first two industries
        matching_companies = select_company_ids_by_primary_industry_ids([industry_id1, industry_id2])

        # verify that it found both the first two companies and not the third
        self.test_case.assertEqual(matching_companies, {
            company_id1: industry_id1,
            company_id2: industry_id2
        })


    def test_select_competitive_companies(self):

        # create two industries
        industry_id1 = ensure_id(insert_test_industry())
        industry_id2 = ensure_id(insert_test_industry())

        # create three companies
        company_id1 = ensure_id(insert_test_company(workflow_status = "published"))
        company_id2 = ensure_id(insert_test_company(workflow_status = "published"))
        company_id3 = ensure_id(insert_test_company(workflow_status = "published"))

        # add primary industries to all three companies.  Company 3 gets a different industry.
        self.main_access.mds.call_add_link("company", company_id1, 'primary_industry_classification', 'industry', industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id2, 'primary_industry_classification', 'industry', industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id3, 'primary_industry_classification', 'industry', industry_id2, "primary_industry", "industry_classification", self.context)

        # make industries 1 and 2 compete with each other
        link_interval = [datetime.datetime(2012, 1, 1), datetime.datetime(2013, 2, 2)]
        link_data = {"home_to_away": {"weight": .7}, "away_to_home": {"weight": .7}}
        self.main_access.mds.call_add_link("industry", industry_id1, 'competitor', 'industry', industry_id2, "competitor", "industry_competition", self.context, link_interval = link_interval,
                                           link_data = link_data)

        # query the competitions of company
        competitive_companies = select_competitive_companies(company_id1)

        # sort both the expected and real array so that the order doesn't matter
        expected_competitive_companies = sorted([
            { "_id": str(company_id1), "interval": None, "competition_strength": 1 },
            { "_id": str(company_id2), "interval": None, "competition_strength": 1 },
            { "_id": str(company_id3), "interval": [datetime.datetime(2012, 1, 1), datetime.datetime(2013, 2, 2)], "competition_strength": .7 }
        ])
        competitive_companies = sorted(competitive_companies)

        # make sure the competitions are correct
        self.test_case.assertEqual(competitive_companies, expected_competitive_companies)


    def test_select_competitive_companies__non_published_companies(self):

        # create an industry
        industry_id1 = ensure_id(insert_test_industry())

        # create three companies.  all published, besides company 3 that's new.
        company_id1 = ensure_id(insert_test_company(workflow_status = "published"))
        company_id2 = ensure_id(insert_test_company(workflow_status = "published"))
        company_id3 = ensure_id(insert_test_company(workflow_status = "new"))

        # add primary industries to all three companies.
        self.main_access.mds.call_add_link("company", company_id1, 'primary_industry_classification', 'industry', industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id2, 'primary_industry_classification', 'industry', industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id3, 'primary_industry_classification', 'industry', industry_id1, "primary_industry", "industry_classification", self.context)

        # query the competitions of company
        competitive_companies = select_competitive_companies(company_id1)

        # sort both the expected and real array so that the order doesn't matter
        expected_competitive_companies = [
            { "_id": str(company_id1), "interval": None, "competition_strength": 1 },
            { "_id": str(company_id2), "interval": None, "competition_strength": 1 }
        ]

        # make sure the competitions are correct
        self.test_case.assertEqual(competitive_companies, expected_competitive_companies)


    def test_select_competitive_companies__multiple_competition_records(self):
        """
        This verifies a specific case where a company has multiple industries.
        """

        # create three industries
        industry_id1 = ensure_id(insert_test_industry())
        industry_id2 = ensure_id(insert_test_industry())
        industry_id3 = ensure_id(insert_test_industry())

        # create three companies
        company_id1 = ensure_id(insert_test_company(workflow_status = "published"))
        company_id2 = ensure_id(insert_test_company(workflow_status = "published"))
        company_id3 = ensure_id(insert_test_company(workflow_status = "published"))

        # add industry1 as the primary for company1.  industry two as the primary for company 2 and as the secondary for company 3.
        self.main_access.mds.call_add_link("company", company_id1, 'primary_industry_classification', 'industry', industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id2, 'primary_industry_classification', 'industry', industry_id2, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", company_id3, 'secondary_industry_classification', 'industry', industry_id2, "secondary_industry", "industry_classification", self.context)

        # also add industry 3 as a secondary of company 2
        self.main_access.mds.call_add_link("company", company_id2, 'secondary_industry_classification', 'industry', industry_id3, "secondary_industry", "industry_classification", self.context)

        # make industries 1 and 2 compete with each other
        link_interval = [datetime.datetime(2012, 1, 1), datetime.datetime(2013, 2, 2)]
        link_data = {"home_to_away": {"weight": .7}, "away_to_home": {"weight": .7}}
        self.main_access.mds.call_add_link("industry", industry_id1, 'competitor', 'industry', industry_id2, "competitor", "industry_competition", self.context, link_interval = link_interval,
                                           link_data = link_data)

        # make industries 1 and 3 compete with each other
        # this will make sure that the numbers for company 2 will use dates and weight from the primary industry, not secondary
        link_interval = [datetime.datetime(2012, 5, 5), datetime.datetime(2013, 6, 6)]
        link_data = { "competition_strength": .9 }
        link_data = {"home_to_away":{"weight": .9}, "away_to_home": {"weight": .9}}
        self.main_access.mds.call_add_link("industry", industry_id1, 'competitor', 'industry', industry_id3, "competitor", "industry_competition", self.context, link_interval = link_interval,
                                           link_data = link_data)

        # query the competitions of company
        competitive_companies = select_competitive_companies(company_id1)

        # create expected company array and make sure only one interval is returned and it matches the competition record I'm looking for
        expected_competitive_companies = [
            { "_id": str(company_id1), "interval": None, "competition_strength": 1 },
            { "_id": str(company_id2), "interval": [datetime.datetime(2012, 1, 1), datetime.datetime(2013, 2, 2)], "competition_strength": .7 }
        ]
        competitive_companies = sorted(competitive_companies)

        # make sure the competitions are correct
        self.test_case.assertEqual(competitive_companies, expected_competitive_companies)


    def test_delete_ccis(self):
        company_id1 = insert_test_company()
        company_id2 = insert_test_company()
        company_id3 = insert_test_company()

        # add some ccis
        insert_test_company_competition_instance(company_id1, company_id1)
        insert_test_company_competition_instance(company_id1, company_id2)
        insert_test_company_competition_instance(company_id1, company_id3)

        # this call doesn't return the actual list of CCI IDs
        _ = insert_test_company_competition_instance(company_id2, company_id3)

        delete_ccis(company_id1, self.context)

        ccis = self.mds_access.call_find_entities_raw("company_competition_instance", {}, self.context)

        # list is 2 items long because MDS automatically inserts the reflexive instance
        self.test_case.assertEqual(len(ccis), 2)


    def test_get_published_banner_ids_of_parent(self):

        # create family 1: 1 parent, 1 published banner, and 1 unpublished banner
        parent_id = insert_test_company(type="retail_parent", workflow_status = "published")
        banner_id1 = insert_test_company(type="retail_banner", workflow_status = "new")
        banner_id2 = insert_test_company(type="retail_banner", workflow_status = "published")

        # link em up
        links1 = self.main_access.mds.call_add_link("company", parent_id, 'retail_parent', 'company', banner_id1, "retail_segment", "retailer_branding", self.context)
        links2 = self.main_access.mds.call_add_link("company", parent_id, 'retail_parent', 'company', banner_id2, "retail_segment", "retailer_branding", self.context)

        # get em
        published_banners = get_published_banner_ids_of_parent(parent_id, self.context)

        self.test_case.assertEqual(published_banners, [banner_id2])

        # delete the published banner link to make sure we get an empty list
        self.main_access.mds.call_del_link_by_id_fo_ril("company", parent_id, "company", banner_id2, links2[0]["_id"])

        # get em again
        published_banners = get_published_banner_ids_of_parent(parent_id, self.context)

        self.test_case.assertEqual(published_banners, [])

    def test_get_company_family(self):
        parent_id = insert_test_company(type="retail_parent")
        banner_id = insert_test_company(type="retail_banner")

        parent_id1 = insert_test_company(type="retail_parent")
        banner_id11 = insert_test_company(type="retail_banner")
        banner_id12 = insert_test_company(type="retail_banner")

        # link em up
        links1 = self.main_access.mds.call_add_link("company", parent_id1, 'retail_parent', 'company', banner_id11,
                                                    "retail_segment", "retailer_branding", self.context)
        links2 = self.main_access.mds.call_add_link("company", parent_id1, 'retail_parent', 'company', banner_id12,
                                                    "retail_segment", "retailer_branding", self.context)

        # get em
        bids, pid = get_company_family(banner_id, self.context)
        self.test_case.assertEqual(bids, [banner_id])
        self.test_case.assertEqual(pid, None)

        # get em
        bids, pid = get_company_family(parent_id, self.context)
        self.test_case.assertEqual(bids, [])
        self.test_case.assertEqual(pid, parent_id)

        # get em
        bids, pid = get_company_family(parent_id1, self.context)
        self.test_case.assertEqual(sorted(bids), sorted([banner_id11, banner_id12]))
        self.test_case.assertEqual(pid, parent_id1)

        # get em
        bids, pid = get_company_family(banner_id11, self.context)
        self.test_case.assertEqual(sorted(bids), sorted([banner_id11, banner_id12]))
        self.test_case.assertEqual(pid, parent_id1)

        # get em
        bids, pid = get_company_family(banner_id12, self.context)
        self.test_case.assertEqual(sorted(bids), sorted([banner_id11, banner_id12]))
        self.test_case.assertEqual(pid, parent_id1)

    def test_get_published_company_family_ids_for_company_ids(self):
        pid1 = insert_test_company(type="retail_parent")
        bid11 = insert_test_company(type="retail_banner", workflow_status="published")

        pid2 = insert_test_company(type="retail_parent", workflow_status="published")
        bid21 = insert_test_company(type="retail_banner")

        # create family 1: 1 parent, 2 published banners
        pid3 = insert_test_company(type="retail_parent", workflow_status="published")
        bid31 = insert_test_company(type="retail_banner", workflow_status="published")
        bid32 = insert_test_company(type="retail_banner", workflow_status="published")

        # create family 1: 1 parent, 1 published banner, and 1 unpublished banner
        pid4 = insert_test_company(type="retail_parent", workflow_status="published")
        bid41 = insert_test_company(type="retail_banner", workflow_status="published")
        bid42 = insert_test_company(type="retail_banner")

        # link em up
        self.main_access.mds.call_add_link("company", pid1, 'retail_parent', 'company', bid11, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid2, 'retail_parent', 'company', bid21, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid3, 'retail_parent', 'company', bid31, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid3, 'retail_parent', 'company', bid32, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid4, 'retail_parent', 'company', bid41, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid4, 'retail_parent', 'company', bid42, "retail_segment", "retailer_branding", self.context)

        # From parents
        cids = get_published_company_family_ids_for_company_ids([pid1], self.context)
        self.test_case.assertItemsEqual(cids, [bid11])

        cids = get_published_company_family_ids_for_company_ids([pid2], self.context)
        self.test_case.assertItemsEqual(cids, [pid2])

        cids = get_published_company_family_ids_for_company_ids([pid3], self.context)
        self.test_case.assertItemsEqual(cids, [pid3, bid31, bid32])

        cids = get_published_company_family_ids_for_company_ids([pid4], self.context)
        self.test_case.assertItemsEqual(cids, [pid4, bid41])

        # From banners
        cids = get_published_company_family_ids_for_company_ids([bid11], self.context)
        self.test_case.assertItemsEqual(cids, [bid11])

        cids = get_published_company_family_ids_for_company_ids([bid21], self.context)
        self.test_case.assertItemsEqual(cids, [pid2])

        cids = get_published_company_family_ids_for_company_ids([bid31], self.context)
        self.test_case.assertItemsEqual(cids, [pid3, bid31, bid32])

        cids = get_published_company_family_ids_for_company_ids([bid32], self.context)
        self.test_case.assertItemsEqual(cids, [pid3, bid31, bid32])

        cids = get_published_company_family_ids_for_company_ids([bid41], self.context)
        self.test_case.assertItemsEqual(cids, [pid4, bid41])

        cids = get_published_company_family_ids_for_company_ids([bid42], self.context)
        self.test_case.assertItemsEqual(cids, [pid4, bid41])

        # All parents
        cids = get_published_company_family_ids_for_company_ids([pid1, pid2, pid3, pid4], self.context)
        self.test_case.assertItemsEqual(cids, [bid11, pid2, pid3, bid31, bid32, pid4, bid41])

        # All banners
        cids = get_published_company_family_ids_for_company_ids([bid11, bid21, bid31, bid32, bid41, bid42], self.context)
        self.test_case.assertItemsEqual(cids, [bid11, pid2, pid3, bid31, bid32, pid4, bid41])

        # All companies
        cids = get_published_company_family_ids_for_company_ids([bid11, pid2, pid3, bid31, bid32, pid4, bid41], self.context)
        self.test_case.assertItemsEqual(cids, [bid11, pid2, pid3, bid31, bid32, pid4, bid41])

    def test_get_published_banner_ids_of_parent(self):
        pid1 = insert_test_company(type="retail_parent")
        bid11 = insert_test_company(type="retail_banner", workflow_status="published")

        pid2 = insert_test_company(type="retail_parent", workflow_status="published")
        bid21 = insert_test_company(type="retail_banner")

        # create family 1: 1 parent, 2 published banners
        pid3 = insert_test_company(type="retail_parent", workflow_status="published")
        bid31 = insert_test_company(type="retail_banner", workflow_status="published")
        bid32 = insert_test_company(type="retail_banner", workflow_status="published")

        # create family 1: 1 parent, 1 published banner, and 1 unpublished banner
        pid4 = insert_test_company(type="retail_parent", workflow_status="published")
        bid41 = insert_test_company(type="retail_banner", workflow_status="published")
        bid42 = insert_test_company(type="retail_banner")

        # link em up
        self.main_access.mds.call_add_link("company", pid1, 'retail_parent', 'company', bid11, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid2, 'retail_parent', 'company', bid21, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid3, 'retail_parent', 'company', bid31, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid3, 'retail_parent', 'company', bid32, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid4, 'retail_parent', 'company', bid41, "retail_segment", "retailer_branding", self.context)
        self.main_access.mds.call_add_link("company", pid4, 'retail_parent', 'company', bid42, "retail_segment", "retailer_branding", self.context)

        # From parents
        cids = get_published_banner_ids_of_parent(pid1, self.context)
        self.test_case.assertItemsEqual(cids, [bid11])

        cids = get_published_banner_ids_of_parent(pid2, self.context)
        self.test_case.assertItemsEqual(cids, [])

        cids = get_published_banner_ids_of_parent(pid3, self.context)
        self.test_case.assertItemsEqual(cids, [bid31, bid32])

        cids = get_published_banner_ids_of_parent(pid4, self.context)
        self.test_case.assertItemsEqual(cids, [bid41])
