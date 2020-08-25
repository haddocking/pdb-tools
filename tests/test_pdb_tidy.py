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
Unit Tests for `pdb_tidy`.
"""

import io
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
        name = 'pdbtools.pdb_tidy'
        self.module = __import__(name, fromlist=[''])

    def exec_module(self, stdin=None):
        """
        Execs module.
        """

        if stdin is not None:
            sys.stdin = io.StringIO(stdin)

        with OutputCapture() as output:
            try:
                self.module.main()
            except SystemExit as e:
                self.retcode = e.code

        self.stdout = output.stdout
        self.stderr = output.stderr

        sys.stdin = sys.__stdin__  # restore

        return

    def test_default(self):
        """$ pdb_tidy data/dummy.pdb"""

        fpath = os.path.join(data_dir, 'dummy.pdb')
        sys.argv = ['', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        # CONECTs are ignored by issue #72, expected only 205 lines
        self.assertEqual(len(self.stdout), 205)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Check if we added TER statements correctly
        n_ter = len([r for r in self.stdout if r.startswith('TER')])
        self.assertEqual(n_ter, 5)

        # Check no CONECT in output
        c_conect = sum(1 for i in self.stdout if i.startswith('CONECT'))
        self.assertEqual(c_conect, 0)

        # Check if we added END statements correctly
        self.assertTrue(self.stdout[-1].startswith('END'))

    def test_default_stdin(self):
        """$ cat data/dummy.pdb | pdb_tidy"""

        fpath = os.path.join(data_dir, 'dummy.pdb')
        sys.argv = ['']

        # Execute the script with file as stdin
        with open(fpath) as fp:
            self.exec_module(fp.read())

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        # CONECTs are ignored by issue #72, expected only 205 lines
        self.assertEqual(len(self.stdout), 205)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Check if we added TER statements correctly
        n_ter = len([r for r in self.stdout if r.startswith('TER')])
        self.assertEqual(n_ter, 5)

        # Check no CONECT in output
        c_conect = sum(1 for i in self.stdout if i.startswith('CONECT'))
        self.assertEqual(c_conect, 0)

        # Check if we added END statements correctly
        self.assertTrue(self.stdout[-1].startswith('END'))

    def test_default_strict(self):
        """$ pdb_tidy -strict data/dummy.pdb"""

        fpath = os.path.join(data_dir, 'dummy.pdb')
        sys.argv = ['', '-strict', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        # CONECTs are ignored by issue #72, expected only 204 lines
        self.assertEqual(len(self.stdout), 204)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Check if we added TER statements correctly
        n_ter = len([r for r in self.stdout if r.startswith('TER')])
        self.assertEqual(n_ter, 4)

        # Check no CONECT in output
        c_conect = sum(1 for i in self.stdout if i.startswith('CONECT'))
        self.assertEqual(c_conect, 0)

        # Check if we added END statements correctly
        self.assertTrue(self.stdout[-1].startswith('END'))

    def test_default_strict_stdin(self):
        """$ cat data/dummy.pdb | pdb_tidy -strict"""

        fpath = os.path.join(data_dir, 'dummy.pdb')
        sys.argv = ['', '-strict']

        # Execute the script
        with open(fpath) as fp:
            self.exec_module(fp.read())

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        # CONECTs are ignored by issue #72, expected only 204 lines
        self.assertEqual(len(self.stdout), 204)
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Check if we added TER statements correctly
        n_ter = len([r for r in self.stdout if r.startswith('TER')])
        self.assertEqual(n_ter, 4)

        # Check no CONECT in output
        c_conect = sum(1 for i in self.stdout if i.startswith('CONECT'))
        self.assertEqual(c_conect, 0)

        # Check if we added END statements correctly
        self.assertTrue(self.stdout[-1].startswith('END'))

    def test_file_not_found(self):
        """$ pdb_tidy not_existing.pdb"""

        # Error (file not found)
        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")

    def test_helptext(self):
        """$ pdb_tidy"""

        sys.argv = ['']

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_tidy -A data/dummy.pdb"""

        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:36],
                         "ERROR! First argument is not a valid")


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
