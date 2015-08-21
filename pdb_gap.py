#!/usr/bin/env python

"""
Detects gaps in (protein) PDB files (sequence/distance).

usage: python pdb_gap.py <pdb file>
example: python pdb_gap.py 1CTF.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

from __future__ import print_function

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        # Read from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # File
        if not os.path.isfile(args[0]):
            sys.stderr.write('File not found: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        pdbfh = open(args[0], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return pdbfh

def _check_structure_gaps(fhandle):
    """Enclosing logic in a function"""

    _centroid = ' CA ' # respect spacing. 'CA  ' != ' CA '
    _distance_threshold = 4.0

    def _calc_distance(i, j):
        return ( (j[0]-i[0])**2 + (j[1]-i[1])**2 + (j[2]-i[2])**2 )**0.5

    prev_at = (None, None, None, None, (None, None, None))
    model = 0
    for line in fhandle:
        line = line.strip()
        if line.startswith('MODEL'):
            model = int(line[10:14])

        elif line.startswith(('ATOM', 'HETATM')):
            aname = line[12:16]
            if aname != _centroid:
                continue

            resn = line[17:20]
            resi = int(line[22:26])
            chain = line[21]
            x, y, z = float(line[30:38]), \
                      float(line[38:46]), \
                      float(line[46:54])

            at_uid = (model, chain, resi, resn, aname, (x,y,z))
            if prev_at[0] == at_uid[0] and prev_at[1] == at_uid[1]:
                d = _calc_distance(at_uid[5], prev_at[5])
                if d > _distance_threshold:
                    print("{0[1]}:{0[3]}{0[2]} < {2:7.2f}A > {1[1]}:{1[3]}{1[2]}".format(prev_at, at_uid, d))
                elif prev_at[2] + 1 != at_uid[2]:
                    print("{0[1]}:{0[3]}{0[2]} < Seq. Gap > {1[1]}:{1[3]}{1[2]}".format(prev_at, at_uid, d))

            prev_at = at_uid

if __name__ == '__main__':

    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    _check_structure_gaps(pdbfh)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
