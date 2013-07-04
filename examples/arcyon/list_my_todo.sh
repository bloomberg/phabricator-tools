# List out the revisions that require the user to act next.

# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

#TODO: echo Your revisions in review with no reviewers:
#TODO: $arcyon query --author-me --no-reviewers --status-type open --statuses 'Needs Review'

echo Revisions you have authored:
arcyon query "$@" --author-me --status-type open --statuses Accepted 'Needs Revision'

echo

echo Revisions you are reviewing:
arcyon query "$@" --reviewer-me --status-type open --statuses 'Needs Review'
