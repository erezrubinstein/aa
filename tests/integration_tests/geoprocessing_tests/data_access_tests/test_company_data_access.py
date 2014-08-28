from datetime import datetime
import unittest
from common.business_logic.company_info import  Sector
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import select_count_companies_by_name, delete_test_company, insert_test_company, select_company_by_id, delete_test_company_sector, delete_test_sector, insert_test_company_sector, insert_test_sector, select_sectors_for_company, select_company_sectors_by_id

__author__ = 'erezrubinstein'


class CompanyDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager)
        cls._data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._data_repository)

        # insert test data
        cls.company_id = insert_test_company()
        cls.sector_id1 = insert_test_sector("UNITTESTSECTOR_1")
        cls.sector_id2 = insert_test_sector("UNITTESTSECTOR_2")
        cls.company_sector_id1 = insert_test_company_sector(cls.sector_id1, cls.company_id)
        cls.company_sector_id2 = insert_test_company_sector(cls.sector_id2, cls.company_id)

    @classmethod
    def tearDownClass(cls):
        # delete test data
        delete_test_company_sector(cls.sector_id1)
        delete_test_company_sector(cls.sector_id2)
        delete_test_sector(cls.sector_id1)
        delete_test_sector(cls.sector_id2)
        delete_test_company(cls.company_id)
        
        dependencies.clear()

    def test_select_company_id_force_insert(self):
        try:
            crazy_company_name = "UNITTEST_SDGJKTHZLKJERLWEJFLSDUFLESRJ"

            # verify that no companies exist with the crazy name
            count_crazy_companies = select_count_companies_by_name(crazy_company_name)
            self.assertEqual(count_crazy_companies, 0)

            # select the company id, which will insert it
            company_id = self._data_repository.select_company_id_force_insert(crazy_company_name)
            self.assertGreater(company_id, 0)

            # verify that one company with the crazy name exists now
            count_crazy_companies = select_count_companies_by_name(crazy_company_name)
            self.assertEqual(count_crazy_companies, 1)

            # select the company again, and verify that the same id returned
            same_company_id = self._data_repository.select_company_id_force_insert(crazy_company_name)
            self.assertEqual(same_company_id, company_id)

            # verify that only one company exists after the second select
            count_crazy_companies = select_count_companies_by_name(crazy_company_name)
            self.assertEqual(count_crazy_companies, 1)
        except:
            raise
        finally:
            delete_test_company(company_id)


    def test_update_company_ticker(self):
        try:
            # create test company
            company_id = insert_test_company()

            # select company and verify ticker is empty
            company = select_company_by_id(company_id)
            self.assertEqual(company.company_id, company_id)
            self.assertEqual(company.ticker, "")

            # update ticker
            self._data_repository.update_company_ticker(company_id, "UNITTEST_ticker")

            # select company again and verify that it has the right ticker
            company = select_company_by_id(company_id)
            self.assertEqual(company.company_id, company_id)
            self.assertEqual(company.ticker, "UNITTEST_ticker")
        except:
            raise
        finally:
            delete_test_company(company_id)



    def test_select_sector_ids_for_company(self):
        # get sectors
        sectors = self._data_repository.select_sector_ids_for_company(self.company_id)

        # make sure all sectors that were inserted are selected properly
        self.assertEqual(len(sectors), 2)
        self.assertEqual(sectors[0], self.sector_id1)
        self.assertEqual(sectors[1], self.sector_id2)


    def test_insert_company_sectors(self):
        sectors = None
        sector1 = None
        sector2 = None
        try:
            # get sectors
            sectors = select_sectors_for_company(self.company_id)

            # make sure there are already 2 sectors (created in test class init)
            self.assertEqual(len(sectors), 2)

            # insert two new sectors
            sector1 = Sector("UNITTEST_SECTOR1", True)
            sector2 = Sector("UNITTEST2", False)
            sectors = [sector1, sector2]
            self._data_repository.insert_company_sectors(sectors, self.company_id, "2012-01-01")

            # select sectors again
            sectors = select_sectors_for_company(self.company_id)

            # verify that there are now 4 sectors, and make sure their values are correct
            self.assertEqual(len(sectors), 4)
        except:
            raise
        finally:
            delete_test_company_sector(sector1.sector_id)
            delete_test_company_sector(sector2.sector_id)
            delete_test_sector(sector1.sector_id)
            delete_test_sector(sector2.sector_id)


    def test_close_old_companies_sectors(self):
        try:
            # create new sector and add it to company
            sector1 = Sector("UNITTEST_SECTOR1241345", True)
            self._data_repository.insert_company_sectors([sector1], self.company_id, "2012-01-01")

            # select sectors and verify it's open
            sectors = select_company_sectors_by_id(sector1.sector_id)
            self.assertEqual(len(sectors), 1)
            self.assertEqual(sectors[0].sector_id, sector1.sector_id)
            self.assertIsNone(sectors[0].assumed_end_date)

            # close the sector
            self._data_repository.close_old_companies_sectors([sector1.sector_id], "2012-01-01")

            # select again and verify that it's closed
            sectors = select_company_sectors_by_id(sector1.sector_id)
            self.assertEqual(len(sectors), 1)
            self.assertEqual(sectors[0].sector_id, sector1.sector_id)
            self.assertEqual(sectors[0].assumed_end_date, datetime(2012, 1, 1))
        except:
            raise
        finally:
            delete_test_company_sector(sector1.sector_id)
            delete_test_sector(sector1.sector_id)


    def test_get_company_by_id(self):
        try:
            company = self._data_repository.get_company_by_id(self.company_id)
            self.assertEqual(company.company_id, self.company_id)
            self.assertEqual(company.ticker, '')
            self.assertEqual(company.name, 'UNITTESTCOMPANY')
        except:
            raise


    def test_select_all_companies(self):
        try:
            # insert another test company (other than above)
            company_id2 = insert_test_company("TESTTICKER", "UNITTESTCOMPANY_SELECT_ALL")

            # select all companies and get list of ids and company_names
            companies = self._data_repository.select_all_companies()
            company_ids = [company.company_id for company in companies]
            company_names = [company.name for company in companies]

            # verify both companies are there
            self.assertGreaterEqual(len(company_ids), 2)
            self.assertIn(self.company_id, company_ids)
            self.assertIn(company_id2, company_ids)
            self.assertIn("UNITTESTCOMPANY_SELECT_ALL", company_names)
            self.assertIn("UNITTESTCOMPANY", company_names)
        finally:
            delete_test_company(company_id2)

if __name__ == '__main__':
    unittest.main()