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
Unit Tests for `pdb_tocif`.
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
        name = 'bin.pdb_tocif'
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

    def test_single_model(self):
        """
        $ pdb_tocif data/dummy.pdb
        """

        fpath = os.path.join(data_dir, 'dummy.pdb')
        sys.argv = ['', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 211)
        self.assertEqual(len(self.stderr), 0)

        # Check no of records
        n_ATOM = len([l for l in self.stdout if l.startswith('ATOM')])
        n_HETATM = len([l for l in self.stdout if l.startswith('HETATM')])
        n_coord = n_ATOM + n_HETATM
        self.assertEqual(n_ATOM, 176)
        self.assertEqual(n_HETATM, 9)
        self.assertEqual(n_coord, 185)

    def test_valid(self):
        """
        $ pdb_tocif data/ensemble_OK.pdb
        """

        fpath = os.path.join(data_dir, 'ensemble_OK.pdb')
        sys.argv = ['', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 30)
        self.assertEqual(len(self.stderr), 0)

        # Check no of records
        n_ATOM = len([l for l in self.stdout if l.startswith('ATOM')])
        n_HETATM = len([l for l in self.stdout if l.startswith('HETATM')])
        n_coord = n_ATOM + n_HETATM
        self.assertEqual(n_ATOM, 4)
        self.assertEqual(n_HETATM, 0)
        self.assertEqual(n_coord, 4)

        # Check model numbers
        records = (('ATOM', 'HETATM'))
        models = [l.split()[-1] for l in self.stdout if l.startswith(records)]
        self.assertEqual(models, ['1', '1', '2', '2'])

        # Check number of fields
        atom_lines = [l for l in self.stdout if l.startswith(records)]
        n_fields = list(set(map(lambda x: len(x.split()), atom_lines)))
        self.assertEqual(n_fields, [20])

    def test_file_not_found(self):
        """
        $ pdb_tocif not_existing.pdb
        """

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
        """
        $ pdb_tocif
        """

        sys.argv = ['']

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """
        $ pdb_tocif -A data/dummy.pdb
        """

        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:36],
                         "ERROR!! Script takes 1 argument, not")


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
