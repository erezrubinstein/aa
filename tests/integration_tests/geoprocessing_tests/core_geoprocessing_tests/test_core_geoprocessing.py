import unittest

from geoprocessing.geoprocessors.competition.gp8_core_trade_area_competition import GP8CoreTradeAreaCompetition
from geoprocessing.geoprocessors.competition.gp9_core_trade_area_competition_geo_json import GP9CoreTradeAreaCompetition
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from tests.integration_tests.geoprocessing_tests.core_geoprocessing_tests.implementation.gp14_test_collection import GP14TestCollection
from tests.integration_tests.geoprocessing_tests.core_geoprocessing_tests.implementation.gp16_test_collection import GP16TestCollection
from tests.integration_tests.geoprocessing_tests.core_geoprocessing_tests.implementation.gp22_test_collection import GP22TestCollection
from tests.integration_tests.geoprocessing_tests.core_geoprocessing_tests.implementation.gp7_test_collection import GP7TestCollection
from tests.integration_tests.geoprocessing_tests.core_geoprocessing_tests.implementation.gp8_and_gp9_test_collection \
    import GP8_GP9_TestCollection


__author__ = 'erezrubinstein'


class TestCoreGeoprocessing(ServiceTestCase):
    """
    Test case for Main Service Export Data functions.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {
            "MDS": mds_app,
            "WFS": wfs_app
        }
        cls.svc_key = "MDS"
        cls.test_colls = {
            "GP8_9": GP8_GP9_TestCollection,
            "GP14": GP14TestCollection,
            "GP7": GP7TestCollection,
            "GP16": GP16TestCollection,
            "GP22": GP22TestCollection
        }
        cls.svc_main_exempt = {}

    # ----------------------------- GP7 ----------------------------- #

    def test_gp7_does_not_override_analytics(self):
        self.tests["GP7"].test_gp7_does_not_override_analytics()

    # ----------------------------- GP8 ----------------------------- #

    def test_simple_with_only_competition__gp8(self):
        self.tests["GP8_9"].test_simple_with_only_competition(GP8CoreTradeAreaCompetition("DistanceMiles10"))

    def test_simple_with_only_monopoly__gp8(self):
        self.tests["GP8_9"].test_simple_with_only_monopoly(GP8CoreTradeAreaCompetition("DistanceMiles10"))

    def test_complex_with_competition_and_monopolies__gp8(self):
        self.tests["GP8_9"].test_complex_with_competition_and_monopolies(GP8CoreTradeAreaCompetition("DistanceMiles10"))

    def test_monopolies_bug_with_closed_store__gp8(self):
        self.tests["GP8_9"].test_monopolies_bug_with_closed_store(GP8CoreTradeAreaCompetition("DistanceMiles10"))

    def test_monopolies_bug_with_no_monopolies_to_close__gp8(self):
        self.tests["GP8_9"].test_monopolies_bug_with_no_monopolies_to_close(GP8CoreTradeAreaCompetition("DistanceMiles10"))

    # ----------------------------- GP9 ----------------------------- #

    def test_simple_with_only_competition__gp9(self):
        self.tests["GP8_9"].test_simple_with_only_competition(GP9CoreTradeAreaCompetition())

    def test_simple_with_only_monopoly__gp9(self):
        self.tests["GP8_9"].test_simple_with_only_monopoly(GP9CoreTradeAreaCompetition())

    def test_complex_with_competition_and_monopolies__gp9(self):
        self.tests["GP8_9"].test_complex_with_competition_and_monopolies(GP9CoreTradeAreaCompetition())

    def test_monopolies_bug_with_closed_store__gp9(self):
        self.tests["GP8_9"].test_monopolies_bug_with_closed_store(GP9CoreTradeAreaCompetition())

    def test_monopolies_bug_with_no_monopolies_to_close__gp9(self):
        self.tests["GP8_9"].test_monopolies_bug_with_no_monopolies_to_close(GP9CoreTradeAreaCompetition())

    def test_competition_weights__industries_with_different_directional_weights(self):
        self.tests["GP8_9"].test_competition_weights__industries_with_different_directional_weights(GP9CoreTradeAreaCompetition())

    # ----------------------------- GP14 ----------------------------- #

    def test_gp14_simple_with_exact_match(self):
        self.tests["GP14"].test_simple_with_exact_match()

    # ----------------------------- GP16 ----------------------------- #

    def test_gp16__simple(self):
        self.tests["GP16"].test_simple_run()

    def test_gp16__mixed_weather_stations(self):
        self.tests["GP16"].test_mixed_weather_stations()

    # ----------------------------- GP22 ----------------------------- #

    def test_gp22__simple(self):
        self.tests["GP22"].test_simple_gp_22_run()

if __name__ == '__main__':
    unittest.main()
