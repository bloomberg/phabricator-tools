#! /usr/bin/env bash

# The Python 'cProfile' module is widely available and can be invoked from the
# command-line, this will record results in the 'arcyd.profile' file.
python -m cProfile -o arcyd.profile $(which arcyd) start --foreground --no-loop

# Analyse the profile interactively using the 'pstats' module
echo 'Starting "pstats" to interactively analyse the profile.'
echo 'Try typing this to get the top-30 functions by cumulative time:'
echo
echo '  sort cumulative'
echo '  stats 30'
echo
echo 'Type "help" to list all commands.'
python -m pstats arcyd.profile
