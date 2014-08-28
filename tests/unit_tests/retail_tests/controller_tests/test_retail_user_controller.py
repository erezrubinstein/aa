from retail.v010.data_access.controllers.user_controller import UserController
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.errors import *
from common.utilities import date_utilities
import unittest
import datetime
import mox


__author__ = 'vgold'


class RetailUserControllerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(RetailUserControllerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_store_helper.py"}

        # Set up useful mocks
        self.mock = self.mox.CreateMock(UserController)
        self.mock.User = self.mox.CreateMockAnything()
        self.mock.Role = self.mox.CreateMockAnything()
        self.mock.Client = self.mox.CreateMockAnything()
        self.mock.Notification = self.mox.CreateMockAnything()
        self.mock.Setting = self.mox.CreateMockAnything()
        self.mock.SurveyQuestion = self.mox.CreateMockAnything()
        self.mock.SurveyResponse = self.mox.CreateMockAnything()

    def doCleanups(self):

        super(RetailUserControllerTests, self).doCleanups()
        dependencies.clear()

    ####################################################
    # UserController.create_user()
    
    def test_create_user__invalid_actor_id(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(None)
        self.mox.ReplayAll()

        with self.assertRaises(NotFoundError) as cm:
            UserController.create_user(self.mock, actor_email, {})
        self.assertEqual(cm.exception.message, 'User with email %s not found.' % actor_email)

    def test_create_user__invalid_actor_permission(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("user")

        self.mox.ReplayAll()
        with self.assertRaises(BadRequestError) as cm:
            UserController.create_user(self.mock, actor_email, {})
        self.assertEqual(cm.exception.message, 'Must be admin or client support to create users.')

    def test_create_user__as_client_support(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("client_support")

        user_dict = {
            '123': '456'
        }
        user = self.mox.CreateMockAnything()
        self.mock._create_user_direct(actor_email, user_dict).AndReturn(user)
        user.serialize().AndReturn(True)

        self.mox.ReplayAll()
        result = UserController.create_user(self.mock, actor_email, user_dict)
        self.assertEqual(result, True)

    def test_create_user__as_admin(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("admin")

        user_dict = {
            '123': '456'
        }
        user = self.mox.CreateMockAnything()
        self.mock._create_user_direct(actor_email, user_dict).AndReturn(user)
        user.serialize().AndReturn(True)

        self.mox.ReplayAll()
        result = UserController.create_user(self.mock, actor_email, user_dict)
        self.assertEqual(result, True)

    ####################################################
    # UserController._create_user_direct()

    def test_create_user_direct__missing_fields(self):

        actor_email = 'asdf'
        user_dict = {"name": "asdf", "email": "asdf@asdf.com"}

        with self.assertRaises(BadRequestError) as cm:
            UserController._create_user_direct(self.mock, actor_email, user_dict)
        self.assertIn('Expected keys', cm.exception.message)

    def test_create_user_direct__user_email_exists(self):

        actor_email = 'asdf'
        user_dict = {"name": "asdf",
                     "email": "asdf@asdf.com",
                     "password": "password",
                     "active": True,
                     "retail_access": True,
                     "retailer_access": False,
                     "client": 1,
                     "roles": ["user"]}

        self.mock.User.get(user_dict["email"]).AndReturn(True)

        self.mox.ReplayAll()
        with self.assertRaises(BadRequestError) as cm:
            UserController._create_user_direct(self.mock, actor_email, user_dict)
        self.assertEqual(cm.exception.message, "Email address %s is invalid or already taken." % user_dict["email"])

    def test_create_user_direct__invalid_client_name(self):

        actor_email = 'asdf'
        user_dict = {"name": "asdf",
                     "email": "asdf@asdf.com",
                     "password": "password",
                     "active": True,
                     "retail_access": True,
                     "retailer_access": False,
                     "client": 1,
                     "roles": ["user"]}

        self.mock.User.get(user_dict["email"]).AndReturn(False)
        self.mock.Client.get(user_dict["client"]).AndReturn(False)

        self.mox.ReplayAll()

        with self.assertRaises(NotFoundError) as cm:
            UserController._create_user_direct(self.mock, actor_email, user_dict)
        self.assertEqual(cm.exception.message, "Client with name %s not found." % user_dict["client"])

    def test_create_user_direct__no_actor_email(self):

        user_email = "asdf@asdf.com"

        self.mock.User.get(user_email).AndReturn(False)

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(now)

        user_dict = {
            "name": "asdf",
            "email": user_email,
            "password": "",
            "active": False,
            "retail_access": True,
            "retailer_access": False,
            "confirmed_at": None,
            "registration_date": now,
            "client": 1,
            "roles": ["user"],
            "expiration_date": "3000-02-01",
            "subscription_level": "Subscriber",
            "default_module": "Investors",
            "first_login_date": None,
            "custom_analytics_enabled": True
        }

        client = self.mox.CreateMockAnything()
        self.mock.Client.get(user_dict["client"]).AndReturn(client)

        self.mox.StubOutWithMock(date_utilities, "parse_date")
        date_utilities.parse_date("3000-02-01").AndReturn("3000-02-01")

        clean_dict = dict(user_dict, client=client)

        self.mock.User.create(**clean_dict).AndReturn("user")
        client.update(push__user_emails="user")

        self.mox.ReplayAll()

        result = UserController._create_user_direct(self.mock, None, user_dict)
        self.assertEqual(result, "user")

    def test_create_user_direct__with_actor_email(self):

        actor_email = 'asdf'
        user_email = "asdf@asdf.com"

        self.mock.User.get(user_email).AndReturn(False)

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn(now)

        user_dict = {
            "name": "asdf",
            "email": user_email,
            "password": "",
            "active": False,
            "retail_access": True,
            "retailer_access": False,
            "confirmed_at": None,
            "registration_date": now,
            "client": 1,
            "roles": ["user"],
            "expiration_date": "3000-02-01",
            "subscription_level": "Subscriber",
            "default_module": "Investors",
            "first_login_date": None,
            "custom_analytics_enabled": True
        }

        client = self.mox.CreateMockAnything()
        self.mock.Client.get(user_dict["client"]).AndReturn(client)

        self.mox.StubOutWithMock(date_utilities, "parse_date")
        date_utilities.parse_date("3000-02-01").AndReturn("3000-02-01")

        self.mock.User.get(actor_email).AndReturn("actor")
        user_dict["last_modified_by"] = "actor"

        clean_dict = dict(user_dict, client=client)

        self.mock.User.create(**clean_dict).AndReturn("user")
        client.update(push__user_emails="user")

        self.mox.ReplayAll()

        result = UserController._create_user_direct(self.mock, actor_email, user_dict)
        self.assertEqual(result, "user")

    ####################################################
    # UserController.update_user()

    def test_update_user__invalid_actor_id(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(None)
        self.mox.ReplayAll()
        user_email = 'ewrw'

        with self.assertRaises(NotFoundError) as cm:
            UserController.update_user(self.mock, actor_email, user_email, {})
        self.assertEqual(cm.exception.message, 'User with email %s not found.' % actor_email)


    def test_update_user__user_not_found(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("user")

        self.mock.User.get(actor_email, include_deleted=True).AndReturn(None)

        self.mox.ReplayAll()
        with self.assertRaises(NotFoundError) as cm:
            UserController.update_user(self.mock, actor_email, actor_email, {})
        self.assertEqual(cm.exception.message, 'User with email %s not found.' % actor_email)

    def test_update_user__as_user(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("user")

        user = self.mox.CreateMockAnything()
        user.id = "id"
        user.deleted = False
        self.mock.User.get(actor_email, include_deleted=True).AndReturn(user)

        clean_dict = {"password": "hhjkhl"}
        self.mock._handle_notification_updates(clean_dict).AndReturn(clean_dict)

        final_dict = dict(clean_dict, last_modified_by=True)
        user.update(**final_dict).AndReturn(user)
        self.mock.User.get(actor_email, include_deleted=True).AndReturn(user)
        user.serialize().AndReturn(user)

        user_dict = {
            "active": True,
            "password": "hhjkhl",
            "roles": ["user"]
        }

        self.mox.ReplayAll()

        result = UserController.update_user(self.mock, actor_email, actor_email, user_dict)
        self.assertEqual(result, user)

    def test_update_user__as_client_support(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("client_support")

        user = self.mox.CreateMockAnything()
        user.id = "id"
        user.deleted = False
        self.mock.User.get(actor_email, include_deleted=True).AndReturn(user)

        clean_dict = {"active": True, "roles": ["user"]}
        self.mock._handle_notification_updates(clean_dict).AndReturn(clean_dict)

        final_dict = dict(clean_dict, last_modified_by=True)
        user.update(**final_dict).AndReturn(user)
        self.mock.User.get(actor_email, include_deleted=True).AndReturn(user)
        user.serialize().AndReturn(user)

        user_dict = {
            "active": True,
            "roles": ["user"]
        }

        self.mox.ReplayAll()

        result = UserController.update_user(self.mock, actor_email, actor_email, user_dict)
        self.assertEqual(result, user)

    def test_update_user__as_admin(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("admin")

        user = self.mox.CreateMockAnything()
        user.id = "id"
        user.deleted = False
        self.mock.User.get(actor_email, include_deleted=True).AndReturn(user)

        clean_dict = {
            "name": "name",
            "active": True,
            "roles": ["user"]
        }
        self.mock._handle_notification_updates(clean_dict).AndReturn(clean_dict)

        final_dict = dict(clean_dict, last_modified_by=True)
        user.update(**final_dict).AndReturn(user)
        self.mock.User.get(actor_email, include_deleted=True).AndReturn(user)
        user.serialize().AndReturn(user)

        user_dict = {
            "name": "name",
            "active": True,
            "roles": ["user"],
            "client": "random client"
        }

        self.mox.ReplayAll()

        result = UserController.update_user(self.mock, actor_email, actor_email, user_dict)

        self.assertEqual(result, user)

    ###########################################
    # UserController.delete_user()

    def test_delete_user__actor_not_found(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(False)

        user_email = ';lkj'

        self.mox.ReplayAll()

        with self.assertRaises(NotFoundError) as cm:
            UserController.delete_user(self.mock, actor_email, user_email)
        self.assertEqual(cm.exception.message, 'User with email %s not found.' % actor_email)

    def test_delete_user__wrong_permission(self):

        actor_email = "asdfasdf"
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("user")

        user_email = 'avsd'

        self.mox.ReplayAll()
        with self.assertRaises(ForbiddenError) as cm:
            UserController.delete_user(self.mock, actor_email, user_email)
        self.assertEqual(cm.exception.message, 'Only client support and admin accounts can delete other user accounts.')

    def test_delete_user__user_not_found(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("client_support")

        user_email = 'trewewrt'
        self.mock.User.get(user_email).AndReturn(False)

        self.mox.ReplayAll()
        with self.assertRaises(NotFoundError) as cm:
            UserController.delete_user(self.mock, actor_email, user_email)
        self.assertEqual(cm.exception.message, 'User with email %s not found.' % user_email)

    def test_delete_user(self):

        actor_email = 'asdf'
        self.mock.User.get(actor_email).AndReturn(True)

        self.mock._get_permission_level_from_user_email(actor_email).AndReturn("client_support")

        user_email = 'cvasd'
        user = self.mox.CreateMockAnything()
        user.id = "id"
        self.mock.User.get(user_email).AndReturn(user)

        user.update(deleted=True, active=False, last_modified_by=True).AndReturn(user)

        self.mox.ReplayAll()
        UserController.delete_user(self.mock, actor_email, user_email)

    ###########################################
    # UserController.__get_permission_level_from_user_id()

    def test_get_permission_level_from_user_email__user_not_found(self):

        user_email = 'asdf'
        self.mock.User.get(user_email).AndReturn(False)

        self.mox.ReplayAll()
        with self.assertRaises(NotFoundError) as cm:
            UserController._get_permission_level_from_user_email(self.mock, user_email)
        self.assertEqual(cm.exception.message, 'User with email %s not found.' % user_email)

    def test_get_permission_level_from_user_email__user(self):

        user_email = 'asdf'
        user = self.mox.CreateMockAnything()
        user.roles = [{"name": "user"}, {"name": "asdf"}]
        self.mock.User.get(user_email).AndReturn(user)

        self.mox.ReplayAll()
        result = UserController._get_permission_level_from_user_email(self.mock, user_email)

        self.assertEqual(result, 'user')

    def test_get_permission_level_from_user_email__client_support(self):

        user_email = 'asdf'
        user = self.mox.CreateMockAnything()
        user.roles = [{"name": "user"}, {"name": "client_support"}]
        self.mock.User.get(user_email).AndReturn(user)

        self.mox.ReplayAll()
        result = UserController._get_permission_level_from_user_email(self.mock, user_email)

        self.assertEqual(result, 'client_support')

    def test_get_permission_level_from_user_email__admin(self):

        user_email = 'asdf'
        user = self.mox.CreateMockAnything()
        user.roles = [{"name": "user"}, {"name": "client_support"}, {"name": "admin"}]
        self.mock.User.get(user_email).AndReturn(user)

        self.mox.ReplayAll()
        result = UserController._get_permission_level_from_user_email(self.mock, user_email)

        self.assertEqual(result, 'admin')

    #---------------------------------# Private Methods #---------------------------------#

    counter = 0

    @classmethod
    def setUpClass(cls):
        cls.counter = 0

    @classmethod
    def get_counter(cls):
        counter = cls.counter
        cls.counter += 1
        return counter

    def __get_user_dict(self, **kwargs):

        return dict({"email": "test%d@test.com" % self.get_counter(),
                     "active": True,
                     "password": "test",
                     "confirmed_at": datetime.datetime.utcnow(),
                     "roles": ["admin"]}, **kwargs)

    def __get_team_dict(self, **kwargs):

        return dict({"name": "Team %d" % self.get_counter(),
                     "description": "The best team evaarrrr!"}, **kwargs)

    def __get_role_dict(self, **kwargs):

        return dict({"name": "Role %d" % self.get_counter(),
                     "description": "The best role evaarrrr!"}, **kwargs)

if __name__ == '__main__':
    unittest.main()
