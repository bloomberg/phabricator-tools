"""Render the outline of an Arcyd report page, with inline CSS, JS etc."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdweb_page
#
# Public Functions:
#   render
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

_CSS_STRING = """
body {
    background-color: #555;
    font-family: Arial, Helvetica, sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family:"Arial Black", Gadget, sans-serif;
    color: #fff;
}

pre {
    font-family:"Lucida Console", Monaco, monospace;
}

a {
    font-family:"Arial Black", Gadget, sans-serif;
    color: #000;
}

a:hover {
    background-color: #000;
    color: #fff;
}

.greeninset {
    background-color: #5C5;
    padding: 6px;
    box-shadow: 0px 0px 30px #111;
}

div.container {
    overflow: hidden;
    width: 100%;
}

.redinset {
    background-color: #E55;
    padding: 6px;
    box-shadow: 0px 0px 30px #111;
}

.activeinset {
    background-color: #EE3;
    padding: 6px;
    box-shadow: 0px 0px 30px #111;
      -webkit-animation: pulsate 1s ease-out;
    -webkit-animation-iteration-count: infinite;
}

.greencard {
    background-color: #5C5;
    padding: 6px;
    float: left;
    margin: 5px;
    border-radius: 6px 6px 6px 6px;
    box-shadow: 0px 0px 30px #111;
}

.redcard {
    background-color: #E55;
    padding: 6px;
    float: left;
    margin: 5px;
    border-radius: 6px 6px 6px 6px;
    box-shadow: 0px 0px 30px #111;
}

@-webkit-keyframes pulsate {
    0% {-webkit-transform: scale(1.0, 1.0); opacity: 0.75;}
    50% {-webkit-transform: scale(1.01, 1.01); opacity: 1.0;}
    100% {-webkit-transform: scale(1.0, 1.0); opacity: 0.75;}
}

.activecard {
    background-color: #EE3;
    border: 6px solid #EE3;
    box-shadow: 0px 0px 30px #111;
      -webkit-animation: pulsate 1s ease-out;
    -webkit-animation-iteration-count: infinite;
}
"""


def render(formatter, content_string):
    with formatter.tags_context('html'):
        with formatter.tags_context('head'):
            with formatter.tags_context('style'):
                formatter.raw(_CSS_STRING)
        with formatter.tags_context('body'):
            formatter.raw(content_string)


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
