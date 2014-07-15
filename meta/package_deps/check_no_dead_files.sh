set -e # exit immediately on error

cd ../../py
unneeded_file=$(mktemp)
needed_file=$(mktemp)
all_file=$(mktemp)

PYTHONPATH='phl'

binaries='abd/abdcmd_arcyd.py aon/aoncmd_arcyon.py bar/barcmd_barc.py pig/pigcmd_phabping.py gab/gabcmd_gitphablog.py lor/lorcmd_linterate.py pox/poxcmd_conduitproxy.py'

# we need to include something from phl so it counts under 'internal'
from_phl='phl/phlsys_subprocess.py'

sfood --follow --internal $binaries $from_phl | sfood-flatten > $needed_file

# determine which files are test-drivers for the needed files by guessing a
# suffix of '__t' and testing if that file exists
test_drivers=`cat $needed_file | sed 's/\.py/__t.py/g' | python -c 'import os, sys; sys.stdout.writelines([f for f in sys.stdin if os.path.isfile(f.strip())])'`

# append the dependencies of the test drivers to the list of needed files
sfood --follow --internal $test_drivers $from_phl | sfood-flatten >> $needed_file

# determine which files are test-drivers for the needed files by guessing a
# suffix of '__t' and testing if that file exists
test_drivers=`cat $needed_file | sed 's/\.py/__t.py/g' | python -c 'import os, sys; sys.stdout.writelines([f for f in sys.stdin if os.path.isfile(f.strip())])'`

# append the dependencies of the test drivers to the list of needed files
sfood --follow --internal $test_drivers $from_phl | sfood-flatten >> $needed_file

# list all of the python source files
find `pwd` -iname *.py | grep -v '__t' > $all_file

# exclude files from 'all' that appear in 'needed'
# ('uniq -u' only removes repeated entries)
sort $all_file $needed_file $needed_file | uniq -u > $unneeded_file

# display the list of unneeded ('dead') files
cat $unneeded_file

if [ -s "$unneeded_file" ]
then
    result=1
    echo '** above files are not reachable from binaries **'
else
    result=0
fi

rm $unneeded_file $needed_file $all_file
exit $result


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
# ------------------------------ END-OF-FILE ----------------------------------
