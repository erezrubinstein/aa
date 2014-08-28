import pprint
from common.utilities.inversion_of_control import Dependency
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_industry
from bson.objectid import ObjectId


class WFSIndustryCompetitionInstanceUpdaterTestCollection(ServiceTestCollection):

    def initialize(self):
        # get params builder
        self.main_params = Dependency("CoreAPIParamsBuilder").value

        # context
        self._context = {
            'user_id': ObjectId(),
            'source': 'wfs_company_competition_pairs_updater_test_collection.py'
        }


    def setUp(self):
        self.mds_access.call_delete_reset_database()
        self.wfs_access.call_delete_reset_database()


    def tearDown(self):
        pass


    def test_industry_competition_pairs_updater__run_industry_search_industries(self):
        self._insert_test_companies_and_industries()
        self._add_competition_link()
        self._run_industry_pairs_updater_task([])
        ccis = self._get_ccis()

        expected_cci_names = set(name for name in [
            "From Company 0 To Company 0",
            "From Company 0 To Company 1",
            "From Company 0 To Company 2",
            "From Company 0 To Company 3",
            "From Company 0 To Company 4",
            "From Company 0 To Company 5",
            "From Company 1 To Company 0",
            "From Company 2 To Company 0",
            "From Company 3 To Company 0",
            "From Company 4 To Company 0",
            "From Company 5 To Company 0",
            "From Company 1 To Company 1",
            "From Company 1 To Company 2",
            "From Company 1 To Company 3",
            "From Company 1 To Company 4",
            "From Company 1 To Company 5",
            "From Company 2 To Company 1",
            "From Company 3 To Company 1",
            "From Company 4 To Company 1",
            "From Company 5 To Company 1",
            "From Company 2 To Company 2",
            "From Company 2 To Company 3",
            "From Company 2 To Company 4",
            "From Company 2 To Company 5",
            "From Company 3 To Company 2",
            "From Company 4 To Company 2",
            "From Company 5 To Company 2",
            "From Company 3 To Company 3",
            "From Company 3 To Company 4",
            "From Company 3 To Company 5",
            "From Company 4 To Company 3",
            "From Company 5 To Company 3",
            "From Company 4 To Company 4",
            "From Company 4 To Company 5",
            "From Company 5 To Company 4",
            "From Company 5 To Company 5"
        ])
        names = set(name for name in ccis.iterkeys())
        self.test_case.assertEqual(names, expected_cci_names)

        for name, data in ccis.iteritems():
            from_industry_id, to_industry_id = self._get_industry_ids_from_to(data)
            self.test_case.assertIn(name, self.expected_industries[(from_industry_id, to_industry_id)])


    def test_industry_competition_pairs_updater__run_industry_specified_industry(self):
        self._insert_test_companies_and_industries()
        self._add_competition_link()
        self._run_industry_pairs_updater_task([self.ind0])
        ccis = self._get_ccis()

        expected_cci_names = set(name for name in [
            "From Company 0 To Company 0",
            "From Company 0 To Company 1",
            "From Company 0 To Company 2",
            "From Company 0 To Company 3",
            "From Company 0 To Company 4",
            "From Company 0 To Company 5",
            "From Company 1 To Company 0",
            "From Company 2 To Company 0",
            "From Company 3 To Company 0",
            "From Company 4 To Company 0",
            "From Company 5 To Company 0",
            "From Company 1 To Company 1",
            "From Company 1 To Company 2",
            "From Company 1 To Company 3",
            "From Company 1 To Company 4",
            "From Company 1 To Company 5",
            "From Company 2 To Company 1",
            "From Company 3 To Company 1",
            "From Company 4 To Company 1",
            "From Company 5 To Company 1",
            "From Company 2 To Company 2",
            "From Company 2 To Company 3",
            "From Company 2 To Company 4",
            "From Company 2 To Company 5",
            "From Company 3 To Company 2",
            "From Company 4 To Company 2",
            "From Company 5 To Company 2",
            "From Company 3 To Company 3",
            "From Company 3 To Company 4",
            "From Company 3 To Company 5",
            "From Company 4 To Company 3",
            "From Company 5 To Company 3"
        ])
        names = set(name for name in ccis.iterkeys())
        self.test_case.assertEqual(names, expected_cci_names)

        for name, data in ccis.iteritems():
            from_industry_id, to_industry_id = self._get_industry_ids_from_to(data)
            self.test_case.assertIn(name, self.expected_industries[(from_industry_id, to_industry_id)])


    def test_industry_competition_pairs_updater__add_competition(self):
        self._insert_test_companies_and_industries()
        self._run_industry_pairs_updater_task([self.ind0, self.ind1])
        ccis = self._get_ccis()

        expected_cci_names = set(name for name in [
            "From Company 0 To Company 0",
            "From Company 0 To Company 1",
            "From Company 0 To Company 2",
            "From Company 0 To Company 3",
            "From Company 1 To Company 0",
            "From Company 2 To Company 0",
            "From Company 3 To Company 0",
            "From Company 1 To Company 1",
            "From Company 1 To Company 2",
            "From Company 1 To Company 3",
            "From Company 2 To Company 1",
            "From Company 3 To Company 1",
            "From Company 2 To Company 2",
            "From Company 2 To Company 3",
            "From Company 3 To Company 2",
            "From Company 3 To Company 3",
            "From Company 4 To Company 4",
            "From Company 4 To Company 5",
            "From Company 5 To Company 4",
            "From Company 5 To Company 5"
        ])
        names = set(name for name in ccis.iterkeys())
        self.test_case.assertEqual(names, expected_cci_names)

        for name, data in ccis.iteritems():
            from_industry_id, to_industry_id = self._get_industry_ids_from_to(data)
            self.test_case.assertIn(name, self.expected_industries[(from_industry_id, to_industry_id)])


        self._add_competition_link()
        self._run_industry_pairs_updater_task([self.ind0, self.ind1])
        ccis = self._get_ccis()

        expected_cci_names = set(name for name in [
            "From Company 0 To Company 0",
            "From Company 0 To Company 1",
            "From Company 0 To Company 2",
            "From Company 0 To Company 3",
            "From Company 0 To Company 4",
            "From Company 0 To Company 5",
            "From Company 1 To Company 0",
            "From Company 2 To Company 0",
            "From Company 3 To Company 0",
            "From Company 4 To Company 0",
            "From Company 5 To Company 0",
            "From Company 1 To Company 1",
            "From Company 1 To Company 2",
            "From Company 1 To Company 3",
            "From Company 1 To Company 4",
            "From Company 1 To Company 5",
            "From Company 2 To Company 1",
            "From Company 3 To Company 1",
            "From Company 4 To Company 1",
            "From Company 5 To Company 1",
            "From Company 2 To Company 2",
            "From Company 2 To Company 3",
            "From Company 2 To Company 4",
            "From Company 2 To Company 5",
            "From Company 3 To Company 2",
            "From Company 4 To Company 2",
            "From Company 5 To Company 2",
            "From Company 3 To Company 3",
            "From Company 3 To Company 4",
            "From Company 3 To Company 5",
            "From Company 4 To Company 3",
            "From Company 5 To Company 3",
            "From Company 4 To Company 4",
            "From Company 4 To Company 5",
            "From Company 5 To Company 4",
            "From Company 5 To Company 5"
        ])
        names = set(name for name in ccis.iterkeys())
        self.test_case.assertEqual(names, expected_cci_names)

        for name, data in ccis.iteritems():
            from_industry_id, to_industry_id = self._get_industry_ids_from_to(data)
            self.test_case.assertIn(name, self.expected_industries[(from_industry_id, to_industry_id)])


    def test_industry_competition_pairs_updater__delete_competition(self):
        self._insert_test_companies_and_industries()
        self._add_competition_link()
        self._run_industry_pairs_updater_task([self.ind0, self.ind1])

        # delete the competition link
        self.mds_access.call_del_link_without_id("industry", self.ind0, "competitor",
                                                 "industry", self.ind1, "competitor",
                                                 "industry_competition")

        # rerun
        self._run_industry_pairs_updater_task([self.ind0, self.ind1])

        ccis = self._get_ccis()

        expected_cci_names = set(name for name in [
            "From Company 0 To Company 0",
            "From Company 0 To Company 1",
            "From Company 0 To Company 2",
            "From Company 0 To Company 3",
            "From Company 1 To Company 0",
            "From Company 2 To Company 0",
            "From Company 3 To Company 0",
            "From Company 1 To Company 1",
            "From Company 1 To Company 2",
            "From Company 1 To Company 3",
            "From Company 2 To Company 1",
            "From Company 3 To Company 1",
            "From Company 2 To Company 2",
            "From Company 2 To Company 3",
            "From Company 3 To Company 2",
            "From Company 3 To Company 3",
            "From Company 4 To Company 4",
            "From Company 4 To Company 5",
            "From Company 5 To Company 4",
            "From Company 5 To Company 5"
        ])
        names = set(name for name in ccis.iterkeys())
        self.test_case.assertEqual(names, expected_cci_names)

        for name, data in ccis.iteritems():
            from_industry_id, to_industry_id = self._get_industry_ids_from_to(data)
            self.test_case.assertIn(name, self.expected_industries[(from_industry_id, to_industry_id)])


    def _get_industry_ids_from_to(self, data):
        from_industry_id = data["from_links"]["industry"]["industry_classification"][0]["entity_id_to"]
        to_industry_id = data["to_links"]["industry"]["industry_classification"][0]["entity_id_to"]
        return from_industry_id, to_industry_id


    def _insert_test_companies_and_industries(self):
        # Create industries
        ind_data_1 = {
            "source_vendor": "NAICS",
            "industry_code": "111111",
            "industry_name": "Industry 1"
        }
        ind_data_2 = {
            "source_vendor": "NAICS",
            "industry_code": "222222",
            "industry_name": "Industry 2"
        }
        self.ind0 = insert_test_industry(data=ind_data_1)
        self.ind1 = insert_test_industry(data=ind_data_2)

        # Create companies
        self.cids = [
            insert_test_company(ticker="TICK0", name="Company 0", type="retail_banner", status="operating"),
            insert_test_company(ticker="TICK1", name="Company 1", type="retail_banner", status="operating"),
            insert_test_company(ticker="TICK2", name="Company 2", type="retail_banner", status="operating"),
            insert_test_company(ticker="TICK3", name="Company 3", type="retail_banner", status="operating"),
            insert_test_company(ticker="TICK4", name="Company 4", type="retail_banner", status="operating"),
            insert_test_company(ticker="TICK5", name="Company 5", type="retail_banner", status="operating")
        ]

        # Create industry links
        self.mds_access.call_add_link("company", self.cids[0], "primary_industry_classification",
                                      "industry", self.ind0, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", self.cids[1], "primary_industry_classification",
                                      "industry", self.ind0, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", self.cids[2], "primary_industry_classification",
                                      "industry", self.ind0, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", self.cids[3], "primary_industry_classification",
                                      "industry", self.ind0, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", self.cids[4], "primary_industry_classification",
                                      "industry", self.ind1, "primary_industry", "industry_classification", self.context)
        self.mds_access.call_add_link("company", self.cids[5], "primary_industry_classification",
                                      "industry", self.ind1, "primary_industry", "industry_classification", self.context)

        self.expected_industries = {
            (self.ind0, self.ind0): [
                "From Company 0 To Company 0",
                "From Company 0 To Company 1",
                "From Company 0 To Company 2",
                "From Company 0 To Company 3",
                "From Company 1 To Company 0",
                "From Company 2 To Company 0",
                "From Company 3 To Company 0",
                "From Company 1 To Company 1",
                "From Company 1 To Company 2",
                "From Company 1 To Company 3",
                "From Company 2 To Company 1",
                "From Company 3 To Company 1",
                "From Company 2 To Company 2",
                "From Company 2 To Company 3",
                "From Company 3 To Company 2",
                "From Company 3 To Company 3",
                ],
            (self.ind0, self.ind1): [
                "From Company 0 To Company 4",
                "From Company 0 To Company 5",
                "From Company 1 To Company 4",
                "From Company 1 To Company 5",
                "From Company 2 To Company 4",
                "From Company 2 To Company 5",
                "From Company 3 To Company 4",
                "From Company 3 To Company 5"
                ],
            (self.ind1, self.ind0): [
                "From Company 4 To Company 0",
                "From Company 5 To Company 0",
                "From Company 4 To Company 1",
                "From Company 5 To Company 1",
                "From Company 4 To Company 2",
                "From Company 5 To Company 2",
                "From Company 4 To Company 3",
                "From Company 5 To Company 3"
                ],
            (self.ind1, self.ind1): [
                "From Company 4 To Company 4",
                "From Company 4 To Company 5",
                "From Company 5 To Company 4",
                "From Company 5 To Company 5"
            ],
        }


    def _add_competition_link(self):
        self.mds_access.call_add_link("industry", self.ind0, "competitor", "industry",
                                      self.ind1, "competitor", "industry_competition", self.context,
                                      link_data={"home_to_away":{"weight": .9}, "away_to_home": {"weight": .9}})

    def _run_industry_pairs_updater_task(self, industry_ids):
        # Form task record
        task_rec = {
            "input": {
                "industry_ids": industry_ids
            },
            "meta": {
                "async": False
            }
        }

        # Run task first time
        self.task = self.wfs_access.call_task_new("entity_updated", "industry", "update_company_competition_pairs",
                                                  task_rec, self.context)


    def _get_ccis(self):
        params = self.main_params.mds.create_params(resource="find_entities_raw", entity_fields=["_id", "data", "name"],
                                                    as_list=True)["params"]
        ccis = self.mds_access.call_find_entities_raw("company_competition_instance", params, self.context)
        return {cci[2]: cci[1] for cci in ccis}