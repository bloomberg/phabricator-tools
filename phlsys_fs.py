#!/usr/bin/env python
# encoding: utf-8
"""Helpers for interacting with the filesystem."""

from contextlib import contextmanager
import os
import sys
import tempfile


#TODO: write a docstring with doctests when we have a tempdir helper
@contextmanager
def chDirContext(newDir):
    savedPath = os.getcwd()
    os.chdir(newDir)
    try:
        yield
    finally:
        os.chdir(savedPath)


@contextmanager
def tmpfile(tmp_dir=None, suffix=''):
    "Create & remove tmp file"
    dir = tmp_dir or os.getenv('TMPDIR', '/tmp')
    tmp_file = tempfile.NamedTemporaryFile(dir=dir, suffix=suffix)
    yield tmp_file
    tmp_file.close()


@contextmanager
def nostd(err=True):
    "Suppress stderr or stdout"
    class Devnull(object):
        def write(self, s):
            self.out = s
    if err:
        savestd = sys.stderr
        sys.stderr = Devnull()
        yield sys.stderr
        sys.stderr = savestd
    else:
        savestd = sys.stdout
        sys.stdout = Devnull()
        yield sys.stdout
        sys.stdout = savestd


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
