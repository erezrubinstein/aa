import os
import mox
import unittest
from common.helpers.configuration_helper import read_config_yml_file
from common.utilities.inversion_of_control import dependencies, Dependency
from economics.helpers.economics_email_template import EconomicsEmailer
from geoprocessing.helpers.dependency_helper import register_mock_dependencies

__author__ = 'clairseager'


class EconomicsEmailHelperTest(mox.MoxTestBase):

    def setUp(self):
        super(EconomicsEmailHelperTest, self).setUp()

        # set up mocks
        register_mock_dependencies()
        self.email_provider = Dependency("EmailProvider").value

        self.email_recipients = "taco"
        self.module_name = "Mad Tea Party"

        self.exception_message = "Something That Can Go Wrong, Will."
        self.info = {"what else": "happened today?"}

    def tearDown(self):
        # remove dependencies for next set of tests
        dependencies.clear()

    def test_email_config(self):

        config_file_path = os.path.dirname(os.path.realpath(__file__)) + '/../../../economics/config.yml'
        config = read_config_yml_file(config_file_path)

        # did you really mean to change that email address?
        self.assertItemsEqual(config["config_prod"]["email_settings"]["email_recipients_developers"], ["engineering@signaldataco.com"])
        self.assertEqual(config["config_prod"]["email_settings"]["username"], "support@signaldataco.com")


    def test_email_without_error(self):
        emailer = EconomicsEmailer(self.email_recipients, self.module_name, exception_message = None, info = None)
        # go
        emailer.send_email()

        # make sure an email was sent
        self.assertEqual(self.email_provider.to_email, self.email_recipients)
        self.assertEqual(self.email_provider.from_email, "zoolander@signaldataco.com")
        self.assertEqual(self.email_provider.subject, "%s Succeeded" % self.module_name)
        self.assertIsNotNone(self.email_provider.message)
        self.assertIn(self.module_name, self.email_provider.message)
        self.assertIn("Success", self.email_provider.message)

    def test_email_with_info(self):
        emailer = EconomicsEmailer(self.email_recipients, self.module_name, exception_message = None, info = self.info)
        # go
        emailer.send_email()

        # make sure an email was sent
        self.assertEqual(self.email_provider.to_email, self.email_recipients)
        self.assertEqual(self.email_provider.from_email, "zoolander@signaldataco.com")
        self.assertEqual(self.email_provider.subject, "%s Succeeded" % self.module_name)
        self.assertIsNotNone(self.email_provider.message)
        self.assertIn(self.module_name, self.email_provider.message)
        self.assertIn("Success", self.email_provider.message)
        self.assertIn(str(self.info), self.email_provider.message)

    def test_email_with_exception(self):
        emailer = EconomicsEmailer(self.email_recipients, self.module_name, exception_message = self.exception_message, info = None)
        # go
        emailer.send_email()

        # make sure an email was sent
        self.assertEqual(self.email_provider.to_email, self.email_recipients)
        self.assertEqual(self.email_provider.from_email, "zoolander@signaldataco.com")
        self.assertEqual(self.email_provider.subject, "%s Error!" % self.module_name)
        self.assertIsNotNone(self.email_provider.message)
        self.assertIn("%s Error!" % self.module_name, self.email_provider.message)
        self.assertIn(self.exception_message, self.email_provider.message)



if __name__ == '__main__':
    unittest.main()
