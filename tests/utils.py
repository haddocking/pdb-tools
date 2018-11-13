#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 João Pedro Rodrigues
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utility classes/functions for the Tests.
"""

try:
    from cStringIO import StringIO
except ImportError:  # Py 3.x?
    from io import StringIO

import sys


class OutputCapture(object):
    """Context manager to capture output usually redirected to stdout.

    Use as:
    >>> with OutputCapture() as output:
    >>> ....run_stuff()
    >>> print(output)  # list with lines
    """

    def __enter__(self):
        self.stdout = []
        self.stderr = []

        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = self._stringout = StringIO()
        sys.stderr = self._stringerr = StringIO()
        return self

    def __exit__(self, *args):

        self.stdout.extend(self._stringout.getvalue().splitlines())
        self.stderr.extend(self._stringerr.getvalue().splitlines())
        del self._stringout    # free up some memory
        del self._stringerr    # free up some memory
        sys.stdout = self._stdout
        sys.stderr = self._stderr
