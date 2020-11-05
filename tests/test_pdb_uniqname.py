#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 João Pedro Rodrigues
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
Unit Tests for `pdb_uniqname`.
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
        name = 'pdbtools.pdb_uniqname'
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
        """$ pdb_uniqname data/hetatm.pdb"""

        # Simulate input
        sys.argv = ['', os.path.join(data_dir, 'hetatm.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 19)  # no lines deleted
        self.assertEqual(len(self.stderr), 0)  # no errors

        records = ('ATOM', 'HETATM')
        atnames = [l[12:16] for l in self.stdout if l.startswith(records)]

        self.assertEqual(
            atnames,
            [
                ' C1 ', ' C2 ', ' H1 ', ' C3 ',
                'CA1 ', 'CA2 ', ' H1 ', ' H2 ',
                ' C1 ', ' C2 ', ' H  ', ' H  '
            ]
        )

    def test_error(self):
        """$ pdb_uniqname data/hetatm_bad.pdb"""

        # Simulate input
        sys.argv = ['', os.path.join(data_dir, 'hetatm_bad.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 1)  # ensure the program threw an error
        self.assertEqual(len(self.stdout), 0)  # no output

        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! No element fou")  # proper error message

    def test_file_not_found(self):
        """$ pdb_uniqname not_existing.pdb"""

        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    def test_file_missing(self):
        """$ pdb_uniqname"""

        sys.argv = ['']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[1],
                         self.module.__doc__.split("\n")[1])

    def test_helptext(self):
        """$ pdb_uniqname"""

        sys.argv = ['']

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[1],
                         self.module.__doc__.split("\n")[1])

    def test_invalid_option(self):
        """$ pdb_uniqname -A data/dummy.pdb"""

        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[1],
                         self.module.__doc__.split("\n")[1])


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
