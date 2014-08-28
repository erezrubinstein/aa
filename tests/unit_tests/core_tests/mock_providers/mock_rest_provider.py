from flask.testing import FlaskClient
from flask.wrappers import Response

import re
import json
import sys
from werkzeug.datastructures import FileStorage

from common.service_access.utilities.type_helpers import is_string_type

__author__ = 'clairseager'


class TestClientRestProvider(object):
    """A Rest Provider for testing and profiling, that uses the Werkzeug test client instead of the requests library."""

    def __init__(self, test_clients):

        self.clients = test_clients
        # for client in self.clients.itervalues():
        #     client.response_wrapper = TestClientRequestResponse

    def open_session(self, *args, **kwargs):
        pass

    def close_session(self):
        pass

    def get_client_and_resource(self, url):

        pat = re.compile("(.*):(\d+)/(.*)")
        match = re.match(pat, url)
        base, port, resource = match.groups()[:3]
        client = self.clients[int(port)]
        return client, "/" + resource

    def make_post_request(self, url, request, time_out=10.0, **kwargs):

        client, resource = self.get_client_and_resource(url)
        #print url, client, resource, request, kwargs.get("headers", None)
        headers = kwargs.get("headers", None)
        content_type = headers.get("content-type", None) if headers else None

        if "files" in kwargs:
            assert(isinstance(request, dict))
            files = kwargs["files"]
            request.update(files)
            #print "REQUEST: ", request
            #print "FILES: ", files
        else:
            assert(is_string_type(request))

        response = client.post(path=resource,
                               data=request,
                               follow_redirects=True,
                               headers = headers,
                               content_type = content_type)
        return response

    def make_get_request(self, url, request, time_out=10.0, **kwargs):

        client, resource = self.get_client_and_resource(url)
        response = client.get(path=resource,
                              query_string=request,
                              follow_redirects=True,
                              headers = kwargs.get("headers", None))
        return response

    def make_put_request(self, url, request, time_out=10.0, **kwargs):

        client, resource = self.get_client_and_resource(url)
        headers = kwargs.get("headers", None)
        content_type = headers.get("content-type", None) if headers else None
        response = client.put(path=resource,
                              data=request,
                              follow_redirects=True,
                              headers = headers,
                              content_type = content_type)
        return response

    def make_delete_request(self, url, request, time_out=10.0, **kwargs):

        client, resource = self.get_client_and_resource(url)
        response = client.delete(path=resource,
                                 query_string=request,
                                 follow_redirects=True,
                                 headers = kwargs.get("headers", None))
        return response


class TestClientRequestResponse(Response):
    """Flask Response class that is masquerading as a requests.Response object

    We are spoofing the methods and properties of the requests.Response object for testing and profiling
    purposes, so that the ServiceAccess class doesn't have to be refactored...
    in general we will use the proper request library with the regular RestProvider.  """

    default_mimetype = 'application/json'

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        json_data = json.loads(self.data)
        # print json_data
        return json_data

    @property
    def content(self):
        return self.data

    @property
    def url(self):
        return "n/a"
