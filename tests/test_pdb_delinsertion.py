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
Unit Tests for `pdb_fixinsert`.
"""

import os
import sys
import unittest
import warnings

from config import data_dir
from utils import OutputCapture


class TestTool(unittest.TestCase):
    """
    Generic class for testing tools.
    """

    def setUp(self):
        # Dynamically import the module
        name = 'pdbtools.pdb_delinsertion'
        self.module = __import__(name, fromlist=[''])

    def exec_module(self):
        """
        Execs module.
        """

        with OutputCapture() as output:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.module.main()
            except SystemExit as e:
                self.retcode = e.code

        self.stdout = output.stdout
        self.stderr = output.stderr

        return

    def test_default(self):
        """$ pdb_fixinsert data/dummy_insertions.pdb"""

        # Simulate input
        # pdb_fixinsert dummy_insertions.pdb
        sys.argv = ['', os.path.join(data_dir, 'dummy_insertions.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 255)  # no lines deleted
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Check if we do not have any insertions
        records = (('ATOM', 'HETATM', 'TER'))
        icodes = set(l[26] for l in self.stdout if l.startswith(records))
        self.assertEqual(icodes, set(' '))

        # Check numbering was corrected
        resid = [int(l[22:26]) for l in self.stdout if l.startswith(records)]
        expected = [
            4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
            4, 4, 4, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8,
            8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 7, 7, 7,
            7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9,
            9, 9, 9, 9, 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2,
            2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, -1, -1, -1, -1, -1, -1,
            -1, -1, -1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            2, 301, 302, 303, 301, 301, 302, 303, 304, 305
        ]
        self.assertEqual(resid, expected)

    def test_select_insertion(self):
        """$ pdb_fixinsert -A1 data/dummy_insertions.pdb"""

        sys.argv = ['', '-A1', os.path.join(data_dir, 'dummy_insertions.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 255)
        self.assertEqual(len(self.stderr), 0)

        records = (('ATOM', 'HETATM', 'TER'))

        # Check the insertions were deleted specifically
        for line in self.stdout:
            if line.startswith(records):
                icode = line[26]
                resid = int(line[22:26])
                if line[17:26] == 'ARG B   4':
                    self.assertIn(icode, ('A', 'B'))
                    self.assertEqual(resid, 4)
                elif line[17:26] == 'GLY B   4':
                    self.assertEqual(icode, ' ')
                    self.assertEqual(resid, 4)
                elif line[17:26] == 'ASN A   1':
                    self.assertEqual(icode, ' ')
                    self.assertEqual(resid, 1)
                elif line[17:26] == 'GLY A   1':
                    self.assertEqual(icode, ' ')
                    self.assertEqual(resid, 2)  # should have renumbered

        # Check numbering was corrected overall
        resid = [int(l[22:26]) for l in self.stdout if l.startswith(records)]
        expected = [
            4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
            4, 4, 4, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8,
            8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 7, 7, 7,
            7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9,
            9, 9, 9, 9, 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2,
            2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, -1, -1, -1, -1, -1, -1,
            -1, -1, -1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            2, 301, 302, 303, 301, 301, 302, 303, 304, 305
        ]

        self.assertEqual(resid, expected)

    def test_file_not_found(self):
        """$ pdb_fixinsert not_existing.pdb"""

        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    @unittest.skipIf(sys.platform.startswith('win'), 'skip on Windows - requires TTY')
    def test_file_missing(self):
        """$ pdb_fixinsert -A89"""

        sys.argv = ['', '-A89']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! No data to process!")

    # @unittest.skipIf(sys.platform.startswith('win'), 'skip on Windows - requires TTY')
    # def test_helptext(self):
    #     """$ pdb_fixinsert"""

    #     sys.argv = ['']

    #     self.exec_module()

    #     self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
    #     self.assertEqual(len(self.stdout), 0)  # no output
    #     self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_fixinsert -A data/dummy_insertions.pdb"""

        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy_insertions.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:27],
                         "ERROR!! Option invalid: 'A'")

    def test_invalid_option_2(self):
        """$ pdb_fixinsert -12A data/dummy_insertions.pdb"""

        sys.argv = ['', '-12A', os.path.join(data_dir, 'dummy_insertions.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:39],
                         "ERROR!! Option invalid: '12A'")

    def test_not_an_option(self):
        """$ pdb_fixinsert 20 data/dummy_insertions.pdb"""

        sys.argv = ['', '20', os.path.join(data_dir, 'dummy_insertions.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0],
                         "ERROR! First argument is not an option: '20'")


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
