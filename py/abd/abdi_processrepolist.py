"""Process a list of repository arguments."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_processrepolist
#
# Public Functions:
#   do
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import functools
import os
import sys

import phlsys_git
import phlsys_scheduleunreliables
import phlsys_strtotime
import phlurl_watcher

import abdt_exhandlers
import abdt_fs
import abdt_git

import abdi_operation
import abdi_processrepoargs
import abdi_repoargs


def do(
        repo_config_path_list,
        sys_admin_emails,
        kill_file,
        reset_file,
        pause_file,
        sleep_secs,
        is_no_loop,
        reporter):

    repo_configs = abdi_repoargs.parse_config_file_list(repo_config_path_list)

    # TODO: test write access to repos here

    operations = []
    conduits = {}

    fs_accessor = abdt_fs.make_default_accessor()
    url_watcher_wrapper = phlurl_watcher.FileCacheWatcherWrapper(
        fs_accessor.layout.urlwatcher_cache_path)

    # refresh cache after loading and before any repos are processed, otherwise
    # we may not pull when we need to on the first run around the loop.
    # TODO: wrap in usual retry handlers so that we can start up in unstable
    #       environments
    url_watcher_wrapper.watcher.refresh()

    _append_operations_for_repos(
        operations,
        reporter,
        conduits,
        url_watcher_wrapper,
        sys_admin_emails,
        repo_configs)

    _append_interrupt_operations(
        operations,
        sys_admin_emails,
        kill_file,
        reset_file,
        pause_file,
        sleep_secs,
        reporter)

    operations.append(
        abdi_operation.RefreshCaches(
            conduits, url_watcher_wrapper.watcher, reporter))

    _process_operations(
        is_no_loop, operations, sys_admin_emails, reporter)


def _process_operations(is_no_loop, operations, sys_admin_emails, reporter):

    on_exception_delay = abdt_exhandlers.make_exception_delay_handler(
        sys_admin_emails, reporter, None)

    if is_no_loop:
        def process_once():
            return phlsys_scheduleunreliables.process_once(list(operations))

        new_ops = _try_handle_reset_file(process_once, on_exception_delay)
        if new_ops != set(operations):
            print 'ERROR: some operations failed'
            sys.exit(1)
    else:
        def loopForever():
            phlsys_scheduleunreliables.process_loop_forever(list(operations))

        while True:
            _try_handle_reset_file(loopForever, on_exception_delay)


def _append_interrupt_operations(
        operations,
        sys_admin_emails,
        kill_file,
        reset_file,
        pause_file,
        sleep_secs,
        reporter):

    def on_pause():
        on_exception_delay = abdt_exhandlers.make_exception_delay_handler(
            sys_admin_emails, reporter, None)
        on_exception_delay("until_file_removed")

    operations.append(
        abdi_operation.CheckSpecialFiles(
            kill_file,
            reset_file,
            pause_file,
            on_pause))

    operations.append(
        abdi_operation.Sleep(
            sleep_secs, reporter))


def _append_operations_for_repos(
        operations,
        reporter,
        conduits,
        url_watcher_wrapper,
        sys_admin_emails,
        repo_configs):

    strToTime = phlsys_strtotime.duration_string_to_time_delta
    retry_delays = [strToTime(d) for d in ["10 minutes", "1 hours"]]

    for repo_name, repo_args in repo_configs:

        # create a function to update this particular repo.
        #
        # use partial to ensure we capture the value of the variables,
        # note that a closure would use the latest value of the variables
        # rather than the value at declaration time.
        abd_repo = abdt_git.Repo(
            phlsys_git.Repo(repo_args.repo_path),
            "origin",
            repo_args.repo_desc)
        process_func = functools.partial(
            _process_single_repo,
            abd_repo,
            repo_name,
            repo_args,
            reporter,
            conduits,
            url_watcher_wrapper)

        on_exception_delay = abdt_exhandlers.make_exception_delay_handler(
            sys_admin_emails, reporter, repo_name)

        operation = phlsys_scheduleunreliables.DelayedRetryNotifyOperation(
            process_func,
            list(retry_delays),  # make a copy to be sure
            on_exception_delay)

        operations.append(operation)


def _try_handle_reset_file(f, on_exception_delay):
    try:
        return f()
    except abdi_operation.ResetFileError as e:
        on_exception_delay(None)
        try:
            os.remove(e.path)
        except:
            on_exception_delay(None)


def _process_single_repo(
        abd_repo,
        repo_name,
        repo_args,
        reporter,
        conduits,
        url_watcher_wrapper):

    watcher = url_watcher_wrapper.watcher
    abdi_processrepoargs.do(
        abd_repo, repo_name, repo_args, reporter, conduits, watcher)

    # save the urlwatcher cache
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
