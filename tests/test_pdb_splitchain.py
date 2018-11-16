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
Unit Tests for `pdb_splitchain`.
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
        name = 'bin.pdb_splitchain'
        self.module = __import__(name, fromlist=[''])
    
    def test_valid_1(self):
        """
        pdb_splitchain - new files created and equal
        """
        
        input_file = os.path.join(data_dir, 'full_example.pdb')
        
        sys.argv = ['', input_file]  # simulate
        
        with OutputCapture() as output:
            try:
                self.module.main()
            except SystemExit as e:
                self.retcode = e.code

        self.stdout = output.stdout
        self.stderr = output.stderr
        
        self.assertEqual(self.retcode, 0)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stderr), 0)  # no errors
        
        
        for chain in ['A','B','C','D','E','F', 'G']:
            new_chain = "full_example_{}.pdb".format(chain)
            test_chain = os.path.join(output_dir, new_chain)
            
            ncfh = open(new_chain, 'r')
            nclines = ncfh.read()
            
            tcfh = open(test_chain, 'r')
            tclines = tcfh.read()
            
            self.assertEqual(nclines, tclines)
            
            ncfh.close()
            tcfh.close()
            
            os.remove(new_chain)
        
    
    def test_FileNotFound(self):
        """
        pdb_splitchain - file not found
        """

        # Error (file not found)
        sys.argv = ['', os.path.join(data_dir, 'not_there.pdb')]
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
