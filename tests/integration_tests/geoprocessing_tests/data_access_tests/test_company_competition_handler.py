from datetime import datetime
import unittest
from common.business_logic.company_info import Competitor
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import insert_test_company, insert_test_competitor, delete_test_company, delete_test_competitors, select_competitive_companies_by_home_company_id

__author__ = 'erezrubinstein'


class CompanyCompetitionDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._data_repository)

        # insert test data
        cls._company_id = insert_test_company()

        # away companies
        cls._away_company_id1 = insert_test_company()
        cls._away_company_id2 = insert_test_company()

    @classmethod
    def tearDownClass(cls):
        # delete test data
        delete_test_competitors(cls._company_id)
        delete_test_competitors(cls._away_company_id1)
        delete_test_competitors(cls._away_company_id2)
        delete_test_company(cls._away_company_id1)
        delete_test_company(cls._away_company_id2)
        delete_test_company(cls._company_id)

        dependencies.clear()

    def test_select_all_open_competitive_companies_ids_for_company(self):
        try:
            # insert one closed record and one opened record
            insert_test_competitor(self._company_id, self._away_company_id1, None, None)
            insert_test_competitor(self._company_id, self._away_company_id2, None, "2012-09-1")

            # select competitive ids
            competitors = self._data_repository.select_all_open_competitive_companies_ids_for_company(self._company_id)

            # make sure only the active competitive company was selected
            self.assertEqual(len(competitors), 1)
            self.assertEqual(competitors[0], self._away_company_id1)
        except:
            raise
        finally:
            delete_test_competitors(self._company_id)


    def test_insert_company_competition(self):
        #Competitor
        try:
            ##################### test basic insert #####################
            start_date = datetime(2012, 1, 1)
            end_date = datetime(2012, 12, 1)

            # insert two test competitors
            comps = [ Competitor.simple_init(self._company_id, self._away_company_id1, 1, start_date, end_date),
                      Competitor.simple_init(self._company_id, self._away_company_id2, 2, start_date) ]
            self._data_repository.insert_company_competition(comps)

            # select and verify that they were inserted properly
            competitors = select_competitive_companies_by_home_company_id(self._company_id)
            self.assertEqual(len(competitors), 2)


            self.assertEqual(competitors[0].home_company_id, self._company_id)
            self.assertEqual(competitors[0].away_company_id, self._away_company_id1)
            self.assertEqual(competitors[0].competition_strength, 1)
            self.assertEqual(competitors[0].assumed_start_date, start_date)
            self.assertEqual(competitors[0].assumed_end_date, end_date)

            self.assertEqual(competitors[1].home_company_id, self._company_id)
            self.assertEqual(competitors[1].away_company_id, self._away_company_id2)
            self.assertEqual(competitors[1].competition_strength, 2)
            self.assertEqual(competitors[1].assumed_start_date, start_date)
            self.assertIsNone(competitors[1].assumed_end_date)

            ##################### test competition_strength insert rule #####################
            # insert the same companies/strengths again and verify that one was re-inserted (null end date) and the other was not re-inserted
            self._data_repository.insert_company_competition(comps)
            competitors = select_competitive_companies_by_home_company_id(self._company_id)
            self.assertEqual(len(competitors), 3)

            # re-insert the same companies, but with different strengths
            comps[0].competition_strength = 3
            comps[1].competition_strength = 4
            self._data_repository.insert_company_competition(comps)

            # verify that this will insert the same home/away relationship with different strengths
            competitors = select_competitive_companies_by_home_company_id(self._company_id)
            self.assertEqual(len(competitors), 5)
            self.assertEqual(competitors[3].home_company_id, self._company_id)
            self.assertEqual(competitors[3].away_company_id, self._away_company_id1)
            self.assertEqual(competitors[3].competition_strength, 3)
            self.assertEqual(competitors[4].assumed_start_date, start_date)
            self.assertEqual(competitors[4].home_company_id, self._company_id)
            self.assertEqual(competitors[4].away_company_id, self._away_company_id2)
            self.assertEqual(competitors[4].competition_strength, 4)
            self.assertEqual(competitors[4].assumed_start_date, start_date)
        except:
            raise
        finally:
            delete_test_competitors(self._company_id)


    def test_close_old_company_competitors(self):
        try:
            # create two competition records
            insert_test_competitor(self._company_id, self._away_company_id1)
            insert_test_competitor(self._company_id, self._away_company_id2)

            # select them and verify that there's no end dates
            competitors = select_competitive_companies_by_home_company_id(self._company_id)
            self.assertEqual(len(competitors), 2)
            self.assertEqual(competitors[0].away_company_id, self._away_company_id1)
            self.assertIsNone(competitors[0].assumed_end_date)
            self.assertEqual(competitors[1].away_company_id, self._away_company_id2)
            self.assertIsNone(competitors[1].assumed_end_date)

            # close both of the competitors
            self._data_repository.close_old_company_competitors([self._away_company_id1, self._away_company_id2], self._company_id, "2012-01-01")

            # select again and verify that both competitors have been closed
            competitors = select_competitive_companies_by_home_company_id(self._company_id)
            self.assertEqual(len(competitors), 2)
            self.assertEqual(competitors[0].away_company_id, self._away_company_id1)
            self.assertEqual(competitors[0].assumed_end_date, datetime(2012, 1, 1))
            self.assertEqual(competitors[1].away_company_id, self._away_company_id2)
            self.assertEqual(competitors[1].assumed_end_date, datetime(2012, 1, 1))
        except:
            raise
        finally:
            delete_test_competitors(self._company_id)

if __name__ == '__main__':
    unittest.main()