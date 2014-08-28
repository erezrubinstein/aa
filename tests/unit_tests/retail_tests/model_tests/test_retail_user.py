from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from retail.v010.data_access.models.user import User
import mox


__author__ = 'erezrubinstein'


class RetailUserTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RetailUserTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value

    def doCleanups(self):

        # call parent clean up and clean dependencies
        super(RetailUserTests, self).doCleanups()
        dependencies.clear()

    def test_user_password_10_character_requirement(self):

        # verify that a password with 9 characters fails
        self.assertEqual(User.validate_password("123456789"), "Passwords must be at least 10 characters.")

        # verify that a password with 10 characters passes
        self.assertEqual(User.validate_password("1234567890"), "")

    def test_user_password_non_alpha_required(self):

        # verify that a password with only alpha characters fails
        self.assertEqual(User.validate_password("asdfasdfasdf"),
                         "Password requires a non alpha character (i.e. number or symbol)")

        # verify that a password with one non alpha character passes
        self.assertEqual(User.validate_password("asdfasdfasd1"), "")
