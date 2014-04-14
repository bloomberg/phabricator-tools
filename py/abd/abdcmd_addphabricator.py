"""Make a new phabricator instance known to the Arcyd instance."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_addphabricator
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

import phlsys_conduit

import abdt_fs


_CONFIG = """
--instance-uri
{instance_uri}
--arcyd-user
{arcyd_user}
--arcyd-cert
{arcyd_cert}
--review-url-format
{review_url_format}
""".strip()

_CONFIG_HTTPS_PROXY = """
--https-proxy
{https_proxy}
""".strip()

_CONFIG_ADMIN_EMAILS_FORMAT = """
--admin-emails
{admin_emails}
""".strip()


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--name',
        type=str,
        metavar='STR',
        required=True,
        help="string name of the phabricator instance, [_a-zA-Z0-9]+")

    parser.add_argument(
        '--instance-uri',
        type=str,
        metavar='ADDRESS',
        required=True,
        help="URI to use to access the conduit API, e.g. "
             "'http://127.0.0.1/api/'.")

    parser.add_argument(
        '--arcyd-user',
        type=str,
        metavar='USERNAME',
        required=True,
        help="username of admin account registered for arcyd to use.")

    parser.add_argument(
        '--arcyd-cert',
        metavar="CERT",
        type=str,
        required=True,
        help="Phabricator Conduit API certificate to use, this is the "
        "value that you will find in your user account in Phabricator "
        "at: http://your.server.example/settings/panel/conduit/. "
        "It can also be found in ~/.arcrc.")

    parser.add_argument(
        '--https-proxy',
        type=str,
        default=None,
        metavar='ADDRESS',
        help="(OPTIONAL) proxy URI for arcyd to use when connecting to "
             "conduit to https.")

    parser.add_argument(
        '--review-url-format',
        type=str,
        metavar='STRING',
        required=True,
        help="a format string for generating URLs for viewing reviews, e.g. "
             "something like this: "
             "'http://my.phabricator/D{review}' , "
             "note that the {review} will be substituted for the id of the "
             "branch.")

    parser.add_argument(
        '--admin-emails',
        nargs='*',
        metavar="TO",
        type=str,
        help="list of email addresses to send important repo events to")


def process(args):

    fs = abdt_fs.make_default_accessor()

    # make sure we can connect with those parameters
    conduit = phlsys_conduit.Conduit(
        args.instance_uri,
        args.arcyd_user,
        args.arcyd_cert,
        https_proxy=args.https_proxy)
    conduit.ping()

    content = _CONFIG.format(
        instance_uri=args.instance_uri,
        arcyd_user=args.arcyd_user,
        arcyd_cert=args.arcyd_cert,
        review_url_format=args.review_url_format)

    if args.https_proxy:
        content = '\n'.join([
            content,
            _CONFIG_HTTPS_PROXY.format(
                https_proxy=args.https_proxy)])

    if args.admin_emails:
        content = '\n'.join([
            content,
            _CONFIG_ADMIN_EMAILS_FORMAT.format(
                admin_emails='\n'.join(args.admin_emails))])

    with fs.lockfile_context():
        fs.create_phabricator_config(args.name, content)


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
