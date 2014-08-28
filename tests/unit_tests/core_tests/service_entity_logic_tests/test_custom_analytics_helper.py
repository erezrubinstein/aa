import datetime
import mox
from mox import IsA
from common.helpers.common_dependency_helper import register_common_mox_dependencies
from common.utilities.date_utilities import FastDateParser
from common.utilities.inversion_of_control import Dependency, dependencies
from core.common.business_logic.service_entity_logic import company_helper, custom_analytics_helper
from core.common.business_logic.service_entity_logic.custom_analytics_helper import validate_selected_time_periods, validate_companies, create_new_analytics_run
from retail.v010.data_access.models import custom_analytics_run

__author__ = 'erezrubinstein'


class TestCustomAnalyticsHelper(mox.MoxTestBase):

    def setUp(self):

        # call parent set up
        super(TestCustomAnalyticsHelper, self).setUp()

        # register mock dependencies
        register_common_mox_dependencies(self.mox)

        # helpers
        self.date_parser = FastDateParser()

        # some time periods for the comp store tests
        self.comp_store_time_periods = {
            "company_1": {
                "t0": "ok",
                "t1": "ok",
                "t2": "ok"
            },
            "company_2": {
                "t0": "ok",
                "t1": "ok",
                "t2": "ok"
            },
            "company_3": {
                "t0": "ok",
                "t1": "ok",
                "t2": "ok"
            }
        }

    def doCleanups(self):

        # call parent clean up
        super(TestCustomAnalyticsHelper, self).doCleanups()

        # clear dependencies
        dependencies.clear()


    def test_get_company_collection_dates_and_input_form_defaults(self):

        # define mocks
        mock_company_ids = ["chicken", "woot", "chilly", "willy", "scheisse"]
        mock_companies = [
            { "_id": "chicken", "data": { "collection": { "dates": { "stores": [1, 2, 3, 4] }}}},
            { "_id": "woot", "data": { "collection": { "dates": { "stores": [3, 4] }}}},
            { "_id": "chilly", "data": { "collection": { "dates": { "stores": [1, 2, 3, 4, 5, 6] }}}},
            { "_id": "willy", "data": { "collection": { "dates": { "stores": [1] }}}},
            { "_id": "scheisse", "data": {}}
        ]

        # this is the order in which the dict.values() returns the arrays...  go figure, but it's consistent...
        mock_collection_dates = {
            "chicken": [1, 2, 3, 4],
            "woot": [3, 4],
            "chilly": [1, 2, 3, 4, 5, 6],
            "willy": [1],
            "scheisse": []
        }

        # stub some stuff
        self.mox.StubOutWithMock(company_helper, "get_store_collection_dates")
        self.mox.StubOutWithMock(custom_analytics_helper, "_get_default_date_periods")

        # begin recording
        company_helper.get_store_collection_dates(mock_company_ids).AndReturn(mock_companies)
        custom_analytics_helper._get_default_date_periods(mock_collection_dates, IsA(FastDateParser)).AndReturn("M Dawg")

        # replay all
        self.mox.ReplayAll()

        # yes sir
        results = custom_analytics_helper.get_company_collection_dates_and_input_form_defaults(mock_company_ids)

        # make sure results are correct
        self.assertEqual(results, {
            "collection_dates": mock_collection_dates,
            "max_collection_length": 6,
            "default_time_periods": "M Dawg"
        })


    def test_get_default_date_periods__basic(self):

        # define mocks
        mock_collection_dates_dict = {
            "woot": ["2012-01-01", "2013-01-01"],
            "chicken": ["2012-05-01", "2013-05-01"]
        }

        # run dates through the method
        default_date_periods = custom_analytics_helper._get_default_date_periods(mock_collection_dates_dict, self.date_parser)

        # verify the results
        self.assertEqual(default_date_periods, {
            "woot": {
                "t0": "2012-01-01",
                "t1": "2013-01-01"
            },
            "chicken": {
                "t0": "2012-05-01",
                "t1": "2013-05-01"
            }
        })


    def test_get_default_date_periods__basic_mismatch_fits_in_beginning(self):

        # define dates such that woot has 3 and chicken has 2.
        # chickens dates are close to woot's beginning so they should fit in the first two slots.
        mock_collection_dates_dict = {
            "woot": ["2012-01-01", "2013-01-01", "2013-05-01"],
            "chicken": ["2012-02-01", "2013-02-01"]
        }

        # run dates through the method
        default_date_periods = custom_analytics_helper._get_default_date_periods(mock_collection_dates_dict, self.date_parser)

        # verify the results
        self.assertEqual(default_date_periods, {
            "woot": {
                "t0": "2012-01-01",
                "t1": "2013-01-01",
                "t2": "2013-05-01"
            },
            "chicken": {
                "t0": "2012-02-01",
                "t1": "2013-02-01",
                "t2": None
            }
        })


    def test_get_default_date_periods__basic_mismatch_fits_in_end(self):

        # define dates such that woot has 3 and chicken has 2.
        # chickens dates are close to woot's ed so they should fit in the last two slots.
        mock_collection_dates_dict = {
            "woot": ["2012-01-01", "2013-01-01", "2013-05-01"],
            "chicken": ["2013-02-01", "2014-02-01"]
        }

        # run dates through the method
        default_date_periods = custom_analytics_helper._get_default_date_periods(mock_collection_dates_dict, self.date_parser)

        # verify the results
        self.assertEqual(default_date_periods, {
            "woot": {
                "t0": "2012-01-01",
                "t1": "2013-01-01",
                "t2": "2013-05-01"
            },
            "chicken": {
                "t0": None,
                "t1": "2013-02-01",
                "t2": "2014-02-01"
            }
        })


    def test_get_default_date_periods__complex(self):

        # create a bunch of complicated dates scenarios
        mock_collection_dates_dict = {
            "woot": ["2012-01-01", "2012-02-01", "2012-07-01", "2013-01-01", "2013-05-01", "2014-02-01"],
            "chicken": ["2013-02-01", "2014-02-01"],
            "chilly": ["2012-02-01", "2014-01-01"],
            "willy": ["2012-06-01", "2013-02-01"],
            "M Dawg": ["2011-01-01", "2011-02-01", "2011-03-01"],
        }

        # run dates through the method
        default_date_periods = custom_analytics_helper._get_default_date_periods(mock_collection_dates_dict, self.date_parser)

        # verify the results
        self.assertEqual(default_date_periods, {
            "woot": {
                "t0": "2012-01-01",
                "t1": "2012-02-01",
                "t2": "2012-07-01",
                "t3": "2013-01-01",
                "t4": "2013-05-01",
                "t5": "2014-02-01"
            },
            "chicken": {
                "t0": None,
                "t1": None,
                "t2": None,
                "t3": "2013-02-01",
                "t4": None,
                "t5": "2014-02-01"
            },
            "chilly": {
                "t0": None,
                "t1": "2012-02-01",
                "t2": None,
                "t3": None,
                "t4": None,
                "t5": "2014-01-01"
            },
            "willy": {
                "t0": None,
                "t1": None,
                "t2": "2012-06-01",
                "t3": "2013-02-01",
                "t4": None,
                "t5": None
            },
            "M Dawg": {
                "t0": "2011-01-01",
                "t1": "2011-02-01",
                "t2": "2011-03-01",
                "t3": None,
                "t4": None,
                "t5": None
            }
        })


    def test_validate_selected_time_periods__valid(self):

        # create valid time periods structure
        # NOTE - t3 for companies 1/2 is the same as t2.  This is on purpose and is valid.
        time_periods = {
            "chicken": {
                "t0": "2011-01-01",
                "t1": "2012-01-01",
                "t2": "2013-01-01",
                "t3": "2013-01-01"
            },
            "woot": {
                "t0": "2011-01-01",
                "t1": None,
                "t2": "2013-01-01",
                "t3": "2013-01-01"
            },
            "chilly": {
                "t0": None,
                "t1": None,
                "t2": "2013-01-01",
                "t3": None
            }
        }

        # run through the verifier
        results = validate_selected_time_periods(time_periods)

        # verify that the results are empty
        self.assertEqual(results, {})


    def test_validate_selected_time_periods__invalid_no_companies(self):

        # create valid time periods structure
        time_periods = {}

        # run through the verifier
        with self.assertRaises(Exception) as ex:
            validate_selected_time_periods(time_periods)

        # make sure the error is right
        self.assertTrue("No Time Periods" in ex.exception.message)


    def test_validate_selected_time_periods__company_is_empty(self):

        # create valid time periods structure
        time_periods = {
            "chicken": {},
            "woot": {}
        }

        # run through the verifier
        results = validate_selected_time_periods(time_periods)

        # make sure the error is right
        self.assertEqual(results, {
            "chicken": "No Time Periods",
            "woot": "No Time Periods"
        })


    def test_validate_selected_time_periods__invalid_date(self):

        # create valid time periods structure
        time_periods = {
            "chicken": {
                "t0": "2011-01-01",
                "t1": None,
                "t2": "afasdf",
            }
        }

        # run through the verifier
        results = validate_selected_time_periods(time_periods)

        # make sure the error is right
        self.assertEqual(results, {
            "chicken": "Time period t2 contains an invalid date"
        })


    def test_validate_selected_time_periods__invalid_time_periods_bad_order(self):

        # create valid time periods structure
        time_periods = {
            "chicken": {
                "t0": "2011-01-01",
                "t1": "2011-01-01",
                "t2": "2012-01-01",
            },
            "woot": {
                "t0": "2011-01-01",
                "t1": "2013-01-01",
                "t2": "2012-01-01",
            }
        }

        # run through the verifier
        results = validate_selected_time_periods(time_periods)

        # make sure the error is right
        self.assertEqual(results, {
            "woot": "t1 (2013-01-01) must be older than t2 (2012-01-01)"
        })


    def test_validate_selected_time_periods__invalid_time_periods_bad_order__complex(self):

        # create two nones in between.  This was created because of a bug.
        time_periods = {
            "chicken": {
                "t0": "2013-01-01",
                "t1": None,
                "t2": None,
                "t3": "2012-01-01",
            }
        }

        # run through the verifier
        results = validate_selected_time_periods(time_periods)

        # make sure the error is right
        self.assertEqual(results, {
            "chicken": "t0 (2013-01-01) must be older than t3 (2012-01-01)",
        })


    def test_validate_selected_time_periods__invalid_time_periods_bad_order__complex_2(self):

        # this structure was created because of a bug
        time_periods = {
            "chicken": {
                "t0": "2014-01-01",
                "t1": "2013-02-01",
                "t2": "2013-03-01",
                "t3": "2013-04-01",
                "t4": "2013-05-01",
                "t5": "2013-06-01",
            }
        }

        # run through the verifier
        results = validate_selected_time_periods(time_periods)

        # make sure the error is right
        self.assertEqual(results, {
            "chicken": "t0 (2014-01-01) must be older than t1 (2013-02-01)",
        })



    def test_validate_selected_time_periods__invalid_must_have_dates(self):

        # create valid time periods structure
        time_periods = {
            "chicken": {
                "t0": None,
                "t1": None,
                "t2": None
            }
        }

        # run through the verifier
        results = validate_selected_time_periods(time_periods)

        # make sure the error is right
        self.assertEqual(results, {
            "chicken": "Must contain at least one date",
        })


    def test_validate_companies(self):

        # define mock companies
        mock_companies = {

            # valid
            "beer": {
                "weight": 0.7
            },

            # invalid weight, needs to be positive number
            "chicken": {
                "weight": 0
            },

            # invalid weight, needs to be positive number
            "woot": {
                "weight": -1
            },

            # invalid weight, needs to be a number
            "chilly": {
                "weight": None
            },

            # invalid weight, not even there,
            "willy": { },

            # invalid weight, needs to be a number
            "morty": {
                "weight": "asdfasdfa"
            },

            # valid
            "chicken_woot": {
                "weight": 10
            }
        }

        # run through the validate function
        results = validate_companies(mock_companies)

        self.assertEqual(results, {
            "chicken": "Invalid weight (must be a positive number)",
            "woot": "Invalid weight (must be a positive number)",
            "chilly": "Invalid weight (must be a positive number)",
            "willy": "Invalid weight (must be a positive number)",
            "morty": "Invalid weight (must be a positive number)"
        })


    def test_create_new_analytics_run(self):

        # create mock companies and time periods
        mock_companies = {
            "chicken": {},
            "chilly": {}
        }
        mock_time_periods = "arggghh"
        mock_formatted_time_periods = {
            "chicken": "woot",
            "chilly": "willy"
        }

        # create misc mock stuff
        mock_report_name = "morty"
        mock_trade_areas = "dog"
        mock_demographic_template = "austin"
        mock_client_id = "danger"
        mock_user_id = "powers"
        mock_run_comp_stores_report = False
        mock_comp_stores_periods = ["I", "Pitty", "The", "Fool"]
        mock_date = datetime.datetime.utcnow()
        mock_ca_run = self.mox.CreateMockAnything()

        # create expected record
        expected_companies = {
            "chicken": {
                "time_periods": "woot"
            },
            "chilly": {
                "time_periods": "willy"
            }
        }
        expected_custom_analytics_run = {
            "report_name": mock_report_name,
            "trade_areas": mock_trade_areas,
            "demographic_template": mock_demographic_template,
            "companies": expected_companies,
            "client_id": mock_client_id,
            "user_id": mock_user_id,
            "status": "queued",
            "internal_status": "queued",
            "created_at": mock_date,
            "run_comp_stores_report": mock_run_comp_stores_report,
            "comp_stores_periods": mock_comp_stores_periods
        }

        # begin stubbing
        self.mox.StubOutWithMock(custom_analytics_helper, "_remove_null_time_periods_and_remap_comp_stores")
        self.mox.StubOutWithMock(datetime, "datetime")
        self.mox.StubOutWithMock(custom_analytics_run, "CustomAnalyticsRun")

        # begin recording
        custom_analytics_helper._remove_null_time_periods_and_remap_comp_stores(mock_time_periods, mock_run_comp_stores_report, mock_comp_stores_periods).AndReturn((mock_formatted_time_periods, mock_comp_stores_periods))
        datetime.datetime.utcnow().AndReturn(mock_date)
        custom_analytics_run.CustomAnalyticsRun(**expected_custom_analytics_run).AndReturn(mock_ca_run)
        mock_ca_run.save()

        # replay all
        self.mox.ReplayAll()

        # go!
        ca_run = create_new_analytics_run(mock_report_name, mock_trade_areas, mock_demographic_template, mock_companies, mock_time_periods, mock_run_comp_stores_report, mock_comp_stores_periods, mock_client_id, mock_user_id)

        # in 'yo face!
        self.assertIsNotNone(ca_run)


    def test_remove_null_time_periods_and_remap_comp_stores(self):

        # create mock periods
        # we have 2 blank in the beginning, one in the middle, and one at the end
        mock_time_periods = {
            "chicken": {
                "t0": None,
                "t1": None,
                "t2": "2014-03-21",
                "t3": None,
                "t4": None,
                "t5": None
            },
            "woot": {
                "t0": None,
                "t1": None,
                "t2": "2014-03-22",
                "t3": None,
                "t4": None,
                "t5": None
            },
            "m-dog": {
                "t0": None,
                "t1": None,
                "t2": "2014-03-23",
                "t3": None,
                "t4": "2014-03-24",
                "t5": None
            }
        }

        # create the formatted (expected) time periods after removing the beginning
        formatted_time_periods = {
            "chicken": {
                "t0": "2014-03-21",
                "t1": None
            },
            "woot": {
                "t0": "2014-03-22",
                "t1": None
            },
            "m-dog": {
                "t0": "2014-03-23",
                "t1": "2014-03-24"
            }
        }

        # run through
        time_period_results, comp_store_setting_results = custom_analytics_helper._remove_null_time_periods_and_remap_comp_stores(mock_time_periods, False, [])

        # make sure everything is right
        self.assertEqual(time_period_results, formatted_time_periods)
        self.assertEqual(comp_store_setting_results, [])


    def test_remove_null_time_periods_and_remap_comp_stores__comp_stores_remapped(self):

        # create 5 time periods with a 2 nulls
        mock_time_periods = {
            "company": {
                "t0": "ok0",
                "t1": None,
                "t2": "ok2",
                "t3": None,
                "t4": "ok4",
                "t5": "ok5"
            }
        }

        # create the expected time periods after removing the beginning
        expected_time_periods = {
            "company": {
                "t0": "ok0",
                "t1": "ok2",
                "t2": "ok4",
                "t3": "ok5"
            }
        }

        # create comp store settings, which will need to be mapped
        comp_store_settings = [
            {
                "CP": "t4",
                "PP": "t2",
                "PY": "t0"
            },
            {
                "CP": "t5",
                "PP": "t2",
                "PY": "t0"
            }
        ]

        # create the expected comp store settings after remapping
        expected_comp_store_settings = [
            {
                "CP": "t2",
                "PP": "t1",
                "PY": "t0"
            },
            {
                "CP": "t3",
                "PP": "t1",
                "PY": "t0"
            }
        ]

        # run through
        time_period_results, comp_store_setting_results = custom_analytics_helper._remove_null_time_periods_and_remap_comp_stores(mock_time_periods, True, comp_store_settings)

        # make sure everything is right
        self.assertEqual(time_period_results, expected_time_periods)
        self.assertEqual(comp_store_setting_results, expected_comp_store_settings)


    def test_validate_comp_store_settings__report_not_checked(self):

        # run the validations
        results = custom_analytics_helper.validate_comp_store_settings(False, [], self.comp_store_time_periods)

        # verify that validations were skipped
        self.assertEqual(results, {})


    def test_validate_comp_store_settings__no_periods(self):

        # run the validations
        results = custom_analytics_helper.validate_comp_store_settings(True, [], self.comp_store_time_periods)

        # verify the error
        self.assertEqual(results, {
            0: "At least one Period is required to run the Comp Stores report."
        })


    def test_validate_comp_store_settings__incomplete_periods(self):

        # create one good period and all the others are incomplete for different reasons
        periods = [
            {
                "CP": "t2",
                "PP": "t1",
                "PY": "t0"
            },
            {
                "CP": "t2",
                "PP": "t1",
                "PY": None
            },
            {
                "CP": "t2",
                "PP": None,
                "PY": "t0"
            },
            {
                "CP": "t2",
                "PP": "t1",
                "PY": "t0"
            },
            {
                "CP": None,
                "PP": "t1",
                "PY": "t0"
            },
            {
            }
        ]

        # run the validations
        results = custom_analytics_helper.validate_comp_store_settings(True, periods, self.comp_store_time_periods)

        # verify the error
        self.assertEqual(results, {
            1: "Comp Stores Period 1 is incomplete.",
            2: "Comp Stores Period 2 is incomplete.",
            4: "Comp Stores Period 4 is incomplete.",
            5: "Comp Stores Period 5 is incomplete."
        })


    def test_validate_comp_store_settings__cohort_order_wrong(self):

        # create four periods.  where p0/p3 are good, p1/2 are not good
        periods = [
            {
                "CP": "t2",
                "PP": "t1",
                "PY": "t0"
            },
            {
                "CP": "t2",
                "PP": "t3",
                "PY": "t1"
            },
            {
                "CP": "t4",
                "PP": "t2",
                "PY": "t3"
            },
            {
                "CP": "t5",
                "PP": "t4",
                "PY": "t3"
            }
        ]

        # run the validations
        results = custom_analytics_helper.validate_comp_store_settings(True, periods, self.comp_store_time_periods)

        # verify the error
        self.assertEqual(results, {
            1: "Period 1 is incorrect.  CP should be later than PP.",
            2: "Period 2 is incorrect.  PP should be later than PY."
        })


    def test_validate_comp_store_settings__mixed_errors(self):

        # create two periods.  p0 is incomplete, p1 has time periods in the wrong order
        periods = [
            {
                "CP": None,
                "PP": None,
                "PY": None
            },
            {
                "CP": "t2",
                "PP": "t3",
                "PY": "t1"
            }
        ]

        # run the validations
        results = custom_analytics_helper.validate_comp_store_settings(True, periods, self.comp_store_time_periods)

        # verify the error
        self.assertEqual(results, {
            0: "Comp Stores Period 0 is incomplete.",
            1: "Period 1 is incorrect.  CP should be later than PP."
        })


    def test_validate_comp_store_settings__same_period(self):

        # create two periods.  p0 is incomplete, p1 has time periods in the wrong order
        periods = [
            {
                "CP": "t0",
                "PP": "t0",
                "PY": "t0"
            }
        ]

        # run the validations
        results = custom_analytics_helper.validate_comp_store_settings(True, periods, self.comp_store_time_periods)

        # verify the error
        self.assertEqual(results, {
            0: "Period 0 is incorrect.  CP should be later than PP.",
        })


    def test_validate_comp_store_settings__not_enough_non_null_periods(self):

        # create 3 time periods, but one is null
        bad_time_periods = {
            "company_1": {
                "t0": "ok",
                "t1": None,
                "t2": "ok"
            },
            "company_2": {
                "t0": "ok",
                "t1": None,
                "t2": "ok"
            },
            "company_3": {
                "t0": "ok",
                "t1": None,
                "t2": "ok"
            }
        }

        # create two periods.  p0 is incomplete, p1 has time periods in the wrong order
        periods = [
            {
                "CP": "t2",
                "PP": "t1",
                "PY": "t0"
            }
        ]

        # run the validations
        results = custom_analytics_helper.validate_comp_store_settings(True, periods, bad_time_periods)

        # verify the error
        self.assertEqual(results, {
            0: "Not enough time periods.  There must be at least 3 (non-None) time periods."
        })


    def test_validate_comp_store_settings__none_periods_in_setup(self):

        # create a bunch of time periods with a couple of null ones
        bad_time_periods = {
            "company_1": {
                "t0": "ok",
                "t1": "ok",
                "t2": None,
                "t3": "ok",
                "t4": "ok"
            },
            "company_2": {
                "t0": "ok",
                "t1": "ok",
                "t2": None,
                "t3": "ok",
                "t4": "ok"
            },
            "company_3": {
                "t0": "ok",
                "t1": "ok",
                "t2": None,
                "t3": "ok",
                "t4": "ok"
            }
        }

        # create two periods.  p0 is incomplete, p1 has time periods in the wrong order
        periods = [
            {
                "CP": "t2", # bad CP
                "PP": "t1",
                "PY": "t0"
            },
            {
                "CP": "t3",
                "PP": "t2", # bad PP
                "PY": "t0"
            },
            {
                "CP": "t4",
                "PP": "t3",
                "PY": "t2" # bad PY
            }
        ]

        # run the validations
        results = custom_analytics_helper.validate_comp_store_settings(True, periods, bad_time_periods)

        # verify the error
        self.assertEqual(results, {
            0: "Period 0 is incorrect.  CP has a time period with all Nones.",
            1: "Period 1 is incorrect.  PP has a time period with all Nones.",
            2: "Period 2 is incorrect.  PY has a time period with all Nones."
        })


    def test_separate_null_from_none_null_time_periods(self):

        # create time periods for a few companies.  some null, some not
        time_periods = {
            "company_1": {
                "t0": "ok",
                "t1": None,
                "t2": "ok",
                "t3": "ok",
                "t4": "ok"
            },
            "company_2": {
                "t0": "ok",
                "t1": None,
                "t2": "ok",
                "t3": "ok",
                "t4": "ok"
            },
            "company_3": {
                "t0": "ok",
                "t1": None,
                "t2": "ok",
                "t3": None,
                "t4": "ok"
            }
        }

        # get the null, not null sets
        non_null, null = custom_analytics_helper._separate_null_from_none_null_time_periods(time_periods)

        # verify
        self.assertEqual(sorted(non_null), sorted(["t0", "t2", "t3", "t4"]))
        self.assertEqual(null, ["t1"])