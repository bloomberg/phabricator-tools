# List out the revisions that require another user to act next.

# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

echo Revisions you have authored, waiting on others:
arcyon query "$@" --author-me --status-type open --statuses 'Needs Review'

echo

echo Revisions you are reviewing, waiting on others:
arcyon query "$@" --reviewer-me --status-type open --statuses 'Needs Revision'
