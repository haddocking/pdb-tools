#!/usr/bin/env python

"""
Adds TER statements whenever there is a break in
residue numbering/chain ids. Adds END statement.

usage: python pdb_tidy.py <pdb file>
example: python pdb_tidy.py 1CTF.pdb

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


def _tidy_structure(fhandle):
    """Enclosing logic in a function"""

    # TER     606      LEU A  75
    _TER = "TER   {:>5d}      {:3s} {:1s}{:>4s}{:1s}" + " " * 53 + "\n"

    coord_re = re.compile('^(ATOM|HETATM)')
    fhandle = fhandle

    pdb_data = []

    # Read first ATOM/HETATM line to initialize prev_line and store it already
    line = None
    for line in fhandle:
        if coord_re.match(line):
            pdb_data.append(line)
            break

    prev_line = line
    for line in fhandle:
        if coord_re.match(line):
            resid_gap = int(line[22:26]) - int(prev_line[22:26])
            if prev_line[21] != line[21] or resid_gap > 1:
                serial = int(prev_line[6:11]) + 1
                resnam = prev_line[17:20]
                chain  = prev_line[21]
                resid  = prev_line[22:26]
                icode  = prev_line[26]

                ter_line = _TER.format(serial, resnam, chain, resid, icode)
                pdb_data.append(ter_line)

            pdb_data.append(line)
            prev_line = line

    # Add last TER statement and END
    if not coord_re.match(line):
        line = prev_line

    serial = int(prev_line[6:11]) + 1
    resnam = line[17:20]
    chain  = line[21]
    resid  = line[22:26]
    icode  = line[26]

    ter_line = _TER.format(serial, resnam, chain, resid, icode)
    pdb_data.append(ter_line)
    pdb_data.append('END' + ' '*77 + '\n')

    return pdb_data


if __name__ == '__main__':

    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _tidy_structure(pdbfh)

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
