from common.web_helpers.retail_email_provider import RetailEmailProvider
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.service_access.utilities.errors import ServiceCallError
from common.utilities.inversion_of_control import Dependency, dependencies
import unittest
import mox


__author__ = 'clairseager'


class RetailEmailProviderTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RetailEmailProviderTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value

        self.mock_emailer = self.mox.CreateMock(RetailEmailProvider)
        self.mock_emailer.mailer = self.mox.CreateMockAnything()
        self.mock_emailer.Message = self.mox.CreateMockAnything()
        self.mock_emailer.author = None
        self.mock_emailer.environment = "INTEGRATION TESTS"


    def doCleanups(self):

        super(RetailEmailProviderTests, self).doCleanups()
        dependencies.clear()

    ####################################################
    # RetailEmailProvider.new_message()

    def test_new_message(self):

        send_to = {"to": "Psy@x.x"}
        content = {
            "subject": "Foo Email Subject",
            "rich": "<b>Bar</b> rich email body",
            "plain": "Oppan Gangnam style"
        }

        # check that we send the right kwargs to Message
        self.mock_emailer.Message(to=send_to["to"], author=self.mock_emailer.author, cc=None, bcc=None, **content).AndReturn("SPAM")

        self.mox.ReplayAll()
        RetailEmailProvider._send_new_message(self.mock_emailer, send_to, content)

    def test_new_message__with_errors(self):

        send_to = {
            "to": "Psy@x.x",
            "cc": "asdf@x.x",
            "bcc": "qwerty@x.x"
        }

        subject = "Foo Email Subject"
        rich = "<b>Bar</b> rich email body"
        plain = "Oppan Gangnam style"

        provider = RetailEmailProvider.__new__(RetailEmailProvider)

        # no recipients
        with self.assertRaises(ServiceCallError) as cm:
            provider._send_new_message({}, {"subject":subject, "rich":rich, "plain":plain })
        self.assertEqual(cm.exception.message, "Email recipients are required. Please supply an email or a list of emails.")

        # no Subject
        with self.assertRaises(ServiceCallError) as cm:
            provider._send_new_message(send_to, {"rich":rich, "plain": plain})
        self.assertEqual(cm.exception.message, "Email subject is required.")

        # no body
        with self.assertRaises(ServiceCallError) as cm:
            provider._send_new_message(send_to, {"subject": subject})
        self.assertEqual(cm.exception.message, "Email content is required. Please supply plain or rich content for the email body.")

    #TODO: test send mail method - including failures on the mailer, which are not handled at the moment


if __name__ == '__main__':
    unittest.main()