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
# phlsys_namedtuple
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

from __future__ import absolute_import

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
