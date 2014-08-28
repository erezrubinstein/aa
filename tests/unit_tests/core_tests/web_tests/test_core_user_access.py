import pprint
import unittest
import uuid
import datetime
import base64
import os
from mox import Mox, IsA, MoxTestBase, MockAnything
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.helpers.core_dependencies import register_core_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency

from flask_security import utils
from core.common.utilities.errors import NotFoundError

__author__ = 'vgold'


class TestCoreUserAccess(MoxTestBase):

    counter = 0

    @classmethod
    def setUpClass(cls):
        cls.counter = 0

    @classmethod
    def get_counter(cls):
        counter = cls.counter
        cls.counter += 1
        return counter

    def setUp(self):
        # call super
        super(TestCoreUserAccess, self).setUp()

        # register mox and common core dependencies
        register_core_mock_dependencies()
        register_common_mox_dependencies(self.mox)

        # get some needed things
        self.user_access = Dependency("CoreUserProvider").value

        role_dict = self.__get_role_dict()
        role_dict["name"] = "admin"
        self.user_access.create_role(role_dict)

    def tearDown(self):

        self.user_access = None
        dependencies.clear()
    
    def test_user_basic_crud(self):

        # create stub
        m = Mox()
        m.StubOutWithMock(utils, "encrypt_password")
        m.StubOutWithMock(utils, "verify_password")
        m.StubOutWithMock(base64, "b64encode")
        m.StubOutWithMock(os, "urandom")

        # start recording
        utils.encrypt_password("test")
        utils.verify_password("test", None).AndReturn(True)
        utils.verify_password("asdfasdf", None).AndReturn(False)
        # mock the urandom return for the salt, and make sure that gets base-64 encoded into something different
        os.urandom(128).AndReturn("she sells sea shells by the sea shore")
        base64.b64encode("she sells sea shells by the sea shore").AndReturn("Salt-n-Pepa")
        m.ReplayAll()

        user_dict = self.__get_user_dict()
        user = self.user_access.create_user(user_dict)

        self.assertIn("id", user)
        self.assertEqual(user_dict["email"], user["email"])
        self.assertEqual(user_dict["is_generalist"], user["is_generalist"])
        self.assertEqual(user_dict["active"], user["active"])
        self.assertEqual(len(user["roles"]), 1)

        self.assertTrue(self.user_access.verify_user_password(user["id"], user_dict["password"]))
        self.assertFalse(self.user_access.verify_user_password(user["id"], "asdfasdf"))

        self.assertEqual("Salt-n-Pepa", user["salt"])

        user2 = self.user_access.update_user(user["id"], {"email": "test2@test.com"})

        self.assertEqual(user2["email"], "test2@test.com")
        self.assertEqual(user2["id"], user["id"])

        user3 = self.user_access.get_user(user2["id"])

        self.assertEqual(user2, user3)

        result = self.user_access.delete_user(user3["id"])
        self.assertEqual(result, True)

        no_user = self.user_access.get_user(user2["id"])
        self.assertEqual(no_user, None)

    def test_user_update_password(self):

        # create stub
        m = Mox()
        m.StubOutWithMock(utils, "encrypt_password")
        m.StubOutWithMock(utils, "verify_password")
        m.StubOutWithMock(base64, "b64encode")
        m.StubOutWithMock(os, "urandom")

        # start recording
        utils.encrypt_password("test")
        utils.verify_password("test", None).AndReturn(True)
        utils.verify_password("asdfasdf", None).AndReturn(False)
        # mock the urandom return for the salt, and make sure that gets base-64 encoded into something different
        os.urandom(128).AndReturn("she sells sea shells by the sea shore")
        base64.b64encode("she sells sea shells by the sea shore").AndReturn("Salt-n-Pepa")

        #go into replay mode
        m.ReplayAll()

        user_dict = self.__get_user_dict()
        user = self.user_access.create_user(user_dict)

        # reset mocks & stubs
        m.ResetAll()
        m.UnsetStubs()

        m.StubOutWithMock(utils, "encrypt_password")
        m.StubOutWithMock(utils, "verify_password")
        m.StubOutWithMock(base64, "b64encode")
        m.StubOutWithMock(os, "urandom")

        utils.encrypt_password("yoda").AndReturn("the force")
        utils.verify_password("yoda", None).AndReturn(True)
        # mock the urandom return for the salt, and make sure that gets base-64 encoded into something different
        os.urandom(128).AndReturn("obi-wan")
        base64.b64encode("obi-wan").AndReturn("darth vader")

        m.ReplayAll()

        updated_user = self.user_access.update_user(user["id"], {"password": "yoda"})

        # we should have "encrypted" the password "yoda" to "the force", and added a new salt
        self.assertEqual(updated_user["password"], "the force")
        self.assertEqual(updated_user["salt"], "darth vader")

    def test_team_basic_crud(self):

        team_dict = self.__get_team_dict()
        team = self.user_access.create_team(team_dict)

        self.assertIn("id", team)
        self.assertEqual(team_dict["name"], team["name"])
        self.assertEqual(team_dict["description"], team["description"])
        self.assertEqual(team_dict["is_generalist"], team["is_generalist"])

        team2 = self.user_access.update_team(team["id"], {"name": "asdfasdf"})

        self.assertEqual(team2["name"], "asdfasdf")
        self.assertEqual(team2["id"], team["id"])

        team3 = self.user_access.get_team(team2["id"])

        self.assertEqual(team2, team3)

        result = self.user_access.delete_team(team3["id"])
        self.assertEqual(result, True)

        no_team = self.user_access.get_team(team2["id"])
        self.assertEqual(no_team, None)

    def test_team_create_with_users_and_industries(self):

        # create stub
        m = Mox()
        m.StubOutWithMock(utils, "encrypt_password")
        m.StubOutWithMock(base64, "b64encode")

        # start recording
        # can't seem to stub os.urandom here... returns None sometimes?
        base64.b64encode(IsA(str)).AndReturn("Larry")
        utils.encrypt_password("test")
        base64.b64encode(IsA(str)).AndReturn("Moe")
        utils.encrypt_password("test")
        base64.b64encode(IsA(str)).AndReturn("Curly")
        utils.encrypt_password("test")

        m.ReplayAll()

        user1 = self.user_access.create_user(self.__get_user_dict())
        user2 = self.user_access.create_user(self.__get_user_dict())
        user3 = self.user_access.create_user(self.__get_user_dict())

        team_dict = self.__get_team_dict()
        team_dict["user_ids"] = [user1["id"], user2["id"], user3["id"]]
        team_dict["industry_ids"] = ["asdf1", "asdf2", "asdf3"]

        team = self.user_access.create_team(team_dict)

        user_teams = self.user_access.find_user_teams({"team_id": team["id"]})
        self.assertEqual(len(user_teams), 3)
        for user_team in user_teams:
            self.assertTrue(user_team["user_id"] in team_dict["user_ids"])

        team_industries = self.user_access.find_team_industries({"team_id": team["id"]})
        self.assertEqual(len(team_industries), 3)
        for team_industry in team_industries:
            self.assertTrue(team_industry["industry_id"] in team_dict["industry_ids"])

    def test_role_basic_crud(self):

        role_dict = self.__get_role_dict()
        role = self.user_access.create_role(role_dict)

        self.assertIn("id", role)
        self.assertEqual(role_dict["name"], role["name"])
        self.assertEqual(role_dict["description"], role["description"])

        role2 = self.user_access.update_role(role["id"], {"name": "asdfasdf"})

        self.assertEqual(role2["name"], "asdfasdf")
        self.assertEqual(role2["id"], role["id"])

        role3 = self.user_access.get_role(role2["id"])

        self.assertEqual(role2, role3)

        result = self.user_access.delete_role(role3["id"])
        self.assertEqual(result, True)

        no_role = self.user_access.get_role(role2["id"])
        self.assertEqual(no_role, None)

    def test_user_teams(self):

        # create stub
        m = Mox()
        m.StubOutWithMock(utils, "encrypt_password")
        m.StubOutWithMock(utils, "verify_password")
        m.StubOutWithMock(base64, "b64encode")
        m.StubOutWithMock(os, "urandom")

        # start recording
        utils.encrypt_password("test")
        utils.verify_password("test", None).AndReturn(True)
        utils.verify_password("asdfasdf", None).AndReturn(False)
        # mock the urandom return for the salt, and make sure that gets base-64 encoded into something different
        os.urandom(128).AndReturn("she sells sea shells by the sea shore")
        base64.b64encode("she sells sea shells by the sea shore").AndReturn("Salt-n-Pepa")
        m.ReplayAll()

        # Create user and teams
        user1 = self.user_access.create_user(self.__get_user_dict())
        team1 = self.user_access.create_team(self.__get_team_dict())
        team2 = self.user_access.create_team(self.__get_team_dict())

        # Add user to teams
        team_ids = [team1["id"], team2["id"]]
        self.user_access.update_user(user1["id"], {"team_ids": team_ids})
        user_teams = self.user_access.find_user_teams({"user_id": user1["id"]})
        team_id_list = [user_team["team_id"] for user_team in user_teams]
        self.assertEqual(team_id_list, team_ids)

        # Making team generalist should make all members generalists
        self.assertEqual(self.user_access.get_user(user1["id"])["is_generalist"], False)
        self.assertEqual(self.user_access.get_team(team1["id"])["is_generalist"], False)
        self.user_access.update_team(team1["id"], {"is_generalist": True})
        self.assertEqual(self.user_access.get_user(user1["id"])["is_generalist"], True)
        self.assertEqual(self.user_access.get_team(team1["id"])["is_generalist"], True)

        # Making team not generalist should not affect members in another generalist team
        self.user_access.update_team(team2["id"], {"is_generalist": True})
        self.user_access.update_team(team1["id"], {"is_generalist": False})
        self.assertEqual(self.user_access.get_user(user1["id"])["is_generalist"], True)
        self.assertEqual(self.user_access.get_team(team1["id"])["is_generalist"], False)
        self.assertEqual(self.user_access.get_team(team2["id"])["is_generalist"], True)

        # Making team not generalist should update all affected users
        self.user_access.update_team(team2["id"], {"is_generalist": False})
        self.assertEqual(self.user_access.get_user(user1["id"])["is_generalist"], False)
        self.assertEqual(self.user_access.get_team(team2["id"])["is_generalist"], False)

    def test_team_industries(self):

        # create stub
        m = Mox()
        m.StubOutWithMock(utils, "encrypt_password")
        m.StubOutWithMock(utils, "verify_password")
        m.StubOutWithMock(base64, "b64encode")
        m.StubOutWithMock(os, "urandom")

        # start recording
        utils.encrypt_password("test")
        utils.verify_password("test", None).AndReturn(True)
        utils.verify_password("asdfasdf", None).AndReturn(False)
        # mock the urandom return for the salt, and make sure that gets base-64 encoded into something different
        os.urandom(128).AndReturn("she sells sea shells by the sea shore")
        base64.b64encode("she sells sea shells by the sea shore").AndReturn("Salt-n-Pepa")
        m.ReplayAll()

        # Create user and teams
        user1 = self.user_access.create_user(self.__get_user_dict())
        team1 = self.user_access.create_team(self.__get_team_dict())
        team2 = self.user_access.create_team(self.__get_team_dict())

        industry_id1 = self.__get_industry_id()
        industry_id2 = self.__get_industry_id()

        # Add user to teams
        team_ids = [team1["id"], team2["id"]]
        self.user_access.update_user(user1["id"], {"team_ids": team_ids})

        industry_ids = [industry_id1, industry_id2]
        self.user_access.update_team(team1["id"], {"industry_ids": industry_ids})

        team_industries = self.user_access.find_team_industries({"team_id": team1["id"]})
        industry_id_list = [team_industry["industry_id"] for team_industry in team_industries]
        self.assertEqual(industry_id_list, industry_ids)

        user_industry_list = self.user_access.get_user_industries(user1["id"])
        self.assertEqual(user_industry_list, industry_ids)


    def test_create_team__new_team__with_industries(self):
        """
        Tests that the create team works as expected.
        Added as a test for RET-1102
        """
        # create various mock items
        mock_team = {
            "id": "chicken_woot",
            "name": "woot",
            "description": "chicken",
            "is_generalist": False,
            "user_ids": ["yoyoma"],
            "industry_ids": ["danger_zone"]
        }

        # stub several functions
        self.mox.StubOutWithMock(self.user_access, "find_team")
        self.user_access.datastore = self.mox.CreateMockAnything()
        self.mox.StubOutWithMock(self.user_access, "_update_team_users")
        self.mox.StubOutWithMock(self.user_access, "_update_team_industries")

        # record
        self.user_access.find_team({ "name": "woot" })
        self.user_access.datastore.create_team(name = "woot", description = "chicken", is_generalist = False).AndReturn(mock_team)
        self.user_access._update_team_users("chicken_woot", ["yoyoma"])
        self.user_access._update_team_industries("chicken_woot", ["danger_zone"])

        # replay
        self.mox.ReplayAll()

        # bomboj for
        team = self.user_access.create_team(mock_team)

        # make sure team is correct
        self.assertEquals(team, mock_team)


    def test_create_team__new_team__none_unique_name(self):
        """
        Tests that the create team works as expected.
        Added as a test for RET-1102
        """
        # create various mock items
        mock_team = {
            "id": "chicken_woot",
            "name": "woot",
            "description": "chicken",
            "is_generalist": False,
            "user_ids": ["yoyoma"],
            "industry_ids": ["danger_zone"]
        }

        # stub several functions
        self.mox.StubOutWithMock(self.user_access, "find_team")

        # record
        self.user_access.find_team({ "name": "woot" }).AndReturn(mock_team)

        # replay
        self.mox.ReplayAll()

        # bomboj for
        with self.assertRaises(NotFoundError) as error:
            self.user_access.create_team(mock_team)
        self.assertEqual(error.exception.message, "Team woot already exists.")


    #---------------------------------# Private Methods #---------------------------------#

    def __get_user_dict(self, **kwargs):

        return dict({"email": "test%d@test.com" % self.get_counter(),
                     "active": True,
                     "is_generalist": False,
                     "password": "test",
                     "confirmed_at": datetime.datetime.utcnow(),
                     "roles": ["admin"]}, **kwargs)

    def __get_team_dict(self, **kwargs):

        return dict({"name": "Team %d" % self.get_counter(),
                     "description": "The best team evaarrrr!",
                     "is_generalist": False}, **kwargs)

    def __get_role_dict(self, **kwargs):

        return dict({"name": "Role %d" % self.get_counter(),
                     "description": "The best role evaarrrr!"}, **kwargs)

    def __get_industry_id(self):

        return uuid.uuid4()

if __name__ == '__main__':
    unittest.main()