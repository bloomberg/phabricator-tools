import json
import os
import sys

# append our module dirs to sys.path, which is the list of paths to search
# for modules this is so we can import our libraries directly
# N.B. this magic is only really passable up-front in the entrypoint module
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BASE_DIR = os.path.dirname(PARENT_DIR)
sys.path.append(os.path.join(BASE_DIR, "py", "phl"))

import phlsys_fs

while True:
    with phlsys_fs.read_file_lock_context('test-file') as f:
        text = f.read()

    data = {}
    if text:
        try:
            data = json.loads(text)
        except Exception as e:
            print e
            print "----"
            print text
            print "----"
            raise

    print "read", len(data), "items"
