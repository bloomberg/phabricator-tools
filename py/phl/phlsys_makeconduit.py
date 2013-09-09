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
#   make_conduit
#   get_uri_user_cert_explanation
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import difflib

import phlsys_arcconfig
import phlsys_arcrc
import phlsys_conduit


class InsufficientInfoException(Exception):

    def __init__(self, message):
        super(InsufficientInfoException, self).__init__(message)


def _make_exception(*args):
    return InsufficientInfoException("\n" + "\n\n".join(args))


def make_conduit(uri=None, user=None, cert=None):
    uri, user, cert, _ = get_uri_user_cert_explanation(uri, user, cert)
    return phlsys_conduit.Conduit(uri, user, cert)


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
                    "  cert: {1}".format(arcrc_path, cert[:16] + '...'))
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
                "  cert: {1}".format(arcrc_path, cert[:16] + '...'))
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
        explanations.append("changed uri:\n{0}".format(diff))
    return uri


#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
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
#------------------------------- END-OF-FILE ----------------------------------
