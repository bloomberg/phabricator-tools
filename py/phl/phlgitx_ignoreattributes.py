"""Configure repos to ignore some attributes, overruling '.gitattributes'.

For non-interactive uses of Git repositories, it can be undesirable to allow
the 'ident string' and other attribute functionality as there are some
edge-cases that may require manual intervention.

Provide support for writing the repo-global '.git/info/attributes' file such
that any enabling of 'ident strings' and some other features via
'.gitattributes' files will be ignored.

Note that this should have no effect on diffs or commits, it only affects the
content of files in the work tree.  This content should not be relevant for
static inspection of the source but would be relevant for other uses, e.g.
automated builds.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitx_ignoreattributes
#
# Public Functions:
#   is_repo_definitely_ignoring
#   ensure_repo_ignoring
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function

import os

import phlsys_fs


_REPO_ATTRIBUTES_PATH = '.git/info/attributes'
_REPO_ATTRIBUTES_IDENT_CONTENT = '* -ident\n'
_REPO_ATTRIBUTES_EOL_CONTENT = '* -eol\n'
_REPO_ATTRIBUTES_TUPLE = (
    _REPO_ATTRIBUTES_IDENT_CONTENT,
    _REPO_ATTRIBUTES_EOL_CONTENT
)
_REPO_ATTRIBUTES_CONTENT = "".join(_REPO_ATTRIBUTES_TUPLE)


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
        contents = phlsys_fs.read_text_file(repo_attributes_path)
        if contents in _REPO_ATTRIBUTES_TUPLE:
            # the file is exactly one of the existing attributes, we can merge
            # correctly by overwriting it with our superset of attributes
            phlsys_fs.write_text_file(
                repo_attributes_path,
                _REPO_ATTRIBUTES_CONTENT)
        else:
            # we won't try to do any sort of merging, just escalate
            raise Exception(
                "cannot ensure ignore attributes in existing file: {}".format(
                    repo_attributes_path))


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
