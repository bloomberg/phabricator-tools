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
from __future__ import division
from __future__ import print_function


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
        print('{} {}'.format(prompt, hint), end=' ')
        choice = raw_input().lower()

        if default is not None and choice == '':
            choice = default

        for option_list in options:
            if choice in option_list:
                return option_list

        print("Please choose from:")
        for option_list in options:
            print("  {}".format(' or '.join(option_list)))
        print()


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
