#!/usr/bin/env python

"""
Removes all HETATM records of the file.

usage: python pdb_striphet.py <pdb file>
example: python pdb_striphet.py 1CTF.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)


def check_input(args):
    """
    Checks whether to read from stdin/file and validates user input/options.
    """

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


def _remove_hetatm(fhandle):
    """Enclosing logic in a function to speed up a bit"""

    coord_recnames = set(['MODEL ', 'ATOM  ',
                          'ANISOU', 'ENDMDL', 'END   ',
                          'TER   ', 'CONECT', 'MASTER'])
    
    for line in fhandle:
        if line[0:6] in coord_recnames:
            yield line


if __name__ == '__main__':

    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _remove_hetatm(pdbfh)

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
