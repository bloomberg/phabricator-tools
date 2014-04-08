# comment on reviews which we find linter errors for

# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR
set -e
#set -x

# need to specify revision and connection parameters on the command-line
#
# e.g.
#     ./phlint -r 4006 --uri http://127.0.0.1
#

revision="$1"
shift

prev_dir=$(pwd)
temp_dir=$(mktemp -d)
left_files_lint=$(mktemp)
right_files_lint=$(mktemp)
message_file=$(mktemp)

arcyon get-diff --format-files $temp_dir -r ${revision} "$@"

cd $temp_dir
    cd left
        set +e
        trap - ERR
        jshint . | sed '/^$/d' > $left_files_lint
        cppcheck -q . 2>> $left_files_lint
        pyflakes . >> $left_files_lint
        trap 'echo FAILED; exit 1' ERR
        set -e
    cd ..
    cd right
        set +e
        trap - ERR
        jshint . | sed '/^$/d' > $right_files_lint
        cppcheck -q . 2>> $right_files_lint
        pyflakes . >> $right_files_lint
        trap 'echo FAILED; exit 1' ERR
        set -e
    cd ..
cd ${prev_dir}

# don't output the first 3 lines of the diff, they're the header and not relevant
#
# e.g.
#      --- /tmp/tmp.Mq5cmFpk20  2013-11-19 14:08:41.868364952 +0000
#      +++ /tmp/tmp.RS4zJ0RPkY  2013-11-19 14:08:41.876364879 +0000
#      @@ -0,0 +1 @@
#
result=$(diff -U 1000 --suppress-common-lines $left_files_lint $right_files_lint | tail -n +4)

left_count=$(cat ${left_files_lint}| wc -l )
right_count=$(cat ${right_files_lint} | wc -l )
new_or_moved_errors=$(echo "${result}" | sed -n '/^\+/p')

no_errors=0
if [ "${right_count}" -eq 0 ]; then
    if [ "${left_count}" -eq 0 ]; then
        no_errors=1
    fi
fi

if [ "${no_errors}" -eq 1 ]; then
    echo verdict: **NO ERRORS BEFORE. NO ERRORS NOW. GOOD.** >> ${message_file}
else
    if [ ! -z "${new_or_moved_errors}" ]; then
        echo first 10 moved or new error messages: > ${message_file}
        echo >> ${message_file}
        echo '``` lang=text, counterexample' >> ${message_file}
        echo "${new_or_moved_errors}" | sed 's/^.//' | head >> ${message_file}
        echo '```' >> ${message_file}
    else
        echo first 10 error messages: > ${message_file}
        echo >> ${message_file}
        echo '``` lang=text, counterexample' >> ${message_file}
        echo cat "${right_files_lint}" | sed 's/^.//' | head >> ${message_file}
        echo '```' >> ${message_file}
    fi
    echo >> ${message_file}
    echo summary: >> ${message_file}
    echo >> ${message_file}
    echo '| number of error messages |' >> ${message_file}
    echo '| ---- |' >> ${message_file}
    echo '| before changes | ' ${left_count} ' |' >> ${message_file}
    echo '| after changes | ' ${right_count} ' |' >> ${message_file}
    echo >> ${message_file}
    if [ "${right_count}" -eq 0 ]; then
        echo verdict: **NO ERROR NOW. GOOD.** >> ${message_file}
    elif [ "${left_count}" -eq "${right_count}" ]; then
        echo verdict: **NOT WORSE. NOT BETTER.** >> ${message_file}
    elif [ "${left_count}" -gt "${right_count}" ]; then
        echo verdict: **IMPROVEMENT. GOOD.** >> ${message_file}
    elif [ "${left_count}" -lt "${right_count}" ]; then
        echo verdict: **MAKE LESS ERROR NOT MOAR!** >> ${message_file}
    fi

    cat ${message_file}

    read -p "Please hit 'y' to continue, any other to abort: "
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo aborted.
        exit 1
    fi

    arcyon comment ${revision} --message-file "${message_file}" "$@"
fi

rm -rf $temp_dir
rm $left_files_lint
rm $right_files_lint
rm $message_file
# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# ------------------------------ END-OF-FILE ----------------------------------
