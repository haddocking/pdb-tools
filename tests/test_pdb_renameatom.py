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
Unit Tests for `pdb_renameatom`.
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
        name = 'pdbtools.pdb_renameatom'
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

    def test_one_option(self):
        """$ pdb_renameatom -HG2,XXX data/dummy.pdb"""

        # Simulate input
        sys.argv = ['', '-HG2,XXX', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors

        hg2_count = sum(1 for l in self.stdout if l[12:16].strip() == 'HG2')
        self.assertEqual(hg2_count, 0)
        xxx_count = sum(1 for l in self.stdout if l[12:16].strip() == 'XXX')
        self.assertEqual(xxx_count, 6)

    def test_DNA_example(self):
        """$ pdb_renameatom -O5',O6' data/dummy.pdb"""

        # Simulate input
        sys.argv = ['', "-O5',O6'", os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # all file lines
        self.assertEqual(len(self.stderr), 0)  # no errors

        hg2_count = sum(1 for l in self.stdout if l[12:16].strip() == "O5'")
        self.assertEqual(hg2_count, 0)
        xxx_count = sum(1 for l in self.stdout if l[12:16].strip() == "O6'")
        self.assertEqual(xxx_count, 1)

    def test_no_input_provided(self):
        """$ pdb_renameatom """
        sys.argv = ['']
        self.exec_module()
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        emsg = 'ERROR! No input provided'
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)
        return

    def test_too_much_input_provided(self):
        """$ pdb_renameatom -HB2,HB3 dummy.pdb yet_another_file.pdb"""
        sys.argv = ['', '-HB2,HB3', 'dummy.pdb', 'yet_another_file.pdb']
        self.exec_module()
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        emsg = 'ERROR! Too many arguments.'
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)
        return

    def test_invalid_option(self):
        """$ pdb_renameatom data/dummy.pdb"""

        _file = os.path.join(data_dir, 'dummy.pdb')
        sys.argv = ['', _file]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        emsg = 'ERROR! First argument is not an option: \'{}\''
        emsg = emsg.format(_file)
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)

    def test_atom2_missing(self):
        """$ pdb_renameatom -AT1 data/dummy.pdb"""

        sys.argv = ['', '-AT1', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        emsg = 'ERROR! You need to provide two atom names: source and target.'
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)

    def test_atoms_at_most_4_chars(self):
        """$ pdb_renameatom -AT1,AT223 data/dummy.pdb"""

        sys.argv = ['', '-AT1,AT223', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        emsg = 'ERROR!! Atom names have maximum 4 characters: \'{}\''
        emsg = emsg.format('-AT1,AT223')
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)

    def test_atoms_at_most_4_chars_2(self):
        """$ pdb_renameatom -AT111,AT2 data/dummy.pdb"""

        sys.argv = ['', '-AT111,AT2', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        emsg = 'ERROR!! Atom names have maximum 4 characters: \'{}\''
        emsg = emsg.format('-AT111,AT2')
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)

    def test_file_not_provided(self):
        """$ pdb_renameatom -HB2,HB4"""

        sys.argv = ['', '-HB2,HB4']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        # proper error message
        emsg = 'ERROR!! No file provided.'
        self.assertEqual(self.stderr[0].split(os.linesep)[0], emsg)

    def test_file_not_provided(self):
        """$ pdb_renameatom -HB2,HB4 not_existing.pdb"""

        sys.argv = ['', '-HB2,HB4', 'not_existing.pdb']

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
