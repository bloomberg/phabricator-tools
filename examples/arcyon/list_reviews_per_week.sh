# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

echo "last update time, counts per week:"
echo "(n.b. counts last 1000 reviews or so only)"
echo

echo "last 7 days: " `arcyon query --update-max-age "1 weeks" | wc -l`
echo "prev 7 days: " `arcyon query --update-min-age "1 weeks" --update-max-age "2 weeks" | wc -l`
echo "2 weeks ago: " `arcyon query --update-min-age "2 weeks" --update-max-age "3 weeks" | wc -l`
echo "3 weeks ago: " `arcyon query --update-min-age "3 weeks" --update-max-age "4 weeks" | wc -l`
echo "4 weeks ago: " `arcyon query --update-min-age "4 weeks" --update-max-age "5 weeks" | wc -l`
