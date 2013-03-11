#!/usr/bin/env python
# encoding: utf-8

"""abd automates the creation and landing of reviews from branches"""

import collections
import unittest

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


GitReviewBranch = collections.namedtuple(
    "abdcmd_default__GitReviewBranch", [
        "branch",
        "description",
        "base",
        "remote_base",
        "remote_branch"])

GitWorkingBranch = collections.namedtuple(
    "abdcmd_default__GitWorkingBranch", [
        "branch",
        "description",
        "base",
        "id",
        "remote_base",
        "remote_branch"])

CloneContext = collections.namedtuple(
    "abdcmd_default__GitClone", [
        "clone",
        "remote",
        "branches"])


def makeGitReviewBranch(review_branch, remote):
    """Return a GitReviewBranch based on a abdt_naming.ReviewBranch and remote.

    :review_branch: an abdt_naming.ReviewBranch to base this on
    :remote: the name of the remote to use
    :returns: a GitReviewBranch

    """
    makeRemote = phlgitu_ref.makeRemote
    return GitReviewBranch(
        branch=review_branch.full_name,
        description=review_branch.description,
        base=review_branch.base,
        remote_base=makeRemote(review_branch.base, remote),
        remote_branch=makeRemote(review_branch.full_name, remote))


def makeGitWorkingBranch(working_branch, remote):
    """Return GitWorkingBranch based on a abdt_naming.WorkingBranch and remote.

    :working_branch: an abdt_naming.WorkingBranch to base this on
    :remote: the name of the remote to use
    :returns: a GitWorkingBranch

    """
    makeRemote = phlgitu_ref.makeRemote
    return GitWorkingBranch(
        branch=working_branch.full_name,
        description=working_branch.description,
        base=working_branch.base,
        id=working_branch.id,
        remote_base=makeRemote(working_branch.base, remote),
        remote_branch=makeRemote(working_branch.full_name, remote))


def getPrimaryUserFromBranch(clone, conduit, base, branch):
    # TODO: this is broken, we need to raise an error if the committer isn't a
    #       user registered with the Phabricator instance
    hashes = phlgit_log.getRangeHashes(clone, base, branch)
    committers = phlgit_log.getCommittersFromHashes(clone, hashes)
    print "- committers: " + str(committers)
    users = phlcon_user.queryUsersFromEmails(conduit, committers)
    print "- users: " + str(users)
    primary_user = users[0]
    if not primary_user:
        raise Exception("first committer is not a Phabricator user")
    return primary_user


def isBasedOn(name, base):
    #TODO: actually do this
    return True


def createReview(conduit, cloneContext, review_branch):

    user, parsed, rawDiff = getReviewParams(
        conduit, cloneContext, review_branch)

    createDifferentialReview(
        conduit, user, parsed, cloneContext, review_branch, rawDiff)


def getReviewParams(conduit, cloneContext, review_branch):
    clone = cloneContext.clone
    if review_branch.base not in cloneContext.branches:
        raise Exception("base does not exist:" + review_branch.base)
    if not isBasedOn(review_branch.branch, review_branch.base):
        raise Exception(
            "'" + review_branch.branch +
            "' is not based on '" + review_branch.base + "'")
    user = getPrimaryUserFromBranch(
        clone, conduit, review_branch.remote_base, review_branch.remote_branch)
    print "- author: " + user

    message = makeMessageDigest(
        clone, review_branch.remote_base, review_branch.remote_branch)
    parsed = phlcon_differential.parseCommitMessage(conduit, message)
    if parsed.errors:
        raise Exception(
            "Errors parsing commit messages: " + str(parsed.errors))

    rawDiff = phlgit_diff.rawDiffRange(
        clone, review_branch.remote_base, review_branch.remote_branch)

    return user, parsed, rawDiff


def createDifferentialReview(
        conduit, user, parsed, cloneContext, review_branch, rawDiff):
    clone = cloneContext.clone
    phlgit_checkout.newBranchForceBasedOn(
        clone, review_branch.branch, review_branch.remote_branch)

    with phlsys_conduit.actAsUserContext(conduit, user):
        print "- creating diff"
        diffid = phlcon_differential.createRawDiff(conduit, rawDiff).id

        print "- creating revision"
        review = phlcon_differential.createRevision(
            conduit, diffid, parsed.fields)
        print "- created " + str(review.revisionid)

        workingBranch = abdt_naming.makeWorkingBranchName(
            abdt_naming.WB_STATUS_OK,
            review_branch.description,
            review_branch.base,
            review.revisionid)

        print "- pushing working branch: " + workingBranch
        phlgit_push.pushAsymmetrical(
            clone, review_branch.branch, workingBranch, cloneContext.remote)

    print "- commenting on " + str(review.revisionid)
    createMessage = ""
    createMessage += "i created this from " + review_branch.branch + ".\n"
    createMessage += " pushed to " + workingBranch + "."
    phlcon_differential.createComment(
        conduit, review.revisionid, message=createMessage, silent=True)


def makeMessageDigest(clone, base, branch):
    hashes = phlgit_log.getRangeHashes(clone, base, branch)
    revisions = phlgit_log.makeRevisionsFromHashes(clone, hashes)
    message = revisions[0].subject + "\n\n"
    for r in revisions:
        message += r.message
    return message


