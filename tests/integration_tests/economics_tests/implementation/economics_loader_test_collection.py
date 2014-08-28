from __future__ import division
from core.service.utilities.helpers import get_code_root
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from economics.process_data.monthly_us_econ_labor_census import MonthlyEconLoaderRunner
from economics.raw_data.monthly_us_labor_data_to_mds import MonthlyLaborGatheringRunner
from common.utilities.inversion_of_control import Dependency
from common.helpers.configuration_helper import read_config_yml_file
from pymongo import mongo_client
import os


__author__ = "vgold"


class EconomicsLoaderTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "economics_loader_test_collection.py"
        self.context = {
            "user_id": self.user_id,
            "source": self.source
        }

        # some pycharm/unittest param that blocks you from seeing a diff failure in an assert statement if it's too long
        self.maxDiff = None
        self.main_param = Dependency("CoreAPIParamsBuilder").value

        self.conn = mongo_client.MongoClient("localhost", 27017)
        self.mds = self.conn["itest_mds"]

    def setUp(self):

        self.mds_access.call_delete_reset_database()
        self.rds_access.call_delete_reset_database()

    def tearDown(self):
        pass

    ##------------------------------------------------##

    def economics_test_load_labor_data_from_rds_to_mds(self):
        """
        Run through labor loader with files that only have Alaska data and itest config.
        """
        file_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
        zipped_filename = file_base_path + "/US_labor_data_2013_09_06.tar.gz"
        filename = "US_labor_data_2013_09_06"
        rds_path = "/economics/unemployment"
        self.__upload_file_to_rds(zipped_filename, filename, rds_path)

        # FEATURE
        code_root = get_code_root()
        config_file_path = os.path.join(code_root, 'economics', 'config.yml')
        config = read_config_yml_file(config_file_path)["config_itest"]

        # DO MAGIC
        runner = MonthlyLaborGatheringRunner(self.logger, config, [])
        runner.run()

        labor_count1 = self.mds.labor.count()
        self.test_case.assertTrue(labor_count1 > 0)

        # DO IT AGAIN TO TEST IDEMPOTENCE
        runner = MonthlyLaborGatheringRunner(self.logger, config, [])
        runner.run()

        labor_count2 = self.mds.labor.count()
        self.test_case.assertEqual(labor_count1, labor_count2)

    def economics_test_load_econ_data_to_mds(self):
        """
        Run through econ loader with files that only have Alaska data and itest config.
        """
        file_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

        zipped_filename = file_base_path + "/US_labor_data_2013_09_06.tar.gz"
        filename = "US_labor_data_2013_09_06"
        rds_path = "/economics/unemployment"
        self.__upload_file_to_rds(zipped_filename, filename, rds_path)

        zipped_filename = file_base_path + "/US_Census_Counties_2013_09_06.tar.gz"
        filename = "US_Census_Counties_2013_09_06"
        rds_path = "/economics/census/county"
        self.__upload_file_to_rds(zipped_filename, filename, rds_path)

        zipped_filename = file_base_path + "/US_Census_Places_2013_09_06.tar.gz"
        filename = "US_Census_Places_2013_09_06"
        rds_path = "/economics/census/place"
        self.__upload_file_to_rds(zipped_filename, filename, rds_path)

        # FEATURE
        code_root = get_code_root()
        config_file_path = os.path.join(code_root, 'economics', 'config.yml')
        config = read_config_yml_file(config_file_path)["config_itest"]

        # DO MAGIC
        runner = MonthlyEconLoaderRunner(self.logger, config, [])
        runner.run()

        econ_count1 = self.mds.econ.count()
        self.test_case.assertTrue(econ_count1 > 0)

        # DO IT AGAIN TO TEST IDEMPOTENCE
        runner = MonthlyEconLoaderRunner(self.logger, config, [])
        runner.run()

        econ_count2 = self.mds.econ.count()

        self.test_case.assertEqual(econ_count1, econ_count2)

    def __upload_file_to_rds(self, zipped_filename, filename, rds_path):

        with open(zipped_filename, 'rb') as f:
            post_file = {
                "file": (filename + ".tar.gz", f)
            }
            self.main_access.rds.call_post_file(rds_path, post_file, context=self.context)
