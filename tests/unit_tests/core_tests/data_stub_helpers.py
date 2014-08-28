from bson.objectid import ObjectId
from core.common.utilities.helpers import generate_id
import random
from core.service.svc_analytics.implementation.calc.engines.competition.trade_area_competitive_stores import Taco

__author__ = 'vgold'


def get_add_one_rir_task_group_update_params(timestamp, task_group_exists = True, stores_created = True):

    if task_group_exists:
        params = {'summary': {'input_sourcing.parsing.end_time': timestamp,
                             "input_sourcing.parsing.result.num_rirs": 2,
                             "input_sourcing.parsing.result.num_raw_records": 2,
                             "input_sourcing.churn_matching.status": "ready",
                             "input_sourcing.churn_matching.message": "Churn matching is ready.",
                             "input_sourcing.churn_validation.status": "not_ready",
                             "input_sourcing.churn_validation.message": "Churn validation is not ready."}}
    else:
        params = {'summary': {'input_sourcing.parsing.start_time': timestamp,
                             'input_sourcing.parsing.end_time': timestamp,
                             'input_sourcing.parsing.status': 'success',
                             'input_sourcing.parsing.message': 'File parsing is complete.',
                             "input_sourcing.churn_matching.status": "skipped",
                             "input_sourcing.churn_matching.message": "Churn matching was skipped.",
                             "input_sourcing.churn_validation.status": "skipped",
                             "input_sourcing.churn_validation.message": "Churn validation was skipped."}}

    if stores_created:
        params["summary"]["input_sourcing.parsing.result"] = {"num_rirs": 1, "num_raw_records": 1, "num_stores_created": 1}

    return params


def get_input_sourcing_task_group_summary_dict():

    return {
        "input_sourcing": {
            "parsing": {
                "start_time": None,
                "end_time": None,
                "status": "ready",
                "message": "File parsing is ready.",
                "message_date": None,
                "result": {}
            },
            "churn_matching": {
                "start_time": None,
                "end_time": None,
                "status": "not_ready",
                "message": "Churn matching is not ready.",
                "message_date": None,
                "result": {}
            },
            "churn_validation": {
                "start_time": None,
                "end_time": None,
                "status": "not_ready",
                "message": "Churn validation is not ready.",
                "message_date": None,
                "result": {}
            }
        }
    }


def get_entity_matcher_summary_results(num_exact_matches = 10, num_auto_linkable_matches = 10, num_inexact_matches = 10, num_mismatches = 10):

    return {
        "summary": {
            "exact": {
                generate_id(): [(generate_id(), random.random()) for _ in xrange(num_exact_matches)]
            },
            "auto_linkable": {
                generate_id(): [(generate_id(), random.random()) for _ in xrange(num_auto_linkable_matches)]
            },
            "inexact": {
                generate_id(): [(generate_id(), random.random()) for _ in xrange(num_inexact_matches)]
            },
            "none": {
                generate_id(): [(generate_id(), random.random()) for _ in xrange(num_mismatches)]
            },
        }
    }


def create_mock_taci(company_id = "", trade_area_id = "", date = "", competitions = None):

    return Taco(date, company_id, trade_area_id, competitions)