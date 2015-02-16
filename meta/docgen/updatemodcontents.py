""""Automatically rewrite modules with a generated 'CONTENTS' section.

In addition to module docstrings that detail the purpose and some intended
usage of a module, it can be useful to have a short inventory of the salient
contents.

The Python built-in function 'help' does a great job of this, e.g.

    FUNCTIONS
        find_insertion_point(module_text)
        find_likely_insertion_point(module_text)

Although Python is highly available, the help pages aren't easily available
in all the contexts that they might be useful, e.g. browsing the code via the
GitHub web interface.

This module aims to improve the availability by inserting comments to roughly
the same effect of the help pages.  This makes the outline highly available in
all contexts.

They are generated as comments rather than docstrings because docstrings will
appear in the help pages.

"""
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
import cStringIO
import contextlib
import os
import sys
import tokenize


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'modules',
        type=str,
        nargs="+")
    argparser.add_argument(
        '--force-insert',
        action="store_true")
    args = argparser.parse_args()

    block_marker = '# ' + ('=' * 77)

    with contextlib.closing(cStringIO.StringIO()) as s:
        print(block_marker, file=s)
        print("# CONTENTS", file=s)
        print("#", "-" * 77, file=s)
        contents_signature = s.getvalue()

    modules = sorted(args.modules)
    for m in modules:
        if not process_module(m, contents_signature, args, block_marker):
            return -1


def process_module(
        m, contents_signature, args, block_marker):
    raw = ''.join(open(m))

    # look for contents block
    try:
        start_index, end_index = find_insertion_point(
            raw, contents_signature, block_marker, args.force_insert)
    except Exception as e:
        print("error while processing file: ", m)
        print(e)
        raise
        return False

    classes = []
    functions = []
    assignments = []
    parse_module(raw, classes, functions, assignments)

    name = os.path.splitext(os.path.basename(m))[0]

    with contextlib.closing(cStringIO.StringIO()) as contents:
        contents.write(contents_signature)
        print_contents(contents, name, classes, functions, assignments)
        print(block_marker, file=contents)

        new_raw = ''.join([
            raw[:start_index],
            contents.getvalue(),
            raw[end_index:]
        ])

        if new_raw != raw:
            with open(m, 'w') as f:
                f.write(new_raw)
            print("wrote", m)

    return True


def find_insertion_point(module_text, contents_signature, block_marker, force):
    block_marker_line = block_marker + '\n'
    start_index = module_text.find(contents_signature)
    if start_index == -1:
        if force:
            start_index = find_likely_insertion_point(module_text)
            end_index = start_index
        else:
            raise Exception(
                "couldn't find contents block in file\n"
                "please insert after imports:\n" +
                contents_signature +
                block_marker)
    else:
        end_index = module_text.find(block_marker_line, start_index + 1)
        if end_index == -1:
            raise Exception(
                "contents block is unterminated in file\n"
                "please terminate with this line:\n" +
                block_marker)
        end_index += len(block_marker_line)

    return start_index, end_index


def parse_module(s, classes, functions, assignments):
    module = ast.parse(s)
    for c in ast.iter_child_nodes(module):
        fields = dict(ast.iter_fields(c))
        if isinstance(c, ast.FunctionDef):
            name = fields["name"]
            if name[0] != '_':
                functions.append(name)
        elif isinstance(c, ast.ClassDef):
            name = fields["name"]
            members = []
            for member in fields["body"]:
                if isinstance(member, ast.FunctionDef):
                    member_fields = dict(ast.iter_fields(member))
                    member_name = member_fields['name']
                    if member_name[0] != '_':
                        members.append(member_name)
            if name[0] != '_':
                classes.append((name, members))
        elif isinstance(c, ast.Assign):
            for t in fields["targets"]:
                name = dict(ast.iter_fields(t))["id"]
                if name[0] != '_':
                    assignments.append(name)


def print_contents(f, name, classes, functions, assignments):
    print("#", name, file=f)
    print("#", file=f)
    if classes:
        print_nested_items_indented(f, "Public Classes", classes)
    if functions:
        print_items_indented(f, "Public Functions", functions)
    if assignments:
        print_items_indented(f, "Public Assignments", assignments)
    print("#", "-" * 77, file=f)
    print(
        "# (this contents block is generated, edits will be lost)",
        file=f)


def find_likely_insertion_point(module_text):
    with contextlib.closing(cStringIO.StringIO(module_text)) as text:
        tokens = list(tokenize.generate_tokens(text.readline))
    first = tokens[0]
    if first[0] == tokenize.STRING:
        return len(first[4])  # return length of the docstring
    else:
        return 0


def print_items_indented(f, description, items):
    print("# " + description + ":", file=f)
    for i in items:
        print("#  ", i, file=f)
    print("#", file=f)


def print_nested_items_indented(f, description, nested_items):
    print("# " + description + ":", file=f)
    for i in nested_items:
        print("#  ", i[0], file=f)
        for j in i[1]:
            print("#    ." + j, file=f)
    print("#", file=f)


if __name__ == "__main__":
    sys.exit(main())

# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
