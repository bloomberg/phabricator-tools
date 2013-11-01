#!/usr/bin/env python
# encoding: utf-8

"""Conduit data for the default Phabricator install."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phldef_conduit
#
# Public Assignments:
#   Account
#   TEST_URI
#   ALICE
#   BOB
#   PHAB
#   NOTAUSER
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

# TODO: add emails too

from __future__ import absolute_import

import collections

Account = collections.namedtuple(
    'phlcon_testdata__Account',
    ['user', 'email', 'certificate', 'phid'])

# if using Vagrant, there will be a Phabricator available locally
# TODO: this should be configurable from the command-line or a config file
TEST_URI = "http://127.0.0.1/api/"

ALICE = Account(
    user="alice",
    email="alice@server.test",
    certificate=(
        "35yxukrjcltwgzfmgsnj2klc2jbrnzehqz3c36ijxnicwysv3xenxymwz532pyh"
        "impxh7jryynh32su2ajxahd3gp7qshyik2qwf6ntuim2acxvjnko6p2q4mhacpv"
        "ugqou2wpmyqwj4hkchgc5vh33lur723r4dexy5b3aj35v4v6ffork727ww5qk5y"
        "hhcmolbcqg3rxl6qpf53spn4aopneggtb675hmpx3xya3et7jrowzlkl3yw3sktvdu"),
    phid="PHID-USER-hncf4pdbrr53lsxn5j6z")

BOB = Account(
    user="bob",
    email="bob@server.test",
    certificate=(
        "6wcgqpgbqyeymlmqdhdj2xya75fa5rwttr4k7pf5klqhiiwgeqiuvsr5ulrboscw"
        "kqtumravl33qc6in4p2hfnqal4ik3c2r33f3ezdqopl34ae4p2khvepg3bktpl5z"
        "nsdrxs5jot4pk6vdz7gasod6eksfzb2rmekawftqbaqqbfwcsaoxhc7eglq7awvm"
        "pbae6gqejpobyvglobiqw4edr7qcqkfcyffi56hbtqzaj7m2ulqbmftdeltaqad"),
    phid="PHID-USER-agn7y2uw2pj4nc5nknhe")

PHAB = Account(
    user="phab",
    email="phab@server.test",
    certificate=(
        "xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7"
        "ru3lrvafgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn"
        "2vah2uidj6u6hhhxo2j3y2w6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2"
        "llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3uvot7fxrotwpi3ty"
        "2b2sa2kvlpf"),
    phid="PHID-USER-n334wwtakshsxeau3qij")

# a user that definitely won't be registered, useful for testing
NOTAUSER = Account(
    user="#:)-",
    email="notauser@server.invalid",
    certificate=(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        "ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
        "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
        "eeeeeeeeeee"),
    phid="PHID-NOTAUSER")

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
