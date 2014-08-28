import unittest
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from geoprocessing.business_logic.business_objects.zip_code import ZipCode
from geoprocessing.business_logic.config import Config
from common.utilities.inversion_of_control import dependencies
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository

__author__ = 'jsternberg'

class ZipCodeTests(unittest.TestCase):
    def setUp(self):
        # set up mock dependencies
        dependencies.register_dependency("Config", Config().instance)
        self._data_repository = MockSQLDataRepository()
        dependencies.register_dependency("DataRepository", self._data_repository)

    def tearDown(self):
        dependencies.clear()

    def test_initialization(self):
        zip = ZipCode('12345')
        self.assertEqual(zip.zip_code,'12345')

    def test_centroid_for_unknown_zip(self):
        zip = ZipCode('99999')
        test_centroid = zip.centroid
        self.assertEqual(test_centroid, None)

    def test_zip_equals(self):
        zip1 = ZipCode('12345')
        zip2 = ZipCode('12345')
        self.assertEqual(zip1, zip2)

    def test_zip_standard_init(self):
        test_centroid = GeographicalCoordinate(10.24, 10.24)
        zip = ZipCode.standard_init('12345', test_centroid)
        self.assertEqual(zip.zip_code, '12345')
        self.assertEqual(zip.centroid, test_centroid)

    def test_select_by_zip_code(self):
        # mock up centroid
        expected_centroid = GeographicalCoordinate(10.24, 10.24)
        self._data_repository.zips_dict['12345'] = expected_centroid

        # get expected zip object and store in the mock data repo
        expected_zip = ZipCode.standard_init('12345', expected_centroid)
        self._data_repository.zips = expected_zip

        # run and verify
        zip = ZipCode.select_by_zip_code('12345')
        self.assertEqual(zip, expected_zip)

