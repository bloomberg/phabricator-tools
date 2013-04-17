"""Process the arguments for a single repository and execute."""

import abdi_processrepo
import abdmail_printsender
import abdmail_mailer
import phlsys_conduit
import phlsys_fs
import phlsys_subprocess


def run_once(args, out):
    print_sender = abdmail_printsender.MailSender(args.arcyd_email)
    mailer = abdmail_mailer.Mailer(
        print_sender,
        [args.admin_email],
        args.repo_desc,
        args.instance_uri)  # TODO: this should be a URI for users not conduit

    with phlsys_fs.chDirContext(args.repo_path):
        out.display("fetch (" + args.repo_desc + "): ")
        phlsys_subprocess.runCommands("git fetch -p")

    # XXX: until conduit refreshes the connection, we'll suffer from
    #      timeouts; reduce the probability of this by using a new
    #      conduit each time.
    conduit = phlsys_conduit.Conduit(
        args.instance_uri,
        args.arcyd_user,
        args.arcyd_cert,
        https_proxy=args.https_proxy)

    out.display("process (" + args.repo_desc + "): ")
    abdi_processrepo.processUpdatedRepo(
        conduit, args.repo_path, "origin", mailer)

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
