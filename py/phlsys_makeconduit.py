"""Create a conduit from the available information.

Can try to examine './.arcconfig' and '~/.arcrc' if not enough information is
provided.

"""

import phlsys_arcconfig
import phlsys_arcrc
import phlsys_conduit


def makeConduit():
    uri, user, cert = getUriUserCertificate()
    return phlsys_conduit.Conduit(uri, user, cert)


def getUriUserCertificate():
    arcrc = phlsys_arcrc.getArcrc()
    arcconfig = phlsys_arcconfig.getArcconfig()
    uri = arcconfig["conduit_uri"]
    uri = phlsys_conduit.makeConduitUri(uri)
    credentials = phlsys_arcrc.getHost(arcrc, uri)
    user = credentials["user"]
    cert = credentials["cert"]
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
