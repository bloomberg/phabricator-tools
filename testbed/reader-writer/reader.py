import fcntl
import json

while True:
    f = open('test-file', 'r')
    fcntl.flock(f, fcntl.LOCK_SH)
    text = f.read()
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()

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
