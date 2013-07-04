# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

# print out "{projectName} {id}" for each open revision by projectName
# use '$ arcyon query --arcanist-projects' to filter by project
arcyon query "$@" --status-type open --format-type ids | xargs -I ID arcyon get-diff -r ID "$@" --format-string "{projectName} {id}" ""
