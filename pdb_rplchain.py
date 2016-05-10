#!/usr/bin/env python

"""
Replaces a particular chain ID in a PDB file.

usage: python pdb_rplchain.py -<chain> -<chain> <pdb file>
example: python pdb_rplchain.py -A -B 1CTF.pdb

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
USAGE = "usage: " + sys.argv[0] + " -<chain> -<chain> <pdb file>\n"

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        sys.stderr.write(USAGE)
        sys.exit(1)

    elif len(args) == 2:
        # Pipe?
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)

        ori_chain = args[0]
        new_chain = args[1]
        assert re.match('\-[A-Za-z0-9 ]', ori_chain), 'Invalid chain ID: ' + ori_chain
        assert re.match('\-[A-Za-z0-9 ]', ori_chain), 'Invalid chain ID: ' + new_chain

    elif len(args) == 3:
        if not os.path.isfile(args[2]):
            sys.stderr.write('File not found: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        pdbfh = open(args[2], 'r')
        ori_chain = args[0]
        new_chain = args[1]
        assert re.match('\-[A-Za-z0-9 ]', ori_chain), 'Invalid chain ID: ' + ori_chain
        assert re.match('\-[A-Za-z0-9 ]', ori_chain), 'Invalid chain ID: ' + new_chain

    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (pdbfh, ori_chain, new_chain)

def _alter_chain(fhandle, ori_chain, new_chain):
    """Enclosing logic in a function to speed up a bit"""

    coord_re = re.compile('^(ATOM|HETATM)')
    fhandle = fhandle
    ori_chain = ori_chain[1:]
    new_chain = new_chain[1:]

    if not ori_chain:
        ori_chain = ' '
    if not new_chain:
        new_chain = ' '

    for line in fhandle:
        if coord_re.match(line) and line[21] == ori_chain:
            yield line[:21] + new_chain + line[22:]
        else:
            yield line

if __name__ == '__main__':
    # Check Input
    pdbfh, ori_chain, new_chain = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _alter_chain(pdbfh, ori_chain, new_chain)

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
