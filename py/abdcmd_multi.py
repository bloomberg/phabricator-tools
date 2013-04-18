#!/usr/bin/env python
# encoding: utf-8

"""Command to process multiple repos."""

import argparse
import time

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
    parser.add_argument(
        '--sleep-secs',
        metavar="TIME",
        type=int,
        default=60,
        help="time to wait between runs through the list")


def process(args):
    repos = list()
    for repo in args.repo_configs:
        # TODO: we should not depend on another command like this
        parser = argparse.ArgumentParser(
            fromfile_prefix_chars=abdcmd_single.getFromfilePrefixChars())
        abdcmd_single.setupParser(parser)
        repo_args = parser.parse_args(repo)
        repos.append(repo_args)

    out = phlsys_statusline.StatusLine()

    while True:
        for repo in repos:
            abdi_processargs.run_once(repo, out)

        sleep_remaining = args.sleep_secs
        while sleep_remaining > 0:
            out.display("sleep (" + str(sleep_remaining) + " seconds) ")
            time.sleep(1)
            sleep_remaining -= 1


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
