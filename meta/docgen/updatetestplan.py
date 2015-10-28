"""Automatically rewrite tests with a generated 'TEST PLAN' section."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# updatetestplan
#
# Public Functions:
#   main
#   process_module
#   parse_module
#   extract_concerns
#   print_contents
#   print_concerns
#   print_functions
#   get_function_id
#   generate_bullet_from_id
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import print_function

import argparse
import ast
import cStringIO
import contextlib
import re
import sys
import textwrap
import tokenize

import updatemodcontents


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
        print("#", " " * 33, "TEST PLAN", file=s)
        print("#", "-" * 77, file=s)
        contents_signature = s.getvalue()

    modules = sorted(args.modules)
    for m in modules:
        process_module(m, contents_signature, args, block_marker)


def process_module(m, contents_signature, args, block_marker):
    raw = ''.join(open(m))

    # look for contents block
    try:
        start_index, end_index = updatemodcontents.find_insertion_point(
            raw, contents_signature, block_marker, args.force_insert)
    except Exception as e:
        print("error while processing file: ", m)
        print(e)
        raise

    functions = parse_module(raw)
    concerns = extract_concerns(raw)

    with contextlib.closing(cStringIO.StringIO()) as contents:
        contents.write(contents_signature)
        print_contents(contents, functions, concerns)
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


def parse_module(s):
    functions = []
    module = ast.parse(s)
    for c in ast.iter_child_nodes(module):
        fields = dict(ast.iter_fields(c))
        if isinstance(c, ast.ClassDef):
            name = fields["name"]
            for member in fields["body"]:
                if isinstance(member, ast.FunctionDef):
                    member_fields = dict(ast.iter_fields(member))
                    member_name = member_fields['name']
                    if member_name.startswith('test_'):
                        functions.append(member_name)

        elif isinstance(c, ast.FunctionDef):
            name = fields["name"]
            if name.startswith('test_'):
                functions.append(name)

    return functions


def extract_concerns(module_text):
    concerns = []
    with contextlib.closing(cStringIO.StringIO(module_text)) as text:
        tokens = tokenize.generate_tokens(text.readline)
        function_id = None

        for token in tokens:
            if (token[0] == tokenize.NAME and
                    token[4].lstrip().startswith('def') and
                    token[1].startswith('test_')):
                function_id = get_function_id(token[1])

            elif function_id and token[0] == tokenize.COMMENT:
                comment = token[1][1:].lstrip()
                comment_str = None
                if comment.startswith('CONCERN:'):
                    comment_str = comment.replace('CONCERN:', '', 1).lstrip()
                if comment.startswith('['):
                    comment_str = re.sub('\[.*\]', '', comment, 1).lstrip()
                if comment_str:
                    while True:
                        next_token = next(tokens, None)
                        if next_token and next_token[0] == tokenize.COMMENT:
                            next_comment = next_token[1][1:].lstrip()
                            comment_str += " " + next_comment
                        elif next_token and next_token[0] == tokenize.NL:
                            continue
                        else:
                            break
                    concern = "[ {func_id}] {comment}".format(
                        func_id=function_id, comment=comment_str)
                    concerns.append(concern)

    return concerns


def print_contents(f, functions, concerns):
    print("# Here we detail the things we are concerned to test and specify "
          "which tests", file=f)
    print("# cover those concerns.", file=f)
    print("#", file=f)
    print("#", "Concerns:", file=f)
    print_concerns(f, concerns)
    print("#", "-" * 77, file=f)
    print("#", "Tests:", file=f)
    print_functions(f, functions)


def print_concerns(f, concerns):
    for concern in concerns:
        lines = textwrap.wrap(concern, 77)
        for line in lines:
            print("#", line, file=f)


def print_functions(f, functions):
    for function in functions:
        function_id = get_function_id(function)
        prefix = generate_bullet_from_id(function_id)
        print("#", prefix, function, file=f)


def get_function_id(function):
    match = re.search('test_(.*?)_', function)
    return match.group(1) if match else ''


def generate_bullet_from_id(id):
    return "[ {id}]".format(id=id)


if __name__ == "__main__":
    sys.exit(main())


# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
