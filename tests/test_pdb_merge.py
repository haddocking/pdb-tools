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
Unit Tests for `pdb_merge`.
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
        name = 'pdbtools.pdb_merge'
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

    def test_default(self):
        """$ pdb_merge data/dummy.pdb data/dummy.pdb"""

        # Simulate input
        sys.argv = ['', os.path.join(data_dir, 'dummy.pdb'),
                    os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 383)  # deleted non-record
        self.assertEqual(len(self.stderr), 0)  # no errors

    def test_merge_three_chains(self):
        """$ pdb_merge data/dummy_merge_A.pdb data/dummy_merge_B.pdb data/dummy_merge_C.pdb"""
        # Simulate input
        sys.argv = [
            '',
            os.path.join(data_dir, 'dummy_merge_A.pdb'),
            os.path.join(data_dir, 'dummy_merge_B.pdb'),
            os.path.join(data_dir, 'dummy_merge_C.pdb'),
            ]

        result_file = os.path.join(data_dir, 'dummy_merged.pdb')

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stderr), 0)  # no errors

        with open(result_file, 'r') as fin:
            expected_lines = [l.strip(os.linesep) for l in fin.readlines()]

        self.assertEqual(self.stdout, expected_lines)

    def test_merge_three_chains_library(self):
        """
        Use pdb_merge as library.


        """
        # Simulate input
        fA = os.path.join(data_dir, 'dummy_merge_A.pdb')
        fB = os.path.join(data_dir, 'dummy_merge_B.pdb')
        fC = os.path.join(data_dir, 'dummy_merge_C.pdb')

        with open(fB, 'r') as fin:
            fB_lines = list(fin.readlines())

        input_data = [fA, fB_lines, fC]

        result_file = os.path.join(data_dir, 'dummy_merged.pdb')

        from pdbtools.pdb_merge import run
        result = list(run(input_data))

        with open(result_file, 'r') as fin:
            expected_lines = list(fin.readlines())

        self.assertEqual(result, expected_lines)


    def test_file_not_found(self):
        """$ pdb_merge not_existing.pdb"""

        # Error (file not found)
        afile = os.path.join(data_dir, 'dummy.pdb')
        bfile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile, bfile]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    def test_error_single_file(self):
        """$ pdb_merge dummy.pdb"""

        # Error (file not found)
        afile = os.path.join(data_dir, 'dummy.pdb')
        sys.argv = ['', afile]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:48],
                        'ERROR!! Please provide more than one input file.'
                        )

    @unittest.skipIf(os.getenv('SKIP_TTY_TESTS'), 'skip on GHA - no TTY')
    def test_helptext(self):
        """$ pdb_merge"""

        sys.argv = ['']

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
