"""Ensure that two or more interfaces match, useful for validating mocks."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_compiface
#
# Public Functions:
#   check_functions_match
#   check_public_ifaces_match
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function

import difflib
import inspect


def check_functions_match(f1, f2):
    """Return True if two functions match, otherwise return False.

    Print useful diagnostics if the functions do not match.

    The functions are considered to match on the following attributes:
    - inspect.argspec
    - inspect.getdoc

    Usage Examples:

        >>> def func1(my_param='default'):
        ...     "docstring for func1."

        >>> def func2(*args, **kwargs): pass

        >>> check_functions_match(func1, func2)
        argspecs differ:
        func1 args: ['my_param']
        func2 args: []
        func1 varargs: None
        func2 varargs: args
        func1 keywords: None
        func2 keywords: kwargs
        func1 defaults: ('default',)
        func2 defaults: None
        docstrings differ:
        func1 -> func2
        ----- diff -----
        - docstring for func1.
        --- end diff ---
        False

        >>> def func3(foo, bar): pass
        >>> def func4(foo, bar): pass
        >>> check_functions_match(func3, func4)
        True

    :f1: the first function to check
    :f2: the second function to check
    :returns: True if f1 and f2 match, otherwise False.

    """
    assert inspect.isfunction(f1)
    assert inspect.isfunction(f2)

    f1_name = f1.__name__
    f2_name = f2.__name__

    does_match = True

    # check that the argument lists match
    f1_argspec = inspect.getargspec(f1)
    f2_argspec = inspect.getargspec(f2)
    if f1_argspec != f2_argspec:
        print("argspecs differ:")

        if f1_argspec.args != f2_argspec.args:
            print(f1_name, "args:", f1_argspec.args)
            print(f2_name, "args:", f2_argspec.args)

        if f1_argspec.varargs != f2_argspec.varargs:
            print(f1_name, "varargs:", f1_argspec.varargs)
            print(f2_name, "varargs:", f2_argspec.varargs)

        if f1_argspec.keywords != f2_argspec.keywords:
            print(f1_name, "keywords:", f1_argspec.keywords)
            print(f2_name, "keywords:", f2_argspec.keywords)

        if f1_argspec.defaults != f2_argspec.defaults:
            print(f1_name, "defaults:", f1_argspec.defaults)
            print(f2_name, "defaults:", f2_argspec.defaults)

        does_match = False

    f1_docstring = inspect.getdoc(f1)
    f2_docstring = inspect.getdoc(f2)
    if f1_docstring != f2_docstring:
        print("docstrings differ:")
        print(f1_name, "->", f2_name)
        print("----- diff -----")
        f1_doclines = f1_docstring.splitlines() if f1_docstring else ""
        f2_doclines = f2_docstring.splitlines() if f2_docstring else ""
        for line in difflib.Differ().compare(f1_doclines, f2_doclines):
            print(line)
        print("--- end diff ---")
        does_match = False

    return does_match


def check_public_ifaces_match(cls1, cls2):
    """Return True if the public interface of two classes match, else False.

    Print useful diagnostics if the interfaces do not match.

    Only 'public' attributes are compared, i.e. those that don't begin with
    an underscore in their name.

    The functions are considered to match on the following attributes:
    - __name__
    - inspect.argspec
    - inspect.getdoc

    Usage Examples:

        >>> class ExampleClass(object):
        ...     def _imp_detail(self): pass
        ...     def example_method(self):
        ...         pass

        >>> class ExampleClass2(object):
        ...     def example_method2(self, int_param):
        ...         return int_param // 2

        >>> check_public_ifaces_match(ExampleClass, ExampleClass2)
        interfaces differ: ExampleClass and ExampleClass2
        only in ExampleClass
        : ['example_method']
        only in ExampleClass2
        : ['example_method2']
        False

        >>> class ExampleClass3(object):
        ...     def _imp_detail(self): pass
        ...     def example_method(self, blah):
        ...         "a docstring for example_method"

        >>> check_public_ifaces_match(ExampleClass, ExampleClass3)
        argspecs differ:
        example_method args: ['self']
        example_method args: ['self', 'blah']
        docstrings differ:
        example_method -> example_method
        ----- diff -----
        + a docstring for example_method
        --- end diff ---
        interfaces differ: ExampleClass and ExampleClass3
        False

        >>> class ExampleClass4(object):
        ...     def _imp_detail2(self): pass
        ...     def example_method(self):
        ...         pass

        >>> check_public_ifaces_match(ExampleClass, ExampleClass4)
        True

    :cls1: the first class to check
    :cls2: the second class to check
    :returns: True if cls1 and cls2 match, otherwise False.

    """
    assert inspect.isclass(cls1)
    assert inspect.isclass(cls2)

    cls1_name = cls1.__name__
    cls2_name = cls2.__name__

    cls1_interface = cls1.__dict__.keys()
    cls2_interface = cls2.__dict__.keys()

    cls1_public_interface = set([i for i in cls1_interface if i[0] != '_'])
    cls2_public_interface = set([i for i in cls2_interface if i[0] != '_'])

    if cls1_public_interface != cls2_public_interface:
        print("interfaces differ:", cls1_name, "and", cls2_name)
        in_cls1_only = cls1_public_interface - cls2_public_interface
        in_cls2_only = cls2_public_interface - cls1_public_interface
        if in_cls1_only:
            print("only in", cls1_name)
            print(":", list(in_cls1_only))
        if in_cls2_only:
            print("only in", cls2_name)
            print(":", list(in_cls2_only))

        return False

    does_match = True

    for f in cls1_public_interface:

        if inspect.isfunction(cls2.__dict__[f]):
            if not inspect.isfunction(cls1.__dict__[f]):
                print(f, " is not a function on ", cls1_name)
                return False

        if inspect.isfunction(cls1.__dict__[f]):
            if not inspect.isfunction(cls2.__dict__[f]):
                print(f, " is not a function on ", cls2_name)
                return False

        if not check_functions_match(cls1.__dict__[f], cls2.__dict__[f]):
            does_match = False

    if not does_match:
        print("interfaces differ:", cls1_name, "and", cls2_name)
    return does_match


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
