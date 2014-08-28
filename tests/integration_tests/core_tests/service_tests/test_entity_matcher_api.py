from __future__ import division
from core.service.svc_main.main_api import app as main_app
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_entity_matcher.entity_matcher_api import app as entity_matcher_app
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from tests.integration_tests.core_tests.service_tests.implementation.entity_matcher_test_collection import EntityMatcherTestCollection
import unittest

__author__ = "irsalmashhor"


###################################################################################################


class Test_Entity_Macther_API(ServiceTestCase):
    """
    Test case for Main Service.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {"ENTITY_MATCHER": entity_matcher_app, "MDS": mds_app, "MAIN": main_app}
        cls.svc_key = "ENTITY_MATCHER"
        cls.test_colls = {"ENTITY_MATCHER": EntityMatcherTestCollection}

##############################################################################################################
##
## Test methods must adhere to a strict naming convention:
##   1)  Name of test method must have "test_" prepended to the actual name of the test method
##       from the test collection.
##
##   2)  The actual test that should run must be called from within the test method (obviously).
##
##   3)  The actual test's name must start with its lowercase service key and an underscore ("mds_",
##       "main_", "rds_", "wfs_", etc.).
##
##   **  NOTE: The values of these test methods are dynamically overwritten to execute the setUp and
##       tearDown methods from the test's collection before and after the actual test specified. This
##       was a design decision, because the test collection should know how to set up and tear down
##       each test it houses.
##
##############################################################################################################

    ##-----------------------## Main Tests ##-------------------------##
    def test_entity_matcher_test_entity_vs_entity_exact_match(self):
        self.tests["ENTITY_MATCHER"].entity_matcher_test_entity_vs_entity_exact_match()

    def test_entity_matcher_test_entity_vs_entity_auto_link(self):
        self.tests["ENTITY_MATCHER"].entity_matcher_test_entity_vs_entity_auto_link()

    def test_entity_matcher_test_entity_vs_entity_inexact_match(self):
        self.tests["ENTITY_MATCHER"].entity_matcher_test_entity_vs_entity_inexact_match()

    def test_entity_matcher_test_entity_vs_entity_mismatch(self):
        self.tests["ENTITY_MATCHER"].entity_matcher_test_entity_vs_entity_mismatch()

    def test_entity_matcher_test_entity_vs_set(self):
        self.tests["ENTITY_MATCHER"].entity_matcher_test_entity_vs_set()

    def test_entity_matcher_test_set_vs_set(self):
        self.tests["ENTITY_MATCHER"].entity_matcher_test_set_vs_set()

    def test_entity_matcher_get_refdata(self):
        self.tests["ENTITY_MATCHER"].entity_matcher_get_refdata()

    def test_entity_matcher_train_retail_input_records(self):
        self.tests["ENTITY_MATCHER"].entity_matcher_train_retail_input_records()

if __name__ == '__main__':
    unittest.main()
