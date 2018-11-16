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
Unit Tests for `pdb_b`.
"""

import os
import sys
import unittest

from config import data_dir
from utils import OutputCapture


class TestTool(unittest.TestCase):
    """
    Generic class for testing tools.
    """

    def setUp(self):
        # Dynamically import the module
        name = 'bin.pdb_b'
        self.module = __import__(name, fromlist=[''])

    def test_valid(self):
        """
        pdb_b - valid input
        """

        sys.argv = ['', '-20.0', os.path.join(data_dir, 'pico.pdb')]  # simulate
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
                         "ATOM      1  N   ASN A   1      22.066  40.557   0.420  1.00 20.00              ")

    def test_FileNotFound(self):
        """
        pdb_b - file not found
        """

        # Error (file not found)
        sys.argv = ['', '-10.0', os.path.join(data_dir, 'not_there.pdb')]
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
        self.assertEqual(stderr[0][:35], "ERROR!! File not found or not reada")

    def test_InvalidOptionValue(self):
        """
        pdb_b - invalid value
        """

        # Error (file not found)
        sys.argv = ['', '-A', os.path.join(data_dir, 'pico.pdb')]
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
        self.assertEqual(stderr[0][:35], "ERROR!! You provided an invalid b-f")
