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
Unit Tests for `pdb_chain`.
"""

import os
import sys
import unittest

from config import data_dir
from utils import OutputCapture


class TestTool(unittest.TestCase):
    """Generic class for testing tools.
    """

    def setUp(self):
        # Dynamically import the module
        name = 'bin.pdb_chain'
        self.module = __import__(name, fromlist=[''])

    def test_valid(self):
        """pdb_chain - valid input"""

        sys.argv = ['', '-Z', os.path.join(data_dir, 'pico.pdb')]  # simulate
        # Execute the script
        with OutputCapture() as output:
            try:
                self.module.main()
            except SystemExit as e:
                retcode = e.code

        stdout = output.stdout
        stderr = output.stderr

        self.assertEqual(retcode, 0)  # ensure the program exited gracefully.
        self.assertEqual(len(stdout), 3)  # no lines deleted
        self.assertEqual(len(stderr), 0)  # no errors
        self.assertEqual(stdout[1],  # functions properly
                         "ATOM      1  N   ASN Z   1      22.066  40.557   0.420  1.00  0.00              ")

    def test_FileNotFound(self):
        """pdb_chain - file not found"""

        # Error (file not found)
        sys.argv = ['', '-Z', os.path.join(data_dir, 'not_there.pdb')]
        # Execute the script
        with OutputCapture() as output:
            try:
                self.module.main()
            except SystemExit as e:
                retcode = e.code

        stdout = output.stdout
        stderr = output.stderr

        self.assertEqual(retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(stdout), 0)  # no output
        self.assertEqual(stderr[0][:39], "ERROR!! File not found or not readable:")

    def test_FileNotGiven(self):
        """pdb_chain - file not found"""

        # Error (file not found)
        sys.argv = ['', '-Z']
        # Execute the script
        with OutputCapture() as output:
            try:
                self.module.main()
            except SystemExit as e:
                retcode = e.code

        stdout = output.stdout
        stderr = output.stderr

        self.assertEqual(retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(stdout), 0)  # no output
        self.assertEqual(stderr[0][:27], "ERROR!! No data to process!")

    def test_InvalidOptionValue(self):
        """pdb_chain - invalid value"""

        # Error (file not found)
        sys.argv = ['', '-AA', os.path.join(data_dir, 'pico.pdb')]
        # Execute the script
        with OutputCapture() as output:
            try:
                self.module.main()
            except SystemExit as e:
                retcode = e.code

        stdout = output.stdout
        stderr = output.stderr

        self.assertEqual(retcode, 1)
        self.assertEqual(len(stdout), 0)  # no output
        self.assertEqual(stderr[0][:53], "ERROR!! Chain identifiers must be a single character:")
