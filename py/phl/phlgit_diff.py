"""Wrapper around 'git diff'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_diff
#
# Public Functions:
#   raw_diff_range_to_here
#   raw_diff_range
#   no_index
#   create_add_file
#   stat_range
#   parse_filenames_from_raw_diff
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

import phlsys_fs
import phlsys_subprocess


def raw_diff_range_to_here(repo, start):
    return repo("diff", start + "...", "-M")


def raw_diff_range(repo, base, new, context_lines=None):
    """Return a raw diff from the history on 'new' that is not on 'base'.

    Note that commits that are cherry-picked from new to old will still appear
    in the diff, this function operates using the commit graph only.

    Raise if git returns a non-zero exit code.

    :repo: a callable supporting git commands, e.g. repo("status")
    :base: the base branch
    :new: the branch with new commits
    :returns: a string of the raw diff

    """
    args = [
        "diff",
        base + "..." + new,
        "-M",  # automatically detect moves/renames
    ]

    if context_lines:
        args.append("--unified=" + str(context_lines))

    result = repo(*args)
    return result


def no_index(left_path, right_path, working_dir=None):
    """Return a string diff between the two paths.

    :left_path: the string path of the left file to diff
    :right_path: the string path of the right file to diff
    :working_dir: the directory to perform the diff relative to
    :returns: the string diff result

    """
    diff = None
    try:
        result = phlsys_subprocess.run(
            'git',
            'diff',
            '--no-index',
            left_path,
            right_path,
            workingDir=working_dir)
        diff = result.stdout
    except phlsys_subprocess.CalledProcessError as e:
        # we expect diff --no-index to return exit codes:
        #   0 if there's no difference between the files
        #   1 if there is a difference
        #
        if e.exitcode != 1:
            raise
        diff = e.stdout

    return diff


def create_add_file(path, content):
    """Return a string diff which adds a new file with the specified content.

    Raise Exception if the is absolute, instead of relative.

    Usage examples:

        create a diff for new file 'README' with content 'hello'
        >>> print(create_add_file('README', 'hello'))
        diff --git a/README b/README
        new file mode 100644
        index 0000000..b6fc4c6
        --- /dev/null
        +++ b/README
        @@ -0,0 +1 @@
        +hello
        \ No newline at end of file
        <BLANKLINE>

    :path: the string path of the new file
    :content: the string content of the new file
    :returns: the string diff result

    """
    left = "/dev/null"  # this seems to work just the same on Windows
    right = path

    if os.path.isabs(path):
        raise Exception(
            "create_add_file: cannot create fake diff for absolute path")

    with phlsys_fs.tmpdir_context() as dir_name:

        right_full = os.path.join(dir_name, right)
        with open(right_full, "w") as f:
            f.write(content)

        diff = no_index(left, right, dir_name)

    return diff


def stat_range(repo, base, new):
    """Return a diff stat from the history on 'new' that is not on 'base'.

    Note that commits that are cherry-picked from new to old will still appear
    in the diff, this function operates using the commit graph only.

    Raise if git returns a non-zero exit code.

    :repo: a callable supporting git commands, e.g. repo("status")
    :base: the string name of the base branch
    :new: the string name of the branch with new commits
    :returns: a string of the diff stat

    """
    return repo(
        "diff",
        "--stat=80",
        base + "..." + new,
        "-M")  # automatically detect moves/renames


def parse_filenames_from_raw_diff(diff):
    matches = re.findall(
        "^diff --git a/(.*) b/(.*)$",
        diff,
        flags=re.MULTILINE)
    if matches:
        names = zip(*matches)
        if len(names) != 2:
            raise Exception(
                "files aren't pairs in diff: " +
                diff + str(names))
        # get a set of unique names from the pairs
        unames = []
        unames.extend(names[0])
        unames.extend(names[1])
        unames = set(unames)
        return unames


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
