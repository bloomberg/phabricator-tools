""""Automatically rewrite modules with the import blocks sorted."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# fiximports
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
#   push_current_future_group
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

ParsedImport = collections.namedtuple(
    'ParsedImport', ['line', 'module', 'is_future'])

_REQUIRED_FUTURE_IMPORTS = set(
    ['absolute_import', 'print_function', 'division'])


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
        except Exception as e:
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

    new_import_lines = None
    if groups:
        new_import_lines = groups[0]
        for g in groups[1:]:
            new_import_lines.append('')
            new_import_lines += g

    if new_import_lines:
        if imports:
            first_line = imports[0].line - 1
            last_line = imports[-1].line - 1
            lines[first_line:last_line + 1] = new_import_lines
        else:
            lines[0:1] = lines[0:1] + new_import_lines

    return '\n'.join(lines) + '\n'


def parse_imports(s):
    module = ast.parse(s)
    imports = []
    for c in ast.iter_child_nodes(module):
        if isinstance(c, ast.ImportFrom):
            fields = dict(ast.iter_fields(c))
            from_module = fields['module']
            if from_module != '__future__':
                raise ProcessingException(
                    'non-future ImportFrom on line ' + str(c.lineno))
            names = [dict(ast.iter_fields(i))['name'] for i in fields['names']]
            if len(names) != 1:
                raise ProcessingException(
                    'multiple imports on line ' + str(c.lineno))
            imports.append(ParsedImport(c.lineno, names[0], True))

        if isinstance(c, ast.Import):
            fields = dict(ast.iter_fields(c))
            names = [dict(ast.iter_fields(i))['name'] for i in fields['names']]
            if len(names) != 1:
                raise ProcessingException(
                    'multiple imports on line ' + str(c.lineno))
            imports.append(ParsedImport(c.lineno, names[0], False))

    return imports


def group_imports(imports, module_name):
    groups = []

    package_group = module_name[0:3]
    package = module_name[0:module_name.index('_')]

    # grab future imports
    current_group = [i.module for i in imports if i.is_future]

    # merge with required future imports
    current_group = list(set(current_group) | _REQUIRED_FUTURE_IMPORTS)

    # grab the names of the modules into a new list
    imports = [i.module for i in imports]

    push_current_future_group(groups, current_group, imports)

    # grab standard library imports
    current_group = [i for i in imports if '_' not in i]
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
        imports[:] = list(set(imports) - set(current_group))
        current_group = ['import ' + i for i in current_group]
        current_group.sort()
        groups.append(current_group)


def push_current_future_group(groups, current_group, imports):
    if current_group:
        imports[:] = list(set(imports) - set(current_group))
        current_group = ['from __future__ import ' + i for i in current_group]
        current_group.sort()
        groups.append(current_group)


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
