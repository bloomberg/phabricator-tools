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

import json
import logging
import os
import threading
import time

import phlsys_git
import phlsys_subprocess
import phlsys_timer
import phlurl_watcher

import abdt_errident
import abdt_exhandlers
import abdt_fs
import abdt_git
import abdt_tryloop

import abdi_processrepoargs


_LOGGER = logging.getLogger(__name__)


class _WorkerManager(object):

    def __init__(self):
        self._workers = []

    def add(self, worker):
        self._workers.append(worker)
        worker.start()

    def join_all(self):
        for w in self._workers:
            w.join()
        self._workers = []


def do(
        repo_configs,
        sys_admin_emails,
        kill_file,
        sleep_secs,
        is_no_loop,
        external_report_command,
        mail_sender):

    args = (
        repo_configs,
        sys_admin_emails,
        kill_file,
        sleep_secs,
        is_no_loop,
        external_report_command,
        mail_sender
    )

    # TODO: Although this basically works for one worker thread, when we add
    # more we'll encounter problems with sharing resources. We'll need to
    # consider at least the following:
    #
    # - logging to files
    # - sharing git snoop url cache
    # - conduits, allowing multiple connections at once
    # - limit max connections to git hosts
    #
    manager = _WorkerManager()
    manager.add(
        threading.Thread(target=_worker, args=args))
    manager.join_all()


class _ArcydManagedRepository(object):

    def __init__(
            self,
            repo_name,
            repo_args,
            conduits,
            url_watcher_wrapper,
            sys_admin_emails,
            mail_sender):

        self._is_disabled = False
        self._abd_repo = abdt_git.Repo(
            phlsys_git.Repo(repo_args.repo_path),
            "origin",
            repo_args.repo_desc)
        self._name = repo_name
        self._args = repo_args
        self._conduits = conduits
        self._url_watcher_wrapper = url_watcher_wrapper
        self._mail_sender = mail_sender
        self._on_exception = abdt_exhandlers.make_exception_delay_handler(
            sys_admin_emails, repo_name)

    def __call__(self):
        if self._is_disabled:
            return

        try:
            abdi_processrepoargs.do(
                self._abd_repo,
                self._name,
                self._args,
                self._conduits,
                self._url_watcher_wrapper.watcher,
                self._mail_sender)
        except Exception:
            self._on_exception(None)
            self._is_disabled = True

        self._url_watcher_wrapper.save()


def _worker(
        repo_configs,
        sys_admin_emails,
        kill_file,
        sleep_secs,
        is_no_loop,
        external_report_command,
        mail_sender):

    # TODO: test write access to repos here

    conduits = {}

    fs_accessor = abdt_fs.make_default_accessor()
    url_watcher_wrapper = phlurl_watcher.FileCacheWatcherWrapper(
        fs_accessor.layout.urlwatcher_cache_path)

    finished = False

    repos = []
    for name, config in repo_configs:
        repos.append(
            _ArcydManagedRepository(
                name,
                config,
                conduits,
                url_watcher_wrapper,
                sys_admin_emails,
                mail_sender))

    while not finished:
        timer = phlsys_timer.Timer()

        # refresh git snoops
        abdt_tryloop.critical_tryloop(
            url_watcher_wrapper.watcher.refresh,
            abdt_errident.GIT_SNOOP,
            '')

        # refresh conduits
        for key in conduits:
            conduit = conduits[key]
            abdt_tryloop.critical_tryloop(
                conduit.refresh_cache_on_cycle,
                abdt_errident.CONDUIT_REFRESH,
                conduit.describe())

        # process repos
        for r in repos:
            r()

        # report cycle stats
        if external_report_command:
            report = {
                "cycle_time_secs": timer.restart(),
            }
            report_json = json.dumps(report)
            full_path = os.path.abspath(external_report_command)
            try:
                phlsys_subprocess.run(full_path, stdin=report_json)
            except phlsys_subprocess.CalledProcessError as e:
                _LOGGER.error("CycleReportJson: {}".format(e))

        # look for killfile
        if os.path.isfile(kill_file):
            os.remove(kill_file)
            finished = True
            break

        if is_no_loop:
            finished = True
            break

        # sleep
        time.sleep(sleep_secs)


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
