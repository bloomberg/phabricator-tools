"""Configure repos to ignore ident strings, overrule '.gitattributes'.

For non-interactive uses of Git repositories, it can be undesirable to allow
the 'ident string' functionality as there are some edge-cases that may require
manual intervention.

Provide support for writing the repo-global '.git/info/attributes' file such
that any enabling of 'ident strings' via '.gitattributes' files will be
ignored.

Note that this should have no effect on diffs or commits, it only affects the
content of files in the work tree.  This content should not be relevant for
static inspection of the source but would be relevant for other uses, e.g.
automated builds.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitx_ignoreident
#
# Public Functions:
#   is_repo_definitely_ignoring
#   ensure_repo_ignoring
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import os

import phlsys_fs


_REPO_ATTRIBUTES_PATH = '.git/info/attributes'
_REPO_ATTRIBUTES_CONTENT = '* -ident\n'


def is_repo_definitely_ignoring(repo_path):
    repo_attributes_path = os.path.join(repo_path, _REPO_ATTRIBUTES_PATH)
    if not os.path.exists(repo_attributes_path):
        return False
    else:
        # check the existing file
        content = phlsys_fs.read_text_file(repo_attributes_path)
        return content == _REPO_ATTRIBUTES_CONTENT


def ensure_repo_ignoring(repo_path):
    if is_repo_definitely_ignoring(repo_path):
        # nothing to do
        return

    repo_attributes_path = os.path.join(repo_path, _REPO_ATTRIBUTES_PATH)
    if not os.path.exists(repo_attributes_path):
        # create the file with required content
        phlsys_fs.write_text_file(
            repo_attributes_path,
            _REPO_ATTRIBUTES_CONTENT)
    else:
        # we won't try to do any sort of merging, just escalate
        raise Exception(
            "cannot ensure ignore ident in existing file: {}".format(
                repo_attributes_path))


# -----------------------------------------------------------------------------
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
# ------------------------------ END-OF-FILE ----------------------------------
