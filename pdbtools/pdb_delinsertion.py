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
Deletes insertion codes in a PDB file.

Deleting an insertion code shifts the residue numbering of downstream
residues. Allows for picking specific residues to delete insertion codes for.

Usage:
    python pdb_delinsertion.py [-<option>] <pdb file>

Example:
    python pdb_delinsertion.py 1CTF.pdb  # delete ALL insertion codes
    python pdb_delinsertion.py -A9,B12 1CTF.pdb  # deletes ins. codes for res
                                                 # 9 of chain A and 12 of chain B.

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import sys
import warnings

from pdbtools import pdb_fixinsert

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


# Monkeypatch warnings output
def simpleformat(msg, *args, **kwargs):
    return str(msg) + '\n'  # just the message


warnings.formatwarning = simpleformat


def main():

    # Add deprecation warning
    # We could use warnings.warn but I don't like the output
    # that much. This makes it stand out more.
    warnings.warn(
        "\n\n** WARNING **\n"
        "  This tool will be deprecated in a future release.\n"
        "  Please use pdb_fixinsertion.py instead.\n\n"
    )

    try:
        pdb_fixinsert.main()
    except SystemExit as e:
        sys.exit(e.code)


if __name__ == '__main__':
    main()
