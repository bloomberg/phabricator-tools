# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

echo Open reviews where you are the author:
../../bin/arcyon query --author-me --status-type open

echo Open reviews where you are a reviewer:
../../bin/arcyon query --reviewer-me --status-type open
