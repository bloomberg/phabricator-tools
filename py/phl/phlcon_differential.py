"""Wrapper to call Phabricator's Differential Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_differential
#
# Public Classes:
#   ReviewStates
#   Action
#   MessageFields
#   Error
#   UpdateClosedRevisionError
#   WriteDiffError
#
# Public Functions:
#   create_raw_diff
#   create_diff
#   parse_commit_message
#   create_revision
#   query
#   get_revision_status
#   update_revision
#   create_comment
#   create_inline_comment
#   get_commit_message
#   close
#   create_empty_revision
#   update_revision_empty
#   get_revision_diff
#   get_diff
#   write_diff_files
#
# Public Assignments:
#   AUTHOR_ACTIONS
#   REVIEWER_ACTIONS
#   USER_ACTIONS
#   CreateRawDiffResponse
#   GetDiffIdResponse
#   ParseCommitMessageResponse
#   RevisionResponse
#   QueryResponse
#   GetDiffResponse
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import os

import phlsys_conduit
import phlsys_dictutil
import phlsys_namedtuple


# Enumerate the states that a Differential review can be in
# from ArcanistRevisionDifferentialStatus.php:
class ReviewStates(object):  # XXX: will derive from Enum in Python 3.4+
    needs_review = 0
    needs_revision = 1
    accepted = 2
    closed = 3
    abandoned = 4


# Enumerate the actions that can be performed on a Differential review
# from .../differential/constants/DifferentialAction.php:
class Action(object):  # XXX: will derive from Enum in Python 3.4+
    close = 'commit'
    comment = 'none'
    accept = 'accept'
    reject = 'reject'
    rethink = 'rethink'
    abandon = 'abandon'
    request = 'request_review'
    reclaim = 'reclaim'
    update = 'update'
    resign = 'resign'
    summarize = 'summarize'
    testplan = 'testplan'
    create = 'create'
    addreviewers = 'add_reviewers'
    addccs = 'add_ccs'
    claim = 'claim'
    reopen = 'reopen'


# Enumerate all the actions that an author may perform on a review
# map the strings that appear in the web UI to string that conduit expects
AUTHOR_ACTIONS = {
    "close": Action.close,
    "comment": Action.comment,
    "plan changes": Action.rethink,
    "abandon": Action.abandon,
    "request review": Action.request,
    "unabandon": Action.reclaim,
    "reopen": Action.reopen,
}

# Enumerate all the actions that an reviewer may perform on a review
# map the strings that appear in the web UI to string that conduit expects
# note that everyone except the author of a review is considered a reviewer
REVIEWER_ACTIONS = {
    "comment": Action.comment,
    "accept": Action.accept,
    "request changes": Action.reject,
    "resign as reviewer": Action.resign,
    "commandeer": Action.claim,
}

# Enumerate all the actions either a reviewer or author may perform
# map the strings that appear in the web UI to string that conduit expects
USER_ACTIONS = dict(AUTHOR_ACTIONS.items() + REVIEWER_ACTIONS.items())


# Enumerate some of the fields that Differential expects to be able fill out
# based on commit messages, these are accepted by create_revision and
# accept_revision
# from phabricator/.../...DefaultFieldSelector.php
class MessageFields(object):  # XXX: will derive from Enum in Python 3.4+
    title = "title"
    summary = "summary"
    test_plan = "testPlan"
    reviewer_phids = "reviewerPHIDs"
    cc_phids = "ccPHIDs"


CreateRawDiffResponse = phlsys_namedtuple.make_named_tuple(
    'CreateRawDiffResponse',
    required=['id', 'uri'],
    defaults={},
    ignored=[])


GetDiffIdResponse = phlsys_namedtuple.make_named_tuple(
    'phlcon_differential__GetDiffIdResponse',
    required=[
        'parent', 'properties', 'sourceControlSystem', 'sourceControlPath',
        'dateCreated', 'dateModified', 'lintStatus', 'bookmark', 'changes',
        'revisionID', 'sourceControlBaseRevision', 'branch',
        'projectName', 'unitStatus', 'creationMethod', 'id', 'description'],
    defaults={},
    ignored=[])


ParseCommitMessageResponse = phlsys_namedtuple.make_named_tuple(
    'phlcon_differential__ParseCommitMessageResponse',
    required=['fields', 'errors'],
    defaults={},
    ignored=[])


RevisionResponse = phlsys_namedtuple.make_named_tuple(
    'phlcon_differential__RevisionResponse',
    required=['revisionid', 'uri'],
    defaults={},
    ignored=[])


QueryResponse = phlsys_namedtuple.make_named_tuple(
    'phlcon_differential__QueryResponse',
    required=[
        'authorPHID', 'status', 'phid', 'testPlan', 'title', 'commits',
        'diffs', 'uri', 'ccs', 'dateCreated', 'lineCount', 'branch',
        'reviewers', 'id', 'statusName', 'hashes', 'summary', 'dateModified',
        'sourcePath', 'auxiliary'],
    defaults={},
    ignored=[])


GetDiffResponse = phlsys_namedtuple.make_named_tuple(
    'phlcon_differential__GetDiffResponse',
    required=['changes'],
    defaults={},
    ignored=[
        'properties', 'sourceControlPath', 'parent', 'lintStatus', 'bookmark',
        'projectName', 'revisionID', 'creationMethod', 'unitStatus',
        'sourceControlBaseRevision', 'branch', 'id', 'dateModified',
        'dateCreated', 'sourceControlSystem', 'description', 'authorEmail',
        'authorName'])


class Error(Exception):
    pass


class UpdateClosedRevisionError(Error):
    pass


class WriteDiffError(Error):
    pass


def create_raw_diff(conduit, diff):
    response = conduit.call("differential.createrawdiff", {"diff": diff})
    return CreateRawDiffResponse(**response)


def create_diff(
        conduit,
        changes_dict,
        source_machine,
        source_path,
        branch,
        source_control_system,  # svn or git
        source_control_path,
        source_control_base_revision,
        lint_status,
        unit_status,
        bookmark=None,
        parent_revision_id=None,
        creation_method=None,
        author_phid=None,
        arcanist_project=None,
        repository_uuid=None):
    """@todo: Docstring for create_diff.

    :conduit: conduit to operate on
    :changes_dict: changes response, 'changes' field of GetDiffResponse
    :source_machine: string name of submitting machine
    :source_path: string @todo
    :branch: string name of the branch this change is being submitted from
    :source_control_system: string? svn or git
    :source_control_path: @todo
    :source_control_base_revision: @todo
    :lint_status: string? none, skip, okay, warn, fail, postponed
    :unit_status: string? none, skip, okay, warn, fail, postponed
    :bookmark: optional string bookmark (mercurial term?)
    :parent_revision_id: @todo
    :creation_method: @todo
    :author_phid: optional string phid of the author
    :arcanist_project: optional string human context for the change
    :repository_uuid: @todo
    :returns: @todo

    Perhaps the best reference for this function is in the Phabricator source
    code itself.
    .../differential/conduit/ConduitAPI_differential_creatediff_Method.php

    """
    d = {
        "changes": changes_dict,
        "sourceMachine": source_machine,
        "sourcePath": source_path,
        "branch": branch,
        "sourceControlSystem": source_control_system,
        "sourceControlPath": source_control_path,
        "sourceControlBaseRevision": source_control_base_revision,
        "lintStatus": lint_status,
        "unitStatus": unit_status,
        "bookmark": bookmark,
        "parentRevisionID": parent_revision_id,
        "creationMethod": creation_method,
        "authorPHID": author_phid,
        "arcanistProject": arcanist_project,
        "repositoryUUID": repository_uuid,
    }
    d = phlsys_dictutil.copy_dict_no_nones(d)
    response = conduit.call("differential.creatediff", d)
    return response


# XXX: it might be better to narrow the contract of this if the conduit
#      API is going to keep changing, don't want to fixup based on
#      changes that don't matter
def _get_diff(conduit, revision_id=None, diff_id=None):
    d = {"revision_id": revision_id, "diff_id": diff_id}
    d = phlsys_dictutil.copy_dict_no_nones(d)
    response = conduit.call("differential.getdiff", d)
    response["id"] = int(response["id"])
    return GetDiffIdResponse(**response)


def parse_commit_message(conduit, corpus, partial=None):
    d = {"corpus": corpus, "partial": partial}
    d = phlsys_dictutil.copy_dict_no_nones(d)
    p = ParseCommitMessageResponse(
        **conduit.call("differential.parsecommitmessage", d))
    phlsys_dictutil.ensure_keys_default(
        p.fields, "", ["summary", "testPlan", "title"])
    phlsys_dictutil.ensure_keys_default(
        p.fields, [], ["reviewerPHIDs"])
    return p


def create_revision(conduit, diffId, fields):
    d = {"diffid": diffId, "fields": fields}
    return RevisionResponse(
        **conduit.call("differential.createrevision", d))


def query(
        conduit,
        ids=None):  # list(uint)
    # TODO: typechecking
    d = phlsys_dictutil.copy_dict_no_nones({'ids': ids})
    response = conduit.call("differential.query", d)
    query_response_list = []
    for r in response:
        phlsys_dictutil.ensure_keys(r, ["sourcePath", "auxiliary"])
        r["id"] = int(r["id"])
        r["status"] = int(r["status"])
        query_response_list.append(QueryResponse(**r))
    return query_response_list


def get_revision_status(conduit, id):
    return query(conduit, [int(id)])[0].status


def update_revision(conduit, id, diffid, fields, message):
    d = {
        "id": id, "diffid": diffid,
        "fields": fields, "message": message
    }

    try:
        response = conduit.call('differential.updaterevision', d)
    except phlsys_conduit.ConduitException as e:
        if e.error == 'ERR_CLOSED':
            raise UpdateClosedRevisionError()
        raise

    response['revisionid'] = int(response['revisionid'])
    return RevisionResponse(**response)


def create_comment(
        conduit,
        revisionId,
        message=None,
        action=None,
        silent=None,
        attach_inlines=None):
    d = {
        "revision_id": revisionId,
        "message": message,
        "action": action,
        "silent": silent
    }
    if attach_inlines:
        d['attach_inlines'] = attach_inlines
    d = phlsys_dictutil.copy_dict_no_nones(d)
    response = conduit.call('differential.createcomment', d)
    response['revisionid'] = int(response['revisionid'])
    return RevisionResponse(**response)


def create_inline_comment(
        conduit,
        revisionId,
        file_path,
        start_line,
        message,
        is_right_side=True,
        line_count=None):
    d = {
        "revisionID": revisionId,
        "filePath": file_path,
        "content": message,
        "lineNumber": start_line,
        "isNewFile": is_right_side,
        'lineLength': line_count,
    }

    d = phlsys_dictutil.copy_dict_no_nones(d)

    conduit.call('differential.createinline', d)


def get_commit_message(conduit, revision_id):
    d = {"revision_id": revision_id}
    return conduit.call('differential.getcommitmessage', d)


def close(conduit, revisionId):
    conduit.call('differential.close', {"revisionID": revisionId})


def create_empty_revision(conduit):
    """Return the revision id of a newly created empty revision.

    :conduit: conduit to operate on
    :return: revision id

    """

    empty_diff = "diff --git a/ b/"
    diff_id = create_raw_diff(conduit, empty_diff).id
    fields = {
        "title": "empty revision",
        "testPlan": "UNTESTED",
    }

    # TODO: add support for reviewers and ccs
    # if reviewers:
    #     assert not isinstance(reviewers, types.StringTypes)
    #     fields["reviewers"] = reviewers
    # if ccs:
    #     assert not isinstance(ccs, types.StringTypes)
    #     fields["ccs"] = ccs

    revision = create_revision(conduit, diff_id, fields)

    return revision.revisionid


def update_revision_empty(conduit, revision_id):
    """Update the specified 'revision_id' with an empty diff.

    :conduit: conduit to operate on
    :revision_id: revision to update
    :return: None

    """

    empty_diff = "diff --git a/ b/"
    diff_id = create_raw_diff(conduit, empty_diff).id
    update_revision(conduit, revision_id, diff_id, [], 'update')


def get_revision_diff(conduit, revision_id):
    result = conduit.call('differential.getdiff', {'revision_id': revision_id})
    return GetDiffResponse(**result)


def get_diff(conduit, diff_id):
    result = conduit.call('differential.getdiff', {'diff_id': diff_id})
    return GetDiffResponse(**result)


def _write_hunks(hunk_list, base_path, extra_path, diff_prefix_ignore_char):

    # nothing to do if the extra path doesn't exist
    # may have been deleted or added in this diff
    if not extra_path or not hunk_list:
        return

    if len(hunk_list) > 1:
        raise WriteDiffError('partial file: {}'.format(extra_path))
    elif int(hunk_list[0]['newOffset']) != 1:
        raise WriteDiffError('partial file: {}'.format(extra_path))
    elif int(hunk_list[0]['oldOffset']) != 1:
        raise WriteDiffError('partial file: {}'.format(extra_path))

    if os.path.isabs(extra_path):
        raise WriteDiffError('refusing abs path: {}'.format(extra_path))

    path = os.path.join(base_path, extra_path)
    directory = os.path.dirname(path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(path, 'w') as outfile:
            for hunk in hunk_list:
                for line in hunk["corpus"].splitlines():
                    if line.startswith(diff_prefix_ignore_char):
                        pass
                    else:
                        print >> outfile, line[1:]
    except IOError as e:
        raise WriteDiffError(e)
    except UnicodeEncodeError as e:
        raise WriteDiffError(e)


def write_diff_files(diff_result, path):
    left_base_path = os.path.join(path, 'left')
    right_base_path = os.path.join(path, 'right')

    for change in diff_result.changes:
        hunks = change["hunks"]
        _write_hunks(hunks, left_base_path, change["oldPath"], '+')
        _write_hunks(hunks, right_base_path, change["currentPath"], '-')


#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
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
#------------------------------- END-OF-FILE ----------------------------------
