arcyon="../../bin/arcyon"
echo "last update time, counts per day:"
echo "(n.b. counts last 1000 reviews or so only)"
echo

echo "last 24hrs: " `$arcyon query --update-max-age "1 days" | wc -l`
echo "prev 24hrs: " `$arcyon query --update-min-age "1 days" --update-max-age "2 days" | wc -l`
echo "2 days ago: " `$arcyon query --update-min-age "2 days" --update-max-age "3 days" | wc -l`
echo "3 days ago: " `$arcyon query --update-min-age "3 days" --update-max-age "4 days" | wc -l`
echo "4 days ago: " `$arcyon query --update-min-age "4 days" --update-max-age "5 days" | wc -l`
