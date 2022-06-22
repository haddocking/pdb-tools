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
Unit Tests for `pdb_intersect`.
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
        name = 'pdbtools.pdb_intersect'
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
        """$ pdb_intersect data/dummy.pdb data/dummy.pdb"""

        # Simulate input
        sys.argv = ['', os.path.join(data_dir, 'dummy.pdb'),
                    os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 188)  # no lines deleted. Same file.
        self.assertEqual(len(self.stderr), 0)  # no errors

        atom_names = [l[12:16] for l in self.stdout]

        # Test content
        atoms_list = [' N  ', ' H  ', ' H2 ', ' H3 ', ' CA ', ' HA ', ' CB ',
                      ' HB2', ' HB3', ' CG ', ' HG2', ' HG3', ' CD ', ' HD2',
                      ' HD3', ' NE ', ' HE ', ' CZ ', ' NH1', 'HH11', 'HH12',
                      ' NH2', 'HH21', 'HH22', ' C  ', ' O  ', ' N  ', ' H  ',
                      ' CA ', ' HA ', ' CB ', ' HB2', ' HB3', ' CG ', ' HG2',
                      ' HG3', ' CD ', ' OE1', ' OE2', ' C  ', ' O  ', ' N  ',
                      ' H  ', ' CA ', ' HA ', ' CB ', ' HB1', ' HB2', ' HB3',
                      ' C  ', ' O  ', '    ', ' N  ', ' H  ', ' H2 ', ' H3 ',
                      ' CA ', ' CA ', ' HA ', ' CB ', ' HB2', ' HB3', ' CG ',
                      ' OD1', ' ND2', 'HD21', 'HD22', ' C  ', ' O  ', ' N  ',
                      ' H  ', ' CA ', ' HA ', ' CB ', ' HB2', ' HB3', ' CG ',
                      ' HG2', ' HG3', ' CD ', ' HD2', ' HD3', ' NE ', ' HE ',
                      ' CZ ', ' NH1', 'HH11', 'HH12', ' NH2', 'HH21', 'HH22',
                      ' C  ', ' O  ', ' N  ', ' H  ', ' CA ', ' HA ', ' CB ',
                      ' HB2', ' HB3', ' CG ', ' HG2', ' HG3', ' CD ', ' OE1',
                      ' OE2', ' C  ', ' O  ', '    ', ' N  ', ' H  ', ' H2 ',
                      ' H3 ', ' CA ', ' HA ', ' CB ', ' HB2', ' HB3', ' CG ',
                      ' HG2', ' HG3', ' CD ', ' HD2', ' HD3', ' NE ', ' HE ',
                      ' CZ ', ' NH1', 'HH11', 'HH12', ' NH2', 'HH21', 'HH22',
                      ' C  ', ' O  ', ' N  ', ' H  ', ' CA ', ' HA ', ' CB ',
                      ' HB2', ' HB3', ' CG ', ' HG2', ' HG3', ' CD ', ' OE1',
                      ' OE2', ' C  ', ' O  ', ' N  ', ' CA ', ' C  ', ' O  ',
                      ' CB ', ' CG ', ' SD ', ' CE ', '    ', ' P  ', ' OP1',
                      ' OP2', " O5'", " C5'", " C4'", " O4'", " C3'", " O3'",
                      " C2'", " C1'", ' N1 ', ' C2 ', ' O2 ', ' N3 ', ' C4 ',
                      ' O4 ', ' C5 ', ' C7 ', ' C6 ', 'CA  ', ' O  ', ' O  ',
                      ' O  ', ' O  ', ' O  ', ' O  ', ' O  ', ' O  ']

        self.assertEqual(atoms_list, atom_names)

    def test_file_not_found(self):
        """$ pdb_intersect not_existing.pdb"""

        # Error (file not found)
        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    @unittest.skipIf(sys.platform.startswith('win'), 'skip on Windows - requires TTY')
    def test_helptext(self):
        """$ pdb_intersect"""

        sys.argv = ['']

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
