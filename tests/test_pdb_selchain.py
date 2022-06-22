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
Unit Tests for `pdb_selchain`.
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
        name = 'pdbtools.pdb_selchain'
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
        """$ pdb_selchain -A data/dummy.pdb"""

        # Simulate input
        # pdb_selchain dummy.pdb
        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 76)  # selected c.A
        self.assertEqual(len(self.stderr), 0)  # no errors

    def test_one_option_CAPS_lowercase(self):
        """$ pdb_selchain -A data/dummy_az09.pdb"""

        # Simulate input
        # pdb_selchain dummy_az09.pdb
        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy_az09.pdb')]

        # Execute the script
        self.exec_module()
        
        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 76)  # selected c.A
        self.assertEqual(len(self.stderr), 0)  # no errors

    def test_one_option_lowercase(self):
        """$ pdb_selchain -b data/dummy_az09.pdb"""

        # Simulate input
        # pdb_selchain dummy.pdb
        sys.argv = ['', '-b', os.path.join(data_dir, 'dummy_az09.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 69)  # selected c.b
        self.assertEqual(len(self.stderr), 0)  # no errors

    def test_one_option_digit(self):
        """$ pdb_selchain -1 data/dummy_az09.pdb"""

        # Simulate input
        # pdb_selchain dummy.pdb
        sys.argv = ['', '-1', os.path.join(data_dir, 'dummy_az09.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 71)  # selected c.1
        self.assertEqual(len(self.stderr), 0)  # no errors
    
    def test_multiple(self):
        """
        $ pdb_selchain -A,B data/dummy.pdb
        """

        sys.argv = ['', '-A,B', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 129)  # c.A + c.B
        self.assertEqual(len(self.stderr), 0)

    def test_file_not_found(self):
        """$ pdb_selchain not_existing.pdb"""

        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    @unittest.skipIf(os.getenv('SKIP_TTY_TESTS'), 'skip on GHA - no TTY')
    def test_file_missing(self):
        """$ pdb_selchain -A"""

        sys.argv = ['', '-A']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0],
                         "ERROR!! No data to process!")

    @unittest.skipIf(os.getenv('SKIP_TTY_TESTS'), 'skip on GHA - no TTY')
    def test_helptext(self):
        """$ pdb_selchain"""

        sys.argv = ['']

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_selchain data/dummy.pdb"""

        sys.argv = ['', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:47],
                         "ERROR!! You must provide at least one chain ide")

    def test_invalid_option_2(self):
        """$ pdb_selchain -AB data/dummy.pdb"""

        sys.argv = ['', '-AB', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:40],
                         "ERROR!! Chain identifier name is invalid")

    def test_not_an_option(self):
        """$ pdb_selchain 20 data/dummy.pdb"""

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
