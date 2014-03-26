"""Fixtures for exercising scenarios with real Git."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitu_fixture
#
# Public Classes:
#   TempRepo
#    .close
#    .repo
#   Worker
#    .create_new_file
#    .add_new_file
#    .commit_new_file
#    .commit_new_file_on_new_branch
#    .append_to_file
#    .add_append_to_file
#    .commit_append_to_file
#    .append_to_file_on_new_branch
#    .checkout_master
#    .repo
#   CentralisedWithWorkers
#    .close
#    .central_repo
#    .workers
#   CentralisedWithTwoWorkers
#    .w0
#    .w1
#
# Public Functions:
#   lone_worker_context
#   temprepo_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import os
import shutil
import tempfile

import phlgit_push
import phlsys_git


@contextlib.contextmanager
def lone_worker_context():
    """Return a newly attached Worker with initial commit, close when expired.

    Usage examples:

        Create a temporary repo and attached worker:
        >>> with lone_worker_context() as worker:
        ...     content = worker.repo("show", "HEAD:README")
        ...     content is not None
        True

    """
    with temprepo_context() as repo:
        worker = Worker(repo)
        worker.commit_new_file('initial commit', 'README')
        yield worker


@contextlib.contextmanager
def temprepo_context():
    """Return a newly created phlsys_git.Repo, close when expired.

    Usage examples:

        Create a temporary repo:
        >>> with temprepo_context() as repo:
        ...     status = repo("rev-parse", "--is-inside-work-tree")
        ...     status.strip().lower() == 'true'
        True

    """
    with contextlib.closing(TempRepo()) as temp_repo:
        yield temp_repo.repo


class TempRepo(object):

    """Make a temporary repository, clean up on close().

    Usage examples:

        Create a temporary repo:
        >>> with temprepo_context() as repo:
        ...     status = repo("rev-parse", "--is-inside-work-tree")
        ...     status.strip().lower() == 'true'
        True

    """

    def __init__(self):
        super(TempRepo, self).__init__()
        self._tmp_dir = tempfile.mkdtemp()
        self._repo = phlsys_git.Repo(self._tmp_dir)
        self._repo("init")

    def close(self):
        """Free up any resources used by this instance.

        Note that you must call this function to prevent leaks, it's best to
        use the supplied 'temprepo_context' if possible to guarantee closing.

        :returns: None

        """
        shutil.rmtree(self._tmp_dir)

    @property
    def repo(self):
        return self._repo


class Worker(object):

    """Attach to a git repo and support actions that a worker might do."""

    def __init__(self, repo):
        super(Worker, self).__init__()
        self._repo = repo

    def create_new_file(self, relative_path, contents=None):
        """Create a new file in the working tree.

        :relative_path: the path of the file, relative to the repo
        :contents: the string contents of the new file
        :returns: None

        """
        path = os.path.join(
            self._repo.working_dir,
            relative_path)

        with open(path, 'w') as f:
            if contents:
                f.write(contents)

    def add_new_file(self, relative_path, contents=None):
        """Create a new file in the working tree and index.

        :relative_path: the path of the file, relative to the repo
        :contents: the string contents of the new file
        :returns: None

        """
        self.create_new_file(relative_path, contents)
        self._repo('add', relative_path)

    def commit_new_file(self, message, relative_path, contents=None):
        """Create and commit a new file.

        :message: the string content of the commit message
        :relative_path: the path of the file, relative to the repo
        :contents: the string contents of the new file
        :returns: None

        """
        self.add_new_file(relative_path, contents)
        self._repo('commit', '-m', message, '--', relative_path)

    def commit_new_file_on_new_branch(
            self, branch, message, relative_path, contents=None, base=None):
        """Checkout a new branch and create and commit a new file.

        :branch: the string name of the new branch
        :message: the string content of the commit message
        :relative_path: the path of the file, relative to the repo
        :contents: the string contents of the new file
        :base: the string name of the branch to base off of or None for HEAD
        :returns: None

        """
        base_ref = base if base is not None else 'HEAD'
        self._repo('checkout', '-b', branch, base_ref)
        self.commit_new_file(message, relative_path, contents)

    def append_to_file(self, relative_path, to_append):
        """Append to a file in the working tree.

        :relative_path: the path of the file, relative to the repo
        :to_append: the string contents to append to the file
        :returns: None

        """
        path = os.path.join(
            self._repo.working_dir,
            relative_path)

        with open(path, 'a') as f:
            f.write(to_append)

    def add_append_to_file(self, relative_path, to_append):
        """Create a new file in the working tree and index.

        :relative_path: the path of the file, relative to the repo
        :to_append: the string contents to append to the file
        :returns: None

        """
        self.append_to_file(relative_path, to_append)
        self._repo('add', relative_path)

    def commit_append_to_file(self, message, relative_path, to_append):
        """Create and commit a new file.

        :message: the string content of the commit message
        :relative_path: the path of the file, relative to the repo
        :to_append: the string contents to append to the file
        :returns: None

        """
        self.add_append_to_file(relative_path, to_append)
        self._repo('commit', '-m', message, '--', relative_path)

    def append_to_file_on_new_branch(
            self, branch, message, relative_path, to_append, base=None):
        """Checkout a new branch and commit an append to a file.

        :branch: the string name of the new branch
        :message: the string content of the commit message
        :relative_path: the path of the file, relative to the repo
        :to_append: the string contents to append to the file
        :base: the string name of the branch to base off of or None for HEAD
        :returns: None

        """
        base_ref = base if base is not None else 'HEAD'
        self._repo('checkout', '-b', branch, base_ref)
        self.commit_append_to_file(message, relative_path, to_append)

    def checkout_master(self):
        """Checkout the 'master' branch."""
        self._repo('checkout', 'master')

    @property
    def repo(self):
        return self._repo


class CentralisedWithWorkers(object):

    """Create temporary linked git repos - one central, the rest workers.

    The worker repos are set up with the central repo as origin, the first
    worker pushes an initial commit to the central repo during __init__.

    Call 'close' when done to prevent leaks.

    """

    def __init__(self, contributor_count):
        super(CentralisedWithWorkers, self).__init__()
        if contributor_count < 1:
            raise(
                Exception("contributor_count must be 1 or more, got {}".format(
                    contributor_count)))

        self._central_repo = phlsys_git.Repo(tempfile.mkdtemp())
        self._central_repo("init", "--bare")

        self._workers = []
        for i in xrange(contributor_count):
            self._workers.append(
                Worker(phlsys_git.Repo(tempfile.mkdtemp())))
            self.workers[-1].repo("init")
            self.workers[-1].repo(
                "remote", "add", "origin", self._central_repo.working_dir)
            self.workers[-1].repo("fetch")

            if i == 0:
                self.workers[0].commit_new_file('initial commit', 'README')
                phlgit_push.push(self.workers[0].repo, 'master', 'origin')

    def close(self):
        shutil.rmtree(self._central_repo.working_dir)
        for worker in self._workers:
            shutil.rmtree(worker.repo.working_dir)

    @property
    def central_repo(self):
        return self._central_repo

    @property
    def workers(self):
        return self._workers


class CentralisedWithTwoWorkers(CentralisedWithWorkers):

    """Create temporary linked git repos - one central, two workers.

    The worker repos are set up with the central repo as origin.
    Call 'close' when done to prevent leaks.

    """

    def __init__(self):
        super(CentralisedWithTwoWorkers, self).__init__(2)

    @property
    def w0(self):
        return self.workers[0]

    @property
    def w1(self):
        return self.workers[1]


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
