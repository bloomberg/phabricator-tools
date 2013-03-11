#!/usr/bin/env python
# encoding: utf-8

"""abd automates the creation and landing of reviews from branches"""

import unittest
#import sys

import phlsys_conduit
import phlsys_fs
import phlcon_differential
import phlcon_user
import phldef_conduit
import abdt_naming
import phlsys_subprocess
import phlsys_git
import phlgit_branch
import phlgit_checkout
import phlgit_config
import phlgit_diff
import phlgit_push
import phlgit_merge
import phlgit_log
import phlgitu_ref

#TODO: refactor this crazy mess
#TODO: support storing branches by status
#      e.g. dev/phab/active/* -> currently watched
#           dev/phab/badname/* -> ignored due to branch name
#           dev/phab/badmsg/* -> ignored due to improperly formatted msg
#           dev/phab/badbase/* -> ignored due to missing or invalid base


def getRemoteName():
    # not expecting this to ever be different, no magic strings just in case
    return "origin"


def getUserFromBranch(clone, conduit, base, branch):
    # TODO: this is broken, we need to raise an error if the committer isn't a
    #       user registered with the Phabricator instance
    hashes = phlgit_log.getRangeHashes(clone, base, branch)
    committers = phlgit_log.getCommittersFromHashes(clone, hashes)
    print "- committers: " + str(committers)
    users = phlcon_user.queryUsersFromEmails(conduit, committers)
    print "- users: " + str(users)
    return users[0]


def isBasedOn(name, base):
    #TODO: actually do this
    return True


def createReview(branch, remote_branches, conduit):
    remote = getRemoteName()
    rb = abdt_naming.makeReviewBranchFromName(branch)

    clone = phlsys_git.GitClone(".")
    if rb.base not in remote_branches:
        raise Exception("base does not exist:" + rb.base)
    if not isBasedOn(branch, rb.base):
        raise Exception("'" + branch + "' is not based on '" + rb.base + "'")
    remoteBase = phlgitu_ref.makeRemote(rb.base, remote)
    remoteBranch = phlgitu_ref.makeRemote(branch, remote)
    user = getUserFromBranch(clone, conduit, remoteBase, remoteBranch)
    print "- author: " + user
#   if not arc.isValidUser(user):
#       raise Exception("'" + name + "' is not a user")

    phlgit_checkout.newBranchForceBasedOn(clone, branch, remoteBranch)
    d = phlcon_differential

    rawDiff = phlgit_diff.rawDiffRange(clone, remoteBase, remoteBranch)
    message = makeMessageDigest(clone, remoteBase, remoteBranch)
    parsed = d.parseCommitMessage(conduit, message)
    if parsed.errors:
        raise Exception(
            "Errors parsing commit messages: " + str(parsed.errors))

    with phlsys_conduit.actAsUser(conduit, user):
        print "- creating diff"
        diffid = d.createRawDiff(conduit, rawDiff).id

        print "- creating revision"
        review = d.createRevision(conduit, diffid, parsed.fields)
        print "- created " + str(review.revisionid)

        workingBranch = abdt_naming.makeWorkingBranchName(
            rb.description, rb.base, review.revisionid)
        print "- pushing working branch: " + workingBranch
        phlgit_push.pushAsymmetrical(clone, branch, workingBranch, remote)

    print "- commenting on " + str(review.revisionid)
    createMessage = ""
    createMessage += "i created this from " + branch + ".\n"
    createMessage += " pushed to " + workingBranch + "."
    d.createComment(
        conduit, review.revisionid, message=createMessage, silent=True)


def makeMessageDigest(clone, remoteBase, remoteBranch):
    hashes = phlgit_log.getRangeHashes(clone, remoteBase, remoteBranch)
    revisions = phlgit_log.makeRevisionsFromHashes(clone, hashes)
    message = revisions[0].subject + "\n\n"
    for r in revisions:
        message += r.message
    return message


def updateCommitMessageFields(earlier, later):
    """Return an updated 'CommitMessageFields' based on the 'earlier' version
    being updated by the 'later' version. If the earlier or later are None then
    the non-None one is returned.

    :earlier: a phlcon_differential.ParseCommitMessageFields
    :later: a phlcon_differential.ParseCommitMessageFields
    :returns: the updated phlcon_differential.ParseCommitMessageFields

    """
    ParseCommitMessageFields = phlcon_differential.ParseCommitMessageFields

    if earlier is None and later is not None:
        assert(isinstance(later, ParseCommitMessageFields))
        return later

    if earlier is not None and later is None:
        assert(isinstance(earlier, ParseCommitMessageFields))
        return earlier

    assert(isinstance(earlier, ParseCommitMessageFields))
    assert(isinstance(later, ParseCommitMessageFields))
    title = earlier.title
    summary = earlier.summary
    if later.summary:
        summary += "\n" + later.summary
    reviewers = set(earlier.reviewerPHIDs)
    reviewers |= set(later.reviewerPHIDs)
    reviewers = list(reviewers)
    testPlan = earlier.testPlan
    if later.testPlan:
        testPlan += "\n" + later.testPlan
    return ParseCommitMessageFields(
        title=title,
        summary=summary,
        reviewerPHIDs=reviewers,
        testPlan=testPlan)


