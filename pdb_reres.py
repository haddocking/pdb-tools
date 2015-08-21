#!/usr/bin/env python

"""
Renumbers residues in a PDB file starting from a given number.

usage: python pdb_reres.py -<resi> <pdb file>
example: python pdb_reres.py -1 1CTF.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

import os
import re
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        # No reres, from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
            reres = 1
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # Resi & Pipe _or_ file & no reres
        if re.match('\-[\-0-9]+', args[0]):
            reres = int(args[0][1:])
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
            reres = 1
    elif len(args) == 2:
        # Chain & File
        if not re.match('\-[\-0-9]+', args[0]):
            sys.stderr.write('Invalid residue number: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not os.path.isfile(args[1]):
            sys.stderr.write('File not found: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        reres = int(args[0][1:])
        pdbfh = open(args[1], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (reres, pdbfh)

def _renumber_pdb_residue(fhandle, sresid):
    """Enclosing logic in a function to speed up a bit"""

    resi = sresid - 1
    prev_resi = None
    for line in fhandle:
        line = line.strip()
        if line.startswith(('ATOM', 'HETATM', 'TER')):
            if line[22:26] != prev_resi:
                prev_resi = line[22:26]
                resi += 1

            yield line[:22] + str(resi).rjust(4) + line[26:] + '\n'
        else:
            yield line + '\n'

if __name__ == '__main__':

    # Check Input
    reres, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _renumber_pdb_residue(pdbfh, reres)

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
