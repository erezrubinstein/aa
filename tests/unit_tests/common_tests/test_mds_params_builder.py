from datetime import datetime
from mox import MoxTestBase
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.service_access.params_builder.mds_params_builder import ParamsBuilderMDS
from common.service_access.utilities.errors import ServiceParamsError
from common.utilities.inversion_of_control import dependencies, Dependency

__author__ = 'erezrubinstein'

import unittest


class MDSParamsBuilderTests(MoxTestBase):
    def setUp(self):
        # call super init
        super(MDSParamsBuilderTests, self).setUp()
        
        # register mox dependencies
        register_common_mox_dependencies(self.mox)

        # get mocked params builder
        self.mds_params_builder = Dependency("CoreAPIParamsBuilder").value.mds


    def tearDown(self):
        dependencies.clear()


    def test_mds_params_interval_filter__one_date(self):
        # get params with one date
        date = datetime(2013, 1, 1)
        interval_filter = {
            "dates": [date]
        }
        params = self.mds_params_builder.create_params(resource = "find_entities_raw", interval_filter = interval_filter)

        # verify it gets created correctly
        self.assertEqual(params["params"]["interval_filter"], interval_filter)

        # make sure you get an error if the field isn't a date
        self.assertRaises(ServiceParamsError, self.mds_params_builder.create_params, resource = "find_entities_raw", interval_filter = str(date))


    def test_mds_params_interval_filter__two_date(self):
        # get params with one date
        date = datetime(2013, 1, 1)
        interval_filter = {
            "dates": [date, date]
        }
        params = self.mds_params_builder.create_params(resource = "find_entities_raw", interval_filter = interval_filter)

        # verify it gets created correctly
        self.assertEqual(params["params"]["interval_filter"], interval_filter)

        # make sure you get an error if the field isn't a date
        self.assertRaises(ServiceParamsError, self.mds_params_builder.create_params, resource = "find_entities_raw", interval_filter = str(date))


    def test_mds_params_interval_filter__date_range(self):
        # get params with two dates
        date_from = datetime(2012, 1, 1)
        date_to = datetime(2013, 1, 1)
        interval_filter = {
            "date_range": [date_from, date_to]
        }
        params = self.mds_params_builder.create_params(resource = "find_entities_raw", interval_filter = interval_filter)

        # verify it gets created correctly
        self.assertEqual(params["params"]["interval_filter"], interval_filter)

        # make sure you get an error if there are more or less than 2 parameters
        interval_filter["date_range"] = [date_from, date_to, date_from]
        self.assertRaises(ServiceParamsError, self.mds_params_builder.create_params, resource = "find_entities_raw", interval_filter = interval_filter)
        interval_filter["date_range"] = [date_from]
        self.assertRaises(ServiceParamsError, self.mds_params_builder.create_params, resource = "find_entities_raw", interval_filter = interval_filter)

        # make sure you get an error if either of the parameters is not a date
        interval_filter["date_range"] = [str(date_from), date_to]
        self.assertRaises(ServiceParamsError, self.mds_params_builder.create_params, resource = "find_entities_raw", interval_filter = [str(date_from), date_to])
        interval_filter["date_range"] = [date_from, str(date_to)]
        self.assertRaises(ServiceParamsError, self.mds_params_builder.create_params, resource = "find_entities_raw", interval_filter = [date_from, str(date_to)])







if __name__ == '__main__':
    unittest.main()
