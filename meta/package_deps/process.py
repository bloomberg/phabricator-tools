#!/usr/bin/env python
# encoding: utf-8

import argparse
from collections import defaultdict
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('raw_deps_in', type=str)
    parser.add_argument('file_deps_out', type=str)
    parser.add_argument('package_deps_out', type=str)
    args = parser.parse_args()

    file_deps = defaultdict(set)
    package_deps = defaultdict(set)

    with open(args.raw_deps_in, 'r') as f:
        for line in f:
            dep = eval(line)
            file_from = dep[0][1]
            file_to = dep[1][1]
            if file_to is not None:
                package_from = parsePackageName(file_from)
                package_to = parsePackageName(file_to)
                file_deps[file_from].add(file_to)
                if package_from != package_to:
                    package_deps[package_from].add(package_to)

    dictValuesToLists(file_deps)
    dictValuesToLists(package_deps)
    writeDictToFile(args.file_deps_out, file_deps)
    writeDictToFile(args.package_deps_out, package_deps)


def parsePackageName(s):
    end = s.index('_')
    return s[:end]


def dictValuesToLists(d):
    for key in d:
        d[key] = sorted(list(d[key]))


def writeDictToFile(filename, d):
    with open(filename, 'w') as f:
        for item in d.iteritems():
            f.write(str(item) + '\n')


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
