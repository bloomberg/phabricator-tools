lines = open('test-file', 'r').readlines()
for (i, s) in enumerate(lines):
    assert i == int(s), str(i) + ' ' + s
print "read", len(lines), "lines"
