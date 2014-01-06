"""Wrapper to integrate with Arcanist's .arcconfig file."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_arcconfig
#
# Public Functions:
#   find_arcconfig
#   load
#   get_arcconfig
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json
import os


def _parent_dir(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def find_arcconfig():
    path = None
    nextpath = os.getcwd()
    while path != nextpath:
        path, nextpath = nextpath, _parent_dir(nextpath)
        config_path = os.path.join(path, ".arcconfig")
        if os.path.isfile(config_path):
            return config_path
    return None


def load(path):
    with open(path) as f:
        return json.load(f)


def get_arcconfig():
    return load(find_arcconfig())


#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
