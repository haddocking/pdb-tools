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
Unit Tests for `pdb_fromcif`.
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
        name = "pdbtools.pdb_fromcif"
        self.module = __import__(name, fromlist=[""])

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

    def test_conversion(self):
        """$ pdb_fromcif data/ensemble_OK.cif"""

        fpath = os.path.join(data_dir, "ensemble_OK.cif")
        sys.argv = ["", fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 9)
        self.assertEqual(len(self.stderr), 0)

        # Check order of records
        expected = [
            "MODEL ",
            "ATOM  ",
            "ATOM  ",
            "ENDMDL",
            "MODEL ",
            "ATOM  ",
            "ATOM  ",
            "ENDMDL",
            "END   ",
        ]
        records = [l[:6] for l in self.stdout]
        self.assertEqual(records, expected)

    def test_file_not_found(self):
        """$ pdb_fromcif not_existing.pdb"""

        # Error (file not found)
        afile = os.path.join(data_dir, "not_existing.pdb")
        sys.argv = ["", afile]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:22], "ERROR!! File not found")

    @unittest.skipIf(os.getenv("SKIP_TTY_TESTS"), "skip on GHA - no TTY")
    def test_helptext(self):
        """$ pdb_fromcif"""

        sys.argv = [""]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_fromcif -A data/dummy.cif"""

        sys.argv = ["", "-A", os.path.join(data_dir, "dummy.cif")]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:43], "ERROR! First argument is not a valid option")

    def test_valid_option(self):
        """$ pdb_fromcif -h36 data/dummy-h36.cif"""

        sys.argv = ["", "-h36", os.path.join(data_dir, "dummy-h36.cif")]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 28)
        self.assertEqual(len(self.stderr), 0)

    def test_h36_encoding(self):
        """Tests that atom serials > 99999 are encoded in hybrid-36 format"""

        def _cif_lines(n_atoms):
            yield "loop_\n"
            for field in [
                "group_PDB", "id", "type_symbol", "label_atom_id",
                "label_alt_id", "label_comp_id", "label_asym_id",
                "label_entity_id", "label_seq_id", "pdbx_PDB_ins_code",
                "Cartn_x", "Cartn_y", "Cartn_z", "occupancy",
                "B_iso_or_equiv", "pdbx_formal_charge", "auth_asym_id",
                "pdbx_PDB_model_num",
            ]:
                yield "_atom_site.{}\n".format(field)
            for i in range(1, n_atoms + 1):
                yield (
                    "ATOM {} N N . ALA A . 1 ? "
                    "0.000 0.000 0.000 1.00 15.00 0 A 1\n"
                ).format(i)

        result = list(self.module.run(_cif_lines(100001), h36=True))

        # 100001 ATOM lines + END
        self.assertEqual(len(result), 100002)
        # last decimal serial
        self.assertEqual(result[99998][6:11], "99999")
        # serial 100000 encodes as "A0000" in hybrid-36
        self.assertEqual(result[99999][6:11], "A0000")
        # serial 100001 encodes as "A0001" in hybrid-36
        self.assertEqual(result[100000][6:11], "A0001")

    def test_missing_charge(self):
        """$ pdb_fromcif data/af3_output.cif"""
        fpath = os.path.join(data_dir, "af3_output.cif")
        sys.argv = ["", fpath]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 3928)
        self.assertEqual(len(self.stderr), 0)


if __name__ == "__main__":
    from config import test_dir

    mpath = os.path.abspath(os.path.join(test_dir, ".."))
    sys.path.insert(0, mpath)  # so we load dev files before  any installation

    unittest.main()
