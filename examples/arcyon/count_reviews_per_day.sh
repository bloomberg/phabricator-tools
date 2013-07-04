# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

echo "last update time, counts per day:"
echo
tempfile=`mktemp`

arcyon query --format-string '$daysSinceDateModified' --max-results 2000 > $tempfile
arcyon query --format-string '$daysSinceDateModified' --max-results 2000 --offset-results 2000 >> $tempfile
arcyon query --format-string '$daysSinceDateModified' --max-results 2000 --offset-results 4000 >> $tempfile
arcyon query --format-string '$daysSinceDateModified' --max-results 2000 --offset-results 6000 >> $tempfile
arcyon query --format-string '$daysSinceDateModified' --max-results 2000 --offset-results 8000 >> $tempfile

uniq -c $tempfile
echo `wc -l < $tempfile` reviews considered
echo "(n.b. counts up to last 10,000 reviews or so only)"
rm $tempfile
