import unittest
import datetime
from common.business_logic.company_info import CompanyInfo
from common.utilities.inversion_of_control import dependencies
from geoprocessing.business_logic.config import Config
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository

__author__ = 'erezrubinstein'


class CompanyInfoTests(unittest.TestCase):

    def setUp(self):
        self.config = Config().instance
        dependencies.register_dependency("Config", self.config)
        self.sql_provider = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", self.sql_provider)

    def tearDown(self):
        dependencies.clear()


    def test_company_info(self):
        file_1 = 'woot_2012_12_25.xlsx'
        file_2 = 'chicken_2012_02_24.xlsx'

        # mock up fake company
        company_1_info = CompanyInfo("test company 1", ["test industry_1"], ["test competitor_1"], ["test store_1"], file_1)
        company_2_info = CompanyInfo("test company 2", ["test industry_2"], ["test competitor_2"], ["test store_2"], file_2)

        # quick check on CompanyInfo's date object.
        self.assertEqual(company_1_info.company_name, 'test company 1')
        self.assertEqual(company_1_info.as_of_date, datetime.datetime(2012, 12, 25))
        self.assertEqual(company_1_info.sectors[0], 'test industry_1')
        self.assertEqual(company_1_info.competitors[0], 'test competitor_1')
        self.assertEqual(company_1_info.parsed_records[0], 'test store_1')

        self.assertEqual(company_2_info.company_name, 'test company 2')
        self.assertEqual(company_2_info.sectors[0], 'test industry_2')
        self.assertEqual(company_2_info.competitors[0], 'test competitor_2')
        self.assertEqual(company_2_info.parsed_records[0], 'test store_2')
        self.assertEqual(company_2_info.as_of_date, datetime.datetime(2012, 02, 24))


if __name__ == '__main__':
    unittest.main()