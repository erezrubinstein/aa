from retail.v010.data_access.controllers.prospect_controller import ProspectController
from retail.v010.helpers.retail_crm_provider import RetailCRMProvider
from common.web_helpers.retail_email_provider import RetailEmailProvider
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.errors import BadRequestError
import unittest
import mox
import datetime


__author__ = 'jsternberg'


class ProspectControllerTests(mox.MoxTestBase):

    def setUp(self):
        # call parent set up
        super(ProspectControllerTests, self).setUp()
        # register mock dependencies
        register_common_mox_dependencies(self.mox)
        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value
        # Create caller context
        self.context = {"user_id": 1, "source": "test_prospect_controller.py"}
        # Set up useful mocks
        self.mock = self.mox.CreateMock(ProspectController)
        self.mock.Prospect = self.mox.CreateMockAnything()

        # email provider & CRM provider
        self.mock_retail_email_provider = self.mox.CreateMock(RetailEmailProvider)
        self.mock_retail_crm_provider = self.mox.CreateMock(RetailCRMProvider)

        #register these as dependencies since they are used that way
        dependencies.register_dependency("RetailEmailProvider", self.mock_retail_email_provider, force_singleton=True)
        dependencies.register_dependency("RetailCRMProvider", self.mock_retail_crm_provider, force_singleton=True)


    def doCleanups(self):
        super(ProspectControllerTests, self).doCleanups()
        dependencies.clear()

    ####################################################
    # ProspectController.create_prospect()

    def test_create_prospect__bad_request_error(self):

        prospect_ctrl = ProspectController()
        bad_inputs = ["", None, 1]

        for badness in bad_inputs:
            with self.assertRaises(BadRequestError):
                prospect_ctrl.create_prospect(badness, badness, "Y", badness, badness, {}, "0.0.0.0", "user_agent", "referrer", "user")

        bad_email = "whatever, dude"
        with self.assertRaises(BadRequestError):
            prospect_ctrl.create_prospect("The Dude", bad_email, "Y", "White Russians, Inc.", "555-1212", {}, "0.0.0.0", "user_agent", "referrer", "user")

        bad_query_dict = 1234.5
        with self.assertRaises(BadRequestError):
            prospect_ctrl.create_prospect("The Dude", "thedude@dudeco.com", "Y", "White Russians, Inc.", "555-1212", bad_query_dict, "0.0.0.0", "user_agent", "referrer", "user")

        bad_list_opt_ins = [None, "not sure"]
        for badness in bad_list_opt_ins:
            with self.assertRaises(BadRequestError):
                prospect_ctrl.create_prospect("The Dude", "thedude@dudeco.com", badness, "White Russians, Inc.", "555-1212", bad_query_dict, "0.0.0.0", "user_agent", "referrer", "user")

    def test_create_prospect__internal_calls(self):

        # test input data
        name = "The Dude"
        email = "thedude@dudeco.com"
        listOptIn = "y"
        organization = "White Russians, Inc."
        phone = "555-1212"
        query_dict = {"rock": "roll"}
        ip_address = "1.2.3.4"
        user_agent = "user_agent"
        referrer = "referrer"
        user = "The Dude User"

        # expected serialized prospect
        prospect = {
            "name": "The Dude",
            "email": "thedude@dudeco.com",
            "listOptIn": "y",
            "organization": "White Russians, Inc.",
            "phone": "555-1212"
        }

        # Begin recording

        self.mock.Prospect.create(serialize=True, name=name, email=email, listOptIn=True, organization=organization, phone=phone,
                                        query_params=query_dict, ip_address=ip_address, user_agent=user_agent,
                                        referrer=referrer, user=user, creation_date=mox.IsA(datetime.datetime)).AndReturn(prospect)

        self.mock_retail_email_provider.send_new_sales_prospect_notification(prospect)
        self.mock_retail_email_provider.send_sales_contact_confirmation(prospect)
        self.mock_retail_crm_provider.create_contact(prospect)

        self.mox.ReplayAll()

        result = ProspectController.create_prospect(self.mock, name, email, listOptIn, organization, phone, query_dict, ip_address, user_agent, referrer, user)

        self.assertEqual(result, prospect)


if __name__ == '__main__':
    unittest.main()