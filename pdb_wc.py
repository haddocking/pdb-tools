#!/usr/bin/env python

"""
Summarizes the contents of a PDB file.

usage: python pdb_wc.py -[acrmHgdiA] <pdb file>
example: python pdb_wc.py 1CTF.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

from __future__ import print_function, division

import math
import os
import re
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        # No option, from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
            option = 'A'
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # option & Pipe _or_ file
        if re.match('\-[acrmHgdiA]', args[0]):
            option = args[0][1]
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
            option = 'A'
    elif len(args) == 2:
        # option & File
        if not re.match('\-[acrmHgdiA]', args[0]):
            sys.stderr.write('Invalid option: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not os.path.isfile(args[1]):
            sys.stderr.write('File not found: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        option = args[0][1]
        pdbfh = open(args[1], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (option, pdbfh)

def _summarize(fhandle, option):
    """Enclosing logic in a function"""

    option = option

    n_models = 0
    has_hetero, has_gaps, has_double, has_insert = "No", "No", "No", "No"
    at_list, res_list, chain_list = [], [], []
    prev_resuid, prev_chainid = None, None

    gap_check = True
    for line in fhandle:
        line = line.strip()

        record = line[0:6]

        if record == 'HETATM':
            has_hetero = "Yes"

        if record.startswith('ENDMDL'):
            gap_check = False

        if record.startswith('MODEL'):
            n_models += 1

        if record == 'ATOM  ':
            if not n_models:
                n_models += 1

            res_uid = (line[17:20], line[21], int(line[22:26]))
            at_uid = (line[12:16], line[16], line[17:20], line[21], line[22:26])
            chain_uid = line[21]

            if res_uid != prev_resuid:
                if prev_chainid == line[21] and prev_resuid and res_uid[2] - 1 != prev_resuid[2]:
                    if gap_check:
                        has_gaps = "Yes"
                    else:
                        gap_check = True

                prev_resuid = res_uid
                res_list.append(res_uid)

            if line[21] != prev_chainid:
                prev_chainid = line[21]
                chain_list.append(chain_uid)

            altloc = line[16]
            if altloc != ' ':
                has_double = "Yes"

            resinsert = line[26]
            if resinsert != ' ':
                has_insert = "Yes"

            at_list.append(at_uid)

    n_atoms, n_u_atoms = len(at_list), len(set(at_list))
    n_residues, n_u_residues = len(res_list), len(set(res_list))
    n_chains, n_u_chains = len(chain_list), len(set(chain_list))

    if option == 'a':
        print(n_atoms, n_u_atoms)
    elif option == 'r':
        print(n_residues, n_u_residues)
    elif option == 'c':
        print(n_chains, n_u_chains)
    elif option == 'm':
        print(n_models)
    elif option == 'H':
        print(has_hetero)
    elif option == 'g':
        print(has_gaps)
    elif option == 'd':
        print(has_double)
    elif option == 'i':
        print(has_insert)
    elif option == 'A':
        print('No. atoms:\t{0}\t({1:4.1f} per model)'.format(n_atoms, n_u_atoms))
        print('No. residues:\t{0}\t({1:4.1f} per model)'.format(n_residues, n_u_residues))
        print('No. chains:\t{0}\t({1:4.1f} per model)'.format(n_chains, n_u_chains))
        print('No. models:\t{0}'.format(n_models))
        print('Hetero Atoms:\t{0}'.format(has_hetero))
        print('Has seq. gaps:\t{0}'.format(has_gaps))
        print('Double Occ.:\t{0}'.format(has_double))
        print('Insertions:\t{0}'.format(has_insert))

if __name__ == '__main__':

    # Check Input
    option, pdbfh = check_input(sys.argv[1:])

    # Do the job
    _summarize(pdbfh, option)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
