#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 João MC Teixeira
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
Unit Tests for `pdb_convertatoms`.
"""
import os
import sys
import unittest

from config import data_dir
from utils import OutputCapture

from pdbtools.pdb_convertatoms import convert_table

class TestTool(unittest.TestCase):
    """
    Generic class for testing tools.
    """
    def setUp(self):
        # Dynamically import the module
        name = 'pdbtools.pdb_convertatoms'
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

    def inspect_lines_are_same(self, stdout):
        """Test if line information outside atom name is kept constant."""

        with open(os.path.join(data_dir, 'dummy.pdb'), 'r') as fin:
            lines = (l.strip(os.linesep) for l in fin.readlines())

            for i, (l1, l2) in enumerate(zip(lines, stdout)):
                self.assertTrue(l1[:12] == l2[:12], msg=(i, l1[:12], l2[:12]))
                self.assertTrue(l1[16:] == l2[16:], msg=(i, l1[16:], l2[16:]))

    def test_atom_max_4_chars(self):
        """Test if all atoms have at most 4 chars."""
        for name, convention in convert_table.items():
            for residue, list_of_atoms in convention.items():
                for atom in list_of_atoms:
                    self.assertTrue(1 <= len(atom) <= 4, msg=atom)

    def test_convert_table_all_okay(self):
        """Test if convention dictionaries have same keys in same order."""
        keys = [sorted(list(d.keys())) for d in convert_table.values()]
        self.assertTrue(all(keys[0] == k for k in keys[1:]))

    def test_amber(self):
        """$ pdb_convertatoms -amber data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-amber', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_biopython(self):
        """$ pdb_convertatoms -biopython data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-biopython', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_bmrb(self):
        """$ pdb_convertatoms -bmrb data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-bmrb', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_cns(self):
        """$ pdb_convertatoms -cns data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-cns', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_iupac(self):
        """$ pdb_convertatoms -iupac data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-iupac', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_msi(self):
        """$ pdb_convertatoms -msi data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-msi', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_pdbv2(self):
        """$ pdb_convertatoms -pdbv2 data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-pdbv2', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_pdbv3(self):
        """$ pdb_convertatoms -pdbv3 data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-pdbv3', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_ucsf(self):
        """$ pdb_convertatoms -ucsf data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-ucsf', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_xplor(self):
        """$ pdb_convertatoms -xplor data/dummy.pdb"""
        # Simulate input
        sys.argv = ['', '-xplor', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors
        self.inspect_lines_are_same(self.stdout)

    def test_no_input_provided(self):
        """$ pdb_convertatoms """
        sys.argv = ['']
        self.exec_module()
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        emsg = 'ERROR! No input provided'
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)
        return

    def test_too_much_input_provided(self):
        """$ pdb_convertatoms -pdbv3 dummy.pdb yet_another_file.pdb"""
        sys.argv = ['', '-pdbv3', 'dummy.pdb', 'yet_another_file.pdb']
        self.exec_module()
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        emsg = 'ERROR! Too many arguments.'
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)
        return

    def test_first_not_an_option(self):
        """$ pdb_convertatoms data/dummy.pdb"""

        _file = os.path.join(data_dir, 'dummy.pdb')
        sys.argv = ['', _file]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        emsg = 'ERROR! First argument is not an option: \'{}\''
        emsg = emsg.format(_file)
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)

    def test_bad_option(self):
        """$ pdb_convertatoms -blabla data/dummy.pdb"""

        sys.argv = ['', '-blabla', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        emsg = 'ERROR! The option provided {!r} is not within the possible options: {}. '
        emsg = emsg.format('-blabla', list(convert_table.keys()))
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)

    def test_file_not_provided(self):
        """$ pdb_convertatoms -ucsf"""

        sys.argv = ['', '-ucsf']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        # proper error message
        emsg = 'ERROR!! No file provided.'
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)

    def test_file_not_exist(self):
        """$ pdb_convertatoms -ucsf not_existing.pdb"""

        sys.argv = ['', '-ucsf', 'not_existing.pdb']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        # proper error message
        emsg = 'ERROR!! File not found or not readable: \'{}\''
        emsg = emsg.format('not_existing.pdb')
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
