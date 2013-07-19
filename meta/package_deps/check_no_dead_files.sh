set -e # exit immediately on error

cd ../../py
unneeded_file=$(mktemp)
needed_file=$(mktemp)
all_file=$(mktemp)

PYTHONPATH='phl'

binaries='abd/abdcmd_arcyd.py aon/aoncmd_arcyon.py pig/pigcmd_phabping.py'

# manually exclude test machinery from the checks
test_machinery='abd/abdt_conduitmock.py abd/abdtst_devphabgit.py phl/phlmail_mocksender.py'

# we need to include something from phl so it counts under 'internal'
from_phl='phl/phlsys_subprocess.py'

sfood --follow --internal $binaries $from_phl $test_machinery | sfood-flatten > $needed_file
find `pwd` -iname *.py | grep -v '__t' > $all_file

# exclude files from 'all' that appear in 'needed'
# ('uniq -u' only removes repeated entries)
sort $all_file $needed_file $needed_file | uniq -u > $unneeded_file

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
