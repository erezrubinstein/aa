from __future__ import division
from tests.integration_tests.economics_tests.implementation.economics_loader_test_collection import EconomicsLoaderTestCollection
from tests.integration_tests.framework.svc_test_case import ServiceTestCase
from core.service.svc_master_data_storage.mds_api import app as mds_app
from core.service.svc_raw_data_storage.rds_api import app as rds_app
import unittest


__author__ = "vgold"


class TestDataChecks(ServiceTestCase):

    @classmethod
    def initialize_class(cls):

        cls.apps = {"MDS": mds_app, "RDS": rds_app}
        cls.svc_key = "MDS"
        cls.test_colls = {
            "ECONOMICS": EconomicsLoaderTestCollection
        }

    def test_economics_test_load_labor_data_from_rds_to_mds(self):
        self.tests["ECONOMICS"].economics_test_load_labor_data_from_rds_to_mds()

    def test_economics_test_load_econ_data_to_mds(self):
        self.tests["ECONOMICS"].economics_test_load_econ_data_to_mds()


if __name__ == '__main__':
    unittest.main()
