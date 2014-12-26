"""linterate - an automated lint excitor.

Download files from differential reviews and apply robust linters to
those files.  Where almost certain errors are detected, make inline
comments on those reviews.

This is emphatically not a stand-in for CI, more a utility for getting
developers excited about CI and showing what's possible with some of the
fantastic linters out there.

This improves on 'phlint' by adding configuration options and a memory
of what it's already covered.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# lorcmd_linterate
#
# Public Classes:
#   BoringErrorFilter
#    .filter_ignored
#   NovelFileErrorFilter
#    .filter_ignored
#    .write_seen
#   CompositeErrorFilter
#    .filter_ignored
#
# Public Functions:
#   main
#   parse_args
#   yield_revisions
#   linterate
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import collections
import datetime
import json
import os
import pickle

import phlcon_differential
import phlsys_choice
import phlsys_cppcheck
import phlsys_fs
import phlsys_makeconduit
import phlsys_subprocess


_USAGE_EXAMPLES = """
usage examples:
    linterate your default Phabricator instance
    $ linterate
"""

_LintResult = collections.namedtuple(
    'lorcmd_linterate___LintResult',
    ['path', 'start_line', 'end_line', 'message'])


def main():
    args = parse_args()
    conduit = phlsys_makeconduit.make_conduit(args.uri, args.user, args.cert)

    error_revisions = []

    novel_filter = NovelFileErrorFilter()

    error_filter = CompositeErrorFilter(
        BoringErrorFilter(),
        novel_filter)

    try:
        for revision in yield_revisions(conduit, args):

            linterate(args, conduit, revision, error_revisions, error_filter)

            # write new 'seen' errors after linterating, to give a chance for
            # the user to ctrl+c and prevent it being recorded
            #
            # it's pretty slow to write this out, we're doing it every time
            # that we've linted files we've downloaded from a webserver though,
            # so on balance it might not be so bad.
            novel_filter.write_seen()

    except phlsys_makeconduit.InsufficientInfoException as e:
        print("ERROR - insufficient information")
        print(e)
        print()
        print("N.B. you may also specify uri, user or cert directly like so:")
        print("  --uri URI           address of phabricator instance")
        print("  --user USERNAME     username of user to connect as")
        print("  --cert CERTIFICATE  certificate for user Phabrictor account")
        return 1

    if error_revisions:
        print('revisions with errors:', ' '.join(error_revisions))
    else:
        print('no revisions had errors')


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    parser.add_argument(
        '--ids', '-i',
        type=int,
        nargs='*',
        help='list of ids to linterate')

    parser.add_argument(
        '--silent',
        action="store_true",
        help='whether to print anything other than errors')

    parser.add_argument(
        '--non-interactive',
        action="store_true",
        help='suppress prompts for the user, take no action')

    phlsys_makeconduit.add_argparse_arguments(parser)

    args = parser.parse_args()

    return args


def yield_revisions(conduit, args):
    revision_list = phlcon_differential.query(conduit, args.ids)

    use_cache = not bool(args.ids)

    history = {}

    if use_cache:
        cache_filename = '.linteratecache'
        if os.path.isfile(cache_filename):
            with open(cache_filename) as cache_file:
                history = json.load(cache_file)

        # filter out revisions with nothing new
        # be careful to convert revision.id to string or it won't match history
        revision_list = filter(
            lambda x: set(history.get(x.phid, [])) != set(x.diffs),
            revision_list)

    for revision in revision_list:
        diff = phlcon_differential.get_revision_diff(conduit, revision.id)
        with phlsys_fs.chtmpdir_context() as temp_dir:
            try:
                phlcon_differential.write_diff_files(diff, temp_dir)
            except phlcon_differential.WriteDiffError as e:
                if not args.silent:
                    print('skipping revision ', revision.id, ':', e)
            else:
                yield revision

        history[revision.phid] = revision.diffs

        if use_cache:
            with open(cache_filename, 'w') as cache_file:
                json.dump(history, cache_file)


def linterate(args, conduit, revision, error_revisions, error_filter):
    if not args.silent:
        print(revision.id, revision.title)

    try:
        errors = None

        if os.path.isdir('right'):
            errors = phlsys_cppcheck.run('right')
            errors = error_filter.filter_ignored(revision, errors)

        if errors:
            if args.silent:
                print(revision.id, revision.title)

            print(phlsys_cppcheck.summarize_results(errors))
            print(revision.uri)

            error_revisions.append(str(revision.id))
            if not args.non_interactive and phlsys_choice.yes_or_no('comment'):
                print("commenting..")
                for e in errors:
                    first_line = min(e.line_numbers)
                    last_line = max(e.line_numbers)
                    line_range = last_line - first_line
                    if line_range > 10:
                        for line in e.line_numbers:
                            phlcon_differential.create_inline_comment(
                                conduit, revision.id, e.path, line, e.message)
                    else:
                        phlcon_differential.create_inline_comment(
                            conduit,
                            revision.id,
                            e.path,
                            first_line,
                            e.message,
                            line_count=line_range)

                # XXX: only leave draft inline comments for now, so the user
                #      may review them in context and manually finish the
                #      comment
                #
                # message = "LINTERATOR SEE POSSIBLE ERROR"
                # phlcon_differential.create_comment(
                #     conduit, revision.id, message, attach_inlines=True)

            print()
    except phlsys_subprocess.CalledProcessError as e:
        if not args.silent:
            print(' ', e)


class BoringErrorFilter(object):

    """Suppress errors that are uninteresting or high false +ve."""

    def __init__(self):
        super(BoringErrorFilter, self).__init__()
        self._boring_rules = [

            # must be an actual error or we're not interested
            lambda x: x.severity != 'error',

        ]

    def filter_ignored(self, revision, errors):
        _ = revision  # NOQA
        # filter out any errors that test positive for 'boring'
        rules = self._boring_rules
        return filter(lambda x: not any(f(x) for f in rules), errors)


class NovelFileErrorFilter(object):

    """Suppress errors for files that we've recently seen errors in."""

    def __init__(self):
        super(NovelFileErrorFilter, self).__init__()
        self._cache_filename = os.path.abspath('.linteratenovelcache')
        self._already_seen = {}
        self._load_seen()
        self._expire_timedelta = datetime.timedelta(days=28)

        # forget the expired things and write again
        now = datetime.datetime.utcnow()
        items = self._already_seen.iteritems()
        max_t = self._expire_timedelta
        self._already_seen = dict((k, v) for k, v in items if now - v <= max_t)
        self.write_seen()

    def filter_ignored(self, revision, errors):
        new_errors = []
        author = revision.authorPHID
        author_path_set = set()
        for e in errors:
            author_path = (author, e.path)

            # let it through if we haven't seen it before
            if author_path not in self._already_seen:
                new_errors.append(e)
                author_path_set.add(author_path)

        # record each author path and the time right now
        for author_path in author_path_set:
            self._already_seen[author_path] = datetime.datetime.utcnow()

        return new_errors

    def _load_seen(self):
        if os.path.isfile(self._cache_filename):
            with open(self._cache_filename, 'rb') as cache_file:
                self._already_seen = pickle.load(cache_file)

    def write_seen(self):
        with open(self._cache_filename, 'wb') as cache_file:
            pickle.dump(self._already_seen, cache_file)


class CompositeErrorFilter(object):

    """Combine multiple error filters into a single one."""

    def __init__(self, *args):
        super(CompositeErrorFilter, self).__init__()
        self._filters = args

    def filter_ignored(self, revision, errors):
        for f in self._filters:
            errors = f.filter_ignored(revision, errors)
        return errors


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
