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
Unit Tests for `pdb_element`.
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
        name = 'bin.pdb_element'
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
        """
        $ pdb_element data/dummy.pdb
        """

        # Simulate input
        sys.argv = ['', os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 204)  # no lines deleted
        self.assertEqual(len(self.stderr), 0)  # no errors

        element_cols = [l[76:78] for l in self.stdout]

        # Test content
        assigned = [l for l in element_cols if l.strip()]
        self.assertEqual(len(assigned), 185)  # ignore TER/END & headers

        # Test order
        element_list = ['  ', '  ', '  ', '  ', '  ', '  ', '', '', '', '', '',
                        '', '', ' N', ' H', ' H', ' H', ' C', ' H', ' C', ' H',
                        ' H', ' C', ' H', ' H', ' C', ' H', ' H', ' N', ' H',
                        ' C', ' N', ' H', ' H', ' N', ' H', ' H', ' C', ' O',
                        ' N', ' H', ' C', ' H', ' C', ' H', ' H', ' C', ' H',
                        ' H', ' C', ' O', ' O', ' C', ' O', ' N', ' H', ' C',
                        ' H', ' C', ' H', ' H', ' H', ' C', ' O', '', ' N',
                        ' H', ' H', ' H', ' C', ' C', ' H', ' C', ' H', ' H',
                        ' C', ' O', ' N', ' H', ' H', ' C', ' O', ' N', ' H',
                        ' C', ' H', ' C', ' H', ' H', ' C', ' H', ' H', ' C',
                        ' H', ' H', ' N', ' H', ' C', ' N', ' H', ' H', ' N',
                        ' H', ' H', ' C', ' O', ' N', ' H', ' C', ' H', ' C',
                        ' H', ' H', ' C', ' H', ' H', ' C', ' O', ' O', ' C',
                        ' O', '  ', ' N', ' H', ' H', ' H', ' C', ' H', ' C',
                        ' H', ' H', ' C', ' H', ' H', ' C', ' H', ' H', ' N',
                        ' H', ' C', ' N', ' H', ' H', ' N', ' H', ' H', ' C',
                        ' O', ' N', ' H', ' C', ' H', ' C', ' H', ' H', ' C',
                        ' H', ' H', ' C', ' O', ' O', ' C', ' O', ' N', ' C',
                        ' C', ' O', ' C', ' C', ' S', ' C', '  ', ' P', ' O',
                        ' O', ' O', ' C', ' C', ' O', ' C', ' O', ' C', ' C',
                        ' N', ' C', ' O', ' N', ' C', ' O', ' C', ' C', ' C',
                        'CA', ' O', ' O', ' O', ' O', ' O', ' O', ' O', ' O',
                        '  ', '', '']

        self.assertEqual(element_cols, element_list)

    def test_file_not_found(self):
        """
        $ pdb_element not_existing.pdb
        """

        # Error (file not found)
        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    def test_helptext(self):
        """
        $ pdb_element
        """

        sys.argv = ['']

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """
        $ pdb_element -A data/dummy.pdb
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
