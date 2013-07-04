# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

arcyon query "$@" --translate --format-string '$authorUsername' | sort | uniq -c | sort -rn | head