def updateReview(branch, workingBranch, remote_branches, conduit):
    wb = abdt_naming.makeWorkingBranchFromName(workingBranch)
    remote = getRemoteName()
    remoteBranch = phlgitu_ref.makeRemote(branch, remote)
    remoteWorking = phlgitu_ref.makeRemote(wb.full_name, remote)
    remoteBase = phlgitu_ref.makeRemote(wb.base, remote)

    clone = phlsys_git.GitClone(".")

    if not phlgit_branch.isIdentical(clone, remoteBranch, remoteWorking):
        if wb.base not in remote_branches:
            raise Exception("base does not exist:" + wb.base)
        if not isBasedOn(remoteBranch, remoteBase):
            raise Exception(
                "'" + remoteBranch + "' is not based on '" + wb.base + "'")

        update(conduit, remote, wb, clone, remoteBranch)
    else:
        phlgit_checkout.newBranchForceBasedOn(
            clone, workingBranch, remoteWorking)

        if wb.base not in remote_branches:
            raise Exception("base does not exist:" + wb.base)

        d = phlcon_differential
        status = d.getRevisionStatus(conduit, wb.id)
        if int(status) == d.REVISION_ACCEPTED:
            land(conduit, remote, wb, clone, remoteWorking, remoteBase, branch)
            # TODO: we probably want to do a better job of cleaning up locally
        else:
            print "do nothing"


def update(conduit, remote, wb, clone, remoteBranch):
    remoteBase = phlgitu_ref.makeRemote(wb.base, remote)
    user = getUserFromBranch(clone, conduit, remoteBase, remoteBranch)

    print "update"

    print "- creating diff"
    rawDiff = phlgit_diff.rawDiffRange(clone, remoteBase, remoteBranch)

    d = phlcon_differential
    with phlsys_conduit.actAsUser(conduit, user):
        diffid = d.createRawDiff(conduit, rawDiff).id

        print "- updating revision " + str(wb.id)
        hashes = phlgit_log.getRangeHashes(clone, remoteBase, remoteBranch)
        revisions = phlgit_log.makeRevisionsFromHashes(clone, hashes)
        fields = None
        for r in revisions:
            p = d.parseCommitMessage(
                conduit, r.subject + "\n\n" + r.message)
            f = phlcon_differential.ParseCommitMessageFields(**p.fields)
            fields = updateCommitMessageFields(fields, f)
        d.updateRevision(
            conduit, wb.id, diffid, fields._asdict(), "update")

    phlgit_push.pushAsymmetricalForce(
        clone, remoteBranch, wb.full_name, remote)

    print "- commenting on revision " + str(wb.id)
    updateMessage = ""
    updateMessage += "i updated this from " + wb.full_name + ".\n"
    updateMessage += "pushed to " + wb.full_name + "."
    d.createComment(
        conduit, wb.id, message=updateMessage, silent=True)


def land(conduit, remote, wb, clone, remoteWorking, remoteBase, branch):
    print "landing " + remoteWorking + " onto " + remoteBase
    user = getUserFromBranch(clone, conduit, remoteBase, remoteWorking)
    d = phlcon_differential
    with phlsys_conduit.actAsUser(conduit, user):
        phlgit_checkout.newBranchForceBasedOn(clone, wb.base, remoteBase)

        # compose the commit message
        info = d.query(conduit, [wb.id])[0]
        message = ""
        message += info.title
        if info.summary.strip():
            message += "\n"
            message += "\n" + info.summary
        message += "\n"
        message += "\nTest plan:"
        message += "\n" + info.testPlan
        message += "\n"
        userNames = phlcon_user.queryUsernamesFromPhids(
            conduit, info.reviewers)
        message += "\nReviewers: " + ','.join(userNames)
        message += "\nDifferential Revision: " + info.uri

        squashMessage = phlgit_merge.squash(
            clone, remoteWorking, message)
        print "- pushing " + remoteBase
        phlgit_push.push(clone, wb.base, remote)
        print "- deleting " + wb.full_name
        phlgit_push.delete(clone, wb.full_name, remote)
        print "- deleting " + branch
        phlgit_push.delete(clone, branch, remote)

    print "- commenting on revision " + str(wb.id)
    closeMessage = ""
    closeMessage += "i landed this on " + wb.base + ".\n"
    closeMessage += "deleted " + wb.full_name + "\n"
    closeMessage += "deleted " + branch + "."
    d.createComment(
        conduit, wb.id, message=closeMessage, silent=True)
    d.createComment(
        conduit, wb.id, message=squashMessage, silent=True)

    with phlsys_conduit.actAsUser(conduit, user):
        d.close(conduit, wb.id)
    # TODO: we probably want to do a better job of cleaning up locally


