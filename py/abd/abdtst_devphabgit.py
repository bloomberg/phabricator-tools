"""Support for testing developer / phab interactions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdtst_devphabgit
#
# Public Classes:
#   Collaboration
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import os

import abdt_commitmessage
import abdt_git
import abdt_naming
import phlsys_fs
import phlsys_subprocess


class Collaboration(object):

    def __init__(self, author, phab):
        # TODO: just make a temp dir
        self._run_commands("rm -rf abd-test")
        self._run_commands("mkdir abd-test")
        self.saved_path = os.getcwd()
        os.chdir("abd-test")
        self._run_commands(
            "git --git-dir=devgit init --bare",
            "git clone devgit developer",
            "git clone devgit phab",
        )

        self._phab_wdir = os.path.abspath("phab")
        self.clone = abdt_git.Clone("phab", "origin")

        self._dev_wdir = os.path.abspath("developer")
        self.dev_clone = abdt_git.Clone("developer", "origin")

        self.clone.set_name_email(phab.user, phab.email)
        self.dev_clone.set_name_email(author.user, author.email)

    def _run_commands(self, *commands):
        phlsys_subprocess.run_commands(*commands)

    def close(self):
        os.chdir(self.saved_path)
        self._run_commands("rm -rf abd-test")

    def dev_commit_all(self, subject, test_plan, reviewer):
        with phlsys_fs.chdir_context(self._dev_wdir):
            reviewers = [reviewer] if reviewer else None
            message = abdt_commitmessage.make(
                subject, None, test_plan, reviewers)
            phlsys_subprocess.run(
                "git", "commit", "-a", "-F", "-", stdin=message)

    def dev_commit_new_file(
            self, filename, test_plan=None, reviewer=None, contents=""):
        with phlsys_fs.chdir_context(self._dev_wdir):
            with open(filename, "w") as f:
                f.write(contents)
            self._run_commands("git add " + filename)
        self.dev_commit_all("add " + filename, test_plan, reviewer)

    def dev_push_branch(self, branch):
        with phlsys_fs.chdir_context(self._dev_wdir):
            self._run_commands("git push origin " + branch)

    def dev_push(self):
        with phlsys_fs.chdir_context(self._dev_wdir):
            self._run_commands("git push origin")

    def dev_push_delete_branch(self, branch):
        with phlsys_fs.chdir_context(self._dev_wdir):
            self._run_commands("git push origin :" + branch)

    def dev_checkout(self, branch):
        with phlsys_fs.chdir_context(self._dev_wdir):
            self._run_commands("git checkout " + branch)

    def dev_reset_branch_to_master(self, branch):
        with phlsys_fs.chdir_context(self._dev_wdir):
            self._run_commands("git checkout " + branch)
            self._run_commands("git reset origin/master --hard")
            self._run_commands("git push -u origin " + branch + " --force")

    def dev_checkout_push_new_branch(self, branch, base=None):
        with phlsys_fs.chdir_context(self._dev_wdir):
            checkout_cmd = "git checkout -b " + branch
            if base:
                checkout_cmd += " " + base
            self._run_commands(checkout_cmd, "git push -u origin " + branch)

    def dev_fetch(self):
        with phlsys_fs.chdir_context(self._dev_wdir):
            self._run_commands("git fetch origin -p")

    def dev_merge_keep_ours(self, branch):
        with phlsys_fs.chdir_context(self._dev_wdir):
            self._run_commands("git merge -s ours " + branch)

    def phab_fetch(self):
        with phlsys_fs.chdir_context(self._phab_wdir):
            self._run_commands("git fetch origin -p")

    def count_phab_working_branches(self):
        branches = self.clone.get_remote_branches()
        wbList = abdt_naming.getWorkingBranches(branches)
        return len(wbList)

    def count_phab_bad_working_branches(self):
        branches = self.clone.get_remote_branches()
        wbList = abdt_naming.getWorkingBranches(branches)
        numBadBranches = 0
        for wb in wbList:
            if abdt_naming.isStatusBad(wb):
                numBadBranches += 1
        return numBadBranches


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
