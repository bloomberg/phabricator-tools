"""Test that the 'subprocess' releases the GIL, allowing threading.

If the GIL was not released for the duration of the calls to 'sleep' then we'd
expect the running time to be over 9 seconds. In practice it's closer to the
ideal of 3 in the single-processor Lubuntu 13.04 VM tested on.

With this result we can see that there's a benefit to using threading in
conjuction with subprocess, if we're spending a lot of time in subprocess.

"""
import datetime
import subprocess
import sys
import threading


def sleep_work(lock):
    with lock:
        print "{}: starting sleep".format(threading.current_thread().name)
    subprocess.check_call(["sleep", "3"])
    with lock:
        print "{}: finished sleep".format(threading.current_thread().name)


def main():
    start = datetime.datetime.now()

    lock = threading.Lock()
    threads = []
    for i in xrange(0, 3):
        t = threading.Thread(
            args=[lock],
            target=sleep_work,
            name=str(i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = datetime.datetime.now()
    duration = end - start
    print "took {} secs".format(duration)


if __name__ == "__main__":
    sys.exit(main())
