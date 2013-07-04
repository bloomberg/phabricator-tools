# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

tempfile=`mktemp`
arcyon query "$@" --format-string '$humanDateModified' --max-results 2000 > $tempfile
arcyon query "$@" --format-string '$humanDateModified' --max-results 2000 --offset-results 2000 >> $tempfile
arcyon query "$@" --format-string '$humanDateModified' --max-results 2000 --offset-results 4000 >> $tempfile
arcyon query "$@" --format-string '$humanDateModified' --max-results 2000 --offset-results 6000 >> $tempfile
arcyon query "$@" --format-string '$humanDateModified' --max-results 2000 --offset-results 8000 >> $tempfile

echo "last update time, counts per date:"
cut -f 1 -d' ' $tempfile | uniq -c

echo
echo "counts per month:"
cut -f 1,2 -d'-' $tempfile | uniq -c

echo
echo `wc -l < $tempfile` reviews considered
echo "(n.b. counts up to last 10,000 reviews or so only)"
rm $tempfile
