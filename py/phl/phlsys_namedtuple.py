"""Wrapper around collections.namedtuple with some added features.

The 'collections.namedtuple' is very useful as a data transfer object,
when communicating with Phabricator it's important to consider that the
schema for the objects can change on the server side before we get a chance
to update our client.

This namedtuple aims to build a layer of tolerance on top of namedtuple such
that the client can continue to function when the schema changes within defined
parameters.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
#
# Public Classes:
#   Error
#
# Public Functions:
#   make_named_tuple
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import collections
import warnings


class Error(Exception):
    pass


def make_named_tuple(name, required, defaults, ignored):
    """Return a factory function for collection.namedtuple objects which uses
    the supplied 'required', 'defaults' and 'ignored' parameters to determine
    what the attributes of the namedtuple should be.

    All items from the supplied 'required' list must be provided in each
    call to the factory function.

    Keys from the specified 'defaults' dict may or may not be provided
    in calls to the returned factory function, for those that are not
    provided then the values are taken from the corresponding keys in the
    'defaults' dict.

    Items from the specified 'ignored' list are removed from the keyword
    arguments provided to the factory function prior to constructing the
    namedtuple.

    If items are encountered which are not mentioned by 'required', 'defaults'
    or 'ignored' then they are automatically ignored and a warnings.warn is
    emitted.

    Usage Examples:

        Create a factory which requires 'number' and returns 'MyTuple's:
        >>> factory = make_named_tuple("MyTuple", ['number'], {}, [])
        >>> factory(number=1)
        MyTuple(number=1)

        Create a factory which ignores 'number' returns 'MyTuple's:
        >>> factory = make_named_tuple("MyTuple", [], {}, ['number'])
        >>> factory(number=1)
        MyTuple()

        Create a factory which defaults 'number' to 2 and returns 'MyTuple's:
        >>> factory = make_named_tuple("MyTuple", [], {'number': 2}, [])
        >>> factory()
        MyTuple(number=2)

    :name: string name of the collections.namedtuple
    :required: list of keys required to be supplied to the factory function
    :defaults: dict of default values to be filled in by the factory function
    :ignored: list of keys for the factory function to ignore
    :returns: factory function which returns a collections.namedtuple

    """
    required_attr = set(required)
    default_attr = dict(defaults)
    default_attr_keys = default_attr.viewkeys()
    ignored_attr = set(ignored)
    expected_attr = required_attr | default_attr_keys
    assert not (default_attr_keys & required_attr)
    assert not (default_attr_keys & ignored_attr)
    assert not (ignored_attr & required_attr)
    NamedTuple = collections.namedtuple(name, required + defaults.keys())

    # define the factory function
    def make_instance(**kwargs):
        keys = kwargs.viewkeys()

        # remove all ignored_attr from kwargs
        ignored_keys = keys & ignored_attr
        for key in ignored_keys:
            del kwargs[key]

        # emit warnings and proceed if we encounter unexpeced attributes
        unexpected = keys - expected_attr
        if unexpected:
            warnings.warn("ignoring unexpected args: " + str(unexpected))
            for key in unexpected:
                del kwargs[key]

        missing_attr = required_attr - keys
        if missing_attr:
            raise Error("missing attributes: " + str(missing_attr))

        auto_attr = default_attr_keys - keys
        for a in auto_attr:
            kwargs[a] = default_attr[a]

        return NamedTuple(**kwargs)

    return make_instance


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
