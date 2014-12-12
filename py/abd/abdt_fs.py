"""Arcyd-specific interactions with the filesystem."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_fs
#
# Public Classes:
#   Error
#   Layout
#    .phabricator_config
#    .repohost_config
#    .repo_config
#    .repo_try
#    .repo_ok
#    .repo
#   Accessor
#    .set_pid
#    .get_pid_or_none
#    .create_root_config
#    .create_phabricator_config
#    .get_phabricator_config_rel_path
#    .create_repohost_config
#    .get_repohost_config_rel_path
#    .create_repo_config
#    .remove_repo_config
#    .repo_name_list
#    .repo_config_path_list
#    .lockfile_context
#    .layout
#
# Public Functions:
#   make_default_accessor
#   initialise_here
#   raise_if_config_name_not_valid
#   is_config_name_valid
#
# Public Assignments:
#   CONFIG_NAME_REGEX
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import os
import re

import phlgit_commit
import phlgit_diffindex
import phlsys_fs
import phlsys_git
import phlsys_subprocess


# Restrict the names that may be used for config files for repos, phab
# instances, repo hosts. The names may be used in URLs and filenames, err on
# the side of caution when allowing characters.
#
# Only allow lowercase names so that we don't get tripped up by
# case-insensitive file systems.
#
# Check that all the characters are either dash, underscore, lowercase a-z or
# numbers 0-9.  Require a match against the whole string (^$).
#
CONFIG_NAME_REGEX = '^[_a-z0-9-]+$'

_README = """
This is an Arcyd repository.

Run 'arcyd --help' for options.
""".strip()

_CONFIG_README = """
In this directory all the configuration is stored, from which all other
run-time data may be generated.

It is important that this directory is preserved and versioned so that it's
possible to see when and why things were changed.
""".strip()

_CONFIG_PHABRICATOR_README = """
In this directory all the phabricator instance configuration is stored.

It is important that this directory is preserved and versioned so that it's
possible to see when and why things were changed.
""".strip()

_CONFIG_REPOSITORY_README = """
In this directory all the repository configuration is stored.

It is important that this directory is preserved and versioned so that it's
possible to see when and why things were changed.
""".strip()

_VAR_README = """
In this directory all the repositories, logs and other run-time generated data
is stored.

It is safe to clean this directory when Arcyd is not running, you should save
any logs that you'd like to keep beforehand of course.

