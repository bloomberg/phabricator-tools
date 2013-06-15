# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

arcyon="../../bin/arcyon"
echo "last update time"
tempfile=`mktemp`
$arcyon query --format-string '$humanTimeSinceDateModified' --max-results 1000 > $tempfile
$arcyon query --format-string '$humanTimeSinceDateModified' --max-results 1000 --offset-results 1000 >> $tempfile
$arcyon query --format-string '$humanTimeSinceDateModified' --max-results 1000 --offset-results 2000 >> $tempfile
uniq -c $tempfile
echo `wc -l < $tempfile` reviews considered
echo "(n.b. counts up to last 3000 reviews or so only)"
rm $tempfile
