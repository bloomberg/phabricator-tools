"""Decorators for tracing out the execution of functions and methods."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_tracedecorator
#
# Public Functions:
#   method_tracer
#   decorate_object_methods
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import inspect
import pprint
import types


def method_tracer(object_to_string):
    """Return a decorator which will trace the execution of object methods.

    Uses the supplied 'object_to_string' to generate a string summary of the
    'self' parameter of the called method.

    e.g.

        >>> class ExampleClass(object):
        ...     @method_tracer(lambda x: 'Example')
        ...     def example_method(self):
        ...         pass
        >>> c = ExampleClass()
        >>> c.example_method()
        Example.example_method() -> None

        >>> class ExampleClass2(object):
        ...     @method_tracer(lambda x: 'Example2')
        ...     def example_method2(self, int_param):
        ...         return int_param // 2
        >>> d = ExampleClass2()
        >>> d.example_method2(42)
        Example2.example_method2(42) -> 21
        21

        >>> class ExampleClass3(object):
        ...     @method_tracer(lambda x: 'Example3')
        ...     def example_method3(self, str_param):
        ...         return str_param[:5]
        >>> e = ExampleClass3()
        >>> e.example_method3("hovercraft")
        Example3.example_method3('hovercraft') -> 'hover'
        'hover'

    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            ret = f(self, *args, **kwargs)
            callstring = object_to_string(self) + '.' + f.__name__ + '('
            callstring += ','.join([pprint.pformat(arg) for arg in args])
            callstring += ')'
            print(callstring, '->', pprint.pformat(ret))
            return ret
        return wrapper
    return decorator


def decorate_object_methods(object_, object_to_string):
    """Decorate all the methods of the supplied object.

    Uses the supplied 'object_to_string' to generate a string summary of the
    'self' parameter of the called method.

    e.g.

        >>> class ExampleClass(object):
        ...     def example_method(self):
        ...         pass
        >>> c = ExampleClass()
        >>> decorate_object_methods(c, lambda x: 'Example')
        >>> c.example_method()
        Example.example_method() -> None

    See also: phlsys_tracedecorator.method_tracer

    """
    tracer = method_tracer(object_to_string)
    for name, attribute in object_.__class__.__dict__.iteritems():
        if inspect.isfunction(attribute):
            new_method = types.MethodType(tracer(attribute), object_)
            object_.__dict__[name] = new_method


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
