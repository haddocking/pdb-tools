#!/usr/bin/env python

"""
Extracts each model of a PDB file to a separate file.

usage: python pdb_splitmodel.py <pdb file>
example: python pdb_splitmodel.py 1CTF.pdb

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
        # Read from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # Read from file
        if not os.path.isfile(args[0]):
            sys.stderr.write('File not found: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        pdbfh = open(args[0], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return pdbfh

def _extract_models(fhandle):

    coord_re = re.compile('^(ATOM|HETATM)')
    fname_root = fhandle.name[:-4] if fhandle.name != '<stdin>' else 'output'
    output_handle = None

    for line in fhandle:
        if coord_re.match(line):
            # ATOM/HETATM line
            output_handle.write(line)
        elif line.startswith('MODEL'):
            model_no = line.split()[-1]
            output_handle = open(fname_root + '_' + model_no + '.pdb', 'w')
        elif line.startswith('ENDMDL'):
            output_handle.write('END\n')
            output_handle.close()

if __name__ == '__main__':
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    _extract_models(pdbfh)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
