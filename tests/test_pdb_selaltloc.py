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

    def test_dummy_A(self):
        """Test -A with dummy.pdb."""
        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 203)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[69],
            "ATOM      3  CA  ASN A   1      21.411  39.311   0.054  0.40  0.00           C  ")

    def test_dummy_B(self):
        """Test -B with dummy.pdb."""
        sys.argv = ['', '-B', os.path.join(data_dir, 'dummy.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 203)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[69],
            "ATOM      3  CA  ASN A   1      20.000  30.000   0.005  0.60  0.00           C  ")

    def test_gives_the_same_dummy_C(self):
        """
        Test -C with dummy.pdb.

        Should output exactly the same PDB because there is not altloc 'C'.
        """
        sys.argv = ['', '-C', os.path.join(data_dir, 'dummy.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 204)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[70],
            "ATOM      3  CA AASN A   1      21.411  39.311   0.054  0.40  0.00           C  ")

        self.assertEqual(
            self.stdout[69],
            "ATOM      3  CA BASN A   1      20.000  30.000   0.005  0.60  0.00           C  ")

    def test_gives_same_dummy_maxocc(self):
        """Test select the maximum occurance."""
        sys.argv = ['', os.path.join(data_dir, 'dummy.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 203)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout[69],
            "ATOM      3  CA  ASN A   1      20.000  30.000   0.005  0.60  0.00           C  "
            )

    def test_vu7_maxocc(self):
        """Test vu7.pdb properly selects highest altloc."""
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
        """Test vu7.pdb properly selects altloc B."""
        sys.argv = ['', '-B', os.path.join(data_dir, 'vu7.pdb')]
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
        """Test vu7.pdb properly selects altloc A."""
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

    def test_anisou_lines(self):
        """
        Test anisou.pdb is not altered because there are not altlocs.

        anisou.pdb has ANISOU lines. Ensure bug reported in #130 is
        corrected.
        """
        infile = os.path.join(data_dir, 'anisou.pdb')
        for opt in ('', '-A', '-B'):
            sys.argv = [opt, infile]
            self.exec_module()
            self.assertEqual(self.retcode, 0)
            self.assertEqual(len(self.stdout), 24)
            self.assertEqual(len(self.stderr), 0)
            with open(infile, "r") as fin:
                expected_lines = [l.strip(os.linesep) for l in fin.readlines()]
            self.assertEqual(self.stdout, expected_lines)

    def test_anisou_with_altloc_maxocc(self):
        """
        Test anisou_altloc.pdb properly selects the highest altloc.

        anisou.pdb has ANISOU lines. Ensure bug reported in #130 is
        corrected.
        """
        infile = os.path.join(data_dir, 'anisou_altloc.pdb')
        sys.argv = ['', infile]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 24)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout,
            [
                "ATOM      1  N   ALA A  31     -12.806   6.423  23.735  0.60 70.81           N  ",
                "ANISOU    1  N   ALA A  31     7836   7867  11203   2151   -675    -66       N  ",
                "ATOM      2  CA  ALA A  31     -13.433   7.788  23.746  0.60 65.66           C  ",
                "ANISOU    2  CA  ALA A  31     7296   7485  10167   1829   -642    -81       C  ",
                "ATOM      3  C   ALA A  31     -12.448   8.891  24.124  1.00 63.44           C  ",
                "ANISOU    3  C   ALA A  31     6818   7632   9654   1744   -656     20       C  ",
                "ATOM      4  O   ALA A  31     -11.549   8.680  24.937  1.00 65.52           O  ",
                "ANISOU    4  O   ALA A  31     6891   8010   9994   1853   -759    238       O  ",
                "ATOM      5  CB  ALA A  31     -14.628   7.834  24.691  1.00 66.76           C  ",
                "ANISOU    5  CB  ALA A  31     7636   7487  10242   1630   -748    143       C  ",
                "ATOM      6  N   THR A  32     -12.659  10.075  23.550  1.00 58.59           N  ",
                "ANISOU    6  N   THR A  32     6249   7244   8768   1532   -569   -122       N  ",
                "ATOM      7  CA  THR A  32     -11.806  11.232  23.788  1.00 55.42           C  ",
                "ANISOU    7  CA  THR A  32     5678   7217   8161   1398   -585    -53       C  ",
                "ATOM      8  C   THR A  32     -12.119  11.857  25.148  1.00 52.59           C  ",
                "ANISOU    8  C   THR A  32     5384   6947   7651   1206   -743    183       C  ",
                "ATOM      9  O   THR A  32     -13.166  11.585  25.770  1.00 49.84           O  ",
                "ANISOU    9  O   THR A  32     5232   6412   7293   1142   -803    278       O  ",
                "ATOM     10  CB  THR A  32     -11.965  12.321  22.696  0.55 51.87           C  ",
                "ANISOU   10  CB  THR A  32     5260   6948   7500   1220   -449   -254       C  ",
                "ATOM     11  OG1 THR A  32     -13.294  12.844  22.720  1.00 48.11           O  ",
                "ANISOU   11  OG1 THR A  32     5047   6344   6890   1015   -452   -282       O  ",
                "ATOM     12  CG2 THR A  32     -11.660  11.781  21.303  1.00 54.23           C  ",
                "ANISOU   12  CG2 THR A  32     5483   7248   7875   1398   -280   -508       C  ",
                ]
            )

    def test_anisou_with_altloc_maxocc_A(self):
        """
        Test anisou_altloc.pdb selects altloc -A.

        anisou.pdb has ANISOU lines. Ensure bug reported in #130 is
        corrected.
        """
        infile = os.path.join(data_dir, 'anisou_altloc.pdb')
        sys.argv = ['', '-A', infile]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 24)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout,
            [
                "ATOM      1  N   ALA A  31     -12.806   6.423  23.735  0.40 70.81           N  ",
                "ANISOU    1  N   ALA A  31     7836   7867  11203   2151   -675    -66       N  ",
                "ATOM      2  CA  ALA A  31     -13.433   7.788  23.746  0.60 65.66           C  ",
                "ANISOU    2  CA  ALA A  31     7296   7485  10167   1829   -642    -81       C  ",
                "ATOM      3  C   ALA A  31     -12.448   8.891  24.124  1.00 63.44           C  ",
                "ANISOU    3  C   ALA A  31     6818   7632   9654   1744   -656     20       C  ",
                "ATOM      4  O   ALA A  31     -11.549   8.680  24.937  1.00 65.52           O  ",
                "ANISOU    4  O   ALA A  31     6891   8010   9994   1853   -759    238       O  ",
                "ATOM      5  CB  ALA A  31     -14.628   7.834  24.691  1.00 66.76           C  ",
                "ANISOU    5  CB  ALA A  31     7636   7487  10242   1630   -748    143       C  ",
                "ATOM      6  N   THR A  32     -12.659  10.075  23.550  1.00 58.59           N  ",
                "ANISOU    6  N   THR A  32     6249   7244   8768   1532   -569   -122       N  ",
                "ATOM      7  CA  THR A  32     -11.806  11.232  23.788  1.00 55.42           C  ",
                "ANISOU    7  CA  THR A  32     5678   7217   8161   1398   -585    -53       C  ",
                "ATOM      8  C   THR A  32     -12.119  11.857  25.148  1.00 52.59           C  ",
                "ANISOU    8  C   THR A  32     5384   6947   7651   1206   -743    183       C  ",
                "ATOM      9  O   THR A  32     -13.166  11.585  25.770  1.00 49.84           O  ",
                "ANISOU    9  O   THR A  32     5232   6412   7293   1142   -803    278       O  ",
                "ATOM     10  CB  THR A  32     -11.965  12.321  22.696  0.45 51.87           C  ",
                "ANISOU   10  CB  THR A  32     5260   6948   7500   1220   -449   -254       C  ",
                "ATOM     11  OG1 THR A  32     -13.294  12.844  22.720  1.00 48.11           O  ",
                "ANISOU   11  OG1 THR A  32     5047   6344   6890   1015   -452   -282       O  ",
                "ATOM     12  CG2 THR A  32     -11.660  11.781  21.303  1.00 54.23           C  ",
                "ANISOU   12  CG2 THR A  32     5483   7248   7875   1398   -280   -508       C  ",
                ]
            )

    def test_anisou_with_altloc_maxocc_B(self):
        """
        Test anisou_altloc.pdb selects altloc -B.

        anisou.pdb has ANISOU lines. Ensure bug reported in #130 is
        corrected.
        """
        infile = os.path.join(data_dir, 'anisou_altloc.pdb')
        sys.argv = ['', '-B', infile]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 24)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout,
            [
                "ATOM      1  N   ALA A  31     -12.806   6.423  23.735  0.60 70.81           N  ",
                "ANISOU    1  N   ALA A  31     7836   7867  11203   2151   -675    -66       N  ",
                "ATOM      2  CA  ALA A  31     -13.433   7.788  23.746  0.40 65.66           C  ",
                "ANISOU    2  CA  ALA A  31     7296   7485  10167   1829   -642    -81       C  ",
                "ATOM      3  C   ALA A  31     -12.448   8.891  24.124  1.00 63.44           C  ",
                "ANISOU    3  C   ALA A  31     6818   7632   9654   1744   -656     20       C  ",
                "ATOM      4  O   ALA A  31     -11.549   8.680  24.937  1.00 65.52           O  ",
                "ANISOU    4  O   ALA A  31     6891   8010   9994   1853   -759    238       O  ",
                "ATOM      5  CB  ALA A  31     -14.628   7.834  24.691  1.00 66.76           C  ",
                "ANISOU    5  CB  ALA A  31     7636   7487  10242   1630   -748    143       C  ",
                "ATOM      6  N   THR A  32     -12.659  10.075  23.550  1.00 58.59           N  ",
                "ANISOU    6  N   THR A  32     6249   7244   8768   1532   -569   -122       N  ",
                "ATOM      7  CA  THR A  32     -11.806  11.232  23.788  1.00 55.42           C  ",
                "ANISOU    7  CA  THR A  32     5678   7217   8161   1398   -585    -53       C  ",
                "ATOM      8  C   THR A  32     -12.119  11.857  25.148  1.00 52.59           C  ",
                "ANISOU    8  C   THR A  32     5384   6947   7651   1206   -743    183       C  ",
                "ATOM      9  O   THR A  32     -13.166  11.585  25.770  1.00 49.84           O  ",
                "ANISOU    9  O   THR A  32     5232   6412   7293   1142   -803    278       O  ",
                "ATOM     10  CB  THR A  32     -11.965  12.321  22.696  0.55 51.87           C  ",
                "ANISOU   10  CB  THR A  32     5260   6948   7500   1220   -449   -254       C  ",
                "ATOM     11  OG1 THR A  32     -13.294  12.844  22.720  1.00 48.11           O  ",
                "ANISOU   11  OG1 THR A  32     5047   6344   6890   1015   -452   -282       O  ",
                "ATOM     12  CG2 THR A  32     -11.660  11.781  21.303  1.00 54.23           C  ",
                "ANISOU   12  CG2 THR A  32     5483   7248   7875   1398   -280   -508       C  ",
                ]
            )

    def test_anisou_missing(self):
        """
        Works properly even when there are missing anisou lines.

        In this case, it does not alter the file.
        """
        infile = os.path.join(data_dir, 'anisou_missing.pdb')
        for opt in ('', '-A'):
            sys.argv = [opt, infile]
            self.exec_module()
            self.assertEqual(self.retcode, 0)
            with open(infile, "r") as fin:
                expected_lines = [l.strip(os.linesep) for l in fin.readlines()]
            self.assertEqual(self.stdout, expected_lines)

    def test_captures_previous_residue_maxocc_A(self):
        """
        Test the previous residue is not lost.

        In version 2.4.5 we realised that the residue previous to the
        residues having alternative locations was missing. See dummy_altloc3.pdb.
        """
        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy_altloc3.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 25)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout,
            [
                "ATOM    153  N   VAL A  18      -0.264 -17.574  22.788  0.00  0.00           N  ",
                "ATOM    154  CA  VAL A  18      -0.201 -17.901  24.209  0.00  0.00           C  ",
                "ATOM    155  C   VAL A  18      -1.047 -19.150  24.437  0.00  0.00           C  ",
                "ATOM    156  O   VAL A  18      -2.260 -19.144  24.214  0.00  0.00           O  ",
                "ATOM    157  CB  VAL A  18      -0.689 -16.724  25.084  0.00  0.00           C  ",
                "ATOM    161  N   TRP A  19      -0.408 -20.230  24.882  0.00  0.00           N  ",
                "ATOM    162  CA  TRP A  19      -1.091 -21.490  25.161  0.00  0.00           C  ",
                "ATOM    163  C   TRP A  19      -1.303 -21.563  26.667  0.00  0.00           C  ",
                "ATOM    164  O   TRP A  19      -0.357 -21.920  27.375  0.00  0.00           O  ",
                "ATOM    165  CB  TRP A  19      -0.272 -22.670  24.635  0.00  0.00           C  ",
                "ATOM    176  N   TYR A  20      -2.522 -21.226  27.083  0.00  0.00           N  ",
                "ATOM    177  CA  TYR A  20      -2.898 -21.178  28.493  0.00  0.00           C  ",
                "ATOM    178  C   TYR A  20      -3.718 -22.410  28.851  0.00  0.00           C  ",
                "ATOM    179  O   TYR A  20      -4.629 -22.780  28.105  0.00  0.00           O  ",
                "ATOM    180  CB  TYR A  20      -3.681 -19.898  28.795  0.00  0.00           C  ",
                "ATOM    189  N   VAL A  21      -3.396 -23.034  29.982  0.40  0.00           N  ",
                "ATOM    190  CA  VAL A  21      -4.121 -24.205  30.467  0.40  0.00           C  ",
                "ATOM    191  C   VAL A  21      -4.530 -24.072  31.930  0.40  0.00           C  ",
                "ATOM    192  O   VAL A  21      -3.835 -23.461  32.747  0.40  0.00           O  ",
                "ATOM    193  CB  VAL A  21      -3.289 -25.497  30.298  0.40  0.00           C  ",
                "ATOM    189  N   PRO A  22      -3.396 -23.034  29.982  0.40  0.00           N  ",
                "ATOM    190  CA  PRO A  22      -4.121 -24.205  30.467  0.40  0.00           C  ",
                "ATOM    191  C   PRO A  22      -4.530 -24.072  31.930  0.40  0.00           C  ",
                "ATOM    192  O   PRO A  22      -3.835 -23.461  32.747  0.40  0.00           O  ",
                "ATOM    193  CB  PRO A  22      -3.289 -25.497  30.298  0.40  0.00           C  ",
                ]
            )

    def test_captures_previous_residue_maxocc(self):
        """
        Test the previous residue is not lost.

        In version 2.4.5 we realised that the residue previous to the
        residues having alternative locations was missing. See dummy_altloc3.pdb.
        """
        sys.argv = ['', os.path.join(data_dir, 'dummy_altloc3.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 25)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout,
            [
                "ATOM    153  N   VAL A  18      -0.264 -17.574  22.788  0.00  0.00           N  ",
                "ATOM    154  CA  VAL A  18      -0.201 -17.901  24.209  0.00  0.00           C  ",
                "ATOM    155  C   VAL A  18      -1.047 -19.150  24.437  0.00  0.00           C  ",
                "ATOM    156  O   VAL A  18      -2.260 -19.144  24.214  0.00  0.00           O  ",
                "ATOM    157  CB  VAL A  18      -0.689 -16.724  25.084  0.00  0.00           C  ",
                "ATOM    161  N   TRP A  19      -0.408 -20.230  24.882  0.00  0.00           N  ",
                "ATOM    162  CA  TRP A  19      -1.091 -21.490  25.161  0.00  0.00           C  ",
                "ATOM    163  C   TRP A  19      -1.303 -21.563  26.667  0.00  0.00           C  ",
                "ATOM    164  O   TRP A  19      -0.357 -21.920  27.375  0.00  0.00           O  ",
                "ATOM    165  CB  TRP A  19      -0.272 -22.670  24.635  0.00  0.00           C  ",
                "ATOM    176  N   TYR A  20      -2.522 -21.226  27.083  0.00  0.00           N  ",
                "ATOM    177  CA  TYR A  20      -2.898 -21.178  28.493  0.00  0.00           C  ",
                "ATOM    178  C   TYR A  20      -3.718 -22.410  28.851  0.00  0.00           C  ",
                "ATOM    179  O   TYR A  20      -4.629 -22.780  28.105  0.00  0.00           O  ",
                "ATOM    180  CB  TYR A  20      -3.681 -19.898  28.795  0.00  0.00           C  ",
                "ATOM    197  N   ALA A  21      -5.676 -24.647  32.284  0.60  0.00           N  ",
                "ATOM    198  CA  ALA A  21      -6.012 -24.814  33.696  0.60  0.00           C  ",
                "ATOM    199  C   ALA A  21      -4.990 -25.677  34.426  0.60  0.00           C  ",
                "ATOM    200  O   ALA A  21      -4.494 -26.675  33.897  0.60  0.00           O  ",
                "ATOM    201  CB  ALA A  21      -7.405 -25.428  33.847  0.60  0.00           C  ",
                "ATOM    197  N   GLY A  22      -5.676 -24.647  32.284  0.60  0.00           N  ",
                "ATOM    198  CA  GLY A  22      -6.012 -24.814  33.696  0.60  0.00           C  ",
                "ATOM    199  C   GLY A  22      -4.990 -25.677  34.426  0.60  0.00           C  ",
                "ATOM    200  O   GLY A  22      -4.494 -26.675  33.897  0.60  0.00           O  ",
                "ATOM    201  CB  GLY A  22      -7.405 -25.428  33.847  0.60  0.00           C  ",
                ]
            )

    def test_captures_previous_residue_maxocc_B(self):
        """
        Test the previous residue is not lost.

        In version 2.4.5 we realised that the residue previous to the
        residues having alternative locations was missing. See dummy_altloc3.pdb.
        """
        sys.argv = ['', '-B', os.path.join(data_dir, 'dummy_altloc3.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 25)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout,
            [
                "ATOM    153  N   VAL A  18      -0.264 -17.574  22.788  0.00  0.00           N  ",
                "ATOM    154  CA  VAL A  18      -0.201 -17.901  24.209  0.00  0.00           C  ",
                "ATOM    155  C   VAL A  18      -1.047 -19.150  24.437  0.00  0.00           C  ",
                "ATOM    156  O   VAL A  18      -2.260 -19.144  24.214  0.00  0.00           O  ",
                "ATOM    157  CB  VAL A  18      -0.689 -16.724  25.084  0.00  0.00           C  ",
                "ATOM    161  N   TRP A  19      -0.408 -20.230  24.882  0.00  0.00           N  ",
                "ATOM    162  CA  TRP A  19      -1.091 -21.490  25.161  0.00  0.00           C  ",
                "ATOM    163  C   TRP A  19      -1.303 -21.563  26.667  0.00  0.00           C  ",
                "ATOM    164  O   TRP A  19      -0.357 -21.920  27.375  0.00  0.00           O  ",
                "ATOM    165  CB  TRP A  19      -0.272 -22.670  24.635  0.00  0.00           C  ",
                "ATOM    176  N   TYR A  20      -2.522 -21.226  27.083  0.00  0.00           N  ",
                "ATOM    177  CA  TYR A  20      -2.898 -21.178  28.493  0.00  0.00           C  ",
                "ATOM    178  C   TYR A  20      -3.718 -22.410  28.851  0.00  0.00           C  ",
                "ATOM    179  O   TYR A  20      -4.629 -22.780  28.105  0.00  0.00           O  ",
                "ATOM    180  CB  TYR A  20      -3.681 -19.898  28.795  0.00  0.00           C  ",
                "ATOM    197  N   ALA A  21      -5.676 -24.647  32.284  0.60  0.00           N  ",
                "ATOM    198  CA  ALA A  21      -6.012 -24.814  33.696  0.60  0.00           C  ",
                "ATOM    199  C   ALA A  21      -4.990 -25.677  34.426  0.60  0.00           C  ",
                "ATOM    200  O   ALA A  21      -4.494 -26.675  33.897  0.60  0.00           O  ",
                "ATOM    201  CB  ALA A  21      -7.405 -25.428  33.847  0.60  0.00           C  ",
                "ATOM    197  N   GLY A  22      -5.676 -24.647  32.284  0.60  0.00           N  ",
                "ATOM    198  CA  GLY A  22      -6.012 -24.814  33.696  0.60  0.00           C  ",
                "ATOM    199  C   GLY A  22      -4.990 -25.677  34.426  0.60  0.00           C  ",
                "ATOM    200  O   GLY A  22      -4.494 -26.675  33.897  0.60  0.00           O  ",
                "ATOM    201  CB  GLY A  22      -7.405 -25.428  33.847  0.60  0.00           C  ",
                ]
            )
    
    def test_handle_multiple_residues(self):
        """
        pdb_selaltloc data/pdb4xoj-small.pdb.

        The test checks that the SER85 residue is not removed by pdb_selaltloc
        as it happened until version 2.5.0.
        """
        sys.argv = ['', os.path.join(data_dir, 'pdb4xoj-small.pdb')]
        print("executing")
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 80)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout,
            [
                "ATOM    511  N   SER A  81      -2.125   6.104  21.775  1.00  8.48           N  ",
                "ANISOU  511  N   SER A  81     1227    964   1028    -36    224     13       N  ",
                "ATOM    512  CA  SER A  81      -1.772   4.741  22.205  1.00  8.74           C  ",
                "ANISOU  512  CA  SER A  81     1233   1007   1077     11    199     56       C  ",
                "ATOM    513  C   SER A  81      -2.262   3.698  21.215  1.00  8.42           C  ",
                "ANISOU  513  C   SER A  81     1167    989   1041    -75     90    138       C  ",
                "ATOM    514  O   SER A  81      -3.353   3.829  20.638  1.00  9.44           O  ",
                "ANISOU  514  O   SER A  81     1153   1058   1375    -48     41     62       O  ",
                "ATOM    515  CB  SER A  81      -2.424   4.479  23.564  1.00 10.45           C  ",
                "ANISOU  515  CB  SER A  81     1683   1191   1094    -49    249     19       C  ",
                "ATOM    516  OG  SER A  81      -1.889   5.387  24.506  1.00 13.63           O  ",
                "ANISOU  516  OG  SER A  81     2449   1531   1199    -52    258     -6       O  ",
                "ATOM    517  N   ALA A  82      -1.494   2.619  21.079  0.50  8.56           N  ",
                "ANISOU  517  N   ALA A  82     1205    991   1055     55     81      1       N  ",
                "ATOM    519  CA  ALA A  82      -2.054   1.440  20.442  0.50  8.66           C  ",
                "ANISOU  519  CA  ALA A  82     1292    950   1046     -2     73     22       C  ",
                "ATOM    521  C   ALA A  82      -3.189   0.918  21.328  0.50  8.99           C  ",
                "ANISOU  521  C   ALA A  82     1375    993   1045     73    344    138       C  ",
                "ATOM    523  O   ALA A  82      -3.041   0.736  22.520  0.80 10.64           O  ",
                "ANISOU  523  O   ALA A  82     1631   1389   1020   -117    191     98       O  ",
                "ATOM    525  CB  ALA A  82      -0.983   0.385  20.289  0.50  8.83           C  ",
                "ANISOU  525  CB  ALA A  82     1351   1028    974     41    216     30       C  ",
                "ATOM    527  N   SER A  83      -4.261   0.519  20.678  1.00  9.47           N  ",
                "ANISOU  527  N   SER A  83     1432   1102   1061   -125    244     55       N  ",
                "ATOM    528  CA  SER A  83      -5.308  -0.275  21.345  0.70 10.42           C  ",
                "ANISOU  528  CA  SER A  83     1524   1180   1256     61    497    220       C  ",
                "ATOM    530  C   SER A  83      -5.324  -1.728  20.924  1.00 10.39           C  ",
                "ANISOU  530  C   SER A  83     1457   1076   1412     -6    466    118       C  ",
                "ATOM    531  O   SER A  83      -5.811  -2.551  21.683  1.00 12.89           O  ",
                "ANISOU  531  O   SER A  83     2075   1194   1628    -49    830    133       O  ",
                "ATOM    532  CB  SER A  83      -6.691   0.285  21.121  0.70 11.38           C  ",
                "ANISOU  532  CB  SER A  83     1538   1167   1615    116    448     25       C  ",
                "ATOM    534  OG  SER A  83      -6.965   0.397  19.729  0.70 11.09           O  ",
                "ANISOU  534  OG  SER A  83     1338   1455   1418    106    285     72       O  ",
                "ATOM    536  N   LYS A  84      -4.827  -2.055  19.735  1.00  9.68           N  ",
                "ANISOU  536  N   LYS A  84     1326   1010   1339    101    429     46       N  ",
                "ATOM    537  CA  LYS A  84      -4.644  -3.431  19.279  0.70 10.05           C  ",
                "ANISOU  537  CA  LYS A  84     1522   1007   1287     42    336    144       C  ",
                "ATOM    539  C   LYS A  84      -3.278  -3.508  18.640  1.00  9.20           C  ",
                "ANISOU  539  C   LYS A  84     1375   1055   1064     95    218     67       C  ",
                "ATOM    540  O   LYS A  84      -2.951  -2.592  17.884  1.00  9.59           O  ",
                "ANISOU  540  O   LYS A  84     1298   1105   1241    165    244    147       O  ",
                "ATOM    541  CB  LYS A  84      -5.744  -3.907  18.283  0.70 10.32           C  ",
                "ANISOU  541  CB  LYS A  84     1408   1097   1416    -68     49    -77       C  ",
                "ATOM    543  CG  LYS A  84      -7.150  -3.728  18.755  0.70 12.75           C  ",
                "ANISOU  543  CG  LYS A  84     1483   1417   1942   -138    412    254       C  ",
                "ATOM    545  CD  LYS A  84      -8.204  -4.287  17.849  0.70 14.48           C  ",
                "ANISOU  545  CD  LYS A  84     1679   1886   1936   -324    273    150       C  ",
                "ATOM    547  CE  LYS A  84      -9.569  -4.039  18.445  0.70 21.19           C  ",
                "ANISOU  547  CE  LYS A  84     1246   3570   3235   -471    223    759       C  ",
                "ATOM    549  NZ  LYS A  84     -10.614  -4.841  17.764  0.70 22.64           N  ",
                "ANISOU  549  NZ  LYS A  84     2289   3604   2707  -1098    686    -21       N  ",
                "ATOM    551  N   SER A  85      -2.563  -4.588  18.881  0.50  9.32           N  ",
                "ANISOU  551  N   SER A  85     1536    976   1028    171    216     66       N  ",
                "ATOM    553  CA  SER A  85      -1.332  -4.882  18.202  0.50  8.74           C  ",
                "ANISOU  553  CA  SER A  85     1455   1080    786    116     49    -76       C  ",
                "ATOM    555  C   SER A  85      -1.483  -6.317  17.695  0.50  9.92           C  ",
                "ANISOU  555  C   SER A  85     1752    836   1179    282    208   -106       C  ",
                "ATOM    557  O   SER A  85      -1.652  -7.279  18.484  0.50 11.61           O  ",
                "ANISOU  557  O   SER A  85     2551    941    916    222    215     86       O  ",
                "ATOM    559  CB  SER A  85      -0.160  -4.700  19.129  0.50 12.48           C  ",
                "ANISOU  559  CB  SER A  85     1350   1725   1666    185   -278     -2       C  ",
                "ATOM    561  OG  SER A  85      -0.049  -3.356  19.526  0.50 16.00           O  ",
                "ANISOU  561  OG  SER A  85     1752   2069   2256    354   -901   -970       O  ",
                "ATOM    563  N   ILE A  86      -1.504  -6.433  16.390  1.00  7.88           N  ",
                "ANISOU  563  N   ILE A  86     1184    936    872     61    178     65       N  ",
                "ATOM    564  CA  ILE A  86      -1.872  -7.694  15.783  1.00  7.95           C  ",
                "ANISOU  564  CA  ILE A  86     1192    863    963    -21    192    154       C  ",
                "ATOM    565  C   ILE A  86      -0.722  -8.196  14.932  1.00  7.58           C  ",
                "ANISOU  565  C   ILE A  86     1181    748    949   -103    205     87       C  ",
                "ATOM    566  O   ILE A  86      -0.535  -7.767  13.777  1.00  8.17           O  ",
                "ANISOU  566  O   ILE A  86     1249    887    967    -55    242    135       O  ",
                "ATOM    567  CB  ILE A  86      -3.164  -7.571  14.969  1.00  8.30           C  ",
                "ANISOU  567  CB  ILE A  86     1190    920   1043    -32    175    224       C  ",
                "ATOM    568  CG1 ILE A  86      -4.302  -7.000  15.799  1.00  9.14           C  ",
                "ANISOU  568  CG1 ILE A  86     1182   1078   1211     15    159    194       C  ",
                "ATOM    569  CG2 ILE A  86      -3.524  -8.934  14.351  1.00  8.71           C  ",
                "ANISOU  569  CG2 ILE A  86     1228    984   1097    -91     80    176       C  ",
                "ATOM    570  CD1 ILE A  86      -5.630  -6.861  15.071  1.00 10.85           C  ",
                "ANISOU  570  CD1 ILE A  86     1307   1331   1482     31    162    271       C  "
                ]
            )

    def test_take_first(self):
        """
        Takes the first occurence when occ is the same and no option is given.

        See: https://github.com/haddocking/pdb-tools/issues/153#issuecomment-1488627668
        """
        sys.argv = ['', os.path.join(data_dir, 'dummy_altloc4.pdb')]
        self.exec_module()
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 25)
        self.assertEqual(len(self.stderr), 0)
        self.assertEqual(
            self.stdout,
            [
                "ATOM    153  N   VAL A  18      -0.264 -17.574  22.788  0.00  0.00           N  ",
                "ATOM    154  CA  VAL A  18      -0.201 -17.901  24.209  0.00  0.00           C  ",
                "ATOM    155  C   VAL A  18      -1.047 -19.150  24.437  0.00  0.00           C  ",
                "ATOM    156  O   VAL A  18      -2.260 -19.144  24.214  0.00  0.00           O  ",
                "ATOM    157  CB  VAL A  18      -0.689 -16.724  25.084  0.00  0.00           C  ",
                "ATOM    161  N   TRP A  19      -0.408 -20.230  24.882  0.00  0.00           N  ",
                "ATOM    162  CA  TRP A  19      -1.091 -21.490  25.161  0.00  0.00           C  ",
                "ATOM    163  C   TRP A  19      -1.303 -21.563  26.667  0.00  0.00           C  ",
                "ATOM    164  O   TRP A  19      -0.357 -21.920  27.375  0.00  0.00           O  ",
                "ATOM    165  CB  TRP A  19      -0.272 -22.670  24.635  0.00  0.00           C  ",
                "ATOM    176  N   TYR A  20      -2.522 -21.226  27.083  0.00  0.00           N  ",
                "ATOM    177  CA  TYR A  20      -2.898 -21.178  28.493  0.00  0.00           C  ",
                "ATOM    178  C   TYR A  20      -3.718 -22.410  28.851  0.00  0.00           C  ",
                "ATOM    179  O   TYR A  20      -4.629 -22.780  28.105  0.00  0.00           O  ",
                "ATOM    180  CB  TYR A  20      -3.681 -19.898  28.795  0.00  0.00           C  ",
                "ATOM    189  N   VAL A  21      -3.396 -23.034  29.982  0.50  0.00           N  ",
                "ATOM    190  CA  VAL A  21      -4.121 -24.205  30.467  0.50  0.00           C  ",
                "ATOM    191  C   VAL A  21      -4.530 -24.072  31.930  0.50  0.00           C  ",
                "ATOM    192  O   VAL A  21      -3.835 -23.461  32.747  0.50  0.00           O  ",
                "ATOM    193  CB  VAL A  21      -3.289 -25.497  30.298  0.50  0.00           C  ",
                "ATOM    189  N   PRO A  22      -3.396 -23.034  29.982  0.50  0.00           N  ",
                "ATOM    190  CA  PRO A  22      -4.121 -24.205  30.467  0.50  0.00           C  ",
                "ATOM    191  C   PRO A  22      -4.530 -24.072  31.930  0.50  0.00           C  ",
                "ATOM    192  O   PRO A  22      -3.835 -23.461  32.747  0.50  0.00           O  ",
                "ATOM    193  CB  PRO A  22      -3.289 -25.497  30.298  0.50  0.00           C  ",
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

    @unittest.skipIf(os.getenv('SKIP_TTY_TESTS'), 'skip on GHA - no TTY')
    def test_file_missing(self):
        """$ pdb_selaltloc -A"""

        sys.argv = ['', '-A']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! No data to process!")



    @unittest.skipIf(os.getenv('SKIP_TTY_TESTS'), 'skip on GHA - no TTY')
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
