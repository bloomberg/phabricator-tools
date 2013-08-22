trap 'kill $(jobs -p)' EXIT
python writer.py &
while sleep 0; do python reader.py; done
