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
Unit Tests for `pdb_splitchain`.
"""

import os
import shutil
import sys
import tempfile
import unittest

from config import data_dir
from utils import OutputCapture


class TestTool(unittest.TestCase):
    """
    Generic class for testing tools.
    """

    def setUp(self):
        # Dynamically import the module
        name = 'pdbtools.pdb_splitchain'
        self.module = __import__(name, fromlist=[''])
        self.tempdir = tempfile.mkdtemp()  # set temp dir
        os.chdir(self.tempdir)

    def tearDown(self):
        os.chdir(os.path.dirname(os.path.abspath('.')))  # cd ../
        shutil.rmtree(self.tempdir)

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
        """$ pdb_splitchain data/dummy.pdb"""

        # Copy input file to tempdir

        # Simulate input
        src = os.path.join(data_dir, 'dummy.pdb')
        dst = os.path.join(self.tempdir, 'dummy.pdb')
        shutil.copy(src, dst)
        sys.argv = ['', dst]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Read files created by script and then delete
        ofiles = [f for f in os.listdir(self.tempdir) if f.startswith('dummy')]
        self.assertEqual(len(ofiles), 4 + 1)  # ori + 4 chains

        # Make sure each file has the chain it should have
        records = (('ATOM', 'HETATM', 'TER', 'ANISOU'))
        for fpath in ofiles:
            if fpath == 'dummy.pdb':
                continue

            with open(os.path.join(self.tempdir, fpath), 'r') as handle:
                fname_chain = fpath.split('_')[1][:-4]  # xxx_(X).pdb
                pdb_chains = [l[21] for l in handle if l.startswith(records)]

                self.assertEqual(fname_chain, list(set(pdb_chains))[0])

    def test_run_fhandler(self):
        """pdb_splitchain.run(fhandler)"""
        from pdbtools import pdb_splitchain

        src = os.path.join(data_dir, 'dummy.pdb')
        dst = os.path.join(self.tempdir, 'dummy.pdb')
        shutil.copy(src, dst)

        with open(dst, 'r') as fin:
            pdb_splitchain.run(fin)

        # Read files created by script and then delete
        ofiles = [f for f in os.listdir(self.tempdir) if f.startswith('dummy')]
        self.assertEqual(len(ofiles), 4 + 1)  # ori + 4 chains

        # Make sure each file has the chain it should have
        records = (('ATOM', 'HETATM', 'TER', 'ANISOU'))
        for fpath in ofiles:
            if fpath == 'dummy.pdb':
                continue

            with open(os.path.join(self.tempdir, fpath), 'r') as handle:
                fname_chain = fpath.split('_')[1][:-4]  # xxx_(X).pdb
                pdb_chains = [l[21] for l in handle if l.startswith(records)]

                self.assertEqual(fname_chain, list(set(pdb_chains))[0])

    def test_run_iterable(self):
        """pdb_splitchain.run(iterable)"""
        from pdbtools import pdb_splitchain

        src = os.path.join(data_dir, 'dummy.pdb')
        dst = os.path.join(self.tempdir, 'dummy.pdb')
        shutil.copy(src, dst)

        with open(dst, 'r') as fin:
            lines = fin.readlines()

        pdb_splitchain.run(lines)

        # Read files created by script and then delete
        ofiles = [
            f
            for f in os.listdir(self.tempdir)
            if f.startswith('splitchains')
            ]
        self.assertEqual(len(ofiles), 4)  # 4 chains

        # Make sure each file has the chain it should have
        records = (('ATOM', 'HETATM', 'TER', 'ANISOU'))
        for fpath in ofiles:

            with open(os.path.join(self.tempdir, fpath), 'r') as handle:
                fname_chain = fpath.split('_')[1][:-4]  # xxx_(X).pdb
                pdb_chains = [l[21] for l in handle if l.startswith(records)]

                self.assertEqual(fname_chain, list(set(pdb_chains))[0])

    def test_run_iterable_with_name(self):
        """pdb_splitchain.run(iterable)"""
        from pdbtools import pdb_splitchain

        src = os.path.join(data_dir, 'dummy.pdb')
        dst = os.path.join(self.tempdir, 'dummy.pdb')
        shutil.copy(src, dst)

        with open(dst, 'r') as fin:
            lines = fin.readlines()

        pdb_splitchain.run(lines, outname='newname')

        # Read files created by script and then delete
        ofiles = [f for f in os.listdir(self.tempdir) if f.startswith('newname')]
        self.assertEqual(len(ofiles), 4)  # 4 chains

        # Make sure each file has the chain it should have
        records = (('ATOM', 'HETATM', 'TER', 'ANISOU'))
        for fpath in ofiles:

            with open(os.path.join(self.tempdir, fpath), 'r') as handle:
                fname_chain = fpath.split('_')[1][:-4]  # xxx_(X).pdb
                pdb_chains = [l[21] for l in handle if l.startswith(records)]

                self.assertEqual(fname_chain, list(set(pdb_chains))[0])

    def test_file_not_found(self):
        """$ pdb_splitchain not_existing.pdb"""

        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    def test_file_missing(self):
        """$ pdb_splitchain -10"""

        sys.argv = ['', '-10']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0][:38],
                         "ERROR!! File not found or not readable")

    @unittest.skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_helptext(self):
        """$ pdb_splitchain"""

        sys.argv = ['']

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_splitchain -A data/dummy.pdb"""

        sys.argv = ['', '-A', os.path.join(data_dir, 'dummy.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! Script takes 1")  # proper error message


if __name__ == '__main__':
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, '..'))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
