#!/usr/bin/env python

"""
Deletes side-chain atoms of specific residue selections.

usage: python pdb_schave.py <i>[,:<j>] <pdb file>
examples:
    python pdb_rslice.py 1:10 1CTF.pdb # Shaves residues 1 to 10
    python pdb_rslice.py 1: 1CTF.pdb # Shaves residues 1 to END
    python pdb_rslice.py 1:10,20:25 1CTF.pdb # Shaves residues 1-10 and 20-25

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
    """
    Checks whether to read from stdin/file
    and validates user input/options.
    """

    if not len(args):
        sys.stderr.write(USAGE)
        sys.exit(1)
    elif len(args) == 1:
        # Resi & Pipe _or_ file & no rslice
        if re.match('[\-0-9,:]+', args[0]):
            rslice = args[0]
            if not sys.stdin.isatty():
                pdbfh = sys.stdin
            else:
                sys.stderr.write(USAGE)
                sys.exit(1)
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 2:
        # Option & File
        if not re.match('[\-0-9,:]+', args[0]):
            sys.stderr.write('Invalid slice: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not os.path.isfile(args[1]):
            sys.stderr.write('File not found: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        rslice = args[0]
        pdbfh = open(args[1], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    # Parse selection
    # Return set of integers to be mapped to residue numbers
    resi_set = set()
    groups = [g for g in rslice.split(',') if g.strip()]
    for g in groups:
        bits = [b for b in g.split(':') if b.strip()]
        if len(bits) == 2:
            st_slice, en_slice = map(int, bits)
            resi_set = resi_set.union(range(st_slice, en_slice + 1))
        elif len(bits) == 1 and rslice[0] == ':':
            st_slice = -99
            en_slice = int(bits[0])
            resi_set = resi_set.union(range(st_slice, en_slice + 1))
        elif len(bits) == 1 and rslice[-1] == ':':
            st_slice = int(bits[0])
            en_slice = 99999
            resi_set = resi_set.union(range(st_slice, en_slice + 1))
        elif len(bits) == 1 and bits[0].find(':') == -1:
            resi_set = resi_set.union(map(int, bits))
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)

    return (resi_set, pdbfh)


def _shave_pdb(fhandle, set_of_residues):
    """Enclosing logic in a function to speed up a bit"""

    resset = set_of_residues
    backbone = set(('CA', 'N', 'O', 'C'))
    for line in fhandle:
        if not (line.startswith(('ATOM', 'HETATM')) and
                int(line[22:26]) in resset and
                line[12:16].strip() not in backbone):

            yield line

if __name__ == '__main__':

    # Check Input
    rslice, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _shave_pdb(pdbfh, rslice)

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