def processUpdatedRepo(path, conduit):
    with phlsys_fs.chDirContext(path):
        clone = phlsys_git.GitClone(".")
        remote = phlgit_branch.getRemote(clone, getRemoteName())
        wbList = abdt_naming.getWorkingBranches(remote)
        makeRb = abdt_naming.makeReviewBranchNameFromWorkingBranch
        rbDict = dict((makeRb(wb), wb.full_name) for wb in wbList)
        for b in remote:
            if abdt_naming.isReviewBranchName(b):
                if b not in rbDict.keys():
                    print "create review for " + b
                    createReview(b, remote, conduit)
                else:
                    print "update review for " + b
                    updateReview(b, rbDict[b], remote, conduit)


def runCommands(*commands):
    phlsys_subprocess.runCommands(*commands)


# TODO: break this down
class TestAbd(unittest.TestCase):

    def _gitCommitAll(self, subject, testPlan, reviewers):
        message = ""
        message += subject + "\n\n"
        message += "Test Plan: " + testPlan + "\n"
        message += "Reviewers: " + reviewers
        phlsys_subprocess.run("git", "commit", "-a", "-F", "-", stdin=message)

    def _createCommitNewFile(self, filename, reviewers):
        runCommands("touch " + filename)
        runCommands("git add " + filename)
        self._gitCommitAll("add " + filename, "test plan", reviewers)

    def _createCommitNewFileNoReviewer(self, filename):
        runCommands("touch " + filename)
        runCommands("git add " + filename)
        phlsys_subprocess.run("git", "commit", "-a", "-F", "-", stdin=filename)

    def setUp(self):
        self.reviewer = phldef_conduit.alice.user
        #TODO: just make a temp dir
        runCommands("rm -rf abd-test")
        runCommands("mkdir abd-test")
        with phlsys_fs.chDirContext("abd-test"):
            runCommands(
                "git --git-dir=devgit init --bare",
                "git clone --mirror devgit mirror",
                "git clone devgit developer",
                "git clone mirror phab",
            )

            devClone = phlsys_git.GitClone("developer")
            phlgit_config.setUsernameEmail(
                devClone,
                phldef_conduit.bob.user,
                phldef_conduit.bob.email)

            with phlsys_fs.chDirContext("developer"):
                self._createCommitNewFile("README", self.reviewer)

                runCommands("git checkout -b ph-review/change/master")
                self._createCommitNewFile("NEWFILE", self.reviewer)

                runCommands("git push origin master")
                runCommands("git push -u origin ph-review/change/master")

            with phlsys_fs.chDirContext("mirror"):
                runCommands("git remote update")

            with phlsys_fs.chDirContext("phab"):
                runCommands("git remote rename origin mirror")
                runCommands("git remote add origin ../devgit")
                runCommands("git fetch origin -p")

    def test_simpleWorkflow(self):
        with phlsys_fs.chDirContext("abd-test"):
            conduit = phlsys_conduit.Conduit(
                phldef_conduit.test_uri,
                phldef_conduit.phab.user,
                phldef_conduit.phab.certificate)

            # create the review
            processUpdatedRepo("phab", conduit)

            # update the review with a new revision
            with phlsys_fs.chDirContext("developer"):
                self._createCommitNewFileNoReviewer("NEWFILE2")
                runCommands("git push -u origin ph-review/change/master")
            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")
            processUpdatedRepo("phab", conduit)

            # accept the review
            with phlsys_fs.chDirContext("phab"):
                clone = phlsys_git.GitClone(".")
                branches = phlgit_branch.getRemote(clone, "origin")
            wbList = abdt_naming.getWorkingBranches(branches)
            self.assertEqual(len(wbList), 1)
            wb = wbList[0]
            with phlsys_conduit.actAsUser(conduit, self.reviewer):
                phlcon_differential.createComment(
                    conduit, wb.id, action="accept")

            processUpdatedRepo("phab", conduit)

    def tearDown(self):
        #TODO: comment this back in
        #runCommands("rm -rf abd-test")
        pass


if __name__ == "__main__":
    unittest.main()
