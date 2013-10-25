"""Operations for maintaining a list of landed branches in upstream repo."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_landinglog
#
# Public Functions:
#   prepend
#   get_log
#   write_log
#   push_log
#
# Public Assignments:
#   LogItem
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections

import phlgit_hashobject
import phlgit_push
import phlgit_revparse
import phlgit_show

_LANDINGLOG_REF = 'refs/arcyd/landinglog'
_MAX_LOG_LENGTH = 1000

# we may want to support multiple remotes with distinct landing logs at some
# point, try not to make that too hard by at least reserving an 'origin'
# namespace
_LOCAL_LANDINGLOG_REF = 'refs/arcyd/origin/landinglog'


LogItem = collections.namedtuple(
    'abdt_landinglog__LogItem',
    ['review_sha1', 'name', 'landed_sha1'])


def prepend(clone, review_sha1, name, landed_sha1):
    """Prepend the specified 'sha1' and 'name' to the landinglog.

    If the list is longer than the global max then truncate it.

    :clone: supports clone.call() for interacting with git
    :sha1: string of the sha1 to prepend
    :name: string name of the ref to prepend
    :returns: None

    """
    log = get_log(clone)
    log.insert(0, LogItem(review_sha1, name, landed_sha1))
    write_log(clone, log)


def _get_log_raw(clone):
    """Return the raw contents of the landinglog from the supplied 'clone'.

    If there is no landinglog then return an empty string.

    :clone: supports clone.call() for interacting with git
    :returns: the contents of the landinglog from the supplied 'clone'

    """
    result = ""
    if phlgit_revparse.get_sha1_or_none(clone, _LOCAL_LANDINGLOG_REF):
        result = phlgit_show.object_(clone, _LOCAL_LANDINGLOG_REF)
    return result


def _write_log_raw(clone, log):
    """Overwrite the landinglog with the string 'log'.

    :clone: supports clone.call() for interacting with git
    :log: the new string contents of the landinglog
    :returns: None

    """
    sha1 = phlgit_hashobject.write_string(clone, log)
    clone.call('update-ref', _LOCAL_LANDINGLOG_REF, sha1)


def get_log(clone):
    """Return a list of LogItem from the landinglog of 'clone'.

    Behaviour is undefined if there is no log.

    :clone: supports clone.call() for interacting with git
    :returns: a list of LogItem from the landinglog of 'clone'

    """
    # restrict reading to the first 3 fields in case we later add more fields.
    log = [LogItem(*l.split()[:3]) for l in _get_log_raw(clone).splitlines()]
    return log


def write_log(clone, log):
    """Overwrite the landinglog with the supplied iterable of LogItem.

    Will truncate the log to _MAX_LOG_LENGTH entries.

    :clone: supports clone.call() for interacting with git
    :log: the iterable to write to the landing log, each entry is a LogItem
    :returns: None

    """
    log = log[:_MAX_LOG_LENGTH]
    _write_log_raw(
        clone, '\n'.join((' '.join(i) for i in log)))


def push_log(clone, remote):
    """Push the local landinglog to the specified 'remote'.

    :clone: supports clone.call() for interacting with git
    :remote: the string name of the remote to push to
    :returns: None

    """
    phlgit_push.push_asymmetrical_force(
        clone, _LOCAL_LANDINGLOG_REF, _LANDINGLOG_REF, remote)


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
