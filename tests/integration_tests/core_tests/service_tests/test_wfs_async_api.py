from __future__ import division
from tests.integration_tests.core_tests.service_tests.implementation.wfs_async_test_collection import WFSAsyncTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_raw_data_storage.rds_api import app as rds_app
from core.service.svc_analytics.analytics_api import app as analytics_app
from core.service.svc_workflow.workflow_api import app as wfs_app
from core.service.svc_main.main_api import app as main_app
import unittest


__author__ = "erezrubinstein"


class Test_WFS_ASYNC_API(ServiceTestCase):
    """
    Test case for Workflow Service.
    See ServiceTestCase class for full documentation.
    """
    @classmethod
    def initialize_class(cls):
        """
        Assign values to inform the setUpClass class method of ServiceTestCase.
        See ServiceTestCase class for full documentation.
        """
        cls.apps = {
            "MAIN": main_app,
            "MDS": mds_app,
            "WFS": wfs_app,
            "RDS": rds_app,
            "ANALYTICS": analytics_app
        }
        cls.svc_key = "WFS"
        cls.test_colls = {"WFS_ASYNC": WFSAsyncTestCollection}

        # start celery
        cls.start_celery = True

    def test_wfs_async_task(self):
        self.tests["WFS_ASYNC"].wfs_test_async_task()

    def test_wfs_async_task__insert_wfs_task_false(self):
        self.tests["WFS_ASYNC"].wfs_test_async_task__insert_wfs_task_false()

    def test_wfs_company_analytics_plan_b(self):
        self.tests["WFS_ASYNC"].wfs_company_analytics_plan_b()

    # TODO: get this working. It doesn't quite work.
    #def test_wfs_task_custom_on_failure(self):
    #    self.tests["WFS_ASYNC"].wfs_task_custom_on_failure()


if __name__ == '__main__':
    unittest.main()
