"""Stop the arcyd instance for the current directory."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_stop
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

import os
import time

import phlsys_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--force',
        action='store_true',
        help="kill the process.")


def process(args):
    # check for the arcydroot file
    if not os.path.exists('.arcydroot'):
        raise Exception('did not find .arcydroot in current directory')

    if args.force:
        raise Exception('--force not implemented yet')

    killfile = 'var/command/killfile'
    phlsys_fs.write_text_file(killfile, '')

    if os.path.isfile(killfile):
        time.sleep(1)
        while os.path.isfile(killfile):
            print 'waiting for arcyd to remove killfile ..'
            time.sleep(1)


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
