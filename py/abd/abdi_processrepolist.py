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

import argparse
import functools
import os
import sys

import phlsys_scheduleunreliables
import phlsys_strtotime
import phlurl_watcher

import abdt_exhandlers

import abdi_operation
import abdi_processrepoargs
import abdi_repoargs


def do(
        repo_configs,
        sys_admin_emails,
        kill_file,
        reset_file,
        pause_file,
        sleep_secs,
        is_no_loop,
        reporter):

    repos = _repos_from_configs(repo_configs)

    # TODO: test write access to repos here

    operations = []
    conduits = {}
    url_watcher = phlurl_watcher.Watcher()

    urlwatcher_cache_path = os.path.abspath('.arcyd.urlwatcher.cache')

    # load the url watcher cache (if any)
    if os.path.isfile(urlwatcher_cache_path):
        with open(urlwatcher_cache_path) as f:
            url_watcher.load(f)

    _append_operations_for_repos(
        operations,
        reporter,
        conduits,
        url_watcher,
        urlwatcher_cache_path,
        sys_admin_emails,
        repos)

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
            conduits, url_watcher, reporter))

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


def _repos_from_configs(repo_configs):
    repos = []

    for repo in repo_configs:
        parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
        abdi_repoargs.setup_parser(parser)
        repo_name = repo[0]  # oddly this comes to us as a list
        repo_name = repo_name[1:]  # strip off the '@' prefix
        repo_name = repo_name.split('/')[-1]  # strip off the path prefix
        repo_args = (repo_name, parser.parse_args(repo))
        abdi_repoargs.validate_args(repo_args[1])
        repos.append(repo_args)

    return repos


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
        url_watcher,
        urlwatcher_cache_path,
        sys_admin_emails,
        repos):

    strToTime = phlsys_strtotime.duration_string_to_time_delta
    retry_delays = [strToTime(d) for d in ["10 minutes", "1 hours"]]

    for repo_name, repo_args in repos:

        # create a function to update this particular repo.
        #
        # use partial to ensure we capture the value of the variables,
        # note that a closure would use the latest value of the variables
        # rather than the value at declaration time.
        process_func = functools.partial(
            _process_single_repo,
            repo_name,
            repo_args,
            reporter,
            conduits,
            url_watcher,
            urlwatcher_cache_path)

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
        repo_name,
        repo_args,
        reporter,
        conduits,
        url_watcher,
        urlwatcher_cache_path):
    abdi_processrepoargs.do(
        repo_name, repo_args, reporter, conduits, url_watcher)

    # save the urlwatcher cache
    with open(urlwatcher_cache_path, 'w') as f:
        url_watcher.dump(f)


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
