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
Unit Tests for `pdb_chkensemble`.
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
        """
        Sets the module.

        Args:
            self: (todo): write your description
        """
        # Dynamically import the module
        name = 'pdbtools.pdb_chkensemble'
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

    def test_valid_ensemble(self):
        """$ pdb_chkensemble data/ensemble_OK.pdb"""

        fpath = os.path.join(data_dir, 'ensemble_OK.pdb')
        sys.argv = ['', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 1)
        self.assertEqual(len(self.stderr), 0)  # no errors

        self.assertEqual(self.stdout[0],
                         "Ensemble of 2 models *seems* OK")

    def test_ensemble_diffatom(self):
        """$ pdb_chkensemble data/ensemble_error_1.pdb"""

        fpath = os.path.join(data_dir, 'ensemble_error_1.pdb')
        sys.argv = ['', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(len(self.stderr), 3)

        self.assertEqual(self.stderr,
                         ["Models 1 and 2 differ:",
                          "Atoms in model 1 only:",
                          "    2  H   ASN A   1 "])

    def test_ensemble_nomodel(self):
        """$ pdb_chkensemble data/ensemble_error_2.pdb"""

        fpath = os.path.join(data_dir, 'ensemble_error_2.pdb')
        sys.argv = ['', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(len(self.stderr), 1)

        self.assertEqual(self.stderr[0],
                         "ERROR!! MODEL record missing before ATOM at line '3'")

    def test_ensemble_noendmdl(self):
        """$ pdb_chkensemble data/ensemble_error_3.pdb"""

        fpath = os.path.join(data_dir, 'ensemble_error_3.pdb')
        sys.argv = ['', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(len(self.stderr), 1)

        self.assertEqual(self.stderr[0],
                         "ERROR!! ENDMDL record missing at line '10'")

    def test_ensemble_noendmdl2(self):
        """$ pdb_chkensemble data/ensemble_error_4.pdb"""

        fpath = os.path.join(data_dir, 'ensemble_error_4.pdb')
        sys.argv = ['', fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(len(self.stderr), 1)

        self.assertEqual(self.stderr[0],
                         "ERROR!! MODEL record found before ENDMDL at line '6'")

    def test_file_not_found(self):
        """$ pdb_chkensemble not_existing.pdb"""

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
        """$ pdb_chkensemble"""

        sys.argv = ['']

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_chkensemble -A data/dummy.pdb"""

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
