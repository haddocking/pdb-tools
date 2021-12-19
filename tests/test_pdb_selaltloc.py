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
Unit Tests for `pdb_selaltloc`.
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
        name = 'pdbtools.pdb_selaltloc'
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

    def test_is_another_group_1(self):
        """Test if is_another_altloc_group altloc is ' '."""
        result = self.module.is_another_altloc_group(
            ' ', None, None, None, None, None, {})

        self.assertTrue(result)

    def test_is_another_group_2(self):
        """Test if is_another_altloc_group second with residue number."""
        result = self.module.is_another_altloc_group(
            'A', 'A', '12', '11', 'ALA', 'ALA', {})
        self.assertTrue(result)

    def test_is_another_group_3(self):
        """Test if is_another_altloc_group second with residue name."""
        result = self.module.is_another_altloc_group(
            'A', 'A', '12', '12', 'PRO', 'ALA', {})
        self.assertTrue(result)

    def test_is_another_group_4(self):
        """Test if is_another_altloc_group third with residueloc."""
        result = self.module.is_another_altloc_group(
            'B', 'A', None, None, None, None, {'B': None, 'A': None})
        self.assertTrue(result)

    def test_is_another_group_5(self):
        """Test if is_another_altloc_group."""
        result = self.module.is_another_altloc_group(
            'B', 'B', '12', '12', 'ALA', 'ALA', {'B': None}
            )
        self.assertFalse(result)

    def test_is_another_group_6(self):
        """Test if is_another_altloc_group."""
        result = self.module.is_another_altloc_group(
            'B', 'A', '12', '13', 'ALA', 'PRO', {'A': None}
            )
        self.assertFalse(result)

    def test_is_another_group_7(self):
        """Test if is_another_altloc_group."""
        result = self.module.is_another_altloc_group(
            'A', ' ', '26', '25', 'LEU', 'GLU', {}
            )
        self.assertFalse(result)

    def test_is_another_group_8(self):
        """Test if is_another_altloc_group."""
        result = self.module.is_another_altloc_group(
            'A', 'A', '26', '25', 'LEU', 'GLU', {'A': None}
            )
        self.assertTrue(result)

    def test_default(self):
        """$ pdb_selaltloc data/dummy_altloc.pdb"""

        # Simulate input
        # pdb_selaltloc dummy.pdb
        sys.argv = ['', os.path.join(data_dir, 'dummy_altloc.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 36)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Make sure sequence is correct
        expected = [
            aa for aa in ['SER', 'GLU', 'ALA', 'LEU'] for _ in range(8)
        ] + ["GLU"] * 2
        observed = [
            ln[17:20] for ln in self.stdout if ln.startswith(("ATOM", "ANISOU"))
        ]

        self.assertEqual(observed, expected)

        # Make sure we picked the right GLU atom
        atom_CA_GLU_26 = [
            l[30:54] for l in self.stdout
            if l[12:16] == " CA " and l[17:20] == "GLU" and l[22:26] == "  26"
        ]
        self.assertEqual(len(atom_CA_GLU_26), 2)
        self.assertEqual(atom_CA_GLU_26[0], " -10.679  -3.437 -12.387")

    def test_default2(self):
        """$ pdb_selaltloc data/dummy_altloc2.pdb"""

        # Simulate input
        # pdb_selaltloc dummy.pdb
        sys.argv = ['', os.path.join(data_dir, 'dummy_altloc2.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 37)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Make sure sequence is correct
        expected = [
            aa for aa in ['SER', 'GLU', 'ALA', 'LEU'] for _ in range(8)
        ] + ["GLU"] * 2
        observed = [
            ln[17:20] for ln in self.stdout if ln.startswith(("ATOM", "ANISOU"))
        ]

        self.assertEqual(observed, expected)

        # Make sure we picked the right GLU atom
        atom_CA_GLU_26 = [
            l[30:54] for l in self.stdout
            if l[12:16] == " CA " and l[17:20] == "GLU" and l[22:26] == "  26"
        ]
        self.assertEqual(len(atom_CA_GLU_26), 2)
        self.assertEqual(atom_CA_GLU_26[0], " -10.679  -3.437 -12.387")

    def test_select_loc_A(self):
        """$ pdb_selaltloc -A data/dummy_altloc.pdb"""

        # Simulate input
        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy_altloc.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 36)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Make sure sequence is correct
        expected = [
            aa for aa in ['SER', 'GLU', 'ALA', 'LEU'] for _ in range(8)
        ] + ["GLU"] * 2
        observed = [
            ln[17:20] for ln in self.stdout if ln.startswith(("ATOM", "ANISOU"))
        ]

        self.assertEqual(observed, expected)

        # Make sure we picked the right GLU atom
        atom_CA_GLU_26 = [
            l[30:54] for l in self.stdout
            if l[12:16] == " CA " and l[17:20] == "GLU" and l[22:26] == "  26"
        ]
        self.assertEqual(len(atom_CA_GLU_26), 2)
        self.assertEqual(atom_CA_GLU_26[0], " -10.000  -3.000 -12.000")

    def test_select_loc_A_2(self):
        """$ pdb_selaltloc -A data/dummy_altloc2.pdb"""

        # Simulate input
        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy_altloc2.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 37)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Make sure sequence is correct
        expected = [
            aa for aa in ['SER', 'GLU', 'ALA', 'LEU'] for _ in range(8)
        ] + ["GLU"] * 2
        observed = [
            ln[17:20] for ln in self.stdout if ln.startswith(("ATOM", "ANISOU"))
        ]

        self.assertEqual(observed, expected)

        # Make sure we picked the right GLU atom
        atom_CA_GLU_26 = [
            l[30:54] for l in self.stdout
            if l[12:16] == " CA " and l[17:20] == "GLU" and l[22:26] == "  26"
        ]
        self.assertEqual(len(atom_CA_GLU_26), 2)
        self.assertEqual(atom_CA_GLU_26[0], " -10.000  -3.000 -12.000")

    def test_select_loc_B(self):
        """$ pdb_selaltloc -B data/dummy_altloc.pdb"""

        # Simulate input
        sys.argv = ['', '-B', os.path.join(data_dir, 'dummy_altloc.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 46)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Make sure sequence is correct
        expected = [
            aa for aa in ['PRO', 'GLU', 'ALA', 'ILE', 'LEU'] for _ in range(8)
        ] + ["GLU"] * 4
        observed = [
            ln[17:20] for ln in self.stdout if ln.startswith(("ATOM", "ANISOU"))
        ]

        self.assertEqual(observed, expected)

    def test_select_loc_B_2(self):
        """$ pdb_selaltloc -B data/dummy_altloc2.pdb"""

        # Simulate input
        sys.argv = ['', '-B', os.path.join(data_dir, 'dummy_altloc2.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 47)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Make sure sequence is correct
        expected = [
            aa for aa in ['PRO', 'GLU', 'ALA', 'ILE', 'LEU'] for _ in range(8)
        ] + ["GLU"] * 4
        observed = [
            ln[17:20] for ln in self.stdout if ln.startswith(("ATOM", "ANISOU"))
        ]

        self.assertEqual(observed, expected)

    def test_select_loc_C(self):
        """$ pdb_selaltloc -C data/dummy_altloc.pdb"""

        # Simulate input
        sys.argv = ['', '-C', os.path.join(data_dir, 'dummy_altloc.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 52)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Make sure sequence is correct
        expected = [
            aa for aa in ['SER', 'PRO', 'GLU', 'ALA', 'ILE', 'LEU'] for _ in range(8)
        ] + ["GLU"] * 2
        observed = [
            ln[17:20] for ln in self.stdout if ln.startswith(("ATOM", "ANISOU"))
        ]

        self.assertEqual(observed, expected)

    def test_select_loc_C_2(self):
        """$ pdb_selaltloc -C data/dummy_altloc2.pdb"""

        # Simulate input
        sys.argv = ['', '-C', os.path.join(data_dir, 'dummy_altloc2.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 61)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Make sure sequence is correct
        expected = [
            aa for aa in ['SER', 'GLU', 'PRO', 'GLU', 'ALA', 'ILE', 'LEU']
            for _ in range(8)
            ] + ["GLU"] * 2
        observed = [
            ln[17:20] for ln in self.stdout if ln.startswith(("ATOM", "ANISOU"))
        ]

        self.assertEqual(observed, expected)

    def test_file_not_found(self):
        """$ pdb_selaltloc not_existing.pdb"""

        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    def test_file_missing(self):
        """$ pdb_selaltloc -A"""

        sys.argv = ['', '-A']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! No data to process!")

    def test_helptext(self):
        """$ pdb_selaltloc"""

        sys.argv = ['']

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_selaltloc -AH data/dummy.pdb"""

        sys.argv = ['', '-AH', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:47],
                         "ERROR!! Alternate location identifiers must be ")

    def test_not_an_option(self):
        """$ pdb_selaltloc 20 data/dummy.pdb"""

        sys.argv = ['', '20', os.path.join(data_dir, 'dummy.pdb')]

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
