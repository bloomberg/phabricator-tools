"""Prompt the user to choose from some options on the command-line."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_choice
#
# Public Functions:
#   yes_or_no
#   yes_or_no_or_abort
#   prompt_with_options
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


def yes_or_no(prompt, default="yes"):
    """Return True if the user chooses 'yes', False if they choose 'no'.

    :prompt: the string prompt to display when asking the question
    :default: the string default to assume if the user just presses 'enter'
    :returns: True or False from the choice of 'yes' or 'no'

    """
    yes_choices = ['yes', 'y']
    no_choices = ['no', 'n']

    choice = prompt_with_options(
        prompt, [yes_choices, no_choices], default)

    if choice == yes_choices:
        result = True
    else:
        assert choice == no_choices
        result = False

    return result


def yes_or_no_or_abort(prompt, default="yes"):
    """Return True if the user chooses 'yes', False if they choose 'no'.

    If the user chooses 'abort' then None is returned, loop until they choose
    one of the options.

    :prompt: the string prompt to display when asking the question
    :default: the string default to assume if the user just presses 'enter'
    :returns: True, False or None from the choice of 'yes', 'no' or 'abort'

    """
    yes_choices = ['yes', 'y']
    no_choices = ['no', 'n']
    abort_choices = ['abort', 'a']

    choice = prompt_with_options(
        prompt, [yes_choices, no_choices, abort_choices], default)

    if choice == yes_choices:
        result = True
    elif choice == no_choices:
        result = False
    else:
        assert choice == abort_choices
        result = None

    return result


def prompt_with_options(prompt, options, default):
    """Return the user's choice from the list of option lists.

    The first option from each list is chosen as the hint for that option,

    for example:
        prompt_with_options('do it', [['yes', 'y'], ['no', 'n']], None)

    will prompt with:
        'do it [yes/no]? '

    Note that the choice is converted to lowercase before comparison so all
    choices should be in lowercase.

    Loop until one of the supplied options is chosen.

    :prompt: the string to present to the user
    :options: the list of option string lists
    :default: the string default option or None if there is no default

    """

    lead_options = [o[0] for o in options]
    if default is not None:
        assert default in lead_options
        lead_options = map(
            lambda x: x.upper() if x == default else x, lead_options)

    hint = '[{}]'.format('/'.join(lead_options))

    while True:
        print '{} {}'.format(prompt, hint),
        choice = raw_input().lower()

        if default is not None and choice == '':
            choice = default

        for option_list in options:
            if choice in option_list:
                return option_list

        print "Please choose from:"
        for option_list in options:
            print "  {}".format(' or '.join(option_list))
        print


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
