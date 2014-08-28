from datetime import datetime
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
import mox
from core.service.svc_workflow.implementation.task.implementation.retailer_tasks.retailer_store_tasks_runner import RetailerStoreTasksRunner


class TestRetailerStoreTasksRunner(mox.MoxTestBase):
    def setUp(self):
        # call parent set up
        super(TestRetailerStoreTasksRunner, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # get various mock dependencies
        self.mock_main_access = Dependency("CoreAPIProvider").value
        self.mock_main_params_builder = Dependency("CoreAPIParamsBuilder").value
        self.mock_logger = Dependency("FlaskLogger").value

        # This is the tasks the runner should expect:
        self.runner_tasks = [
            {
                "flow": "retailer_curation",
                "process": "input_sourcing",
                "stage": "customer_gis_loading",
                "status_field": "data.workflow.customer_gis_loading.status",
                "stores_to_run": []
            },
            {
                "flow": "retailer_curation",
                "process": "retailer_analytics",
                "stage": "retailer_store_trade_area_ring_calcs",
                "status_field": "data.workflow.retailer_store_trade_area_ring_calcs.status",
                "stores_to_run": []
            }
        ]



    def doCleanups(self):
        # call parent clean up
        super(TestRetailerStoreTasksRunner, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_calculate_num_jobs_available(self):
        # Test that the query for getting num jobs available is correct

        input_rec = self.get_common_input_rec()
        runner = RetailerStoreTasksRunner(input_rec)
        runner.tasks = self.runner_tasks

        self.mock_main_access.mds.call_find_entities_raw(
            'retailer_store',
            {
                'query': {
                    '$or':
                        [
                            {'data.workflow.customer_gis_loading.status': {'$in': ['queued', 'in_progress']}},
                            {'data.workflow.retailer_store_trade_area_ring_calcs.status': {'$in': ['queued', 'in_progress']}}
                        ]
                },
                'limit': 10,
                'options': {'as_list': True},
                'entity_fields': ['_id']
            },
            {'source': 'unit_test', 'user_id': 'test_user'}
        ).AndReturn([1,2,3,4])

        self.mox.ReplayAll()

        runner._calculate_num_jobs_available()

        # Should have 6 jobs available (max = 10, found = 4)
        self.assertEqual(6, runner.num_jobs_available)


    def test_get_queued_stores_to_run(self):
        # Test that the query for getting retailer stores that are queued is correct
        # and that it will store the results properly

        input_rec = self.get_common_input_rec()
        runner = RetailerStoreTasksRunner(input_rec)
        runner.num_jobs_available = 7

        # First it should try and query for the GIS loader task (get 4 stores)
        self.mock_main_access.mds.call_find_entities_raw(
            'retailer_store',
            {
                'query': {'data.workflow.customer_gis_loading.status': 'needs_run'},
                'limit': 7,
                'options': {'as_list': True},
                'entity_fields': ['_id', 'data.retailer_client_id', 'data.store_id']
            },
            {'source': 'unit_test', 'user_id': 'test_user'}
        ).AndReturn([1,2,3,4])

        # Then it should try and query for the store trade area calcs tasks, and only look for 3 more stores
        self.mock_main_access.mds.call_find_entities_raw(
            'retailer_store',
            {
                'query': {'data.workflow.retailer_store_trade_area_ring_calcs.status': 'needs_run'},
                'limit': 3,
                'options': {'as_list': True},
                'entity_fields': ['_id', 'data.retailer_client_id', 'data.store_id']
            },
            {'source': 'unit_test', 'user_id': 'test_user'}
        ).AndReturn([7,8,9])

        self.mox.ReplayAll()

        runner._get_queued_stores_to_run()

        self.assertEqual([1,2,3,4], runner.tasks[0]["stores_to_run"])
        self.assertEqual([7,8,9], runner.tasks[1]["stores_to_run"])


    def test_create_tasks(self):
        input_rec = self.get_common_input_rec()
        runner = RetailerStoreTasksRunner(input_rec)

        # tasks for gis_loading
        runner.tasks[0]["stores_to_run"] = [
            # object_id, retailer_client_id, store_id
            [1, 1, "20"],
            [1, 1, "520"],
        ]

        # task for trade_area_ring
        runner.tasks[1]["stores_to_run"] = [
            # object_id, retailer_client_id, store_id
            [1, 1, "216"],
            [1, 1, "22"]
        ]

        runner.as_of_date = datetime(2014, 10, 1)

        # These are the params and recs that should be created by the code for gis_loading tasks
        expected_gis_loading_task_params = [
            {
                'input': {
                    'as_of_date': datetime(2014, 10, 1, 0, 0),
                    'retailer_client_id': 1,
                    'retailer_store_id': '20'
                },
                'meta': {'async': True}},
            {
                'input': {
                    'as_of_date': datetime(2014, 10, 1, 0, 0),
                    'retailer_client_id': 1,
                    'retailer_store_id': '520'
                },
                'meta': {'async': True}}
        ]

        expected_gis_loading_task_recs = [dict(param.items() + [("_id", 10)]) for param in expected_gis_loading_task_params]

        # These are the params and recs that should be created by the code for trade_area_ring tasks
        expected_trade_area_ring_task_params = [
            {
                'input': {
                    'as_of_date': datetime(2014, 10, 1, 0, 0),
                    'retailer_client_id': 1,
                    'retailer_store_id': '216'
                },
                'meta': {'async': True}},
            {
                'input': {
                    'as_of_date': datetime(2014, 10, 1, 0, 0),
                    'retailer_client_id': 1,
                    'retailer_store_id': '22'
                },
                'meta': {'async': True}}
        ]

        expected_trade_area_ring_task_recs = [dict(param.items() + [("_id", 15)]) for param in expected_trade_area_ring_task_params]

        # Mock the corresponding wfs calls
        self.mock_main_access.wfs.call_task_batch_new(
            'retailer_curation', 'input_sourcing', 'customer_gis_loading',expected_gis_loading_task_params,
            {'source': 'unit_test', 'user_id': 'test_user'}).AndReturn(expected_gis_loading_task_recs)

        self.mock_main_access.wfs.call_task_batch_new(
            'retailer_curation',  'retailer_analytics', 'retailer_store_trade_area_ring_calcs', expected_trade_area_ring_task_params,
            {'source': 'unit_test', 'user_id': 'test_user'}).AndReturn(expected_trade_area_ring_task_recs)

        self.mox.ReplayAll()

        # Run eet!
        runner._create_tasks()

        # Validate results (yeah task id is the same because its a pain to write code to make it different
        expected_gis_loading_task_results = [
            {
                "task_id": 10,
                "retailer_client_id": 1,
                "retailer_store_id": "20",
            },
            {
                "task_id": 10,
                "retailer_client_id": 1,
                "retailer_store_id": "520",
            }
        ]

        self.assertEqual(expected_gis_loading_task_results, runner.results["tasks"]["customer_gis_loading"])


        expected_trade_area_ring_task_results = [
            {
                "task_id": 15,
                "retailer_client_id": 1,
                "retailer_store_id": "216",
            },
            {
                "task_id": 15,
                "retailer_client_id": 1,
                "retailer_store_id": "22",
            }
        ]

        self.assertEqual(expected_trade_area_ring_task_results, runner.results["tasks"]["retailer_store_trade_area_ring_calcs"])




    def get_common_input_rec(self):
        return {"max_simultaneous_jobs": 10,
                "async": True,
                "context": {"source": "unit_test",
                            "user_id": "test_user"}}