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
# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
