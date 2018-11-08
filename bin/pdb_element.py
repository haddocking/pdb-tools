#!/usr/bin/env python
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
Assigns the element column to the PDB file, guessing the element from the atom
names.

Usage:
    python pdb_element.py <pdb file>

Example:
    python pdb_element.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        if not os.path.isfile(args[0]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[0], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def assign_element(fhandle):
    """Assigns each atom's element based on the atom name field.

    Rules specified in the format specification:
        - Alignment of one-letter atom name such as C starts at column 14,
          while two-letter atom name such as FE starts at column 13.
        - Atom nomenclature begins with atom type.
    """

    elements = set(('H', 'D', 'HE', 'LI', 'BE', 'B', 'C', 'N', 'O', 'F', 'NE',
                    'NA', 'MG', 'AL', 'SI', 'P', 'S', 'CL', 'AR', 'K', 'CA',
                    'SC', 'TI', 'V', 'CR', 'MN', 'FE', 'CO', 'NI', 'CU', 'ZN',
                    'GA', 'GE', 'AS', 'SE', 'BR', 'KR', 'RB', 'SR', 'Y', 'ZR',
                    'NB', 'MO', 'TC', 'RU', 'RH', 'PD', 'AG', 'CD', 'IN', 'SN',
                    'SB', 'TE', 'I', 'XE', 'CS', 'BA', 'LA', 'CE', 'PR', 'ND',
                    'PM', 'SM', 'EU', 'GD', 'TB', 'DY', 'HO', 'ER', 'TM', 'YB',
                    'LU', 'HF', 'TA', 'W', 'RE', 'OS', 'IR', 'PT', 'AU', 'HG',
                    'TL', 'PB', 'BI', 'PO', 'AT', 'RN', 'FR', 'RA', 'AC', 'TH',
                    'PA', 'U', 'NP', 'PU', 'AM', 'CM', 'BK', 'CF', 'ES', 'FM',
                    'MD', 'NO', 'LR', 'RF', 'DB', 'SG', 'BH', 'HS', 'MT'))

    records = ('ATOM', 'HETATM', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            atom_name = line[12:16]

            if atom_name[0].isalpha() and not atom_name[2:].isdigit():
                element = atom_name.strip()
            else:
                atom_name = atom_name.strip()
                if atom_name[0].isdigit():
                    element = atom_name[1]
                else:
                    element = atom_name[0]

            if element not in elements:
                element = '  '  # empty element in case we cannot assign

            line = line[:76] + element.rjust(2) + line[78:]

        yield line


if __name__ == '__main__':
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = assign_element(pdbfh)

    try:
        sys.stdout.write(''.join(new_pdb))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
