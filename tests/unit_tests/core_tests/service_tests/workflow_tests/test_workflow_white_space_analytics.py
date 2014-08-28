import datetime
from bson.objectid import ObjectId
import mox
from mox import IgnoreArg
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities import time_series
from common.utilities.date_utilities import LAST_ANALYTICS_DATE
from common.utilities.inversion_of_control import Dependency, dependencies
from common.web_helpers import logging_helper
from core.common.business_logic.service_entity_logic import white_space_grid_helper, company_analytics_helper
from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.white_space_cell_analytics import WhiteSpaceCellAnalytics
from core.service.svc_workflow.implementation.task.implementation.company_analytics_tasks.white_space_grid_analytics import WhiteSpaceGridAnalytics


__author__ = "erezrubinstein"

class TestWorkflowWhiteSpaceAnalytics(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestWorkflowWhiteSpaceAnalytics, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_logger = Dependency("FlaskLogger").value

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.task_id = ObjectId()
        self.as_of_date = datetime.datetime(2013, 12, 1)

        # reset so we can record again
        self.mox.ResetAll()


    def doCleanups(self):

        # call parent clean up
        super(TestWorkflowWhiteSpaceAnalytics, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    # -------------------------------- grid analytic tests -------------------------------- #

    def test_grid_analytics__successful_run(self):

        # create mock vars
        mock_company_ids = [1, 2, 3, 4, 5]
        mock_results = "woot!"

        # create mock input rec and task object
        input_rec = self._create_grid_analytics_input_rec()
        grid_task = WhiteSpaceGridAnalytics(input_rec)

        # stub out methods
        self.mox.StubOutWithMock(grid_task, "_get_all_company_ids")
        self.mox.StubOutWithMock(grid_task, "_create_grid_cell_analytic_tasks")
        self.mox.StubOutWithMock(grid_task, "_format_results")
        self.mox.StubOutWithMock(grid_task, "_update_task")

        # begin recording
        grid_task._get_all_company_ids().AndReturn(mock_company_ids)
        grid_task._create_grid_cell_analytic_tasks(mock_company_ids)
        grid_task._format_results().AndReturn(mock_results)
        grid_task._update_task(mock_results)

        # replay all
        self.mox.ReplayAll()

        # bomboj for!
        results = grid_task.run()

        # make sure everything is good after the fact
        self.assertEqual(results, mock_results)
        self.assertEqual(grid_task._num_child_tasks, 5)
        self.assertIsNone(grid_task._exception)


    def test_grid_analytics__failed_run(self):

        # create mock vars
        mock_results = "woot!"

        # create mock input rec and task object
        input_rec = self._create_grid_analytics_input_rec()
        grid_task = WhiteSpaceGridAnalytics(input_rec)

        # create mock exception and method to raise it
        exception = Exception("Big Poppa")
        def raise_exception():
            raise exception

        # stub out methods
        self.mox.StubOutWithMock(grid_task, "_get_all_company_ids")
        self.mox.StubOutWithMock(logging_helper, "log_exception")
        self.mox.StubOutWithMock(grid_task, "_format_results")
        self.mox.StubOutWithMock(grid_task, "_update_task")

        # begin recording
        grid_task._get_all_company_ids().WithSideEffects(raise_exception)
        logging_helper.log_exception(self.mock_logger, "Error Running WhiteSpaceGridAnalytics Task", exception, IgnoreArg())
        grid_task._format_results().AndReturn(mock_results)
        grid_task._update_task(mock_results)

        # replay all
        self.mox.ReplayAll()

        # bomboj for!
        results = grid_task.run()

        # make sure everything is good after the fact
        self.assertEqual(results, mock_results)
        self.assertEqual(grid_task._num_child_tasks, 0)
        self.assertEqual(grid_task._exception, exception)


    def test_grid_analytics_get_all_company_ids(self):

        # create mock objects
        mock_params = { "entity_fields": ["_id"] }
        mock_results = [
            { "_id": "chicken"},
            { "_id": "pork"}
        ]

        # begin recording
        self.mock_main_access.mds.call_find_entities_raw("company", params=mock_params, encode_and_decode_results=False).AndReturn(mock_results)

        # replay all
        self.mox.ReplayAll()

        # bomboj for!
        grid_task = WhiteSpaceGridAnalytics(self._create_grid_analytics_input_rec())
        results = grid_task._get_all_company_ids()

        # make sure results are good
        self.assertEqual(results, ["chicken", "pork"])


    def test_grid_analytics__create_grid_cell_analytic_tasks__async(self):

        # create mock objects
        mock_company_ids = ["chilly", "willy", "taco"]

        # begin recording
        self.mock_main_access.wfs.call_task_new("retail_analytics", "analytics", "white_space_cell_analytics", self._create_cell_rec("chilly"), self.context, timeout = None)
        self.mock_main_access.wfs.call_task_new("retail_analytics", "analytics", "white_space_cell_analytics", self._create_cell_rec("willy"), self.context, timeout = None)
        self.mock_main_access.wfs.call_task_new("retail_analytics", "analytics", "white_space_cell_analytics", self._create_cell_rec("taco"), self.context, timeout = None)

        # replay all
        self.mox.ReplayAll()

        # bomboj for!
        grid_task = WhiteSpaceGridAnalytics(self._create_grid_analytics_input_rec())
        grid_task._create_grid_cell_analytic_tasks(mock_company_ids)


    def test_grid_analytics__create_grid_cell_analytic_tasks__sync(self):

        # create mock objects
        mock_company_ids = ["chilly", "willy", "taco"]

        # begin recording
        self.mock_main_access.wfs.call_task_new("retail_analytics", "analytics", "white_space_cell_analytics", self._create_cell_rec("chilly", False), self.context, timeout = 100)
        self.mock_main_access.wfs.call_task_new("retail_analytics", "analytics", "white_space_cell_analytics", self._create_cell_rec("willy", False), self.context, timeout = 100)
        self.mock_main_access.wfs.call_task_new("retail_analytics", "analytics", "white_space_cell_analytics", self._create_cell_rec("taco", False), self.context, timeout = 100)

        # replay all
        self.mox.ReplayAll()

        # bomboj for!
        grid_task = WhiteSpaceGridAnalytics(self._create_grid_analytics_input_rec(False))
        grid_task._create_grid_cell_analytic_tasks(mock_company_ids)




    # -------------------------------- cell analytic tests -------------------------------- #

    def test_cell_analytics__successful_run(self):

        # create mock vars
        company_id = "oooh the baby"
        mock_analytics_start_date = "moet"
        mock_analytics_end_date = "chandon"
        mock_company_counts_current = "chicken!"
        mock_company_counts_openings = "sesame chicken!"
        mock_new_matches = "New"
        mock_existing_matches = "Existing"
        mock_to_insert = "Everything :)"
        mock_to_delete = "Nothing :("
        mock_results = "woot!"

        # create mock input rec and task object
        input_rec = self._create_cell_analytics_input_rec(company_id)
        cell_task = WhiteSpaceCellAnalytics(input_rec)

        # stub out methods
        self.mox.StubOutWithMock(company_analytics_helper, "query_company_return_store_analytics_date_range")
        self.mox.StubOutWithMock(time_series, "get_start_of_next_month")
        self.mox.StubOutWithMock(white_space_grid_helper, "get_current_stores_with_matches")
        self.mox.StubOutWithMock(white_space_grid_helper, "get_opened_stores_with_matches")
        self.mox.StubOutWithMock(cell_task, "_create_new_cell_matches")
        self.mox.StubOutWithMock(white_space_grid_helper, "select_existing_cell_matches")
        self.mox.StubOutWithMock(cell_task, "_figure_out_match_difference")
        self.mox.StubOutWithMock(cell_task, "_batch_delete")
        self.mox.StubOutWithMock(cell_task, "_batch_insert")
        self.mox.StubOutWithMock(cell_task, "_format_results")

        # begin recording
        company_analytics_helper.query_company_return_store_analytics_date_range(company_id).AndReturn((mock_analytics_start_date, mock_analytics_end_date))
        time_series.get_start_of_next_month(mock_analytics_end_date).AndReturn(mock_analytics_end_date)
        white_space_grid_helper.get_current_stores_with_matches(company_id, mock_analytics_end_date).AndReturn(mock_company_counts_current)
        white_space_grid_helper.get_opened_stores_with_matches(company_id, mock_analytics_start_date, mock_analytics_end_date).AndReturn(mock_company_counts_openings)
        cell_task._create_new_cell_matches(mock_company_counts_current, mock_company_counts_openings).AndReturn(mock_new_matches)
        white_space_grid_helper.select_existing_cell_matches(company_id).AndReturn(mock_existing_matches)
        cell_task._figure_out_match_difference(mock_new_matches, mock_existing_matches).AndReturn((mock_to_insert, mock_to_delete))
        cell_task._batch_delete(mock_to_delete)
        cell_task._batch_insert(mock_to_insert)
        cell_task._format_results().AndReturn(mock_results)

        # replay all
        self.mox.ReplayAll()

        # bomboj for!
        results = cell_task.run()

        # make sure everything is good after the fact
        self.assertEqual(results, mock_results)
        self.assertEqual(cell_task._status, "success")
        self.assertIsNone(cell_task._exception)


    def test_cell_analytics__failed_run(self):

        # create mock vars
        company_id = "oooh the baby"

        # create mock input rec and task object
        input_rec = self._create_cell_analytics_input_rec(company_id)
        cell_task = WhiteSpaceCellAnalytics(input_rec)

        # create mock exception and method to raise it
        exception = Exception("Big Poppa")
        def raise_exception(company_id):
            raise exception

        # stub out methods
        self.mox.StubOutWithMock(company_analytics_helper, "query_company_return_store_analytics_date_range")

        # begin recording
        company_analytics_helper.query_company_return_store_analytics_date_range(company_id).WithSideEffects(raise_exception)

        # replay all
        self.mox.ReplayAll()

        # bomboj for!
        with self.assertRaises(Exception):
            cell_task.run()


    def test_cell_analytics__create_new_cell_matches(self):

        # create mock vars
        mock_company_id = "bob saget"
        mock_company_count_groups_current = [
            {
                "_id": 1,
                "data": {
                    "white_space_cell_matches": {
                        "threshold_1": { "cell_id": 1, "grid_id": 1, "grid_name": "one" },
                        "threshold_2": { "cell_id": 11, "grid_id": 2, "grid_name": "two" },
                        # new threshold/grid, which will not have any openings
                        "threshold_3": { "cell_id": 111, "grid_id": 3, "grid_name": "three" }
                    }
                }
            },
            {
                "_id": 2,
                "data": {
                    "white_space_cell_matches": {
                        "threshold_1": { "cell_id": 1, "grid_id": 1, "grid_name": "one" },
                        "threshold_2": { "cell_id": 11, "grid_id": 2, "grid_name": "two" }
                    }
                }
            },
            {
                "_id": 3,
                "data": {
                    "white_space_cell_matches": {
                        "threshold_1": { "cell_id": 2, "grid_id": 1, "grid_name": "one" },
                        "threshold_2": { "cell_id": 22, "grid_id": 2, "grid_name": "two" }
                    }
                }
            }
        ]
        mock_company_count_groups_openings = [
            # very important to make sure the first store that creates the cells (i.e. 1) is not an opening.
            # this tests a bug that I had found.
            # Ask Erez if you're changing this.
            { "_id": 2 },
            { "_id": 3 }
        ]

        # create mock input rec and task object
        input_rec = self._create_cell_analytics_input_rec(mock_company_id)
        cell_task = WhiteSpaceCellAnalytics(input_rec)

        # replay all
        self.mox.ReplayAll()

        # go!
        response = cell_task._create_new_cell_matches(mock_company_count_groups_current, mock_company_count_groups_openings)

        # make sure response is correct
        # IDs are converted to strings because that's how we expect the data to be stored in the db
        self.assertEqual(sorted(response), sorted([
            white_space_grid_helper.create_cell_match_record("1", "1", "one", "threshold_1", mock_company_id, 2, True),
            white_space_grid_helper.create_cell_match_record("11", "2", "two", "threshold_2", mock_company_id, 2, True),
            white_space_grid_helper.create_cell_match_record("111", "3", "three", "threshold_3", mock_company_id, 1, False),
            white_space_grid_helper.create_cell_match_record("2", "1", "one", "threshold_1", mock_company_id, 1, True),
            white_space_grid_helper.create_cell_match_record("22", "2", "two", "threshold_2", mock_company_id, 1, True),
        ]))


    def test_cell_analytics__figure_out_match_difference(self):

        # create simple mocks
        mock_company_id = "falafel"

        # mock new matches (cell 1 is gone, cell 2 changes, cell 3 stays the same, cell 4 is new, cell 5 changes)
        mock_new_matches = [
            white_space_grid_helper.create_cell_match_record("2", "grid_id", "grid_name", "threshold", mock_company_id, 4, False),
            white_space_grid_helper.create_cell_match_record("3", "grid_id", "grid_name", "threshold", mock_company_id, 6, False),
            white_space_grid_helper.create_cell_match_record("4", "grid_id", "grid_name", "threshold", mock_company_id, 8, False),
            white_space_grid_helper.create_cell_match_record("5", "grid_id", "grid_name", "threshold", mock_company_id, 10, False)
        ]

        # mock existing matches (company 1 exists, company 2 changes, company 3 stays the same)
        # create mongo ids, so that we can tell which ones are deleted...
        mock_existing_matches = [
            white_space_grid_helper.create_cell_match_record("1", "grid_id", "grid_name", "threshold", mock_company_id, 2, False, 11),
            white_space_grid_helper.create_cell_match_record("2", "grid_id", "grid_name", "threshold", mock_company_id, 1, False, 22),
            white_space_grid_helper.create_cell_match_record("3", "grid_id", "grid_name", "threshold", mock_company_id, 6, False, 33),
            white_space_grid_helper.create_cell_match_record("5", "grid_id", "grid_name", "threshold", mock_company_id, 10, True, 55)
        ]

        # create mock input rec and task object
        input_rec = self._create_cell_analytics_input_rec(mock_company_id)
        cell_task = WhiteSpaceCellAnalytics(input_rec)

        # go!
        to_insert, to_delete = cell_task._figure_out_match_difference(mock_new_matches, mock_existing_matches)

        # verify that to delete has company 1, which is gone, and company 2, which has been updated, and company 5, which is also updated
        self.assertEqual(sorted(to_delete), [11, 22, 55])

        # verify that company 2, which changed, and company 4, which is new, company 5, which changed, are to be inserted
        self.assertEqual(sorted(to_insert), sorted([mock_new_matches[0], mock_new_matches[2], mock_new_matches[3]]))



    # --------------------------- Private Helpers --------------------------- #

    def _create_grid_analytics_input_rec(self, spawn_async_tasks = True):
        return {
            "context": self.context,
            "task_id": ObjectId(),
            "spawn_async_tasks": spawn_async_tasks
        }

    def _create_cell_analytics_input_rec(self, company_id):
        return {
            "context": self.context,
            "company_id": company_id,
            "as_of_date": self.as_of_date
        }

    def _create_cell_rec(self, company_id, spawn_async_tasks = True):
        return {
            "input": {
                "company_id": company_id
            },
            "meta": {
                "async": spawn_async_tasks,
                "insert_wfs_task": not spawn_async_tasks
            }
        }

    def _create_mock_cell(self, cell_id):
        return {
            "_id": cell_id,
            "data": {
                "grid_id" : "grid_id",
                "grid_name" : "grid_name",
                "threshold" : "threshold",
                "demographics": {
                    "HINC0_CY": { "value": 1 },
                    "HINC100_CY": { "value": 2 },
                    "HINC150_CY": { "value": 3 },
                    "HINC15_CY": { "value": 4 },
                    "HINC200_CY": { "value": 5 },
                    "HINC25_CY": { "value": 6 },
                    "HINC35_CY": { "value": 7 },
                    "HINC50_CY": { "value": 8 },
                    "HINC75_CY": { "value": 9 },
                    "PCI_CY": { "value": 10 },
                    "TOTHH_CY": { "value": 11 },
                    "TOTPOP_CY": { "value": 12 }
                }
            }
    }