"""Test suite for phlurl_request."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] URL utilities work correctly
# [ B] URL grouping works correctly
# [ C] Http requests can be issued using URLs
# [ D] Connections to host are reused for subsequent requests to same host/port
# [ E] Basic authentication is used if username/password details are provided
# [ F] '301 moved permanently' HTTP redirection is handled properly
# -----------------------------------------------------------------------------
# Tests:
# [ A] Test.test_join_url
# [ A] Test.test_split_url
# [ B] Test.test_group_urls
# [ C] HttpTest.test_get
# [ D] HttpTest.test_get_many
# [CE] HttpTest_Auth.test_get
# [DE] HttpTest_Auth.test_get_many
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import BaseHTTPServer
import SocketServer
import multiprocessing
import unittest

import phlurl_request


class HttpReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        self.wfile = None  # for pychecker

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write('OK')

    def log_message(self, format, *args):
        pass  # don't print output to stderr


class BasicAuthHttpReqHandler(HttpReqHandler):

    def __init__(self, *args, **kwargs):
        HttpReqHandler.__init__(self, *args, **kwargs)
        self.headers = None  # for pychecker
        self.wfile = None  # for pychecker

    def do_GET(self):
        auth = self.headers.getheader('Authorization')
        if auth is None:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('Authentication required')
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(auth)


def httpd_serve_forever(parent_pipe, req_handler):
    httpd = SocketServer.TCPServer(("localhost", 0), req_handler, False)
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()
    parent_pipe.send(httpd.server_address)
    parent_pipe.close()
    httpd.serve_forever()


def start_httpd(request_handler):
    parent_conn, child_conn = multiprocessing.Pipe(False)

    httpd_process = multiprocessing.Process(
        target=httpd_serve_forever,
        args=(child_conn, request_handler,))

    httpd_process.start()
    child_conn.close()

    httpd_host, httpd_port = parent_conn.recv()
    return (httpd_process, httpd_host, httpd_port)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_join_url(self):
        self.assertEqual(
            phlurl_request.join_url('http://example.com/', 'mypage/'),
            'http://example.com/mypage/')
        self.assertEqual(
            phlurl_request.join_url('http://example.com', 'mypage/'),
            'http://example.com/mypage/')
        self.assertEqual(
            phlurl_request.join_url('https://example.com:443/', 'mypage/'),
            'https://example.com:443/mypage/')
        self.assertEqual(
            phlurl_request.join_url('https://example.com:443', 'mypage/'),
            'https://example.com:443/mypage/')

    def test_split_url(self):
        self.assertEqual(
            phlurl_request.split_url('https://www.bloomberg.com:80/index'),
            phlurl_request.SplitUrlResult(
                'https://www.bloomberg.com:80/index',
                'https', 'www.bloomberg.com', 80, '/index', None, None))
        self.assertEqual(
            phlurl_request.split_url('HTTPS://WWW.BLOOMBERG.COM:80/INDEX'),
            phlurl_request.SplitUrlResult(
                'HTTPS://WWW.BLOOMBERG.COM:80/INDEX',
                'https', 'www.bloomberg.com', 80, '/INDEX', None, None))
        self.assertEqual(
            phlurl_request.split_url('https://www.bloomberg.com/index'),
            phlurl_request.SplitUrlResult(
                'https://www.bloomberg.com/index',
                'https', 'www.bloomberg.com', None, '/index', None, None))
        self.assertEqual(
            phlurl_request.split_url(
                'https://www.bloomberg.com/index?a=index&b=c'),
            phlurl_request.SplitUrlResult(
                'https://www.bloomberg.com/index?a=index&b=c',
                'https',
                'www.bloomberg.com',
                None,
                '/index?a=index&b=c',
                None,
                None))

    def test_group_urls(self):
        urls = ['http://a.io/a', 'http://a.io/b', 'https://b.io/c']

        expected_split_a = phlurl_request.SplitUrlResult(
            'http://a.io/a',
            'http', 'a.io', None, '/a', None, None)

        expected_split_b = phlurl_request.SplitUrlResult(
            'http://a.io/b',
            'http', 'a.io', None, '/b', None, None)

        expected_split_c = phlurl_request.SplitUrlResult(
            'https://b.io/c',
            'https', 'b.io', None, '/c', None, None)

        expected_http = {
            ('a.io', None): [expected_split_a, expected_split_b],
        }

        expected_https = {
            ('b.io', None): [expected_split_c]
        }

        result = phlurl_request._group_urls(urls)
        http_result = dict(result.http)
        https_result = dict(result.https)

        self.assertEqual(
            http_result,
            expected_http)

        self.assertEqual(
            https_result,
            expected_https)


class HttpTest(unittest.TestCase):

    def __init__(self, data):
        super(HttpTest, self).__init__(data)
        self.httpd_process = None
        self.httpd_host = None
        self.httpd_port = None

    def setUp(self):
        self.httpd_process, self.httpd_host, self.httpd_port = start_httpd(
            HttpReqHandler)

    def tearDown(self):
        self.httpd_process.terminate()

    def test_get(self):
        self.assertEqual(
            phlurl_request.get(self._url('http://{host}:{port}/index')),
            (200, 'OK'))

    def test_get_many(self):

        expected = {
            self._url('http://{host}:{port}/a'): (200, 'OK'),
            self._url('http://{host}:{port}/b'): (200, 'OK'),
            self._url('http://{host}:{port}/c'): (200, 'OK'),
        }

        self.assertEqual(
            phlurl_request.get_many(expected.iterkeys()),
            expected)

    def _url(self, format_string):
        return format_string.format(
            host=self.httpd_host,
            port=self.httpd_port)


class HttpTest_Auth(unittest.TestCase):

    def __init__(self, data):
        super(HttpTest_Auth, self).__init__(data)
        self.httpd_process = None
        self.httpd_host = None
        self.httpd_port = None

    def setUp(self):
        self.httpd_process, self.httpd_host, self.httpd_port = start_httpd(
            BasicAuthHttpReqHandler)

    def tearDown(self):
        self.httpd_process.terminate()

    def test_get(self):

        self.assertEqual(
            phlurl_request.get(self._url('http://{host}:{port}/index')),
            (401, 'Authentication required'))

        self.assertEqual(
            phlurl_request.get(
                self._url('http://foo:bar@{host}:{port}/index')),
            (200, 'Basic Zm9vOmJhcg=='))

    def test_get_many(self):

        url_a = self._url('http://{host}:{port}/index')
        url_b = self._url('http://foo:bar@{host}:{port}/index')
        url_c = self._url('http://baz:buz@{host}:{port}/index')

        expected = {
            url_a: (401, 'Authentication required'),
            url_b: (200, 'Basic Zm9vOmJhcg=='),
            url_c: (200, 'Basic YmF6OmJ1eg=='),
        }

        self.assertEqual(
            phlurl_request.get_many(expected.iterkeys()),
            expected)

    def _url(self, format_string):
        return format_string.format(
            host=self.httpd_host,
            port=self.httpd_port)


# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
