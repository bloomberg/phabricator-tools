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

.bluecard {
    background-color: #5CC;
    padding: 6px;
    float: left;
    margin: 5px;
    border-radius: 6px 6px 6px 6px;
    box-shadow: 0px 0px 30px #111;
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

tr.stats:nth-child(odd) {
    background-color:#eee;
}

tr.stats:nth-child(even) {
    background-color:#fff;
}

th.stats {
    padding: 15px;
    background-color: black;
    color: white;
}

td.stats {
    padding: 10px;
    color: black;
}
"""


def render(formatter, content_string):
    with formatter.tags_context('html'):
        with formatter.tags_context('head'):
            with formatter.tags_context('style'):
                formatter.raw(_CSS_STRING)
        with formatter.tags_context('body'):
            formatter.raw(content_string)


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
