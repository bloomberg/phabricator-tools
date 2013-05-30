arcyon="../../bin/arcyon"
echo "last update time"
echo "(n.b. counts last 1000 reviews or so only)"
$arcyon query --format-string '$humanTimeSinceDateModified' | uniq -c
