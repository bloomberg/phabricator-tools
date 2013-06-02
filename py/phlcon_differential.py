"""Wrapper to call Phabricator's Differential Conduit API"""

import collections
import copy
import unittest

import phldef_conduit
import phlsys_conduit

# from ArcanistRevisionDifferentialStatus.php:
# const NEEDS_REVIEW      = 0;
# const NEEDS_REVISION    = 1;
# const ACCEPTED          = 2;
# const CLOSED            = 3;
# const ABANDONED         = 4;
# TODO: look into some sort of const protection for these
REVISION_NEEDS_REVIEW = 0
REVISION_NEEDS_REVISION = 1
REVISION_ACCEPTED = 2
REVISION_CLOSED = 3
REVISION_ABANDONED = 4

# from .../differential/constants/DifferentialAction.php:
# const ACTION_CLOSE          = 'commit';
# const ACTION_COMMENT        = 'none';
# const ACTION_ACCEPT         = 'accept';
# const ACTION_REJECT         = 'reject';
# const ACTION_RETHINK        = 'rethink';
# const ACTION_ABANDON        = 'abandon';
# const ACTION_REQUEST        = 'request_review';
# const ACTION_RECLAIM        = 'reclaim';
# const ACTION_UPDATE         = 'update';
# const ACTION_RESIGN         = 'resign';
# const ACTION_SUMMARIZE      = 'summarize';
# const ACTION_TESTPLAN       = 'testplan';
# const ACTION_CREATE         = 'create';
# const ACTION_ADDREVIEWERS   = 'add_reviewers';
# const ACTION_ADDCCS         = 'add_ccs';
# const ACTION_CLAIM          = 'claim';
# const ACTION_REOPEN         = 'reopen';
ACTION_CLOSE = 'commit'
ACTION_COMMENT = 'none'
ACTION_ACCEPT = 'accept'
ACTION_REJECT = 'reject'
ACTION_RETHINK = 'rethink'
ACTION_ABANDON = 'abandon'
ACTION_REQUEST = 'request_review'
ACTION_RECLAIM = 'reclaim'
ACTION_UPDATE = 'update'
ACTION_RESIGN = 'resign'
ACTION_SUMMARIZE = 'summarize'
ACTION_TESTPLAN = 'testplan'
ACTION_CREATE = 'create'
ACTION_ADDREVIEWERS = 'add_reviewers'
ACTION_ADDCCS = 'add_ccs'
ACTION_CLAIM = 'claim'
ACTION_REOPEN = 'reopen'

AUTHOR_ACTIONS = {
    "close": ACTION_CLOSE,
    "comment": ACTION_COMMENT,
    "plan changes": ACTION_RETHINK,
    "abandon": ACTION_ABANDON,
    "request review": ACTION_REQUEST,
    "unabandon": ACTION_RECLAIM,
    "reopen": ACTION_REOPEN
}

REVIEWER_ACTIONS = {
    "comment": ACTION_COMMENT,
    "accept": ACTION_ACCEPT,
    "request changes": ACTION_REJECT,
    "resign as reviewer": ACTION_RESIGN,
    "commandeer": ACTION_CLAIM,
}

USER_ACTIONS = dict(AUTHOR_ACTIONS.items() + REVIEWER_ACTIONS.items())


# from phabricator/.../...DefaultFieldSelector.php
class MessageFields(object):
    title = "title"
    summary = "summary"
    test_plan = "testPlan"
    reviewer_phids = "reviewerPHIDs"
    cc_phids = "ccPHIDs"


def _makeNT(name, *fields):
    return collections.namedtuple(
        'phlcon_differential__' + name,
        fields)


def _copyDictNoNones(d):
    clean = {}
    clean.update((k, v) for k, v in d.iteritems() if v is not None)
    return clean


def _ensureKeys(d, *keys):
    for k in keys:
        if k not in d:
            d[k] = None


def _ensureKeysDefault(dic, default, *keys):
    """Ensure that the dictionary has the supplied keys.

    Initialiase them with a deepcopy of the supplied 'default' if not.

    :dic: the dictionary to modify
    :default: the default value (will be deep copied)
    :*keys: the keys to ensure
    :returns: None

    """
    for k in keys:
        if k not in dic:
            dic[k] = copy.deepcopy(default)

