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
from __future__ import division
from __future__ import print_function

import phlsys_conduit
import phlsys_makeconduit

import abdi_repoargs
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
        help="string name of the phabricator instance, {regex}".format(
            regex=abdt_fs.CONFIG_NAME_REGEX))

    abdi_repoargs.setup_phab_parser(parser)

    parser.add_argument(
        '--admin-emails',
        nargs='*',
        metavar="TO",
        type=str,
        help="list of email addresses to send important repo events to")


def process(args):

    fs = abdt_fs.make_default_accessor()

    # make sure we can connect with those parameters
    uri, user, cert, _ = phlsys_makeconduit.get_uri_user_cert_explanation(
        args.instance_uri, args.arcyd_user, args.arcyd_cert)
    conduit = phlsys_conduit.Conduit(
        uri, user, cert, https_proxy=args.https_proxy)
    conduit.ping()

    content = _CONFIG.format(
        instance_uri=uri,
        arcyd_user=user,
        arcyd_cert=cert,
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
# Copyright (C) 2014-2015 Bloomberg Finance L.P.
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
