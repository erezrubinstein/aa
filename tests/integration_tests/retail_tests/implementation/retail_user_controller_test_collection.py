from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from retail.v010.data_access.controllers.client_controller import ClientController
from retail.v010.data_access.controllers.user_controller import VALID_RETAIL_ROLES, UserController
from retail.v010.data_access.retail_data_helper import RetailDataHelper


class RetailUserControllerTestCollection(ServiceTestCollection):

    # Random number to avoid interfering with other test collections in the same suite
    test_user_start = 2345
    test_client_start = 2345

    test_user_counter = 0
    test_client_counter = 0

    def initialize(self):
        self.user_controller = UserController()
        self.client_controller = ClientController()
        self.retail_data_helper = RetailDataHelper(self.config, self.user_controller)
        self.retail_data_helper.add_default_data()

    def setUp(self):
        self.__get_default_users()

    def tearDown(self):
        pass

    @classmethod
    def increment_test_user_counter(cls):
        cls.test_user_counter += 1

    @classmethod
    def increment_test_client_counter(cls):
        cls.test_client_counter += 1

    ##------------------------------------ Tests --------------------------------------##

    def test_create_user(self):

        client = self.__create_test_client()
        ali_g = self.__create_test_user(client_name=client["name"])

        correct_user_subdict = {
            'confirmed_at': None,
            'login_count': 0,
            'phone': None,
            'last_login_at': None,
            'active': True,
            'retail_access': True,
            'retailer_access': False,
            'current_login_ip': None,
            'assistant_name': None,
            'roles': [self.role_user],
            'client_name': client["name"],
            'last_login_ip': None,
            'assistant_phone': None,
            'current_login_at': None
        }
        self.test_case.assertDictContainsSubset(correct_user_subdict, ali_g)

        # make sure ali g was added to the user list in Nexus Research Intelligence
        client = self.user_controller.Client.get(client["name"], serialize=True)
        correct_client_user_email_list = [ali_g["email"]]
        self.test_case.assertListEqual(client['user_emails'], correct_client_user_email_list)

    def test_get_user(self):
        user = self.user_controller.User.get(self.user_admin['email'])
        self.test_case.assertDictContainsSubset(self.user_admin, user.serialize())

    def test_get_user__case_insensitive(self):
        user = self.user_controller.User.get(self.user_admin['email'].upper())
        self.test_case.assertDictContainsSubset(self.user_admin, user.serialize())

    def test_find_user(self):
        user = self.user_controller.User.find(email=self.user_admin['email'], serialize=True)
        self.test_case.assertDictContainsSubset(self.user_admin, user)

    def test_find_user__case_insensitive(self):
        user = self.user_controller.User.find(email=self.user_admin['email'].upper(), serialize=True)
        self.test_case.assertDictContainsSubset(self.user_admin, user)

    def test_find_users(self):
        users = self.user_controller.User.find_all(active=True)
        # only need to test the number of users returned here, we expect 4
        self.test_case.assertTrue(len(users) >= 4)

    def test_update_user(self):
        client = self.__create_test_client()
        ali_g = self.__create_test_user(client_name=client["name"])

        # send in a different name and email, these fields can only be changed by an administrator
        update_dict = {
            'name': 'Buzz Aldren',
            'email': 'baldren@nexusri.com',
            'assistant_name': 'Borat',
            'assistant_phone': '555-555-5555',
            'roles': ['user', 'client_support'],
            'password': "How come I can't remember me pin numbah"
        }

        self.user_controller.update_user(self.user_admin['email'], ali_g['email'], update_dict)

        ali_g_updated = self.user_controller.User.get(update_dict['email'])

        correct_user_subdict = {
            'name': 'Buzz Aldren',
            'email': 'baldren@nexusri.com',
            'assistant_name': 'Borat',
            'assistant_phone': '555-555-5555',
            'roles': [self.role_user, self.role_client_support],
            'confirmed_at': None,
            'login_count': 0,
            'phone': None,
            'last_login_at': None,
            'active': True,
            'current_login_ip': None,
            'last_login_ip': None,
            'current_login_at': None
        }

        self.test_case.assertDictContainsSubset(correct_user_subdict, ali_g_updated.serialize())

    def test_delete_user(self):

        client = self.__create_test_client()
        ali_g = self.__create_test_user(client_name=client["name"])

        # make sure ali g was added to the user list in Nexus Research Intelligence
        client = self.user_controller.Client.get(client["name"], serialize=True)
        self.test_case.assertEqual(len(client['user_emails']), 1)
        self.test_case.assertIn(ali_g['email'], client['user_emails'])

        # delete ali g
        self.user_controller.delete_user(self.user_admin['email'], ali_g['email'])

        ali_g_new = self.user_controller.User.get(ali_g['email'], serialize=True)
        self.test_case.assertIsNone(ali_g_new)

        # make sure ali g was removed from the user list in client
        client = self.user_controller.Client.get(client["name"], serialize=True)

        self.test_case.assertEqual(len(client['user_emails']), 0)
        self.test_case.assertNotIn(ali_g['email'], client['user_emails'])

    def test_create_role(self):
        # temporarily add josh to the list of valid retail roles
        VALID_RETAIL_ROLES.append('josh')
        role_dict = {
            'name': 'josh',
            'description': 'benevolent dictator'
        }
        role = self.user_controller.Role.create(**role_dict)
        self.test_case.assertDictContainsSubset(role_dict, role.serialize())

        # revert valid retail roles
        VALID_RETAIL_ROLES.remove('josh')
        role.delete()

    def test_get_role(self):

        role = self.user_controller.Role.get(self.role_user['name'])
        self.test_case.assertDictContainsSubset(self.role_user, role.serialize())

    def test_find_role(self):

        role = self.user_controller.Role.find(name=self.role_user['name'])
        self.test_case.assertDictContainsSubset(self.role_user, role.serialize())

    def test_find_roles(self):

        roles = self.user_controller.Role.find_all(description='ruh roh!!!')
        self.test_case.assertEqual(len(roles), 0)

        # temporarily add ruh and roh to the list of valid retail roles
        VALID_RETAIL_ROLES.append('ruh')
        VALID_RETAIL_ROLES.append('roh')

        ruh_role_dict = {
            'name': 'ruh',
            'description': 'ruh roh!!!'
        }
        roh_role_dict = {
            'name': 'roh',
            'description': 'ruh roh!!!'
        }
        ruh = self.user_controller.Role.create(**ruh_role_dict)
        roh = self.user_controller.Role.create(**roh_role_dict)
        roles = self.user_controller.Role.find_all(description='ruh roh!!!')
        # only need to test that we got 2 roles back
        self.test_case.assertEqual(len(roles), 2)

        # revert valid retail roles
        VALID_RETAIL_ROLES.remove('ruh')
        VALID_RETAIL_ROLES.remove('roh')
        ruh.delete()
        roh.delete()

    def test_update_role(self):
        # temporarily add josh to the list of valid retail roles
        VALID_RETAIL_ROLES.append('josh')
        role_dict = {
            'name': 'josh',
            'description': 'benevolent dictator'
        }
        role = self.user_controller.Role.create(**role_dict)
        self.test_case.assertDictContainsSubset(role_dict, role.serialize())
        new_description = 'actually nevermind, i shall rule with an iron fist'
        role.update(description=new_description)

        role = self.user_controller.Role.get('josh')
        self.test_case.assertEqual(role.description, new_description)

        # revert valid retail roles
        VALID_RETAIL_ROLES.remove('josh')
        role.delete()

    def test_delete_role(self):

        # temporarily add josh to the list of valid retail roles
        VALID_RETAIL_ROLES.append('josh')
        role_dict = {
            'name': 'josh',
            'description': 'benevolent dictator'
        }
        role = self.user_controller.Role.create(**role_dict)
        self.test_case.assertDictContainsSubset(role_dict, role.serialize())

        # delete josh's role :(
        role.delete()

        # try to get the role again
        role = self.user_controller.Role.get('josh')
        self.test_case.assertIsNone(role)

        # revert valid retail roles
        VALID_RETAIL_ROLES.remove('josh')

    ##------------------------------------ Private helpers --------------------------------------##

    def __get_default_users(self):
        self.user_admin = self.user_controller.User.get("admin@nexusri.com", serialize=True)
        self.client_signal = self.user_controller.Client.get("Signal Data", serialize=True)
        self.role_user = self.user_controller.Role.get('user', serialize=True)
        self.role_client_support = self.user_controller.Role.get('client_support', serialize=True)

    def __create_test_user(self, client_name, actor_email='test@nexusri.com', serialize=True):
        password = 'yoyoyoyo%s' % (self.test_user_counter + self.test_user_start)

        user_dict = {
            'name': "test_user_%s" % (self.test_user_counter + self.test_user_start),
            'email': "test_email_%s@nexusri.com" % (self.test_user_counter + self.test_user_start),
            'password': password,
            'active': True,
            'client': client_name,
            'retail_access': True,
            'retailer_access': False,
            'roles': ['user']
        }

        user = self.user_controller.create_user(actor_email, user_dict, serialize=False)
        user.update(active=True, password=user_dict["password"])
        updated_user = self.user_controller.User.get(user.email, serialize=False)
        self.increment_test_user_counter()

        # Return unhashed password separately, because it's not returned in user object
        return updated_user.serialize() if updated_user and serialize else updated_user

    def __create_test_client(self, actor_email='test@nexusri.com', serialize=True):
        client_dict = {
            'name': 'test_client_%s' % (self.test_client_counter + self.test_client_start),
            'description': 'company set out to take over the world',
            'contact_name': 'Thomas Aquinas',
            'contact_email': 'taquinas@nexusri.com',
            'contact_phone': '555-123-1234'
        }

        client = self.client_controller.create_client(actor_email, client_dict, serialize=serialize)
        self.increment_test_client_counter()
        return client
