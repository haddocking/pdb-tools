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
Returns a new PDB file only with atoms in common to all input PDB files.

Atoms are judged equal is their name, altloc, res. name, res. num, insertion
code and chain fields are the same. Coordinates are taken from the first input
file.

Usage:
    python pdb_intersect.py <pdb file>

Example:
    python pdb_intersect.py 1CTF.pdb

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
    fl = []  # file list

    if len(args) >= 1:
        for fn in args:
            if not os.path.isfile(fn):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(fn))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(fn, 'r')
            fl.append(fh)

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fl


def intersect_pdb_files(flist):
    """Returns atoms common to all input files.
    """

    atom_data = {}  # atom_uid: line
    records = ('ATOM', 'HETATM', 'ANISOU', 'TER')

    ref = flist[0]
    for line in ref:

        if line.startswith(records):
            atom_uid = line[12:27]
            atom_data[atom_uid] = line

    ref.close()

    common_atoms = set(atom_data.keys())
    for fhandle in flist[1:]:
        file_atoms = set()

        for line in fhandle:
            atom_uid = line[12:27]
            file_atoms.add(atom_uid)

        fhandle.close()

        common_atoms = common_atoms & file_atoms

    for atom in atom_data:
        if atom in common_atoms:
            yield atom_data[atom]


if __name__ == '__main__':
    # Check Input
    pdbflist = check_input(sys.argv[1:])

    # Do the job
    new_pdb = intersect_pdb_files(pdbflist)

    try:
        sys.stdout.write(''.join(new_pdb))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    sys.exit(0)
