import os
import sys
import tempfile
import contextlib


@contextlib.contextmanager
def nostd(err=True):
    "Suppress stderr or stdout"
    class Devnull(object):
        def write(self, s):
            self.out = s
    if err:
        savestd = sys.stderr
        sys.stderr = Devnull()
        yield sys.stderr
        sys.stderr = savestd
    else:
        savestd = sys.stdout
        sys.stdout = Devnull()
        yield sys.stdout
        sys.stdout = savestd

@contextlib.contextmanager
def tmpfile(tmp_dir=None, suffix=''):
    "Create & remove tmp file"
    dir = tmp_dir or os.getenv('TMPDIR', '/tmp')
    tmp_file = tempfile.NamedTemporaryFile(dir=dir, suffix=suffix)
    yield tmp_file
    tmp_file.close()

