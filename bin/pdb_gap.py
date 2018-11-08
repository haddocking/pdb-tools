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
Detects gaps between consecutive residues in the sequence, both by a distance
criterion or discontinuous residue numbering. Only applies for protein residues.

Usage:
    python pdb_gap.py <pdb file>

Example:
    python pdb_gap.py 1CTF.pdb

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


def detect_gaps(fhandle):
    """Detects gaps between residues in the PDB file.
    """

    fmt_GAPd = "{0[1]}:{0[3]}{0[2]} < {2:7.2f}A > {1[1]}:{1[3]}{1[2]}\n"
    fmt_GAPs = "{0[1]}:{0[3]}{0[2]} < Seq. Gap > {1[1]}:{1[3]}{1[2]}\n"

    centroid = ' CA '  # respect spacing. 'CA  ' != ' CA '
    distance_threshold = 4.0 * 4.0

    def calculate_sq_atom_distance(i, j):
        """Squared euclidean distance between two 3d points"""
        return (i[0] - j[0]) * (i[0] - j[0]) + \
               (i[1] - j[1]) * (i[1] - j[1]) + \
               (i[2] - j[2]) * (i[2] - j[2])

    prev_at = (None, None, None, None, (None, None, None))
    model = 0
    n_gaps = 0
    for line in fhandle:

        if line.startswith('MODEL'):
            model = int(line[10:14])

        elif line.startswith('ATOM'):
            atom_name = line[12:16]
            if atom_name != centroid:
                continue

            resn = line[17:20]
            resi = int(line[22:26])
            chain = line[21]
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])

            at_uid = (model, chain, resi, resn, atom_name, (x, y, z))
            if prev_at[0] == at_uid[0] and prev_at[1] == at_uid[1]:
                d = calculate_sq_atom_distance(at_uid[5], prev_at[5])
                if d > distance_threshold:
                    sys.stdout.write(fmt_GAPd.format(prev_at, at_uid, d))
                    n_gaps += 1
                elif prev_at[2] + 1 != at_uid[2]:
                    sys.stdout.write(fmt_GAPs.format(prev_at, at_uid))
                    n_gaps += 1

            prev_at = at_uid

    sys.stdout.write('Found {} gap(s) in the structure\n'.format(n_gaps))


if __name__ == '__main__':
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    detect_gaps(pdbfh)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
