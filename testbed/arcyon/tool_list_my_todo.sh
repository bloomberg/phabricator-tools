# List out the revisions that require the user to act next.

#TODO: echo Your revisions in review with no reviewers:
#TODO: $arcyon query --author-me --no-reviewers --status-type open --statuses 'Needs Review'

echo Revisions you have authored:
../../bin/arcyon query --author-me --status-type open --statuses Accepted 'Needs Revision'

echo Revisions you are reviewing:
../../bin/arcyon query --reviewer-me --status-type open --statuses 'Needs Review'
