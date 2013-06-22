"""Wrapper to integrate with Arcanist's ~/.arcrc file"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
#
# Public Functions:
#   find_arcrc
#   load
#   get_arcrc
#   get_host
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import json
import os.path

import phlsys_conduit


def find_arcrc():
    home = os.path.expanduser("~")
    path = os.path.join(home, ".arcrc")
    if os.path.isfile(path):
        return path
    return None


def load(path):
    with open(path) as f:
        return json.load(f)


def get_arcrc():
    return load(find_arcrc())


def get_host(arcrc, host):
    normalised = phlsys_conduit.make_conduit_uri(host)
    return arcrc["hosts"].get(normalised, None)


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
