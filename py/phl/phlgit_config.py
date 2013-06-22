"""Wrapper around 'git config'"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_config
#
# Public Functions:
#   set_username_email
#   get_username
#   get_email
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================


def set_username_email(clone, username, email):
    """Set the user.name and user.email on the supplied git clone.

    :clone: the clone to operate on
    :username: the string value for user.name
    :email: the string value for user.email
    :returns: None

    """
    clone.call("config", "user.name", username)
    clone.call("config", "user.email", email)


def get_username(clone):
    """Return the string username for the current clone.

    :clone: the clone to operate on
    :returns: string username for the current clone

    """
    return clone.call("config", "--get", "user.name").strip()


def get_email(clone):
    """Return the string email for the current clone.

    :clone: the clone to operate on
    :returns: string email for the current clone

    """
    return clone.call("config", "--get", "user.email").strip()




#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
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
