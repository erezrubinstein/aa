from common.utilities.date_utilities import START_OF_WORLD, END_OF_WORLD
from core.common.business_logic.service_entity_logic import industry_helper, company_helper
from geoprocessing.geoprocessors.demographics.gp7_core_trade_area_geo_processor import GP7CoreTradeAreaDemographics
from tests.integration_tests.utilities.data_access_misc_queries import *
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection


__author__ = 'erezrubinstein'


class GP8_GP9_TestCollection(ServiceTestCollection):

    def initialize(self):
        self.user_id = 'test@nexusri.com'
        self.source = "gp8_gp9_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):

        # set up base home data
        self.home_company_id = insert_test_company()
        self.home_store_id = create_store_with_rir(self.home_company_id, latitude = 1, longitude = -1)
        self.trade_area_id = insert_test_trade_area(self.home_store_id, self.home_company_id, latitude = 1, longitude = -1)

        # set up home trade area document, for geoprocessing
        self.trade_area_gp_document = select_trade_area(self.trade_area_id)

        # add industry to company
        self.home_industry_id = insert_test_industry()
        self.main_access.mds.call_add_link("company", self.home_company_id, 'primary_industry_classification', 'industry', self.home_industry_id, "primary_industry", "industry_classification", self.context)

    def tearDown(self):

        # delete when ending
        self.mds_access.call_delete_reset_database()



    # -------------------------------------- Begin Testing!! -------------------

    def test_simple_with_only_competition(self, geoprocessor):

        # create an industry
        industry_id1 = insert_test_industry()

        # create away companies
        away_company_id_1 = insert_test_company(workflow_status = "published")
        away_company_id_2 = insert_test_company(workflow_status = "published")

        # add industries to away companies
        self.main_access.mds.call_add_link("company", away_company_id_1, 'primary_industry_classification', 'industry', industry_id1, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", away_company_id_2, 'primary_industry_classification', 'industry', self.home_industry_id, "primary_industry", "industry_classification", self.context)

        # make industries compete
        # also, add some competition strengths.
        self.main_access.mds.call_add_link("industry", self.home_industry_id, 'competitor', 'industry', industry_id1, "competitor", "industry_competition",
                                           self.context, link_data = {"home_to_away":{"weight": .5}, "away_to_home": {"weight": .5}})

        # create several open, close dates for the stores
        closed_date1 = datetime(2012, 1, 1)
        opened_date2 = datetime(2012, 1, 1)
        closed_date2 = datetime(2012, 12, 2)
        opened_date3 = datetime(2012, 12, 2)

        # insert four stores.  Two for each company.
        away_store_id_1 = create_store_with_rir(away_company_id_1, latitude = 1, longitude = -1)
        away_store_id_2 = create_store_with_rir(away_company_id_1, latitude = 1.0001, longitude = -1.0001, as_of_date = opened_date2, as_of_date_is_opened_date = True)
        away_store_id_3 = create_store_with_rir(away_company_id_2, latitude = 1.0003, longitude = -1.0003, as_of_date = opened_date3, as_of_date_is_opened_date = True)
        away_store_id_4 = create_store_with_rir(away_company_id_2, latitude = 4, longitude = -4)

        # update some store closed dates (to close them)
        self._update_store_interval(away_store_id_1, None, closed_date1)
        self._update_store_interval(away_store_id_2, opened_date2, closed_date2)

        # run GP7 and GP8 on our home trade area
        GP7CoreTradeAreaDemographics().process_object(self.trade_area_gp_document)
        geoprocessor.process_object(self.trade_area_gp_document)

        # select the trade area after geoprocessing
        trade_area = select_trade_area(self.trade_area_id)

        # create expected competitive store array
        expected_competitive_stores = [
            {
                "away_geo": [-1, 1],
                "away_lat": 1,
                "away_lng": -1,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 0.5,
                "end_date": closed_date1.isoformat(),
                "away_zip": "12345",
                "away_company_id": away_company_id_1,
                "start_date": START_OF_WORLD.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_1
            },
            {
                "away_geo": [-1.0001, 1.0001],
                "away_lat": 1.0001,
                "away_lng": -1.0001,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 0.5,
                "end_date": closed_date2.isoformat(),
                "away_zip": "12345",
                "away_company_id": away_company_id_1,
                "start_date": opened_date2.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_2
            },
            {
                "away_geo": [-1.0003, 1.0003],
                "away_lat": 1.0003,
                "away_lng": -1.0003,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 1,
                "end_date": END_OF_WORLD.isoformat(),
                "away_zip": "12345",
                "away_company_id": away_company_id_2,
                "start_date": opened_date3.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_3
            }
        ]

        # verify the competition and monopoly structures
        self.test_case.assertEqual(sorted(trade_area["data"]["competitive_stores"]), sorted(expected_competitive_stores))
        self.test_case.assertEqual(trade_area["data"]["monopolies"], [])


    def test_simple_with_only_monopoly(self, geoprocessor):

        # run GP7 and GP8 without competition
        GP7CoreTradeAreaDemographics().process_object(self.trade_area_gp_document)
        geoprocessor.process_object(self.trade_area_gp_document)

        # select the trade area after geoprocessing
        trade_area = select_trade_area(self.trade_area_id)

        # create expected monopolies array
        expected_monopolies = [
            {
                "monopoly_type": "AbsoluteMonopoly",
                "start_date": START_OF_WORLD.isoformat(),
                "end_date": END_OF_WORLD.isoformat()
            }
        ]

        # verify the competition and monopoly structures
        self.test_case.assertEqual(trade_area["data"]["competitive_stores"], [])
        self.test_case.assertEqual(sorted(trade_area["data"]["monopolies"]), sorted(expected_monopolies))


    def test_complex_with_competition_and_monopolies(self, geoprocessor):

        # create away company
        away_company_id = insert_test_company(workflow_status = "published")

        # make the away company compete with the home company
        self.main_access.mds.call_add_link("company", self.home_company_id, 'competitor', 'company', away_company_id, "competitor", "company_competition", self.context)

        # add home industry to home company
        self.main_access.mds.call_add_link("company", away_company_id, 'primary_industry_classification', 'industry', self.home_industry_id, "primary_industry", "industry_classification", self.context)

        # create several dates for the stores.  To show the timeline of the company
        opened_date1 = None                     # has foreign competitor
        closed_date1 = datetime(2012, 1, 1)     # absolute monopoly
        opened_date2 = datetime(2012, 2, 2)     # has foreign competitor
        closed_date2 = datetime(2012, 12, 2)    # absolute monopoly
        opened_date3 = datetime(2013, 3, 3)     # single player monopoly
        closed_date3 = datetime(2013, 4, 4)     # absolute monopoly
        opened_date4 = datetime(2013, 5, 5)     # single player monopoly
        closed_date4 = None                     # ...

        # insert several stores.  Some for the away company and some for the home company itself.
        away_store_id_1 = create_store_with_rir(away_company_id, latitude = 1, longitude = -1)
        away_store_id_2 = create_store_with_rir(away_company_id, latitude = 1, longitude = -1, as_of_date = opened_date2, as_of_date_is_opened_date = True)
        away_store_id_3 = create_store_with_rir(self.home_company_id, latitude = 1, longitude = -1, as_of_date = opened_date3, as_of_date_is_opened_date = True)
        away_store_id_4 = create_store_with_rir(self.home_company_id, latitude = 1, longitude = -1, as_of_date = opened_date4, as_of_date_is_opened_date = True)

        # update the stores start/end date to reflect the sequence above
        self._update_store_interval(away_store_id_1, opened_date1, closed_date1)
        self._update_store_interval(away_store_id_2, opened_date2, closed_date2)
        self._update_store_interval(away_store_id_3, opened_date3, closed_date3)
        self._update_store_interval(away_store_id_4, opened_date4, closed_date4)

        # run GP7 and GP8 on our home trade area
        GP7CoreTradeAreaDemographics().process_object(self.trade_area_gp_document)
        geoprocessor.process_object(self.trade_area_gp_document)

        # select the trade area after geoprocessing
        trade_area = select_trade_area(self.trade_area_id)

        # create expected competitive store array
        expected_competitive_stores = [
            {
                "away_geo": [-1, 1],
                "away_lat": 1,
                "away_lng": -1,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 1,
                "end_date": closed_date1.isoformat(),
                "away_zip": "12345",
                "away_company_id": away_company_id,
                "start_date": START_OF_WORLD.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_1
            },
            {
                "away_geo": [-1, 1],
                "away_lat": 1,
                "away_lng": -1,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 1,
                "end_date": closed_date2.isoformat(),
                "away_zip": "12345",
                "away_company_id": away_company_id,
                "start_date": opened_date2.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_2
            },
            {
                "away_geo": [-1, 1],
                "away_lat": 1,
                "away_lng": -1,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 1,
                "end_date": closed_date3.isoformat(),
                "away_zip": "12345",
                "away_company_id": self.home_company_id,
                "start_date": opened_date3.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_3
            },
            {
                "away_geo": [-1, 1],
                "away_lat": 1,
                "away_lng": -1,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 1,
                "end_date": END_OF_WORLD.isoformat(),
                "away_zip": "12345",
                "away_company_id": self.home_company_id,
                "start_date": opened_date4.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_4
            }
        ]

        # create expected monopolies array
        expected_monopolies = [
            {
                "monopoly_type": "AbsoluteMonopoly",
                "start_date": closed_date1.isoformat(),
                "end_date": opened_date2.isoformat()
            },
            {
                "monopoly_type": "AbsoluteMonopoly",
                "start_date": closed_date2.isoformat(),
                "end_date": opened_date3.isoformat()
            },
            {
                "monopoly_type": "SinglePlayerMonopoly",
                "start_date": opened_date3.isoformat(),
                "end_date": closed_date3.isoformat()
            },
            {
                "monopoly_type": "AbsoluteMonopoly",
                "start_date": closed_date3.isoformat(),
                "end_date": opened_date4.isoformat()
            },
            {
                "monopoly_type": "SinglePlayerMonopoly",
                "start_date": opened_date4.isoformat(),
                "end_date": END_OF_WORLD.isoformat()
            }
        ]

        competitive_stores = sorted(trade_area["data"]["competitive_stores"], key=lambda x: x["away_store_id"])
        monopolies = sorted(trade_area["data"]["monopolies"], key=lambda x: x["start_date"])

        # verify the competition and monopoly structures
        self.test_case.assertItemsEqual(competitive_stores, expected_competitive_stores)
        self.test_case.assertItemsEqual(monopolies, expected_monopolies)


    def test_monopolies_bug_with_closed_store(self, geoprocessor):
        """
        This tests a bug we found in production to make sure it doesn't happen again
        """

        # set up company, store, trade_area
        home_company_id = insert_test_company(workflow_status = "published")
        home_store_id = create_store_with_rir(home_company_id, latitude = 1, longitude = -1)
        trade_area_id = insert_test_trade_area(home_store_id, home_company_id, latitude = 1, longitude = -1)
        trade_area_gp_document = select_trade_area(trade_area_id)

        # update the store to have a closed_date
        closed_date = datetime(2012, 1, 1)
        self._update_store_interval(home_store_id, START_OF_WORLD, closed_date)

        # create several other stores of the same company
        away_store_id_1 = create_store_with_rir(home_company_id, latitude = 1, longitude = -1)

        # run GP7 and GP8 on our home trade area
        GP7CoreTradeAreaDemographics().process_object(trade_area_gp_document)
        geoprocessor.process_object(trade_area_gp_document)

        # select the trade area after geoprocessing
        trade_area = select_trade_area(trade_area_id)

        # create expected competitive store array
        expected_competitive_stores = [
            {
                "away_geo": [-1, 1],
                "away_lat": 1,
                "away_lng": -1,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 1,
                "end_date": closed_date.isoformat(),
                "away_zip": "12345",
                "away_company_id": home_company_id,
                "start_date": START_OF_WORLD.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_1
            }
        ]

        # create expected monopolies array
        expected_monopolies = [
            {
                "monopoly_type": "SinglePlayerMonopoly",
                "start_date": START_OF_WORLD.isoformat(),
                "end_date": closed_date.isoformat()
            }
        ]

        # verify the competition and monopoly structures
        self.test_case.assertEqual(trade_area["data"]["competitive_stores"], expected_competitive_stores)
        self.test_case.assertEqual(sorted(trade_area["data"]["monopolies"]), sorted(expected_monopolies))


    def test_monopolies_bug_with_no_monopolies_to_close(self, geoprocessor):
        """
        This tests a bug we found in production to make sure it doesn't happen again
        """

        # create a home and away company
        home_company_id = insert_test_company()
        away_company_id = insert_test_company(workflow_status = "published")

        # add industry and link both companies to it
        industry_id = insert_test_industry()
        self.main_access.mds.call_add_link("company", home_company_id, 'primary_industry_classification', 'industry', industry_id, "primary_industry", "industry_classification", self.context)
        self.main_access.mds.call_add_link("company", away_company_id, 'primary_industry_classification', 'industry', industry_id, "primary_industry", "industry_classification", self.context)

        # set up company, store, trade_area and update it to have a closed date.
        home_store_id = create_store_with_rir(home_company_id, latitude = 1, longitude = -1)
        closed_date = datetime(2012, 1, 1)
        self._update_store_interval(home_store_id, START_OF_WORLD, closed_date)

        # create trade area
        trade_area_id = insert_test_trade_area(home_store_id, home_company_id, latitude = 1, longitude = -1, opened_date = None, closed_date = closed_date)
        trade_area_gp_document = select_trade_area(trade_area_id)

        # create an away store of a different company
        away_store_id_1 = create_store_with_rir(away_company_id, latitude = 1, longitude = -1)

        # run GP7 and GP8 on our home trade area
        GP7CoreTradeAreaDemographics().process_object(trade_area_gp_document)
        geoprocessor.process_object(trade_area_gp_document)

        # select the trade area after geoprocessing
        trade_area = select_trade_area(trade_area_id)

        # create expected competitive store array
        expected_competitive_stores = [
            {
                "away_geo": [-1, 1],
                "away_lat": 1,
                "away_lng": -1,
                "away_company_name": "UNITTEST_COMPANY",
                "weight": 1,
                "end_date": closed_date.isoformat(),
                "away_zip": "12345",
                "away_company_id": away_company_id,
                "start_date": START_OF_WORLD.isoformat(),
                "away_state": "UT",
                "away_city": "UNIT_TEST_VILLE",
                "away_street_number": "123",
                "away_street": "Main St",
                "away_store_id": away_store_id_1
            }
        ]

        # create expected monopolies array
        expected_monopolies = []

        # verify the competition and monopoly structures
        self.test_case.assertEqual(trade_area["data"]["competitive_stores"], expected_competitive_stores)
        self.test_case.assertEqual(sorted(trade_area["data"]["monopolies"]), sorted(expected_monopolies))


    def test_competition_weights__industries_with_different_directional_weights(self, geoprocessor):
        """
        Industry A competes with Industry B
        A->B : weight 1.0
        B->A : weight 0.0

        """
        # industries
        industry_A = insert_test_industry()
        industry_B = insert_test_industry()

        # companies
        company_A = insert_test_company(name = "company_A", workflow_status = "published")
        company_B = insert_test_company(name = "company_B", workflow_status = "published")

        # two stores per company
        A_store_1 = create_store_with_rir(company_A, longitude = 0.0, latitude = 0.0)
        A_store_2 = create_store_with_rir(company_A, longitude = 10.0, latitude = 10.0)
        B_store_1 = create_store_with_rir(company_B, longitude = 0.0, latitude = 0.0)
        B_store_2 = create_store_with_rir(company_B, longitude = 10.0, latitude = 10.0)

        # shape arrays
        shape_array_1 = [[[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0], [1.0, 0.0]]]
        shape_array_2 = [[[11.0, 10.0], [10.0, 11.0], [9.0, 10.0], [10.0, 9.0], [11.0, 10.0]]]

        # one trade area per store
        A_trade_area_1 = insert_test_geoprocessed_trade_area(A_store_1, B_store_1, company_id = company_A, longitude = 0.0, latitude = 0.0, shape_array = shape_array_1)
        A_trade_area_2 = insert_test_geoprocessed_trade_area(A_store_2, B_store_2, company_id = company_A, longitude = 10.0, latitude = 10.0, shape_array = shape_array_2)
        B_trade_area_1 = insert_test_geoprocessed_trade_area(B_store_1, A_store_1, company_id = company_B, longitude = 0.0, latitude = 0.0, shape_array = shape_array_1)
        B_trade_area_2 = insert_test_geoprocessed_trade_area(B_store_2, A_store_2, company_id = company_B, longitude = 10.0, latitude = 10.0, shape_array = shape_array_2)

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

        # geoprocess those steeds
        geoprocessor.process_object(select_trade_area(A_trade_area_1))
        geoprocessor.process_object(select_trade_area(A_trade_area_2))
        geoprocessor.process_object(select_trade_area(B_trade_area_1))
        geoprocessor.process_object(select_trade_area(B_trade_area_2))

        # re processed trade areas
        A_trade_area_1__competitive_stores = select_trade_area(A_trade_area_1)["data"]["competitive_stores"]
        A_trade_area_2__competitive_stores = select_trade_area(A_trade_area_2)["data"]["competitive_stores"]
        B_trade_area_1__competitive_stores = select_trade_area(B_trade_area_1)["data"]["competitive_stores"]
        B_trade_area_2__competitive_stores = select_trade_area(B_trade_area_2)["data"]["competitive_stores"]

        # A 1
        self.test_case.assertEqual(1, len(A_trade_area_1__competitive_stores))
        self.test_case.assertEqual(B_store_1, A_trade_area_1__competitive_stores[0]["away_store_id"])
        self.test_case.assertEqual(1.0, A_trade_area_1__competitive_stores[0]["weight"])

        # A 2
        self.test_case.assertEqual(1, len(A_trade_area_2__competitive_stores))
        self.test_case.assertEqual(B_store_2, A_trade_area_2__competitive_stores[0]["away_store_id"])
        self.test_case.assertEqual(1.0, A_trade_area_2__competitive_stores[0]["weight"])

        # B 1
        self.test_case.assertEqual(1, len(B_trade_area_1__competitive_stores))
        self.test_case.assertEqual(A_store_1, B_trade_area_1__competitive_stores[0]["away_store_id"])
        self.test_case.assertEqual(0.0, B_trade_area_1__competitive_stores[0]["weight"])

        # B 2
        self.test_case.assertEqual(1, len(B_trade_area_2__competitive_stores))
        self.test_case.assertEqual(A_store_2, B_trade_area_2__competitive_stores[0]["away_store_id"])
        self.test_case.assertEqual(0.0, B_trade_area_2__competitive_stores[0]["weight"])


    # -------------------------------------- Private Methods --------------------------------------

    def _update_store_interval(self, store_id, open_date, close_date):

        query = { "_id": store_id }
        update_operation = { "$set": { "interval": [open_date, close_date] }}
        self.main_access.mds.call_batch_update_entities("store", query, update_operation, self.context)




