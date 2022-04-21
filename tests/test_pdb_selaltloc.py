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

    def test_is_same_group_1(self):
        """
        Test if from the same group.

        Exemple of a starting line with empty strings.
        """
        result = self.module.is_another_altloc_group(
            ' ', '', '1', '', 'ALA', '', {}, {})

        self.assertFalse(result)

    def test_is_same_group_2(self):
        """
        Test if from the same group.

        Example of a starting line with Nones.
        """
        result = self.module.is_another_altloc_group(
            ' ', None, None, None, None, None, {}, {})

        self.assertFalse(result)

    def test_is_same_group_3(self):
        """
        Test if from the same group.

        Example of all parameters are the same as previous line.
        """
        result = self.module.is_another_altloc_group(
            'B', 'B', '12', '12', 'ALA', 'ALA', {'B': None},
            {'B': {('ALA', '12')}}
            )
        self.assertFalse(result)


    def test_is_same_group_4(self):
        """
        Test if line is from another group.

        Multiple residue altloc.

        This considers altloc spanning several residues. See example
        dummy_altloc2.pdb.
        """
        result = self.module.is_another_altloc_group(
            'A', 'A', '26', '25', 'LEU', 'GLU', {'A': ['lines']},
            {'A': {('GLU', '25')}}
            )
        self.assertFalse(result)

    def test_is_same_group_5(self):
        """
        Test if line is from another group.

        Multiple residue altloc.

        This considers altloc spanning several residues. See example
        dummy_altloc2.pdb.
        """
        result = self.module.is_another_altloc_group(
            'A', ' ', '26', '25', 'GLU', 'GLU', {' ': ['lines']},
            {' ': {('GLU', '25')}}
            )
        self.assertFalse(result)

    def test_is_same_group_6(self):
        """
        Test if line is from another group.

        Multiple residue altloc.

        This considers altloc spanning several residues. See example
        dummy_altloc2.pdb.
        """
        result = self.module.is_another_altloc_group(
            'A', ' ', '25', '25', 'ALA', 'GLU', {' ': ['lines']},
            {' ': {('GLU', '25')}}
            )
        self.assertFalse(result)

    def test_is_another_group_1(self):
        result = self.module.is_another_altloc_group(
            ' ', 'B', '2', '1', 'ALA', 'PRO', {'B': ['lines']},
            {'B': {('PRO', '1')}}
            )
        self.assertTrue(result)

    def test_is_another_group_2(self):
        result = self.module.is_another_altloc_group(
            ' ', ' ', '2', '1', 'ALA', 'ALA', {' ': ['lines']},
            {' ': {('ALA', '1')}}
            )
        self.assertTrue(result)

    def test_is_another_group_3(self):
        result = self.module.is_another_altloc_group(
            ' ', ' ', '1', '1', 'ALA', 'GLU', {' ': ['lines']},
            {' ': {('GLU', '1')}}
            )
        self.assertTrue(result)

    def test_is_another_group_4(self):
        result = self.module.is_another_altloc_group(
            'A', 'A', '26', '25', 'LEU', 'GLU', {' ': ['lines'], 'A': ['lines']},
            {' ': {('LEU', '25')}, 'A': {('GLU', '26')}}
            )
        self.assertTrue(result)

    def test_all_same_residue(self):
        """Test all same residue."""
        inp = {
            ' ': [
                    "ATOM      3  N   ASN A   1      22.066  40.557   0.420  1.00  0.00           N  ",
                    "ATOM      3  H   ASN A   1      21.629  41.305  -0.098  1.00  0.00           H  ",
                    "ATOM      3  H2  ASN A   1      23.236  40.798   0.369  1.00  0.00           H  ",
                    "ATOM      3  H3  ASN A   1      21.866  40.736   1.590  1.00  0.00           H  ",
                    ],
            'B': ["ATOM      3  CA BASN A   1      20.000  30.000   0.005  0.60  0.00           C  "],
            'A': ["ATOM      3  CA AASN A   1      21.411  39.311   0.054  0.40  0.00           C  "],
            }

        result = self.module.all_same_residue(inp)
        self.assertTrue(result)

    def test_all_same_residue_false(self):
        """Test all same residue."""
        inp = {
            'B': ["ATOM      3  CA BSER A   2      20.000  30.000   0.005  0.60  0.00           C  "], 'A': ["ATOM      3  CA AASN A   1      21.411  39.311   0.054  0.40  0.00           C  "], } 
        result = self.module.all_same_residue(inp)
        self.assertFalse(result)

    def test_partial_altloc(self):
        inp = {
            'A': [
                    "ATOM    333  CA AGLU A  26     -10.000  -3.000 -12.000  0.50  4.89           C  ",
                    "ANISOU  333  CA AGLU A  26      576    620    663     31     42     45       C  ",
                 ],
            'B':[
                "ATOM    333  CA CGLU A  26     -10.679  -3.437 -12.387  1.00  4.89           C  ",
                "ANISOU  333  CA CGLU A  26      576    620    663     31     42     45       C  ",
                ],
            }

        result = self.module.partial_altloc(inp)
        self.assertFalse(result)


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

    def test_gives_same_dummy_A(self):
        """Test dummy.pdb is not altered because there are not altlocs."""
        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 203)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[80],
            "ATOM      3  CA  ASN A   1      21.411  39.311   0.054  0.40  0.00           C  ")

    def test_gives_same_dummy_B(self):
        """Test dummy.pdb is not altered because there are not altlocs."""
        sys.argv = ['', '-B', os.path.join(data_dir, 'dummy.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 203)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[80],
            "ATOM      3  CA  ASN A   1      20.000  30.000   0.005  0.60  0.00           C  "
            )

    def test_gives_same_dummy_maxocc(self):
        """Test dummy.pdb is not altered because there are not altlocs."""
        sys.argv = ['', os.path.join(data_dir, 'dummy.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 203)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[80],
            "ATOM      3  CA  ASN A   1      20.000  30.000   0.005  0.60  0.00           C  "
            )

    def test_vu7_maxocc(self):
        """Test dummy.pdb is not altered because there are not altlocs."""
        sys.argv = ['', os.path.join(data_dir, 'vu7.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 30)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[15],
            "HETATM 2910  C27 VU7 A 403     -20.472  24.444  21.209  0.70 25.90           C  ",
            )
        self.assertEqual(
            self.stdout[23:30],
            [
                "HETATM 2918  C20 VU7 A 403     -25.101  22.166  21.562  1.00 19.10           C  ",
                "HETATM 2919  C22 VU7 A 403     -25.005  23.859  23.317  1.00 20.89           C  ",
                "HETATM 2921  C25 VU7 A 403     -21.980  23.567  22.880  0.70 25.16           C  ",
                "HETATM 2923  C26 VU7 A 403     -20.710  24.002  22.511  0.70 29.65           C  ",
                "HETATM 2925  C28 VU7 A 403     -21.503  24.451  20.265  0.70 24.53           C  ",
                "HETATM 2927  C29 VU7 A 403     -22.775  24.020  20.615  0.70 24.22           C  ",
                "HETATM 2929  F30 VU7 A 403     -23.749  24.031  19.675  0.70 26.05           F  ",
                ]
            )

    def test_vu7_maxocc_B(self):
        """Test dummy.pdb is not altered because there are not altlocs."""
        sys.argv = ['', os.path.join(data_dir, 'vu7.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 30)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[15],
            "HETATM 2910  C27 VU7 A 403     -20.472  24.444  21.209  0.70 25.90           C  ",
            )
        self.assertEqual(
            self.stdout[23:30],
            [
                "HETATM 2918  C20 VU7 A 403     -25.101  22.166  21.562  1.00 19.10           C  ",
                "HETATM 2919  C22 VU7 A 403     -25.005  23.859  23.317  1.00 20.89           C  ",
                "HETATM 2921  C25 VU7 A 403     -21.980  23.567  22.880  0.70 25.16           C  ",
                "HETATM 2923  C26 VU7 A 403     -20.710  24.002  22.511  0.70 29.65           C  ",
                "HETATM 2925  C28 VU7 A 403     -21.503  24.451  20.265  0.70 24.53           C  ",
                "HETATM 2927  C29 VU7 A 403     -22.775  24.020  20.615  0.70 24.22           C  ",
                "HETATM 2929  F30 VU7 A 403     -23.749  24.031  19.675  0.70 26.05           F  ",
                ]
            )

    def test_vu7_maxocc_A(self):
        """Test dummy.pdb is not altered because there are not altlocs."""
        sys.argv = ['', '-A', os.path.join(data_dir, 'vu7.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 30)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[15],
            "HETATM 2909  C27 VU7 A 403     -20.473  24.388  21.073  0.30 23.87           C  ",
            )
        self.assertEqual(
            self.stdout[23:30],
            [
                "HETATM 2918  C20 VU7 A 403     -25.101  22.166  21.562  1.00 19.10           C  ",
                "HETATM 2919  C22 VU7 A 403     -25.005  23.859  23.317  1.00 20.89           C  ",
                "HETATM 2920  C25 VU7 A 403     -22.814  24.071  20.642  0.30 22.86           C  ",
                "HETATM 2922  C26 VU7 A 403     -21.562  24.484  20.224  0.30 22.96           C  ",
                "HETATM 2924  C28 VU7 A 403     -20.656  23.873  22.343  0.30 25.28           C  ",
                "HETATM 2926  C29 VU7 A 403     -21.907  23.454  22.776  0.30 23.59           C  ",
                "HETATM 2928  F30 VU7 A 403     -22.039  22.963  24.024  0.30 24.64           F  ",
                ]
            )

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
