from common.utilities.inversion_of_control import Dependency, dependencies
from geoprocessing.business_logic.business_objects.store import Store
from geoprocessing.business_logic.enums import TradeAreaThreshold
from geoprocessing.geoprocessors.ba_online.gp6_BA_online_reports import GP6_BA_Online_Reports
from geoprocessing.helpers.dependency_helper import register_mock_dependencies
from tests.unit_tests.geoprocessing_tests.mock_providers.mock_rest_provider import MockResponse

__author__ = 'erezrubinstein'

import unittest


class TestGP6(unittest.TestCase):
    def setUp(self):
        # set up mock dependencies

        register_mock_dependencies()
        self.data_provider = Dependency("DataRepository").value
        self.rest_provider = Dependency("RestProvider").value
        self.ba_online_helper = Dependency("BAOnlineConnection").value
        self.config = Dependency("Config").value

        # set up data
        self.store = Store.simple_init_with_address(store_id=777777, company_id=666666, longitude=99.99999999, latitude=88.88888888)
        self.store.address_id = 10
        self.data_provider.stores[self.store.store_id] = self.store
        self.data_provider.addresses[10] = self.store.address

        # make sure config is correct with the below reports
        self.config.ba_online_templates = ["acs_housing", "traffic"]

    def tearDown(self):
        dependencies.clear()


    #####################################################################################################################
    #############################################   initialization Tests ################################################
    #####################################################################################################################

    def test_initialization(self):
        gp6 = GP6_BA_Online_Reports(TradeAreaThreshold.DistanceMiles10)
        gp6._initialize()

        #make sure the values are initialized correctly
        self.assertEqual(gp6._demographics, [])




    #####################################################################################################################
    ############################################   _do_geoprocessing Tests ##############################################
    #####################################################################################################################

    def test_do_geoprocessing(self):
        # mock up data
        self.ba_online_helper.generate_report_response = "woot"

        # run gp
        gp6 = GP6_BA_Online_Reports(TradeAreaThreshold.DistanceMiles10)
        gp6._home_store = self.store
        gp6._do_geoprocessing()

        #make sure the values are initialized correctly
        self.assertEqual(gp6._response, "woot")




    #####################################################################################################################
    ######################################### _preprocess_data_for_save Tests ###########################################
    #####################################################################################################################

    def test__preprocess_data_for_save(self):
        # create gp
        gp6 = GP6_BA_Online_Reports(TradeAreaThreshold.DistanceMiles10)

        # mock up data
        gp6._response = MockResponse("""{"Reports":[{"TemplateName":"acs_housing","ReportDescription":"ACS Housing Summary","ReportFormat":"s.xml","ReportURL":"http://woot.xml"},{"TemplateName":"traffic","ReportDescription":"Traffic Count Profile","ReportFormat":"s.xml","ReportURL":"http://chicken.xml"}]}""", "", 10)
        self.ba_online_helper.download_urls["http://woot.xml"] = """<?xml version="1.0" encoding="utf-8"?>
            <Report>
            <ReportTitle />
            <ReportTitle2 />
            <ReportName>ACS Housing Summary</ReportName>
            <TemplateName>ACS Housing Summary</TemplateName>
            <DataPath>Data</DataPath>
            <ReportOrientation>Portrait</ReportOrientation>
            <ReportType>Summary</ReportType>
            <TextObjects />
            <ReportVariables />
            <Areas>
            <Area>
            <ReportItem name="AREA_ID" caption="" value="12345_1" />
            <ReportItem name="AREA_DESC" caption="" value="10 miles" />
            <ReportItem name="DEMOG_ID" caption="" value="0" />
            </Area>
            </Areas>
            </Report>"""
        self.ba_online_helper.download_urls["http://chicken.xml"] = self.ba_online_helper.download_urls["http://woot.xml"]


        # run gp
        gp6._home_store = self.store
        gp6._demographics = []
        gp6._preprocess_data_for_save()

        # make sure we have 2 sets of demographics
        self.assertEqual(len(gp6._demographics), 2)
        self.assertEqual(len(gp6._demographics[0].dem_report_items), 3)
        self.assertEqual(len(gp6._demographics[1].dem_report_items), 3)





    ########################################################################################################################
    ###########################################   save_processed_data Tests ################################################
    ########################################################################################################################

    def test_save_processed_data(self):
        # create gp
        gp6 = GP6_BA_Online_Reports(TradeAreaThreshold.DistanceMiles10)

        # mock up data
        gp6._response = MockResponse("""{"Reports":[{"TemplateName":"acs_housing","ReportDescription":"ACS Housing Summary","ReportFormat":"s.xml","ReportURL":"http://woot.xml"},{"TemplateName":"traffic","ReportDescription":"Traffic Count Profile","ReportFormat":"s.xml","ReportURL":"http://chicken.xml"}]}""", "", 10)
        self.ba_online_helper.download_urls["http://woot.xml"] = """<?xml version="1.0" encoding="utf-8"?>
            <Report>
            <ReportTitle />
            <ReportTitle2 />
            <ReportName>ACS Housing Summary</ReportName>
            <TemplateName>ACS Housing Summary</TemplateName>
            <DataPath>Data</DataPath>
            <ReportOrientation>Portrait</ReportOrientation>
            <ReportType>Summary</ReportType>
            <TextObjects />
            <ReportVariables />
            <Areas>
            <Area>
            <ReportItem name="AREA_ID" caption="" value="12345_1" />
            <ReportItem name="AREA_DESC" caption="" value="10 miles" />
            <ReportItem name="DEMOG_ID" caption="" value="0" />
            </Area>
            </Areas>
            </Report>"""
        self.ba_online_helper.download_urls["http://chicken.xml"] = self.ba_online_helper.download_urls["http://woot.xml"]


        # run gp
        gp6._home_store = self.store
        gp6._store_id = self.store.store_id
        gp6._period_id = 3
        gp6._demographics = []
        gp6._preprocess_data_for_save()
        gp6._save_processed_data()

        #assert mock has correct data and tht both templates were saved
        self.assertEqual(len(self.data_provider.inserted_demographics), 2)
        self.assertEqual(self.data_provider.inserted_demographics[0]["store_id"], self.store.store_id)
        self.assertEqual(self.data_provider.inserted_demographics[1]["store_id"], self.store.store_id)
        self.assertEqual(len(self.data_provider.inserted_demographics[0]["demographic_report_items"]), 3)
        self.assertEqual(len(self.data_provider.inserted_demographics[1]["demographic_report_items"]), 3)
        self.assertEqual(self.data_provider.inserted_demographics[0]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[1]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[0]["template_name"], "acs_housing")
        self.assertEqual(self.data_provider.inserted_demographics[1]["template_name"], "traffic")





    #####################################################################################################################
    #############################################   complete process Tests ##############################################
    #####################################################################################################################

    def test_complete_process(self):
        """
        Main end-to-end test of the process function.
        """
        # create gp
        gp6 = GP6_BA_Online_Reports(TradeAreaThreshold.DistanceMiles10)

        # mock up data
        self.data_provider.period_ids_per_year[2011] = 3
        self.ba_online_helper.generate_report_response = MockResponse("""{"Reports":[{"TemplateName":"acs_housing","ReportDescription":"ACS Housing Summary","ReportFormat":"s.xml","ReportURL":"http://woot.xml"},{"TemplateName":"traffic","ReportDescription":"Traffic Count Profile","ReportFormat":"s.xml","ReportURL":"http://chicken.xml"}]}""", "", 10)
        self.ba_online_helper.download_urls["http://woot.xml"] = """<?xml version="1.0" encoding="utf-8"?>
            <Report>
            <ReportTitle />
            <ReportTitle2 />
            <ReportName>ACS Housing Summary</ReportName>
            <TemplateName>ACS Housing Summary</TemplateName>
            <DataPath>Data</DataPath>
            <ReportOrientation>Portrait</ReportOrientation>
            <ReportType>Summary</ReportType>
            <TextObjects />
            <ReportVariables />
            <Areas>
            <Area>
            <ReportItem name="AREA_ID" caption="" value="12345_1" />
            <ReportItem name="AREA_DESC" caption="" value="10 miles" />
            <ReportItem name="DEMOG_ID" caption="" value="0" />
            </Area>
            </Areas>
            </Report>"""
        self.ba_online_helper.download_urls["http://chicken.xml"] = self.ba_online_helper.download_urls["http://woot.xml"]

        # run gp
        gp6._home_store = self.store
        gp6._demographics = []
        gp6.process(self.store.company_id, self.store.store_id)

        #assert mock has correct data and tht both templates were saved
        self.assertEqual(len(self.data_provider.inserted_demographics), 2)
        self.assertEqual(self.data_provider.inserted_demographics[0]["store_id"], self.store.store_id)
        self.assertEqual(self.data_provider.inserted_demographics[1]["store_id"], self.store.store_id)
        self.assertEqual(len(self.data_provider.inserted_demographics[0]["demographic_report_items"]), 3)
        self.assertEqual(len(self.data_provider.inserted_demographics[1]["demographic_report_items"]), 3)
        self.assertEqual(self.data_provider.inserted_demographics[0]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[1]["period_id"], 3)
        self.assertEqual(self.data_provider.inserted_demographics[0]["template_name"], "acs_housing")
        self.assertEqual(self.data_provider.inserted_demographics[1]["template_name"], "traffic")





if __name__ == '__main__':
    unittest.main()
