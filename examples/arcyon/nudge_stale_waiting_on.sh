# comment 'nudge' on reviews which we've been waiting on for over 2 days

# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

arcyon="../../bin/arcyon"
minage="2 days"
ids1=`$arcyon query --author-me --status-type open --statuses 'Needs Review' --format-type ids --update-min-age "$minage"`
ids2=`$arcyon query --reviewer-me --status-type open --statuses 'Needs Revision' --format-type ids --update-min-age "$minage"`

echo "will comment 'nudge' on the following reviews:"
ids=`echo $ids1 $ids2`
echo $ids

read -p "Hit 'y' to continue or any other to exit: " choice
if [ ! "$choice" = "y" ]; then
    echo user aborted.
    exit 2
fi

$arcyon comment $ids -m 'nudge'
