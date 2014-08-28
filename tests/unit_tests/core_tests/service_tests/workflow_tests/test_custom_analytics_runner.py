import datetime
import json
from bson.objectid import ObjectId
from fabric import context_managers
import mox
from mox import IgnoreArg, Regex, IsA
import time
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import Dependency, dependencies
from common.web_helpers import logging_helper
from core.service.svc_workflow.implementation.task.implementation.custom_analytics.custom_analytics_runner import CustomAnalyticsRunner
from geoprocessing.build.db import build_db
from geoprocessing.custom_analytics import custom_analytics_loader


__author__ = "erezrubinstein"

class TestCustomAnalyticsRunner(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCustomAnalyticsRunner, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mox dependencies
        self.mock_retail_access = Dependency("RetailMongoAccess").value
        self.mock_logger = Dependency("FlaskLogger").value
        self.mock_cloud_provider = Dependency("CloudProvider").value
        self.mock_deployment_provider = Dependency("DeploymentProvider").value
        self.mock_service_config = Dependency("ServiceConfig").value

        # various needed data
        self.context = { "user": "chicken_woot" }
        self.task_id = ObjectId()
        self.custom_analytics_run_id = ObjectId()
        self.as_of_date = datetime.datetime(2013, 12, 1)
        self.task_rec = {
            "context": self.context,
            "custom_analytics_run_id": str(self.custom_analytics_run_id)
        }


    def doCleanups(self):

        # call parent clean up
        super(TestCustomAnalyticsRunner, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_successful_run(self):

        # create the runner
        runner = CustomAnalyticsRunner(self.task_rec)

        # begin stubbing things out
        self.mox.StubOutWithMock(runner, "_update_ca_run")
        self.mox.StubOutWithMock(runner, "_query_entity")
        self.mox.StubOutWithMock(runner, "_get_client_detail")
        self.mox.StubOutWithMock(runner, "_create_new_sql_db")
        self.mox.StubOutWithMock(runner, "_run_loader")
        self.mox.StubOutWithMock(runner, "_create_worker_server")
        self.mox.StubOutWithMock(runner, "_chmod_the_key")
        self.mox.StubOutWithMock(runner, "_deploy_code_to_worker")
        self.mox.StubOutWithMock(runner, "_replace_server_configs")
        self.mox.StubOutWithMock(runner, "_call_executor")

        # begin recording
        runner._update_ca_run()
        runner._query_entity().AndReturn("woot")
        runner._get_client_detail("woot").AndReturn(("test_client", "woot@woot.com"))
        runner._create_new_sql_db("woot").AndReturn(("chilly", "willy"))
        runner._update_ca_run(target_db_name = "chilly", logging_db_name = "willy")
        runner._run_loader("chilly", "woot").AndReturn("dates_sucka")
        runner._create_worker_server().AndReturn("sucka")
        runner._chmod_the_key()
        runner._deploy_code_to_worker("sucka")
        runner._replace_server_configs("sucka")
        runner._call_executor("woot", "sucka", "chilly", "willy", "test_client", "woot@woot.com", "dates_sucka")

        # replay all
        self.mox.ReplayAll()

        # run
        runner.run()


    def test_successful_run__multiple_heartbeats(self):

        # create the runner
        runner = CustomAnalyticsRunner(self.task_rec)

        # set the heart beat to be every .2 seconds
        runner._heart_beat_seconds = .2

        # create a side effect method to sleep for .3 seconds
        def sleep_side_effect(*args):
            time.sleep(.3)

        # begin stubbing things out
        self.mox.StubOutWithMock(runner, "_update_ca_run")
        self.mox.StubOutWithMock(runner, "_query_entity")
        self.mox.StubOutWithMock(runner, "_get_client_detail")
        self.mox.StubOutWithMock(runner, "_create_new_sql_db")
        self.mox.StubOutWithMock(runner, "_run_loader")
        self.mox.StubOutWithMock(runner, "_create_worker_server")
        self.mox.StubOutWithMock(runner, "_chmod_the_key")
        self.mox.StubOutWithMock(runner, "_deploy_code_to_worker")
        self.mox.StubOutWithMock(runner, "_replace_server_configs")
        self.mox.StubOutWithMock(runner, "_call_executor")

        # begin recording
        runner._update_ca_run()
        runner._query_entity().AndReturn("woot")
        runner._get_client_detail("woot").AndReturn(("test_client", "woot@woot.com"))
        runner._create_new_sql_db("woot").AndReturn(("chilly", "willy"))
        runner._update_ca_run(target_db_name = "chilly", logging_db_name = "willy")
        runner._run_loader("chilly", "woot").AndReturn("dates_sucka")
        runner._create_worker_server().AndReturn("sucka")
        runner._chmod_the_key()
        runner._deploy_code_to_worker("sucka")
        runner._replace_server_configs("sucka")
        runner._call_executor("woot", "sucka", "chilly", "willy", "test_client", "woot@woot.com",  "dates_sucka").WithSideEffects(sleep_side_effect)
        runner._update_ca_run()

        # replay all
        self.mox.ReplayAll()

        # run
        runner.run()


    def test_error_run(self):

        # create the runner
        runner = CustomAnalyticsRunner(self.task_rec)

        # define an exception method
        exception = Exception("yo mama")
        def raise_exception():
            raise exception

        # begin stubbing things out
        self.mox.StubOutWithMock(runner, "_update_ca_run")
        self.mox.StubOutWithMock(runner, "_query_entity")
        self.mox.StubOutWithMock(logging_helper, "log_exception")
        self.mox.StubOutWithMock(runner, "_send_error_email")

        # begin recording
        runner._update_ca_run()
        runner._query_entity().WithSideEffects(raise_exception)
        logging_helper.log_exception(self.mock_logger, "Error running CustomAnalyticsRunner", exception, IgnoreArg())
        runner._update_ca_run("error", error_string = "yo mama", error_stack_trace = IsA(basestring))
        runner._send_error_email("yo mama", IsA(basestring), self.custom_analytics_run_id)

        # replay all
        self.mox.ReplayAll()

        # run
        with self.assertRaises(Exception):
            runner.run()


    def test_query_entity(self):

        # create mocks
        query = { "_id": self.custom_analytics_run_id }
        projection = { "client_id": 1, "companies": 1, "demographic_template": 1, "trade_areas": 1, "report_name": 1, "user_id": 1, "run_comp_stores_report": 1, "comp_stores_periods": 1 }

        # begin recording
        self.mock_retail_access.find("custom_analytics_run", query, projection).AndReturn(["woot"])

        # replay all
        self.mox.ReplayAll()

        # go
        self.assertEqual(CustomAnalyticsRunner(self.task_rec)._query_entity(), "woot")


    def test_get_client_detail(self):

        # create mock ca_run
        mock_ca_run = {
            "user_id": "51ed900cf3d31bcca5653367",
            "client_id": "51ed900cf3d31bcca5653366"
        }

        # create mock queries
        user_query = { "_id": ObjectId("51ed900cf3d31bcca5653367") }
        user_projection = { "email": 1 }
        client_query = { "_id": ObjectId("51ed900cf3d31bcca5653366") }
        client_projection = { "name": 1 }

        # create mock documents
        mock_user = { "email": "chilly" }
        mock_client = { "name": "willy" }

        # begin recording
        self.mock_retail_access.find("user", user_query, user_projection).AndReturn([mock_user])
        self.mock_retail_access.find("client", client_query, client_projection).AndReturn([mock_client])

        # replay all
        self.mox.ReplayAll()

        # go
        self.assertEqual(CustomAnalyticsRunner(self.task_rec)._get_client_detail(mock_ca_run), ("willy", "chilly"))


    def test_create_new_sql_db(self):

        # create mocks
        mock_client_id = "chicken woot"
        mock_ca_run = {
            "_id": self.custom_analytics_run_id,
            "client_id": mock_client_id,

            # crazy report name!
            "report_name": "123chilly_willy-'\"#!"
        }
        mock_date_time = datetime.datetime(2014, 1, 1)
        mock_target_db_name = "ca_chicken_woot_123chillywilly_2014_01_01_%s" % str(self.custom_analytics_run_id)
        mock_target_db_logging = mock_target_db_name + "_logging"


        # stub some stuff out
        self.mox.StubOutWithMock(datetime, "datetime")
        self.mox.StubOutClassWithMocks(build_db, "DBBuilder")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_date_time)
        self.mock_service_config.__getitem__("GEOPROCESSING_CONFIG").AndReturn("meatwad")
        mock_db_builder = build_db.DBBuilder(mock_target_db_name, mock_target_db_logging, "meatwad")
        mock_db_builder.run()

        # replay all
        self.mox.ReplayAll()

        # go
        results = CustomAnalyticsRunner(self.task_rec)._create_new_sql_db(mock_ca_run)
        self.assertEqual(results, (mock_target_db_name, mock_target_db_logging))


    def test_run_loader(self):

        # create mocks
        mock_db_name = "chilly_willy"
        mock_ca_run = { "companies": "chicken_woot" }

        # begin stubbing
        self.mox.StubOutClassWithMocks(custom_analytics_loader, "CustomAnalyticsLoader")

        # begin recording
        mock_loader = custom_analytics_loader.CustomAnalyticsLoader(mock_db_name, "chicken_woot")
        mock_loader.load().AndReturn("woot")

        # replay all
        self.mox.ReplayAll()

        # go!
        self.assertEqual(CustomAnalyticsRunner(self.task_rec)._run_loader(mock_db_name, mock_ca_run), "woot")


    def test_create_worker_server__has_stopped_server(self):

        # begin recording
        self.mock_cloud_provider.get_stopped_cloud_formation_ec2_instance_ids("GeoProcessingWorker").AndReturn(["chicken"])
        self.mock_cloud_provider.start_ec2_instance("chicken")
        self.mock_cloud_provider.get_ec2_instance_public_dns("chicken").AndReturn("woot")

        # replay all
        self.mox.ReplayAll()

        # go
        self.assertEqual(CustomAnalyticsRunner(self.task_rec)._create_worker_server(), "signal_deploy@woot")


    def test_create_worker_server__create_new_server(self):

        # begin recording
        self.mock_cloud_provider.get_stopped_cloud_formation_ec2_instance_ids("GeoProcessingWorker").AndReturn([])
        self.mock_deployment_provider.create_cloud_server(Regex("/geoprocessing"),
                                                          "build/amazon_cloud_formation/create_geo_processing_amazon_worker_server.py",
                                                          Regex("create_amazon_ubuntu_geo_processing_server.json"),
                                                          "PublicDNS", "GeoProcessingWorker").AndReturn("woot")

        # replay all
        self.mox.ReplayAll()

        # go
        self.assertEqual(CustomAnalyticsRunner(self.task_rec)._create_worker_server(), "signal_deploy@woot")


    def test_create_worker_server(self):
        pass


    def test_deploy_code_to_worker(self):

        # begin recording
        self.mock_deployment_provider.rsync_to_server(Regex("/python"), "chicken:/signal", Regex("infrastructure/keys/SignalDataKey-USEast-2013-07.pem"))

        # replay all
        self.mox.ReplayAll()

        # go
        CustomAnalyticsRunner(self.task_rec)._deploy_code_to_worker("chicken")


    def test_replace_server_configs(self):

        # define some mocks
        old_config = "/signal/python/geoprocessing/config.yml"
        new_config = "/signal/python/geoprocessing/config.cloud.custom_analytics.yml"
        mock_settings = self.mox.CreateMockAnything()

        # begin stubbing
        self.mox.StubOutWithMock(context_managers, "settings")

        # begin recording
        context_managers.settings(host_string = "chicken", key_filename = Regex("SignalDataKey-USEast-2013-07.pem")).AndReturn(mock_settings)
        mock_settings.__enter__()
        self.mock_deployment_provider.replace_configuration_files_on_server(old_config, new_config)
        mock_settings.__exit__(IgnoreArg(), IgnoreArg(), IgnoreArg())

        # replay all
        self.mox.ReplayAll()

        # I love gooooooold
        CustomAnalyticsRunner(self.task_rec)._replace_server_configs("chicken")


    def test_call_executor__no_comp_stores(self):

        # create a mock ca_run
        # this is a real run from the db
        mock_ca_run = {
            "_cls" : "CustomAnalyticsRun",
            "_id" : ObjectId("5317855ef3d31b80ddcc958a"),
            "_types" : [
                "CustomAnalyticsRun"
            ],
            "client_id" : "51ed900cf3d31bcca5653366",
            "companies" : {
                "518347ea4af885658cf882aa" : {
                    "is_target" : True,
                    "time_periods" : {
                        "t0" : "2012-01-11T00:00:00",
                        "t1" : "2012-03-28T00:00:00"
                    },
                    "company_name" : "Whole Foods Market",
                    "weight" : 1
                },
                "525272003f0cd228d1092401" : {
                    "is_target" : True,
                    "time_periods" : {
                        "t0" : "2012-01-11T00:00:00",
                        "t1" : "2012-03-28T00:00:00"
                    },
                    "company_name" : "Adidas",
                    "weight" : 1
                }
            },
            "created_at" : datetime.datetime(2014, 3, 1),
            "demographic_template" : "Drug Stores",
            "report_name" : "Dollar Stores Report",
            "status" : "complete",
            "trade_areas" : [
                "DistanceMiles3",
                "DistanceMiles6"
            ],
            "user_id" : "51ed900cf3d31bcca5653367"
        }

        # create mock time periods
        mock_time_periods = {
            "t0": datetime.datetime(1900, 1, 1, 0, 0),
            "t1": datetime.datetime(1900, 2, 1, 0, 0)
        }

        # create expected settings
        expected_settings = json.dumps({
            "ca_run_id": "5317855ef3d31b80ddcc958a",
            "demographic_template": "Drug Stores",
            "trade_areas": ["DistanceMiles3", "DistanceMiles6"],
            "target_db": "chilly",
            "target_db_logging": "willy",
            "report_name": "Dollar Stores Report",
            "client_name": "test_client",
            "client_email": "test_email",
            "company_settings": {
                "518347ea4af885658cf882aa" : {
                    "is_target" : True,
                    "time_periods" : {
                        "t0" : "2012-01-11T00:00:00",
                        "t1" : "2012-03-28T00:00:00"
                    },
                    "company_name" : "Whole Foods Market",
                    "weight" : 1
                },
                "525272003f0cd228d1092401" : {
                    "is_target" : True,
                    "time_periods" : {
                        "t0" : "2012-01-11T00:00:00",
                        "t1" : "2012-03-28T00:00:00"
                    },
                    "company_name" : "Adidas",
                    "weight" : 1
                }
            },
            "time_periods": [
                {
                    "label": "t0",
                    "date": "1900-01-01 00:00:00"
                },
                {
                    "label": "t1",
                    "date": "1900-02-01 00:00:00"
                }
            ],
            "run_comp_stores_report": False,
            "comp_stores_periods": []
        })

        # create misc mocks
        mock_settings = self.mox.CreateMockAnything()

        # begin stubbing
        self.mox.StubOutWithMock(context_managers, "settings")

        # begin recording
        context_managers.settings(host_string = "chicken", key_filename = Regex("SignalDataKey-USEast-2013-07.pem")).AndReturn(mock_settings)
        mock_settings.__enter__()
        self.mock_deployment_provider.run_custom_analytics_remotely("/signal/python/geoprocessing/build/geoprocessing_custom_analytics_executor.py", "/signal/python/geoprocessing", expected_settings)
        mock_settings.__exit__(IgnoreArg(), IgnoreArg(), IgnoreArg())

        # replay all
        self.mox.ReplayAll()

        # go
        CustomAnalyticsRunner(self.task_rec)._call_executor(mock_ca_run, "chicken", "chilly", "willy", "test_client", "test_email", mock_time_periods, .01)


    def test_call_executor__run_comp_stores(self):

        # create a mock ca_run
        # this is a real run from the db
        mock_ca_run = {
            "_cls" : "CustomAnalyticsRun",
            "_id" : ObjectId("5317855ef3d31b80ddcc958a"),
            "_types" : [
                "CustomAnalyticsRun"
            ],
            "client_id" : "51ed900cf3d31bcca5653366",
            "companies" : {
                "518347ea4af885658cf882aa" : {
                    "is_target" : True,
                    "time_periods" : {
                        "t0" : "2012-01-11T00:00:00",
                        "t1" : "2012-03-28T00:00:00"
                    },
                    "company_name" : "Whole Foods Market",
                    "weight" : 1
                },
                "525272003f0cd228d1092401" : {
                    "is_target" : True,
                    "time_periods" : {
                        "t0" : "2012-01-11T00:00:00",
                        "t1" : "2012-03-28T00:00:00"
                    },
                    "company_name" : "Adidas",
                    "weight" : 1
                }
            },
            "created_at" : datetime.datetime(2014, 3, 1),
            "demographic_template" : "Drug Stores",
            "report_name" : "Dollar Stores Report",
            "status" : "complete",
            "trade_areas" : [
                "DistanceMiles3",
                "DistanceMiles6"
            ],
            "user_id" : "51ed900cf3d31bcca5653367",
            "run_comp_stores_report": True,
            "comp_stores_periods": ["chicken", "woot"]
        }

        # create mock time periods
        mock_time_periods = {
            "t0": datetime.datetime(1900, 1, 1, 0, 0), 
            "t1": datetime.datetime(1900, 2, 1, 0, 0)
        }

        # create expected settings
        expected_settings = json.dumps({
            "ca_run_id": "5317855ef3d31b80ddcc958a",
            "demographic_template": "Drug Stores",
            "trade_areas": ["DistanceMiles3", "DistanceMiles6"],
            "target_db": "chilly",
            "target_db_logging": "willy",
            "report_name": "Dollar Stores Report",
            "client_name": "test_client",
            "client_email": "test_email",
            "company_settings": {
                "518347ea4af885658cf882aa" : {
                    "is_target" : True,
                    "time_periods" : {
                        "t0" : "2012-01-11T00:00:00",
                        "t1" : "2012-03-28T00:00:00"
                    },
                    "company_name" : "Whole Foods Market",
                    "weight" : 1
                },
                "525272003f0cd228d1092401" : {
                    "is_target" : True,
                    "time_periods" : {
                        "t0" : "2012-01-11T00:00:00",
                        "t1" : "2012-03-28T00:00:00"
                    },
                    "company_name" : "Adidas",
                    "weight" : 1
                }
            },
            "time_periods": [
                {
                    "label": "t0",
                    "date": "1900-01-01 00:00:00"
                },
                {
                    "label": "t1",
                    "date": "1900-02-01 00:00:00"
                }
            ],
            "run_comp_stores_report": True,
            "comp_stores_periods": ["chicken", "woot"]
        })

        # create misc mocks
        mock_settings = self.mox.CreateMockAnything()

        # begin stubbing
        self.mox.StubOutWithMock(context_managers, "settings")

        # begin recording
        context_managers.settings(host_string = "chicken", key_filename = Regex("SignalDataKey-USEast-2013-07.pem")).AndReturn(mock_settings)
        mock_settings.__enter__()
        self.mock_deployment_provider.run_custom_analytics_remotely("/signal/python/geoprocessing/build/geoprocessing_custom_analytics_executor.py", "/signal/python/geoprocessing", expected_settings)
        mock_settings.__exit__(IgnoreArg(), IgnoreArg(), IgnoreArg())

        # replay all
        self.mox.ReplayAll()

        # go
        CustomAnalyticsRunner(self.task_rec)._call_executor(mock_ca_run, "chicken", "chilly", "willy", "test_client", "test_email", mock_time_periods, .01)


    def test_update_ca_run__basic(self):

        # create mock query and operations
        mock_date = datetime.datetime.utcnow()
        mock_query = { "_id": self.custom_analytics_run_id }
        mock_operation = {
            "$set": {
                "status": "in_progress",
                "internal_status": "in_progress",
                "heart_beat": mock_date
            }
        }

        # stub stuff
        self.mox.StubOutWithMock(datetime, "datetime")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_date)
        self.mock_retail_access.update("custom_analytics_run", mock_query, mock_operation)

        # replay all
        self.mox.ReplayAll()

        # go
        CustomAnalyticsRunner(self.task_rec)._update_ca_run()


    def test_update_ca_run__other_status(self):

        # create mock query and operations
        mock_date = datetime.datetime.utcnow()
        mock_query = { "_id": self.custom_analytics_run_id }
        mock_operation = {
            "$set": {
                "status": "in_progress",
                "internal_status": "woot",
                "heart_beat": mock_date
            }
        }

        # stub stuff
        self.mox.StubOutWithMock(datetime, "datetime")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_date)
        self.mock_retail_access.update("custom_analytics_run", mock_query, mock_operation)

        # replay all
        self.mox.ReplayAll()

        # go
        CustomAnalyticsRunner(self.task_rec)._update_ca_run("woot")


    def test_update_ca_run__with_dbs(self):

        # create mock query and operations
        mock_date = datetime.datetime.utcnow()
        mock_query = { "_id": self.custom_analytics_run_id }
        mock_operation = {
            "$set": {
                "status": "in_progress",
                "internal_status": "in_progress",
                "heart_beat": mock_date,
                "target_db_name": "chicken",
                "logging_db_name": "woot"
            }
        }

        # stub stuff
        self.mox.StubOutWithMock(datetime, "datetime")

        # begin recording
        datetime.datetime.utcnow().AndReturn(mock_date)
        self.mock_retail_access.update("custom_analytics_run", mock_query, mock_operation)

        # replay all
        self.mox.ReplayAll()

        # go
        CustomAnalyticsRunner(self.task_rec)._update_ca_run(target_db_name = "chicken", logging_db_name = "woot")