import mox
from mox import IsA
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from common.web_helpers import logging_helper
from core.service.svc_workflow.implementation.task.implementation.retail_input_tasks.company_deletion import CompanyDeletion

__author__ = 'erezrubinstein'

import unittest




class TestWorkflowCompanyDeletion(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(TestWorkflowCompanyDeletion, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_logger = Dependency("FlaskLogger").value

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.company_id = "chilly_willy"
        self.company_name = "chicken_woot"
        self.input_rec = {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "context": self.context
        }

        # create company deletion object
        self.deleter = CompanyDeletion(self.input_rec)

        # reset so we can record again
        self.mox.ResetAll()


    def doCleanups(self):

        # call parent clean up
        super(TestWorkflowCompanyDeletion, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_init(self):

        # verify that the base variables match the passed in parameters
        self.assertEqual(self.deleter.company_id, self.company_id)
        self.assertEqual(self.deleter.company_name, self.company_name)
        self.assertEqual(self.deleter.context, self.context)


    def test_skip_published_company(self):
        """
        make sure that a company is not deleted if it's 'published'
        """

        # stub out various methods
        self.mox.StubOutWithMock(self.deleter, "_get_company")
        self.mox.StubOutWithMock(self.deleter, "_check_is_company_published")
        self.mox.StubOutWithMock(self.deleter, "to_dict")

        # start recording
        self.deleter._get_company()
        self.deleter._check_is_company_published().AndReturn(True)
        self.deleter.to_dict().AndReturn("woot")

        # replay all
        self.mox.ReplayAll()

        # run and verify results
        results = self.deleter.run()
        self.assertEqual(results, "woot")


    def test_run__successful(self):
        """
        verify all the steps of a successful delete
        """

        # stub out various methods
        self.mox.StubOutWithMock(self.deleter, "_get_company")
        self.mox.StubOutWithMock(self.deleter, "_check_is_company_published")
        self.mox.StubOutWithMock(self.deleter, "_mark_company_for_deletion")
        self.mox.StubOutWithMock(self.deleter, "_archive_company")
        self.mox.StubOutWithMock(self.deleter, "_delete_trade_areas")
        self.mox.StubOutWithMock(self.deleter, "_delete_rirs")
        self.mox.StubOutWithMock(self.deleter, "_delete_stores")
        self.mox.StubOutWithMock(self.deleter, "_delete_addresses")
        self.mox.StubOutWithMock(self.deleter, "_delete_tasks")
        self.mox.StubOutWithMock(self.deleter, "_get_task_groups")
        self.mox.StubOutWithMock(self.deleter, "_delete_task_groups")
        self.mox.StubOutWithMock(self.deleter, "_delete_files")
        self.mox.StubOutWithMock(self.deleter, "_find_competitors")
        self.mox.StubOutWithMock(self.deleter, "_delete_ccis")
        self.mox.StubOutWithMock(self.deleter, "_run_plan_b_on_competitors")
        self.mox.StubOutWithMock(self.deleter, "_delete_white_space_matches")
        self.mox.StubOutWithMock(self.deleter, "_delete_company")
        self.mox.StubOutWithMock(self.deleter, "to_dict")

        # start recording
        self.deleter._get_company()
        self.deleter._check_is_company_published().AndReturn(False)
        self.deleter._mark_company_for_deletion()
        self.deleter._archive_company().AndReturn(self.deleter)
        self.deleter._delete_trade_areas().AndReturn(self.deleter)
        self.deleter._delete_rirs().AndReturn(self.deleter)
        self.deleter._delete_stores().AndReturn(self.deleter)
        self.deleter._delete_addresses().AndReturn(self.deleter)
        self.deleter._delete_tasks().AndReturn(self.deleter)
        self.deleter._get_task_groups().AndReturn(self.deleter)
        self.deleter._delete_task_groups().AndReturn(self.deleter)
        self.deleter._delete_files().AndReturn(self.deleter)
        self.deleter._find_competitors().AndReturn(self.deleter)
        self.deleter._delete_ccis().AndReturn(self.deleter)
        self.deleter._run_plan_b_on_competitors().AndReturn(self.deleter)
        self.deleter._delete_white_space_matches().AndReturn(self.deleter)
        self.deleter._delete_company().AndReturn(self.deleter)
        self.deleter.to_dict().AndReturn("woot")

        # replay all
        self.mox.ReplayAll()

        # run and verify results
        results = self.deleter.run()
        self.assertEqual(results, "woot")


    def test_run__failure(self):
        """
        verify all the steps of a failed delete (i.e. raises an exception
        """

        # fake raise exception method
        exception = Exception("YO!")
        def raise_exception():
            raise exception

        # stub out various methods
        self.mox.StubOutWithMock(self.deleter, "_get_company")
        self.mox.StubOutWithMock(self.deleter, "_check_is_company_published")
        self.mox.StubOutWithMock(self.deleter, "_mark_company_for_deletion")
        self.mox.StubOutWithMock(self.deleter, "_archive_company")
        self.mox.StubOutWithMock(logging_helper, "log_exception")
        self.mox.StubOutWithMock(self.deleter, "_unmark_company_for_deletion")

        # start recording
        self.deleter._get_company()
        self.deleter._check_is_company_published().AndReturn(False)
        self.deleter._mark_company_for_deletion()
        self.deleter._archive_company().WithSideEffects(raise_exception)
        logging_helper.log_exception(self.mock_logger, "Error Deleting a Company", exception, IsA(basestring))
        self.deleter._unmark_company_for_deletion()

        # replay all
        self.mox.ReplayAll()

        # run and verify exception
        with self.assertRaises(Exception) as ex:
            self.deleter.run()
        self.assertEqual('YO!', ex.exception.message)


    def test_delete_addresses(self):
        """
        Makes sure that delete addresses works with the correct logic
        """

        # create mock addresses.  One with one company, to be deleted.  The other with two companies, to be updated.
        mock_addresses = [
            { "_id": "chicken", "data": { "company_ids": [self.company_id] }},
            { "_id": "woot", "data": { "company_ids": [self.company_id, 2] }}
        ]

        # expected parameters for query
        expected_parameters = {
            "query" : { "data.company_ids": self.company_id },
            "entity_fields": ["_id", "data.company_ids"]
        }
        update_query = { "_id": "woot" }
        update_operation = { "$pull": { "company_ids": self.company_id }}

        # start recording
        self.mock_main_access.mds.call_find_entities_raw("address", expected_parameters, self.context).AndReturn(mock_addresses)
        self.mock_main_access.mds.call_del_entity("address", "chicken", error_if_absent=False)
        self.mock_main_access.mds.call_batch_update_entities("address", update_query, update_operation, self.context)

        # replay all
        self.mox.ReplayAll()

        # run!
        self.deleter._delete_addresses_one_by_one()


if __name__ == '__main__':
    unittest.main()
