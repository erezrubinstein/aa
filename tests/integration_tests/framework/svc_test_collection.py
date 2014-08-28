from __future__ import division


__author__ = "vgold"


class ServiceTestCollection(object):

    def __init__(self, deps):
        """
        Set class variables to be available to class when setUpClass is called
        """
        self.config = deps["config"]
        self.logger = deps["logger"]
        self.main_access = deps["main_access"]
        self.mds_access = deps["mds_access"]
        self.rds_access = deps["rds_access"]
        self.entity_matcher_access = deps["entity_matcher_access"]
        self.analytics_access = deps["analytics_access"]
        self.wfs_access = deps["wfs_access"]
        self.web_access = deps["web_access"]
        self.source = "svc_test_collection.py"
        self.user_id = "integration test"
        self.context = {"source": self.source, "user_id": self.user_id}
        self.test_case = None

    ##----------------------## Methods to be overridden by developer ##--------------------------##

    # These methods must remain stubbed here, because they are called automatically from ServiceTestCase

    def initialize(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

###################################################################################################
