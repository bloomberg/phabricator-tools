"""Create a conduit from the available information.

Can try to examine './.arcconfig' and '~/.arcrc' if not enough information is
provided.

"""

import phlsys_arcconfig
import phlsys_arcrc
import phlsys_conduit


class InsufficientInfoException(Exception):

    def __init__(self, message):
        super(InsufficientInfoException, self).__init__(message)


def _makeException(*args):
    return InsufficientInfoException("\n" + "\n\n".join(args))


def makeConduit(uri=None, user=None, cert=None):
    uri, user, cert = getUriUserCertificate(uri, user, cert)
    return phlsys_conduit.Conduit(uri, user, cert)


def getUriUserCertificate(uri, user, cert):
    if uri and user and cert:
        return uri, user, cert

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
        "$ arc install-certificate [URI]")
    bad_arcrc = (
        "can't load .arcrc, it may be invalid json or not permissioned\n"
        "path used: " + str(arcrc_path))
    bad_arcconfig = (
        "can't load .arcconfig, it may be invalid json or not permissioned\n"
        "path used: " + str(arcconfig_path))
    arcrc_no_default = (
        "no default uri was discovered in .arcrc, you may add one like so:\n"
        "$ arc set-config default https://your.phabricator/")
    arcconfig_no_uri = (
        ".arcconfig doesn't seem to contain a conduit_uri entry\n"
        "path used: " + str(arcconfig_path))

    # try to discover conduit uri first
    if uri is None:
        if not arcconfig_path:
            if not arcrc_path:
                raise _makeException(no_uri, no_arcconfig, no_arcrc)
            if arcrc is None:
                raise _makeException(no_uri, no_arcconfig, bad_arcrc)
            if "config" in arcrc:
                uri = arcrc["config"].get("default", None)
            if uri is None:
                raise _makeException(no_uri, no_arcconfig, arcrc_no_default)
        else:  # if arcconfig_path
            if arcconfig is None:
                raise _makeException(no_uri, bad_arcconfig)
            uri = arcconfig.get("conduit_uri", None)
            if uri is None:
                raise _makeException(no_uri, arcconfig_no_uri)

    uri = phlsys_conduit.makeConduitUri(uri)

    arcrc_no_entry = (
        "no entry for the uri was found in .arcrc, you may add one like so:\n"
        "$ arc install-certificate " + uri)

    # try to discover user
    if user is None:
        if not arcrc_path:
            raise _makeException(no_user, no_arcrc)
        if arcrc is None:
            raise _makeException(no_user, bad_arcrc)
        if "hosts" in arcrc:
            host = phlsys_arcrc.get_host(arcrc, uri)
            if host is None:
                raise _makeException(no_user, arcrc_no_entry)
            user = host.get("user", None)
            if cert is None:
                cert = host.get("cert", None)
            if user is None:
                raise _makeException(no_user, arcrc_no_entry)
        if user is None:
            raise _makeException(no_user, arcrc_no_entry)

    # try to discover cert
    if cert is None:
        if not arcrc_path:
            raise _makeException(no_cert, no_arcrc)
        if arcrc is None:
            raise _makeException(no_cert, bad_arcrc)
        if "hosts" in arcrc:
            host = phlsys_arcrc.get_host(arcrc, uri)
            if host is None:
                raise _makeException(no_cert, arcrc_no_entry)
            cert = host.get("cert", None)
        if cert is None:
            raise _makeException(no_cert, arcrc_no_entry)

    # make a generic statement if we've missed an error case
    if not (uri and user and cert) or arcrc_path is None:
        raise Exception("unexpected error determinining uri, user or cert")

    return uri, user, cert


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
