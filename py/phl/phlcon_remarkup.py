"""Helpers to easily generate properly formatted remarkup."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_remarkup
#
# Public Functions:
#   code_block
#   dict_to_table
#   encased
#   bold
#   italic
#   monospaced
#   deleted
#   link
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def code_block(message, lang=None, name=None, lines=None, isBad=False):
    """Return a string code block.

    Note that the code block should start on a new line and will insert
    a blank line at the start and end of itself.  If there is already a
    preceeding blank line then the block will not display correctly.

    e.g. good:
        "hello\\n" + code_block("goodbye")

    e.g. bad:
        "hello" + code_block("goodbye")

    e.g. bad:
        "hello\\n\\n" + code_block("goodbye")

    >>> code_block("hello")
    '\\n```hello```\\n\\n'

    :message: the string to be formatted as a code block
    :lang: language that the code block is in, e.g. 'text', 'html'
    :name: name of the file the block represents
    :lines: number of lines to limit the viewport to (will have scrollbars)
    :isBad: whether to format the snippet as a 'counter example'
    :returns: string of the new wrapped code block

    """
    block = "\n```"

    attributes = []
    if lang is not None:
        attributes.append("lang=" + lang)
    if name is not None:
        attributes.append("name=" + name)
    if lines is not None:
        attributes.append("lines=" + str(int(lines)))
    if isBad:
        attributes.append("counterexample")

    if attributes:
        block += ', '.join(attributes) + "\n"

    block += message + "```\n\n"

    return block


def dict_to_table(dictionary):
    """Return a string table from the supplied dictionary.

    Note that the table should start on a new line and will insert a blank
    line at the start of itself and at the end.

    e.g. good:
        "hello\n" + dict_to_table({"a": "b"})

    e.g. bad:
        "hello" + dict_to_table({"a": "b"})

    >>> dict_to_table({"a": "b"})
    '\\n| **a** | b |\\n\\n'

    >>> dict_to_table({})
    ''

    :dictionary: the string to be formatted as a code block
    :returns: string of the new wrapped code block

    """
    block = ""
    if dictionary:
        block = "\n"

        for (key, value) in dictionary.iteritems():
            block += "| **" + str(key) + "** | " + str(value) + " |\n"

        block += "\n"

    return block


def encased(message, marker):
    """Return string 'message' encased in specified marker at both ends.

    >>> encased("hello", "**")
    '**hello**'

    :message: the string to be encased
    :marker: the string to encase with
    :returns: 'message' encased in markers

    """
    return marker + message + marker


def bold(message):
    """Return string 'message' encased in bold markers.

    >>> bold("hello")
    '**hello**'

    :message: the string to be encased
    :returns: 'message' encased in bold markers

    """
    return encased(message, "**")


def italic(message):
    """Return string 'message' encased in italic markers.

    >>> italic("hello")
    '//hello//'

    :message: the string to be encased
    :returns: 'message' encased in italic markers

    """
    return encased(message, "//")


def monospaced(message):
    """Return string 'message' encased in monospace markers.

    >>> monospaced("hello")
    '`hello`'

    :message: the string to be encased
    :returns: 'message' encased in monospace markers

    """
    return encased(message, "`")


def deleted(message):
    """Return string 'message' encased in deleted markers.

    >>> deleted("hello")
    '~~hello~~'

    :message: the string to be encased
    :returns: 'message' encased in deleted markers

    """
    return encased(message, "~~")


def link(url):
    """Return 'url' explicitly remarked up as a link.

    >>> link("http://server.test/")
    '[[http://server.test/]]'

    :url: the string to be remarked up
    :returns: 'url' encased in appropriate remarkup

    """
    return "[[{url}]]".format(url=url)


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
