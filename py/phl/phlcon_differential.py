"""Wrapper to call Phabricator's Differential Conduit API"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
#
# Public Classes:
#   ReviewStates
#   Action
#   MessageFields
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
#   get_commit_message
#   close
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
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import phlsys_dictutil
import phlsys_namedtuple


# Enumerate the states that a Differential review can be in
## from ArcanistRevisionDifferentialStatus.php:
class ReviewStates(object):  # XXX: will derive from Enum in Python 3.4+
    needs_review = 0
    needs_revision = 1
    accepted = 2
    closed = 3
    abandoned = 4


# Enumerate the actions that can be performed on a Differential review
## from .../differential/constants/DifferentialAction.php:
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
    """@todo: Docstring for create_diff

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
    response = conduit.call('differential.updaterevision', d)
    response['revisionid'] = int(response['revisionid'])
    return RevisionResponse(**response)


def create_comment(
        conduit, revisionId, message=None, action=None, silent=None):
    d = {
        "revision_id": revisionId, "message": message,
        "action": action, "silent": silent
    }
    d = phlsys_dictutil.copy_dict_no_nones(d)
    response = conduit.call('differential.createcomment', d)
    response['revisionid'] = int(response['revisionid'])
    return RevisionResponse(**response)


def get_commit_message(conduit, revision_id):
    d = {"revision_id": revision_id}
    return conduit.call('differential.getcommitmessage', d)


def close(conduit, revisionId):
    conduit.call('differential.close', {"revisionID": revisionId})


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
