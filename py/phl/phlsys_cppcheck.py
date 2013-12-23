"""Run the external tool 'cppcheck' and process results."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_cppcheck
#
# Public Classes:
#   Error
#
# Public Functions:
#   run
#   parse_output
#   result_to_str
#   summarize_results
#
# Public Assignments:
#   Result
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections
import xml.etree.ElementTree

import phlsys_fs
import phlsys_subprocess


Result = collections.namedtuple(
    'phlsys_cppcheck__Result',
    ['severity', 'id', 'path', 'line_numbers', 'message'])


class Error(Exception):
    pass


def run(dir_path):
    """Return errors from running cppcheck in supplied 'dir_path'.

    :dir_path: string of the path to the directory to run in
    :returns: list of Result

    """
    with phlsys_fs.chdir_context(dir_path):
        # XXX: handle the "couldn't find files" exception
        return parse_output(phlsys_subprocess.run(
            'cppcheck', '-q', '.', '--xml', '--xml-version=2').stderr.strip())


def parse_output(output):
    """Return a list of Result from the supplied 'output'.

    :output: string of the output from cppcheck
    :returns: list of Result

    """
    results = []
    root = xml.etree.ElementTree.fromstring(output)
    error_list = root.find('errors')

    if error_list is not None:
        for error in error_list.iterfind('error'):
            path = None
            line_numbers = []
            message = error.get('verbose')
            severity = error.get('severity')
            identity = error.get('id')

            for line in error.iterfind('location'):
                path = line.get('file')
                line_numbers.append(int(line.get('line')))

            if message is None:
                raise Error('could not find message: {}'.format(error.items()))
            if severity is None:
                raise Error(
                    'could not find severity: {}'.format(error.items()))
            if identity is None:
                raise Error(
                    'could not find identity: {}'.format(error.items()))
            if path is None:
                # oddly this happens with the 'toomanyconfigs' error type
                # we'll continue without adding it in this case
                continue

            results.append(
                Result(severity, identity, path, line_numbers, message))

    return results


def result_to_str(result):
    """Return a string based on the attributes of the supplied Result.

    Usage example:
        >>> result_to_str(Result('error', 'nullPointer', 'my.cpp', [1], 'bad'))
        'my.cpp (1): (error) nullPointer - bad'

    :error: an Result, probably from parse_output()
    :returns: a string

    """
    return "{} ({}): ({}) {} - {}".format(
        result.path,
        ', '.join([str(i) for i in result.line_numbers]),
        result.severity,
        result.id,
        result.message)


def summarize_results(result_list):
    """Return a string summary of the supplied list of Result.

    :result_list: a list of Result, probably from parse_output()
    :returns: a string

    """
    return "\n".join((result_to_str(x) for x in result_list))


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
