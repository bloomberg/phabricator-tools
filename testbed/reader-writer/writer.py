import fcntl
import json
import os
import random

while True:
    d = {}
    for i in xrange(0, random.randint(1, 1000)):
        d[i] = random.randint(1, 1000)

    f = open('test-file', 'r+')
    fcntl.flock(f, fcntl.LOCK_EX)
    f.truncate()
    f.write(json.dumps(d))
    f.flush()
    os.fsync(f.fileno())
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()

    # print ".",
