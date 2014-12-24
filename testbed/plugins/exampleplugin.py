"""A very simple example plugin."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# exampleplugin
#
# Public Functions:
#   on_review_created
#   get_hooks
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================


def on_review_created(params):
    print("a review was created")


def get_hooks():
    return [("after_create_review", on_review_created)]


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
