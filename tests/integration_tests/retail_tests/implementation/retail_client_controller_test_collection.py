from __future__ import division
from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from retail.v010.data_access.controllers.client_controller import ClientController
from retail.v010.data_access.controllers.user_controller import UserController
from retail.v010.data_access.retail_data_helper import RetailDataHelper


class RetailClientControllerTestCollection(ServiceTestCollection):

    test_user_start = 456
    test_client_start = 456

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

    def test_create_client(self):

        client = self.__create_test_client()

        correct_dict = {
            'user_emails': [],
            'description': u'company set out to take over the world',
            'contact_email': u'taquinas@nexusri.com',
            'contact_name': u'Thomas Aquinas',
            'contact_phone': u'555-123-1234'
        }

        self.test_case.assertDictContainsSubset(correct_dict, client)

    def test_get_client(self):

        client = self.user_controller.Client.get('Signal Data')
        self.test_case.assertDictContainsSubset(self.client_signal, client.serialize())

    def test_find_client(self):

        client = self.user_controller.Client.find(name='Signal Data')
        self.test_case.assertDictContainsSubset(self.client_signal, client.serialize())

    def test_find_clients(self):

        client = self.__create_test_client()
        clients = self.user_controller.Client.find_all(name=client["name"])
        self.test_case.assertEqual(len(clients), 1)

    def test_update_client(self):

        client = self.__create_test_client(serialize=False)
        update_dict = {
            'name': 'Arnold Schwarzenegger',
            'description': "Oh, you think you're bad, huh? You're a ******* choir boy compared to me! A CHOIR BOY!",
            'contact_name': 'Jericho Cane',
            'contact_email': 'jcane@nexusri.com',
            'contact_phone': '555-9922342342342343242313'
        }
        self.client_controller.update_client('test@nexusri.com', client["name"], update_dict)
        updated_client = self.client_controller.Client.get(update_dict['name'])

        self.test_case.assertDictContainsSubset(update_dict, updated_client.serialize())

    def test_delete_client(self):

        # create blue shift client
        client = self.__create_test_client()

        # create user to add to client so we can test that deleting a client doesn't delete the users in its list
        ali_g = self.__create_test_user(client_name=client["name"])

        # delete client, make sure the user for ali g still exists
        self.client_controller.delete_client(self.user_admin['email'], client["name"])

        client = self.client_controller.Client.get(client["name"])
        self.test_case.assertIsNone(client)

        ali_g = self.client_controller.User.get(ali_g["email"])
        self.test_case.assertIsNone(ali_g)

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
