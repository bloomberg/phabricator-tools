"""Operations involving commit messages and ParseCOmmitMessageFields."""

import collections
import types


def _isIterable(x):
    return isinstance(x, collections.Iterable)


def _isString(x):
    return isinstance(x, types.StringTypes)


def _isIterableNotString(x):
    return _isIterable(x) and not _isString(x)


def _merge(x, y):
    if x is None and y is not None:
        return y

    if y is None and x is not None:
        return x

    if x == y:
        return x

    if _isString(x) and _isString(y):
        return x + y

    if _isIterableNotString(x) and _isIterableNotString(y):
        return list(set(x) | set(y))

    raise ValueError("can't merge: " + str(x) + " and " + str(y))


def _copyValues(x, y, keys):
    for k in keys:
        x[k] = y[k]


# see
# .../differential/field/selector/DifferentialDefaultFieldSelector.php
def update(earlier, later):
    """Return an merged 'CommitMessageFields' based on the 'earlier' version.

    Apply the 'later' version as an update to the 'earlier' one.

    If either the earlier or later are None then the non-None one is returned.

    :earlier: a dictionary of message fields
    :later: a dictionary of message fields
    :returns: the merged dictionary of message fields

    """

    if earlier is None and later is not None:
        return later

    if earlier is not None and later is None:
        return earlier

    earlier_keys = set(earlier.keys())
    later_keys = set(later.keys())

    merged = {}
    _copyValues(merged, earlier_keys, earlier_keys.difference(later_keys))
    _copyValues(merged, later_keys, later_keys.difference(earlier_keys))

    conflict_keys = earlier_keys.intersection(later_keys)

    if "title" in conflict_keys:
        merged["title"] = earlier["title"]
        conflict_keys.remove("title")

    for k in conflict_keys:
        merged[k] = _merge(earlier[k], later[k])

    return merged


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
