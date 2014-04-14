"""Helpers for interacting with the filesystem."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_fs
#
# Public Classes:
#   LockfileExistsError
#
# Public Functions:
#   read_file_lock_context
#   write_file_lock_context
#   lockfile_context
#   chdir_context
#   tmpfile
#   tmpdir_context
#   chtmpdir_context
#   nostd
#   ensure_dir
#   write_text_file
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import fcntl
import os
import shutil
import sys
import tempfile


class LockfileExistsError(Exception):
    pass


@contextlib.contextmanager
def read_file_lock_context(filename):
    """Open 'filename' for reading and acquire a shared lock, unlock and close.

    Note that the lock is 'advisory', which means that the lock doesn't prevent
    access to the file.  The lock is merely associated with the file and will
    not be respected by other processes unless they explicitly check it.

    Usage example:

        >>> with chtmpdir_context():
        ...     with open('testfile', 'w') as f:
        ...         f.write('hello')
        ...     with read_file_lock_context('testfile') as f:
        ...         print f.read()
        hello

    """
    with open(filename, 'r') as file_object:
        fcntl.flock(file_object, fcntl.LOCK_SH)
        try:
            yield file_object
        finally:
            fcntl.flock(file_object, fcntl.LOCK_UN)


@contextlib.contextmanager
def write_file_lock_context(filename):
    """Open 'filename' for write and acquire exclusive lock, unlock and close.

    Note that the lock is 'advisory', which means that the lock doesn't prevent
    access to the file.  The lock is merely associated with the file and will
    not be respected by other processes unless they explicitly check it.

    Usage example:

        >>> with chtmpdir_context():
        ...     with write_file_lock_context('testfile') as f:
        ...         f.write('hello')
        ...     with read_file_lock_context('testfile') as f:
        ...         print f.read()
        hello

    """
    # 'touch' the file to make sure we can open it for 'r+'
    with open(filename, 'a'):
        pass

    with open(filename, 'r+') as file_object:
        fcntl.flock(file_object, fcntl.LOCK_EX)
        file_object.truncate()
        try:
            yield file_object
        finally:
            file_object.flush()
            os.fsync(file_object.fileno())
            fcntl.flock(file_object, fcntl.LOCK_UN)


@contextlib.contextmanager
def lockfile_context(filename):
    """Create 'filename' exclusively during context if poss. Fail otherwise.

    A lockfile is a file used as a mutex on the file system, to guarantee
    exclusive access to another resource.

    Manage lockfiles easily with this contextmanager.  It will exclusively
    create the lockfile on entering the context and destroy it when the context
    is left.  If the lockfile cannot be exclusively created then raise
    LockfileExistsError.

    Creating files may be done atomically on a POSIX file system if the correct
    flags are used (O_CREAT | O_EXCL).
    http://pubs.opengroup.org/onlinepubs/9699919799/functions/open.html

    Note that if an unexpected exception is raised while the context is being
    entered then it's possible the lock will be acquired and 'leaked'. e.g. if
    the program is terminated whilst entering the context.

    """
    try:
        handle = os.open(filename, os.O_CREAT | os.O_EXCL)
    except OSError as e:
        if e.errno == 17:
            raise LockfileExistsError()
        else:
            raise

    # XXX: note that if we are interrupted here (e.g. by program termination)
    #      then the file will still exist and the lock will be erroneously
    #      still acquired after program exit.
    #
    #      there doesn't seem to be a good way to completely exclude this
    #      possibility - there's always the space between os.open() and
    #      assignment to 'handle'.

    try:
        yield
    finally:
        os.close(handle)
        os.remove(filename)


@contextlib.contextmanager
def chdir_context(new_path):
    """Change directory to the supplied 'new_path', change back when expired.

    Usage examples:

        Create a temporary directory and change to it:
        >>> with tmpdir_context() as temp_dir:
        ...     with chdir_context(temp_dir):
        ...         os.getcwd() == temp_dir
        True

        >>> os.getcwd() == temp_dir
        False

    """
    saved_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(saved_path)


@contextlib.contextmanager
def tmpfile(tmp_dir=None, suffix=''):
    "Create & remove tmp file"
    dir = tmp_dir or os.getenv('TMPDIR', '/tmp')
    tmp_file = tempfile.NamedTemporaryFile(dir=dir, suffix=suffix)
    yield tmp_file
    tmp_file.close()


@contextlib.contextmanager
def tmpdir_context():
    """Return the path to a newly created directory, remove when expired.

    Usage examples:

        create and remove a temporary directory:
        >>> with tmpdir_context() as temp_dir:
        ...     os.path.isdir(temp_dir)
        True

        >>> os.path.isdir(temp_dir)
        False

        create and remove a temporary directory despite an exception:
        >>> try:
        ...     with tmpdir_context() as temp_dir2:
        ...         os.path.isdir(temp_dir2)
        ...         raise Exception('hi')
        ... except Exception:
        ...     pass
        True

        >>> os.path.isdir(temp_dir2)
        False

    """
    tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)


@contextlib.contextmanager
def chtmpdir_context():
    """Change to a newly created dir, remove and change back when expired.

    Usage examples:

        create and remove a temporary directory:
        >>> with chtmpdir_context() as temp_dir:
        ...     os.getcwd() == temp_dir
        True

        >>> os.getcwd() == temp_dir
        False

        >>> os.path.isdir(temp_dir)
        False

        create and remove a temporary directory despite an exception:
        >>> try:
        ...     with chtmpdir_context() as temp_dir2:
        ...         os.getcwd() == temp_dir2
        ...         raise Exception('hi')
        ... except Exception:
        ...     pass
        True

        >>> os.getcwd() == temp_dir2
        False

        >>> os.path.isdir(temp_dir2)
        False

    """
    saved_path = os.getcwd()
    tmp_dir = tempfile.mkdtemp()
    os.chdir(tmp_dir)
    try:
        yield tmp_dir
    finally:
        os.chdir(saved_path)
        shutil.rmtree(tmp_dir)


@contextlib.contextmanager
def nostd(err=True):
    "Suppress stderr or stdout"
    class Devnull(object):

        def write(self, s):
            self.out = s
    if err:
        savestd = sys.stderr
        sys.stderr = Devnull()
        yield sys.stderr
        sys.stderr = savestd
    else:
        savestd = sys.stdout
        sys.stdout = Devnull()
        yield sys.stdout
        sys.stdout = savestd


def ensure_dir(path):
    """Ensure that the supplied 'path' is a directory if it is not already.

    Create intermediate folders if necessary

    :path: the string path of the dir to potentially create
    :returns: None

    """
    if not os.path.exists(path):
        os.makedirs(path)


def write_text_file(path, text):
    """Write the 'text' to the file at 'path', create dirs and file if needed.

    :path: the string path of the file to write
    :text: the string contents of the file
    :returns: None

    """
    dir_path = os.path.dirname(path)
    if dir_path:
        ensure_dir(dir_path)
    with open(path, 'w') as f:
        f.write(text)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
