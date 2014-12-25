"""Barc - a command-line client to complement 'arcyd'.

Essentially a prescriptive tool for supporting arcyd's branch-based workflow.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# barcmd_barc
#
# Public Functions:
#   main
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function

import argparse

import phlsys_subcommand

import barcmd_gc
import barcmd_list

_USAGE_EXAMPLES = """
usage example:
    Using the example accounts baked into the 'phabricator-tools'
    vagrant/puppet installation. (see ./README)

    to clean up landed local branches:
    $ barc gc --force --aggressive

    to display help on the 'gc' sub-command:
    $ barc gc --help

    """


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    subparsers = parser.add_subparsers()

    phlsys_subcommand.setup_parser(
        "gc", barcmd_gc, subparsers)
    phlsys_subcommand.setup_parser(
        "list", barcmd_list, subparsers)

    args = parser.parse_args()

    return args.func(args)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
