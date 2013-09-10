trap 'kill $(jobs -p)' EXIT

python writer.py &

python reader.py &
python reader.py &
python reader.py &
python reader.py &
python reader.py &
python reader.py &
python reader.py &
python reader.py &
python reader.py &
python reader.py &

jobs
wait
