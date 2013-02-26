"""Wrapper to call Phabricator's Differential Conduit API"""

import collections
import copy
import unittest

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
    """Ensure that the dictionary has the supplied keys, initialiase them with
    a deepcopy of the supplied 'default' if not.

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
ParseCommitMessageFields = _makeNT(
    'ParseCommitMessageFields',
    'reviewerPHIDs', 'summary', 'testPlan', 'title')
RevisionResponse = _makeNT(
    'RevisionResponse',
    'revisionid', 'uri')
QueryResponse = _makeNT(
    'QueryResponse',
    'authorPHID', 'status', 'phid', 'testPlan', 'title', 'commits',
    'diffs', 'uri', 'ccs', 'dateCreated', 'lineCount', 'branch', 'reviewers',
    'id', 'statusName', 'hashes', 'summary', 'dateModified', 'sourcePath')


def createRawDiff(conduit, diff):
    response = conduit.call("differential.createrawdiff", {"diff": diff})
    return CreateRawDiffResponse(**response)


# XXX: it might be better to narrow the contract of this if the conduit
#      API is going to keep changing, don't want to fixup based on
#     changes that don't matter
def _getDiff(conduit, revisionId=None, diffId=None):
    d = {"revision_id": revisionId, "diff_id": diffId}
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
    queryResponseList = []
    for r in response:
        _ensureKeys(r, "sourcePath")
        r["id"] = int(r["id"])
        r["status"] = int(r["status"])
        queryResponseList.append(QueryResponse(**r))
    return queryResponseList


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


def close(conduit, revisionId):
    conduit.call('differential.close', {"revisionID": revisionId})


class TestDifferential(unittest.TestCase):

    def setUp(self):
        self.conduit = phlsys_conduit.Conduit(
            phlsys_conduit.Conduit.testUri)
        self.reviewerConduit = phlsys_conduit.Conduit(
            phlsys_conduit.Conduit.testUri, 'angelos')

    def testNullQuery(self):
        query(self.conduit)

    def testParseCommitMessage(self):
        title = "this is the title"
        summary = "this is the summary"
        testPlan = "this is the test plan"
        reviewers = "angelos"
        message = ""
        message += title + "\n"
        message += "\n"
        message += summary + "\n"
        message += "Test Plan: " + testPlan + "\n"
        message += "Reviewers: " + reviewers + "\n"
        parseResponse = parseCommitMessage(self.conduit, message)
        self.assertEqual(parseResponse.fields["title"], title)
        self.assertEqual(parseResponse.fields["summary"], summary)
        self.assertEqual(parseResponse.fields["testPlan"], testPlan)
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

        diffResponse = createRawDiff(self.conduit, diff)

        getDiffResponse = _getDiff(self.conduit, diffId=diffResponse.id)
        self.assertEqual(getDiffResponse.id, diffResponse.id)

        parseResponse = parseCommitMessage(self.conduit, message)
        self.assertEqual(len(parseResponse.errors), 0)

        createResponse = createRevision(
            self.conduit, diffResponse.id, parseResponse.fields)

        queryResponseList = query(self.conduit, [createResponse.revisionid])
        self.assertEqual(len(queryResponseList), 1)
        self.assertEqual(queryResponseList[0].uri, createResponse.uri)
        self.assertEqual(queryResponseList[0].id, createResponse.revisionid)
        self.assertEqual(queryResponseList[0].status, REVISION_NEEDS_REVIEW)

        diff2Response = createRawDiff(self.conduit, diff2)

        updateResponse = updateRevision(
            self.conduit,
            createResponse.revisionid, diff2Response.id,
            parseResponse.fields, "updated with new diff")
        self.assertEqual(updateResponse.revisionid, createResponse.revisionid)
        self.assertEqual(updateResponse.uri, createResponse.uri)

        commentResponse = createComment(
            self.reviewerConduit, createResponse.revisionid, action="accept")
        self.assertEqual(commentResponse.revisionid, createResponse.revisionid)
        self.assertEqual(commentResponse.uri, createResponse.uri)

        queryResponseList = query(self.conduit, [createResponse.revisionid])
        self.assertEqual(len(queryResponseList), 1)
        self.assertEqual(queryResponseList[0].uri, createResponse.uri)
        self.assertEqual(queryResponseList[0].id, createResponse.revisionid)
        self.assertEqual(queryResponseList[0].status, REVISION_ACCEPTED)

        close(self.conduit, createResponse.revisionid)

        queryResponseList = query(self.conduit, [createResponse.revisionid])
        self.assertEqual(len(queryResponseList), 1)
        self.assertEqual(queryResponseList[0].uri, createResponse.uri)
        self.assertEqual(queryResponseList[0].id, createResponse.revisionid)
        self.assertEqual(queryResponseList[0].status, REVISION_CLOSED)

if __name__ == "__main__":
    unittest.main()

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
