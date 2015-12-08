""""Automatically rewrite files with the correct legal footer."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# fixlegal
#
# Public Functions:
#   main
#   should_process_file
#   is_new_file
#   get_first_year
#   get_last_year
#   get_corrected_contents
#   divide_legal
#   make_expected_legal_text
#   make_date_range_text
#   timestamp_str_to_year
#   get_file_extension
#
# Public Assignments:
#   FileData
#   DIVIDER
#   COPYRIGHT_FORMAT
#   BLANK_LINE
#   APACHE2_LICENSE
#   END_OF_FILE
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import print_function

import argparse
import collections
import datetime
import os
import subprocess
import sys


FileData = collections.namedtuple(
    'fixlegal__FileData',
    ['path', 'last_year'])

DIVIDER = """
# -----------------------------------------------------------------------------
""".strip()

COPYRIGHT_FORMAT = "# Copyright (C) {date_range} Bloomberg Finance L.P."

BLANK_LINE = "#"

APACHE2_LICENSE = """
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
""".strip()

END_OF_FILE = """
# ------------------------------ END-OF-FILE ----------------------------------
""".strip()


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('path', type=str)
    argparser.add_argument(
        '--different-since',
        metavar='COMMIT',
        help='restrict checking to files which are different since COMMIT. '
             'a diff from COMMIT to the INDEX will be generated and the files '
             'mentioned will be considered.',
        type=str)
    args = argparser.parse_args()

    os.chdir(args.path)

    if args.different_since:
        file_list = subprocess.check_output(
            [
                'git', 'diff', args.different_since,
                '--cached',
                '--name-only'
            ]
        ).splitlines()
    else:
        file_list = subprocess.check_output(
            ['git', 'ls-tree', '-r', '--name-only', 'HEAD']).splitlines()

    file_list = filter(should_process_file, file_list)
    file_list = filter(os.path.isfile, file_list)

    for f in file_list:
        # rewrite the file if necessary
        raw = ''.join(open(f))
        new_raw = get_corrected_contents(raw, f)
        if raw != new_raw:
            with open(f, 'w') as out:
                out.write(new_raw)
            print("wrote", f)


def should_process_file(path):

    ignore_endings = [
        '.generated.txt',
        '.md',
        '.json',
    ]

    ignore_filenames = [
        '.arcconfig',
        '.gitignore',
        '.pylint.rc',
    ]

    ignore_paths = [
        '.travis.yml',
        'LICENSE',
        'meta/package_deps/expected-package-deps',
        'meta/review_states/review_states.dot',
        'testbed/arcyon/diff1',
        'testbed/arcyon/diff2',
        'testbed/linterate/hello_world.cpp',
        'testbed/linterate/hello_world_bad.cpp',
        'vagrant/Vagrantfile',
        'vagrant/puppet/phabricator/files/initial.db',
        'vagrant/puppet/phabricator/manifests/default.pp',
        'vagrant/puppet/phabricator/templates/vhost.erb',
    ]

    for i in ignore_endings:
        if path.endswith(i):
            return False

    for i in ignore_filenames:
        if os.path.basename(path) == i:
            return False

    for i in ignore_paths:
        if path == i:
            return False

    return True


def is_new_file(path):
    timestamp_str = subprocess.check_output(
        ['git', 'log', '-1', '--format=%ct', '--', path])
    return False if timestamp_str else True


def get_first_year(path):
    timestamp_str_list = subprocess.check_output([
        'git',
        'log',
        '--format=%ct',
        '--follow',
        '--find-copies=95',
        '--find-renames=80',
        path
    ])
    timestamp_str = timestamp_str_list.splitlines()[-1]
    return timestamp_str_to_year(timestamp_str)


def get_last_year(path):
    timestamp_str = subprocess.check_output(
        ['git', 'log', '-1', '--format=%ct', '--', path])
    return timestamp_str_to_year(timestamp_str)


def get_corrected_contents(contents, path):
    if is_new_file(path):
        first_year = last_year = datetime.date.today().year
    else:
        first_year = get_first_year(path)
        last_year = get_last_year(path)

    expected_legal_text = make_expected_legal_text(path, first_year, last_year)
    before_legal_text, actual_legal_text = divide_legal(contents, path)

    if actual_legal_text == expected_legal_text:
        return contents

    return before_legal_text + expected_legal_text


def divide_legal(contents, path):
    end_of_file_marker_pos = contents.rfind('\n' + END_OF_FILE)
    if -1 == end_of_file_marker_pos:
        return contents, ""

    start_of_legal_marker_pos = contents.rfind(
        '\n' + DIVIDER, 0, end_of_file_marker_pos)

    if -1 == start_of_legal_marker_pos:
        return contents, ""

    start_of_legal_marker_pos += 1  # don't eat the newline

    return (
        contents[:start_of_legal_marker_pos],
        contents[start_of_legal_marker_pos:]
    )


def make_expected_legal_text(path, first_year, last_year):
    date_range_text = make_date_range_text(first_year, last_year)
    copyright = COPYRIGHT_FORMAT.format(date_range=date_range_text)
    return '\n'.join([
        DIVIDER,
        copyright,
        BLANK_LINE,
        APACHE2_LICENSE,
        END_OF_FILE,
        ''
    ])


def make_date_range_text(first_year, last_year):
    if first_year == last_year:
        text = str(first_year)
    else:
        text = "{}-{}".format(first_year, last_year)
    return text


def timestamp_str_to_year(timestamp):
        timestamp_no_ws = timestamp.strip()
        timestamp_float = float(timestamp_no_ws)
        dt = datetime.datetime.utcfromtimestamp(timestamp_float)
        return dt.year


def get_file_extension(path):
    return os.path.splitext(path)[1].split('.')[-1].lower()


if __name__ == "__main__":
    sys.exit(main())


# -----------------------------------------------------------------------------
# Copyright (C) 2014-2015 Bloomberg Finance L.P.
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
