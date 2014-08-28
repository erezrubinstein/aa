__author__ = 'erezrubinstein'

class MockBAOnlineConnection(object):
    def __init__(self):
        # variables for mocking
        self.generate_report_response = None
        self.download_urls = {}


    def generate_report(self, request_format, url):
        return self.generate_report_response

    def generate_report_with_post(self, request_format, url):
        return self.generate_report_response

    def download_file(self, url):
        return self.download_urls[url]