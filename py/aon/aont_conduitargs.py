"""create an argparser for conduit paramters."""


def addArguments(parser):
    connection = parser.add_argument_group(
        'connection arguments',
        'use these optional parameters to override settings present in your\n'
        '"~/.arcrc" or ".arcconfig" files')

    connection.add_argument(
        "--uri",
        type=str,
        metavar="ADDRESS",
        help="address of the phabricator instance to connect to.")

    connection.add_argument(
        "--user",
        type=str,
        metavar="NAME",
        help="name of the user to connect as.")

    connection.add_argument(
        "--cert",
        type=str,
        metavar="HEX",
        help="long certificate string of the user to connect as, you can find "
             "this string here: "
             "http://your.phabricator/settings/panel/conduit/. generally you "
             "wouldn't expect to enter this on the command-line and would "
             "make an ~/.arcrc file by using '$ arc install-certificate'.")


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
