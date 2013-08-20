"""Command to process multiple repos without looping."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_multionce
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import argparse

import abdcmd_single
import abdi_processargs
import phlsys_statusline


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--repo-configs',
        metavar="N",
        action='append',
        nargs='+',
        type=str,
        help="files to load configuration from, prefix with @")


def process(args, retry_delays, on_exception_delay):
    _ = retry_delays, on_exception_delay  # NOQA
    outputter = phlsys_statusline.StatusLine()

    # TODO: don't depend on another command in this way
    parser = argparse.ArgumentParser(
        fromfile_prefix_chars=abdcmd_single.getFromfilePrefixChars())
    abdcmd_single.setupParser(parser)

    for config_file in args.repo_configs:
        repo_args = parser.parse_args(config_file)
        abdi_processargs.run_once(repo_args, outputter)


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
