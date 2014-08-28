from __future__ import division
from common.service_access.web_access import CoreWebAccess
from tests.unit_tests.core_tests.mock_providers.mock_rest_provider import TestClientRestProvider
from common.service_access.entity_matcher_access import EntityMatcherAccess
from common.utilities.inversion_of_control import dependencies, Dependency
from core.service.run_core_services import start_celery
from multiprocessing import Process
from time import sleep
import unittest
import shutil
import time
import os


class ServiceTestCase(unittest.TestCase):
    """
    This class wraps unittest.TestCase to allow its children to share test collections between each other
    using classes that inherit from the ServiceTestCollection class.

    Attrs:
        *
        * Required to be set by inheriting class
        *
        apps:               Dictionary of API service flask applications
                                {
                                    service key: app class
                                }

        svc_key:            String identifier for the service from which to load config and logger
        test_colls:         Dictionary of service keys and classes from which to load tests
        mock_rest:          (NOT FULLY IMPLEMENTED) Boolean, whether to use mock rest provider or real one

        *
        * Set internally
        *
        tests:              Dictionary that will hold test collection instances
        logger:             Log manager to use in tests
        main_access:        MainAccess instance to communicate with Main service
        rds_access:         RDSAccess instance to communicate with Raw Data service
        mds_access:         MDSAccess instance to communicate with Main Data service
        wfs_access:         WFSAccess instance to communicate with Workflow service
        web_access:         WebAccess instance to communicate with the Core Web site
        entity_matcher_access:    ...
        analytics_access:         ...
    """
    apps = {}
    svc_key = ""
    test_colls = {}
    mock_rest = False
    start_celery = False

    tests = {}
    logger = None
    main_access = None
    rds_access = None
    mds_access = None
    wfs_access = None
    web_access = None
    entity_matcher_access = None
    analytics_access = None
    child_processes = []
    environment = "INTEGRATION TESTING"
    start_servers = True
    web_servers = ["CORE_WEB", "RETAIL_WEB", "RETAILER_WEB"]

    @classmethod
    def setUpClass(cls):
        # Remove old logs
        cwd = os.getcwd()
        if os.path.exists("%s/log" % cwd):
            shutil.rmtree("%s/log" % cwd)

        # User must set up some initialization stuff
        cls.initialize_class()

        # Run all the stuffs
        cls.run_apps()
        cls.create_service_access_instances()
        cls.initialize_services()
        cls.initialize_tests()

    @classmethod
    def tearDownClass(cls):
        # terminate child processes
        for process in cls.child_processes:
            process.terminate()

        # Let user run one-time code after everything is done
        cls.finalize_class()

        # stop celery if we have initialized the workflow service
        if "WFS" in cls.apps and cls.start_celery:
            cls.apps["WFS"].stop_celery()

    def setUp(self):
        self.add_test_case_to_tests()
        self.call_test_collection_setUp()
        # self.wrap_tests_with_setup_and_teardown()

    def tearDown(self):
        self.call_test_collection_tearDown()

    ##----------------------## Methods to be overridden by developer ##--------------------------##

    @classmethod
    def initialize_class(cls):
        raise NotImplementedError("Base class implementation of initialize_class called")

    @classmethod
    def finalize_class(cls):
        pass

    ##------------------------------------------------##

    @classmethod
    def run_apps(cls):
        if cls.apps == {}:
            raise NotImplementedError("Base class implementation of initialize_class must set self.apps")

        # initialize applications so we can get their configs and loggers and whatnot
        for key, app in cls.apps.iteritems():
            if key in cls.web_servers:
                app.init_server(cls.environment)
            else:
                app.init_api("INTEGRATION TESTING")

        # Check for start_servers variable
        if "START_SERVERS" in cls.apps[cls.svc_key].config:
            cls.start_servers = cls.apps[cls.svc_key].config["START_SERVERS"]

        # re-initialize services with continuous integration config
        if not cls.start_servers:
            for key, app in cls.apps.iteritems():
                if key in cls.web_servers:
                    app.init_server(environment="CONTINUOUS INTEGRATION")
                else:
                    app.init_api("CONTINUOUS INTEGRATION")

        # run celery if we have initialized the workflow service
        if "WFS" in cls.apps and cls.start_celery:
            cls.apps["WFS"].init_celery_operator()
            cls.apps["WFS"].start_celery()
            start_celery("workflow_config_integration_test.py")

        if cls.svc_key == "":
            raise NotImplementedError("Base class implementation of initialize_class must set self.svc_key")

        cls.config = cls.apps[cls.svc_key].config
        cls.logger = cls.apps[cls.svc_key].logger

        dependencies.register_dependency("CoreConfig", cls.config)

        test_clients = {}
        if cls.mock_rest:
            for key, app in cls.apps.iteritems():
                test_client = app.test_client()
                port = app.config["PORT"]
                test_clients[port] = test_client

            test_client_rest = TestClientRestProvider(test_clients)
            dependencies.register_dependency("RestProvider", test_client_rest)

        cls.child_processes = []
        if cls.start_servers:
            for key, app in cls.apps.iteritems():
                # create new process and add to class list
                if key in cls.web_servers:
                    p = Process(group=None,
                                target=app.run_app,
                                args=(cls.environment,),
                                kwargs={"use_debugger": False,
                                        "use_reloader": False})  # don't need to init the servers again!
                else:
                    kwargs = {"use_debugger": False,
                              "use_reloader": False}

                    if cls.mock_rest:
                        kwargs["test_clients"] = test_clients

                    p = Process(group=None,
                                target=app.run_api,
                                args=(cls.environment,),
                                kwargs=kwargs)
                cls.child_processes.append(p)

                # mark as daemon and start
                # IMP! Do not join processes
                p.daemon = True
                p.start()
            # this is to give the services some time to fire up, sometimes we get the can't connect error
            sleep(5)
        return cls

    @classmethod
    def create_service_access_instances(cls):
        """
        Create service access instances.
        """
        cls.main_access = Dependency("CoreAPIProvider").value
        cls.wfs_access = cls.main_access.wfs
        cls.mds_access = cls.main_access.mds
        cls.rds_access = cls.main_access.rds
        cls.analytics_access = cls.main_access.analytics

        if "ENTITY_MATCHER" in cls.apps:
            cls.entity_matcher_access = EntityMatcherAccess(Dependency("ServiceAccess").value,
                                                            cls.apps["ENTITY_MATCHER"].config["ENTITY_MATCHER_API_URL"])

        # this isn't really a service access instance, but rather a simple wrapper on RestProvider
        web_url = None
        if "CORE_WEB" in cls.apps:
            web_url = cls.apps["CORE_WEB"].config["CORE_SITE_URL"]
        elif "RETAIL_WEB" in cls.apps:
            web_url = cls.apps["RETAIL_WEB"].config["RETAIL_WEB_URL"]
        elif "RETAILER_WEB" in cls.apps:
            web_url = cls.apps["RETAILER_WEB"].config["RETAILER_URL"]

        if web_url:
            cls.web_access = CoreWebAccess(web_url)

        return cls

    @classmethod
    def initialize_services(cls):
        """
        Reset databases for all applications.
        """
        for app_key in cls.apps:
            time.sleep(1)
            if hasattr(cls, "%s_access" % app_key.lower()):
                access_instance = getattr(cls, "%s_access" % app_key.lower())
                if hasattr(access_instance, 'call_delete_reset_database'):
                    access_instance.call_delete_reset_database()

                if hasattr(access_instance, 'call_reference_data_reload'):
                    access_instance.call_reference_data_reload()

        # For some crazy reason, retail web tests were failing with only 1 second sleep!!!
        time.sleep(2)
        return cls

    @classmethod
    def initialize_tests(cls):
        """
        Instantiate test collections and save to dictionary in instance attribute 'tests' with svc_key as dict key.
        Call initalize on each test collection instance.
        """
        if cls.test_colls == set({}):
            raise NotImplementedError("Base class implementation of initialize_apps must set self.tests")

        deps = {
            "config": cls.apps[cls.svc_key].config,
            "logger": cls.logger,
            "main_access": cls.main_access,
            "mds_access": cls.mds_access,
            "rds_access": cls.rds_access,
            "wfs_access": cls.wfs_access,
            "entity_matcher_access": cls.entity_matcher_access,
            "analytics_access": cls.analytics_access,
            "web_access": cls.web_access
        }

        for test_coll_key, test_coll in cls.test_colls.iteritems():
            cls.tests[test_coll_key] = test_coll(deps)
            cls.tests[test_coll_key].initialize()

        return cls

    def add_test_case_to_tests(self):
        """
        Add instance of this class to the test_case attribute of each instance of a test collection.
        """
        for svc_key, test_coll in self.tests.iteritems():
            test_coll.test_case = self

        return self

    def call_test_collection_setUp(self):
        for test_key in self.test_colls:
            test = self.tests[test_key]

            if hasattr(test, "setUp") and hasattr(test.setUp, '__call__'):
                test.setUp()

    # def wrap_tests_with_setup_and_teardown(self):
    #     for test_key in self.test_colls:
    #         test_coll = self.tests[test_key]
    #
    #         # Do NOT use iteritems, because we're changing the test collection in the loop
    #         for test_name, test in test_coll.__dict__.items():
    #             if test_name not in ["initialize", "setUp", "tearDown"] and not test_name.startswith("_") \
    #                     and hasattr(test, '__call__'):
    #
    #                 def new_test(*args, **kwargs):
    #                     if hasattr(test_coll, "setUp") and hasattr(test_coll.setUp, '__call__'):
    #                         test_coll.setUp()
    #                     result = test(*args, **kwargs)
    #                     if hasattr(test_coll, "tearDown") and hasattr(test_coll.tearDown, '__call__'):
    #                         test_coll.setUp()
    #                     return result
    #
    #                 test_coll.test_name = new_test

    def call_test_collection_tearDown(self):
        for test_key in self.test_colls:
            test = self.tests[test_key]

            if hasattr(test, "tearDown") and hasattr(test.tearDown, '__call__'):
                test.tearDown()

    ##--------------- Extend test case to provide to test collection instance -------------##

    def assertStatus(self, response, status_code):
        """
        Helper method to check matching response status.

        :param response: Flask response
        :param status_code: response status code (e.g. 200)
        """
        self.assertEqual(response.status_code, status_code)

    assert_status = assertStatus

    def assert200(self, response):
        """
        Checks if response status code is 200

        :param response: Flask response
        """

        self.assertStatus(response, 200)

    assert_200 = assert200

    def assert201(self, response):
        """
        Checks if response status code is 200

        :param response: Flask response
        """

        self.assertStatus(response, 201)

    assert_201 = assert201

    def assert400(self, response):
        """
        Checks if response status code is 400

        :versionadded: 0.2.5
        :param response: Flask response
        """

        self.assertStatus(response, 400)

    assert_400 = assert400


    def assert401(self, response):
        """
        Checks if response status code is 401

        :versionadded: 0.2.1
        :param response: Flask response
        """

        self.assertStatus(response, 401)

    assert_401 = assert401

    def assert403(self, response):
        """
        Checks if response status code is 403

        :versionadded: 0.2
        :param response: Flask response
        """

        self.assertStatus(response, 403)

    assert_403 = assert403

    def assert404(self, response):
        """
        Checks if response status code is 404

        :param response: Flask response
        """

        self.assertStatus(response, 404)

    assert_404 = assert404

    def assert405(self, response):
        """
        Checks if response status code is 405

        :versionadded: 0.2
        :param response: Flask response
        """

        self.assertStatus(response, 405)

    assert_405 = assert405

###################################################################################################
