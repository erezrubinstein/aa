from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.business_logic.business_objects.report_item import ReportItem
from geoprocessing.business_logic.business_objects.store import Store
from common.utilities.Logging.log_manager import LogManager
from common.utilities.inversion_of_control import dependencies
from geoprocessing.data_access.data_repository import DataRepository
from geoprocessing.data_access.period_handler import PeriodQueryHelper
from geoprocessing.business_logic.config import Config
from tests.integration_tests.geoprocessing_tests.data_access_tests.data_access_misc_queries import insert_test_segment, delete_test_segment, select_count_trade_area_by_store, delete_test_trade_area, insert_test_company, insert_test_store, insert_test_address, delete_test_address, delete_test_store, delete_test_competitors, delete_test_company, select_count_data_items, delete_data_item, select_trade_area_id_by_store, select_demographic_numvalues, select_demographic_strvalues, delete_demographic_num_and_str_values, delete_period, insert_test_report_item

__author__ = 'erezrubinstein'

import unittest

class DemographicsDataAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dependencies.register_dependency("Config", Config().instance)
        dependencies.register_dependency("LogManager", LogManager())
        cls._SQL_data_repository = DataRepository()
        dependencies.register_dependency("DataRepository", cls._SQL_data_repository)

        # insert test data
        cls._company_id = insert_test_company()
        cls._address_id = insert_test_address(-1, 1)
        cls._store_id = insert_test_store(cls._company_id, cls._address_id)
        cls._store = Store().select_by_id(cls._store_id)

        #create dummy segment
        cls._segment_id = insert_test_segment()

    @classmethod
    def tearDownClass(cls):
        if cls._store_id is not None:
            delete_test_store(cls._store_id)
        if cls._address_id is not None:
            delete_test_address(cls._address_id)
        if cls._company_id is not None:
            delete_test_competitors(cls._company_id)
        if cls._company_id is not None:
            delete_test_company(cls._company_id)
        if cls._segment_id is not None:
            delete_test_segment(cls._segment_id)

        dependencies.clear()

    def test_get_seg_id__null_max_age(self):
        """
        Test to make sure we can successfully select a segment_id that has a minimum age, but no maximum.
        This relates to JIRA RET-156 (https://nexusri.atlassian.net/browse/RET-156)
        """
        try:
            # insert a test segment
            segment_id = insert_test_segment(800, None, 'F')

            # create a report item to mimic the segment above
            report_item = ReportItem("FEM800C10", "10", "FEM800C10")
            report_item.maximum_age = None

            # select the segment with this report item
            selected_segment_id = self._SQL_data_repository.get_seg_id(report_item)

            # make sure it's selected correctly
            self.assertEqual(segment_id, selected_segment_id)
        finally:
            delete_test_segment(segment_id)


    def test_insert_demographics(self):
        """
        This is the major integration test that tests all the smaller inserts (above) together
        """
        # create test report items
        report_items = [ReportItem("unittest_insert_demographics_1", "value1", "test_insert_demographics_1"),
                        ReportItem("unittest_insert_demographics_2", "10", "FEM400C00")]

        trade_area_id = None
        census_period_id = None
        next_census_period_id = None

        # make sure that the data structures do not exist
        try:
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            count_data_items1 = select_count_data_items(report_items[0])
            count_data_items2 = select_count_data_items(report_items[1])


            self.assertEqual(count_trade_areas, 0)
            self.assertEqual(count_data_items1, 0)
            self.assertEqual(count_data_items2, 0)

            insert_test_report_item(report_items[0], 'UNITTESTSOURCE')
            insert_test_report_item(report_items[1], 'UNITTESTSOURCE')

            # main insert
            trade_area = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)
            period_id = PeriodQueryHelper().select_period_id_for_year(5766)
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items, "Nexus Age by Sex Report", "UNITTESTSOURCE")
            trade_area_id = select_trade_area_id_by_store(self._store_id)

            # get period and target period to compare against inserted data
            census_period_id = PeriodQueryHelper().select_period_id_for_year(5766)
            target_period_id = PeriodQueryHelper().select_period_id_for_year(2011)

            #make sure trade area was inserted correctly
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            count_data_items1 = select_count_data_items(report_items[0])
            count_data_items2 = select_count_data_items(report_items[1])
            self.assertEqual(count_trade_areas, 1)
            self.assertEqual(count_data_items1, 1)
            self.assertEqual(count_data_items2, 1)

            #make sure that the second report item has the right segment id that we created in the class test init
            self.assertEqual(report_items[1].segment_id, self._segment_id)

            #get demographic str/num values and assert their values
            num_values = select_demographic_numvalues(trade_area_id)
            str_values = select_demographic_strvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(num_values), 1)
            self.assertEqual(num_values[0][2], 10.0)
            self.assertEqual(num_values[0][3], target_period_id)
            self.assertEqual(num_values[0][4], census_period_id)
            self.assertEqual(len(str_values), 1)
            self.assertEqual(str_values[0][2], "value1")
            self.assertEqual(str_values[0][3], target_period_id)
            self.assertEqual(str_values[0][4], census_period_id)


            #*** update the report items and make sure it updates them instead of inserting new ones
            report_items = [ReportItem("unittest_insert_demographics_1", "value2", "test_insert_demographics_1"),
                            ReportItem("unittest_insert_demographics_2", "20", "FEM400C00")]
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items, "Nexus Age by Sex Report", "UNITTESTSOURCE")

            #get demographic str/num values and assert their values
            num_values = select_demographic_numvalues(trade_area_id)
            str_values = select_demographic_strvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(num_values), 1)
            self.assertEqual(num_values[0][2], 20.0)
            self.assertEqual(num_values[0][3], target_period_id)
            self.assertEqual(num_values[0][4], census_period_id)
            self.assertEqual(len(str_values), 1)
            self.assertEqual(str_values[0][2], "value2")
            self.assertEqual(str_values[0][3], target_period_id)
            self.assertEqual(str_values[0][4], census_period_id)

            #*** insert the report items for a different period and make sure it inserts new records without touching the old ones

            # get next period and target period to compare against inserted data
            next_census_period_id = PeriodQueryHelper().select_period_id_for_year(5776)
            period_id = next_census_period_id
            report_items_next_year = [ReportItem("unittest_insert_demographics_1", "value3", "test_insert_demographics_1"),
                            ReportItem("unittest_insert_demographics_2", "40", "FEM400C00")]
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items_next_year, "Nexus Age by Sex Report", "UNITTESTSOURCE")

            #get demographic str/num values and assert their values
            num_values = select_demographic_numvalues(trade_area_id)
            str_values = select_demographic_strvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(num_values), 2) # should be one from the previous year + one from the next year
            self.assertEqual(num_values[0][2], 20.0)
            self.assertEqual(num_values[0][3], target_period_id)
            self.assertEqual(num_values[0][4], census_period_id)
            self.assertEqual(num_values[1][2], 40.0)
            self.assertEqual(num_values[1][3], target_period_id)
            self.assertEqual(num_values[1][4], next_census_period_id)
            self.assertEqual(len(str_values), 2)
            self.assertEqual(str_values[0][2], "value2")
            self.assertEqual(str_values[0][3], target_period_id)
            self.assertEqual(str_values[0][4], census_period_id)
            self.assertEqual(str_values[1][2], "value3")
            self.assertEqual(str_values[1][3], target_period_id)
            self.assertEqual(str_values[1][4], next_census_period_id)

        except:
            raise
        finally:
            #clean up
            if trade_area_id > 0:
                delete_demographic_num_and_str_values(trade_area_id)
                delete_test_trade_area(self._store_id)
                delete_data_item(report_items[0])
                delete_data_item(report_items[1])
                if report_items_next_year:
                    delete_data_item(report_items_next_year[0])
                    delete_data_item(report_items_next_year[1])

            # delete wacky census periods for test data (no need to delete target period since they get defaulted to 2011)
            if census_period_id:
                delete_period(census_period_id)
            if next_census_period_id:
                delete_period(next_census_period_id)


    def test_insert_single_str_demographic(self):
        """
        This is the major integration test that tests all the smaller inserts (above) together
        but with only a single str report item
        """
        # create test report items
        report_items = [ReportItem("unittest_insert_demographics_1", "value1", "test_insert_demographics_1")]

        trade_area_id = None
        census_period_id = None
        next_census_period_id = None

        # make sure that the data structures do not exist
        try:
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            count_data_items1 = select_count_data_items(report_items[0])

            insert_test_report_item(report_items[0], 'UNITTESTSOURCE')
            self.assertEqual(count_trade_areas, 0)
            self.assertEqual(count_data_items1, 0)
            trade_area = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)
            period_id = PeriodQueryHelper().select_period_id_for_year(5766)
            # main insert
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items, "Nexus Age by Sex Report", "UNITTESTSOURCE")
            trade_area_id = select_trade_area_id_by_store(self._store_id)

            # get period and target period to compare against inserted data
            census_period_id = PeriodQueryHelper().select_period_id_for_year(5766)
            target_period_id = PeriodQueryHelper().select_period_id_for_year(2011)

            #make sure trade area was inserted correctly
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            count_data_items1 = select_count_data_items(report_items[0])
            self.assertEqual(count_trade_areas, 1)
            self.assertEqual(count_data_items1, 1)

            #get demographic str values and assert their values
            str_values = select_demographic_strvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(str_values), 1)
            self.assertEqual(str_values[0][2], "value1")
            self.assertEqual(str_values[0][3], target_period_id)
            self.assertEqual(str_values[0][4], census_period_id)


            #*** update the report items and make sure it updates them instead of inserting new ones
            report_items = [ReportItem("unittest_insert_demographics_1", "value2", "test_insert_demographics_1")]
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items, "Nexus Age by Sex Report", "UNITTESTSOURCE")

            #get demographic str/num values and assert their values
            str_values = select_demographic_strvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(str_values), 1)
            self.assertEqual(str_values[0][2], "value2")
            self.assertEqual(str_values[0][3], target_period_id)
            self.assertEqual(str_values[0][4], census_period_id)

            #*** insert the report items for a different period and make sure it inserts new records without touching the old ones

            # get next period and target period to compare against inserted data
            next_census_period_id = PeriodQueryHelper().select_period_id_for_year(5776)
            period_id = next_census_period_id
            report_items_next_year = [ReportItem("unittest_insert_demographics_1", "value3", "test_insert_demographics_1")]
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items_next_year, "Nexus Age by Sex Report", "UNITTESTSOURCE")

            #get demographic str/num values and assert their values
            str_values = select_demographic_strvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(str_values), 2)
            self.assertEqual(str_values[0][2], "value2")
            self.assertEqual(str_values[0][3], target_period_id)
            self.assertEqual(str_values[0][4], census_period_id)
            self.assertEqual(str_values[1][2], "value3")
            self.assertEqual(str_values[1][3], target_period_id)
            self.assertEqual(str_values[1][4], next_census_period_id)

        except:
            raise
        finally:
            #clean up
            if trade_area_id > 0:
                delete_demographic_num_and_str_values(trade_area_id)
                delete_test_trade_area(self._store_id)
                delete_data_item(report_items[0])
                if report_items_next_year:
                    delete_data_item(report_items_next_year[0])

            # delete wacky census periods for test data (no need to delete target period since they get defaulted to 2011)
            if census_period_id:
                delete_period(census_period_id)
            if next_census_period_id:
                delete_period(next_census_period_id)


    def test_insert_single_num_demographic(self):
        """
        This is the major integration test that tests all the smaller inserts (above) together
        but with only a single num report item
        """
        # create test report items
        report_items = [ReportItem("unittest_insert_demographics_2", "10", "FEM400C00")]

        trade_area_id = None
        census_period_id = None
        next_census_period_id = None

        # make sure that the data structures do not exist
        try:
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            count_data_items1 = select_count_data_items(report_items[0])

            insert_test_report_item(report_items[0], 'UNITTESTSOURCE')
            self.assertEqual(count_trade_areas, 0)
            self.assertEqual(count_data_items1, 0)
            trade_area = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)
            period_id = PeriodQueryHelper().select_period_id_for_year(5766)
            # main insert
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items, "Nexus Age by Sex Report", "UNITTESTSOURCE")
            trade_area_id = select_trade_area_id_by_store(self._store_id)

            # get period and target period to compare against inserted data
            census_period_id = PeriodQueryHelper().select_period_id_for_year(5766)
            target_period_id = PeriodQueryHelper().select_period_id_for_year(2011)

            #make sure trade area was inserted correctly
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            count_data_items1 = select_count_data_items(report_items[0])
            self.assertEqual(count_trade_areas, 1)
            self.assertEqual(count_data_items1, 1)

            #make sure that the second report item has the right segment id that we created in the class test init
            self.assertEqual(report_items[0].segment_id, self._segment_id)

            #get demographic str/num values and assert their values
            num_values = select_demographic_numvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(num_values), 1)
            self.assertEqual(num_values[0][2], 10.0)
            self.assertEqual(num_values[0][3], target_period_id)
            self.assertEqual(num_values[0][4], census_period_id)


            #*** update the report items and make sure it updates them instead of inserting new ones
            report_items = [ReportItem("unittest_insert_demographics_2", "20", "FEM400C00")]
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items, "Nexus Age by Sex Report", "UNITTESTSOURCE")

            #get demographic str/num values and assert their values
            num_values = select_demographic_numvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(num_values), 1)
            self.assertEqual(num_values[0][2], 20.0)
            self.assertEqual(num_values[0][3], target_period_id)
            self.assertEqual(num_values[0][4], census_period_id)

            #*** insert the report items for a different period and make sure it inserts new records without touching the old ones

            # get next period and target period to compare against inserted data
            next_census_period_id = PeriodQueryHelper().select_period_id_for_year(5776)
            period_id = next_census_period_id
            report_items_next_year = [ReportItem("unittest_insert_demographics_2", "40", "FEM400C00")]
            self._SQL_data_repository.insert_demographics(trade_area, period_id, report_items_next_year, "Nexus Age by Sex Report", "UNITTESTSOURCE")

            #get demographic str/num values and assert their values
            num_values = select_demographic_numvalues(trade_area_id)
            #assert values data
            self.assertEqual(len(num_values), 2) # should be one from the previous year + one from the next year
            self.assertEqual(num_values[0][2], 20.0)
            self.assertEqual(num_values[0][3], target_period_id)
            self.assertEqual(num_values[0][4], census_period_id)
            self.assertEqual(num_values[1][2], 40.0)
            self.assertEqual(num_values[1][3], target_period_id)
            self.assertEqual(num_values[1][4], next_census_period_id)

        except:
            raise
        finally:
            #clean up
            if trade_area_id > 0:
                delete_demographic_num_and_str_values(trade_area_id)
                delete_test_trade_area(self._store_id)
                delete_data_item(report_items[0])
                if report_items_next_year:
                    delete_data_item(report_items_next_year[0])
                if report_items[0].segment_id:
                    delete_test_segment(report_items[0].segment_id)

            # delete wacky census periods for test data (no need to delete target period since they get defaulted to 2011)
            if census_period_id:
                delete_period(census_period_id)
            if next_census_period_id:
                delete_period(next_census_period_id)

    def test_lazy_load_trade_area_shape(self):

        try:
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            self.assertEqual(count_trade_areas, 0)

            trade_area_1 = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DriveTimeMinutes10)

            trade_area_2 = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)

            self._SQL_data_repository.insert_trade_area_shape(trade_area_1.trade_area_id, 'LINESTRING(0 0, 0 0, 0 0, 0 0)', 3)
            self._SQL_data_repository.insert_trade_area_shape(trade_area_2.trade_area_id, 'LINESTRING(0 0, 0 0, 0 0, 0 0)', 3)

            self.assertEqual(trade_area_1.wkt_representation(), 'LINESTRING(0 0, 0 0, 0 0, 0 0)')
            self.assertEqual(trade_area_2.wkt_representation(), 'LINESTRING(0 0, 0 0, 0 0, 0 0)')

            trade_areas = self._SQL_data_repository.select_trade_areas_by_store_id_require_shape(self._store_id)
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            self.assertEqual(count_trade_areas, 2)

        except:
            raise

        finally:
            if trade_areas:
                for trade_area in trade_areas:
                    self._SQL_data_repository.delete_trade_area_shape(trade_area)
                    self._SQL_data_repository.delete_trade_area(trade_area)
                self.assertEqual(select_count_trade_area_by_store(self._store_id), 0)

    def test_delete_trade_area(self):
        try:
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            self.assertEqual(count_trade_areas, 0)

            trade_area_1 = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DriveTimeMinutes10)

            trade_area_2 = self._SQL_data_repository.select_trade_area_force_insert(self._store_id, TradeAreaThreshold.DistanceMiles10)

            self._SQL_data_repository.insert_trade_area_shape(trade_area_1.trade_area_id, 'LINESTRING(0 0, 0 0, 0 0, 0 0)', 3)
            self._SQL_data_repository.insert_trade_area_shape(trade_area_2.trade_area_id, 'LINESTRING(0 0, 0 0, 0 0, 0 0)', 3)

            trade_areas = self._SQL_data_repository.select_trade_areas_by_store_id_require_shape(self._store_id)
            count_trade_areas = select_count_trade_area_by_store(self._store_id)
            self.assertEqual(count_trade_areas, 2)

        except:
            raise

        finally:
            if trade_areas:
                for trade_area in trade_areas:
                    self._SQL_data_repository.delete_trade_area_shape(trade_area)
                    self._SQL_data_repository.delete_trade_area(trade_area)
                self.assertEqual(select_count_trade_area_by_store(self._store_id), 0)

if __name__ == '__main__':
    unittest.main()