This is really a stand-in for using '/var' on the machine, this makes it
convenient to run arcyd where it can't be installed as root whilst keeping it
conceivable to move to a packaged install process later.
""".strip()

_VAR_REPO_README = """
This is where Arcyd keeps all the local clones of repositories that it is
managing.
""".strip()

_VAR_LOG_README = """
This is where Arcyd keeps all activity logs.
""".strip()

_VAR_STATUS_README = """
This is where Arcyd keeps all status information.
""".strip()

_VAR_COMMAND_README = """
This is where Arcyd looks for command files, e.g. to pause or stop.
""".strip()

_VAR_RUN_README = """
This is where Arcyd puts it's pidfile.
""".strip()


class Error(Exception):
    pass


class Layout(object):

    arcydroot = '.arcydroot'
    root_config = 'configfile'
    pid = 'var/run/arcyd.pid'
    stdout = 'var/log/stdout'
    stderr = 'var/log/stderr'
    log_debug = 'var/log/debug'
    log_info = 'var/log/info'
    log_remote_io_reads = 'var/log/remote_io_reads'
    phabricator_config_dir = 'config/repository'
    repository_config_dir = 'config/repository'
    urlwatcher_cache_path = '.arcyd.urlwatcher.cache'
    lockfile = 'var/lockfile'

    dir_run = 'var/run'

    @staticmethod
    def phabricator_config(name):
        """Return the string path to the phabricator config 'name'.

        :name: string name of the new config, see CONFIG_NAME_REGEX
        :returns: the string relative path of the new file

        """
        return 'config/phabricator/{}'.format(name)

    @staticmethod
    def repohost_config(name):
        """Return the string path to the repohost config 'name'.

        :name: string name of the new config, see CONFIG_NAME_REGEX
        :returns: the string relative path of the new file

        """
        return 'config/repohost/{}'.format(name)

    @staticmethod
    def repo_config(name):
        """Return the string path to the repo config 'name'.

        :name: string name of the new config, see CONFIG_NAME_REGEX
        :returns: the string relative path of the new file

        """
        return 'config/repository/{}'.format(name)

    @staticmethod
    def repo_try(name):
        """Return the string path to the 'try' file for the repo."""
        return "var/status/{}.try".format(name)

    @staticmethod
    def repo_ok(name):
        """Return the string path to the 'ok' file for the repo."""
        return "var/status/{}.ok".format(name)

    @staticmethod
    def repo(name):
        """Return the string path to repo 'name'."""
        return "var/repo/{}".format(name)


class Accessor(object):

    def __init__(self, layout, path):
        self._layout = layout
        self._root = os.path.abspath(path)
        self._repo = phlsys_git.Repo(path)

        self._check_arcydroot()

    def _make_abspath(self, relative_path):
        """Return a string of the absolute path to the file in the layout.

        :relative_path: a string of the path relative to .arcydroot
        :returns: a string of the absolute path

        """
        return os.path.join(self._root, relative_path)

    def _check_arcydroot(self):
        arcydroot_path = self._make_abspath(self._layout.arcydroot)
        if not os.path.exists(arcydroot_path):
            raise Exception('did not find {}'.format(
                self._layout.arcydroot))

    def set_pid(self, pid):
        """Set the pid for the current arcyd instance.

        :pid: the integer pid of the current arcyd instance
        :returns: None

        """
        pid_path = self._make_abspath(self._layout.pid)
        phlsys_fs.write_text_file(pid_path, str(pid))

    def get_pid_or_none(self):
        """Return the pid for the current arcyd instance.

        :returns: the integer pid of the current arcyd instance or None

        """
        pid = None
        pid_path = self._make_abspath(self._layout.pid)
        if os.path.isfile(pid_path):
            with open(pid_path) as f:
                pid = int(f.read())

        return pid

    def _create_config(self, rel_path, content, message):
        """Create and commit a new config file.

        :rel_path: the string relative path to the config file
        :content: the string contents of the new config file
        :message: the string commit message for the file

        """
        if phlgit_diffindex.is_index_dirty(self._repo):
            raise Error("git index has staged changes")

        path = self._make_abspath(rel_path)

        if os.path.exists(path):
            raise Error("config already exists")

        phlsys_fs.write_text_file(path, content)
        self._repo('add', rel_path)
        phlgit_commit.index(self._repo, message)

    def _remove_config(self, rel_path, message):
        """Remove and commit the removal of an existing config file.

        :rel_path: the string relative path to the config file
        :message: the string commit message for the file

        """
        if phlgit_diffindex.is_index_dirty(self._repo):
            raise Error("git index has staged changes")

        path = self._make_abspath(rel_path)

        if not os.path.exists(path):
            raise Error("config doesn't exist: {}".format(rel_path))

        self._repo('rm', rel_path)
        phlgit_commit.index(self._repo, message)

    def create_root_config(self, content):
        """Create and commit the root config file.

        :content: the string content of the new config file
        :returns: None

        """
        rel_path = self._layout.root_config
        self._create_config(rel_path, content, 'Create root config')

    def create_phabricator_config(self, name, content):
        """Create a new phabricator config file.

        :name: string name of the new config, see CONFIG_NAME_REGEX
        :content: the string content of the new config file
        :returns: None

        """
        raise_if_config_name_not_valid(name)
        rel_path = self._layout.phabricator_config(name)
        self._create_config(
            rel_path, content, 'Add phabricator config: {}'.format(name))

    def get_phabricator_config_rel_path(self, name):
        """Return the string path for the phabricator config 'name'.

        Raise Exception if the config does not exist.

        :name: string name of the config, see CONFIG_NAME_REGEX
        :returns: None

        """
        rel_path = self._layout.phabricator_config(name)
        path = self._make_abspath(rel_path)

        if not os.path.isfile(path):
            raise Exception('{} has no phabricator config'.format(name))

        return rel_path

    def create_repohost_config(self, name, content):
        """Create a new repohost config file.

        :name: string name of the new config, see CONFIG_NAME_REGEX
        :content: the string content of the new config file
        :returns: None

        """
        raise_if_config_name_not_valid(name)
        rel_path = self._layout.repohost_config(name)
        self._create_config(
            rel_path, content, 'Add repohost config: {}'.format(name))

    def get_repohost_config_rel_path(self, name):
        """Return the string path for the repohost config 'name'.

        Raise Exception if the config does not exist.

        :name: string name of the config, see CONFIG_NAME_REGEX
        :returns: None

        """
        rel_path = self._layout.repohost_config(name)
        path = self._make_abspath(rel_path)

        if not os.path.isfile(path):
            raise Exception('{} has no repohost config'.format(name))

        return rel_path

    def create_repo_config(self, name, content):
        """Create a new repo config file.

        :name: string name of the new config, see CONFIG_NAME_REGEX
        :content: the string content of the new config file
        :returns: None

        """
        raise_if_config_name_not_valid(name)
        rel_path = self._layout.repo_config(name)
        self._create_config(
            rel_path, content, 'Add repo config: {}'.format(name))

    def remove_repo_config(self, name):
        """Remove an existing repo config file.

        :name: string name of the existing config, see CONFIG_NAME_REGEX
        :returns: None

        """
        rel_path = self._layout.repo_config(name)
        self._remove_config(
            rel_path, 'Remove repo config: {}'.format(name))

    def repo_name_list(self):
        """Return a list of string names of managed repositories.

        :returns: list of string

        """
        p = self.layout.repository_config_dir
        return [r for r in os.listdir(p) if r != 'README']

    def repo_config_path_list(self):
        """Return a list of string paths to repo configs.

        :returns: list of string

        """
        p = self.layout.repository_config_dir
        return [os.path.join(p, r) for r in os.listdir(p) if r != 'README']

    @contextlib.contextmanager
    def lockfile_context(self):
        retry_context = phlsys_fs.lockfile_retry_context
        with retry_context(self.layout.lockfile, attempts=3, wait_secs=1):
            yield
        # TODO: raise some 'usage error' if the lockfile can't be acquired

    @property
    def layout(self):
        return self._layout


def make_default_accessor():
    """Return an Accessor for the current directory, using Layout.

    :returns: a new Accessor

    """
    return Accessor(Layout(), '.')


def initialise_here():
    """Return a new default Accessor after initialising the current directory.

    :returns: a new Accessor, mounted at the current directory

    """
    layout = Layout()

    phlsys_subprocess.run('git', 'init')
    repo = phlsys_git.Repo('.')

    # create filesystem hierarchy
    phlsys_fs.write_text_file(layout.arcydroot, 'this dir is an arcydroot')
    phlsys_fs.write_text_file('README', _README)
    phlsys_fs.write_text_file('config/README', _CONFIG_README)
    phlsys_fs.write_text_file(
        'config/phabricator/README', _CONFIG_PHABRICATOR_README)
    phlsys_fs.write_text_file(
        'config/repository/README', _CONFIG_REPOSITORY_README)
    phlsys_fs.write_text_file('var/README', _VAR_README)
    phlsys_fs.write_text_file('var/repo/README', _VAR_REPO_README)
    phlsys_fs.write_text_file('var/log/README', _VAR_LOG_README)
    phlsys_fs.write_text_file('var/status/README', _VAR_STATUS_README)
    phlsys_fs.write_text_file('var/command/README', _VAR_COMMAND_README)
    phlsys_fs.write_text_file('var/run/README', _VAR_RUN_README)

    repo('add', '.')
    phlsys_fs.write_text_file('.gitignore', 'var\n')
    repo('add', '.')
    phlgit_commit.index(repo, 'Initialised new Arcyd instance')

    return Accessor(Layout(), '.')


def raise_if_config_name_not_valid(name):
    """Raise an appropriate error if the supplied 'name' is not valid.

    :name: a string candidate config name
    :returns: None

    """
    # XXX: We could add some helpful hints as to why it's not valid in the
    #      error message.
    if not is_config_name_valid(name):
        raise Error("config name is invalid: {}".format(name))


def is_config_name_valid(name):
    """Return True if 'name' is valid for a config, False otherwise.

    Usage examples:
        >>> is_config_name_valid('my_phabricator99')
        True
        >>> is_config_name_valid('My_phabricator99')
        False
        >>> is_config_name_valid('my-phabricator99')
        True
        >>> is_config_name_valid('my_phabricator.99')
        False

    :name: a string candidate config name
    :returns: True or False

    """
    return re.match(CONFIG_NAME_REGEX, name) is not None


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
