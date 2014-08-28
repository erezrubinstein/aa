from retail.v010.data_access.controllers.reset_password_request_controller import ResetPasswordRequestController
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.utilities.errors import *
import unittest
import datetime
import uuid
import mox


__author__ = 'vgold'


class ResetPasswordRequestControllerTests(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(ResetPasswordRequestControllerTests, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # Set mock attributes on WorkflowService instance for calls to ignore
        self.cfg = Dependency("MoxConfig").value
        self.logger = Dependency("FlaskLogger").value

        # Create caller context
        self.context = {"user_id": 1, "source": "test_store_helper.py"}

        # Set up useful mocks
        self.mock = self.mox.CreateMock(ResetPasswordRequestController)
        self.mock.User = self.mox.CreateMockAnything()
        self.mock.ResetPasswordRequest = self.mox.CreateMockAnything()

    def doCleanups(self):

        super(ResetPasswordRequestControllerTests, self).doCleanups()
        dependencies.clear()

    ###########################################
    # ResetPasswordRequestController.create_reset_password_request()

    def test_create_reset_password_request__missing_email(self):

        user_data = {
            "asdf": "user_email"
        }

        self.mox.ReplayAll()
        with self.assertRaises(BadRequestError):
            ResetPasswordRequestController.create_reset_password_request(self.mock, None, user_data)

    def test_create_reset_password_request__no_user(self):

        user_data = {
            "email": "user_email"
        }

        self.mock.User.get(user_data["email"]).AndReturn(None)

        self.mox.ReplayAll()
        with self.assertRaises(NotFoundError):
            ResetPasswordRequestController.create_reset_password_request(self.mock, None, user_data)

    def test_create_reset_password_request(self):

        user_data = {
            "email": "user_email"
        }

        user = self.mox.CreateMockAnything()
        user.email = "user_email"
        user.active = True

        self.mock.User.get(user_data["email"]).AndReturn(user)

        rpr1 = self.mox.CreateMockAnything()
        rpr1.status = "closed"

        rpr2 = self.mox.CreateMockAnything()
        rpr2.status = "open"

        self.mock.ResetPasswordRequest.find_all(user=user).AndReturn([rpr1, rpr2])
        rpr2.update(status="closed")

        self.mox.StubOutWithMock(uuid, 'uuid4')

        code = "code"
        uuid.uuid4().AndReturn(code)

        hash_string = "hash_string"
        self.mock.User.hash_string(code).AndReturn(hash_string)

        self.mock.ResetPasswordRequest.find(hash=hash_string).AndReturn(None)

        rpr = "rpr"
        self.mock.ResetPasswordRequest.create(serialize=True, user=user, hash=hash_string, status="open").AndReturn(rpr)

        self.mox.ReplayAll()

        results = ResetPasswordRequestController.create_reset_password_request(self.mock, None, user_data)
        self.assertEqual(results, (rpr, code))

    def test_create_reset_password_request__inactive_user(self):

        user_data = {
            "email": "user_email"
        }

        user = self.mox.CreateMockAnything()
        user.active = False

        self.mock.User.get(user_data["email"]).AndReturn(user)

        self.mox.ReplayAll()

        with self.assertRaises(UnauthorizedError):
            ResetPasswordRequestController.create_reset_password_request(self.mock, None, user_data)

    ###########################################
    # ResetPasswordRequestController.update_reset_password_request()

    def test_update_reset_password_request__missing_rpr(self):

        rpr_id = "rpr_id"
        update_dict = None

        self.mock.ResetPasswordRequest.get(rpr_id).AndReturn(None)

        self.mox.ReplayAll()

        with self.assertRaises(NotFoundError):
            ResetPasswordRequestController.update_reset_password_request(self.mock, rpr_id, update_dict)

    def test_update_reset_password_request__invalid_status(self):

        rpr_id = "rpr_id"
        update_dict = {
            "status": "open"
        }

        self.mock.ResetPasswordRequest.get(rpr_id).AndReturn(True)

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            ResetPasswordRequestController.update_reset_password_request(self.mock, rpr_id, update_dict)

    def test_update_reset_password_request(self):

        rpr_id = "rpr_id"
        update_dict = {
            "status": "closed"
        }

        rpr = self.mox.CreateMockAnything()
        self.mock.ResetPasswordRequest.get(rpr_id).AndReturn(rpr)

        self.mox.StubOutWithMock(datetime, 'datetime')
        datetime.datetime.utcnow().AndReturn("datetime")

        rpr.update(status=update_dict["status"], last_modified_at="datetime").AndReturn(rpr)
        self.mock.ResetPasswordRequest.get(rpr_id, serialize=True).AndReturn("success")

        self.mox.ReplayAll()

        result = ResetPasswordRequestController.update_reset_password_request(self.mock, rpr_id, update_dict)
        self.assertEqual(result, "success")

    ######################################################################################
    # ResetPasswordRequestController.finalize_reset_password_request()

    def test_finalize_reset_password_request__missing_code(self):

        rpr_id = "rpr_id"
        update_dict = None

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            ResetPasswordRequestController.finalize_reset_password_request(self.mock, rpr_id, update_dict)

    def test_finalize_reset_password_request__missing_passwords(self):

        rpr_id = "rpr_id"
        code = "code"
        update_dict = {
            "code": code
        }

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, "datetime")

        rpr = self.mox.CreateMockAnything()
        self.mock._get_and_validate_rpr(rpr_id, code).AndReturn(rpr)

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            ResetPasswordRequestController.finalize_reset_password_request(self.mock, rpr_id, update_dict)

    def test_finalize_reset_password_request__empty_passwords(self):

        rpr_id = "rpr_id"
        code = "code"
        pw = ""
        update_dict = {
            "code": code,
            "password": pw
        }

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, "datetime")

        rpr = self.mox.CreateMockAnything()
        self.mock._get_and_validate_rpr(rpr_id, code).AndReturn(rpr)

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            ResetPasswordRequestController.finalize_reset_password_request(self.mock, rpr_id, update_dict)

    def test_finalize_reset_password_request__fail_password_validation(self):

        rpr_id = "rpr_id"
        code = "code"
        pw = "asdf"
        update_dict = {
            "code": code,
            "password": pw
        }

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, "datetime")

        rpr = self.mox.CreateMockAnything()
        self.mock._get_and_validate_rpr(rpr_id, code).AndReturn(rpr)

        # fail the validate password and raise an error!
        self.mock.User.validate_password("asdf").AndReturn("ERROR!")

        self.mox.ReplayAll()

        with self.assertRaises(UserWarningError) as ex:
            ResetPasswordRequestController.finalize_reset_password_request(self.mock, rpr_id, update_dict)

        # make sure error message is correct
        self.assertEqual(ex.exception.data, "ERROR!")

    def test_finalize_reset_password_request(self):

        rpr_id = "rpr_id"
        code = "code"
        pw = "asdfasdfasdf"
        update_dict = {
            "code": code,
            "password": pw
        }

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, "datetime")

        rpr = self.mox.CreateMockAnything()
        self.mock._get_and_validate_rpr(rpr_id, code).AndReturn(rpr)

        # verify password
        self.mock.User.validate_password(pw).AndReturn("")

        datetime.datetime.utcnow().AndReturn(now)

        rpr.user = self.mox.CreateMockAnything()
        rpr.user.id = "user_id"
        clean_dict = {
            "password": pw,
            "active": True,
            "first_login_date": now
        }
        rpr.user.update(**clean_dict)

        datetime.datetime.utcnow().AndReturn(now)
        rpr.update(status="closed", last_modified_at=now)
        self.mock.ResetPasswordRequest.get(rpr_id, serialize=True).AndReturn("success")

        self.mox.ReplayAll()

        results = ResetPasswordRequestController.finalize_reset_password_request(self.mock, rpr_id, update_dict)
        self.assertEqual(results, "success")

    ######################################################################################
    # ResetPasswordRequestController._get_and_validate_rpr()

    def test_get_and_validate_rpr(self):

        rpr_id = "rpr_id"
        code = "code"

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, "datetime")

        rpr = self.mox.CreateMockAnything()
        rpr.status = "open"
        self.mock.ResetPasswordRequest.get(rpr_id).AndReturn(rpr)

        rpr.created_at = now - datetime.timedelta(3)
        datetime.datetime.utcnow().AndReturn(now)

        rpr.hash = "hash"
        self.mock.User.verify_hash(code, rpr.hash).AndReturn(True)

        self.mox.ReplayAll()

        results = ResetPasswordRequestController._get_and_validate_rpr(self.mock, rpr_id, code)
        self.assertEqual(results, rpr)

    def test_get_and_validate_rpr__missing_rpr(self):

        rpr_id = "rpr_id"
        code = "code"

        self.mock.ResetPasswordRequest.get(rpr_id).AndReturn(None)

        self.mox.ReplayAll()

        with self.assertRaises(NotFoundError):
            ResetPasswordRequestController._get_and_validate_rpr(self.mock, rpr_id, code)

    def test_get_and_validate_rpr__invalid_rpr_status(self):

        rpr_id = "rpr_id"
        code = "code"

        rpr = self.mox.CreateMockAnything()
        rpr.status = "closed"
        self.mock.ResetPasswordRequest.get(rpr_id).AndReturn(rpr)

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            ResetPasswordRequestController._get_and_validate_rpr(self.mock, rpr_id, code)

    def test_get_and_validate_rpr__invalid_rpr_creation_time(self):

        rpr_id = "rpr_id"
        code = "code"

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, "datetime")

        rpr = self.mox.CreateMockAnything()
        rpr.status = "open"
        rpr.created_at = now - datetime.timedelta(20)

        self.mock.ResetPasswordRequest.get(rpr_id).AndReturn(rpr)

        datetime.datetime.utcnow().AndReturn(now)
        datetime.datetime.utcnow().AndReturn(now)

        rpr.update(status="closed", last_modified_at=now)

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            ResetPasswordRequestController._get_and_validate_rpr(self.mock, rpr_id, code)

    def test_get_and_validate_rpr__invalid_hash(self):

        rpr_id = "rpr_id"
        code = "code"

        now = datetime.datetime.utcnow()
        self.mox.StubOutWithMock(datetime, "datetime")

        rpr = self.mox.CreateMockAnything()
        rpr.status = "open"
        self.mock.ResetPasswordRequest.get(rpr_id).AndReturn(rpr)

        rpr.created_at = now - datetime.timedelta(3)
        datetime.datetime.utcnow().AndReturn(now)

        rpr.hash = "hash"
        self.mock.User.verify_hash(code, rpr.hash).AndReturn(False)

        self.mox.ReplayAll()

        with self.assertRaises(BadRequestError):
            ResetPasswordRequestController._get_and_validate_rpr(self.mock, rpr_id, code)

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