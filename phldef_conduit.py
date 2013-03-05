#!/usr/bin/env python
# encoding: utf-8

"""Conduit data for the default Phabricator install."""

#TODO: add emails too

import collections

Account = collections.namedtuple(
    'phlcon_testdata__Account',
    ['user', 'certificate'])

# if using Vagrant, there will be a Phabricator available locally
# TODO: this should be configurable from the command-line or a config file
test_uri = "http://127.0.0.1/api/"

alice = Account(user="alice", certificate=(
    "35yxukrjcltwgzfmgsnj2klc2jbrnzehqz3c36ijxnicwysv3xenxymwz532pyhimpxh7jryy"
    "nh32su2ajxahd3gp7qshyik2qwf6ntuim2acxvjnko6p2q4mhacpvugqou2wpmyqwj4hkchgc"
    "5vh33lur723r4dexy5b3aj35v4v6ffork727ww5qk5yhhcmolbcqg3rxl6qpf53spn4aopneg"
    "gtb675hmpx3xya3et7jrowzlkl3yw3sktvdu"))

bob = Account(user="bob", certificate=(
    "6wcgqpgbqyeymlmqdhdj2xya75fa5rwttr4k7pf5klqhiiwgeqiuvsr5ulrboscwkqtumravl"
    "33qc6in4p2hfnqal4ik3c2r33f3ezdqopl34ae4p2khvepg3bktpl5znsdrxs5jot4pk6vdz7"
    "gasod6eksfzb2rmekawftqbaqqbfwcsaoxhc7eglq7awvmpbae6gqejpobyvglobiqw4edr7q"
    "cqkfcyffi56hbtqzaj7m2ulqbmftdeltaqad"))

phab = Account(user="phab", certificate=(
    "xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7"
    "ru3lrvafgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn"
    "2vah2uidj6u6hhhxo2j3y2w6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2"
    "llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3uvot7fxrotwpi3ty"
    "2b2sa2kvlpf"))
