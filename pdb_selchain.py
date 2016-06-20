#!/usr/bin/env python

"""
Extracts one or more chains from a PDB file.

usage: python pdb_selchain.py -<chain> <pdb file>
example: python pdb_selchain.py -A 1CTF.pdb

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
        # No chain, from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
            chain = ' '
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # Chain & Pipe _or_ file & no chain
        if re.match('\-[A-Za-z0-9]+', args[0]):
            chain = args[0][1:]
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
            chain = ' '
    elif len(args) == 2:
        # Chain & File
        if not re.match('\-[A-Za-z0-9]+', args[0]):
            sys.stderr.write('Invalid chain ID: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not os.path.isfile(args[1]):
            sys.stderr.write('File not found: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        chain = args[0][1:]
        pdbfh = open(args[1], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (chain, pdbfh)

def _select_chain(fhandle, chain_id):
    """Enclosing logic in a function to speed up a bit"""

    coord_re = re.compile('^(ATOM|HETATM)')
    fhandle = fhandle
    chain_id = set(chain_id)

    for line in fhandle:
        if coord_re.match(line) and line[21] in chain_id:
            yield line

if __name__ == '__main__':
    # Check Input
    chain, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _select_chain(pdbfh, chain)

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
