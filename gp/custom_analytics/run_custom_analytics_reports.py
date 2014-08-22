import datetime
from fabric.context_managers import cd, lcd
from fabric.operations import local
from geoprocessing.custom_analytics.reports.custom_analytics_comp_stores_report import CustomAnalyticsCompStoresReport
from geoprocessing.custom_analytics.reports.custom_analytics_competition_report import CustomAnalyticsCompetitionReport
from geoprocessing.custom_analytics.reports.custom_analytics_demographics_aggregate_report import CustomAnalyticsDemographicsAggregateReport
from geoprocessing.custom_analytics.reports.custom_analytics_regional_footprint_report import CustomAnalyticsRegionalFootprintReport
from geoprocessing.custom_analytics.reports.custom_analytics_store_counts_report import CustomAnalyticsStoreCountReport
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies

__author__ = 'erezrubinstein'

class CustomAnalyticsReportRunner(object):

    def __init__(self, categories, time_periods, company_definitions = None, folder_path = "", logger = None, report_name = None, comp_store_settings = None):

        # main dictionary that categorizes which reports belong to which category
        self.reports = {
            "base_reports": [
                CustomAnalyticsStoreCountReport,
                CustomAnalyticsCompetitionReport,
                CustomAnalyticsDemographicsAggregateReport,
                CustomAnalyticsRegionalFootprintReport
            ],
            "comp_stores": [
                CustomAnalyticsCompStoresReport
            ]
        }

        # set class vars
        self.categories = categories
        self.time_periods = time_periods
        self.company_definitions = company_definitions
        self.folder_path = folder_path
        self.logger = logger
        self.report_name = report_name
        self.comp_store_settings = comp_store_settings

        # create report instances
        self.report_instances = self._create_report_instances()



    def run_reports(self):

        # loop through each report in this category
        for report_instance in self.report_instances:

            # nice message
            self._log_info_message("running: %s" % str(type(report_instance)))

            # truncate the report table
            report_instance.lets_make_a_run_for_the_border()

            # run the report
            report_instance.taco_flavored_kisses()


    def export_report_to_excel(self):

        # before starting, delete all the xlsx files in this folder
        # this errors if there are no files, hence the try, except
        try:
            with lcd(self.folder_path):
                local("rm *.xlsx")
        except:
            pass

        # loop through each report in this category
        for report_instance in self.report_instances:

            # nice message
            self._log_info_message("exporting: %s" % str(type(report_instance)))

            # get the results
            results = report_instance.omg_they_killed_kenny()

            # export to excel
            report_instance.mrs_garrisson(results, self.folder_path)


    def zip_up_reports(self):

        # list of reports
        reports = []

        # loop through each report in this category
        for report_instance in self.report_instances:

            # get the report in this folder
            reports.append(report_instance._get_excel_workbook_name())

        # create the zip command
        statement = "find *.xlsx | zip 'Custom Analytics Reports' -@"

        # nice message
        self._log_info_message("zipping reports")

        # run via fabric
        with lcd(self.folder_path):
            local(statement)


    # ---------------------------- Private Stuff ---------------------------- #

    def _create_report_instances(self):

        # base list
        report_instances = []

        # enumerate through classes
        for category in self.categories:
            for report_class in self.reports[category]:

                if category == "comp_stores":
                    report_instances.append(report_class(self.time_periods, self.comp_store_settings, self.company_definitions, self.report_name))
                else:
                    report_instances.append(report_class(self.time_periods, self.company_definitions, self.report_name))

        # booya
        return report_instances


    def _log_info_message(self, message):

        if self.logger:
            self.logger.info(message)
        else:
            print message




# -------------------- Main -------------------- #

def main():

    # create time periods
    time_periods = [
        {
            "label": "t0",
            "date": datetime.datetime(1900, 1, 1)
        },
        {
            "label": "t1",
            "date": datetime.datetime(2013, 7, 31)
        }
    ]

    # create company definitions
    company_definitions = {
		"518347ea4af885658cf882aa" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-11-28T00:00:00",
				"t1" : "2013-06-27T00:00:00"
			},
			"company_name" : "C. Wonder",
			"weight" : 1
		},
		"525272003f0cd228d1092401" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : None,
				"t1" : "2013-12-31T00:00:00"
			},
			"company_name" : "C. Wonder Outlet",
			"weight" : 1
		},
		"dfaer342adsf" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-12T00:00:00",
				"t1" : "2013-07-16T00:00:00"
			},
			"company_name" : "Coach",
			"weight" : 0.7
		},

		"51e65cf95892d05bd02ff35b" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-12T00:00:00",
				"t1" : "2013-07-16T00:00:00"
			},
			"company_name" : "Coach Factory Store",
			"weight" : 0.7
		},
		"51c115865892d00e498773c9" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-12T00:00:00",
				"t1" : "2013-07-16T00:00:00"
			},
			"company_name" : "Coach Men",
			"weight" : 0.7
		},
		"51c011365892d073f4c5e074" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-12T00:00:00",
				"t1" : "2013-07-16T00:00:00"
			},
			"company_name" : "Coach Men Factory",
			"weight" : 0.7
		},
		"518194954af8850754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-26T00:00:00",
				"t1" : "2013-07-01T00:00:00"
			},
			"company_name" : "Furla",
			"weight" : 0.5
		},
        "518194954af8850754c759a" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-11-30T00:00:00",
				"t1" : "2013-11-27T00:00:00"
			},
			"company_name" : "Furla Outlets",
			"weight" : 0.5
		},
        "518194954af8850754c759" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Kate Spade",
			"weight" : 0.3
		},
        "518194954af8850754c75" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Kate Spade Outlet",
			"weight" : 0.3
		},
        "518194954af8850754c7" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-01-11T00:00:00",
				"t1" : "2013-07-21T00:00:00"
			},
			"company_name" : "KORS-AuthDealers",
			"weight" : 0.3
		},
        "518194954af8850754" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-10-03T00:00:00",
				"t1" : "2013-07-03T00:00:00"
			},
			"company_name" : "Longchamp Authorized Dealers",
			"weight" : 0.3
		},
        "518194759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-09-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Marc By Marc Jacobs Women's Accessories",
			"weight" : 0.7
		},
        "5181949af8850754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-08-27T00:00:00",
				"t1" : "2013-07-01T00:00:00"
			},
			"company_name" : "Michael Kors",
			"weight" : 0.7
		},
        "5181949af80754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-08-27T00:00:00",
				"t1" : "2013-07-01T00:00:00"
			},
			"company_name" : "Michael Kors Outlet",
			"weight" : 0.7
		},
        "5181949a0754c759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-11-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Tory Burch",
			"weight" : 1.4
		},
        "5181949af8759ab" : {
			"is_target" : True,
			"time_periods" : {
				"t0" : "2012-11-26T00:00:00",
				"t1" : "2013-06-28T00:00:00"
			},
			"company_name" : "Tory Burch Outlet",
			"weight" : 1.5
		}
	}

    comp_store_settings = [
        {
            "CP": "t1",
            "PP": "t0",
            "PY": "t0"
        }
    ]

    # bomboj for!
    runner = CustomAnalyticsReportRunner(["base_reports", "comp_stores"], time_periods, company_definitions, "exports/", comp_store_settings = comp_store_settings)
    runner.run_reports()
    runner.export_report_to_excel()
    runner.zip_up_reports()

    print "done"


if __name__ == "__main__":

    # register dependencies
    register_concrete_dependencies()

    # run
    main()