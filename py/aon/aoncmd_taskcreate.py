"""Create a new task in maniphest.

you can use the 'task id' output from this command as input to the
'arcyon task-update' command.

usage examples:
    create a new task with just a title:
    $ arcyon task-create 'title'
    99

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_taskcreate
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlcon_maniphest
import phlsys_makeconduit

import aont_conduitargs


def getFromfilePrefixChars():
    return ""


def setupParser(parser):

    parser.add_argument(
        'title',
        metavar='STRING',
        help='the title of the task',
        type=str)

    aont_conduitargs.addArguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(args.uri, args.user, args.cert)
    result = phlcon_maniphest.create_task(conduit, args.title)
    print result.uri


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
