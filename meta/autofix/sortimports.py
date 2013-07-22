""""Automatically rewrite modules with the import blocks sorted."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# sortimports
#
# Public Classes:
#   ProcessingException
#
# Public Functions:
#   main
#   process_module
#   rewrite_module
#   parse_imports
#   group_imports
#   push_current_group
#
# Public Assignments:
#   ParsedImport
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import print_function

import argparse
import ast
import collections
import os
import sys

ParsedImport = collections.namedtuple('ParsedImport', ['line', 'module'])


class ProcessingException(Exception):

    def __init__(self, description):
        super(ProcessingException, self).__init__(description)


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
        except ProcessingException as e:
            print('Exception while processing: ', m)
            print(e)
            return 1

    return 0


def process_module(m):
    raw = ''.join(open(m))

    new_raw = rewrite_module(raw, os.path.basename(m))

    if new_raw != raw:
        with open(m, 'w') as f:
            f.write(new_raw)
            print("wrote", m)


def rewrite_module(s, module_name):
    imports = parse_imports(s)
    groups = group_imports(imports, module_name)
    lines = s.splitlines()

    if imports:
        new_import_lines = []
        for g in groups:
            for i in g:
                new_import_lines.append('import ' + i)
            new_import_lines.append('')
        new_import_lines.pop(-1)

        first_line = imports[0].line - 1
        last_line = imports[-1].line - 1
        lines[first_line:last_line + 1] = new_import_lines

    return '\n'.join(lines) + '\n'


def parse_imports(s):
    module = ast.parse(s)
    imports = []
    for c in ast.iter_child_nodes(module):
        if isinstance(c, ast.ImportFrom):
            raise ProcessingException('ImportFrom on line ' + str(c.lineno))
        if isinstance(c, ast.Import):
            fields = dict(ast.iter_fields(c))
            names = [dict(ast.iter_fields(i))['name'] for i in fields['names']]
            if len(names) != 1:
                raise ProcessingException(
                    'multiple imports on line ' + str(c.lineno))
            imports.append(ParsedImport(c.lineno, names[0]))

    return imports


def group_imports(imports, module_name):
    groups = []

    package_group = module_name[0:3]
    package = module_name[0:module_name.index('_')]

    # grab the names of the modules into a new list
    imports = [i.module for i in imports]

    # grab standard library imports
    current_group = [i for i in imports if not '_' in i]
    push_current_group(groups, current_group, imports)

    # grab external deps
    current_group = [i for i in imports if not i.startswith(package_group)]
    push_current_group(groups, current_group, imports)

    # grab same group, different package deps
    current_group = [i for i in imports if not i.startswith(package)]
    push_current_group(groups, current_group, imports)

    # grab same package deps
    current_group = [i for i in imports if i.startswith(package)]
    push_current_group(groups, current_group, imports)

    # nothing should be left over
    assert not imports

    return groups


def push_current_group(groups, current_group, imports):
    if current_group:
        groups.append(current_group)
        imports[:] = sorted(list(set(imports) - set(current_group)))


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
