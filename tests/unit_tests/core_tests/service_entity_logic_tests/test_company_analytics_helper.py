from dateutil.relativedelta import relativedelta
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic.company_analytics_helper import get_company_store_analytics_date_range
import unittest
import datetime

__author__ = 'erezrubinstein'


class TestCompanyHelper(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestCompanyHelper, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # various needed data
        self.context = { "user": "chicken_woot" }

    def doCleanups(self):
        # call parent clean up
        super(TestCompanyHelper, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_operating__one_collection(self):
        """
        Test with one collection and analytics having been run
        """

        # set op vars.  One collection, recent analytics, recent stores
        company_status = "operating"
        store_collection_dates = [datetime.datetime(2013, 1, 1)]
        last_analytics_stores_month = datetime.datetime(2013, 12, 1)
        last_month_with_stores = datetime.datetime(2014, 1, 1)

        # get start/end dates
        start, end = get_company_store_analytics_date_range(company_status, store_collection_dates, last_analytics_stores_month, last_month_with_stores)

        # should be last collection to one year back
        self.assertEqual(end, datetime.datetime(2013, 1, 1))
        self.assertEqual(start, datetime.datetime(2012, 1, 1))


    def test_operating__two_collections__analytics_complete(self):
        """
        Test with two collections, where last analytics date is after the collections
        """

        # set op vars.  One collection, recent analytics, recent stores
        company_status = "operating"
        store_collection_dates = [datetime.datetime(2013, 6, 1), datetime.datetime(2013, 1, 1)]
        last_analytics_stores_month = datetime.datetime(2013, 12, 1)
        last_month_with_stores = datetime.datetime(2014, 1, 1)

        # get start/end dates
        start, end = get_company_store_analytics_date_range(company_status, store_collection_dates, last_analytics_stores_month, last_month_with_stores)

        # should be first to last collections
        self.assertEqual(end, datetime.datetime(2013, 6, 1))
        self.assertEqual(start, datetime.datetime(2013, 1, 1))


    def test_operating__two_collections__analytics_not_complete(self):
        """
        Test with two collections, where last analytics date is before the collections
        """

        # set op vars.  One collection, recent analytics, recent stores
        company_status = "operating"
        store_collection_dates = [datetime.datetime(2013, 6, 1), datetime.datetime(2013, 1, 1)]
        last_analytics_stores_month = datetime.datetime(2013, 2, 1)
        last_month_with_stores = datetime.datetime(2013, 3, 1)

        # get start/end dates
        start, end = get_company_store_analytics_date_range(company_status, store_collection_dates, last_analytics_stores_month, last_month_with_stores)

        # should be last analytics stores month to first collection
        self.assertEqual(end, datetime.datetime(2013, 2, 1))
        self.assertEqual(start, datetime.datetime(2013, 1, 1))


    def test_operating__multiple_collections__analytics_complete(self):
        """
        Test with several collections, where last analytics date is after all the collections
        """

        # set op vars.  One collection, recent analytics, recent stores
        company_status = "operating"
        store_collection_dates = [datetime.datetime(2013, 8, 1), datetime.datetime(2013, 7, 1), datetime.datetime(2013, 6, 1),
                                  datetime.datetime(2012, 8, 1), datetime.datetime(2012, 7, 1)]
        last_analytics_stores_month = datetime.datetime(2013, 9, 1)
        last_month_with_stores = datetime.datetime(2013, 10, 1)

        # get start/end dates
        start, end = get_company_store_analytics_date_range(company_status, store_collection_dates, last_analytics_stores_month, last_month_with_stores)

        # should be latest collection to closest collection of one year to date
        self.assertEqual(end, datetime.datetime(2013, 8, 1))
        self.assertEqual(start, datetime.datetime(2012, 8, 1))


    def test_operating__multiple_collections__analytics_not_complete(self):
        """
        Test with several collections, where last analytics date is before all the collections
        """

        # set op vars.  One collection, recent analytics, recent stores
        company_status = "operating"
        store_collection_dates = [datetime.datetime(2013, 8, 1), datetime.datetime(2013, 7, 1), datetime.datetime(2013, 6, 1),
                                  datetime.datetime(2012, 8, 1), datetime.datetime(2012, 7, 1)]
        last_analytics_stores_month = datetime.datetime(2013, 6, 1)
        last_month_with_stores = datetime.datetime(2013, 7, 1)

        # get start/end dates
        start, end = get_company_store_analytics_date_range(company_status, store_collection_dates, last_analytics_stores_month, last_month_with_stores)

        # should be last analytics stores month to closest collection of one year to date
        self.assertEqual(end, datetime.datetime(2013, 6, 1))
        self.assertEqual(start, datetime.datetime(2012, 8, 1))


    def test_operating__multiple_collections__next_most_recent_far_away(self):
        """
        Test with several collections, where last analytics date is before all the collections
        """

        # set op vars.  One collection, recent analytics, recent stores
        company_status = "operating"
        store_collection_dates = [datetime.datetime(2013, 8, 1), datetime.datetime(2011, 7, 1), datetime.datetime(2011, 6, 1),
                                  datetime.datetime(2011, 1, 1)]
        last_analytics_stores_month = datetime.datetime(2014, 1, 1)
        last_month_with_stores = datetime.datetime(2014, 1, 1)

        # get start/end dates
        start, end = get_company_store_analytics_date_range(company_status, store_collection_dates, last_analytics_stores_month, last_month_with_stores)

        # should be last analytics, to a year before
        self.assertEqual(end, datetime.datetime(2013, 8, 1))
        self.assertEqual(start, datetime.datetime(2011, 7, 1))


    def test_not_operating__one_collection(self):
        """
        Test with several collections, where last analytics date is before all the collections
        """

        # set op vars.  One collection, recent analytics, recent stores
        company_status = "moet_chandon"
        store_collection_dates = [datetime.datetime(2013, 8, 1)]
        last_analytics_stores_month = datetime.datetime(2014, 1, 1)
        last_month_with_stores = datetime.datetime(2013, 9, 1)

        # get start/end dates
        start, end = get_company_store_analytics_date_range(company_status, store_collection_dates, last_analytics_stores_month, last_month_with_stores)

        # should be the last month with store minus one year
        self.assertEqual(end, datetime.datetime(2013, 9, 1))
        self.assertEqual(start, datetime.datetime(2012, 9, 1))


    def test_not_operating__multiple_collection(self):
        """
        Test with several collections, where last analytics date is before all the collections
        """

        # set op vars.  One collection, recent analytics, recent stores
        company_status = "moet_chandon"
        store_collection_dates = [datetime.datetime(2013, 8, 1), datetime.datetime(2013, 1, 1), datetime.datetime(2012, 5, 1), datetime.datetime(2012, 4, 1)]
        last_analytics_stores_month = datetime.datetime(2014, 1, 1)
        last_month_with_stores = datetime.datetime(2013, 9, 1)

        # get start/end dates
        start, end = get_company_store_analytics_date_range(company_status, store_collection_dates, last_analytics_stores_month, last_month_with_stores)

        # should be the closest collection within a year to the last month with stores
        self.assertEqual(end, datetime.datetime(2013, 9, 1))
        self.assertEqual(start, datetime.datetime(2012, 5, 1))


