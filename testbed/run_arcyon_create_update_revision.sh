set -e # stop at the first sign of trouble
id="$(../bin/arcyon create-revision -t title -p plan -f diff1)"
../bin/arcyon update-revision -i $id -f diff2 -m update
