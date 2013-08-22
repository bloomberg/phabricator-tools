import json
import os
import random
import sys

# append our module dirs to sys.path, which is the list of paths to search
# for modules this is so we can import our libraries directly
# N.B. this magic is only really passable up-front in the entrypoint module
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BASE_DIR = os.path.dirname(PARENT_DIR)
sys.path.append(os.path.join(BASE_DIR, "py", "phl"))

import phlsys_fs


while True:
    d = {}
    for i in xrange(0, random.randint(1, 1000)):
        d[i] = random.randint(1, 1000)

    with phlsys_fs.write_file_lock_context('test-file') as f:
        f.write(json.dumps(d))

    # print ".",
