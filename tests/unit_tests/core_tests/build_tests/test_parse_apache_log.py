from datetime import datetime
from dateutil import tz
from common.helpers.common_dependency_helper import register_common_mock_dependencies
from common.utilities.inversion_of_control import dependencies, Dependency
from infrastructure.monitoring.apache_log_parser import ApacheLogParser

__author__ = 'erezrubinstein'

import unittest


class ApacheLogParsingTests(unittest.TestCase):
    def setUp(self):
        # register dependencies
        register_common_mock_dependencies()

        # get local dependencies for mocking
        self._file_provider = Dependency("FileProvider").value
        self._email_provider = Dependency("EmailProvider").value

        # date replacement helpers
        self.from_zone = tz.gettz('UTC')
        self.to_zone = tz.gettz('America/New_York')


    def tearDown(self):
        # remove dependencies
        dependencies.clear()


    def __replace_utc_date(self, request_datetime):
        request_datetime = request_datetime.replace(tzinfo = self.from_zone)

        # Convert time zone
        return request_datetime.astimezone(self.to_zone)


    def test_parse_lines(self):
        # mock up file
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "GET /company HTTP/1.1" "200" "2378" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22" "0/168290"',
                                          '"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "GET /favicon.html HTTP/1.1" "404" "406" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22" "0/2188"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        # verify lines were parsed correctly
        self.assertEqual(len(parser.log_entries), 2)

        # assert first entry
        self.assertEqual(parser.log_entries[0].client_ip, "207.97.145.90")
        self.assertEqual(parser.log_entries[0].request_time, self.__replace_utc_date(datetime(2013, 3, 13, 15, 24, 38)))
        self.assertEqual(parser.log_entries[0].request, "GET /company HTTP/1.1")
        self.assertEqual(parser.log_entries[0].response_status, 200)
        self.assertEqual(parser.log_entries[0].response_size, 2378)
        self.assertEqual(parser.log_entries[0].user_agent, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22")
        self.assertEqual(parser.log_entries[0].response_milliseconds, 168)

        # assert first entry
        self.assertEqual(parser.log_entries[1].client_ip, "207.97.145.90")
        self.assertEqual(parser.log_entries[1].request_time, self.__replace_utc_date(datetime(2013, 3, 13, 15, 24, 38)))
        self.assertEqual(parser.log_entries[1].request, "GET /favicon.html HTTP/1.1")
        self.assertEqual(parser.log_entries[1].response_status, 404)
        self.assertEqual(parser.log_entries[1].response_size, 406)
        self.assertEqual(parser.log_entries[1].user_agent, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22")
        self.assertEqual(parser.log_entries[1].response_milliseconds, 2)


    def test_ignore_static_resource(self):
        # mock up file".jpg", ".gif", ".png", ".js", ".ico", ".css"
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "GET /company.jpg HTTP/1.1" "200" "2378" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22" "0/168290"',
                                          '"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "GET /favicon.gif HTTP/1.1" "404" "406" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22" "0/2188"',
                                          '"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "GET /favicon.png HTTP/1.1" "404" "406" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22" "0/2188"',
                                          '"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "GET /favicon.js HTTP/1.1" "404" "406" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22" "0/2188"',
                                          '"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "GET /favicon.ico HTTP/1.1" "404" "406" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22" "0/2188"',
                                          '"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "GET /favicon.css HTTP/1.1" "404" "406" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.160 Safari/537.22" "0/2188"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        # verify lines were parsed correctly
        self.assertEqual(len(parser.log_entries), 0)


    def test_log_per_hour_breakup(self):
        # create log entry for every hour (in utc)
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:04:24:38 +0000]" "1" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "2" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:06:24:38 +0000]" "3" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:07:24:38 +0000]" "4" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:08:24:38 +0000]" "5" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:09:24:38 +0000]" "6" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:10:24:38 +0000]" "7" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:11:24:38 +0000]" "8" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:12:24:38 +0000]" "9" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:13:24:38 +0000]" "10" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:14:24:38 +0000]" "11" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:15:24:38 +0000]" "12" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:16:24:38 +0000]" "13" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:17:24:38 +0000]" "14" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:18:24:38 +0000]" "15" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:19:24:38 +0000]" "16" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:20:24:38 +0000]" "17" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:21:24:38 +0000]" "18" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:22:24:38 +0000]" "19" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:23:24:38 +0000]" "20" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:00:24:38 +0000]" "21" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:01:24:38 +0000]" "22" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:02:24:38 +0000]" "23" "200" "2378" "Mozilla" "0/168290"',
                                           '"207.97.145.90" "[13/Mar/2013:03:24:38 +0000]" "24" "200" "2378" "Mozilla" "0/168290"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        # verify that we have an entry for every hour with the right entries
        self.assertEqual(len(parser.logs_per_hour), 8)

        # verify that each log per hour has 3 entries
        for entry in parser.logs_per_hour:
            self.assertEqual(len(parser.logs_per_hour[entry]), 3)

        # verify that each entry was bucketed in the right place
        self.assertEqual(parser.logs_per_hour[3][0].request, "1")
        self.assertEqual(parser.logs_per_hour[3][1].request, "2")
        self.assertEqual(parser.logs_per_hour[3][2].request, "3")
        self.assertEqual(parser.logs_per_hour[6][0].request, "4")
        self.assertEqual(parser.logs_per_hour[6][1].request, "5")
        self.assertEqual(parser.logs_per_hour[6][2].request, "6")
        self.assertEqual(parser.logs_per_hour[9][0].request, "7")
        self.assertEqual(parser.logs_per_hour[9][1].request, "8")
        self.assertEqual(parser.logs_per_hour[9][2].request, "9")
        self.assertEqual(parser.logs_per_hour[12][0].request, "10")
        self.assertEqual(parser.logs_per_hour[12][1].request, "11")
        self.assertEqual(parser.logs_per_hour[12][2].request, "12")
        self.assertEqual(parser.logs_per_hour[15][0].request, "13")
        self.assertEqual(parser.logs_per_hour[15][1].request, "14")
        self.assertEqual(parser.logs_per_hour[15][2].request, "15")
        self.assertEqual(parser.logs_per_hour[18][0].request, "16")
        self.assertEqual(parser.logs_per_hour[18][1].request, "17")
        self.assertEqual(parser.logs_per_hour[18][2].request, "18")
        self.assertEqual(parser.logs_per_hour[21][0].request, "19")
        self.assertEqual(parser.logs_per_hour[21][1].request, "20")
        self.assertEqual(parser.logs_per_hour[21][2].request, "21")
        self.assertEqual(parser.logs_per_hour[24][0].request, "22")
        self.assertEqual(parser.logs_per_hour[24][1].request, "23")
        self.assertEqual(parser.logs_per_hour[24][2].request, "24")


    def test_run_calculations_per_hour(self):
        # create log entry for every hour (in utc)
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:04:24:38 +0000]" "request" "200" "10" "Mozilla" "0/1000"',
                                           '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request" "200" "20" "Mozilla" "0/2000"',
                                           '"207.97.145.90" "[13/Mar/2013:08:24:38 +0000]" "request" "200" "40" "Mozilla" "0/4000"',
                                           '"207.97.145.90" "[13/Mar/2013:09:24:38 +0000]" "request" "200" "50" "Mozilla" "0/5000"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        # make sure we have calculations for both hours
        self.assertEqual(len(parser.calculations_per_hour), 2)

        # make sure calculations are right per hour
        self.assertEqual(len(parser.calculations_per_hour), 2)
        self.assertEqual(parser.calculations_per_hour[3]["count"], 2)
        self.assertEqual(parser.calculations_per_hour[3]["mean_response_size"], 15)
        self.assertEqual(parser.calculations_per_hour[3]["mean_response_milliseconds"], 1.5)
        self.assertEqual(parser.calculations_per_hour[6]["count"], 2)
        self.assertEqual(parser.calculations_per_hour[6]["mean_response_size"], 45)
        self.assertEqual(parser.calculations_per_hour[6]["mean_response_milliseconds"], 4.5)


    def test_run_calculations_per_hour_per_url(self):
        # create log entry for every hourwith different urls (in utc)
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:04:24:38 +0000]" "request1" "200" "10" "Mozilla" "0/1000"',
                                           '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "200" "20" "Mozilla" "0/2000"',
                                           '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request2" "200" "40" "Mozilla" "0/4000"',
                                           '"207.97.145.90" "[13/Mar/2013:06:24:38 +0000]" "request2" "200" "50" "Mozilla" "0/5000"',
                                           '"207.97.145.90" "[13/Mar/2013:07:24:38 +0000]" "request1" "200" "70" "Mozilla" "0/7000"',
                                           '"207.97.145.90" "[13/Mar/2013:08:24:38 +0000]" "request1" "200" "80" "Mozilla" "0/8000"',
                                           '"207.97.145.90" "[13/Mar/2013:08:24:38 +0000]" "request2" "200" "90" "Mozilla" "0/9000"',
                                           '"207.97.145.90" "[13/Mar/2013:09:24:38 +0000]" "request2" "200" "100" "Mozilla" "0/10000"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        # make sure calculations per hour are right
        self.assertEqual(len(parser.calculations_per_hour), 2)
        self.assertEqual(parser.calculations_per_hour[3]["count"], 4)
        self.assertEqual(parser.calculations_per_hour[3]["mean_response_size"], 30)
        self.assertEqual(parser.calculations_per_hour[3]["mean_response_milliseconds"], 3)
        self.assertEqual(parser.calculations_per_hour[6]["count"], 4)
        self.assertEqual(parser.calculations_per_hour[6]["mean_response_size"], 85)
        self.assertEqual(parser.calculations_per_hour[6]["mean_response_milliseconds"], 8.5)

        # make sure we have 2 urls per group
        self.assertEqual(len(parser.calculations_per_hour[3]["urls"]), 2)
        self.assertEqual(len(parser.calculations_per_hour[6]["urls"]), 2)

        # make sure calculations per hour per url are right
        self.assertEqual(parser.calculations_per_hour[3]["urls"]["request1"]["count"], 2)
        self.assertEqual(parser.calculations_per_hour[3]["urls"]["request1"]["mean_response_size"], 15)
        self.assertEqual(parser.calculations_per_hour[3]["urls"]["request1"]["mean_response_milliseconds"], 1.5)
        self.assertEqual(parser.calculations_per_hour[3]["urls"]["request2"]["count"], 2)
        self.assertEqual(parser.calculations_per_hour[3]["urls"]["request2"]["mean_response_size"], 45)
        self.assertEqual(parser.calculations_per_hour[3]["urls"]["request2"]["mean_response_milliseconds"], 4.5)
        self.assertEqual(parser.calculations_per_hour[6]["urls"]["request1"]["count"], 2)
        self.assertEqual(parser.calculations_per_hour[6]["urls"]["request1"]["mean_response_size"], 75)
        self.assertEqual(parser.calculations_per_hour[6]["urls"]["request1"]["mean_response_milliseconds"], 7.5)
        self.assertEqual(parser.calculations_per_hour[6]["urls"]["request2"]["count"], 2)
        self.assertEqual(parser.calculations_per_hour[6]["urls"]["request2"]["mean_response_size"], 95)
        self.assertEqual(parser.calculations_per_hour[6]["urls"]["request2"]["mean_response_milliseconds"], 9.5)


    def test_run_calculations__do_not_calculate__300_to_500_response(self):
        # create log entry for every hourwith different urls (in utc)
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "300" "10" "Mozilla" "0/1000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "330" "20" "Mozilla" "0/2000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "400" "40" "Mozilla" "0/4000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "450" "50" "Mozilla" "0/5000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "500" "70" "Mozilla" "0/7000"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        self.assertEqual(len(parser.calculations_per_hour), 1)

        # make sure we have 500 response only
        self.assertEqual(len(parser.calculations_per_hour[3]["urls"]), 1)

        # make sure calculations per hour per url are right
        self.assertEqual(parser.calculations_per_hour[3]["urls"]["request1"]["count"], 1)


    def test_calculate_errors(self):
        # create log entry for every hourwith different urls (in utc)
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "300" "10" "Mozilla" "0/1000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "400" "40" "Mozilla" "0/4000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "450" "50" "Mozilla" "0/5000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "450" "50" "Mozilla" "0/5000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "450" "50" "Mozilla" "0/5000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "450" "50" "Mozilla" "0/5000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "500" "70" "Mozilla" "0/7000"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        # 3 errors (not 300)
        self.assertEqual(len(parser.error_list), 3)

        # verify errors are ordered by number
        self.assertEqual(parser.error_list[0]["url"], "request1")
        self.assertEqual(parser.error_list[0]["error"], 450)
        self.assertEqual(parser.error_list[0]["count"], 4)
        self.assertEqual(parser.error_list[1]["url"], "request1")
        self.assertEqual(parser.error_list[1]["error"], 400)
        self.assertEqual(parser.error_list[1]["count"], 1)
        self.assertEqual(parser.error_list[2]["url"], "request1")
        self.assertEqual(parser.error_list[2]["error"], 500)
        self.assertEqual(parser.error_list[2]["count"], 1)


    def test_success_email_sent(self):
        # create log entry for every hourwith different urls
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:04:24:38 +0000]" "request1" "200" "10" "Mozilla" "0/1000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "200" "20" "Mozilla" "0/2000"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        # verify success email sent (basic asserts, don't look at content or to)
        self.assertEqual(self._email_provider.html_from_email, "arnie@nexusri.com")
        self.assertGreater(len(self._email_provider.html_to_email), 0)
        self.assertEqual(self._email_provider.html_subject, "Core Log Parser Report")
        self.assertGreater(len(self._email_provider.html_message), 10)


    def test_success_email_sent(self):
        # create log entry for every hourwith different urls
        self._file_provider.file_lines = ['"207.97.145.90" "[13/Mar/2013:04:24:38 +0000]" "request1" "200" "10" "Mozilla" "0/1000"',
                                          '"207.97.145.90" "[13/Mar/2013:05:24:38 +0000]" "request1" "200" "20" "Mozilla" "0/2000"']

        # parse away
        parser = ApacheLogParser()
        parser.process_log()

        # verify success email sent (basic asserts, don't look at content or to)
        self.assertEqual(self._email_provider.html_from_email, "arnie@nexusri.com")
        self.assertGreater(len(self._email_provider.html_to_email), 0)
        self.assertEqual(self._email_provider.html_subject, "Core Log Parser Report")
        self.assertGreater(len(self._email_provider.html_message), 10)


    def test_error_email_sent(self):
        # update a method with an exception
        parser = ApacheLogParser()
        def exception (): raise Exception("UNITTESTERROR")
        parser._read_file = exception

        # parse away
        parser.process_log()

        # verify success email sent (basic asserts, don't look at content or to)
        self.assertEqual(self._email_provider.html_from_email, "arnie@nexusri.com")
        self.assertGreater(len(self._email_provider.html_to_email), 0)
        self.assertEqual(self._email_provider.html_subject, "Core Log Parser ERROR!!!")
        self.assertGreater(len(self._email_provider.html_message), 10)



if __name__ == '__main__':
    unittest.main()
