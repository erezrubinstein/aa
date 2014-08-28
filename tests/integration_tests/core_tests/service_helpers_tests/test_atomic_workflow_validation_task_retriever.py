from core.service.svc_workflow.helpers.atomic_workflow_validation_task_retriever import AtomicWorkflowValidationTaskRetriever
from common.utilities.multi_process_manager import MultiProcessManager
from common.data_access.mongo_access import MongoAccess
from bson.objectid import ObjectId
import unittest


__author__ = 'vgold'


class TestAtomicWorkflowValidationTaskRetriever(unittest.TestCase):

    mongo_access = None

    @classmethod
    def setUpClass(cls):
        cls.mongo_access = MongoAccess("itest_wfs", "localhost", 27017, coll_names=["task", "lox"])

    @classmethod
    def tearDownClass(cls):
        cls.mongo_access.conns["default"].close()

    def setUp(self):
        self.mongo_access.drop_collections(["task", "lox"])

    def tearDown(self):
        pass

    def test_retrieve_next_task(self):
        flow = "retail_curation"
        process = "input_sourcing"
        stage = "churn_validation"

        company_id = str(ObjectId())
        industry_id = str(ObjectId())

        tasks = [
            {
                "_id": ObjectId(),
                "type": "task",
                "flow": flow,
                "process": process,
                "stage": stage,
                "input": {
                    "company_id": company_id,
                    "industry_id": industry_id
                },
                "task_status": {
                    "status": "open"
                }
            }
            for _ in xrange(50)
        ]

        self.mongo_access.insert("task", tasks)

        def run_atomic_task_retriever(ctxt):
            task_retriever = AtomicWorkflowValidationTaskRetriever(self.mongo_access, flow, process, stage, ctxt)
            return task_retriever.retrieve_next_task()

        args_list = [
            {
                "user_id": i,
                "user": {
                    "is_generalist": False
                },
                "team_industries": [industry_id]
            }
            for i in range(100)
        ]

        procman = MultiProcessManager()
        procman.run_mapped_processes(run_atomic_task_retriever, args_list, with_lock=False, raise_on_error=False)

        errors = procman.error_results
        non_errors = []
        for e in errors:
            if e is None and len(non_errors) == 0:
                non_errors.append(e)
            else:
                self.assertTrue(e.startswith("Traceback"))
        self.assertEqual(len(non_errors), 1)

        results = procman.results
        results = [
            r
            for r in results
            if r is not None
        ]
        self.assertEqual(len(results), 1)

        self.assertDictEqual(results[0], {
            '_id': results[0]["_id"],
            'context_data': {
                'team_industries': [industry_id],
                'user': {'is_generalist': False},
                'user_id': results[0]["context_data"]["user_id"]
            },
            'flow': 'retail_curation',
            'input': {
                'company_id': company_id,
                'industry_id': industry_id
            },
            'process': 'input_sourcing',
            'stage': 'churn_validation',
            'task_status': {
                'status': 'in_progress'
            },
            'type': 'task'
        })

        user_locked_task_query = {
            "task_status.status": "locked",
            "context_data.user_id": results[0]["context_data"]["user_id"]
        }
        num_tasks_locked_by_user = self.mongo_access.find("task", user_locked_task_query).count()
        self.assertEqual(num_tasks_locked_by_user, len(tasks) - 1)

        user_in_progress_task_query = {
            "task_status.status": "in_progress",
            "context_data.user_id": results[0]["context_data"]["user_id"]
        }
        num_tasks_in_progress_by_user = self.mongo_access.find("task", user_in_progress_task_query).count()
        self.assertEqual(num_tasks_in_progress_by_user, 1)


if __name__ == '__main__':
    unittest.main()
