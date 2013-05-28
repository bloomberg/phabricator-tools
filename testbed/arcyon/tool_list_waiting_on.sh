# List out the revisions that require the user to act next.

echo Revisions you have authored, waiting on others:
../../bin/arcyon query --author-me --status-type open --statuses 'Needs Review'

echo Revisions you are reviewing, waiting on others:
../../bin/arcyon query --reviewer-me --status-type open --statuses 'Needs Revision'
