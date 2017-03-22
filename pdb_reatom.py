#!/usr/bin/env python

"""
Renumbers atoms in a PDB file starting from a given number.

usage: python pdb_reatom.py -<atomi> <pdb file>
example: python pdb_reatom.py -1 1CTF.pdb

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
    Checks whether to read from stdin/file and validates user input/options.
    """

    if not len(args):
        # No reatom, from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
            reatom = 1
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # Resi & Pipe _or_ file & no reatom
        if re.match('\-[0-9]+', args[0]):
            reatom = int(args[0][1:])
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
            reatom = 1
    elif len(args) == 2:
        # Chain & File
        if not re.match('\-[0-9]+', args[0]):
            sys.stderr.write('Invalid atom number: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not os.path.isfile(args[1]):
            sys.stderr.write('File not found: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        reatom = int(args[0][1:])
        pdbfh = open(args[1], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (reatom, pdbfh)


def _renumber_pdb_atoms(fhandle, satomi):
    """Enclosing logic in a function to speed up a bit"""

    coord_re = re.compile('^(ATOM|HETATM)')
    satomi = satomi

    for line in fhandle:
        if coord_re.match(line):
            yield line[:6] + str(satomi).rjust(5) + line[11:]
            satomi += 1
        else:
            yield line


if __name__ == '__main__':

    # Check Input
    reatom, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _renumber_pdb_atoms(pdbfh, reatom)

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
