""""Automatically generate documentation from module docstrings."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# genmoddoc
#
# Public Functions:
#   main
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import print_function

import argparse
import ast
import os
import sys


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'modules',
        type=str,
        nargs="+")
    argparser.add_argument(
        '--docfile',
        type=argparse.FileType('w'),
        required=True)
    args = argparser.parse_args()

    modules = sorted(args.modules)
    for m in modules:
        module = ast.parse(''.join(open(m)))
        doc = ast.get_docstring(module)

        if doc:
            print('* `' + os.path.basename(m) + '` -', file=args.docfile)
            print(doc.splitlines()[0], file=args.docfile)
        else:
            print('* `' + os.path.basename(m) + '`', file=args.docfile)


if __name__ == "__main__":
    sys.exit(main())

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
