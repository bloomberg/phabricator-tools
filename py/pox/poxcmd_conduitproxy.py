"""conduit-proxy - a webserver for proxying connections to conduit.

It's useful to be able to create admin users for role-accounts in Phabricator
so that they may be able to perform tasks on behalf of users. For installs that
serve a lot of users, the amount of role accounts could get out of hand and
become difficult to audit.

Conduit-proxy allows a single admin role-account user to be re-used without
giving away admin credentials directly to multiple parties.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# poxcmd_conduitproxy
#
# Public Functions:
#   main
#
# Public Assignments:
#   logger
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import BaseHTTPServer
import argparse
import json
import logging
import os
import ssl
import time
import urlparse

import phlsys_conduit
import phlsys_makeconduit

_USAGE_EXAMPLES = """
usage examples:
    proxy the local phabricator install on port 8000, with password 'squirrel':
    $ conduit-proxy --uri http://127.0.0.1 --port 8000 --secret squirrel
"""

logger = logging.getLogger(__name__)  # 'logger' is not allcaps by convention

# TODO: authentication beyond a public secret
# TODO: support multiple conduit destinations


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    phlsys_makeconduit.add_argparse_arguments(parser)

    parser.add_argument(
        '--sslcert',
        metavar="SSLCERT",
        help="certificate to use if you want https")

    parser.add_argument(
        '--port',
        metavar="PORT",
        type=int,
        default=8000,
        help="port to serve the conduit on")

    parser.add_argument(
        '--secret',
        metavar="STRING",
        required=True,
        help="the magic word used to gain access")

    args = parser.parse_args()

    _setup_logging()
    _httpd_serve_forever(args)


def _setup_logging():
    """Configure the root logger to write to a file and the console."""
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        format='%(asctime)s %(message)s',
        level=logging.DEBUG,
        filename='conduit-proxy.log')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)


def _httpd_serve_forever(args):
    """Use '_RequestHandler' to serve webpages forever, optionally with ssl."""
    server_address = ('', args.port)
    factory = _request_handler_factory(args)
    httpd = BaseHTTPServer.HTTPServer(server_address, factory)
    if args.sslcert:
        certpath = os.path.abspath(args.sslcert)
        print certpath
        httpd.socket = ssl.wrap_socket(
            httpd.socket,
            certfile=certpath,
            server_side=True)
    httpd.serve_forever()


class _RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """Handle POST requests by calling out to conduit and reporting back.

    Note that we don't have to worry about threading here as httpd is
    single-threaded.

    """

    def __init__(self, conduitproxy_args, *args):

        # setup the long-running conduit for the proxy
        self.__conduitproxy_args = conduitproxy_args
        self.__conduit = phlsys_makeconduit.make_conduit(
            self.__conduitproxy_args.uri,
            self.__conduitproxy_args.user,
            self.__conduitproxy_args.cert)

        self.path = None  # for pychecker
        self.rfile = None  # for pychecker
        self.wfile = None  # for pychecker
        self.headers = None  # for pychecker

        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        """Handle http POST requests, override of base class function."""

        # do this before sending any response as we may raise an exception
        content = self.__get_content(self.__get_post_body())

        # send the response back to the client
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(content)

    def __get_content(self, post_body):
        """Decode the request and determine the appropriate content."""
        conduit_method = self.path[5:]
        conduit_data = _object_from_urlencoded_json(post_body)
        conduit_proxy_data = conduit_data.get('__conduit__', None)

        username = _get_key_or_none(conduit_proxy_data, "user")
        certificate = _get_key_or_none(conduit_proxy_data, "cert")

        self.__handle_act_as_user(conduit_proxy_data)

        # TODO: log revision id as well, if relevant
        logger.info("user {user} - {method}".format(
            user=username, method=conduit_method))

        response = self.__get_response(
            conduit_method,
            conduit_data,
            certificate)

        content = json.dumps(response)

        return content

    def __get_response(self, conduit_method, conduit_data, certificate):
        """Act on the decoded request and determine the appropriate response.

        Note that this may or may not result in a communication with
        conduit, depending on the kind of request and authentication.

        """
        if conduit_method == 'conduit.connect':
            response = {
                "result": {},
                "error_code": phlsys_conduit.CONDUITPROXY_ERROR_CONNECT,
                "error_info": "This is a conduit proxy, no need to connect",
            }
        else:
            if certificate != self.__conduitproxy_args.secret:
                response = {
                    "result": {},
                    "error_code": phlsys_conduit.CONDUITPROXY_ERROR_BADAUTH,
                    "error_info": "Incorrect user or cert",
                }
            else:
                response = self.__conduit.raw_call(
                    conduit_method, conduit_data)
        return response

    def __get_post_body(self):
        """Return the content that was supplied to us by the client.

        :returns: string content of request

        """
        content_len = int(self.headers.getheader('content-length', 0))
        return self.rfile.read(content_len)

    def __handle_act_as_user(self, conduit_proxy_data):
        """Set our conduit to impersonate another user, if requested."""
        act_as_user = None
        if conduit_proxy_data:
            # Note that we may throw here if conduit_proxy_data is not a dict,
            # this is ok because the BaseHTTPRequestHandler will handle it for
            # us.
            # TODO: check assumption that it handles this for us
            act_as_user = conduit_proxy_data.get('actAsUser', None)
        if act_as_user:
            self.__conduit.set_act_as_user(act_as_user)
        else:
            if self.__conduit.get_act_as_user():
                self.__conduit.clear_act_as_user()


def _object_from_urlencoded_json(encoded):
    """Return the python object represented by the supplied 'encoded'.

    :returns: a python object

    """
    query_string_data = urlparse.parse_qs(encoded)
    params_data = query_string_data['params'][0]
    conduit_data = json.loads(params_data)
    return conduit_data


def _get_key_or_none(d, key):
    return d.get(key, None) if d else None


def _request_handler_factory(custom_param):
    """Return a function that creates a '__RequestHandler'.

    This allows us to provide a 'factory function' suitable for passing to
    BaseHTTPServer.HTTPServer(), whilst providing our own custom first
    argument.

    There doesn't appear to be another way for us to construct our
    '__RequestHandler' with a custom argument.

    :returns: a '__RequestHandler' factory function with a pre-baked argument

    """

    def factory(*args):
        return _RequestHandler(custom_param, *args)

    return factory


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# ------------------------------ END-OF-FILE ----------------------------------
