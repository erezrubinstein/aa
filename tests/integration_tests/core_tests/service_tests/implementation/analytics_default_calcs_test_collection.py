from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency


__author__ = "clairseager"


class AnalyticsDefaultCalcsTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "analytics_competition_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # some pycharm/unittest param that blocks you from seeing a diff failure in an assert statement if it's too long
        self.maxDiff = None
        self.main_param = Dependency("CoreAPIParamsBuilder").value

    def setUp(self):
        self.main_access.call_delete_reset_database()
        self.mds_access.call_delete_reset_database()
        self.analytics_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def analytics_test_circular_calc_dependencies(self):
        """The ordered calcs endpoint tests for circular dependencies. It will raise an error
        here if it finds one. """

        results = self.analytics_access.call_find_calcs_ordered(self.context)



###################################################################################################
