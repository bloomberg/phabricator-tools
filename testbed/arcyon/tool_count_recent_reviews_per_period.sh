arcyon="../../bin/arcyon"
echo "last update time"
echo "(n.b. counts last 3000 reviews or so only)"
tempfile=`mktemp`
$arcyon query --format-string '$humanTimeSinceDateModified' --max-results 1000 > $tempfile
$arcyon query --format-string '$humanTimeSinceDateModified' --max-results 1000 --offset-results 1000 >> $tempfile
$arcyon query --format-string '$humanTimeSinceDateModified' --max-results 1000 --offset-results 2000 >> $tempfile
uniq -c $tempfile
rm $tempfile
