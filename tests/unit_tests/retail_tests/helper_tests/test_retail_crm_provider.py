from retail.v010.helpers.retail_crm_provider import RetailCRMProvider
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
import unittest
import mox
import base64
import json


__author__ = 'jsternberg'


class RetailCRMProviderTests(mox.MoxTestBase):

    @classmethod
    def setUpClass(cls):

        cls.url = "https://api.insight.ly/v2.1/"
        cls.headers = {
            "Authorization": "Basic %s" % base64.b64encode("1234456789:"),
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json"
        }

        cls.stub_orgs = [{
            "ORGANISATION_ID": 999,
            "ORGANISATION_NAME": "Church of the Subgenius"
        }]

        cls.stub_contacts = [{
            "FIRST_NAME": "Bob",
            "LAST_NAME": "Dobbs",
            "LINKS": [{
                "ORGANISATION_ID": 999,
                "ROLE": "Member"
            }],
            "TAGS":[{
                "TAG_NAME": "web_lead"
            }],
            "CONTACTINFOS": [{
                "TYPE": "Email",
                "LABEL": "Work",
                "DETAIL": "bob@slack.com"
            },{
                "TYPE": "Phone",
                "LABEL": "Work",
                "DETAIL": "555-1212"
            }],
            "CUSTOMFIELDS": [{
                "CUSTOM_FIELD_ID": "CONTACT_FIELD_8",
                "FIELD_VALUE": "Opted In"
            }]
        }]

    def setUp(self):
        # call parent set up
        super(RetailCRMProviderTests, self).setUp()
        # register mock dependencies
        register_common_mox_dependencies(self.mox)
        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value
        # Create caller context
        self.context = {"user_id": 1, "source": "test_prospect_controller.py"}
        # Set up useful mocks
        self.mock = self.mox.CreateMock(RetailCRMProvider)

        # stub out API key & register as the config
        self.mock_retail_confg = {
            "INSIGHTLY_CRM_ENABLED": True,
            "INSIGHTLY_CRM_API_KEY": "1234456789"
        }
        dependencies.register_dependency("RetailConfig", self.mock_retail_confg, force_singleton=True)

    def doCleanups(self):
        super(RetailCRMProviderTests, self).doCleanups()
        dependencies.clear()


    def test_retail_crm_provider__init(self):

        crm_provider = RetailCRMProvider(self.mock_retail_confg, self.logger)
        self.assertEqual(crm_provider.url, self.url)
        self.assertEqual(crm_provider.headers, self.headers)

    def test_retail_crm_provider__get_all_organizations(self):

        crm_provider = RetailCRMProvider(self.mock_retail_confg, self.logger)

        response = self.__build_mock_org_get_response()
        crm_provider.rest_provider.get(self.url + "organisations?Brief=True", headers=self.headers).AndReturn(response)

        self.mox.ReplayAll()

        orgs = crm_provider.get_all_organizations()

        self.assertEqual(orgs, self.stub_orgs)

    def test_retail_crm_provider__get_organization(self):

        crm_provider = RetailCRMProvider(self.mock_retail_confg, self.logger)

        response = self.__build_mock_org_get_response()
        crm_provider.rest_provider.get(self.url + "organisations?Brief=True", headers=self.headers).AndReturn(response)

        self.mox.ReplayAll()

        org = crm_provider.get_organization(self.stub_orgs[0]["ORGANISATION_NAME"])

        self.assertEqual(org, self.stub_orgs[0])

    def test_retail_crm_provider__create_organization(self):

        crm_provider = RetailCRMProvider(self.mock_retail_confg, self.logger)

        org = {
            "ORGANISATION_NAME": self.stub_orgs[0]["ORGANISATION_NAME"]
        }
        response = self.__build_mock_org_post_response()
        crm_provider.rest_provider.post(self.url + "organisations", json.dumps(org), headers=self.headers).AndReturn(response)

        self.mox.ReplayAll()

        org = crm_provider.create_organization(self.stub_orgs[0]["ORGANISATION_NAME"])

        self.assertEqual(org, self.stub_orgs[0])

    def test_retail_crm_provider__create_contact(self):

        crm_provider = RetailCRMProvider(self.mock_retail_confg, self.logger)

        self.mox.StubOutWithMock(crm_provider, "get_organization")
        crm_provider.get_organization(self.stub_orgs[0]["ORGANISATION_NAME"]).AndReturn(self.stub_orgs[0])

        response = self.__build_mock_contact_post_response()
        crm_provider.rest_provider.post(self.url + "contacts", json.dumps(self.stub_contacts[0]), headers=self.headers).AndReturn(response)

        self.mox.ReplayAll()

        prospect = {
            "name": "Bob Dobbs",
            "organization": "Church of the Subgenius",
            "phone": "555-1212",
            "email": "bob@slack.com",
            "listOptIn": True
        }

        contact = crm_provider.create_contact(prospect)

        self.assertEqual(contact, self.stub_contacts[0])


    ## ------------- private funcs --------------- ##


    def __build_mock_org_get_response(self):

        response = self.mox.CreateMockAnything()

        def stub_json():
            return self.stub_orgs

        response.json = stub_json

        return response

    def __build_mock_org_post_response(self):

        response = self.mox.CreateMockAnything()

        def stub_json():
            return self.stub_orgs[0]

        response.json = stub_json

        return response

    def __build_mock_contact_post_response(self):

        response = self.mox.CreateMockAnything()

        def stub_json():
            return self.stub_contacts[0]

        response.json = stub_json

        return response


if __name__ == '__main__':
    unittest.main()