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
Unit Tests for `pdb_delaltloc`.
"""

import os
import sys
import unittest

from config import data_dir, output_dir
from utils import OutputCapture


class TestTool(unittest.TestCase):
    """
    Generic class for testing tools.
    """

    def setUp(self):
        # Dynamically import the module
        name = 'bin.pdb_delaltloc'
        self.module = __import__(name, fromlist=[''])
    
    def exec_module(self):
        """
        Execs module.
        """
        
        with OutputCapture() as output:
            try:
                self.module.main()
            except SystemExit as e:
                self.retcode = e.code

        self.stdout = output.stdout
        self.stderr = output.stderr
        
        return
    
    def read_prepare(self, input_file, output_file):
        """
        Prepares input and output common to the different tests.
        """
        
        with open(input_file) as ifile:
            self.len_original = len(ifile.readlines())
        
        with open(output_file) as ofile:
            self.output_data = [l.strip("\n") for l in ofile]
        
        return
    
    def test_valid_1(self):
        """
        pdb_delaltloc - test without option
        """
        
        input_file = os.path.join(data_dir, 'pdb_delaltloc.pdb')
        output_file = os.path.join(output_dir, 'output_pdb_delaltloc_1.pdb')
        
        sys.argv = ['', input_file]  # simulate
        # Execute the script
        
        self.read_prepare(input_file, output_file)
        self.exec_module()
        
        self.assertEqual(self.retcode, 0)  # ensure the program exited gracefully.
        self.assertNotEqual(len(self.stdout), self.len_original)  # lines are deleted
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.assertEqual(self.stdout, self.output_data)
    
    def test_valid_2(self):
        """
        pdb_delaltloc - test remove A
        """
        
        input_file = os.path.join(data_dir, 'pdb_delaltloc.pdb')
        output_file = os.path.join(output_dir, 'output_pdb_delaltloc_1.pdb')
        
        sys.argv = ['', '-A', input_file]  # simulate
        # Execute the script
        
        self.read_prepare(input_file, output_file)
        self.exec_module()
        
        self.assertEqual(self.retcode, 0)  # ensure the program exited gracefully.
        self.assertNotEqual(len(self.stdout), self.len_original)  # lines are deleted
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.assertEqual(self.stdout, self.output_data)
    
    def test_valid_3(self):
        """
        pdb_delaltloc - test remove B
        """
        
        input_file = os.path.join(data_dir, 'pdb_delaltloc.pdb')
        output_file = os.path.join(output_dir, 'output_pdb_delaltloc_2.pdb')
        
        sys.argv = ['', '-B', input_file]  # simulate
        # Execute the script
        
        self.read_prepare(input_file, output_file)
        self.exec_module()
        
        self.assertEqual(self.retcode, 0)  # ensure the program exited gracefully.
        self.assertNotEqual(len(self.stdout), self.len_original)  # lines are deleted
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.assertEqual(self.stdout, self.output_data)
    
    def test_FileNotFound(self):
        """
        pdb_delaltloc - file not found
        """
        
        # Error (file not found)
        not_there = os.path.join(data_dir, 'not_there.pdb')
        sys.argv = ['', '-A', not_there]
        
        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! File not found or not readable: '{}'".format(not_there))
    
    def test_FileNotProvided(self):
        """
        pdb_delaltloc - file not provided
        """
        
        sys.argv = ['', '-A']
        
        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! No data to process!")
    
    def test_NothingProvided(self):
        """
        pdb_delaltloc - nothing provided
        """
        
        sys.argv = ['']
        
        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])
    
    def test_InvalidOptionValue(self):
        """
        pdb_delaltloc - invalid argument
        """
        
        # Error (file not found)
        sys.argv = ['', '-AA', os.path.join(data_dir, 'pico.pdb')]
        
        # Execute the script
        self.exec_module()
        
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0][:70], "ERROR!! Alternate location identifiers must be single characters: 'AA'")
    
    def test_NotOptionValue(self):
        """
        pdb_delaltloc - not an option
        """
        
        # Error (file not found)
        sys.argv = ['', 'A', os.path.join(data_dir, 'pico.pdb')]
        
        # Execute the script
        self.exec_module()
        
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0], "ERROR! First argument is not an option: 'A'")
