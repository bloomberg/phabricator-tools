"""Arcyd-specific interactions with the filesystem."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_fs
#
# Public Classes:
#   Layout
#    .phabricator_config
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
#    .create_repo_config
#    .layout
#
# Public Functions:
#   make_default_accessor
#   initialise_here
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import os

import phlgit_commit
import phlsys_fs
import phlsys_git
import phlsys_subprocess


_README = """
This is an Arcyd repository.

Run 'arcyd --help' for options.
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


class Layout(object):

    arcydroot = '.arcydroot'
    root_config = 'config'
    pid = 'var/run/arcyd.pid'

    dir_run = 'var/run'

    @staticmethod
    def phabricator_config(name):
        """Return the string path to the phabricator config 'name'.

        :name: string name of the new config [a-zA-Z0-9_]
        :returns: the string relative path of the new file

        """
        return 'phabricator-{}.config'.format(name)

    @staticmethod
    def repo_config(name):
        """Return the string path to the repo config 'name'.

        :name: string name of the new config [a-zA-Z0-9_]
        :returns: the string relative path of the new file

        """
        return 'repo-{}.config'.format(name)

    @staticmethod
    def repo_try(name):
        """Return the string path to the 'try' file for the repo."""
        return "var/status/repo-{}.config.try".format(name)

    @staticmethod
    def repo_ok(name):
        """Return the string path to the 'ok' file for the repo."""
        return "var/status/repo-{}.config.ok".format(name)

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
        """Create and commit the a new config file.

        :rel_path: the string relative path to the config file
        :content: the string contents of the new config file
        :message: the string commit message for the file

        """
        path = self._make_abspath(rel_path)

        if os.path.exists(path):
            raise Exception("config already exists")

        phlsys_fs.write_text_file(path, content)
        self._repo.call('add', rel_path)
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

        :name: string name of the new config [a-zA-Z0-9_]
        :content: the string content of the new config file
        :returns: None

        """
        rel_path = self._layout.phabricator_config(name)
        self._create_config(
            rel_path, content, 'Add phabricator config: {}'.format(name))

    def get_phabricator_config_rel_path(self, name):
        """Return the string path for the phabricator config 'name'.

        Raise Exception if the config does not exist.

        :name: string name of the config [a-zA-Z0-9_]
        :returns: None

        """
        rel_path = self._layout.phabricator_config(name)
        path = self._make_abspath(rel_path)

        if not os.path.isfile(path):
            raise Exception('{} has no phabricator config'.format(name))

        return rel_path

    def create_repo_config(self, name, content):
        """Create a new repo config file.

        :name: string name of the new config [a-zA-Z0-9_]
        :content: the string content of the new config file
        :returns: None

        """
        rel_path = self._layout.repo_config(name)
        self._create_config(
            rel_path, content, 'Add repo config: {}'.format(name))

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
    phlsys_fs.write_text_file('var/README', _VAR_README)
    phlsys_fs.write_text_file('var/repo/README', _VAR_REPO_README)
    phlsys_fs.write_text_file('var/log/README', _VAR_LOG_README)
    phlsys_fs.write_text_file('var/status/README', _VAR_STATUS_README)
    phlsys_fs.write_text_file('var/command/README', _VAR_COMMAND_README)
    phlsys_fs.write_text_file('var/run/README', _VAR_RUN_README)

    repo.call('add', '.')
    phlsys_fs.write_text_file('.gitignore', 'var\n')
    repo.call('add', '.')
    phlgit_commit.index(repo, 'Initialised new Arcyd instance')

    return Accessor(Layout(), '.')


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
