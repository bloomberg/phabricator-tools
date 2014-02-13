"""Arcyd-specific interactions with the filesystem."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_fs
#
# Public Classes:
#   Layout
#   Accessor
#    .set_pid
#    .get_pid_or_none
#
# Public Functions:
#   make_default_accessor
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import os

import phlsys_fs


class Layout(object):

    arcydroot = '.arcydroot'
    pid = 'var/run/arcyd.pid'


class Accessor(object):

    def __init__(self, layout, path):
        self._layout = layout
        self._root = os.path.abspath(path)

        self._check_arcydroot()

    def _make_abspath(self, relative_path):
        """Return a string of the absolute path to the file in the layout.

        :relative_path: a string of the path relative to .arcydroot
        :returns: a string of the absolute path

        """
        return os.path.join(self._root, relative_path)

    def _check_arcydroot(self):
        arcydroot_path = self._make_abspath(self._layout.arcydroot)
        if not os.path.exists(arcydroot_path):
            raise Exception('did not find {}'.format(
                self._layout.arcydroot))

    def set_pid(self, pid):
        """Set the pid for the current arcyd instance.

        :pid: the integer pid of the current arcyd instance
        :returns: None

        """
        pid_path = self._make_abspath(self._layout.pid)
        phlsys_fs.write_text_file(pid_path, str(pid))

    def get_pid_or_none(self):
        """Return the pid for the current arcyd instance.

        :returns: the integer pid of the current arcyd instance or None

        """
        pid = None
        pid_path = self._make_abspath(self._layout.pid)
        if os.path.isfile(pid_path):
            with open(pid_path) as f:
                pid = int(f.read())

        return pid


def make_default_accessor():
    """Return an Accessor for the current directory, using Layout.

    :returns: a new Accessor

    """
    return Accessor(Layout(), '.')


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
