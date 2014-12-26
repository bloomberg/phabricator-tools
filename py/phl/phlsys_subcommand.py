"""Help to wrap up modules as subcommands."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_subcommand
#
# Public Functions:
#   setup_parser
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse


def setup_parser(name, module, subparsers):
    doc = module.__doc__
    docSubject = doc.splitlines()[0]
    docEpilog = '\n'.join(doc.splitlines()[1:])
    parser = subparsers.add_parser(
        name,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help=docSubject,
        description=docSubject,
        epilog=docEpilog,
        fromfile_prefix_chars=module.getFromfilePrefixChars())
    module.setupParser(parser)
    parser.set_defaults(func=module.process)


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
