"""Rotating file handler for compressing rolled over logs."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_compressedlogging
#
# Public Classes:
#   CompressedRotatingFileHandler
#    .rotate_existing_files
#    .rotator
#    .doRollover
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gzip
import logging
import logging.handlers
import os
import shutil

# pychecker makes us do this, it won't recognise that logging.handlers is a
# thing
_LG = logging


class CompressedRotatingFileHandler(_LG.handlers.RotatingFileHandler):

    def rotate_existing_files(self):
        for i in range(self.backupCount - 1, 0, -1):
            source = '{filename}.{extension}.gz'.format(
                filename=self.baseFilename, extension=i)
            dest = '{filename}.{extension}.gz'.format(
                filename=self.baseFilename, extension=i + 1)
            if os.path.exists(source):
                if os.path.exists(dest):
                    os.remove(dest)
                os.rename(source, dest)

        dest = self.baseFilename + ".1.gz"
        if os.path.exists(dest):
            os.remove(dest)

    def rotator(self, source, dest):
        with open(source, 'rb') as f_in, gzip.open(dest, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(source)

    def doRollover(self):
        if self.stream:
            self.stream.close()

        self.rotate_existing_files()
        self.rotator(self.baseFilename, self.baseFilename + ".1.gz")

        self.mode = 'w'
        self.stream = self._open()


# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
