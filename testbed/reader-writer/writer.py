while True:
    f = open('test-file', 'r+')
    for i in xrange(0, 1000):
        f.write(str(i) + '\n')
    f.close()
    print ".",
