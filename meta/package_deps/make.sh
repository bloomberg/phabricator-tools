set -e # exit immediately on error

#PYTHONPATH=../../py sfood ../../py/*.py --internal | sfood-graph | dot -Tsvg -o deps.svg
sfood ../../py/*.py --internal > deps
./process.py deps file-deps package-deps
