""""Automatically rewrite modules with the import blocks sorted."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# updatemodcontents
#
# Public Functions:
#   main
#   process_module
#   find_insertion_point
#   parse_module
#   print_contents
#   find_likely_insertion_point
#   print_items_indented
#   print_nested_items_indented
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import print_function

import argparse
import ast
import collections
import sys

ParsedImport = collections.namedtuple('ParsedImport', ['line', 'module'])
ImportGroup = collections.namedtuple('ImportGroup', ['line', 'imports'])


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'modules',
        type=str,
        nargs="+")
    args = argparser.parse_args()

    modules = sorted(args.modules)
    for m in modules:
        try:
            process_module(m)
        except Exception as e:
            print('Exception while processing: ', m)
            print(e)
            return 1

    return 0


def process_module(m):
    raw = ''.join(open(m))

    new_raw = rewrite_module(raw)

    if new_raw != raw:
        with open(m, 'w') as f:
            f.write(new_raw)
            print("wrote", m)


def rewrite_module(s):
    imports = parse_imports(s)
    groups = group_imports(imports)
    lines = s.splitlines()

    for g in groups:
        imports = sorted([i.module for i in g.imports])
        for i, name in enumerate(imports):
            lines[g.line + i - 1] = 'import ' + name

    return '\n'.join(lines) + '\n'


def parse_imports(s):
    module = ast.parse(s)
    imports = []
    for c in ast.iter_child_nodes(module):
        if isinstance(c, ast.ImportFrom):
            raise Exception('ImportFrom on line ' + str(c.lineno))
        if isinstance(c, ast.Import):
            fields = dict(ast.iter_fields(c))
            names = [dict(ast.iter_fields(i))['name'] for i in fields['names']]
            if len(names) != 1:
                raise Exception('multiple imports on line ' + str(c.lineno))
            imports.append(ParsedImport(c.lineno, names[0]))

    return imports


def group_imports(imports):
    last_line = -2
    groups = []
    current_group = []
    for i in imports:
        if i.line == last_line + 1:
            current_group.append(i)
        else:
            current_group = []
            groups.append(current_group)
            current_group.append(i)
        last_line = i.line

    groups = [ImportGroup(g[0].line, g) for g in groups]
    return groups


if __name__ == "__main__":
    sys.exit(main())

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
