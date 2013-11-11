set -e # exit immediately on error

cd ../../py
unneeded_file=$(mktemp)
needed_file=$(mktemp)
all_file=$(mktemp)

PYTHONPATH='phl'

binaries='abd/abdcmd_arcyd.py aon/aoncmd_arcyon.py bar/barcmd_barc.py pig/pigcmd_phabping.py gab/gabcmd_gitphablog.py'

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
