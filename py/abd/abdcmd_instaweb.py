"""Start a local webserver to report the status of an arcyd instance."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_instaweb
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import BaseHTTPServer
import os

import abdcmd_arcydstatushtml
import abdcmd_repostatushtml


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--port',
        metavar="PORT",
        type=int,
        default=8000,
        help="port to serve pages on")

    parser.add_argument(
        '--report-file',
        metavar="REPORTFILE",
        type=str,
        required=True,
        help="path to the arcyd report file to render")

    parser.add_argument(
        '--reset-file',
        metavar="NAME",
        type=str,
        help="filename to watch for, will reset operations if the file is "
             "detected and remove the file.")
    parser.add_argument(
        '--pause-file',
        metavar="NAME",
        type=str,
        help="filename to watch for, will pause operations while the file is "
             "detected.")

    parser.add_argument(
        '--repo-file-dir',
        metavar="REPOFILEDIR",
        type=str,
        required=True,
        help="path to the repo files to render")


class _NotFoundError(Exception):
    pass


class _RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, instaweb_args, *args):
        self._instaweb_args = instaweb_args
        self.path = None  # for pychecker
        self.wfile = None  # for pychecker
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):

        try:
            content = self._get_content()
        except _NotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><body><h1>404</h1></body></html>")
            self.wfile.close()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content)
            self.wfile.close()

    def _get_content(self):

        args = self._instaweb_args

        if self.path == '/':
            content = abdcmd_arcydstatushtml.render_content(
                args.reset_file, args.pause_file, args.report_file, '')
        elif self.path.lower().endswith('favicon.ico'):
            raise _NotFoundError('could not find favicon')
        else:
            relative_path = self.path.lstrip('/')
            dir_path = os.path.join(args.repo_file_dir, relative_path)

            # XXX: this is fragile, will go away once arcyd folder
            #      layout is standardized
            repo_path = dir_path + '.try'
            branches_path = dir_path + '.ok'
            content = abdcmd_repostatushtml.render_content(
                repo_path, branches_path)

        return content


def _request_handler_factory(instaweb_args):

    def factory(*args):
        return _RequestHandler(instaweb_args, *args)

    return factory


def process(args):

    # start a webserver
    server_address = ('', args.port)
    factory = _request_handler_factory(args)
    httpd = BaseHTTPServer.HTTPServer(server_address, factory)
    httpd.serve_forever()


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
