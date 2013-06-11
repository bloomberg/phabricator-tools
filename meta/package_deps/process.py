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
