###############################################################################
## generate documentation #####################################################
#                                                                             #
# The following operations are performed:                                     #
# :o update 'contents block' documentation at the top of each component       #
# :o update package group documentation .md files                             #
#                                                                             #
###############################################################################

set -e # exit immediately on error

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

###############################################################################
# update 'contents block' documentation at the top of each component
###############################################################################

python meta/docgen/updatemodcontents.py \
    --force-insert \
    `find py/ meta/docgen meta/autofix -iname '*.py' | grep -v __t`

###############################################################################
# update package group documentation .md files
###############################################################################

for dir in $(find py/ -mindepth 1 -maxdepth 1 -type d); do
    group=$(basename "${dir}")
    mdfile="${dir}/README.md"
    echo "# ${group}" > ${mdfile}
    python meta/docgen/genmoddoc.py \
        --docfile - \
        `find ${dir} -iname '*.py' | grep -v __t` \
        >> ${mdfile}
    echo >> ${mdfile}
    echo '-----' >> ${mdfile}
    echo '*please note: this file is generated, edits will be lost*' >> ${mdfile}
done

###############################################################################
# update 'man page' documentation in doc/man
###############################################################################

arcyon='bin/arcyon'
${arcyon} -h > doc/man/arcyon/arcyon.generated.txt
${arcyon} show-config -h > doc/man/arcyon/arcyon_show_config.generated.txt
${arcyon} query -h > doc/man/arcyon/arcyon_query.generated.txt
${arcyon} comment -h > doc/man/arcyon/arcyon_comment.generated.txt
${arcyon} raw-diff -h > doc/man/arcyon/arcyon_raw_diff.generated.txt
${arcyon} create-revision -h > doc/man/arcyon/arcyon_create_revision.generated.txt
${arcyon} update-revision -h > doc/man/arcyon/arcyon_update_revision.generated.txt
${arcyon} get-diff -h > doc/man/arcyon/arcyon_get_diff.generated.txt
${arcyon} paste -h > doc/man/arcyon/arcyon_paste.generated.txt
${arcyon} task-create -h > doc/man/arcyon/arcyon_task_create.generated.txt
${arcyon} task-update -h > doc/man/arcyon/arcyon_task_update.generated.txt
${arcyon} task-query -h > doc/man/arcyon/arcyon_task_query.generated.txt

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
