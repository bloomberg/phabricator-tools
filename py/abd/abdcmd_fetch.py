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

import phlsys_git
import phlurl_watcher

import abdi_processrepoargs
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

    repo_config_path_list = fs.repo_config_path_list()
    repo_name_config_list = abdi_repoargs.parse_config_file_list(
        repo_config_path_list)

    url_watcher_wrapper = phlurl_watcher.FileCacheWatcherWrapper(
        fs.layout.urlwatcher_cache_path)

    url_watcher_wrapper.watcher.refresh()

    for repo_name, repo_config in repo_name_config_list:
        print(repo_name + '..', end=' ')
        snoop_url = abdi_repoargs.get_repo_snoop_url(repo_config)

        abd_repo = abdt_git.Repo(
            phlsys_git.Repo(repo_config.repo_path),
            "origin",
            repo_config.repo_desc)

        did_fetch = abdi_processrepoargs.fetch_if_needed(
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
