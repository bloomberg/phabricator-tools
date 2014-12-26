"""Create a conduit from the available information.

Can try to examine './.arcconfig' and '~/.arcrc' if not enough
information is provided.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_makeconduit
#
# Public Classes:
#   InsufficientInfoException
#
# Public Functions:
#   add_argparse_arguments
#   make_conduit
#   obscured_cert
#   get_uri_user_cert_explanation
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import difflib

import phlsys_arcconfig
import phlsys_arcrc
import phlsys_conduit


class InsufficientInfoException(Exception):

    def __init__(self, message):
        super(InsufficientInfoException, self).__init__(message)


def _make_exception(*args):
    return InsufficientInfoException("\n" + "\n\n".join(args))


def add_argparse_arguments(parser):
    """Add a 'connection arguments' group to the supplied argparse.parser."""

    connection = parser.add_argument_group(
        'connection arguments',
        'use these optional parameters to override settings present in your\n'
        '"~/.arcrc" or ".arcconfig" files')

    connection.add_argument(
        "--uri",
        type=str,
        metavar="ADDRESS",
        help="address of the phabricator instance to connect to.")

    connection.add_argument(
        "--user",
        type=str,
        metavar="NAME",
        help="name of the user to connect as.")

    connection.add_argument(
        "--cert",
        type=str,
        metavar="HEX",
        help="long certificate string of the user to connect as, you can find "
             "this string here: "
             "http://your.phabricator/settings/panel/conduit/. generally you "
             "wouldn't expect to enter this on the command-line and would "
             "make an ~/.arcrc file by using '$ arc install-certificate'.")

    connection.add_argument(
        '--act-as-user',
        type=str,
        metavar="NAME",
        help="name of the user to impersonate (admin only).\n")


def make_conduit(uri=None, user=None, cert=None, act_as_user=None):
    uri, user, cert, _ = get_uri_user_cert_explanation(uri, user, cert)
    return phlsys_conduit.Conduit(uri, user, cert, act_as_user)


def obscured_cert(cert):
    """Return an obscured version of the supplied 'cert' suitable for display.

    :cert: a string of a conduit certificate
    :returns: a string of an obscured conduit certificate

    """
    return cert[:4] + '...' + cert[-4:]


def get_uri_user_cert_explanation(uri, user, cert):
    if uri and user and cert:
        explanations = ["all parameters were supplied"]
        uri = _fix_uri(explanations, uri)
        return uri, user, cert, '\n\n'.join(explanations)

    arcrc, arcrc_path = _load_arcrc()
    arcconfig_path, arcconfig = _load_arcconfig()

    install_arc_url = str(
        "http://www.phabricator.com/docs/phabricator/article/"
        "Arcanist_User_Guide.html#installing-arcanist")

    no_uri = "no uri to a Phabricator instance was specified."
    no_user = "no username for the Phabricator instance was specified."
    no_cert = "no certificate for the Phabricator instance was specified."
    no_arcconfig = (
        "couldn't find an .arcconfig, this file should contain "
        "the uri for the phabricator instance you wish to connect "
        "to.\n"
        "we search for it in the current working directory and in "
        "the parent directories\n"
        "here is an example .arcconfig:\n"
        "{\n"
        "    \"conduit_uri\" : \"https://your.phabricator/\"\n"
        "}")
    no_arcrc = (
        "couldn't find ~/.arcrc, this file should contain "
        "usernames and certificates which will allow us to authenticate with "
        "Phabricator.\n"
        "To generate a valid ~/.arcrc for a particular instance, you may "
        "run:\n"
        "\n"
        "$ arc install-certificate [URI]\n"
        "N.B. to install arc:\n" + install_arc_url)
    bad_arcrc = (
        "can't load .arcrc, it may be invalid json or not permissioned\n"
        "path used: " + str(arcrc_path))
    bad_arcconfig = (
        "can't load .arcconfig, it may be invalid json or not permissioned\n"
        "path used: " + str(arcconfig_path))
    arcrc_no_default = (
        "no default uri was discovered in .arcrc, you may add one like so:\n"
        "$ arc set-config default https://your.phabricator/\n"
        "N.B. to install arc:\n" + install_arc_url)
    arcconfig_no_uri = (
        ".arcconfig doesn't seem to contain a conduit_uri entry\n"
        "path used: " + str(arcconfig_path))

    explanations = []

    # try to discover conduit uri first
    if uri is None:
        if not arcconfig_path:
            if not arcrc_path:
                raise _make_exception(no_uri, no_arcconfig, no_arcrc)
            if arcrc is None:
                raise _make_exception(no_uri, no_arcconfig, bad_arcrc)
            if "config" in arcrc:
                uri = arcrc["config"].get("default", None)
            if uri is None:
                raise _make_exception(no_uri, no_arcconfig, arcrc_no_default)
            explanations.append(
                "got uri from 'default' entry in arcrc\n"
                "  path: {0}\n"
                "  uri: {1}".format(arcrc_path, uri))
        else:  # if arcconfig_path
            if arcconfig is None:
                raise _make_exception(no_uri, bad_arcconfig)
            uri = arcconfig.get("conduit_uri", None)
            if uri is None:
                raise _make_exception(no_uri, arcconfig_no_uri)
            explanations.append(
                "got uri from .arcconfig\n"
                "  path: {0}\n"
                "  uri: {1}".format(arcconfig_path, uri))

    uri = _fix_uri(explanations, uri)

    arcrc_no_entry = (
        "no entry for the uri was found in .arcrc, you may add one like so:\n"
        "$ arc install-certificate " + uri + "\n"
        "N.B. to install arc:\n" + install_arc_url)

    # try to discover user
    if user is None:
        if not arcrc_path:
            raise _make_exception(no_user, no_arcrc)
        if arcrc is None:
            raise _make_exception(no_user, bad_arcrc)
        if "hosts" in arcrc:
            host = phlsys_arcrc.get_host(arcrc, uri)
            if host is None:
                raise _make_exception(no_user, arcrc_no_entry)
            user = host.get("user", None)
            explanations.append(
                "got user from uri's entry in .arcrc\n"
                "  path: {0}\n"
                "  user: {1}".format(arcrc_path, user))
            if cert is None:
                cert = host.get("cert", None)
                explanations.append(
                    "got cert from uri's entry in .arcrc\n"
                    "  path: {0}\n"
                    "  cert: {1}".format(arcrc_path, obscured_cert(cert)))
            if user is None:
                raise _make_exception(no_user, arcrc_no_entry)
        if user is None:
            raise _make_exception(no_user, arcrc_no_entry)

    # try to discover cert
    if cert is None:
        if not arcrc_path:
            raise _make_exception(no_cert, no_arcrc)
        if arcrc is None:
            raise _make_exception(no_cert, bad_arcrc)
        if "hosts" in arcrc:
            host = phlsys_arcrc.get_host(arcrc, uri)
            if host is None:
                raise _make_exception(no_cert, arcrc_no_entry)
            cert = host.get("cert", None)
            explanations.append(
                "got cert from uri's entry in .arcrc\n"
                "  path: {0}\n"
                "  cert: {1}".format(arcrc_path, obscured_cert(cert)))
        if cert is None:
            raise _make_exception(no_cert, arcrc_no_entry)

    # make a generic statement if we've missed an error case
    if not (uri and user and cert) or arcrc_path is None:
        raise Exception("unexpected error determinining uri, user or cert")

    return uri, user, cert, '\n\n'.join(explanations)


def _load_arcconfig():
    # try to load arcconfig, if we can find it
    arcconfig_path = phlsys_arcconfig.find_arcconfig()
    arcconfig = None
    try:
        if arcconfig_path is not None:
            arcconfig = phlsys_arcconfig.load(arcconfig_path)
    except ValueError:
        pass
    except EnvironmentError:
        pass
    return arcconfig_path, arcconfig


def _load_arcrc():
    # try to load arcrc, if we can find it
    arcrc_path = phlsys_arcrc.find_arcrc()
    arcrc = None
    try:
        if arcrc_path is not None:
            arcrc = phlsys_arcrc.load(arcrc_path)
    except ValueError:
        pass
    except EnvironmentError:
        pass
    return arcrc, arcrc_path


def _fix_uri(explanations, uri):
    old_uri = uri
    uri = phlsys_conduit.make_conduit_uri(uri)
    if uri != old_uri:
        diff = list(difflib.Differ().compare([old_uri], [uri]))
        diff = ['  ' + s.strip() for s in diff]
        diff = '\n'.join(diff)
        explanations.append("assumed uri to conduit:\n{0}".format(diff))
    return uri


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
