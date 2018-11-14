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

from config import data_dir, output_dir
from utils import OutputCapture


class TestTool(unittest.TestCase):
    """Generic class for testing tools.
    """

    def setUp(self):
        # Dynamically import the module
        name = 'bin.pdb_chain'
        self.module = __import__(name, fromlist=[''])
    
    def read_prepare(self, input_file, output_file):
        """
        Prepares input and output common to the different tests.
        """
        
        with OutputCapture() as output:
            try:
                self.module.main()
            except SystemExit as e:
                retcode = e.code

        stdout = output.stdout
        stderr = output.stderr
        
        with open(input_file) as ifile:
            len_original = len(ifile.readlines())
        
        with open(output_file) as ofile:
            output_data = [l.strip("\n") for l in ofile]
        
        return retcode, stdout, stderr, len_original, output_data
    
    def test_valid_1(self):
        """pdb_chain - test single chain"""
        
        input_file = os.path.join(data_dir, 'nano.pdb')
        output_file = os.path.join(output_dir, 'output_pdb_chain_1.pdb')
        
        sys.argv = ['', '-Z', input_file]  # simulate
        # Execute the script
        
        retcode, stdout, stderr, len_original, output_data = \
            self.read_prepare(input_file, output_file)
        
        self.assertEqual(retcode, 0)  # ensure the program exited gracefully.
        self.assertEqual(len(stdout), len_original)  # no lines deleted
        self.assertEqual(len(stderr), 0)  # no errors
        self.assertEqual(stdout, output_data)
    
    def test_valid_2(self):
        
        input_file = os.path.join(data_dir, 'input_pdb_chain_2.pdb')
        output_file = os.path.join(output_dir, 'output_pdb_chain_2.pdb')
        
        sys.argv = ['', '-Z', input_file]  # simulate
        # Execute the script
        
        retcode, stdout, stderr, len_original, output_data = \
            self.read_prepare(input_file, output_file)
        
        self.assertEqual(retcode, 0)  # ensure the program exited gracefully.
        self.assertEqual(len(stdout), len_original)  # no lines deleted
        self.assertEqual(len(stderr), 0)  # no errors
        self.assertEqual(stdout, output_data)
    
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
