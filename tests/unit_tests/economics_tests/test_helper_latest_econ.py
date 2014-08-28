from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from economics.helpers.helpers import get_latest_econ_month
import datetime
import unittest
import mox

__author__ = 'jsternberg'


class EconomicsHelperLatestEconTests(mox.MoxTestBase):

    def setUp(self):
        super(EconomicsHelperLatestEconTests, self).setUp()

        # set up mocks
        register_common_mox_dependencies(self.mox)
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.main_param = Dependency("CoreAPIParamsBuilder").value

        self.context = {
            "user": "Alfred E. Neuman",
            "source": "What? Me worry?"
        }

    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()

    def test_get_latest_econ_month__basic(self):

        self.mox.StubOutWithMock(self.mock_main_access.mds, "call_find_entities_raw")

        query = {}
        fields = ["data.econ_count_by_date"]
        sort = [["data.rds_file_id", -1]]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   sort=sort, limit=1)["params"]

        mock_stats = [
            {
                "data": {
                    "econ_count_by_date": [
                        {
                            "count": 198484,
                            "date": "2014-01-01T00:00:00"
                        },
                        {
                            "count": 4860,
                            "date": 2013
                        },
                        {
                            "count": 198448,
                            "date": "2013-12-01T00:00:00"
                        },
                        {
                            "count": 198448,
                            "date": "2013-11-01T00:00:00"
                        },
                        {
                            "count": 198448,
                            "date": "2013-10-01T00:00:00"
                        }
                    ]
                }
            }
        ]

        self.mock_main_access.mds.call_find_entities_raw("econ_stats", params, context=self.context,
                                                         encode_and_decode_results=False).AndReturn(mock_stats)

        # replay mode
        self.mox.ReplayAll()

        expected = datetime.datetime(2014, 1, 1)
        latest = get_latest_econ_month(self.main_param, self.mock_main_access, context=self.context)

        self.assertEqual(latest, expected)

    def test_get_latest_econ_month__real_dates(self):

        self.mox.StubOutWithMock(self.mock_main_access.mds, "call_find_entities_raw")

        query = {}
        fields = ["data.econ_count_by_date"]
        sort = [["data.rds_file_id", -1]]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   sort=sort, limit=1)["params"]

        mock_stats = [
            {
                "data": {
                    "econ_count_by_date": [
                        {
                            "count": 198484,
                            "date": datetime.datetime(2014, 1, 1)
                        },
                        {
                            "count": 4860,
                            "date": 2013
                        },
                        {
                            "count": 198448,
                            "date": datetime.datetime(2013, 12, 1)
                        },
                        {
                            "count": 198448,
                            "date": datetime.datetime(2013, 11, 1)
                        },
                        {
                            "count": 198448,
                            "date": datetime.datetime(2013, 10, 1)
                        }
                    ]
                }
            }
        ]

        self.mock_main_access.mds.call_find_entities_raw("econ_stats", params, context=self.context,
                                                         encode_and_decode_results=False).AndReturn(mock_stats)

        # replay mode
        self.mox.ReplayAll()

        expected = datetime.datetime(2014, 1, 1)
        latest = get_latest_econ_month(self.main_param, self.mock_main_access, context=self.context)

        self.assertEqual(latest, expected)

    def test_get_latest_econ_month__latest_month_incomplete(self):

        self.mox.StubOutWithMock(self.mock_main_access.mds, "call_find_entities_raw")

        query = {}
        fields = ["data.econ_count_by_date"]
        sort = [["data.rds_file_id", -1]]
        params = self.main_param.mds.create_params(resource="find_entities_raw", query=query, entity_fields=fields,
                                                   sort=sort, limit=1)["params"]

        mock_stats = [
            {
                "data": {
                    "econ_count_by_date": [
                        {
                            "count": 180000,
                            "date": datetime.datetime(2014, 1, 1)
                        },
                        {
                            "count": 4860,
                            "date": 2013
                        },
                        {
                            "count": 198448,
                            "date": datetime.datetime(2013, 12, 1)
                        },
                        {
                            "count": 198448,
                            "date": datetime.datetime(2013, 11, 1)
                        },
                        {
                            "count": 198448,
                            "date": datetime.datetime(2013, 10, 1)
                        }
                    ]
                }
            }
        ]

        self.mock_main_access.mds.call_find_entities_raw("econ_stats", params, context=self.context,
                                                         encode_and_decode_results=False).AndReturn(mock_stats)

        # replay mode
        self.mox.ReplayAll()

        expected = datetime.datetime(2013, 12, 1)
        latest = get_latest_econ_month(self.main_param, self.mock_main_access, context=self.context)

        self.assertEqual(latest, expected)


if __name__ == '__main__':
    unittest.main()
