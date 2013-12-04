trap "echo 'FAILED!'; exit 1" ERR

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

python -m compileall ../py
