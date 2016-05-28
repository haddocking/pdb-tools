#!/usr/bin/env python

"""
Calculates distances between all atoms in a structure.
Filters the distances if a cutoff value is given (default 5.0A).
If the cutoff is preceeded by a '+' sign, only inter-chain distances are calculated.

usage: python pdb_dist.py [[-+]cutoff] <pdb file>
example: python pdb_dist.py -5.0 1CTF.pdb
         python pdb_dist.py +5.0 1BRS.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

from __future__ import print_function

import os
import re
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

CUTOFF_DEFAULT = 5.0
# Atom name, residue number, chain ID, same, same, same, d_ij
_OUTPUT_FORMAT = "{0[0]:<4s} {0[1]:>3s} {0[2]:>4s} {0[3]:1s} : {1[0]:<4s} {1[1]:>4s} {1[2]:>4s} {1[3]:1s} | {2:5.2f}"

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        # From pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
            cutoff = CUTOFF_DEFAULT
            inter = False
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # Options & Pipe _or_ file & no option
        if re.match(r'[\-\+][0-9\.]+', args[0]):
            inter = args[0][0] == '+'
            cutoff = float(args[0][1:])
            if not sys.stdin.isatty():
                pdbfh = sys.stdin
            else:
                sys.stderr.write(USAGE)
                sys.exit(1)
        else:
            if not os.path.isfile(args[0]):
                sys.stderr.write('File not found: ' + args[0] + '\n')
                sys.stderr.write(USAGE)
                sys.exit(1)
            pdbfh = open(args[0], 'r')
            cutoff = CUTOFF_DEFAULT
            inter = False

    elif len(args) == 2:
        # Option & File
        if not re.match(r'[\-\+][0-9\.]+', args[0]):
            sys.stderr.write('Invalid option: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)

        if not os.path.isfile(args[1]):
            sys.stderr.write('File not found: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        cutoff = float(args[0][1:])
        pdbfh = open(args[1], 'r')
        inter = args[0][0] == '+'
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (inter, cutoff, pdbfh)

def _calculate_atom_distance(i, j):
    """Euclidean distance between two 3d points"""
    return ((i[0] - j[0])**2 + (i[1] - j[1])**2 + (i[2] - j[2])**2) ** 0.5

def calculate_distances(fhandle, cutoff, inter):
    """Enclosing logic in a function to speed up a bit"""

    coord_re = re.compile('^(ATOM|HETATM)')
    fhandle = fhandle
    cutoff = cutoff
    inter = inter

    atoms = []
    for line in fhandle:
        line = line.strip()
        if coord_re.match(line):
            # atom name, altloc, res number, chain name
            atom_uid = (line[12:16].strip(), line[17:20].strip(), line[22:26].strip(), line[21])
            x, y, z = line[30:38], line[38:46], line[46:54]
            x, y, z = float(x), float(y), float(z)

            atoms.append((atom_uid, (x, y, z)))

    for i, atom_i in enumerate(atoms):
        for atom_j in atoms[i+1:]:
            # Avoid intra-residue calculations & intra chain if requested
            if not ((atom_i[0][1:] == atom_j[0][1:]) or (inter and atom_i[0][3] == atom_j[0][3])):
                d_ij = _calculate_atom_distance(atom_i[1], atom_j[1])
                if d_ij <= cutoff:
                    print(_OUTPUT_FORMAT.format(atom_i[0], atom_j[0], d_ij))


if __name__ == '__main__':
    # Check Input
    inter, cutoff, pdbfh = check_input(sys.argv[1:])

    # Do the job
    calculate_distances(pdbfh, cutoff, inter)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