CreateRawDiffResponse = _makeNT('CreateRawDiffResponse', 'id', 'uri')
GetDiffIdResponse = _makeNT(
    'GetDiffIdResponse',
    'parent', 'properties', 'sourceControlSystem', 'sourceControlPath',
    'dateCreated', 'dateModified', 'lintStatus', 'bookmark', 'changes',
    'revisionID', 'sourceControlBaseRevision', 'branch',
    'projectName', 'unitStatus', 'creationMethod', 'id', 'description')
ParseCommitMessageResponse = _makeNT(
    'ParseCommitMessageResponse',
    'fields', 'errors')
RevisionResponse = _makeNT(
    'RevisionResponse',
    'revisionid', 'uri')
QueryResponse = _makeNT(
    'QueryResponse',
    'authorPHID', 'status', 'phid', 'testPlan', 'title', 'commits',
    'diffs', 'uri', 'ccs', 'dateCreated', 'lineCount', 'branch', 'reviewers',
    'id', 'statusName', 'hashes', 'summary', 'dateModified', 'sourcePath',
    'auxiliary')


def createRawDiff(conduit, diff):
    response = conduit.call("differential.createrawdiff", {"diff": diff})
    return CreateRawDiffResponse(**response)


def createDiff(
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
    """@todo: Docstring for createDiff

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
    d = _copyDictNoNones(d)
    response = conduit.call("differential.creatediff", d)
    return response


# XXX: it might be better to narrow the contract of this if the conduit
#      API is going to keep changing, don't want to fixup based on
#      changes that don't matter
def _getDiff(conduit, revision_id=None, diff_id=None):
    d = {"revision_id": revision_id, "diff_id": diff_id}
    d = _copyDictNoNones(d)
    response = conduit.call("differential.getdiff", d)
    response["id"] = int(response["id"])
    return GetDiffIdResponse(**response)


def parseCommitMessage(conduit, corpus, partial=None):
    d = {"corpus": corpus, "partial": partial}
    d = _copyDictNoNones(d)
    p = ParseCommitMessageResponse(
        **conduit.call("differential.parsecommitmessage", d))
    _ensureKeysDefault(
        p.fields, "", "summary", "testPlan", "title")
    _ensureKeysDefault(
        p.fields, [], "reviewerPHIDs")
    return p


def createRevision(conduit, diffId, fields):
    d = {"diffid": diffId, "fields": fields}
    return RevisionResponse(
        **conduit.call("differential.createrevision", d))


def query(
        conduit,
        ids=None):  # list(uint)
    # TODO: typechecking
    d = _copyDictNoNones({'ids': ids})
    response = conduit.call("differential.query", d)
    query_response_list = []
    for r in response:
        _ensureKeys(r, "sourcePath", "auxiliary")
        r["id"] = int(r["id"])
        r["status"] = int(r["status"])
        query_response_list.append(QueryResponse(**r))
    return query_response_list


def getRevisionStatus(conduit, id):
    return query(conduit, [int(id)])[0].status


def updateRevision(conduit, id, diffid, fields, message):
    d = {
        "id": id, "diffid": diffid,
        "fields": fields, "message": message
    }
    response = conduit.call('differential.updaterevision', d)
    response['revisionid'] = int(response['revisionid'])
    return RevisionResponse(**response)


def createComment(conduit, revisionId, message=None, action=None, silent=None):
    d = {
        "revision_id": revisionId, "message": message,
        "action": action, "silent": silent
    }
    d = _copyDictNoNones(d)
    response = conduit.call('differential.createcomment', d)
    response['revisionid'] = int(response['revisionid'])
    return RevisionResponse(**response)


def getCommitMessage(conduit, revision_id):
    d = {"revision_id": revision_id}
    return conduit.call('differential.getcommitmessage', d)


def close(conduit, revisionId):
    conduit.call('differential.close', {"revisionID": revisionId})


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.conduit = None
        self.reviewerConduit = None

    def setUp(self):
        test_data = phldef_conduit
        self.conduit = phlsys_conduit.Conduit(
            test_data.test_uri,
            test_data.alice.user,
            test_data.alice.certificate)

        self.reviewerConduit = phlsys_conduit.Conduit(
            test_data.test_uri,
            test_data.bob.user,
            test_data.bob.certificate)

    def testNullQuery(self):
        query(self.conduit)

    def testParseCommitMessage(self):
        title = "this is the title"
        summary = "this is the summary"
        test_plan = "this is the test plan"
        reviewers = "bob"
        message = ""
        message += title + "\n"
        message += "\n"
        message += summary + "\n"
        message += "Test Plan: " + test_plan + "\n"
        message += "Reviewers: " + reviewers + "\n"
        parse_response = parseCommitMessage(self.conduit, message)
        self.assertEqual(parse_response.fields["title"], title)
        self.assertEqual(parse_response.fields["summary"], summary)
        self.assertEqual(parse_response.fields["testPlan"], test_plan)
        # XXX: can't check reviewerPHIDs at this point

    def testCreateCloseRawDiffRevision(self):
        diff = """
diff --git a/readme b/readme
index d4711bb..ee5b241 100644
--- a/readme
+++ b/readme
@@ -7,3 +7,4 @@ and one more!!
 -- and one last(?) one
 alaric!
 local stuff!
+manual conduit submission
"""
        message = """
add a line to README

Test Plan: I proof-read it and it looked ok
"""

        diff2 = """
diff --git a/readme b/readme
index d4711bb..1c634f5 100644
--- a/readme
+++ b/readme
@@ -7,3 +7,5 @@ and one more!!
 -- and one last(?) one
 alaric!
 local stuff!
+manual conduit submission
+another line
"""

        diff_response = createRawDiff(self.conduit, diff)

        get_diff_response = _getDiff(self.conduit, diff_id=diff_response.id)
        self.assertEqual(get_diff_response.id, diff_response.id)

        parse_response = parseCommitMessage(self.conduit, message)
        self.assertEqual(len(parse_response.errors), 0)

        create_response = createRevision(
            self.conduit, diff_response.id, parse_response.fields)

        query_response_list = query(self.conduit, [create_response.revisionid])
        self.assertEqual(len(query_response_list), 1)
        self.assertEqual(query_response_list[0].uri, create_response.uri)
        self.assertEqual(query_response_list[0].id, create_response.revisionid)
        self.assertEqual(query_response_list[0].status, REVISION_NEEDS_REVIEW)

        diff2_response = createRawDiff(self.conduit, diff2)

        update_response = updateRevision(
            self.conduit,
            create_response.revisionid, diff2_response.id,
            parse_response.fields, "updated with new diff")
        self.assertEqual(
            update_response.revisionid, create_response.revisionid)
        self.assertEqual(update_response.uri, create_response.uri)

        comment_response = createComment(
            self.reviewerConduit, create_response.revisionid, action="accept")
        self.assertEqual(
            comment_response.revisionid, create_response.revisionid)
        self.assertEqual(comment_response.uri, create_response.uri)

        query_response_list = query(self.conduit, [create_response.revisionid])
        self.assertEqual(len(query_response_list), 1)
        self.assertEqual(query_response_list[0].uri, create_response.uri)
        self.assertEqual(query_response_list[0].id, create_response.revisionid)
        self.assertEqual(query_response_list[0].status, REVISION_ACCEPTED)

        close(self.conduit, create_response.revisionid)

        query_response_list = query(self.conduit, [create_response.revisionid])
        self.assertEqual(len(query_response_list), 1)
        self.assertEqual(query_response_list[0].uri, create_response.uri)
        self.assertEqual(query_response_list[0].id, create_response.revisionid)
        self.assertEqual(query_response_list[0].status, REVISION_CLOSED)

    def testCreateDiffRevision(self):
        diff = """
diff --git a/readme b/readme
index d4711bb..ee5b241 100644
--- a/readme
+++ b/readme
@@ -1,3 +1,4 @@ and one more!!
 -- and one last(?) one
 alaric!
 local stuff!
+manual conduit submission
"""
        message = """
add a line to README

Test Plan: I proof-read it and it looked ok
"""
        raw_diff_response = createRawDiff(self.conduit, diff)
        get_diff_response = _getDiff(
            self.conduit,
            diff_id=raw_diff_response.id)

        diff_response = createDiff(
            self.conduit,
            changes_dict=get_diff_response.changes,
            source_machine="test_machine",
            source_path="source_path",
            branch="branch",
            source_control_system="git",  # svn or git
            source_control_path="control_path",
            source_control_base_revision="0",
            lint_status="none",
            unit_status="none",
            bookmark=None,
            parent_revision_id=None,
            creation_method="arcanist daemon",
            author_phid=None,
            arcanist_project="project",
            repository_uuid=None)

        parse_response = parseCommitMessage(self.conduit, message)
        self.assertEqual(len(parse_response.errors), 0)

        # rely on createRevision to raise if we get anything seriously wrong
        createRevision(
            self.conduit, diff_response["diffid"], parse_response.fields)

    def _createRevision(self, title):
        diff = """diff --git a/ b/"""
        message = title + "\n\ntest plan: no test plan"
        diff_response = createRawDiff(self.conduit, diff)
        parse_response = parseCommitMessage(self.conduit, message)
        create_response = createRevision(
            self.conduit, diff_response.id, parse_response.fields)
        return create_response.revisionid

    def _authorCommentAction(self, revisionid, action):
        createComment(self.conduit, revisionid, action=action)

    def _reviewCommentAction(self, revisionid, action):
        createComment(self.reviewerConduit, revisionid, action=action)

    def _getState(self, revisionid):
        return query(self.conduit, [revisionid])[0].status

    def _authorActExp(self, revisionid, action, state):
        self._authorCommentAction(revisionid, action)
        self.assertEqual(self._getState(revisionid), state)

    def _reviewActExp(self, revisionid, action, state):
        self._reviewCommentAction(revisionid, action)
        self.assertEqual(self._getState(revisionid), state)

    def testReviewStates(self):
        revisionid = self._createRevision("testReviewStates")
        self._authorActExp(revisionid, ACTION_RETHINK, REVISION_NEEDS_REVISION)
        self._authorActExp(revisionid, ACTION_REQUEST, REVISION_NEEDS_REVIEW)
        self._authorActExp(revisionid, ACTION_ABANDON, REVISION_ABANDONED)
        self._authorActExp(revisionid, ACTION_RECLAIM, REVISION_NEEDS_REVIEW)

        self._reviewActExp(revisionid, ACTION_REJECT, REVISION_NEEDS_REVISION)
        self._reviewActExp(revisionid, ACTION_ACCEPT, REVISION_ACCEPTED)
        self._reviewActExp(revisionid, ACTION_REJECT, REVISION_NEEDS_REVISION)
        self._reviewActExp(revisionid, ACTION_ACCEPT, REVISION_ACCEPTED)

        self._authorActExp(revisionid, ACTION_CLOSE, REVISION_CLOSED)

    def testUpdateNoFields(self):
        revisionid = self._createRevision("testUpdateNoFields")
        diff = """diff --git a/ b/"""
        diff_response = createRawDiff(self.conduit, diff)
        updateRevision(
            self.conduit, revisionid, diff_response.id, [], "update")

    def testUpdateStrangeFields(self):
        revisionid = self._createRevision("testUpdateStrangeFields")
        message = "test\n\nmeh: blah\nstrange: blah\n123: blah\ntest plan: hmm"
        diff = """diff --git a/ b/"""
        diff_response = createRawDiff(self.conduit, diff)
        parse_response = parseCommitMessage(self.conduit, message)
        print str(parse_response.fields)
        updateRevision(
            self.conduit,
            revisionid,
            diff_response.id,
            parse_response.fields,
            "update")
        # TODO: check that the strange fields appear in the summary field

    def testCanGetCommitMessage(self):
        revisionid = self._createRevision("testUpdateStrangeFields")
        getCommitMessage(self.conduit, revisionid)


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
