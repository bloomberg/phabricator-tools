###############################################################################
# looping test for Arcyd, aimed at exercising the whole cycle
###############################################################################

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

./_loop.sh "python $(pwd)/bad_git_push_arcyd.py"
