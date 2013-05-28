# print out "{projectName} {id}" for each open revision by projectName
# the output from this should be easy to process with grep and cut to list
# the revisions for a particular project
arcyon='../../bin/arcyon'

$arcyon query --status-type open --format-type ids | xargs -I ID $arcyon get-diff -r ID --format-string "{projectName} {id}" ""
