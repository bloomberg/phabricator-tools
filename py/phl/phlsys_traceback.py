"""Emit enhanced traceback strings with local variables."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_traceback
#
# Public Functions:
#   excepthook
#   format_exc
#   format_tb
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function

import cStringIO
import contextlib
import sys

# useful ref for traceback stuff:
# http://doughellmann.com/2012/04/
#                          determining-the-name-of-a-process-from-python-2.html
# http://code.activestate.com/recipes/
#                                   52215-get-more-information-from-tracebacks/


def excepthook(type, value, traceback):
    """Replacement for sys.excepthook, prints extra information.

    Can be installed like so:
        >>> sys.excepthook = excepthook

    """
    sys.__excepthook__(type, value, traceback)
    print()
    print(format_tb(traceback))


def format_exc():
    """Return a string containing traceback for the current exception.

    Similar to traceback.format_exc, returns a string with the traceback of the
    current exception.  This traceback also includes local variables however.

    :returns: string traceback of current exception

    """
    tb = sys.exc_info()[2]
    return format_tb(tb)


def format_tb(tb):
    """Return a string containing traceback for the supplied traceback.

    Similar to traceback.format_tb, returns a string with the traceback of the
    current exception.  This traceback also includes local variables however.

    :returns: string traceback of supplied traceback

    """

    # fill in the stack
    stack = []
    while tb.tb_next:
        tb = tb.tb_next
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()

    result = ""
    with contextlib.closing(cStringIO.StringIO()) as s:
        print("Extended traceback (most recent call last):", file=s)
        for frame in stack:
            print(file=s)
            print(
                "File \"{filename}\", line {line}, in '{frame}'".format(
                    frame=frame.f_code.co_name,
                    filename=frame.f_code.co_filename,
                    line=frame.f_lineno),
                file=s)
            for key, value in frame.f_locals.items():
                print("{0:>15} = ".format(key), end='', file=s)
                try:
                    print(value, file=s)
                except:
                    print("!! exception while printing !!", file=s)

        # unfortunately pychecker doesn't like the getvalue() call and thinks
        # it doesn't exist, we also have to ask pyflakes to ignore the
        # pychecker directive
        __pychecker__ = "no-objattr"  # NOQA
        result = s.getvalue()
    return result

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
