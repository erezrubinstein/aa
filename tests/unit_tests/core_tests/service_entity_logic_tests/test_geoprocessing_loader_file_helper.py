from dateutil import parser
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies
from core.common.business_logic.service_entity_logic import geoprocessing_loader_file_helper
from core.common.business_logic.service_entity_logic.geoprocessing_loader_file_helper import get_unique_folder_name
import datetime
import mox
import xlwt


__author__ = "erezrubinstein"


class TestGPLoaderFileHelper(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestGPLoaderFileHelper, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)


    def doCleanups(self):
        # call parent clean up
        super(TestGPLoaderFileHelper, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_get_unique_folder_name(self):
        # mock datetime
        mock_time = parser.parse("2013-05-06 14:50:45.578714")

        # stub out datetime
        self.mox.StubOutWithMock(datetime, "datetime")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_time)

        # replay all
        self.mox.ReplayAll()

        # get unique folder name
        folder = get_unique_folder_name()

        # make sure the folder name is correct
        self.assertEqual(folder, "gp_loader_files__2013-05-06-14-50-45-578714")


    def test_save_geoprocessing_loader_files(self):

        # mock get_unique_folder_name and create_company_file
        self.mox.StubOutWithMock(geoprocessing_loader_file_helper, "get_unique_folder_name")
        self.mox.StubOutWithMock(geoprocessing_loader_file_helper, "create_directory")
        self.mox.StubOutWithMock(geoprocessing_loader_file_helper, "create_company_file")
        self.mox.StubOutWithMock(geoprocessing_loader_file_helper, "zip_folder")

        # start recording
        geoprocessing_loader_file_helper.get_unique_folder_name().AndReturn("woot")
        geoprocessing_loader_file_helper.create_directory("/tmp/woot")
        geoprocessing_loader_file_helper.create_company_file("woot", "", "2012-01-01", ["danger_zone"], "/tmp/woot").InAnyOrder()
        geoprocessing_loader_file_helper.create_company_file("chicken", "", "2012-01-01", ["willy"], "/tmp/woot").InAnyOrder()
        geoprocessing_loader_file_helper.create_company_file("woot", "", "2013-01-01", ["billy"], "/tmp/woot").InAnyOrder()
        geoprocessing_loader_file_helper.create_company_file("chicken", "", "2013-01-01", ["renaissance_fair"], "/tmp/woot").InAnyOrder()
        geoprocessing_loader_file_helper.zip_folder("/tmp/woot")

        # replay
        self.mox.ReplayAll()

        # create fake data
        mock_data = {
            "2012-01-01": {
                "woot": ["danger_zone"],
                "chicken": ["willy"]
            },
            "2013-01-01": {
                "woot": ["billy"],
                "chicken": ["renaissance_fair"]
            }
        }

        # bomboj for!
        zip_file = geoprocessing_loader_file_helper.save_geoprocessing_loader_files(mock_data, "/tmp")

        # make sure zip returned
        self.assertEqual(zip_file, ("/tmp/woot.zip", "woot.zip"))


    def test_save_geoprocessing__over_65K_stores(self):

        # create 65K records for woot
        woot_stores = [1] * 65000

        # create 64999 records for chicken
        chicken_stores = [2] * 64999

        # create fake data
        mock_data = {
            "2012-01-01": {
                "woot": woot_stores,
                "chicken": chicken_stores
            }
        }

        # mock get_unique_folder_name and create_company_file
        self.mox.StubOutWithMock(geoprocessing_loader_file_helper, "get_unique_folder_name")
        self.mox.StubOutWithMock(geoprocessing_loader_file_helper, "create_directory")
        self.mox.StubOutWithMock(geoprocessing_loader_file_helper, "create_company_file")
        self.mox.StubOutWithMock(geoprocessing_loader_file_helper, "zip_folder")

        # start recording
        geoprocessing_loader_file_helper.get_unique_folder_name().AndReturn("woot")
        geoprocessing_loader_file_helper.create_directory("/tmp/woot")
        geoprocessing_loader_file_helper.create_company_file("chicken", "", "2012-01-01", chicken_stores, "/tmp/woot").InAnyOrder()
        geoprocessing_loader_file_helper.create_company_file("woot", "", "2012-01-01", [1] * 64999, "/tmp/woot").InAnyOrder()
        geoprocessing_loader_file_helper.create_company_file("woot", "_1", "2012-01-01", [1], "/tmp/woot").InAnyOrder()
        geoprocessing_loader_file_helper.zip_folder("/tmp/woot")

        # replay
        self.mox.ReplayAll()

        # bomboj for!
        zip_file = geoprocessing_loader_file_helper.save_geoprocessing_loader_files(mock_data, "/tmp")

        # make sure zip returned
        self.assertEqual(zip_file, ("/tmp/woot.zip", "woot.zip"))


    def test_create_company_file(self):

        # create mock data
        folder = "/tmp/woot"
        date = "2012-01-01"
        file_name = "/tmp/woot/chicken_2012_01_01.xls"
        mock_stores = [
            {
                "store_number": "",
                "store_id": "518692c6f3d31b59eca03fb8",
                "zip": "36606",
                "city": "Mobile",
                "longitude": -80,
                "store_format": None,
                "note": None,
                "phone": "251-471-0556",
                "state": "AL",
                "company_name": "Honey",
                "address": "1551 East I-65 Service Road S",
                "latitude": 40,
                "suite": "Suite B",
                "shopping_center": None,
            },
            {
                "store_number": "",
                "store_id": "518692c6f3d31b59eca03fc3",
                "zip": "06605",
                "city": "Bridgeport",
                "longitude": -80,
                "store_format": None,
                "note": None,
                "phone": "203-331-9660",
                "state": "CT",
                "company_name": "BooBoo",
                "address": "828 Railroad Ave.",
                "latitude": 40,
                "suite": None,
                "shopping_center": None
            }
        ]

        trade_area_threshold = 'DriveTimeChickens'

        # mock excel writer and sheet
        self.mox.StubOutClassWithMocks(xlwt, "Workbook")
        sheet = self.mox.CreateMockAnything()
        column = self.mox.CreateMockAnything()


        # start recording
        workbook = xlwt.Workbook()
        workbook.add_sheet("Final Output").AndReturn(sheet)

        # set column widths
        sheet.col(0).AndReturn(column).set_width(800)
        sheet.col(1).AndReturn(column).set_width(500)
        sheet.col(2).AndReturn(column).set_width(500)

        # write header
        sheet.write(0, 1, "A")
        sheet.write(0, 2, "C")
        sheet.write(0, 5, "chicken")

        # write stores
        sheet.write(1, 1, "D")
        sheet.write(1, 2, "C")
        # first store
        sheet.write(1, 3, '518692c6f3d31b59eca03fb8')
        sheet.write(1, 4, "1551 East I-65 Service Road S")
        sheet.write(1, 5, "Mobile")
        sheet.write(1, 6, "AL")
        sheet.write(1, 7, "36606")
        sheet.write(1, 8, "251-471-0556")
        sheet.write(1, 10, None)
        sheet.write(1, 12, "Suite B")
        sheet.write(1, 13, "")
        sheet.write(1, 14, None)
        sheet.write(1, 15, None)
        sheet.write(1, 16, -80)
        sheet.write(1, 17, 40)
        sheet.write(1, 18, "Honey")
        # second stores
        sheet.write(2, 1, "D")
        sheet.write(2, 2, "C")
        sheet.write(2, 3, '518692c6f3d31b59eca03fc3')
        sheet.write(2, 4, "828 Railroad Ave.")
        sheet.write(2, 5, "Bridgeport")
        sheet.write(2, 6, "CT")
        sheet.write(2, 7, "06605")
        sheet.write(2, 8, "203-331-9660")
        sheet.write(2, 10, None)
        sheet.write(2, 12, None)
        sheet.write(2, 13, "")
        sheet.write(2, 14, None)
        sheet.write(2, 15, None)
        sheet.write(2, 16, -80)
        sheet.write(2, 17, 40)
        sheet.write(2, 18, "BooBoo")

        # save
        workbook.save(file_name)

        # replay all
        self.mox.ReplayAll()

        # go!
        geoprocessing_loader_file_helper.create_company_file("chicken", "", date, mock_stores, folder)