def updateCommitMessageFields(earlier, later):
    """Return an updated 'CommitMessageFields' based on the 'earlier' version.

    Apply the 'later' version as an update to the 'earlier' one.

    If either the earlier or later are None then the non-None one is returned.

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


def updateReview(conduit, cloneContext, reviewBranch, workingBranch):
    rb = reviewBranch
    wb = workingBranch

    clone = cloneContext.clone
    isBranchIdentical = phlgit_branch.isIdentical
    if not isBranchIdentical(clone, rb.remote_branch, wb.remote_branch):
        if wb.base not in cloneContext.branches:
            raise Exception("base does not exist:" + wb.base)
        if not isBasedOn(rb.remote_branch, wb.remote_base):
            raise Exception(
                "'" + rb.remote_branch + "' is not based on '" + wb.base + "'")

        update(conduit, wb, cloneContext, rb.remote_branch)
    else:
        if wb.base not in cloneContext.branches:
            raise Exception("base does not exist:" + wb.base)

        d = phlcon_differential
        status = d.getRevisionStatus(conduit, wb.id)
        if int(status) == d.REVISION_ACCEPTED:
            land(conduit, wb, cloneContext, reviewBranch.branch)
            # TODO: we probably want to do a better job of cleaning up locally
        else:
            print "do nothing"


def update(conduit, wb, cloneContext, remoteBranch):
    clone = cloneContext.clone
    user = getPrimaryUserFromBranch(
        clone, conduit, wb.remote_base, remoteBranch)

    print "update"

    print "- creating diff"
    rawDiff = phlgit_diff.rawDiffRange(clone, wb.remote_base, remoteBranch)

    d = phlcon_differential
    with phlsys_conduit.actAsUserContext(conduit, user):
        diffid = d.createRawDiff(conduit, rawDiff).id

        print "- updating revision " + str(wb.id)
        hashes = phlgit_log.getRangeHashes(clone, wb.remote_base, remoteBranch)
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
        clone, remoteBranch, wb.branch, cloneContext.remote)

    print "- commenting on revision " + str(wb.id)
    updateMessage = ""
    updateMessage += "i updated this from " + wb.branch + ".\n"
    updateMessage += "pushed to " + wb.branch + "."
    d.createComment(
        conduit, wb.id, message=updateMessage, silent=True)


def land(conduit, wb, cloneContext, branch):
    clone = cloneContext.clone
    print "landing " + wb.remote_branch + " onto " + wb.remote_base
    user = getPrimaryUserFromBranch(
        clone, conduit, wb.remote_base, wb.remote_branch)
    d = phlcon_differential
    with phlsys_conduit.actAsUserContext(conduit, user):
        phlgit_checkout.newBranchForceBasedOn(clone, wb.base, wb.remote_base)

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
            clone, wb.remote_branch, message)
        print "- pushing " + wb.remote_base
        phlgit_push.push(clone, wb.base, cloneContext.remote)
        print "- deleting " + wb.branch
        phlgit_push.delete(clone, wb.branch, cloneContext.remote)
        print "- deleting " + branch
        phlgit_push.delete(clone, branch, cloneContext.remote)

    print "- commenting on revision " + str(wb.id)
    closeMessage = ""
    closeMessage += "i landed this on " + wb.base + ".\n"
    closeMessage += "deleted " + wb.branch + "\n"
    closeMessage += "deleted " + branch + "."
    d.createComment(
        conduit, wb.id, message=closeMessage, silent=True)
    d.createComment(
        conduit, wb.id, message=squashMessage, silent=True)

    with phlsys_conduit.actAsUserContext(conduit, user):
        d.close(conduit, wb.id)
    # TODO: we probably want to do a better job of cleaning up locally


def processUpdatedRepo(conduit, path, remote):
    with phlsys_fs.chDirContext(path):
        clone = phlsys_git.GitClone(".")
        remote_branches = phlgit_branch.getRemote(clone, remote)
        cloneContext = CloneContext(clone, remote, remote_branches)
        wbList = abdt_naming.getWorkingBranches(remote_branches)
        makeRb = abdt_naming.makeReviewBranchNameFromWorkingBranch
        rbDict = dict((makeRb(wb), wb) for wb in wbList)
        for b in remote_branches:
            if abdt_naming.isReviewBranchName(b):
                review_branch = abdt_naming.makeReviewBranchFromName(b)
                review_branch = makeGitReviewBranch(review_branch, remote)
                if b not in rbDict.keys():
                    print "create review for " + b
                    createReview(conduit, cloneContext, review_branch)
                else:
                    print "update review for " + b
                    working_branch = rbDict[b]
                    working_branch = makeGitWorkingBranch(
                        working_branch, remote)
                    updateReview(
                        conduit, cloneContext, review_branch, working_branch)


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
            processUpdatedRepo(conduit, "phab", "origin")

            # update the review with a new revision
            with phlsys_fs.chDirContext("developer"):
                self._createCommitNewFileNoReviewer("NEWFILE2")
                runCommands("git push -u origin ph-review/change/master")
            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")
            processUpdatedRepo(conduit, "phab", "origin")

            # accept the review
            with phlsys_fs.chDirContext("phab"):
                clone = phlsys_git.GitClone(".")
                branches = phlgit_branch.getRemote(clone, "origin")
            wbList = abdt_naming.getWorkingBranches(branches)
            self.assertEqual(len(wbList), 1)
            wb = wbList[0]
            with phlsys_conduit.actAsUserContext(conduit, self.reviewer):
                phlcon_differential.createComment(
                    conduit, wb.id, action="accept")

            processUpdatedRepo(conduit, "phab", "origin")

    def tearDown(self):
        #TODO: comment this back in
        #runCommands("rm -rf abd-test")
        pass


if __name__ == "__main__":
    unittest.main()
