# coding=utf-8
import unittest
from core.service.svc_workflow.implementation.task.implementation.celery.celery_router import CeleryRouter

__author__ = 'imashhor'


class CeleryRouterTest(unittest.TestCase):
    def test_celery_router(self):
        router = CeleryRouter()

        self.assertDictEqual(
            {'queue': 'high_priority'},
            router.route_for_task(
                "core.service.svc_workflow.implementation.task.implementation.celery.core_tasks.CompanyDeletion_CeleryTask"
            )
        )

        self.assertDictEqual(
            {'queue': 'analytics'},
            router.route_for_task(
                "core.service.svc_workflow.implementation.task.implementation.celery.core_tasks.CompanyAnalyticsCalculations_CeleryTask"
            )
        )

        self.assertDictEqual(
            {'queue': 'default'},
            router.route_for_task(
                "some.random.task"
            )
        )

