import datetime
from bson.objectid import ObjectId
import mox
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.errors import BadRequestError
from core.service.svc_workflow.implementation.task.implementation.retail_input_tasks.company_name_change import CompanyNameChange

__author__ = 'erezrubinstein'


class TestWorkflowCompanyNameChange(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestWorkflowCompanyNameChange, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.company_id = "chilly_willy"
        self.start_time = datetime.datetime(2013, 1, 1)
        self.end_time = datetime.datetime(2013, 3, 3)
        self.input_rec = {
            "company_id": self.company_id,
            "context": self.context
        }

        # create company name change object, but stub out the start date before
        self.mox.StubOutWithMock(datetime, "datetime")
        datetime.datetime.utcnow().AndReturn(self.start_time)
        self.mox.ReplayAll()
        self.name_changer = CompanyNameChange(self.input_rec)

        # reset so we can record again
        self.mox.ResetAll()


    def doCleanups(self):
        # call parent clean up
        super(TestWorkflowCompanyNameChange, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_init(self):
        """
        Verify that everything is initialized correctly
        """

        # verify input rec stuff is initialized correctly
        self.assertEqual(self.name_changer._input_rec, self.input_rec)
        self.assertEqual(self.name_changer._company_id, self.company_id)
        self.assertEqual(self.name_changer._context, self.context)

        # verify MISC variables are initialized correctly
        self.assertEqual(self.name_changer._status, "in-progress")
        self.assertEqual(self.name_changer._exception, None)
        self.assertEqual(self.name_changer._start_time, self.start_time)
        self.assertEqual(self.name_changer._company_name, "")
        self.assertEqual(self.name_changer._rds_update_path_operations, [])

        # make sure there are regular expressions in there
        self.assertGreater(len(self.name_changer._file_regular_expressions), 0)


    def test_run__success(self):
        """
        Verify the logic of a successful run
        """

        # stub out various methods
        self.mox.StubOutWithMock(self.name_changer, "_get_company_name")
        self.mox.StubOutWithMock(self.name_changer, "_update_mds_files")
        self.mox.StubOutWithMock(self.name_changer, "_update_rds_files")
        self.mox.StubOutWithMock(self.name_changer, "_update_rirs")
        self.mox.StubOutWithMock(self.name_changer, "_update_stores")
        self.mox.StubOutWithMock(self.name_changer, "_update_trade_areas")
        self.mox.StubOutWithMock(self.name_changer, "_update_workflow_task_groups")
        self.mox.StubOutWithMock(self.name_changer, "_format_results")

        # record and play back
        self.name_changer._get_company_name()
        self.name_changer._update_mds_files()
        self.name_changer._update_rds_files()
        self.name_changer._update_rirs()
        self.name_changer._update_stores()
        self.name_changer._update_trade_areas()
        self.name_changer._update_workflow_task_groups()
        self.name_changer._format_results().AndReturn("woot")
        self.mox.ReplayAll()

        # run
        results = self.name_changer.run()

        # verify results and the state of the name changer
        self.assertEqual(results, "woot")
        self.assertEqual(self.name_changer._status, "success")
        self.assertIsNone(self.name_changer._exception)


    def test_run__failure(self):
        """
        Verify the logic of a failed run
        """

        # create a fake exception method
        exception = Exception("woot")
        def exception_method():
            raise exception

        # switch a real method with an exception one
        self.name_changer._get_company_name = exception_method

        # stub out the format results method
        self.mox.StubOutWithMock(self.name_changer, "_format_results")

        # record and play back
        self.name_changer._format_results().AndReturn("woot")
        self.mox.ReplayAll()

        # run
        results = self.name_changer.run()

        # verify results and the state of the name changer
        self.assertEqual(results, "woot")
        self.assertEqual(self.name_changer._status, "failure")
        self.assertEqual(self.name_changer._exception, exception)


    def test_get_company_name(self):
        """
        Test that the get company query is done correctly
        """

        # create expected parameters and mock return values
        expected_params = {
            "query": { "_id": ObjectId(self.company_id) },
            "entity_fields": ["name"]
        }
        mock_companies = [{ "name": "chilly_willy_updated" }]


        # begin recording
        self.mock_main_access.mds.call_find_entities_raw("company", expected_params, self.context).AndReturn(mock_companies)

        # replay all
        self.mox.ReplayAll()

        # run
        self.name_changer._get_company_name()

        # make sure name was updated
        self.assertEqual(self.name_changer._company_name, "chilly_willy_updated")


    def test_update_mds_files__basic(self):
        """
        Test that update mds files, updates those files and parameters that it should and ignores what it shouldn't update.
        """

        # create expected params for the raw find
        expected_params = {
            "query": { "data.company_id": self.company_id },
            "entity_fields": ["_id", "data.company_name", "data.path", "data.rds_file_id", "name"]
        }

        # create mock files
        mock_files = [
            # IGNORE - file one has neither company_name nor path
            { "_id": 1, "data": {}, "name": "woot1.txt" },
            # UPDATE NAME ONLY - file two has just a company_name
            { "_id": 2,  "data": { "company_name": "chicken" }, "name": "woot2.txt" },
            # IGNORE - file three has just a path, but doesn't match regex
            { "_id": 3,  "data": { "path": "woot" }, "name": "woot3.txt" },
            # UPDATE PATH ONLY - file three has just a path, which matches the regex
            { "_id": 4,  "data": { "path": "retail_input_files/safe_zone/", "rds_file_id": 44 }, "name": "woot4.txt" },
            # UPDATE NAME ONLY - file four has both a company_name and a path, but the path doesn't match regex
            { "_id": 5,  "data": { "company_name": "chicken", "path": "woot" }, "name": "woot5.txt" },
            # UPDATE BOTH - file four has both a company_name and a path, which matches the regex
            { "_id": 6,  "data": { "company_name": "chicken", "path": "retail_input_files/safe_zone/", "rds_file_id": 66 }, "name": "woot6" }
        ]

        # set the name changer's new name to a mock name
        self.name_changer._company_name = "danger_zone"

        # begin recording
        self.mock_main_access.mds.call_find_entities_raw("file", expected_params, self.context).AndReturn(mock_files)
        self.mock_main_access.mds.call_batch_update_entities("file", { "_id": 2 }, { "$set": { "data.company_name": "danger_zone" }}, self.context)
        self.mock_main_access.mds.call_batch_update_entities("file", { "_id": 4 }, { "$set": { "data.path": "retail_input_files/danger_zone/", "name": "retail_input_files/danger_zone/woot4.txt" }}, self.context)
        self.mock_main_access.mds.call_batch_update_entities("file", { "_id": 5 }, { "$set": { "data.company_name": "danger_zone" }}, self.context)
        self.mock_main_access.mds.call_batch_update_entities("file", { "_id": 6 }, { "$set": { "data.company_name": "danger_zone", "data.path": "retail_input_files/danger_zone/", "name": "retail_input_files/danger_zone/woot6" }}, self.context)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.name_changer._update_mds_files()

        # verify that the two files who updated their path, registered their files to update the rds path
        self.assertEqual(self.name_changer._rds_update_path_operations, [
            { "_id": 44, "new_path": "retail_input_files/danger_zone/" },
            { "_id": 66, "new_path": "retail_input_files/danger_zone/" }
        ])


    def test_update_mds_files__regular_expressions(self):
        """
        Test all the different file path regular expressions for which we should update a company name
        """

        # create expected params for the raw find
        expected_params = {
            "query": { "data.company_id": self.company_id },
            "entity_fields": ["_id", "data.company_name", "data.path", "data.rds_file_id", "name"]
        }

        # create mock files
        mock_files = [
            # good
            { "_id": 1,  "data": { "path": "retail_input_files/safe_zone/", "rds_file_id": 11 }, "name": "woot1.txt" },
            # no good
            { "_id": 2,  "data": { "path": "retail_input_files/safe_zone/asdf", "rds_file_id": 22 }, "name": "woot2.txt" },
            # good
            { "_id": 3,  "data": { "path": "retail_store_count_files/safe_zone/", "rds_file_id": 33}, "name": "woot3.txt" },
            # no good
            { "_id": 4,  "data": { "path": "retail_store_count_files/safe_zone/asf", "rds_file_id": 44 }, "name": "woot4.txt" },
            # good
            { "_id": 5,  "data": { "path": "platform_research_reports/safe_zone/", "rds_file_id": 55 }, "name": "woot5.txt" },
            # good
            { "_id": 6,  "data": { "path": "platform_research_reports/safe_zone/asdf/", "rds_file_id": 66 }, "name": "woot6.txt" },
            # no good
            { "_id": 7,  "data": { "path": "new_file/safe_zone/", "rds_file_id": 77 }, "name": "woot7.txt" }
        ]

        # set the name changer's new name to a mock name
        self.name_changer._company_name = "danger_zone"

        # begin recording
        self.mock_main_access.mds.call_find_entities_raw("file", expected_params, self.context).AndReturn(mock_files)
        self.mock_main_access.mds.call_batch_update_entities("file", { "_id": 1 }, { "$set": { "data.path": "retail_input_files/danger_zone/", "name": "retail_input_files/danger_zone/woot1.txt" }}, self.context)
        self.mock_main_access.mds.call_batch_update_entities("file", { "_id": 3 }, { "$set": { "data.path": "retail_store_count_files/danger_zone/", "name": "retail_store_count_files/danger_zone/woot3.txt" }}, self.context)
        self.mock_main_access.mds.call_batch_update_entities("file", { "_id": 5 }, { "$set": { "data.path": "platform_research_reports/danger_zone/", "name": "platform_research_reports/danger_zone/woot5.txt" }}, self.context)
        self.mock_main_access.mds.call_batch_update_entities("file", { "_id": 6 }, { "$set": { "data.path": "platform_research_reports/danger_zone/asdf/", "name": "platform_research_reports/danger_zone/asdf/woot6.txt" }}, self.context)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.name_changer._update_mds_files()

        # verify that the two files who updated their path, registered their files to update the rds path
        self.assertEqual(self.name_changer._rds_update_path_operations, [
            { "_id": 11, "new_path": "retail_input_files/danger_zone/" },
            { "_id": 33, "new_path": "retail_store_count_files/danger_zone/" },
            { "_id": 55, "new_path": "platform_research_reports/danger_zone/" },
            { "_id": 66, "new_path": "platform_research_reports/danger_zone/asdf/" }
        ])


    def test_update_rds_files(self):
        """
        Test that the RDS update is done correctly
        """

        # register mock rds update operations
        self.name_changer._rds_update_path_operations = [
            { "_id": 1, "new_path": "chilly" },
            { "_id": 2, "new_path": "willy" }
        ]

        # begin recording
        self.mock_main_access.rds.call_update_file_path(1, "chilly", self.context)
        self.mock_main_access.rds.call_update_file_path(2, "willy", self.context)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.name_changer._update_rds_files()


    def test_update_rds_files__file_exists_exception_ignored(self):
        """
        Test that the RDS file update ignores a "file already exists exception"
        """

        # generic raise exception method
        def raise_exception(*args):
            raise BadRequestError("BadRequestError: A file with the same filename 'retail_input_files/TEST_EREZ_BALDUCCI'S/TEST_EREZ_2011_06_14.xlsx' already exists")

        # register mock rds update operations
        self.name_changer._rds_update_path_operations = [{ "_id": 1, "new_path": "chilly" }]

        # begin recording
        self.mock_main_access.rds.call_update_file_path(1, "chilly", self.context).WithSideEffects(raise_exception)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.name_changer._update_rds_files()


    def test_update_rds_files__other_exception_not_ignored(self):
        """
        Test that the RDS file update does not ignore any exception that's not a "file already exists exception"
        """

        # generic raise exception method
        def raise_exception(*args):
            raise BadRequestError("woot!")

        # register mock rds update operations
        self.name_changer._rds_update_path_operations = [{ "_id": 1, "new_path": "chilly" }]

        # begin recording
        self.mock_main_access.rds.call_update_file_path(1, "chilly", self.context).WithSideEffects(raise_exception)

        # replay all
        self.mox.ReplayAll()

        # go!
        with self.assertRaises(BadRequestError):
            self.name_changer._update_rds_files()



    def test_update_rirs(self):
        """
        Test update rirs
        """

        # stub out various methods
        self.mox.StubOutWithMock(self.name_changer, "_standard_data_update")

        # record and play back
        self.name_changer._standard_data_update("retail_input_record")

        # replay all
        self.mox.ReplayAll()

        # go
        self.name_changer._update_rirs()


    def test_update_stores(self):
        """
        Test update stores
        """

        # stub out various methods
        self.mox.StubOutWithMock(self.name_changer, "_standard_data_update")

        # record and play back
        self.name_changer._standard_data_update("store")

        # replay all
        self.mox.ReplayAll()

        # go
        self.name_changer._update_stores()


    def test_update_trade_areas(self):
        """
        Test update trade areas
        """

        # stub out various methods
        self.mox.StubOutWithMock(self.name_changer, "_standard_data_update")

        # record and play back
        self.name_changer._standard_data_update("trade_area")

        # replay all
        self.mox.ReplayAll()

        # go
        self.name_changer._update_trade_areas()


    def test_standard_data_update(self):
        """
        Test that the method that stores, rirs, and trade areas call works correctly
        """

        # create expected parameters
        query = { "data.company_id": self.company_id, "data.company_name": { "$exists": True }}
        operations = { "$set": { "data.company_name": "danger_zone" }}

        # mock company name
        self.name_changer._company_name = "danger_zone"

        # start recording
        self.mock_main_access.mds.call_batch_update_entities("woot", query, operations, self.context)

        # replay all
        self.mox.ReplayAll()

        # go!
        self.name_changer._standard_data_update("woot")


    def test_update_workflow_task_groups(self):
        """
        Verify that the update workflow task groups is done correctly
        """

        # create parameters for find query
        find_params = {
            "query": {
                "unique_key.company_id": self.company_id,
                "data.company_name": { "$exists": True }
            }
        }
        update_params = { "data": { "company_name": "danger_zone" }}

        # mock company name
        self.name_changer._company_name = "danger_zone"

        # create mock task_groups
        mock_task_groups = [
            { "_id": 1 },
            { "_id": 2 }
        ]

        # begin recording
        self.mock_main_access.wfs.call_task_group_find(self.context, find_params).AndReturn(mock_task_groups)
        self.mock_main_access.wfs.call_update_task_group_id(1, self.context, update_params)
        self.mock_main_access.wfs.call_update_task_group_id(2, self.context, update_params)

        # replay all!
        self.mox.ReplayAll()

        # go!
        self.name_changer._update_workflow_task_groups()


    def test_format_results__success(self):
        """
        Test that the format results formats results correctly
        """

        # mock various state vars of the name changer
        self.name_changer._status = "woot"
        self.name_changer._company_name = "chicken"

        # create the expected output
        expected_output = {
            "status": "woot",
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "company_id": self.company_id,
            "company_name": "chicken"
        }

        # begin recording
        datetime.datetime.utcnow().AndReturn(self.end_time)

        # replay All
        self.mox.ReplayAll()

        # go
        results = self.name_changer._format_results()

        # make sure results are correct
        self.assertEqual(results, expected_output)
