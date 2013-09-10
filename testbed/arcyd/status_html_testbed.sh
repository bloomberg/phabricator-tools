trap "echo FAILED!; exit 1" ERR

# cd to the dir of this script to make paths simpler
cd "$(dirname "$0")"

arcyd="$(pwd)/../../proto/arcyd"

tempdir=$(mktemp -d)
olddir=$(pwd)
cd ${tempdir}

$arcyd dev-status-html
chromium-browser *.html

cd ${olddir}
rm -rf ${tempdir}
