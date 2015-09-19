#!/usr/bin/env python
# encoding: utf-8

import os
import random
import sys

# The code base currently depends on version 2.7 of Python, any earlier
# than that and it won't have the requisite argparse feaures.  Any later
# than that (3.x) and there are breaking changes in the syntax.
#
# Prevent nasty runtime surprises by enforcing version 2.7 as early as
# possible.
#
# The version check itself will not work prior to Python version 2.0,
# that's when sys.version_info was introduced.
#
if sys.version_info[:2] != (2, 7):
    sys.stderr.write("You need python 2.7 to run this script\n")
    exit(1)

# append our module dirs to sys.path, which is the list of paths to search
# for modules this is so we can import our libraries directly
# N.B. this magic is only really passable up-front in the entrypoint module
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BASE_DIR = os.path.dirname(PARENT_DIR)
sys.path.append(os.path.join(BASE_DIR, "py", "abd"))
sys.path.append(os.path.join(BASE_DIR, "py", "phl"))

import phlsys_git

import abdcmd_arcyd

if __name__ == "__main__":

    #
    # monkey-patch the base-level git clone to be unreliable
    #

    old_call = getattr(phlsys_git.Repo, '__call__')

    def unreliable_call(self, *args, **kwargs):
        if args and args[0] == 'push':
            if random.choice([True, False]):
                raise Exception('bad_git_push_arcyd.py: random git push fail')
        return old_call(self, *args, **kwargs)

    setattr(phlsys_git.Repo, '__call__', unreliable_call)

    # run arcyd as usual
    sys.exit(abdcmd_arcyd.main())


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
