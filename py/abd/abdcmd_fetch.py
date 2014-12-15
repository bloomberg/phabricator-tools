"""Fetch managed repos.

This can be useful if you are switching from one arcyd instance to
another, to 'pre-fetch' before actually moving over.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_fetch
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import
from __future__ import print_function

import sys

import phlgitx_refcache
import phlsys_git
import phlsys_pid
import phlurl_watcher

import abdi_processrepoarglist
import abdi_repoargs
import abdt_fs
import abdt_git


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    pass


def process(args):

    _ = args  # NOQA
    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():
        pid = fs.get_pid_or_none()
        if pid is not None and phlsys_pid.is_running(pid):
            raise Exception("cannot fetch whilst arcyd is running.")

        repo_config_path_list = fs.repo_config_path_list()
        repo_name_config_list = abdi_repoargs.parse_config_file_list(
            repo_config_path_list)

        url_watcher_wrapper = phlurl_watcher.FileCacheWatcherWrapper(
            fs.layout.urlwatcher_cache_path)

        # Let the user know what's happening before potentially blocking for a
        # while.
        print('Refreshing repository snoop status ..', end=' ')
        # Make sure that the output is actually visible by flushing stdout
        # XXX: Will use 'flush' parameter to 'print()' in Python 3.3
        sys.stdout.flush()
        print("done")

        url_watcher_wrapper.watcher.refresh()

        for repo_name, repo_config in repo_name_config_list:
            print(repo_name + ' ..', end=' ')

            # Make sure that the output is actually visible by flushing stdout
            # XXX: Will use 'flush' parameter to 'print()' in Python 3.3
            sys.stdout.flush()

            snoop_url = abdi_repoargs.get_repo_snoop_url(repo_config)

            sys_repo = phlsys_git.Repo(repo_config.repo_path)
            refcache_repo = phlgitx_refcache.Repo(sys_repo)
            abd_repo = abdt_git.Repo(
                refcache_repo,
                "origin",
                repo_config.repo_desc)

            did_fetch = abdi_processrepoarglist.fetch_if_needed(
                url_watcher_wrapper.watcher,
                snoop_url,
                abd_repo,
                repo_config.repo_desc)

            if did_fetch:
                print('fetched')
            else:
                print('skipped')

            url_watcher_wrapper.save()


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
