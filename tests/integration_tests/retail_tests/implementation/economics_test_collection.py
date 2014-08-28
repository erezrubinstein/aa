from __future__ import division
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_company, insert_test_company_analytics
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import LAST_ANALYTICS_DATE, LAST_ECONOMICS_DATE


__author__ = "vgold"


class EconomicsTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "economics_test_collection.py"
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

    def analytics_test_unemployment_distribution(self):
        self.test_case.maxDiff = None

        as_of_date = LAST_ECONOMICS_DATE

        analytics = {
            "stores": {
                "monthly": {
                    "store_counts": [
                        {
                            "date": as_of_date,
                            "value": 20
                        }
                    ]
                }
            }
        }

        can_data = {
            "aggregate_trade_area_unemployment_rate": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        }

        # Test with one banner

        cid = insert_test_company(type="retail_banner", analytics=analytics)
        insert_test_company_analytics(cid, as_of_date, engine="economics", target_year=None, analytics=can_data)

        resource = "/data/preset/unemployment_distribution"
        params = {
            "banner_ids": [cid],
            "labor_as_of_date": as_of_date,
            "stores_as_of_date": as_of_date
        }
        economics = self.main_access.call_get_preset(resource, params=params, context=self.context)

        store_distribution = [4, 1, 1, 1, 1, 1, 1, 1, 1, 3]

        expected_result = {
            "index": ["<5%", "5% -\n5.9%", "6% -\n6.9%", "7% -\n7.9%", "8% -\n8.9%", "9% -\n9.9%",
                      "10% -\n10.9%", "11% -\n11.9%", "12% -\n12.9%", "13%+"],
            "date": as_of_date.isoformat().rsplit(".", 1)[0],
            "data": {
                "stores": store_distribution,
                "percent_store_base": [
                    value / 20.0 * 100
                    for value in store_distribution
                ]
            }
        }

        self.test_case.assertDictEqual(economics, expected_result)

        # Test with two banners

        cid2 = insert_test_company(type="retail_banner", analytics=analytics)
        insert_test_company_analytics(cid2, as_of_date, engine="economics", target_year=None, analytics=can_data)

        resource = "/data/preset/unemployment_distribution"
        params = {
            "banner_ids": [cid, cid2],
            "labor_as_of_date": as_of_date,
            "stores_as_of_date": as_of_date
        }
        economics = self.main_access.call_get_preset(resource, params=params, context=self.context)

        store_distribution = map(lambda x: x * 2, store_distribution)

        expected_result = {
            "index": ["<5%", "5% -\n5.9%", "6% -\n6.9%", "7% -\n7.9%", "8% -\n8.9%", "9% -\n9.9%",
                      "10% -\n10.9%", "11% -\n11.9%", "12% -\n12.9%", "13%+"],
            "date": as_of_date.isoformat().rsplit(".", 1)[0],
            "data": {
                "stores": store_distribution,
                "percent_store_base": [
                    value / 40.0 * 100
                    for value in store_distribution
                ]
            }
        }

        self.test_case.assertDictEqual(economics, expected_result)
