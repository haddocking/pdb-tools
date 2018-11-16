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
Unit Tests for `pdb_chkensemble`.
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
        name = 'bin.pdb_chkensemble'
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
    
    def test_valid_1(self):
        """
        pdb_chkensemble - 2 equal models
        """
        
        input_file = os.path.join(data_dir, 'nano_2_models.pdb')
        
        sys.argv = ['', input_file]  # simulate
        # Execute the script
        
        self.exec_module()
        
        self.assertEqual(self.retcode, 0)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.assertEqual(self.stdout[0][-17:], 'models *seems* OK')
    
    def test_valid_2(self):
        """
        pdb_chkensemble - 2 different models
        """
        
        input_file = os.path.join(data_dir, 'nano_2_models_diff.pdb')
        
        sys.argv = ['', input_file]  # simulate
        # Execute the script
        
        self.exec_module()
        
        self.assertEqual(self.retcode, 0)  # ensure the program exited gracefully.
        self.assertEqual(self.stderr,
                         ["Models 1 and 2 differ:",
                          "Atoms in model 2 only:",
                          "   17  O   ASN A   1 "
                         ])  # no errors
    
    def test_FileNotFound(self):
        """
        pdb_chkensemble - file not found
        """
        
        # Error (file not found)
        not_there = os.path.join(data_dir, 'not_there.pdb')
        sys.argv = ['', not_there]
        
        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! File not found or not readable: '{}'".format(not_there))
    
    def test_FileNotProvided(self):
        """
        pdb_chkensemble - file not provided
        """
        
        sys.argv = ['']
        
        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])
