from common.helpers.common_dependency_helper import register_common_mox_dependencies
from core.common.utilities.errors import InputError
from core.service.svc_analytics.implementation.analytics_service import AnalyticsService
from core.service.svc_analytics.config import analytics_config_unit_test as cfg_module
from common.helpers.mock_providers.mock_logger import MockLogger
from common.data_access import mongo_access
import unittest
import mox


__author__ = 'jsternberg'


class AnalyticsServiceTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(AnalyticsServiceTests, self).setUp()

        # convert config module to self.cfg dict
        self.__set_cfg()
        self.logger = MockLogger()

        self.mock_mongo_access = self.__get_mock_mongo_access()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        self.stub_default_calcs = {"rows":[
            {
                "name": "Calc A",
                "input": {
                    "entity_type": "company",
                    "fields": [
                        "id",
                        "no_dependencies.initial_data"
                    ]
                },
                "output": {
                    "target_entity_type": "company",
                    "key": "data.analytics.alpha"
                }
            },
            {
                "name": "Calc B - Depends on A",
                "input": {
                    "entity_type": "company",
                    "fields": [
                        "data.analytics.alpha"
                    ]
                },
                "output": {
                    "target_entity_type": "company",
                    "key": "data.analytics.bravo"
                }
            },
            {
                "name": "Calc C - Depends on B",
                "input": {
                    "entity_type": "company",
                    "fields": [
                        "data.analytics.bravo.primary"
                    ]
                },
                "output": {
                    "target_entity_type": "trade_area",
                    "key": "data.analytics.chicken.woot"
                }
            },
            {
                "name": "Calc D - Depends on A and B",
                "input": {
                    "entity_type": "company",
                    "fields": [
                        "data.analytics.alpha",
                        "data.analytics.bravo.baz"
                    ]
                },
                "output": {
                    "target_entity_type": "trade_area",
                    "key": "data.analytics.delta"
                }
            },
            {
                "name": "Calc E",
                "input": {
                    "entity_type": "company",
                    "fields": [
                        "data.analytics.delta" # Calc D delta goes in the trade area entity
                    ]
                },
                "output": {
                    "target_entity_type": "company",
                    "key": "data.analytics.echo"
                }
            },
            {
                "name": "Calc F - Depends on A and E",
                "input": {
                    "entity_type": "company",
                    "fields": [
                        "data.analytics.alpha",
                        "data.analytics.echo"
                    ]
                },
                "output": {
                    "target_entity_type": "company",
                    "key": "data.analytics.foxtrot"
                }
            },
            {
                "name": "Calc G - Depends on D",
                "input": {
                    "entity_type": "trade_area",
                    "fields": [
                        "data.analytics.chicken", # does not include the woot key
                        "data.analytics.bravo",   # Calc B bravo goes in company entity
                        "data.analytics.delta"
                    ]
                },
                "output": {
                    "target_entity_type": "company",
                    "key": "data.analytics.golf"
                }
            },
            {
                "name": "Calc H - Depends on C and D",
                "input": {
                    "entity_type": "trade_area",
                    "fields": [
                        "data.analytics.chicken.woot",
                        "data.analytics.delta"
                    ]
                },
                "output": {
                    "target_entity_type": "company",
                    "key": "data.analytics.hotel"
                }
            }
        ]}


    def tearDown(self):

        self.mox.UnsetStubs()

    def test_init_service(self):
        """ Test basic service initialization."""

        # service loads ref data from mongodb on init
        stub_ref_data = [{"foo":"bar"}]

        # stub out mongodb data access before init
        self.mock_mongo_access.find_one(mox.IsA(basestring)).AndReturn(stub_ref_data)

        # replay all
        self.mox.ReplayAll()

        # go!
        analytics_service = AnalyticsService(self.cfg, self.logger)

        # make sure we have a db and ref data, and we're initialized
        self.assertEqual(analytics_service.db, self.mock_mongo_access)
        self.assertEqual(analytics_service.refdata, stub_ref_data)
        self.assertTrue(analytics_service.is_initialized)

    def test_reset_service_data(self):
        """ Test that resetting service data calls the proper underlying functions.
        """

        # stub out mongodb data access before init
        stub_ref_data = [{"foo":"bar"}]
        self.mock_mongo_access.find_one(mox.IsA(basestring)).AndReturn(stub_ref_data)

        # replay all, to begin, because of self.mock_mongo_access, in setUp
        self.mox.ReplayAll()

        analytics_service = AnalyticsService(self.cfg, self.logger)

        self.mox.StubOutWithMock(analytics_service, "_AnalyticsService__connect_db")
        self.mox.StubOutWithMock(analytics_service, "reset_reference_data")
        self.mox.StubOutWithMock(analytics_service, "reset_default_calcs")

        analytics_service._AnalyticsService__connect_db().AndReturn(None)
        analytics_service.reset_reference_data().AndReturn(None)
        analytics_service.reset_default_calcs().AndReturn(None)

        # replay all, again, for this test's mocks
        self.mox.ReplayAll()

        #go!
        analytics_service.reset_service_data()

    def test_reset_reference_data(self):
        """ Test that resetting reference data calls the proper underlying functions.
        """

        # stub out mongodb data access before init
        stub_ref_data = [{"foo":"bar"}]
        self.mock_mongo_access.find_one(mox.IsA(basestring)).AndReturn(stub_ref_data)

        # replay all, to begin, because of self.mock_mongo_access, in setUp
        self.mox.ReplayAll()

        analytics_service = AnalyticsService(self.cfg, self.logger)

        # create stubs
        stub_ref_data = [{"foo":"bar"}]
        self.mox.StubOutWithMock(analytics_service, "_AnalyticsService__read_default_reference_data")
        self.mox.StubOutWithMock(analytics_service, "_AnalyticsService__load_reference_data")

        # start recording again
        self.mox.ResetAll()

        #record internal calls
        analytics_service._AnalyticsService__read_default_reference_data().AndReturn(stub_ref_data)
        self.mock_mongo_access.drop(mox.IsA(basestring)).AndReturn(None)
        self.mock_mongo_access.insert(mox.IsA(basestring), stub_ref_data).AndReturn(None)
        analytics_service._AnalyticsService__load_reference_data().AndReturn(None)

        # replay all, again, for this test's mocks
        self.mox.ReplayAll()

        #go!
        analytics_service.reset_reference_data()

    def test_reset_default_calcs(self):
        """ Test that resetting default calcs calls the proper underlying functions.
        """

        # stub out mongodb data access before init
        stub_ref_data = [{"foo":"bar"}]
        self.mock_mongo_access.find_one(mox.IsA(basestring)).AndReturn(stub_ref_data)

        # replay all, to begin, because of self.mock_mongo_access, in setUp
        self.mox.ReplayAll()

        analytics_service = AnalyticsService(self.cfg, self.logger)

        # create stubs
        stub_default_calcs = [{"foo":"bar"}]
        self.mox.StubOutWithMock(analytics_service, "_AnalyticsService__read_default_calcs")

        # start recording again
        self.mox.ResetAll()

        #record internal calls
        analytics_service._AnalyticsService__read_default_calcs().AndReturn(stub_default_calcs)
        self.mock_mongo_access.drop(mox.IsA(basestring)).AndReturn(None)
        self.mock_mongo_access.insert(mox.IsA(basestring), stub_default_calcs).AndReturn(None)

        # replay all, again, for this test's mocks
        self.mox.ReplayAll()

        #go!
        analytics_service.reset_default_calcs()


    def test_find_calcs_ordered(self):
        """make sure that super complicated graph gets topsorted correctly"""

        # stub out mongodb data access before init
        stub_ref_data = [{"foo":"bar"}]
        self.mock_mongo_access.find_one(mox.IsA(basestring)).AndReturn(stub_ref_data)

        self.mox.ReplayAll()

        analytics_service = AnalyticsService(self.cfg, self.logger)

        # start recording again
        self.mox.ResetAll()

        self.mox.StubOutWithMock(analytics_service.db, "find_filter_sort_page")
        self.mox.StubOutWithMock(analytics_service.db, "alive")

        #record internal calls
        analytics_service.db.find_filter_sort_page("calcs", query={"skip_calculation": { "$ne": True }}, fields=["engine", "engine_module", "input", "output", "name", "dependent_on", "skip_calculation", "multi_outputs"]).AndReturn(self.stub_default_calcs)

        self.mox.ReplayAll()

        ordered_list = [calc["name"] for calc in analytics_service.find_calcs_ordered([], {})]

        # ROUGH ORDER
        # "Calc A",
        # "Calc E",
        # "Calc B - Depends on A",
        # "Calc F - Depends on A and E",
        # "Calc C - Depends on B",
        # "Calc D - Depends on A and B",
        # "Calc H - Depends on C and D",
        # "Calc G - Depends on D"

        self.assertTrue(ordered_list.index("Calc B - Depends on A") > ordered_list.index("Calc A"))
        self.assertTrue(ordered_list.index("Calc F - Depends on A and E") > ordered_list.index("Calc A"))
        self.assertTrue(ordered_list.index("Calc F - Depends on A and E") > ordered_list.index("Calc E"))
        self.assertTrue(ordered_list.index("Calc C - Depends on B") > ordered_list.index("Calc B - Depends on A"))
        self.assertTrue(ordered_list.index("Calc D - Depends on A and B") > ordered_list.index("Calc A"))
        self.assertTrue(ordered_list.index("Calc D - Depends on A and B") > ordered_list.index("Calc B - Depends on A"))
        self.assertTrue(ordered_list.index("Calc H - Depends on C and D") > ordered_list.index("Calc C - Depends on B"))
        self.assertTrue(ordered_list.index("Calc H - Depends on C and D") > ordered_list.index("Calc D - Depends on A and B"))
        self.assertTrue(ordered_list.index("Calc G - Depends on D") > ordered_list.index("Calc D - Depends on A and B"))


    def test_find_calcs_ordered_catches_circular_dependency(self):

        # stub out mongodb data access before init
        stub_ref_data = [{"foo":"bar"}]
        self.mock_mongo_access.find_one(mox.IsA(basestring)).AndReturn(stub_ref_data)

        self.mox.ReplayAll()

        analytics_service = AnalyticsService(self.cfg, self.logger)

        self.mox.StubOutWithMock(analytics_service.db, "find_filter_sort_page")

        # start recording again
        self.mox.ResetAll()

        # create a circular dependency
        circular = self.stub_default_calcs
        circular["rows"][0]["input"]["fields"]=["data.analytics.hotel"]

        #record internal calls
        analytics_service.db.find_filter_sort_page("calcs", query={"skip_calculation": { "$ne": True }}, fields=["engine", "engine_module", "input", "output", "name", "dependent_on", "skip_calculation", "multi_outputs"]).AndReturn(circular)

        self.mox.ReplayAll()

        with self.assertRaises(InputError) as context:
            analytics_service.find_calcs_ordered([], {})
        self.assertTrue("Circular calc" in context.exception.message)



