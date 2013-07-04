# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

echo Open reviews where you are the author:
arcyon query "$@" --author-me --status-type open

echo

echo Open reviews where you are a reviewer:
arcyon query "$@" --reviewer-me --status-type open
