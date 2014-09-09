import unittest
from geoprocessing.business_logic.enums import TradeAreaThreshold
from common.utilities.inversion_of_control import dependencies
from geoprocessing.geoprocessors.proximity.gp5_ArcGIS_drive_times import GP5ArcGISDriveTimeProcessor
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_sql_data_repository import MockSQLDataRepository
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockRestProvider
from geoprocessing.business_logic.business_objects.store import Store

__author__ = 'jsternberg'

class GP5ArcGISDriveTimeTests(unittest.TestCase):

    def setUp(self):
        # set up mock dependencies
        register_mock_dependencies()
        self._rest_provider = MockRestProvider()
        self._sql_provider = MockSQLDataRepository()

        # set up test store
        self._store = Store.simple_init_with_address(42, 14107, -100.00, 45.00)
        self._sql_provider.stores[self._store.store_id] = self._store
        self._store.address_id = 10
        self._sql_provider.addresses[10] = self._store.address
        self._threshold = TradeAreaThreshold.LatitudeLongitudeDecimal

    def tearDown(self):
        dependencies.clear()

    def test_initialize(self):
        gp5 = GP5ArcGISDriveTimeProcessor(self._threshold)

        self.assertEqual(gp5._threshold, self._threshold)
        self.assertEqual(gp5._away_store_id_dt_response, {})