##-----------------------private methods---------------------------------------------------##

    def __set_cfg(self):
        cfg_rec = {}
        for key in dir(cfg_module):
            if key.isupper():
                cfg_rec[key] = getattr(cfg_module, key)
        self.cfg = cfg_rec

    def __get_mock_mongo_access(self):
        mock = self.mox.CreateMock(mongo_access.MongoAccess)
        self.mox.StubOutWithMock(mongo_access, "MongoAccess")
        mongo_access.MongoAccess(self.cfg["MONGODB_DB"], self.cfg["MONGODB_HOST"],
                                                     self.cfg["MONGODB_PORT"],
                                                     coll_names=mox.IsA(list),
                                                     logger=self.logger,
                                                     replica_set=self.cfg["MONGODB_REPLICA_SET"],
                                                     read_preference=self.cfg["MONGODB_READ_PREFERENCE"],
                                                     tag_sets=self.cfg["MONGODB_TAG_SETS"],
                                                     autoreconnect_max_retries=self.cfg["MONGODB_AUTORECONNECT_MAX_RETRIES"],
                                                     autoreconnect_retry_interval=self.cfg["MONGODB_AUTORECONNECT_RETRY_INTERVAL"],
                                                     autoreconnect_attempt_log_frequency=self.cfg["MONGODB_AUTORECONNECT_ATTEMPT_LOG_FREQUENCY"]).AndReturn(mock)
        return mock



##-------------------------------------------------------------------------------------------##

if __name__ == '__main__':
    unittest.main()
