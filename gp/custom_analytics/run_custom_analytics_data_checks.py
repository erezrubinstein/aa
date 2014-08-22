from common.helpers import email_provider
from core.data_checks.config.config import email_settings
from geoprocessing.custom_analytics.data_checks.all_stores_have_counties_data_check import CustomAnalyticsStoresHaveCountiesDataCheck
from geoprocessing.custom_analytics.data_checks.trade_area_competition_or_monopolies_data_check import CustomAnalyticsTradeAreaCompetitionOrMonopoliesDataCheck
from geoprocessing.custom_analytics.data_checks.trade_area_demographics_count_data_check import CustomAnalyticsTradeAreaDemographicCountsDataCheck
from geoprocessing.custom_analytics.data_checks.trade_areas_exist_data_check import CustomAnalyticsTradeAreaExistsDataCheck
from geoprocessing.custom_analytics.data_checks.store_count_data_check import CustomAnalyticsStoreCountsDataCheck
from geoprocessing.helpers.dependency_helper import register_concrete_dependencies

__author__ = 'erezrubinstein'

class CustomAnalyticsDataCheckRunner(object):

    def __init__(self, ca_run_id = "", report_name = "", target_db = "", client_name = "", client_email = "", logger = None):

        # define data checks
        self.data_checks = [

            # make sure everything has at least one store
            CustomAnalyticsStoreCountsDataCheck,

            # make sure all stores have the correct trade areas
            CustomAnalyticsTradeAreaExistsDataCheck,

            # make sure every trade area has at least a competition or a monopoly
            CustomAnalyticsTradeAreaCompetitionOrMonopoliesDataCheck,

            # make sure every store has at least one county
            CustomAnalyticsStoresHaveCountiesDataCheck
        ]

        # set class settings that are passed in
        self.ca_run_id = ca_run_id
        self.report_name = report_name
        self.target_db = target_db
        self.client_name = client_name
        self.client_email = client_email
        self.logger = logger

    def run_checks(self):

        # base dict for data checks
        data_check_results = []

        # always pass by default
        data_checks_pass = True

        # loop through every data check and run it
        for data_check_class in self.data_checks:

            # create the data check
            data_check_instance = data_check_class()

            # run the data check
            self._log_info_message("running data check: %s" % str(type(data_check_instance)))
            data_check_name, results = data_check_instance.run()

            # if the data check fails (i.e. we have results), than mark as failed
            if results:
                data_checks_pass = False

            # add to the results
            data_check_results.append({
                "name": data_check_name,
                "results": results
            })

        # if data checks fail, than send an email
        if not data_checks_pass:
            self._send_failed_email(data_check_results)

        # return the data check results
        return data_checks_pass



    # ------------------------- Private ------------------------- #

    def _log_info_message(self, message):

        if self.logger:
            self.logger.info(message)
        else:
            print message

    def _send_failed_email(self, data_check_results):

        # create tables for every results
        html_results = [
            self._create_html_table(result)
            for result in data_check_results
        ]

        # join by line break
        html_results = "<br /><br />".join(html_results)

        # html, baby!
        html = '''
            <html>
                <head>
                    <title>Data Checks Failed</title>
                </head>
                <body>
                    <!-- EMAILHEADER -->
                    <h1>Data Checks Failed</h1>

                    <!-- Report Details -->
                    <div><b>CA Run Id: </b>%s</div>
                    <div><b>Report Name: </b>%s</div>
                    <div><b>Target DB: </b>%s</div>
                    <div><b>Client Name: </b>%s</div>
                    <div><b>User Email: </b>%s</div>

                    <br />
                    %s
                </body>
            </html>''' % (self.ca_run_id, self.report_name, self.target_db, self.client_name, self.client_email, html_results)

        # email settings
        from_email = "support@signaldataco.com"
        to_email = ["engineering@signaldataco.com"]
        subject = "Custom Analytics Data Checks Failed"

        # send the email
        smtp_helper = email_provider.EmailProvider(email_settings["smtp_server"], email_settings["username"], email_settings["password"])
        smtp_helper.send_html_email(from_email, to_email, subject, html)


    def _create_html_table(self, result):

        if result["results"]:

            # create table header out of the results header
            headers = ["<th>%s</th>" % header for header in result["results"]["headers"]]
            headers = " ".join(headers)
            headers = "<thead>%s</thead>" % headers

            # create the rows
            rows = []

            for row in result["results"]["rows"]:

                # create the cells
                cells = ["<td>%s</td>" % row[header] for header in result["results"]["headers"]]
                cells = " ".join(cells)

                # add the cells to the rows
                rows.append("<tr>%s</tr>" % cells)

            # make the rows into html
            rows = "\n".join(rows)
            rows = "<tbody>%s</tbody>" % rows

            # make into table
            result_html = """
            <table border="1">
            %s
            %s
            </table>""" % (headers, rows)

        else:

            result_html = "Passed"

        return """
        <h3>%s</h3>
        %s
        """ % (result["name"], result_html)




# ------------------------- Main ------------------------- #

def main():

    # very nice
    print CustomAnalyticsDataCheckRunner("run_id", "report_name", "target_db", "client_name", "client_email").run_checks()

if __name__ == "__main__":

    # register dependencies
    register_concrete_dependencies()

    # run
    main()