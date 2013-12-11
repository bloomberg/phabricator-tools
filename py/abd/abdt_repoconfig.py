"""Per-repository configuration options."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_repoconfig
#
# Public Classes:
#   Data
#
# Public Functions:
#   merge_override_into_data
#   merge_data_objects
#   make_default_data
#   data_from_json
#   json_from_data
#   validate_data
#   data_from_repo_or_none
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import copy
import json

import phlgit_show
import phlgit_showref


class Data(object):

    def __init__(self):
        super(Data, self).__init__()
        self.description = None
        self.branch_url_format = None
        self.review_url_format = None
        self.admin_emails = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


def _merge_lists_as_sets(*list_list):
    # sets aren't serializable as json so we want to store as list
    new_set = set()
    for l in list_list:
        if l is not None:
            new_set |= set(l)
    return list(new_set)


def merge_override_into_data(default, override):
    """Return the result of overriding the non-None keys of 'override'.

    :default: the lower precedence Data
    :override: the higher precedence Data
    :returns: the higher precedence Data

    """
    # first create a copy of default, use deepcopy() for future-proofing
    result = copy.deepcopy(default)

    string_keys = [
        "description",
        "branch_url_format",
        "review_url_format",
    ]

    list_keys = [
        "admin_emails",
    ]

    assert set(string_keys + list_keys) == set(Data().__dict__.keys())

    for key, value in override.__dict__.iteritems():
        if value is not None:
            if key in string_keys:
                setattr(result, key, value)
            else:  # it's a list attribute
                assert key in list_keys
                if key in result.__dict__:
                    left = getattr(result, key)
                    right = getattr(override, key)
                    setattr(result, key, _merge_lists_as_sets(left, right))
                else:
                    setattr(result, key, value)

    return result


def merge_data_objects(*data_list):
    """Merge many Data objects, precedence increases with index in the list.

    if an item in the list is None then it is ignored.

    :object_list: multiple Data() args
    :returns: a Data() that represents the composite of all the configs

    """
    result = data_list[0]
    data_list = data_list[1:]
    for data in data_list:
        if data is not None:
            result = merge_override_into_data(result, data)
    return result


def make_default_data():
    """Returns a 'Data' with sensible default values.

    :returns: a 'Data'

    """
    data = Data()
    data.description = "(unnamed repo)"
    return data


def data_from_json(json_string):
    """Returns a 'Data' from the supplied 'json_string'.

    The 'json_string' doesn't have to mention all the attributes of Data, it
    must not mention attributes that don't exist in Data already.

    :json_string: a string of the json data
    :returns: a abdt_repoconfig.Data based on 'json_string'

    """
    data = Data()
    for key, value in json.loads(json_string).iteritems():
        getattr(data, key)  # raise if the attribute doesn't already exist
        setattr(data, key, value)
    return data


def json_from_data(data):
    """Returns a json string from the supplied 'data'.

    :data: a abdt_repoconfig.Data to encode as json
    :returns: a json string based on 'data'

    """
    return json.dumps(
        data,
        default=lambda x: x.__dict__,
        sort_keys=True,
        indent=4)


def validate_data(data):
    """Raise if the supplied data is invalid in any way.

    :data: a Data() to be validated
    :returns: None

    """

    # make sure that 'data' has the same attributes as a blank data
    data_key_set = set(data.__dict__.keys())
    blank_data_key_set = set(Data().__dict__.keys())
    if data_key_set != blank_data_key_set:
        if data_key_set.issubset(blank_data_key_set):
            raise Exception(
                "supplied 'data' is missing fields: {fields}".format(
                    fields=list(blank_data_key_set - data_key_set)))
        elif data_key_set.issuperset(blank_data_key_set):
            raise Exception(
                "supplied 'data' has extra fields: {fields}".format(
                    fields=list(data_key_set - blank_data_key_set)))
        else:
            raise Exception(
                "supplied 'data' is missing or gained: {fields}".format(
                    fields=list(data_key_set ^ blank_data_key_set)))

    if data.branch_url_format is not None:
        branch = 'blahbranch'
        data.branch_url_format.format(branch=branch)

    if data.review_url_format is not None:
        review = 123
        data.review_url_format.format(review=review)


def data_from_repo_or_none(repo):
    """Returns a valid 'Data' if 'repo' has a config file.

    Will raise if the config file could not be parsed.

    Will return 'None' if no config file was found.

    :repo: a git repo object that supports call()
    :returns: a valid 'Data' or None

    """
    config = None

    # try to get the file content from the special ref, if it exists
    ref = 'refs/config/origin/arcyd'
    if ref in phlgit_showref.names(repo):
        try:
            config = phlgit_show.file_on_ref(
                repo, 'repo.json', ref)
        except Exception:
            pass

    if config is not None:
        config = data_from_json(config)

    return config


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
