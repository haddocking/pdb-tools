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
Unit Tests for `pdb_addter`.
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
        name = 'pdbtools.pdb_add_manual_ter'
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

    def test_range_1(self):
        """$ pdb_add_manual_ter -1:5 data/add_manual_ter_test_regular.pdb"""

        # Simulate input
        sys.argv = ['', '-1:5', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 79)
        self.assertEqual(len(self.stderr), 0)

        records = ('TER')
        ter_locations = [l[0:80] for l in self.stdout if l.startswith(records)]

        expected = ["TER      12      ALA X   1" + " " * 54,
                    "TER      23      ALA X   2" + " " * 54,
                    "TER      34      ALA X   3" + " " * 54,
                    "TER      45      ALA X   4" + " " * 54,
                    "TER      56      ALA X   5" + " " * 54]

        self.assertEqual(ter_locations, expected)

    def test_range_2(self):
        """$ pdb_add_manual_ter -1: data/add_manual_ter_test_regular.pdb"""

        # Simulate input
        sys.argv = ['', '-1:', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 81)
        self.assertEqual(len(self.stderr), 0)

        records = ('TER')
        ter_locations = [l[0:80] for l in self.stdout if l.startswith(records)]

        expected = ["TER      12      ALA X   1" + " " * 54,
                    "TER      23      ALA X   2" + " " * 54,
                    "TER      34      ALA X   3" + " " * 54,
                    "TER      45      ALA X   4" + " " * 54,
                    "TER      56      ALA X   5" + " " * 54,
                    "TER      67      ALA X   6" + " " * 54,
                    "TER      79      ALA X   7" + " " * 54]

        self.assertEqual(ter_locations, expected)

    def test_range_3(self):
        """$ pdb_add_manual_ter -1:7:3 data/add_manual_ter_test_regular.pdb"""

        # Simulate input
        sys.argv = ['', '-1:7:3', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 76)
        self.assertEqual(len(self.stderr), 0)

        records = ('TER')
        ter_locations = [l[0:80] for l in self.stdout if l.startswith(records)]

        expected = ["TER      32      ALA X   3" + " " * 54,
                    "TER      63      ALA X   6" + " " * 54]

        self.assertEqual(ter_locations, expected)

    def test_range_4(self):
        """$ pdb_add_manual_ter -1::5 data/add_manual_ter_test_regular.pdb"""

        # Simulate input
        sys.argv = ['', '-1::5', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 75)
        self.assertEqual(len(self.stderr), 0)

        records = ('TER')
        ter_locations = [l[0:80] for l in self.stdout if l.startswith(records)]

        expected = ["TER      52      ALA X   5" + " " * 54]

        self.assertEqual(ter_locations, expected)

    def test_range_5(self):
        """$ pdb_add_manual_ter -1:: data/add_manual_ter_test_existingTER.pdb"""

        # Simulate input
        sys.argv = ['', '-1:', os.path.join(data_dir, 'add_manual_ter_existingTER.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 81)
        self.assertEqual(len(self.stderr), 0)

        records = ('TER')
        ter_locations = [l[0:80] for l in self.stdout if l.startswith(records)]

        expected = ["TER      12      ALA X   1" + " " * 54,
                    "TER      23      ALA X   2" + " " * 54,
                    "TER      34      ALA X   3" + " " * 54,
                    "TER      45      ALA X   4" + " " * 54,
                    "TER      56      ALA X   5" + " " * 54,
                    "TER      67      ALA X   6" + " " * 54,
                    "TER      79      ALA X   7" + " " * 54]

        self.assertEqual(ter_locations, expected)

    def test_range_6(self):
        """$ pdb_add_manual_ter -1::2 data/add_manual_ter_existingTER.pdb"""

        # Simulate input
        sys.argv = ['', '-1::2', os.path.join(data_dir, 'add_manual_ter_existingTER.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 78)
        self.assertEqual(len(self.stderr), 0)

        records = ('TER')
        ter_locations = [l[0:80] for l in self.stdout if l.startswith(records)]

        expected = ["TER      12      ALA X   1" + " " * 54,
                    "TER      23      ALA X   2" + " " * 54,
                    "TER      44      ALA X   4" + " " * 54,
                    "TER      65      ALA X   6" + " " * 54]

        self.assertEqual(ter_locations, expected)

    def test_range_7(self):
        """$ pdb_add_manual_ter -1: data/dummy.pdb"""

        # Simulate input
        sys.argv = ['', '-1:', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 220)
        self.assertEqual(len(self.stderr), 0)

        records = ('TER')
        ter_locations = [l[0:80] for l in self.stdout if l.startswith(records)]

        #issue where TER automatically increments line number needs to be resolved
        expected = ["TER      27      ARG B   4" + " " * 54,
                    "TER      43      GLU B   6" + " " * 54,
                    "TER      54      ALA B   7" + " " * 54,
                    "TER      72      ASN A   1" + " " * 54,
                    "TER      97      ARG A   2" + " " * 54,
                    "TER     113      GLU A   3" + " " * 54,
                    "TER     140      ARG C   5" + " " * 54,
                    "TER     156      GLU C   2" + " " * 54,
                    "TER     165      MET C  -1" + " " * 54,
                    "TER     186       DT D   2" + " " * 54,
                    "TER     188       CA A 301" + " " * 54,
                    "TER     190      HOH A 302" + " " * 54,
                    "TER     192      HOH A 303" + " " * 54,
                    "TER     194      HOH B 301" + " " * 54,
                    "TER     196      HOH C 301" + " " * 54,
                    "TER     198      HOH C 302" + " " * 54,
                    "TER     200      HOH C 303" + " " * 54,
                    "TER     202      HOH C 304" + " " * 54,
                    "TER     204      HOH C 305" + " " * 54]

        self.assertEqual(ter_locations, expected)

    def test_range_8(self):
        """$ pdb_add_manual_ter -1:17:3 data/dummy.pdb"""

        # Simulate input
        sys.argv = ['', '-1:17:3', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 206)
        self.assertEqual(len(self.stderr), 0)

        #add TER location asserts for dummy pdb

    def test_invalid_range_1(self):
        """$ pdb_add_manual_ter --9998:: data/add_manual_ter_test_regular.pdb"""

        # Simulate input
        sys.argv = ['', '--9998::', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! Starting value")

    def test_invalid_range_2(self):
        """$ pdb_add_manual_ter -:10000: data/add_manual_ter_test_regular.pdb"""

        # Simulate input
        sys.argv = ['', '-:10000:', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! Please specify")

    def test_invalid_range_3(self):
        """$ pdb_add_manual_ter -::: data/add_manual_ter_test_regular.pdb"""

        # Simulate input
        sys.argv = ['', '-:::', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:21],
                         "ERROR!! Residue range")

    def test_invalid_range_4(self):
        """$ pdb_add_manual_ter -5:1:: data/add_manual_ter_test_regular.pdb"""

        # Simulate input
        sys.argv = ['', '-5:1::', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:21],
                         "ERROR!! Residue range")

    def test_file_not_found(self):
        """$ pdb_add_manual_ter not_existing.pdb"""

        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    def test_file_missing(self):
        """$ pdb_add_manual_ter -1:10"""

        sys.argv = ['', '-1:10']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! No data to process!")

    def test_helptext(self):
        """$ pdb_add_manual_ter"""

        sys.argv = ['']

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_add_manual_ter -A:B data/add_manual_ter_test_regular.pdb"""

        sys.argv = ['', '-A:B', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:],
                         "ERROR!! Range values must be integers!")

    def test_not_an_option(self):
        """$ pdb_add_manual_ter 20 data/add_manual_ter_test_regular.pdb"""

        sys.argv = ['', '20', os.path.join(data_dir, 'add_manual_ter_test_regular.pdb')]

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
