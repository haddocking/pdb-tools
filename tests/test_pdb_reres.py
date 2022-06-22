#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 1118 João Pedro Rodrigues
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
Unit Tests for `pdb_reres`.
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
        name = 'pdbtools.pdb_reres'
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
        """$ pdb_reres data/dummy.pdb"""

        # Simulate input
        # pdb_reres dummy.pdb
        sys.argv = ['', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # no lines deleted
        self.assertEqual(len(self.stderr), 0)  # no errors

        records = (('ATOM', 'HETATM'))
        resid_list = [int(l[22:26]) for l in self.stdout
                      if l.startswith(records)]

        expected = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                    2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4,
                    4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                    5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6,
                    6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
                    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8,
                    8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10,
                    10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
                    10, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

        self.assertEqual(resid_list, expected)

    def test_two_options_pos(self):
        """$ pdb_reres -10 data/dummy.pdb"""

        # Simulate input
        # pdb_reres dummy.pdb
        sys.argv = ['', '-10', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # no lines deleted
        self.assertEqual(len(self.stderr), 0)  # no errors

        records = (('ATOM', 'HETATM'))
        resid_list = [int(l[22:26]) for l in self.stdout
                      if l.startswith(records)]

        expected = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
                    10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11,
                    11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12,
                    12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13,
                    13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14,
                    14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14,
                    14, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
                    15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16,
                    16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17,
                    17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 18, 18,
                    18, 18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 19, 19, 19, 19,
                    19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 20, 21, 22, 23,
                    24, 25, 26, 27, 28]

        self.assertEqual(resid_list, expected)

    def test_two_options_neg(self):
        """$ pdb_reres --10 data/dummy.pdb"""

        sys.argv = ['', '--10', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 204)
        self.assertEqual(len(self.stderr), 0)

        records = (('ATOM', 'HETATM'))
        resid_list = [int(l[22:26]) for l in self.stdout
                      if l.startswith(records)]

        expected = [-10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10,
                    -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10,
                    -10, -10, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9,
                    -9, -9, -9, -8, -8, -8, -8, -8, -8, -8, -8, -8, -8, -7, -7,
                    -7, -7, -7, -7, -7, -7, -7, -7, -7, -7, -7, -7, -7, -7, -7,
                    -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6,
                    -6, -6, -6, -6, -6, -6, -6, -6, -6, -5, -5, -5, -5, -5, -5,
                    -5, -5, -5, -5, -5, -5, -5, -5, -5, -4, -4, -4, -4, -4, -4,
                    -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4,
                    -4, -4, -4, -4, -4, -3, -3, -3, -3, -3, -3, -3, -3, -3, -3,
                    -3, -3, -3, -3, -3, -2, -2, -2, -2, -2, -2, -2, -2, -1, -1,
                    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                    -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]

        self.assertEqual(resid_list, expected)

    def test_three_with_single_res_models(self):
        """$ pdb_reres -4 data/ensemble.OK.pdb"""
        sys.argv = ['', '-4', os.path.join(data_dir, 'ensemble_OK.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 11)
        self.assertEqual(len(self.stderr), 0)

        records = ('ATOM', 'HETATM')
        resid_list = [int(l[22:26]) for l in self.stdout
                      if l.startswith(records)]

        expected = [4, 4, 4, 4]
        self.assertEqual(resid_list, expected)

        models = ('MODEL',)
        models_int = [int(l[5:]) for l in self.stdout if l.startswith(models)]
        models_expected = [1, 2]
        self.assertEqual(models_int, models_expected)

    def test_three_with_models(self):
        """$ pdb_reres -4 data/ensemble.OK.pdb"""
        sys.argv = ['', '-4', os.path.join(data_dir, 'ensemble_more_OK.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 13)
        self.assertEqual(len(self.stderr), 0)

        records = ('ATOM', 'HETATM')
        resid_list = [int(l[22:26]) for l in self.stdout
                      if l.startswith(records)]

        expected = [4, 4, 5, 5, 4, 4]
        self.assertEqual(resid_list, expected)

        models = ('MODEL',)
        models_int = [int(l[5:]) for l in self.stdout if l.startswith(models)]
        models_expected = [1, 2]
        self.assertEqual(models_int, models_expected)

    def test_too_many_residues(self):
        """$ pdb_reres -9998 data/dummy.pdb"""

        sys.argv = ['', '-9998', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(len(self.stderr), 1)

        self.assertEqual(self.stderr[0][:22],
                         "Cannot set residue num")  # proper error message

    def test_file_not_found(self):
        """$ pdb_reres -10 not_existing.pdb"""

        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', '-10', afile]

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    @unittest.skipIf(sys.platform.startswith('win'), 'skip on Windows - requires TTY')
    def test_file_missing(self):
        """$ pdb_reres -10"""

        sys.argv = ['', '-10']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! No data to process!")

    @unittest.skipIf(sys.platform.startswith('win'), 'skip on Windows - requires TTY')
    def test_helptext(self):
        """$ pdb_reres"""

        sys.argv = ['']

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_reres -A data/dummy.pdb"""

        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:47],
                         "ERROR!! You provided an invalid residue number:")

    def test_not_an_option(self):
        """$ pdb_reres 11 data/dummy.pdb"""

        sys.argv = ['', '11', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0],
                         "ERROR! First argument is not an option: '11'")


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
